from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
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
    Float,
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
from ..tools import clsNop

from ...models import CommonModel
from ..models import pbbBase, pbbDBSession, PBB_ARGS
from ref import Kelurahan, Kecamatan, Dati2

            
class DatPetaBlok(pbbBase, CommonModel):
    __tablename__  = 'dat_peta_blok'
    kd_propinsi = Column(String(2), primary_key=True)
    kd_dati2 = Column(String(2), primary_key=True)
    kd_kecamatan = Column(String(3), primary_key=True)
    kd_kelurahan = Column(String(3), primary_key=True)
    kd_blok = Column(String(3), primary_key=True)
    status_peta_blok = Column(Integer)
    __table_args__ = (
        ForeignKeyConstraint([kd_propinsi, kd_dati2, kd_kecamatan, kd_kelurahan], 
            [Kelurahan.kd_propinsi, Kelurahan.kd_dati2, Kelurahan.kd_kecamatan, Kelurahan.kd_kelurahan]),
            PBB_ARGS)

class DatSubjekPajak(pbbBase, CommonModel):
    __tablename__  = 'dat_subjek_pajak'
    subjek_pajak_id = Column(String(30), primary_key=True)
    nm_wp = Column(String(30))
    jalan_wp = Column(String(30))
    blok_kav_no_wp = Column(String(15))
    rw_wp = Column(String(2))
    rt_wp = Column(String(3))
    kelurahan_wp = Column(String(30))
    kota_wp = Column(String(30))
    kd_pos_wp = Column(String(5))
    telp_wp = Column(String(20))
    npwp = Column(String(15))
    status_pekerjaan_wp = Column(String(1))
    __table_args__ = (PBB_ARGS,)

class DatPetaBlok(pbbBase, CommonModel):
    __tablename__ = 'dat_peta_blok'
    kd_propinsi = Column(String(2), primary_key=True)
    kd_dati2 = Column(String(2), primary_key=True)
    kd_kecamatan = Column(String(3), primary_key=True)
    kd_kelurahan = Column(String(3), primary_key=True)
    kd_blok = Column(String(3), primary_key=True)
    status_peta_blok = Column(Integer)
    __table_args__ = (
        ForeignKeyConstraint([kd_propinsi, kd_dati2, kd_kecamatan, kd_kelurahan], 
            [Kelurahan.kd_propinsi, Kelurahan.kd_dati2, Kelurahan.kd_kecamatan, 
             Kelurahan.kd_kelurahan]),
             PBB_ARGS,)
    
