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
from ..tools import FixNop, FixSppt

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
    @classmethod
    def query(cls):
        return pbbDBSession.query(cls)

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
    @classmethod
    def query(cls):
        return pbbDBSession.query(cls)
        
    @classmethod
    def query_id(cls, id):
        return cls.query().filter(func.trim(cls.subjek_pajak_id)==id)
        
    @classmethod
    def add_dict(cls, row_dicted, row = None):
        if not row:
            row = cls()
            if not 'status_pekerjaan_wp' in row_dicted:
                row_dicted['status_pekerjaan_wp'] = 5
        row.from_dict(row_dicted)
        pbbDBSession.add(row)
        pbbDBSession.flush()
        return row
        
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
    def query(cls):
        return pbbDBSession.query(cls)

    @classmethod
    def query_id(cls, id):
        pkey = FixNop(id)
        query = cls.query()
        return query.filter(cls.kd_propinsi == pkey['kd_propinsi'],
                            cls.kd_dati2 == pkey['kd_dati2'],
                            cls.kd_kecamatan == pkey['kd_kecamatan'],
                            cls.kd_kelurahan == pkey['kd_kelurahan'],
                            cls.kd_blok == pkey['kd_blok'],
                            cls.no_urut == pkey['no_urut'],
                            cls.kd_jns_op == pkey['kd_jns_op'],
                            )
        
    @classmethod
    def get_by_nop(cls, p_kode):
        return cls.query_id(p_kode)
        
    @classmethod
    def add_dict(cls, row_dicted, row = None):
        # if not row:
        # q = cls.query_id(row_dicted['id'])
        # row = q.first()
        if not row:
            row = cls()
        row.from_dict(row_dicted)
        pbbDBSession.add(row)
        pbbDBSession.flush()
        return row
    
    @classmethod
    def set_luas_bumi(cls, row_dicted):
        q = cls.query_id(row_dicted['id'])
        row = q.first()
        if row:
            row.total_luas_bumi = row_dicted['total_luas_bumi']
            pbbDBSession.add(row)
            pbbDBSession.flush()
        return row
    
    @classmethod
    def set_luas_bng(cls, row_dicted):
        q = cls.query_id(row_dicted['id'])
        row = q.first()
        if row:
            row.total_luas_bng = row_dicted['total_luas_bng']
            pbbDBSession.add(row)
            pbbDBSession.flush()
        return row
        
    @classmethod
    def get_info_op_bphtb(cls, p_kode):
        pkey = FixNop(p_kode)
        query = pbbDBSession.query(
                    cls.jalan_op, cls.blok_kav_no_op, cls.rt_op, cls.rw_op,
                    cls.total_luas_bumi.label('luas_bumi_sppt'), cls.total_luas_bng.label('luas_bng_sppt'),
                    cls.njop_bumi.label('njop_bumi_sppt'), cls.njop_bng.label('njop_bng_sppt'),
                    DatSubjekPajak.nm_wp,
                    func.coalesce(DatOpAnggota.luas_bumi_beban,0).label('luas_bumi_beban'),
                    func.coalesce(DatOpAnggota.luas_bng_beban,0).label('luas_bng_beban'),
                    func.coalesce(DatOpAnggota.njop_bumi_beban,0).label('njop_bumi_beban'),
                    func.coalesce(DatOpAnggota.njop_bng_beban,0).label('njop_bng_beban'), ).\
                join(DatOpBumi).\
                outerjoin(DatSubjekPajak).\
                outerjoin(DatOpAnggota)
        return query.filter(
                            DatOpBumi.no_bumi < '4',
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
    @classmethod
    def query(cls):
        return pbbDBSession.query(cls)


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
    @classmethod
    def query(cls):
        return pbbDBSession.query(cls)


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
        ForeignKeyConstraint([kd_propinsi, kd_dati2, kd_kecamatan, kd_kelurahan,
                 kd_blok, kd_znt],
                [DatPetaZnt.kd_propinsi, DatPetaZnt.kd_dati2, DatPetaZnt.kd_kecamatan,
                 DatPetaZnt.kd_kelurahan, DatPetaZnt.kd_blok, DatPetaZnt.kd_znt]),
        ForeignKeyConstraint([kd_propinsi, kd_dati2, kd_kecamatan, kd_kelurahan,
                 kd_blok, no_urut, kd_jns_op],
                [DatObjekPajak.kd_propinsi, DatObjekPajak.kd_dati2,
                 DatObjekPajak.kd_kecamatan, DatObjekPajak.kd_kelurahan,
                 DatObjekPajak.kd_blok, DatObjekPajak.no_urut,
                 DatObjekPajak.kd_jns_op]), PBB_ARGS,)
    @classmethod
    def query(cls):
        return pbbDBSession.query(cls)
        
    @classmethod
    def query_id(cls, id, no_bumi):
        pkey = FixNop(id)
        query = cls.query()
        return query.filter(cls.kd_propinsi == pkey['kd_propinsi'],
                            cls.kd_dati2 == pkey['kd_dati2'],
                            cls.kd_kecamatan == pkey['kd_kecamatan'],
                            cls.kd_kelurahan == pkey['kd_kelurahan'],
                            cls.kd_blok == pkey['kd_blok'],
                            cls.no_urut == pkey['no_urut'],
                            cls.kd_jns_op == pkey['kd_jns_op'],
                            cls.no_bumi == no_bumi)
    @classmethod
    def add_dict(cls, row_dicted, row = None):
        # q = cls.query_id(row_dicted['id'], row_dicted['no_bumi'])
        # row = q.first()
        if not row:
            row = cls()
        row.from_dict(row_dicted)
        pbbDBSession.add(row)
        pbbDBSession.flush()
        row_dicted['total_luas_bumi'] = row_dicted['luas_bumi']
        DatObjekPajak.set_luas_bumi(row_dicted)
        return row
                            
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
    @classmethod
    def query(cls):
        return pbbDBSession.query(cls)
        
    @classmethod
    def query_id(cls, id):
        pkey = FixNop(NOP)
        query = cls.query()
        return query.filter_by(kd_propinsi = pkey['kd_propinsi'],
                            kd_dati2 = pkey['kd_dati2'],
                            kd_kecamatan = pkey['kd_kecamatan'],
                            kd_kelurahan = pkey['kd_kelurahan'],
                            kd_blok = pkey['kd_blok'],
                            no_urut = pkey['no_urut'],
                            kd_jns_op = pkey['kd_jns_op'],)
                            
