import sys
from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    BigInteger,
    Float,
    Text,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    String,
    SmallInteger,
    types,
    func,
    ForeignKeyConstraint,
    literal_column,
    and_
    )
from sqlalchemy.orm import aliased

from sqlalchemy.orm.exc import NoResultFound

from sqlalchemy.orm import (
    relationship,
    backref,
    #primary_join
    )
import re
from ...tools import as_timezone, FixLength

from ...models import CommonModel
from ..models import pbbBase, pbbDBSession, pbb_schema

#from ref import Kelurahan, Kecamatan, Dati2, KELURAHAN, KECAMATAN
    
PBB_ARGS = {'extend_existing':True,  
        'schema': pbb_schema}    
        
class TempatPembayaran(pbbBase, CommonModel):
    __tablename__ = 'tempat_pembayaran'
    kd_kanwil = Column(String(2), primary_key=True)
    kd_kantor = Column(String(2), primary_key=True)
    kd_tp = Column(String(2), primary_key=True)
    nm_tp = Column(String(30))
    alamat_tp = Column(String(50))
    no_rek_tp = Column(String(15))
    __table_args__ = (PBB_ARGS,)
