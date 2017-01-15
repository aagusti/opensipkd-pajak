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
from ...pbb.tools import FixNopel, FixNop

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
    def query(cls):
        return pbbDBSession.query(cls)
    
    @classmethod
    def query_id(cls,id):
        fixNopel = FixNopel(id)
        return cls.query().\
                    filter(cls.kd_kanwil == fixNopel['kd_kanwil'],
                              cls.kd_kantor == fixNopel['kd_kantor'],
                              cls.thn_pelayanan == fixNopel['tahun'],
                              cls.bundel_pelayanan == fixNopel['bundel'],
                              cls.no_urut_pelayanan == fixNopel['urut'],)
    
    @classmethod
    def get_by_code(cls,code):
        fixNopel = FixNopel(code)
        return cls.query().\
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

    @classmethod
    def query(cls):
        return pbbDBSession.query(cls)
        
    @classmethod
    def query_id(cls,id):
        fixNopel = FixNopel(id)
        return cls.query().\
                    filter(cls.kd_kanwil == fixNopel['kd_kanwil'],
                              cls.kd_kantor == fixNopel['kd_kantor'],
                              cls.thn_pelayanan == fixNopel['tahun'],
                              cls.bundel_pelayanan == fixNopel['bundel'],
                              cls.no_urut_pelayanan == fixNopel['urut'],)
    
    
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
    def query(cls):
        return pbbDBSession.query(cls)
        
    @classmethod
    def query_id(cls,id):
        fixNopelDet = FixNopelDet(id)
        return cls.query().\
                    filter(cls.kd_kanwil == fixNopelDet['kd_kanwil'],
                            cls.kd_kantor == fixNopelDet['kd_kantor'],
                            cls.thn_pelayanan == fixNopelDet['tahun'],
                            cls.bundel_pelayanan == fixNopelDet['bundel'],
                            cls.no_urut_pelayanan == fixNopelDet['urut'],
                            cls.kd_propinsi_pemohon == fixNopelDet["kd_propinsi"],
                            cls.kd_dati2_pemohon == fixNopelDet["kd_dati2"],
                            cls.kd_kecamatan_pemohon == fixNopelDet["kd_kecamatan"],
                            cls.kd_kelurahan_pemohon == fixNopelDet["kd_kelurahan"],
                            cls.kd_blok_pemohon == fixNopelDet["kd_blok"],
                            cls.no_urut_pemohon == fixNopelDet["no_urut"],
                            cls.kd_jns_op_pemohon == fixNopelDet["kd_jns_op"])
                              
    @classmethod
    def get_by_code(cls,code_nopel,code_nop):
        fixNopel = FixNopel(code_nopel)
        fixNop = FixNop(code_nop)
        return cls.query().\
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
        ForeignKeyConstraint([kd_kanwil, kd_kantor, thn_pelayanan, 
                bundel_pelayanan, no_urut_pelayanan], 
                [PstPermohonan.kd_kanwil, PstPermohonan.kd_kantor, 
                 PstPermohonan.thn_pelayanan, PstPermohonan.bundel_pelayanan, 
                 PstPermohonan.no_urut_pelayanan]), PBB_ARGS,)
                 
    @classmethod
    def query(cls):
        return pbbDBSession.query(cls)
        
    @classmethod
    def query_id(cls,id):
        fixNopelDet = FixNopelDet(id)
        return cls.query().\
                    filter(cls.kd_kanwil == fixNopelDet['kd_kanwil'],
                            cls.kd_kantor == fixNopelDet['kd_kantor'],
                            cls.thn_pelayanan == fixNopelDet['tahun'],
                            cls.bundel_pelayanan == fixNopelDet['bundel'],
                            cls.no_urut_pelayanan == fixNopelDet['urut'],
                            cls.kd_propinsi_pemohon == fixNopelDet["kd_propinsi"],
                            cls.kd_dati2_pemohon == fixNopelDet["kd_dati2"],
                            cls.kd_kecamatan_pemohon == fixNopelDet["kd_kecamatan"],
                            cls.kd_kelurahan_pemohon == fixNopelDet["kd_kelurahan"],
                            cls.kd_blok_pemohon == fixNopelDet["kd_blok"],
                            cls.no_urut_pemohon == fixNopelDet["no_urut"],
                            cls.kd_jns_op_pemohon == fixNopelDet["kd_jns_op"])

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
        ForeignKeyConstraint([kd_kanwil, kd_kantor, thn_pelayanan, bundel_pelayanan,
                              no_urut_pelayanan], 
                             [PstPermohonan.kd_kanwil, PstPermohonan.kd_kantor, 
                              PstPermohonan.thn_pelayanan, PstPermohonan.bundel_pelayanan, 
                              PstPermohonan.no_urut_pelayanan]),PBB_ARGS)
                              
    @classmethod
    def query(cls):
        return pbbDBSession.query(cls)
        
    @classmethod
    def query_id(cls,id):
        fixNopelDet = FixNopelDet(id)
        return cls.query().\
                    filter(cls.kd_kanwil == fixNopelDet['kd_kanwil'],
                            cls.kd_kantor == fixNopelDet['kd_kantor'],
                            cls.thn_pelayanan == fixNopelDet['tahun'],
                            cls.bundel_pelayanan == fixNopelDet['bundel'],
                            cls.no_urut_pelayanan == fixNopelDet['urut'],
                            cls.kd_propinsi_pemohon == fixNopelDet["kd_propinsi"],
                            cls.kd_dati2_pemohon == fixNopelDet["kd_dati2"],
                            cls.kd_kecamatan_pemohon == fixNopelDet["kd_kecamatan"],
                            cls.kd_kelurahan_pemohon == fixNopelDet["kd_kelurahan"],
                            cls.kd_blok_pemohon == fixNopelDet["kd_blok"],
                            cls.no_urut_pemohon == fixNopelDet["no_urut"],
                            cls.kd_jns_op_pemohon == fixNopelDet["kd_jns_op"])