class DatObjekPajak(pbbBase, CommonModel):
    __tablename__  = 'dat_objek_pajak'
    kd_propinsi = Column(String(2), primary_key=True)
    kd_dati2 = Column(String(2), primary_key=True)
    kd_kecamatan = Column(String(3), primary_key=True)
    kd_kelurahan = Column(String(3), primary_key=True)
    kd_blok = Column(String(3), primary_key=True)
    no_urut = Column(String(4), primary_key=True)
    kd_jns_op = Column(String(1), primary_key=True)
    subjek_pajak_id = Column(String(30))
    no_formulir_spop = Column(String(11))
    no_persil = Column(String(5))
    jalan_op = Column(String(30))
    blok_kav_no_op = Column(String(15))
    rw_op = Column(String(2))
    rt_op = Column(String(3))
    kd_status_cabang = Column(Integer)
    kd_status_wp = Column(String(1))
    total_luas_bumi = Column(Float)
    total_luas_bng = Column(Float)
    njop_bumi = Column(Float)
    njop_bng = Column(Float)
    status_peta_op = Column(Integer)
    jns_transaksi_op = Column(String(1))
    tgl_pendataan_op = Column(DateTime)
    nip_pendata = Column(String(18))
    tgl_pemeriksaan_op = Column(DateTime)
    nip_pemeriksa_op = Column(String(18))
    tgl_perekaman_op = Column(DateTime)
    nip_perekam_op = Column(String(18))
    __table_args__ = (
        ForeignKeyConstraint([kd_propinsi, kd_dati2, kd_kecamatan, kd_kelurahan, kd_blok], 
            [DatPetaBlok.kd_propinsi, DatPetaBlok.kd_dati2, DatPetaBlok.kd_kecamatan, 
            DatPetaBlok.kd_kelurahan, DatPetaBlok.kd_blok]),
        ForeignKeyConstraint([subjek_pajak_id], 
            [DatSubjekPajak.subjek_pajak_id]),
            PBB_ARGS,)

    @classmethod
    def query_data(cls):
        return pbb_DBSession.query(cls)
        
    @classmethod
    def get_by_nop(cls, p_kode):
        pkey = FixLength(NOP)
        pkey.set_raw(p_kode)
        query = cls.query_data()
        return query.filter_by(kd_propinsi = pkey['kd_propinsi'], 
                            kd_dati2 = pkey['kd_dati2'], 
                            kd_kecamatan = pkey['kd_kecamatan'], 
                            kd_kelurahan = pkey['kd_kelurahan'], 
                            kd_blok = pkey['kd_blok'], 
                            no_urut = pkey['no_urut'], 
                            kd_jns_op = pkey['kd_jns_op'],)

    @classmethod
    def get_info_op_bphtb(cls, p_kode):
        pkey = clsNop(NOP)
        query = pbb_DBSession.query(
                  cls.jalan_op, cls.blok_kav_no_op, cls.rt_op, cls.rw_op,
                  cls.total_luas_bumi.label('luas_bumi_sppt'), cls.total_luas_bng.label('luas_bng_sppt'), 
                  cls.njop_bumi.label('njop_bumi_sppt'), cls.njop_bng.label('njop_bng_sppt'),
                  DatSubjekPajak.nm_wp,  
                  func.coalesce(DatOpAnggota.luas_bumi_beban,0).label('luas_bumi_beban'), 
                  func.coalesce(DatOpAnggota.luas_bng_beban,0).label('luas_bng_beban'), 
                  func.coalesce(DatOpAnggota.njop_bumi_beban,0).label('njop_bumi_beban'), 
                  func.coalesce(DatOpAnggota.njop_bng_beban,0).label('njop_bng_beban'), ).\
              outerjoin(DatSubjekPajak).\
              outerjoin(DatOpAnggota)
              
        return query.filter(
                            cls.kd_propinsi == pkey['kd_propinsi'], 
                            cls.kd_dati2 == pkey['kd_dati2'], 
                            cls.kd_kecamatan == pkey['kd_kecamatan'], 
                            cls.kd_kelurahan == pkey['kd_kelurahan'], 
                            cls.kd_blok == pkey['kd_blok'], 
                            cls.no_urut == pkey['no_urut'], 
                            cls.kd_jns_op == pkey['kd_jns_op'],)
                            
class DatZnt(pbbBase, CommonModel):
    __tablename__ = 'dat_znt'
    kd_propinsi = Column(String(2), primary_key=True)
    kd_dati2 = Column(String(2), primary_key=True)
    kd_kecamatan = Column(String(3), primary_key=True)
    kd_kelurahan = Column(String(3), primary_key=True)
    kd_znt = Column(String(2), primary_key=True)
    __table_args__ = (
        ForeignKeyConstraint([kd_propinsi, kd_dati2, kd_kecamatan, kd_kelurahan], 
            [Kelurahan.kd_propinsi, Kelurahan.kd_dati2, Kelurahan.kd_kecamatan, 
             Kelurahan.kd_kelurahan]),
             PBB_ARGS)


class DatPetaZnt(pbbBase, CommonModel):
    __tablename__ = 'dat_peta_znt'
    kd_propinsi = Column(String(2), primary_key=True)
    kd_dati2 = Column(String(2), primary_key=True)
    kd_kecamatan = Column(String(3), primary_key=True)
    kd_kelurahan = Column(String(3), primary_key=True)
    kd_blok = Column(String(3), primary_key=True)
    kd_znt = Column(String(2), primary_key=True)
    __table_args__ = (
        ForeignKeyConstraint([kd_propinsi, kd_dati2, kd_kecamatan, kd_kelurahan, kd_blok], 
            [DatPetaBlok.kd_propinsi, DatPetaBlok.kd_dati2, DatPetaBlok.kd_kecamatan, 
             DatPetaBlok.kd_kelurahan, DatPetaBlok.kd_blok]),
        ForeignKeyConstraint([kd_propinsi, kd_dati2, kd_kecamatan, kd_kelurahan, kd_znt], 
            [DatZnt.kd_propinsi, DatZnt.kd_dati2, DatZnt.kd_kecamatan, 
             DatZnt.kd_kelurahan, DatZnt.kd_znt]),
             PBB_ARGS,)

                          