class DatOpBangunan(pbbBase, CommonModel):
    __tablename__ = 'dat_op_bangunan'
    kd_propinsi = Column(String(2), primary_key=True)
    kd_dati2 = Column(String(2), primary_key=True)
    kd_kecamatan = Column(String(3), primary_key=True)
    kd_kelurahan = Column(String(3), primary_key=True)
    kd_blok = Column(String(3), primary_key=True)
    no_urut = Column(String(4), primary_key=True)
    kd_jns_op = Column(String(1), primary_key=True)
    no_bng = Column(Integer, primary_key=True)
    kd_jpb = Column(String(2))
    no_formulir_lspop = Column(String(11))
    thn_dibangun_bng = Column(String(4))
    thn_renovasi_bng = Column(String(4))
    luas_bng = Column(Float)
    jml_lantai_bng = Column(Integer)
    kondisi_bng = Column(String(1))
    jns_konstruksi_bng = Column(String(1))
    jns_atap_bng = Column(String(1))
    kd_dinding = Column(String(1))
    kd_lantai = Column(String(1))
    kd_langit_langit = Column(String(1))
    nilai_sistem_bng = Column(Float)
    jns_transaksi_bng = Column(String(1))
    tgl_pendataan_bng = Column(DateTime)
    nip_pendata_bng = Column(String(18))
    tgl_pemeriksaan_bng = Column(DateTime)
    nip_pemeriksa_bng = Column(String(18))
    tgl_perekaman_bng = Column(DateTime)
    nip_perekam_bng = Column(String(18))
    __table_args__ = (
        ForeignKeyConstraint([kd_propinsi, kd_dati2, kd_kecamatan, kd_kelurahan,
            kd_blok, no_urut, kd_jns_op], [DatObjekPajak.kd_propinsi,
            DatObjekPajak.kd_dati2, DatObjekPajak.kd_kecamatan,
            DatObjekPajak.kd_kelurahan, DatObjekPajak.kd_blok,
            DatObjekPajak.no_urut, DatObjekPajak.kd_jns_op]),
            PBB_ARGS)
    @classmethod
    def query(cls):
        return pbbDBSession.query(cls)

    @classmethod
    def query_id(cls, id, no_bng):
        pkey = FixNop(id)
        query = cls.query()
        return query.filter(cls.kd_propinsi == pkey['kd_propinsi'],
                            cls.kd_dati2 == pkey['kd_dati2'],
                            cls.kd_kecamatan == pkey['kd_kecamatan'],
                            cls.kd_kelurahan == pkey['kd_kelurahan'],
                            cls.kd_blok == pkey['kd_blok'],
                            cls.no_urut == pkey['no_urut'],
                            cls.kd_jns_op == pkey['kd_jns_op'],
                            cls.no_bng == no_bng)
    @classmethod
    def add_dict(cls, row_dicted, row = None):
        # q = cls.query_id(row_dicted['id'], row_dicted['no_bumi'])
        # row = q.first()
        if not row:
            row = cls()
        row.from_dict(row_dicted)
        pbbDBSession.add(row)
        pbbDBSession.flush()
        total_luas_bng = cls.total_luas_bng(row_dicted['id']).scalar()
        row_dicted['total_luas_bng'] = total_luas_bng
        DatObjekPajak.set_luas_bng(row_dicted)
        return row

    @classmethod
    def total_luas_bng(cls, id):
        pkey = FixNop(id)
        query = pbbDBSession.query(func.sum(cls.luas_bng).label('total_luas_bng'))
        return query.filter(cls.kd_propinsi == pkey['kd_propinsi'],
                    cls.kd_dati2 == pkey['kd_dati2'],
                    cls.kd_kecamatan == pkey['kd_kecamatan'],
                    cls.kd_kelurahan == pkey['kd_kelurahan'],
                    cls.kd_blok == pkey['kd_blok'],
                    cls.no_urut == pkey['no_urut'],
                    cls.kd_jns_op == pkey['kd_jns_op'],
                    )
                            
