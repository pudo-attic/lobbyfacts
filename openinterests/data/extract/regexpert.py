import logging
from datetime import datetime
from pprint import pprint
from urlparse import urljoin
from itertools import count
from lxml import html
import requests

from openinterests.data import sl, etl_engine

log = logging.getLogger(__name__)

URL = 'http://ec.europa.eu/transparency/regexpert/search_results_groups.cfm?page=%s'

FIELDS = {
        'Task': 'task',
        'Mission': 'mission'
    }

def pseudotable(el):
    data = {}
    for d in el.findall('div'):
        if d.get('class') in ['labelspan', 'col1']:
            label = d.text.strip().strip(':')
            label = FIELDS.get(label, label.lower().replace(' ', '_'))
        elif d.get('class') in ['contentspan', 'col2']:
            data[label] = d.text.strip()
        elif d.get('class') in ['contentTable', 'col2 listbox']:
            flds = [f.text.strip() for f in d.findall('div') \
                    if f.text and len(f.text.strip())]
            data[label] = flds
    return data

def scrape_member(url):
    data = {'url': url}
    res = requests.get(url)
    doc = html.document_fromstring(res.content)
    data.update(pseudotable(doc.find('.//fieldset')))
    return data

def scrape_group(url):
    data = {'url': url}
    res = requests.get(url)
    doc = html.document_fromstring(res.content)

    gdetails = doc.find('.//*[@id="groupDetails"]')
    data['title'] = gdetails.find('.//div[@class="col1"]').text.strip()
    data['identifier'] = data['title'].rsplit('(', 1)[-1].replace(')', '')
    data['status'] = gdetails.find('.//div/span').text
    data['status_note'] = gdetails.find('.//div[@id="statusNote"]/p').text.strip()
    log.info("Scraping: %s", data['title'])
    details = gdetails.find('.//*[@id="details"]')
    label = None
    data.update(pseudotable(details))
    data['last_updated'] = datetime.strptime(data['last_updated'], "%d %b %Y")
    try:
        data['active_since'] = datetime.strptime(data['active_since'], "%d/%m/%y")
    except:
        try:
            data['active_since'] = datetime.strptime(data['active_since'], "%Y")
        except:
            try:
                data['active_since'] = datetime.strptime(data['active_since'], "%d/%m/%Y")
            except:
                log.error("Can't parse date: %s", data['active_since'])



    ainfo = gdetails.find('.//*[@id="info"]')
    data['additional_info'] = []
    for act in ainfo.findall('.//fieldset'):
        a = {'type': act.find('legend').text.strip(),
             'text': act.find('legend').tail.strip(),
             'attachments': [],
             'links': []}
        for div in act.findall('div'):
            if div.get('class') == 'attachements':
                url = urljoin(URL, div.find('.//a').get('href'))
                a['attachments'].append(url)
            else:
                url = urljoin(URL, div.find('.//a').get('href'))
                a['links'].append(url)
        data['additional_info'].append(a)

    subgroups = gdetails.find('.//*[@id="subgroups"]')
    data['subgroups'] = []
    for subgroup in subgroups.findall('.//table[@class="listContentContainerSubGroup"]'):
        g = {'name': subgroup.find('.//td/a').text.strip(),
             'duration': subgroup.find('.//td[@class="col2"]').text.strip(),
             'members': []}
        members = [m for m in subgroup.getnext().findall('.//div') if 'SubSubSub' in m.get('class', '')]
        for member in members:
            m = pseudotable(member)
            m['url'] = urljoin(URL, "detailMember.cfm?memberID=%s&orig=group" % member.get('id').split('_')[0])
            g['members'].append(m)
        data['subgroups'].append(g)

    data['members'] = []
    for list_a in doc.findall('.//div[@id="list"]//td/a'):
        m = scrape_member(urljoin(URL, list_a.get('href')))
        data['members'].append(m)

    return data

def scrape_index():
    for i in count(1):
        res = requests.post(URL % i, data={
            'searchType': 'simple',
            'searchByCheck': 0,
            'SearchBy': 0,
            'selectiontype_Group': 2,
            'dg_type': 1,
            'selectiontype_DG': 1,
            'Submit': 'Search'
            })
        doc = html.document_fromstring(res.content)
        links = doc.findall('.//table[@class="listContentContainer"]//a')
        if not len(links):
            return
        for link in links:
            yield scrape_group(urljoin(URL, link.get('href')))

