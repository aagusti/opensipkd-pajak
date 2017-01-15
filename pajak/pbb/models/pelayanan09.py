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
from ...tools import as_timezone
from ...models import CommonModel
from ..tools import FixNopelDetail
from ..models import pbbBase, pbbDBSession, pbb_schema
from pelayanan import PstDetail
#from ref import Kelurahan, Kecamatan, Dati2, KELURAHAN, KECAMATAN
    
PBB_ARGS = {'extend_existing':True,  
        #'autoload':True,
        'schema': pbb_schema}    

class Skkpp(pbbBase, CommonModel):
    __tablename__ = 'skkpp'
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
    kd_tp = Column(String(2))
    no_sk_skkpp = Column(String(30))
    tgl_sk_skkpp = Column(DateTime)
    jns_keputusan_skkpp = Column(String(1))
    kpkn = Column(String(30))
    nilai_skkpp = Column(Float)
    tgl_rekam_skkp = Column(DateTime)
    nip_rekam_skkp = Column(String(18))
    posted = Column(Integer, nullable=False)
    __table_args__ = (ForeignKeyConstraint([kd_kanwil, kd_kantor, thn_pelayanan,
        bundel_pelayanan, no_urut_pelayanan, kd_propinsi_pemohon, kd_dati2_pemohon,
        kd_kecamatan_pemohon, kd_kelurahan_pemohon, kd_blok_pemohon, no_urut_pemohon,
        kd_jns_op_pemohon], [PstDetail.kd_kanwil, PstDetail.kd_kantor, 
        PstDetail.thn_pelayanan, PstDetail.bundel_pelayanan, 
        PstDetail.no_urut_pelayanan, PstDetail.kd_propinsi_pemohon, 
        PstDetail.kd_dati2_pemohon, PstDetail.kd_kecamatan_pemohon, 
        PstDetail.kd_kelurahan_pemohon, PstDetail.kd_blok_pemohon, 
        PstDetail.no_urut_pemohon, PstDetail.kd_jns_op_pemohon]),
        PBB_ARGS,)
    @classmethod
    def query(cls):
        return pbbDBSession.query(cls)
    
    @classmethod
    def query_id(cls,id):
        fxNopel = FixNopelDetail(id)
        return cls.query().\
               filter(cls.kd_kanwil == fxNopel.kd_kanwil, 
                    cls.kd_kantor == fxNopel.kd_kantor, 
                    cls.thn_pelayanan == fxNopel.tahun, 
                    cls.bundel_pelayanan == fxNopel.bundel, 
                    cls.no_urut_pelayanan == fxNopel.urut,
                    cls.kd_propinsi_pemohon==fxNopel.kd_propinsi,
                    cls.kd_dati2_pemohon==fxNopel.kd_dati2,
                    cls.kd_kecamatan_pemohon==fxNopel.kd_kecamatan,
                    cls.kd_kelurahan_pemohon==fxNopel.kd_kelurahan,
                    cls.kd_blok_pemohon==fxNopel.kd_blok,
                    cls.no_urut_pemohon==fxNopel.no_urut,
                    cls.kd_jns_op_pemohon==fxNopel.kd_jns_op,
                    )

class Spmkp(pbbBase, CommonModel):
    __tablename__ = 'spmkp'
    kd_kanwil = Column(String(2), primary_key=True)
    kd_kantor = Column(String(2), primary_key=True)
    no_spmkp = Column(String(30), primary_key=True)
    tgl_spmkp = Column(DateTime)
    thn_pelayanan = Column(String(4))
    bundel_pelayanan = Column(String(4))
    no_urut_pelayanan = Column(String(3))
    kd_propinsi_pemohon = Column(String(2))
    kd_dati2_pemohon = Column(String(2))
    kd_kecamatan_pemohon = Column(String(3))
    kd_kelurahan_pemohon = Column(String(3))
    kd_blok_pemohon = Column(String(3))
    no_urut_pemohon = Column(String(4))
    kd_jns_op_pemohon = Column(String(1))
    no_rek_wp = Column(String(20))
    nm_bank_wp = Column(String(30))
    tgl_rekam_spmkp = Column(DateTime)
    nip_rekam_spmkp = Column(String(18))
    __table_args__ = (ForeignKeyConstraint([kd_kanwil, kd_kantor, thn_pelayanan,
        bundel_pelayanan, no_urut_pelayanan, kd_propinsi_pemohon, 
        kd_dati2_pemohon, kd_kecamatan_pemohon, kd_kelurahan_pemohon, 
        kd_blok_pemohon, no_urut_pemohon, kd_jns_op_pemohon], 
        [Skkpp.kd_kanwil, Skkpp.kd_kantor, Skkpp.thn_pelayanan, Skkpp.bundel_pelayanan, 
        Skkpp.no_urut_pelayanan, Skkpp.kd_propinsi_pemohon, Skkpp.kd_dati2_pemohon, 
        Skkpp.kd_kecamatan_pemohon, Skkpp.kd_kelurahan_pemohon, Skkpp.kd_blok_pemohon, 
        Skkpp.no_urut_pemohon, Skkpp.kd_jns_op_pemohon]),PBB_ARGS,)
        
    @classmethod
    def query(cls):
        return pbbDBSession.query(cls)
        
    @classmethod
    def query_id(cls,id):
        fxNopel = FixNopelDetail(id)
        return cls.query().\
               filter(cls.kd_kanwil == fxNopel.kd_kanwil, 
                    cls.kd_kantor == fxNopel.kd_kantor, 
                    cls.thn_pelayanan == fxNopel.tahun, 
                    cls.bundel_pelayanan == fxNopel.bundel, 
                    cls.no_urut_pelayanan == fxNopel.urut,
                    cls.kd_propinsi_pemohon==fxNopel.kd_propinsi,
                    cls.kd_dati2_pemohon==fxNopel.kd_dati2,
                    cls.kd_kecamatan_pemohon==fxNopel.kd_kecamatan,
                    cls.kd_kelurahan_pemohon==fxNopel.kd_kelurahan,
                    cls.kd_blok_pemohon==fxNopel.kd_blok,
                    cls.no_urut_pemohon==fxNopel.no_urut,
                    cls.kd_jns_op_pemohon==fxNopel.kd_jns_op,
                    )
    @classmethod
    def delete_id(cls,id):
        q = cls.query_id(id)
        q.delete()
                    