class Fasilitas(pbbBase, CommonModel):
    __tablename__ = 'fasilitas'
    kd_fasilitas = Column(String(2), primary_key=True)
    nm_fasilitas = Column(String(50))
    satuan_fasilitas = Column(String(10))
    status_fasilitas = Column(String(1))
    ketergantungan = Column(String(1))
    __table_args__ = (PBB_ARGS,)
    @classmethod
    def query(cls):
        return pbbDBSession.query(cls)
        
    @classmethod
    def query_id(cls, id):
        query = cls.query()
        return query.filter(cls.kd_fasilitas == id,
                            )                            
class DatFasilitasBangunan(pbbBase, CommonModel):
    __tablename__ = 'dat_fasilitas_bangunan'
    kd_propinsi = Column(String(2), primary_key=True)
    kd_dati2 = Column(String(2), primary_key=True)
    kd_kecamatan = Column(String(3), primary_key=True)
    kd_kelurahan = Column(String(3), primary_key=True)
    kd_blok = Column(String(3), primary_key=True)
    no_urut = Column(String(4), primary_key=True)
    kd_jns_op = Column(String(1), primary_key=True)
    no_bng = Column(Integer, primary_key=True)
    kd_fasilitas = Column(String(2), primary_key=True)
    jml_satuan = Column(Integer)
    __table_args__ = (
        ForeignKeyConstraint([kd_propinsi, kd_dati2, kd_kecamatan, kd_kelurahan,
            kd_blok, no_urut, kd_jns_op, no_bng], [DatOpBangunan.kd_propinsi,
            DatOpBangunan.kd_dati2, DatOpBangunan.kd_kecamatan,
            DatOpBangunan.kd_kelurahan, DatOpBangunan.kd_blok, DatOpBangunan.no_urut,
            DatOpBangunan.kd_jns_op, DatOpBangunan.no_bng]),
        ForeignKeyConstraint([kd_fasilitas], [Fasilitas.kd_fasilitas]),
        PBB_ARGS)
    @classmethod
    def query(cls):
        return pbbDBSession.query(cls)

    @classmethod
    def query_id(cls, id, no_bng, kd_fasilitas):
        pkey = FixNop(id)
        query = cls.query()
        return query.filter_by(kd_propinsi = pkey['kd_propinsi'],
                            kd_dati2 = pkey['kd_dati2'],
                            kd_kecamatan = pkey['kd_kecamatan'],
                            kd_kelurahan = pkey['kd_kelurahan'],
                            kd_blok = pkey['kd_blok'],
                            no_urut = pkey['no_urut'],
                            kd_jns_op = pkey['kd_jns_op'],
                            no_bng = no_bng,
                            kd_fasilitas = kd_fasilitas)
                            
