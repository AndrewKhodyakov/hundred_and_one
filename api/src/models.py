"""
    Here my models
"""
from sqlalchemy import Column, Integer, Numeric, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class OneHundredReport(Base):
    """
    model for one_hundred_report
    """
    __tablename__ = 'one_hundred_report'

    p_k = Column(Integer, primary_key=True)
    regn = Column(Integer)
    plan = Column(String(length=1, collation='utf-8'))
    num_sc = Column(String(length=10))
    a_p = Column(String(length=1))
    vr = Column(Numeric)
    vv = Column(Numeric)
    vitg = Column(Numeric)
    ora = Column(Numeric)
    ova = Column(Numeric)
    oitga = Column(Numeric)
    orp = Column(Numeric)
    ir = Column(Numeric)
    iv = Column(Numeric)
    iitg = Column(Integer)
    dt = Column(DateTime)
    priz = Column(Integer)

    def __repr__(self):
        """
        pretty print
        """
        return str(self.p_k) + '_' + str(self.regn) + '_' + str(self.dt)
