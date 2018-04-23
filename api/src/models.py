"""
    Here my models
"""
from sqlalchemy import Column, Integer, BigInteger, String, DateTime
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
    VR = Column(BigInteger)
    VV = Column(BigInteger)
    VITG = Column(BigInteger)
    ORA = Column(BigInteger)
    OVA = Column(BigInteger)
    OITGA = Column(BigInteger)
    ORP = Column(BigInteger)
    OVP = Column(BigInteger)
    OITGP = Column(BigInteger)
    IR = Column(BigInteger)
    IV = Column(BigInteger)
    IITG = Column(BigInteger)
    DT = Column(DateTime)
    PRIZ = Column(Integer)

    def __repr__(self):
        """
        pretty print
        """
        return str(self.P_K) + '_' + str(self.REGN) + '_' + str(self.DT)