class DatOpBumi(pbbBase, CommonModel):
    __tablename__  = 'dat_op_bumi'
    kd_propinsi = Column(String(2), primary_key=True)
    kd_dati2 = Column(String(2), primary_key=True)
    kd_kecamatan = Column(String(3), primary_key=True)
    kd_kelurahan = Column(String(3), primary_key=True)
    kd_blok = Column(String(3), primary_key=True)
    no_urut = Column(String(4), primary_key=True)
    kd_jns_op = Column(String(1), primary_key=True)
    no_bumi = Column(Integer, primary_key=True)
    kd_znt = Column(String(2))
    luas_bumi = Column(Float)
    jns_bumi = Column(String(1))
    nilai_sistem_bumi = Column(Float)
    __table_args__ = (
        ForeignKeyConstraint([kd_propinsi, kd_dati2, kd_kecamatan, kd_kelurahan, kd_blok, kd_znt], 
                [DatPetaZnt.kd_propinsi, DatPetaZnt.kd_dati2, DatPetaZnt.kd_kecamatan, 
                 DatPetaZnt.kd_kelurahan, DatPetaZnt.kd_blok, DatPetaZnt.kd_znt]),
        ForeignKeyConstraint([kd_propinsi, kd_dati2, kd_kecamatan, kd_kelurahan, kd_blok, no_urut, kd_jns_op], 
                [DatObjekPajak.kd_propinsi, DatObjekPajak.kd_dati2, 
                 DatObjekPajak.kd_kecamatan, DatObjekPajak.kd_kelurahan, 
                 DatObjekPajak.kd_blok, DatObjekPajak.no_urut, 
                 DatObjekPajak.kd_jns_op]),
        PBB_ARGS,)

class DatOpAnggota(pbbBase, CommonModel):
    __tablename__  = 'dat_op_anggota'
    kd_propinsi_induk = Column(String(2), primary_key=True)
    kd_dati2_induk = Column(String(2), primary_key=True)
    kd_kecamatan_induk = Column(String(3), primary_key=True)
    kd_kelurahan_induk = Column(String(3), primary_key=True)
    kd_blok_induk = Column(String(3), primary_key=True)
    no_urut_induk = Column(String(4), primary_key=True)
    kd_jns_op_induk = Column(String(1), primary_key=True)
    kd_propinsi = Column(String(2), primary_key=True)
    kd_dati2 = Column(String(2), primary_key=True)
    kd_kecamatan = Column(String(3), primary_key=True)
    kd_kelurahan = Column(String(3), primary_key=True)
    kd_blok = Column(String(3), primary_key=True)
    no_urut = Column(String(4), primary_key=True)
    kd_jns_op = Column(String(1), primary_key=True)
    luas_bumi_beban = Column(Float)
    luas_bng_beban = Column(Float)
    nilai_sistem_bumi_beban = Column(Float)
    nilai_sistem_bng_beban = Column(Float)
    njop_bumi_beban = Column(Float)
    njop_bng_beban = Column(Float)
    __table_args__ = (ForeignKeyConstraint([kd_propinsi, kd_dati2, kd_kecamatan, kd_kelurahan,
                                            kd_blok, no_urut,kd_jns_op], 
                                            [DatObjekPajak.kd_propinsi, DatObjekPajak.kd_dati2,
                                             DatObjekPajak.kd_kecamatan,DatObjekPajak.kd_kelurahan,
                                             DatObjekPajak.kd_blok, DatObjekPajak.no_urut,
                                             DatObjekPajak.kd_jns_op]),
                     PBB_ARGS)
          

                                     
