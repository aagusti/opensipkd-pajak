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
from ..tools import clsNop, hitung_denda, clsBayar, clsSppt
from ...models import CommonModel
from ..models import pbbBase, pbbDBSession, pbb_schema

#from ref import Kelurahan, Kecamatan, Dati2, KELURAHAN, KECAMATAN
    
PBB_ARGS = {'extend_existing':True,  
        #'autoload':True,
        'schema': pbb_schema}    

class SaldoAwal(pbbBase, CommonModel):
    __tablename__  = 'saldo_awal'
    __table_args__ = {'extend_existing':True, 
                      'schema': pbb_schema}    

    id          = Column(BigInteger, primary_key=True)
    tahun       = Column(String(4))
    tahun_tetap = Column(String(4))
    uraian      = Column(String(200))
    nilai       = Column(BigInteger)
    posted      = Column(Integer)
    created      = Column(DateTime)
    create_uid   = Column(Integer)
    updated      = Column(DateTime)
    update_uid   = Column(Integer)
                      
class Sppt(pbbBase, CommonModel):
    __tablename__  = 'sppt'
    __table_args__ = PBB_ARGS
    kd_propinsi = Column(String(2), primary_key=True)
    kd_dati2 = Column(String(2), primary_key=True)
    kd_kecamatan = Column(String(3), primary_key=True)
    kd_kelurahan = Column(String(3), primary_key=True)
    kd_blok = Column(String(3), primary_key=True)
    no_urut = Column(String(4), primary_key=True)
    kd_jns_op = Column(String(1), primary_key=True)
    thn_pajak_sppt = Column(String(4), primary_key=True)
    siklus_sppt                          = Column(Integer)                 
    kd_kanwil                            = Column(String(2))
    kd_kantor                            = Column(String(2))
    kd_tp                                = Column(String(2))
    nm_wp_sppt                           = Column(String(30))
    jln_wp_sppt                          = Column(String(30))
    blok_kav_no_wp_sppt                  = Column(String(15))
    rw_wp_sppt                           = Column(String(2))
    rt_wp_sppt                           = Column(String(3))
    kelurahan_wp_sppt                    = Column(String(30))
    kota_wp_sppt                         = Column(String(30))
    kd_pos_wp_sppt                       = Column(String(5))
    npwp_sppt                            = Column(String(15))
    no_persil_sppt                       = Column(String(5))
    kd_kls_tanah                         = Column(String(3))
    thn_awal_kls_tanah                   = Column(String(4))
    kd_kls_bng                           = Column(String(3))
    thn_awal_kls_bng                     = Column(String(4))
    tgl_jatuh_tempo_sppt                 = Column(DateTime(timezone=False))
    luas_bumi_sppt                       = Column(BigInteger)
    luas_bng_sppt                        = Column(BigInteger)
    njop_bumi_sppt                       = Column(BigInteger)
    njop_bng_sppt                        = Column(BigInteger)
    njop_sppt                            = Column(BigInteger)
    njoptkp_sppt                         = Column(BigInteger)                
    pbb_terhutang_sppt                   = Column(BigInteger)
    faktor_pengurang_sppt                = Column(BigInteger)
    pbb_yg_harus_dibayar_sppt            = Column(BigInteger)
    status_pembayaran_sppt               = Column(String(1))
    status_tagihan_sppt                  = Column(String(1))
    status_cetak_sppt                    = Column(String(1))
    tgl_terbit_sppt                      = Column(DateTime(timezone=False))
    tgl_cetak_sppt                       = Column(DateTime(timezone=False))
    nip_pencetak_sppt                    = Column(String(18))
    posted                               = Column(Integer)
    
    @classmethod
    def query_by_nop(cls, nop):
        fxNop = clsNop(nop)
        return pbbDBSession.query(cls).\
            filter(cls.kd_propinsi == fxNop.kd_propinsi,
                cls.kd_dati2 == fxNop.kd_dati2,
                cls.kd_kecamatan == fxNop.kd_kecamatan,
                cls.kd_kelurahan == fxNop.kd_kelurahan,
                cls.kd_blok == fxNop.kd_blok,
                cls.no_urut == fxNop.no_urut,
                cls.kd_jns_op == fxNop.kd_jns_op)
    
    @classmethod
    def piutang(cls, nop, tahun, tanggal):
        row = cls.query_by_nop(nop).\
            filter(cls.thn_pajak_sppt == tahun,
                   cls.status_pembayaran_sppt<'2').first()
        if not row:
            return
        pokok = row.pbb_yg_harus_dibayar_sppt
        jatuh_tempo = row.tgl_jatuh_tempo_sppt    
        bayar = PembayaranSppt.get_bayar(nop,tahun).first()
        ke = 1
        print "***************bayar", bayar
        if bayar.bayar or bayar.denda or bayar.ke:
            pokok -= (bayar.bayar - bayar.denda)
            ke = bayar.ke+1
        denda = hitung_denda(pokok, jatuh_tempo, tanggal)
        
        return dict(pokok = pokok,
                    denda = denda,
                    jatuh_tempo = jatuh_tempo,
                    ke = ke)
                    
    @classmethod
    def set_status(cls, id, status):
        fxSppt = clsSppt(id)
        row = cls.query_by_nop(id).\
            filter(cls.thn_pajak_sppt == fxSppt.thn_pajak_sppt).first()
        if row:
            row.status_pembayaran_sppt = status
            pbbDBSession.add(row)
            pbbDBSession.flush()
        return row
            
