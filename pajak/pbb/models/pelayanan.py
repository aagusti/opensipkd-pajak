import sys
from datetime import datetime
from sqlalchemy import (
    Column, Integer, BigInteger, Float, Text, DateTime, ForeignKey, 
    UniqueConstraint, String, SmallInteger, types, func, ForeignKeyConstraint,
    literal_column, and_
    )
    
from sqlalchemy.orm import aliased

from sqlalchemy.orm.exc import NoResultFound

from sqlalchemy.orm import (
    relationship,
    backref,
    #primary_join
    )
import re
from ...tools import as_timezone #, FixLength
from ...pbb.tools import fixNopel, fixNop

from ...models import CommonModel
from ..models import pbbBase, pbbDBSession, pbb_schema

#from ref import Kelurahan, Kecamatan, Dati2, KELURAHAN, KECAMATAN
    
PBB_ARGS = {'extend_existing':True,  
        'schema': pbb_schema}    
        
class PstPermohonan(pbbBase, CommonModel):
    __tablename__ = 'pst_permohonan'
    __table_args__ = (PBB_ARGS,)
    kd_kanwil = Column(String(2), primary_key=True)
    kd_kantor = Column(String(2), primary_key=True)
    thn_pelayanan = Column(String(4), primary_key=True)
    bundel_pelayanan = Column(String(4), primary_key=True)
    no_urut_pelayanan = Column(String(3), primary_key=True)
    no_srt_permohonan = Column(String(30))
    tgl_surat_permohonan = Column(DateTime)
    nama_pemohon = Column(String(30))
    alamat_pemohon = Column(String(40))
    keterangan_pst = Column(String(75))
    catatan_pst = Column(String(75))
    status_kolektif = Column(String(1))
    tgl_terima_dokumen_wp = Column(DateTime)
    tgl_perkiraan_selesai = Column(DateTime)
    nip_penerima = Column(String(18))
    @classmethod
    def get_by_code(cls,code):
        fixNopel.set_raw(code)
        return pbbDBSession.query(cls).\
                    filter(cls.kd_kanwil == fixNopel['kd_kanwil'],
                              cls.kd_kantor == fixNopel['kd_kantor'],
                              cls.thn_pelayanan == fixNopel['tahun'],
                              cls.bundel_pelayanan == fixNopel['bundel'],
                              cls.no_urut_pelayanan == fixNopel['urut'],)

class PstLampiran(pbbBase, CommonModel):
    __tablename__ = 'pst_lampiran'
    kd_kanwil = Column(String(2), primary_key=True)
    kd_kantor = Column(String(2), primary_key=True)
    thn_pelayanan = Column(String(4), primary_key=True)
    bundel_pelayanan = Column(String(4), primary_key=True)
    no_urut_pelayanan = Column(String(3), primary_key=True)
    l_permohonan = Column(Integer)
    l_surat_kuasa = Column(Integer)
    l_ktp_wp = Column(Integer)
    l_sertifikat_tanah = Column(Integer)
    l_sppt = Column(Integer)
    l_imb = Column(Integer)
    l_akte_jual_beli = Column(Integer)
    l_sk_pensiun = Column(Integer)
    l_sppt_stts = Column(Integer)
    l_stts = Column(Integer)
    l_sk_pengurangan = Column(Integer)
    l_sk_keberatan = Column(Integer)
    l_skkp_pbb = Column(Integer)
    l_spmkp_pbb = Column(Integer)
    l_lain_lain = Column(Integer)
    l_cagar = Column(Integer)
    l_penghasilan = Column(Integer)
    l_npwpd = Column(Integer)
    l_sket_lurah = Column(Integer)
    l_sket_tanah = Column(Integer)
    __table_args__ = (ForeignKeyConstraint([kd_kanwil, kd_kantor, thn_pelayanan,
        bundel_pelayanan, no_urut_pelayanan], [PstPermohonan.kd_kanwil, 
        PstPermohonan.kd_kantor, PstPermohonan.thn_pelayanan, 
        PstPermohonan.bundel_pelayanan, PstPermohonan.no_urut_pelayanan]), 
        PBB_ARGS,)
    
    
class PstDetail(pbbBase, CommonModel):
    __tablename__ = 'pst_detail'
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
    kd_jns_pelayanan = Column(String(2), primary_key=True)
    thn_pajak_permohonan = Column(String(4), primary_key=True)
    nama_penerima = Column(String(30))
    catatan_penyerahan = Column(String(75))
    status_selesai = Column(Integer)
    tgl_selesai = Column(DateTime)
    kd_seksi_berkas = Column(String(2))
    tgl_penyerahan = Column(DateTime)
    nip_penyerah = Column(String(18))
    __table_args__ = (ForeignKeyConstraint([kd_kanwil, kd_kantor, thn_pelayanan,
            bundel_pelayanan, no_urut_pelayanan], [PstPermohonan.kd_kanwil,
            PstPermohonan.kd_kantor, PstPermohonan.thn_pelayanan, 
            PstPermohonan.bundel_pelayanan, PstPermohonan.no_urut_pelayanan]),
            PBB_ARGS,)
    @classmethod
    def get_by_code(cls,code_nopel,code_nop):
        fixNopel.set_raw(code_nopel)
        fixNop.set_raw(code_nop)
        return pbbDBSession.query(cls).\
                    filter(cls.kd_kanwil == fixNopel['kd_kanwil'],
                            cls.kd_kantor == fixNopel['kd_kantor'],
                            cls.thn_pelayanan == fixNopel['tahun'],
                            cls.bundel_pelayanan == fixNopel['bundel'],
                            cls.no_urut_pelayanan == fixNopel['urut'],
                            cls.kd_propinsi_pemohon == fixNop["kd_propinsi"],
                            cls.kd_dati2_pemohon == fixNop["kd_dati2"],
                            cls.kd_kecamatan_pemohon == fixNop["kd_kecamatan"],
                            cls.kd_kelurahan_pemohon == fixNop["kd_kelurahan"],
                            cls.kd_blok_pemohon == fixNop["kd_blok"],
                            cls.no_urut_pemohon == fixNop["no_urut"],
                            cls.kd_jns_op_pemohon == fixNop["kd_jns_op"])
    
class PstDataOpBaru(pbbBase, CommonModel):
    __tablename__ = 'pst_data_op_baru'
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
    nama_wp_baru = Column(String(30))
    letak_op_baru = Column(String(35))
    __table_args__ = (
        ForeignKeyConstraint([kd_kanwil, kd_kantor, thn_pelayanan, bundel_pelayanan, no_urut_pelayanan], [PstPermohonan.kd_kanwil, PstPermohonan.kd_kantor, PstPermohonan.thn_pelayanan, PstPermohonan.bundel_pelayanan, PstPermohonan.no_urut_pelayanan]), PBB_ARGS,)

class PstPermohonanPengurangan(pbbBase, CommonModel):
    __tablename__ = 'pst_permohonan_pengurangan'
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
    jns_pengurangan = Column(String(1))
    pct_permohonan_pengurangan = Column(Integer)
    __table_args__ = (
        ForeignKeyConstraint([kd_kanwil, kd_kantor, thn_pelayanan, bundel_pelayanan, no_urut_pelayanan], [PstPermohonan.kd_kanwil, PstPermohonan.kd_kantor, PstPermohonan.thn_pelayanan, PstPermohonan.bundel_pelayanan, PstPermohonan.no_urut_pelayanan]),PBB_ARGS)

