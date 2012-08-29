from openinterests.core import db
from openinterests.model.api import ApiEntityMixIn
from openinterests.model.revision import RevisionedMixIn
from openinterests.model.entity import Entity
from openinterests.model.representative import Representative

class FinancialData(db.Model, RevisionedMixIn, ApiEntityMixIn):
    __tablename__ = 'financial_data'

    representative_id = db.Column(db.String(36), db.ForeignKey('representative.id'))

    turnover_min = db.Column(db.BigInteger, nullable=True)
    turnover_max = db.Column(db.BigInteger, nullable=True)
    turnover_absolute = db.Column(db.BigInteger, nullable=True)
    cost_min = db.Column(db.BigInteger, nullable=True)
    cost_max = db.Column(db.BigInteger, nullable=True)
    cost_absolute = db.Column(db.BigInteger, nullable=True)
    direct_rep_costs_min = db.Column(db.BigInteger, nullable=True)
    direct_rep_costs_max = db.Column(db.BigInteger, nullable=True)
    total_budget = db.Column(db.BigInteger, nullable=True)
    public_financing_total = db.Column(db.BigInteger, nullable=True)
    public_financing_infranational = db.Column(db.BigInteger, nullable=True)
    public_financing_national = db.Column(db.BigInteger, nullable=True)
    eur_sources_grants = db.Column(db.BigInteger, nullable=True)
    eur_sources_procurement = db.Column(db.BigInteger, nullable=True)
    other_sources_donation = db.Column(db.BigInteger, nullable=True)
    other_sources_contributions = db.Column(db.BigInteger, nullable=True)
    other_sources_total = db.Column(db.BigInteger, nullable=True)

    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    type = db.Column(db.Unicode)


    def update_values(self, data):
        self.representative_id = data.get('representative').id

        self.turnover_min = data.get('turnover_min')
        self.turnover_max = data.get('turnover_max')
        self.turnover_absolute = data.get('turnover_absolute')
        self.cost_min = data.get('cost_min')
        self.cost_max = data.get('cost_max')
        self.cost_absolute = data.get('cost_absolute')
        self.direct_rep_costs_min = data.get('direct_rep_costs_min')
        self.direct_rep_costs_max = data.get('direct_rep_costs_max')
        self.total_budget = data.get('total_budget')
        self.public_financing_total = data.get('public_financing_total')
        self.public_financing_infranational = data.get('public_financing_infranational')
        self.public_financing_national = data.get('public_financing_national')
        self.eur_sources_grants = data.get('eur_sources_grants')
        self.eur_sources_procurement = data.get('eur_sources_procurement')
        self.other_sources_donation = data.get('other_sources_donation')
        self.other_sources_contributions = data.get('other_sources_donation')
        self.other_sources_total = data.get('other_sources_total')

        self.start_date = data.get('start_date')
        self.end_date = data.get('end_date')
        self.type = data.get('type')

    @classmethod
    def by_rsd(cls, representative, start_date):
        q = db.session.query(cls)
        q = q.filter_by(current=True)
        q = q.filter(cls.representative_id==representative.id)
        q = q.filter(cls.start_date==start_date)
        return q.first()

    def as_shallow(self, turnovers=False):
        d = super(FinancialData, self).as_dict()
        d.update({
            'uri': self.uri,
            'type': self.type,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'turnover_min': self.turnover_min,
            'turnover_max': self.turnover_max,
            'turnover_absolute': self.turnover_absolute,
            'cost_min': self.cost_min,
            'cost_max': self.cost_max,
            'cost_absolute': self.cost_absolute,
            'direct_rep_costs_min': self.direct_rep_costs_min,
            'direct_rep_costs_max': self.direct_rep_costs_max,
            'total_budget': self.total_budget,
            'public_financing_total': self.public_financing_total,
            'public_financing_national': self.public_financing_national,
            'public_financing_infranational': self.public_financing_infranational,
            'eur_sources_grants': self.eur_sources_grants,
            'eur_sources_procurement': self.eur_sources_procurement,
            'other_sources_donation': self.other_sources_donation,
            'other_sources_contributions': self.other_sources_contributions,
            'other_sources_total': self.other_sources_total,
            })
        if turnovers:
            d['turnovers'] = [t.as_dict(financial_data=False) for t in self.turnovers]
        return d

    def as_dict(self):
        d = self.as_shallow(turnovers=True)
        d.update({
            'representative': self.representative.as_shallow() if self.representative else None
            })
        return d

    def __repr__(self):
        return "<FinancialData(%s,%r)>" % (self.start_date, self.representative)


Representative.financial_datas = db.relationship(FinancialData,
            primaryjoin=db.and_(Representative.id==FinancialData.representative_id,
                                FinancialData.current==True),
            foreign_keys=[Representative.id],
            lazy='dynamic',
            backref=db.backref('representative',
                uselist=False,
                primaryjoin=db.and_(Representative.id==FinancialData.representative_id,
                                    Representative.current==True)
                ))


class FinancialTurnover(db.Model, RevisionedMixIn, ApiEntityMixIn):
    __tablename__ = 'financial_turnover'

    financial_data_id = db.Column(db.String(36), db.ForeignKey('financial_data.id'))
    entity_id = db.Column(db.String(36), db.ForeignKey('entity.id'))

    min = db.Column(db.BigInteger)
    max = db.Column(db.BigInteger)

    def update_values(self, data):
        self.financial_data_id = data.get('financial_data').id
        self.entity_id = data.get('entity').id

        self.min = data.get('min')
        self.max = data.get('max')

    @classmethod
    def by_fde(cls, financial_data, entity):
        q = db.session.query(cls)
        q = q.filter_by(current=True)
        q = q.filter(cls.financial_data_id==financial_data.id)
        q = q.filter(cls.entity_id==entity.id)
        return q.first()

    def as_dict(self, financial_data=True, entity=True):
        d = super(FinancialTurnover, self).as_dict()
        d.update({
            'uri': self.uri,
            'min': self.min,
            'max': self.max
            })
        if financial_data:
            d['financial_data'] = self.financial_data.as_shallow()
        if entity:
            d['entity'] = self.entity.as_shallow()
        return d

    def __repr__(self):
        return "<FinancialTurnover(%r,%r)>" % (self.financial_data, self.entity)


FinancialData.turnovers = db.relationship('FinancialTurnover', 
            primaryjoin=db.and_(FinancialTurnover.financial_data_id==FinancialData.id,
                                FinancialTurnover.current==True),
            foreign_keys=[FinancialData.id],
            lazy='dynamic',
            backref=db.backref('financial_data',
                uselist=False,
                primaryjoin=db.and_(FinancialTurnover.financial_data_id==FinancialData.id,
                                    FinancialData.current==True)
                ))


Entity.turnovers = db.relationship('FinancialTurnover', 
            primaryjoin=db.and_(FinancialTurnover.entity_id==Entity.id,
                                FinancialTurnover.current==True),
            foreign_keys=[Entity.id],
            lazy='dynamic',
            backref=db.backref('entity',
                uselist=False,
                primaryjoin=db.and_(FinancialTurnover.entity_id==Entity.id,
                                    Entity.current==True)
                ))