class SpptAkrual(pbbBase, CommonModel):
    __tablename__  = 'sppt_akrual'
    __table_args__ = PBB_ARGS
    kd_propinsi = Column(String(2), primary_key=True)
    kd_dati2 = Column(String(2), primary_key=True)
    kd_kecamatan = Column(String(3), primary_key=True)
    kd_kelurahan = Column(String(3), primary_key=True)
    kd_blok = Column(String(3), primary_key=True)
    no_urut = Column(String(4), primary_key=True)
    kd_jns_op = Column(String(1), primary_key=True)
    thn_pajak_sppt = Column(String(4), primary_key=True)
    siklus_sppt = Column(Integer, primary_key=True)
    siklus_sppt                          = Column(Integer)                 
    kd_kanwil                            = Column(String(2))
    kd_kantor                            = Column(String(2))
    kd_tp                                = Column(String(2))
    nm_wp_sppt                           = Column(String(30))
    jln_wp_sppt                          = Column(String(30))
    blok_kav_no_wp_sppt                  = Column(String(15))
    rw_wp_sppt                           = Column(String(2))
    rt_wp_sppt                           = Column(String(3))
    kelurahan_wp_sppt                    = Column(String(30))
    kota_wp_sppt                         = Column(String(30))
    kd_pos_wp_sppt                       = Column(String(5))
    npwp_sppt                            = Column(String(15))
    no_persil_sppt                       = Column(String(5))
    kd_kls_tanah                         = Column(String(3))
    thn_awal_kls_tanah                   = Column(String(4))
    kd_kls_bng                           = Column(String(3))
    thn_awal_kls_bng                     = Column(String(4))
    tgl_jatuh_tempo_sppt                 = Column(DateTime(timezone=False))
    luas_bumi_sppt                       = Column(BigInteger)
    luas_bng_sppt                        = Column(BigInteger)
    njop_bumi_sppt                       = Column(BigInteger)
    njop_bng_sppt                        = Column(BigInteger)
    njop_sppt                            = Column(BigInteger)
    njoptkp_sppt                         = Column(BigInteger)                
    pbb_terhutang_sppt                   = Column(BigInteger)
    faktor_pengurang_sppt                = Column(BigInteger)
    pbb_yg_harus_dibayar_sppt            = Column(BigInteger)
    status_pembayaran_sppt               = Column(String(1))
    status_tagihan_sppt                  = Column(String(1))
    status_cetak_sppt                    = Column(String(1))
    tgl_terbit_sppt                      = Column(DateTime(timezone=False))
    tgl_cetak_sppt                       = Column(DateTime(timezone=False))
    nip_pencetak_sppt                    = Column(String(18))
    posted                               = Column(Integer)
    create_date                          = Column(DateTime(timezone=False))
    
class SpptRekap(pbbBase, CommonModel):
    __tablename__  = 'sppt_rekap'
    __table_args__ = PBB_ARGS 
    id          = Column(BigInteger, primary_key=True)
    tanggal     = Column(DateTime)
    kode      = Column(String(30))
    uraian      = Column(String(200))
    pokok       = Column(BigInteger)
    posted      = Column(Integer)
    created      = Column(DateTime)
    create_uid   = Column(Integer)
    updated      = Column(DateTime)
    update_uid   = Column(Integer)
    
    
