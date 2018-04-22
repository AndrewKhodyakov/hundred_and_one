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

    P_K = Column(Integer, primary_key=True)
    REGN = Column(Integer)
    PLAN = Column(String(length=1, collation='utf-8'))
    NUM_SC = Column(String(length=10))
    A_P = Column(String(length=1))
    VR = Column(Numeric)
    VV = Column(Numeric)
    VITG = Column(Numeric)
    ORA = Column(Numeric)
    OVA = Column(Numeric)
    OITGA = Column(Numeric)
    ORP = Column(Numeric)
    OVP = Column(Numeric)
    OITGP = Column(Numeric)
    IR = Column(Numeric)
    IV = Column(Numeric)
    IITG = Column(Integer)
    DT = Column(DateTime)
    PRIZ = Column(Integer)

    def __repr__(self):
        """
        pretty print
        """
        return str(self.p_k) + '_' + str(self.regn) + '_' + str(self.dt)