def save_member(engine, etlId, member):
    member = dict(member.items())
    member['subgroup'] = member.get('subgroup')

    member.pop('representatives', [])
    member.pop('interest_represented', [])
    member['professional_profile'] = ', '.join(member.pop('professional_profile', []))

    def _s(data):
        if 'subgroup_status' in data:
            del data['subgroup_status']
        for policy_area in data.pop('policy_area', []):
            sl.upsert(engine, sl.get_table(engine, 'expertgroup_member_policy_area'),
                    {'expertgroup_etl_id': etlId, 'member': data['name'],
                     'policy_area': policy_area, 'subgroup': data['subgroup']},
                    ['expertgroup_etl_id', 'policy_area', 'member', 'subgroup'])
        for country in data.pop('countries/area_represented',
            data.pop('countries/areas_represented', [])):
            sl.upsert(engine, sl.get_table(engine, 'expertgroup_member_country'),
                    {'expertgroup_etl_id': etlId, 'member': data['name'],
                      'country': country, 'subgroup': data['subgroup']},
                      ['expertgroup_etl_id', 'country', 'member', 'subgroup'])
        data['expertgroup_etl_id'] = etlId
        sl.upsert(engine, sl.get_table(engine, 'expertgroup_member'),
            data, ['expertgroup_etl_id', 'name', 'subgroup'])

    if 'public_authorities' in member or 'public_authority' in member:
        for na in member.pop('public_authorities', member.pop('public_authority', [])):
            d = dict(member.items())
            d['short_name'] = na
            d['name'] = "%s (%s)" % (na, d['country'])
            _s(d)
    else:
        if not 'name' in member: 
            member['name'] = member.get('country')
        _s(member)


def save(engine, group):
    #etlId = "%s//%s" % (group['identifier'], group['last_updated'])
    etlId = "%s//ALL" % group['identifier']
    for policy_area in group.pop('policy_area', []):
        sl.upsert(engine, sl.get_table(engine, 'expertgroup_policy_area'),
                  {'expertgroup_etl_id': etlId, 'policy_area': policy_area},
                  ['expertgroup_etl_id', 'policy_area'])
    for task in group.pop('task', []):
        sl.upsert(engine, sl.get_table(engine, 'expertgroup_task'),
                  {'expertgroup_etl_id': etlId, 'task': task},
                  ['expertgroup_etl_id', 'task'])
    for composition in group.pop('composition', []):
        sl.upsert(engine, sl.get_table(engine, 'expertgroup_composition'),
                  {'expertgroup_etl_id': etlId, 'composition': composition},
                  ['expertgroup_etl_id', 'composition'])
    for associated_dg in group.pop('associated_dg', []):
        sl.upsert(engine, sl.get_table(engine, 'expertgroup_directorate'),
                  {'expertgroup_etl_id': etlId, 'directorate': associated_dg},
                  ['expertgroup_etl_id', 'directorate'])
    for lead_dg in group.pop('lead_dg', []):
        sl.upsert(engine, sl.get_table(engine, 'expertgroup_directorate'),
                  {'expertgroup_etl_id': etlId, 'directorate': lead_dg, 'lead': True},
                  ['expertgroup_etl_id', 'directorate'])
    for member in group.pop('members'):
        save_member(engine, etlId, member)

    for subgroup in group.pop('subgroups'):
        subgroup['expertgroup_etl_id'] = etlId
        for member in subgroup.pop('members'):
            member['subgroup'] = subgroup['name']
            save_member(engine, etlId, member)
        sl.upsert(engine, sl.get_table(engine, 'expertgroup_subgroup'),
                  subgroup, ['expertgroup_etl_id', 'name'])
    void = group.pop('additional_info')

    group['etl_id'] = etlId
    group.pop('link_to_website', '')
    sl.upsert(engine, sl.get_table(engine, 'expertgroup'),
              group, ['etl_id'])
    #pprint(group)


def extract(engine):
    for group in scrape_index():
        save(engine, group)

if __name__ == '__main__':
    engine = etl_engine()
    extract(engine)

