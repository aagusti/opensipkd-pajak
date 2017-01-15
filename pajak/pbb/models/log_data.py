import sys
from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    BigInteger,
    Text,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    String,
    SmallInteger,
    Float,
    types,
    func,
    ForeignKeyConstraint,
    literal_column,
    and_
    )
from sqlalchemy.orm import aliased

from sqlalchemy.orm.exc import NoResultFound

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship,
    backref,
    #primary_join
    )
import re
from ...tools import as_timezone, FixLength

from ...models import CommonModel
from ..models import pbbBase, pbbDBSession, pbb_schema
from ...pbb.tools import FixNopel, FixNop
from pelayanan import PstDetail
#from ref import Kelurahan, Kecamatan, Dati2, KELURAHAN, KECAMATAN
    
PBB_ARGS = {'extend_existing':True,  
        #'autoload':True,
        'schema': pbb_schema}    

class LogKeluaranPst(pbbBase, CommonModel):
    __tablename__ = 'log_keluaran_pst'
    kd_kanwil = Column(String(2), primary_key=True)
    kd_kantor = Column(String(2), primary_key=True)
    thn_pelayanan = Column(String(4), primary_key=True)
    bundel_pelayanan = Column(String(4), primary_key=True)
    no_urut_pelayanan = Column(String(3), primary_key=True)
    kd_propinsi_pemohon = Column(String(2), primary_key=True)
    kd_dati2_pemohon = Column(String(2), primary_key=True)
    kd_kecamatan_pemohon = Column(String(3), primary_key=True)
    kd_kelurahan_pemohon = Column(String(3), primary_key=True)
    kd_blok_pemohon = Column(String(3), primary_key=True)
    no_urut_pemohon = Column(String(4), primary_key=True)
    kd_jns_op_pemohon = Column(String(1), primary_key=True)
    log_tahun_pajak = Column(String(4), primary_key=True)
    kd_jns_pelayanan = Column(String(2))
    log_sppt = Column(Integer)
    log_stts = Column(Integer)
    log_dhkp = Column(Integer)
    log_sk = Column(Integer)
    log_status = Column(Integer)
    __table_args__ = (PBB_ARGS,)
    
    @classmethod
    def pst_add_log_keluaran(cls, values):
        fixNopel = values["fixNopelDetail"]
        q = pbbDBSession.query(PstDetail).\
                filter(
                    PstDetail.kd_kanwil == fixNopel['kd_kanwil'], 
                    PstDetail.kd_kantor == fixNopel['kd_kantor'], 
                    PstDetail.thn_pelayanan == fixNopel['tahun'], 
                    PstDetail.bundel_pelayanan == fixNopel['bundel'], 
                    PstDetail.no_urut_pelayanan == fixNopel['urut'],
                    PstDetail.kd_propinsi_pemohon==fixNopel['kd_propinsi'],
                    PstDetail.kd_dati2_pemohon==fixNopel['kd_dati2'],
                    PstDetail.kd_kecamatan_pemohon==fixNopel['kd_kecamatan'],
                    PstDetail.kd_kelurahan_pemohon==fixNopel['kd_kelurahan'],
                    PstDetail.kd_blok_pemohon==fixNopel['kd_blok'],
                    PstDetail.no_urut_pemohon==fixNopel['no_urut'],
                    PstDetail.kd_jns_op_pemohon==fixNopel['kd_jns_op'],
                )
                
        row = q.first()
        if row:
            q_cls = pbbDBSession.query(cls).\
                filter(cls.kd_kanwil == fixNopel['kd_kanwil'], 
                    cls.kd_kantor == fixNopel['kd_kantor'], 
                    cls.thn_pelayanan == fixNopel['tahun'], 
                    cls.bundel_pelayanan == fixNopel['bundel'], 
                    cls.no_urut_pelayanan == fixNopel['urut'],
                    cls.kd_propinsi_pemohon==fixNopel['kd_propinsi'],
                    cls.kd_dati2_pemohon==fixNopel['kd_dati2'],
                    cls.kd_kecamatan_pemohon==fixNopel['kd_kecamatan'],
                    cls.kd_kelurahan_pemohon==fixNopel['kd_kelurahan'],
                    cls.kd_blok_pemohon==fixNopel['kd_blok'],
                    cls.no_urut_pemohon==fixNopel['no_urut'],
                    cls.kd_jns_op_pemohon==fixNopel['kd_jns_op'],)
                    
            row_cls =  q_cls.first()
            if not row_cls:
                row_cls = cls()
                row_cls.from_dict(row.to_dict())
                row_cls.from_dict(values)
                row_cls.log_tahun_pajak = row.thn_pajak_permohonan
                pbbDBSession.add(row_cls)
                pbbDBSession.flush()
                