class PembayaranSppt(pbbBase, CommonModel):
    __tablename__  = 'pembayaran_sppt'
    __table_args__ = (
                      # ForeignKeyConstraint(['kd_propinsi','kd_dati2','kd_kecamatan','kd_kelurahan',
                              # 'kd_blok', 'no_urut','kd_jns_op', 'thn_pajak_sppt'], 
                              # ['sppt.kd_propinsi', 'sppt.kd_dati2',
                               # 'sppt.kd_kecamatan','sppt.kd_kelurahan',
                               # 'sppt.kd_blok', 'sppt.no_urut',
                               # 'sppt.kd_jns_op','sppt.thn_pajak_sppt']),
                      PBB_ARGS)
    kd_propinsi = Column(String(2), primary_key=True)
    kd_dati2 = Column(String(2), primary_key=True)
    kd_kecamatan = Column(String(3), primary_key=True)
    kd_kelurahan = Column(String(3), primary_key=True)
    kd_blok = Column(String(3), primary_key=True)
    no_urut = Column(String(4), primary_key=True)
    kd_jns_op = Column(String(1), primary_key=True)
    thn_pajak_sppt = Column(String(4), primary_key=True)
    pembayaran_sppt_ke = Column(Integer, primary_key=True)
    kd_kanwil           = Column(String(2)) 
    kd_kantor           = Column(String(2)) 
    kd_tp               = Column(String(2)) 
    denda_sppt          = Column(BigInteger) 
    jml_sppt_yg_dibayar = Column(BigInteger) 
    tgl_pembayaran_sppt = Column(DateTime(timezone=False)) 
    tgl_rekam_byr_sppt  = Column(DateTime(timezone=False))
    nip_rekam_byr_sppt  = Column(String(18)) 
    posted              = Column(Integer) 

    @classmethod
    def query_by_nop(cls, nop):
        fxNop = clsNop(nop)
        return pbbDBSession.query(cls).\
            filter(cls.kd_propinsi == fxNop.kd_propinsi,
                cls.kd_dati2 == fxNop.kd_dati2,
                cls.kd_kecamatan == fxNop.kd_kecamatan,
                cls.kd_kelurahan == fxNop.kd_kelurahan,
                cls.kd_blok == fxNop.kd_blok,
                cls.no_urut == fxNop.no_urut,
                cls.kd_jns_op == fxNop.kd_jns_op)
                
    @classmethod
    def query_id(cls,id):
        fxBayar = clsBayar(id)
        return cls.query_by_nop(id).\
               filter(
                PembayaranSppt.thn_pajak_sppt==fxBayar.thn_pajak_sppt,
                PembayaranSppt.kd_kanwil==fxBayar.kd_kanwil,
                PembayaranSppt.kd_kantor==fxBayar.kd_kantor,
                PembayaranSppt.kd_tp==fxBayar.kd_tp,
                PembayaranSppt.pembayaran_sppt_ke==fxBayar.pembayaran_sppt_ke,
                )
                
    @classmethod
    def reversal(cls, id):
        fxBayar = clsBayar(id)
        q = cls.query_id(id)
        row = q.first()
        if row:
            row.denda_sppt = 0
            row.jml_sppt_yg_dibayar = 0
            pbbDBSession.add(row)
            pbbDBSession.flush()
            Sppt.set_status(id,0)
        return row
        
    @classmethod
    def get_bayar(cls, nop, tahun):
        fxNop = clsNop(nop)
        q = pbbDBSession.query(func.sum(cls.denda_sppt).label("denda"),
                                 func.sum(cls.jml_sppt_yg_dibayar).label("bayar"),
                                 func.max(cls.pembayaran_sppt_ke).label("ke")).\
            filter(cls.kd_propinsi == fxNop.kd_propinsi,
                cls.kd_dati2 == fxNop.kd_dati2,
                cls.kd_kecamatan == fxNop.kd_kecamatan,
                cls.kd_kelurahan == fxNop.kd_kelurahan,
                cls.kd_blok == fxNop.kd_blok,
                cls.no_urut == fxNop.no_urut,
                cls.kd_jns_op == fxNop.kd_jns_op,
                cls.thn_pajak_sppt == tahun)
        if not q:
            return
        return q
                    
class PembayaranRekap(pbbBase, CommonModel):
    __tablename__  = 'pembayaran_sppt_rekap'
    __table_args__ = PBB_ARGS  

    id          = Column(BigInteger, primary_key=True)
    tanggal     = Column(DateTime)
    kode      = Column(String(30))
    uraian      = Column(String(200))
    denda       = Column(BigInteger)
    bayar       = Column(BigInteger)
    posted      = Column(Integer)
    created      = Column(DateTime)
    create_uid   = Column(Integer)
    updated      = Column(DateTime)
    update_uid   = Column(Integer)
    
    