class TmpPendataan(pbbBase, CommonModel):
    __tablename__ = 'tmp_pendataan'
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
    kd_propinsi = Column(String(2), primary_key=True)
    kd_dati2 = Column(String(2), primary_key=True)
    kd_kecamatan = Column(String(3), primary_key=True)
    kd_kelurahan = Column(String(3), primary_key=True)
    kd_blok = Column(String(3), primary_key=True)
    no_urut = Column(String(4), primary_key=True)
    kd_jns_op = Column(String(1), primary_key=True)
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
    no_bumi = Column(Integer, primary_key=True)
    kd_znt = Column(String(2))
    luas_bumi = Column(Float)
    jns_bumi = Column(String(1))
    nilai_sistem_bumi = Column(Float)
    no_bng = Column(Integer, primary_key=True)
    kd_jpb = Column(String(2))
    no_formulir_lspop = Column(String(11))
    thn_dibangun_bng = Column(String(4))
    thn_renovasi_bng = Column(String(4))
    luas_bng = Column(Float)
    jml_lantai_bng = Column(Integer)
    kondisi_bng = Column(String(1))
    jns_konstruksi_bng = Column(String(1))
    jns_atap_bng = Column(String(1))
    kd_dinding = Column(String(1))
    kd_lantai = Column(String(1))
    kd_langit_langit = Column(String(1))
    nilai_sistem_bng = Column(Float)
    jns_transaksi_bng = Column(String(1))
    tgl_pendataan_bng = Column(DateTime)
    nip_pendata_bng = Column(String(18))
    tgl_pemeriksaan_bng = Column(DateTime)
    nip_pemeriksa_bng = Column(String(18))
    tgl_perekaman_bng = Column(DateTime)
    nip_perekam_bng = Column(String(18))
    kd_fasilitas = Column(String(2), primary_key=True)
    jml_satuan = Column(Integer)
    status = Column(Integer, nullable=False)
    tgl_proses = Column(DateTime)
    thn_pendataan = Column(String(4), primary_key=True)
    __table_args__ = (PBB_ARGS,)

    @classmethod
    def query(cls):
        return pbbDBSession.query(cls)

    @classmethod
    def query_data(cls):
        return pbbDBSession.query(cls.subjek_pajak_id, cls.nm_wp, cls.jalan_wp,
               cls.blok_kav_no_wp, cls.rw_wp, cls.rt_wp, cls.kelurahan_wp, 
               cls.kota_wp, cls.kd_pos_wp, cls.telp_wp, cls.npwp, 
               cls.status_pekerjaan_wp, cls.kd_propinsi, cls.kd_dati2, 
               cls.kd_kecamatan, cls.kd_kelurahan, cls.kd_blok, cls.no_urut,
               cls.kd_jns_op, cls.no_formulir_spop, cls.no_persil, cls.jalan_op, 
               cls.blok_kav_no_op, cls.rw_op, cls.rt_op, cls.kd_status_cabang, 
               cls.kd_status_wp, cls.total_luas_bumi, cls.total_luas_bng,
               cls.njop_bumi, cls.njop_bng, cls.status_peta_op, cls.jns_transaksi_op, 
               cls.tgl_pendataan_op, cls.nip_pendata, cls.tgl_pemeriksaan_op, 
               cls.nip_pemeriksa_op, cls.tgl_perekaman_op, cls.nip_perekam_op, 
               cls.no_bumi, cls.kd_znt, cls.luas_bumi, cls.jns_bumi, 
               cls.nilai_sistem_bumi, cls.no_bng, cls.kd_jpb, cls.no_formulir_lspop, 
               cls.thn_dibangun_bng, cls.thn_renovasi_bng, cls.luas_bng, 
               cls.jml_lantai_bng, cls.kondisi_bng, cls.jns_konstruksi_bng, 
               cls.jns_atap_bng, cls.kd_dinding, cls.kd_lantai, cls.kd_langit_langit, 
               cls.nilai_sistem_bng, cls.jns_transaksi_bng, cls.tgl_pendataan_bng, 
               cls.nip_pendata_bng, cls.tgl_pemeriksaan_bng, cls.nip_pemeriksa_bng, 
               cls.tgl_perekaman_bng, cls.nip_perekam_bng, cls.kd_fasilitas, 
               cls.jml_satuan, cls.status, cls.tgl_proses)

    @classmethod
    def query_id(cls,id):
        ids = id.split('.')
        pkey = FixSppt(ids[0])
        return cls.query().filter_by(
                kd_propinsi = pkey['kd_propinsi'],
                kd_dati2 = pkey['kd_dati2'],
                kd_kecamatan = pkey['kd_kecamatan'],
                kd_kelurahan = pkey['kd_kelurahan'],
                kd_blok = pkey['kd_blok'],
                no_urut = pkey['no_urut'],
                kd_jns_op = pkey['kd_jns_op'],
                thn_pendataan = pkey['thn_pajak_sppt'],
                no_bumi = ids[1],
                no_bng = ids[2],
                kd_fasilitas = ids[3])
#END OF SCRIPT