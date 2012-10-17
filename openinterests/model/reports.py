from sqlalchemy.sql.expression import nullslast

from openinterests.core import db

from openinterests.model.entity import Entity
from openinterests.model.country import Country
from openinterests.model.representative import Representative
from openinterests.model.financial_data import FinancialData

def _greatest():
    return db.func.greatest

def test_report():
    """ Just a test for debugging reports. """
    return db.session.query(Entity.id.label('id'),
        Entity.name.label('name'))

def rep_by_exp(sub_category_id=None):
    """Representatives spending most on lobbying in a subcategory."""
    q = db.session.query(Representative.id,
            Representative.identification_code)
    q = q.join(Country)
    q = q.join(FinancialData)
    q = q.join(Entity)
    q = q.add_column(Country.name.label("contact_country"))
    q = q.add_column(Entity.name)
    cost = _greatest()(FinancialData.cost_absolute,
                       FinancialData.cost_max)
    cost = cost.label("cost")
    if sub_category_id is not None:
        q = q.filter(Representative.sub_category_id==sub_category_id)
    q = q.filter(cost!=None)
    q = q.add_column(cost)
    q = q.order_by(cost.desc())
    return q

def rep_by_country():
    """Group the representatives for each country."""
    q = db.session.query(Country.name)
    q = q.join(Representative)
    q = q.group_by(Country.name)
    count = db.func.count(Representative.id).label("count")
    q = q.add_column(count)
    q = q.order_by(count.desc())
    return q

def rep_by_turnover(sub_category_id=None):
    """Lobbying firms with the highest turnover in a subcategory."""
    q = db.session.query(Representative.id,
            Representative.identification_code)
    q = q.join(Country)
    q = q.join(FinancialData)
    q = q.join(Entity)
    q = q.add_column(Country.name.label("contact_country"))
    q = q.add_column(Entity.name)
    turnover = _greatest()(FinancialData.turnover_absolute,
                       FinancialData.turnover_max)
    turnover = turnover.label("turnover")
    if sub_category_id is not None:
        q = q.filter(Representative.sub_category_id==sub_category_id)
    q = q.filter(turnover!=None)
    q = q.add_column(turnover)
    q = q.order_by(turnover.desc())
    return q