class PenerimaKompensasi(pbbBase, CommonModel):
    __tablename__ = 'penerima_kompensasi'
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
    no_urut_penerima_kompensasi = Column(Integer, primary_key=True)
    kd_propinsi_kompensasi = Column(String(2))
    kd_dati2_kompensasi = Column(String(2))
    kd_kecamatan_kompensasi = Column(String(3))
    kd_kelurahan_kompensasi = Column(String(3))
    kd_blok_kompensasi = Column(String(3))
    no_urut_kompensasi = Column(String(4))
    kd_jns_op_kompensasi = Column(String(1))
    thn_pajak_kompensasi = Column(String(4))
    nilai_yang_dikompensasi = Column(Float)
    __table_args__ = (ForeignKeyConstraint([kd_kanwil, kd_kantor, thn_pelayanan,
        bundel_pelayanan, no_urut_pelayanan, kd_propinsi_pemohon, 
        kd_dati2_pemohon, kd_kecamatan_pemohon, kd_kelurahan_pemohon, 
        kd_blok_pemohon, no_urut_pemohon, kd_jns_op_pemohon], 
        [Skkpp.kd_kanwil, Skkpp.kd_kantor, Skkpp.thn_pelayanan, 
        Skkpp.bundel_pelayanan, Skkpp.no_urut_pelayanan, Skkpp.kd_propinsi_pemohon, 
        Skkpp.kd_dati2_pemohon, Skkpp.kd_kecamatan_pemohon, Skkpp.kd_kelurahan_pemohon, 
        Skkpp.kd_blok_pemohon, Skkpp.no_urut_pemohon, Skkpp.kd_jns_op_pemohon]),
        PBB_ARGS,)
    
    def nop_kompensasi(self):
        return '.'.join([self.kd_propinsi_kompensasi, self.kd_dati2_kompensasi,
                    self.kd_kecamatan_kompensasi, self.kd_kelurahan_kompensasi, 
                    self.kd_blok_kompensasi, self.no_urut_kompensasi, 
                    self.kd_jns_op_kompensasi])
    @classmethod
    def query(cls):
        return pbbDBSession.query(cls)
        
    @classmethod
    def query_id(cls,id):
        fxNopel = FixNopelDetail(id)
        return pbbDBSession.query(cls).\
               filter(cls.kd_kanwil == fxNopel.kd_kanwil, 
                    cls.kd_kantor == fxNopel.kd_kantor, 
                    cls.thn_pelayanan == fxNopel.tahun, 
                    cls.bundel_pelayanan == fxNopel.bundel, 
                    cls.no_urut_pelayanan == fxNopel.urut,
                    cls.kd_propinsi_pemohon==fxNopel.kd_propinsi,
                    cls.kd_dati2_pemohon==fxNopel.kd_dati2,
                    cls.kd_kecamatan_pemohon==fxNopel.kd_kecamatan,
                    cls.kd_kelurahan_pemohon==fxNopel.kd_kelurahan,
                    cls.kd_blok_pemohon==fxNopel.kd_blok,
                    cls.no_urut_pemohon==fxNopel.no_urut,
                    cls.kd_jns_op_pemohon==fxNopel.kd_jns_op,
                    #no_urut_penerima_kompensasi == id[-3:]
                    )                 
                    
    @classmethod
    def delete_id(cls,id):
        q = cls.query_id(id)
        q.delete()
        
#END Of Script