class MaxUrutPstOl(pbbBase, CommonModel):
    __tablename__  = 'max_urut_pst_ol'
    __table_args__ = (PBB_ARGS)
    kd_kanwil = Column(String(2), primary_key=True)          
    kd_kantor = Column(String(2), primary_key=True)
    thn_pelayanan = Column(String(4))           
    bundel_pelayanan = Column(String(4))
    no_urut_pelayanan = Column(String(3))
                 
    @classmethod
    def query(cls):
        return pbbDBSession.query(cls)
        

    @classmethod
    def get_nopel(cls, request):
        settings = request.registry.settings
        
        thn_pelayanan = datetime.now().strftime('%Y')
        row = cls.query().first()
        if not row:
            row = cls()
            row.kd_kanwil = settings['pbb_kd_kanwil']
            row.kd_kantor = settings['pbb_kd_kantor']
            row.thn_pelayanan = thn_pelayanan
            row.bundel_pelayanan = '9000'
            row.no_urut_pelayanan = '000'
            
        if row.thn_pelayanan!=thn_pelayanan:
            row.thn_pelayanan = thn_pelayanan
            row.bundel_pelayanan = '9000'
            row.no_urut_pelayanan = '000'
            
        bundel_pelayanan = int(row.bundel_pelayanan)
        no_urut_pelayanan = int(row.no_urut_pelayanan)
        if no_urut_pelayanan == 999:
            bundel_pelayanan +=1
            no_urut_pelayanan = 1
        else:    
            no_urut_pelayanan += 1
            
        row.thn_pelayanan = thn_pelayanan
        row.bundel_pelayanan = str(bundel_pelayanan).zfill(4)
        row.no_urut_pelayanan = str(no_urut_pelayanan).zfill(3)
        pbb_DBSession.add(row)
        pbb_DBSession.flush()
        return (row.kd_kanwil, row.kd_kantor, row.thn_pelayanan, row.bundel_pelayanan, row.no_urut_pelayanan)
