import csv

from lobbyfacts.core import app

COUNTRIES = []

def get_countries():
    if not len(COUNTRIES):
        with app.open_resource('resources/countries.csv') as f:
            reader = csv.DictReader(f)
            for row in reader:
                row = dict([(k,v.decode('utf-8')) for (k,v) in row.items()])
                row['euname'] = row.get('euname','').lower().strip()
                COUNTRIES.append(row)
    return COUNTRIES

def country_by_name(name):
    name = name.lower().strip()
    for country in get_countries():
        if country['euname'] == name:
            return country
    raise ValueError("%s: unknown country" % name)


if __name__ == '__main__':
    print country_by_name('Armenia')
    print country_by_name('Bosnia')

