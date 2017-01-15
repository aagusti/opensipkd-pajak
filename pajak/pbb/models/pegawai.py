from sqlalchemy import (
    Column, Integer, BigInteger, Float, Text, DateTime, ForeignKey, 
    UniqueConstraint, String, SmallInteger, types, func, ForeignKeyConstraint,
    literal_column, and_
    )
    
from ...models import CommonModel
from ..models import pbbBase, pbbDBSession, pbb_schema, PBB_ARGS

class Pegawai(pbbBase, CommonModel):
    __tablename__ = 'pegawai'
    nip = Column(String(18), primary_key=True)
    nm_pegawai = Column(String(30))
    __table_args__ = (PBB_ARGS,)
    @classmethod
    def query(cls):
        return pbbDBSession.query(cls)
        
    @classmethod
    def query_id(cls,id):
        return cls.query().\
                    filter(cls.nip == id,)

class DatLogin(pbbBase, CommonModel):
    __tablename__ = 'dat_login'
    nm_login = Column(String(18), primary_key=True)
    nip = Column(String(18))
    password = Column(String(50))
    __table_args__ = (PBB_ARGS,)
    @classmethod
    def query(cls):
        return pbbDBSession.query(cls)
        
    @classmethod
    def query_id(cls,id):
        return cls.query().\
                    filter(cls.nm_login == id,)
#END OF SCRIPT    