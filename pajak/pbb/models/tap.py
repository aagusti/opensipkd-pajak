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
    scoped_session,
    sessionmaker,
    relationship,
    backref,
    #primary_join
    )
import re
from ...tools import as_timezone 
from ..tools import FixNop, hitung_denda, FixBayar, FixSppt
from ...models import CommonModel
from ..models import pbbBase, pbbDBSession, pbb_schema
from ..models.ref import Kelurahan, Kecamatan, Dati2
from pendataan import DatObjekPajak
    
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
    def query(cls):
        return pbbDBSession.query(cls)
        
    @classmethod
    def query_id(cls, id):
        fxSppt = FixSppt(id)
        return cls.query().filter(
                cls.kd_propinsi == fxSppt.kd_propinsi,
                cls.kd_dati2 == fxSppt.kd_dati2,
                cls.kd_kecamatan == fxSppt.kd_kecamatan,
                cls.kd_kelurahan == fxSppt.kd_kelurahan,
                cls.kd_blok == fxSppt.kd_blok,
                cls.no_urut == fxSppt.no_urut,
                cls.kd_jns_op == fxSppt.kd_jns_op,
                cls.thn_pajak_sppt == fxSppt.thn_pajak_sppt)
    
    @classmethod
    def query_data(cls):
        return cls.query()
        
    @classmethod
    def count(cls, p_kode):
        fxNop = FixNop(p_kode)
        query = pbbDBSession.query(func.count(cls.kd_propinsi))
        return query.filter(
                cls.kd_propinsi == fxNop.kd_propinsi,
                cls.kd_dati2 == fxNop.kd_dati2,
                cls.kd_kecamatan == fxNop.kd_kecamatan,
                cls.kd_kelurahan == fxNop.kd_kelurahan,
                cls.kd_blok == fxNop.kd_blok,
                cls.no_urut == fxNop.no_urut,
                cls.kd_jns_op == fxNop.kd_jns_op).scalar()
                
    @classmethod
    def get_by_nop(cls, p_kode):
        fxNop = FixNop(p_kode)
        query = cls.query()
        return query.filter_by(
                cls.kd_propinsi == fxNop.kd_propinsi,
                cls.kd_dati2 == fxNop.kd_dati2,
                cls.kd_kecamatan == fxNop.kd_kecamatan,
                cls.kd_kelurahan == fxNop.kd_kelurahan,
                cls.kd_blok == fxNop.kd_blok,
                cls.no_urut == fxNop.no_urut,
                cls.kd_jns_op == fxNop.kd_jns_op)
                
    @classmethod
    def get_by_nop_thn(cls, p_kode, p_tahun):
        return cls.query_id(p_kode+p_tahun)
                
    @classmethod
    def query_by_nop(cls, nop):
        return cls.get_by_nop(nop)
        
    @classmethod
    def piutang(cls, nop, tahun, tanggal):
        row = cls.query_id(nop+tahun).\
            filter(cls.thn_pajak_sppt == tahun,
                   cls.status_pembayaran_sppt<'2').first()
        if not row:
            return
        pokok = row.pbb_yg_harus_dibayar_sppt
        jatuh_tempo = row.tgl_jatuh_tempo_sppt    
        bayar = PembayaranSppt.get_bayar(nop,tahun).first()
        ke = 1
        if bayar.bayar or bayar.denda or bayar.ke:
            pokok -= (bayar.bayar - bayar.denda)
            ke = bayar.ke+1
        denda = hitung_denda(pokok, jatuh_tempo, tanggal)
        
        return dict(pokok = pokok,
                    denda = denda,
                    jatuh_tempo = jatuh_tempo,
                    ke = ke)
    @classmethod
    def get_bayar(cls, p_kode):
        fxNop = FixNop(p_kode)
        query = pbbDBSession.query(
              func.concat(cls.kd_propinsi, '.').\
                   concat(cls.kd_dati2).concat('-').\
                   concat(cls.kd_kecamatan).concat('.').\
                   concat(cls.kd_kelurahan).concat('-').\
                   concat(cls.kd_blok).concat('.').\
                   concat(cls.no_urut).concat('-').\
                   concat(cls.kd_jns_op).label('nop'), 
            cls.thn_pajak_sppt,
			cls.nm_wp_sppt,	cls.jln_wp_sppt, cls.blok_kav_no_wp_sppt,
			cls.rw_wp_sppt, cls.rt_wp_sppt, cls.kelurahan_wp_sppt,
            cls.kota_wp_sppt, cls.kd_pos_wp_sppt, cls.npwp_sppt, 
            cls.kd_kls_tanah, cls.kd_kls_bng, 
			cls.luas_bumi_sppt, cls.luas_bng_sppt, 
            cls.njop_bumi_sppt, cls.njop_bng_sppt, cls.njop_sppt,			
			cls.njoptkp_sppt, cls.pbb_terhutang_sppt, cls.faktor_pengurang_sppt,
			cls.status_pembayaran_sppt, 
            cls.tgl_jatuh_tempo_sppt,
			cls.pbb_yg_harus_dibayar_sppt.label('pokok'),
            func.max(PembayaranSppt.tgl_pembayaran_sppt).label('tgl_pembayaran_sppt'),
            func.sum(func.coalesce(PembayaranSppt.jml_sppt_yg_dibayar,0)).label('bayar'),
            func.sum(func.coalesce(PembayaranSppt.denda_sppt,0)).label('denda_sppt'),).\
			outerjoin(PembayaranSppt,and_(
                            cls.kd_propinsi==PembayaranSppt.kd_propinsi,
                            cls.kd_dati2==PembayaranSppt.kd_dati2,
                            cls.kd_kecamatan==PembayaranSppt.kd_kecamatan,
                            cls.kd_kelurahan==PembayaranSppt.kd_kelurahan,
                            cls.kd_blok==PembayaranSppt.kd_blok,
                            cls.no_urut==PembayaranSppt.no_urut,
                            cls.kd_jns_op==PembayaranSppt.kd_jns_op,
                            cls.thn_pajak_sppt==PembayaranSppt.thn_pajak_sppt
                            )).\
            group_by(cls.kd_propinsi, cls.kd_dati2, cls.kd_kecamatan, cls.kd_kelurahan, 
                    cls.kd_blok, cls.no_urut, cls.kd_jns_op, cls.thn_pajak_sppt,
                    cls.nm_wp_sppt,	cls.jln_wp_sppt, cls.blok_kav_no_wp_sppt,
                    cls.rw_wp_sppt, cls.rt_wp_sppt, cls.kelurahan_wp_sppt,
                    cls.kota_wp_sppt, cls.kd_pos_wp_sppt, cls.npwp_sppt, 
                    cls.kd_kls_tanah, cls.kd_kls_bng, 
                    cls.luas_bumi_sppt, cls.luas_bng_sppt, 
                    cls.njop_bumi_sppt, cls.njop_bng_sppt, cls.njop_sppt,			
                    cls.njoptkp_sppt, cls.pbb_terhutang_sppt, cls.faktor_pengurang_sppt,
                    cls.status_pembayaran_sppt, 
                    cls.tgl_jatuh_tempo_sppt,
                    cls.pbb_yg_harus_dibayar_sppt.label('pokok'),)
            
        return query.filter(
                cls.kd_propinsi == fxNop.kd_propinsi,
                cls.kd_dati2 == fxNop.kd_dati2,
                cls.kd_kecamatan == fxNop.kd_kecamatan,
                cls.kd_kelurahan == fxNop.kd_kelurahan,
                cls.kd_blok == fxNop.kd_blok,
                cls.no_urut == fxNop.no_urut,
                cls.kd_jns_op == fxNop.kd_jns_op)
                            
    @classmethod
    def set_status(cls, id, status):
        row = cls.query_id(id).first()
        if row:
            row.status_pembayaran_sppt = status
            pbbDBSession.add(row)
            pbbDBSession.flush()
        return row
        
    @classmethod
    def get_info_op(cls, p_kode):
        fxNop = FixNop(p_kode)
        query = pbbDBSession.query(
              func.concat(cls.kd_propinsi, '.').\
                   concat(cls.kd_dati2).concat('-').\
                   concat(cls.kd_kecamatan).concat('.').\
                   concat(cls.kd_kelurahan).concat('-').\
                   concat(cls.kd_blok).concat('.').\
                   concat(cls.no_urut).concat('-').\
                   concat(cls.kd_jns_op).label('nop'),
              cls.thn_pajak_sppt, cls.nm_wp_sppt.label('nm_wp'),
              func.concat(cls.jln_wp_sppt,', ').concat(cls.blok_kav_no_wp_sppt).label('alamat_wp'),
              func.concat(cls.rt_wp_sppt, ' / ').concat(cls.rw_wp_sppt).label('rt_rw_wp'),
              cls.kelurahan_wp_sppt.label('kelurahan_wp'), cls.kota_wp_sppt.label('kota_wp'), 
              cls.luas_bumi_sppt.label('luas_tanah'), cls.njop_bumi_sppt.label('njop_tanah'),
              cls.luas_bng_sppt.label('luas_bng'),cls.njop_bng_sppt.label('njop_bng'),
              cls.pbb_yg_harus_dibayar_sppt.label('ketetapan'), 
              cls.status_pembayaran_sppt.label('status_bayar'),
              func.concat(DatObjekPajak.jalan_op,', ').concat(DatObjekPajak.blok_kav_no_op).label('alamat_op'),
              func.concat(DatObjekPajak.rt_op,' / ').concat(DatObjekPajak.rw_op).label('rt_rw_op'),).\
              filter(cls.kd_propinsi == DatObjekPajak.kd_propinsi, 
                     cls.kd_dati2 == DatObjekPajak.kd_dati2, 
                     cls.kd_kecamatan == DatObjekPajak.kd_kecamatan, 
                     cls.kd_kelurahan == DatObjekPajak.kd_kelurahan, 
                     cls.kd_blok == DatObjekPajak.kd_blok, 
                     cls.no_urut == DatObjekPajak.no_urut, 
                     cls.kd_jns_op == DatObjekPajak.kd_jns_op)
        return query.filter(
                    cls.kd_propinsi == fxNop.kd_propinsi,
                    cls.kd_dati2 == fxNop.kd_dati2,
                    cls.kd_kecamatan == fxNop.kd_kecamatan,
                    cls.kd_kelurahan == fxNop.kd_kelurahan,
                    cls.kd_blok == fxNop.kd_blok,
                    cls.no_urut == fxNop.no_urut,
                    cls.kd_jns_op == fxNop.kd_jns_op)
    @classmethod
    def get_info_op_bphtb(cls, p_kode, p_tahun):
        fxNop = FixNop(p_kode)
        q = pbbDBSession.query(cls.luas_bumi_sppt, cls.luas_bng_sppt,
                cls.njop_bumi_sppt, cls.njop_bng_sppt, DatObjekPajak.jalan_op,
                DatObjekPajak.blok_kav_no_op, DatObjekPajak.rt_op, DatObjekPajak.rw_op,
                cls.nm_wp_sppt.label('nm_wp'),
                func.coalesce(SpptOpBersama.luas_bumi_beban_sppt,0).label('luas_bumi_beban'),
                func.coalesce(SpptOpBersama.luas_bng_beban_sppt,0).label('luas_bng_beban'),
                func.coalesce(SpptOpBersama.njop_bumi_beban_sppt,0).label('njop_bumi_beban'),
                func.coalesce(SpptOpBersama.njop_bng_beban_sppt,0).label('njop_bng_beban'))
        q = q.filter(
                cls.kd_propinsi == DatObjekPajak.kd_propinsi,
                cls.kd_dati2 == DatObjekPajak.kd_dati2,
                cls.kd_kecamatan == DatObjekPajak.kd_kecamatan,
                cls.kd_kelurahan == DatObjekPajak.kd_kelurahan,
                cls.kd_blok == DatObjekPajak.kd_blok,
                cls.no_urut == DatObjekPajak.no_urut,
                cls.kd_jns_op == DatObjekPajak.kd_jns_op)
        q = q.outerjoin(SpptOpBersama, and_(
                cls.kd_propinsi==SpptOpBersama.kd_propinsi,
                cls.kd_dati2==SpptOpBersama.kd_dati2,
                cls.kd_kecamatan==SpptOpBersama.kd_kecamatan,
                cls.kd_kelurahan==SpptOpBersama.kd_kelurahan,
                cls.kd_blok==SpptOpBersama.kd_blok,
                cls.no_urut==SpptOpBersama.no_urut,
                cls.kd_jns_op==SpptOpBersama.kd_jns_op,
                ))
        return q.filter(cls.kd_propinsi == fxNop.kd_propinsi,
                    cls.kd_dati2 == fxNop.kd_dati2,
                    cls.kd_kecamatan == fxNop.kd_kecamatan,
                    cls.kd_kelurahan == fxNop.kd_kelurahan,
                    cls.kd_blok == fxNop.kd_blok,
                    cls.no_urut == fxNop.no_urut,
                    cls.kd_jns_op == fxNop.kd_jns_op,
                    cls.thn_pajak_sppt == p_tahun)

    @classmethod
    def get_piutang(cls, p_kode, p_tahun, p_count):
        #Digunakan untuk menampilkan status sppt sesuai dengan jumah p_count
        fxNop = FixNop(p_kode)
        p_tahun_awal = str(int(p_tahun)-p_count+1)
               
        q1 = pbbDBSession.query(cls.thn_pajak_sppt,(cls.pbb_yg_harus_dibayar_sppt).label('pokok'), 
                                   cls.tgl_jatuh_tempo_sppt, cls.nm_wp_sppt,
                                   func.sum(PembayaranSppt.denda_sppt).label('denda_sppt'),
                                   func.sum(PembayaranSppt.jml_sppt_yg_dibayar).label('bayar'),
                                   func.sum(cls.pbb_yg_harus_dibayar_sppt-
                                            (PembayaranSppt.jml_sppt_yg_dibayar-
                                             PembayaranSppt.denda_sppt)).label('sisa')
                                    ).\
              outerjoin(PembayaranSppt, and_(
                  cls.kd_propinsi==PembayaranSppt.kd_propinsi,
                  cls.kd_dati2==PembayaranSppt.kd_dati2,
                  cls.kd_kecamatan==PembayaranSppt.kd_kecamatan,
                  cls.kd_kelurahan==PembayaranSppt.kd_kelurahan,
                  cls.kd_blok==PembayaranSppt.kd_blok,
                  cls.no_urut==PembayaranSppt.no_urut,
                  cls.kd_jns_op==PembayaranSppt.kd_jns_op,
                  cls.thn_pajak_sppt==PembayaranSppt.thn_pajak_sppt
                  )).\
              filter(
                    cls.kd_propinsi == fxNop.kd_propinsi,
                    cls.kd_dati2 == fxNop.kd_dati2,
                    cls.kd_kecamatan == fxNop.kd_kecamatan,
                    cls.kd_kelurahan == fxNop.kd_kelurahan,
                    cls.kd_blok == fxNop.kd_blok,
                    cls.no_urut == fxNop.no_urut,
                    cls.kd_jns_op == fxNop.kd_jns_op).\
              filter(cls.thn_pajak_sppt.between(p_tahun_awal,p_tahun)
                    ).\
              group_by(cls.thn_pajak_sppt, cls.pbb_yg_harus_dibayar_sppt, 
                      cls.tgl_jatuh_tempo_sppt, cls.nm_wp_sppt).subquery()
              
        query = pbbDBSession.query(func.sum(q1.c.pokok).label('pokok'),
                                    func.sum(q1.c.denda_sppt).label('denda_sppt'),
                                    func.sum(q1.c.bayar).label('bayar'),
                                    func.sum(q1.c.sisa).label('sisa'),
                                    )
        
        return query
        
    @classmethod
    def get_dop1(cls, p_kode, p_tahun):
        fxNop = FixNop(p_kode)
        query = pbbDBSession.query( 
                    func.concat(cls.kd_propinsi, '.').\
                    concat(cls.kd_dati2).concat('-').\
                    concat(cls.kd_kecamatan).concat('.').\
                    concat(cls.kd_kelurahan).concat('-').\
                    concat(cls.kd_blok).concat('.').\
                    concat(cls.no_urut).concat('-').\
                    concat(cls.kd_jns_op).label('nop'),
              cls.thn_pajak_sppt.label('thn_pajak_sppt'), 
              cls.luas_bumi_sppt.label('luas_bumi_sppt'), 
              cls.njop_bumi_sppt.label('njop_bumi_sppt'), 
              cls.luas_bng_sppt.label('luas_bng_sppt'), 
              cls.njop_bng_sppt.label('njop_bng_sppt'), 
              cls.nm_wp_sppt.label('nm_wp_sppt'),
              cls.jln_wp_sppt.label('jln_wp_sppt'), 
              cls.blok_kav_no_wp_sppt.label('blok_kav_no_wp_sppt'),
              cls.rw_wp_sppt.label('rw_wp_sppt'), 
              cls.rt_wp_sppt.label('rt_wp_sppt'), 
              cls.kelurahan_wp_sppt.label('kelurahan_wp_sppt'),
              cls.kota_wp_sppt.label('kota_wp_sppt'), 
              cls.kd_pos_wp_sppt.label('kd_pos_wp_sppt'), 
              cls.npwp_sppt.label('npwp_sppt'),
              cls.no_persil_sppt.label('no_persil_sppt'),
              cls.pbb_yg_harus_dibayar_sppt.label('pbb_yg_harus_dibayar_sppt'), 
              cls.status_pembayaran_sppt.label('status_pembayaran_sppt')).\
              filter(
                    cls.kd_propinsi == fxNop.kd_propinsi,
                    cls.kd_dati2 == fxNop.kd_dati2,
                    cls.kd_kecamatan == fxNop.kd_kecamatan,
                    cls.kd_kelurahan == fxNop.kd_kelurahan,
                    cls.kd_blok == fxNop.kd_blok,
                    cls.no_urut == fxNop.no_urut,
                    cls.kd_jns_op == fxNop.kd_jns_op,
                    cls.thn_pajak_sppt==p_tahun)
        return query

              # Kelurahan.nm_kelurahan.label('nm_kelurahan'), 
              # Kecamatan.nm_kecamatan.label('nm_kecamatan'), 
              # Dati2.nm_dati2.label('nm_dati2')).\
            # filter(cls.kd_propinsi == Kelurahan.kd_propinsi, 
                   # cls.kd_dati2 == Kelurahan.kd_dati2, 
                   # cls.kd_kecamatan == Kelurahan.kd_kecamatan, 
                   # cls.kd_kelurahan == Kelurahan.kd_kelurahan,).\
            # filter(cls.kd_propinsi == Kecamatan.kd_propinsi, 
                  # cls.kd_dati2 == Kecamatan.kd_dati2, 
                  # cls.kd_kecamatan == Kecamatan.kd_kecamatan,).\
            # filter(cls.kd_propinsi == Dati2.kd_propinsi, 
                    # cls.kd_dati2 == Dati2.kd_dati2,).\
            # fi
        
              # func.max(PembayaranSppt.tgl_pembayaran_sppt).label('tgl_bayar'),
              # func.sum(func.coalesce(PembayaranSppt.jml_sppt_yg_dibayar,0)).label('jml_sppt_yg_dibayar'),
              # func.sum(func.coalesce(PembayaranSppt.denda_sppt,0)).label('denda_sppt'),).\
              # outerjoin(DatObjekPajak, and_(
                            # cls.kd_propinsi==DatObjekPajak.kd_propinsi,
                            # cls.kd_dati2==DatObjekPajak.kd_dati2,
                            # cls.kd_kecamatan==DatObjekPajak.kd_kecamatan,
                            # cls.kd_kelurahan==DatObjekPajak.kd_kelurahan,
                            # cls.kd_blok==DatObjekPajak.kd_blok,
                            # cls.no_urut==DatObjekPajak.no_urut,
                            # cls.kd_jns_op==DatObjekPajak.kd_jns_op,
                            # )).\
              # outerjoin(SpptOpBersama, and_(
                  # cls.kd_propinsi==SpptOpBersama.kd_propinsi,
                  # cls.kd_dati2==SpptOpBersama.kd_dati2,
                  # cls.kd_kecamatan==SpptOpBersama.kd_kecamatan,
                  # cls.kd_kelurahan==SpptOpBersama.kd_kelurahan,
                  # cls.kd_blok==SpptOpBersama.kd_blok,
                  # cls.no_urut==SpptOpBersama.no_urut,
                  # cls.kd_jns_op==SpptOpBersama.kd_jns_op,
                  # cls.thn_pajak_sppt==SpptOpBersama.thn_pajak_sppt)).\
              # outerjoin(PembayaranSppt,and_(
                  # cls.kd_propinsi==PembayaranSppt.kd_propinsi,
                  # cls.kd_dati2==PembayaranSppt.kd_dati2,
                  # cls.kd_kecamatan==PembayaranSppt.kd_kecamatan,
                  # cls.kd_kelurahan==PembayaranSppt.kd_kelurahan,
                  # cls.kd_blok==PembayaranSppt.kd_blok,
                  # cls.no_urut==PembayaranSppt.no_urut,
                  # cls.kd_jns_op==PembayaranSppt.kd_jns_op,
                  # cls.thn_pajak_sppt==PembayaranSppt.thn_pajak_sppt
                  # )).\
              # group_by(cls.kd_propinsi, cls.kd_dati2, cls.kd_kecamatan, cls.kd_kelurahan, cls.kd_blok,
                    # cls.no_urut, cls.kd_jns_op, 
                    # cls.thn_pajak_sppt, 
                    # cls.luas_bumi_sppt, 
                    # cls.njop_bumi_sppt, 
                    # cls.luas_bng_sppt, 
                    # cls.njop_bng_sppt, 
                    # cls.nm_wp_sppt,
                    # cls.jln_wp_sppt, 
                    # cls.blok_kav_no_wp_sppt,
                    # cls.rw_wp_sppt, 
                    # cls.rt_wp_sppt, 
                    # cls.kelurahan_wp_sppt,
                    # cls.kota_wp_sppt, 
                    # cls.kd_pos_wp_sppt, 
                    # cls.npwp_sppt,
                    # cls.no_persil_sppt,
                    # cls.pbb_yg_harus_dibayar_sppt, 
                    # cls.status_pembayaran_sppt,
                    # DatObjekPajak.jalan_op, 
                    # DatObjekPajak.blok_kav_no_op, 
                    # DatObjekPajak.rt_op, 
                    # DatObjekPajak.rw_op,
                    # SpptOpBersama.luas_bumi_beban_sppt, 
                    # SpptOpBersama.luas_bng_beban_sppt, 
                    # SpptOpBersama.njop_bumi_beban_sppt, 
                    # SpptOpBersama.njop_bng_beban_sppt,
                    # Kelurahan.nm_kelurahan, 
                    # Kecamatan.nm_kecamatan, 
                    # Dati2.nm_dati2,
                    # )
        # return query.filter(
                    # cls.kd_propinsi == fxNop.kd_propinsi,
                    # cls.kd_dati2 == fxNop.kd_dati2,
                    # cls.kd_kecamatan == fxNop.kd_kecamatan,
                    # cls.kd_kelurahan == fxNop.kd_kelurahan,
                    # cls.kd_blok == fxNop.kd_blok,
                    # cls.no_urut == fxNop.no_urut,
                    # cls.kd_jns_op == fxNop.kd_jns_op,
                    # cls.thn_pajak_sppt==p_tahun)

              # DatObjekPajak.jalan_op.label('jalan_op'), 
              # DatObjekPajak.blok_kav_no_op.label('blok_kav_no_op'), 
              # DatObjekPajak.rt_op.label('rt_op'), 
              # DatObjekPajak.rw_op.label('rw_op'),
              # func.coalesce(SpptOpBersama.luas_bumi_beban_sppt,0).label('luas_bumi_beban'), 
              # func.coalesce(SpptOpBersama.luas_bng_beban_sppt,0).label('luas_bng_beban'), 
              # func.coalesce(SpptOpBersama.njop_bumi_beban_sppt,0).label('njop_bumi_beban'), 
              # func.coalesce(SpptOpBersama.njop_bng_beban_sppt,0).label('njop_bng_beban'),
                    
    @classmethod
    def get_dop(cls, p_kode, p_tahun):
        fxNop = FixNop(p_kode)
        query = pbbDBSession.query( 
                    func.concat(cls.kd_propinsi, '.').\
                    concat(cls.kd_dati2).concat('-').\
                    concat(cls.kd_kecamatan).concat('.').\
                    concat(cls.kd_kelurahan).concat('-').\
                    concat(cls.kd_blok).concat('.').\
                    concat(cls.no_urut).concat('-').\
                    concat(cls.kd_jns_op).label('nop'),
              cls.thn_pajak_sppt.label('thn_pajak_sppt'), 
              cls.luas_bumi_sppt.label('luas_bumi_sppt'), 
              cls.njop_bumi_sppt.label('njop_bumi_sppt'), 
              cls.luas_bng_sppt.label('luas_bng_sppt'), 
              cls.njop_bng_sppt.label('njop_bng_sppt'), 
              cls.nm_wp_sppt.label('nm_wp_sppt'),
              cls.jln_wp_sppt.label('jln_wp_sppt'), 
              cls.blok_kav_no_wp_sppt.label('blok_kav_no_wp_sppt'),
              cls.rw_wp_sppt.label('rw_wp_sppt'), 
              cls.rt_wp_sppt.label('rt_wp_sppt'), 
              cls.kelurahan_wp_sppt.label('kelurahan_wp_sppt'),
              cls.kota_wp_sppt.label('kota_wp_sppt'), 
              cls.kd_pos_wp_sppt.label('kd_pos_wp_sppt'), 
              cls.npwp_sppt.label('npwp_sppt'),
              cls.no_persil_sppt.label('no_persil_sppt'),
              cls.pbb_yg_harus_dibayar_sppt.label('pbb_yg_harus_dibayar_sppt'), 
              cls.status_pembayaran_sppt.label('status_pembayaran_sppt'),
              DatObjekPajak.jalan_op.label('jalan_op'), 
              DatObjekPajak.blok_kav_no_op.label('blok_kav_no_op'), 
              DatObjekPajak.rt_op.label('rt_op'), 
              DatObjekPajak.rw_op.label('rw_op'),
              func.coalesce(SpptOpBersama.luas_bumi_beban_sppt,0).label('luas_bumi_beban'), 
              func.coalesce(SpptOpBersama.luas_bng_beban_sppt,0).label('luas_bng_beban'), 
              func.coalesce(SpptOpBersama.njop_bumi_beban_sppt,0).label('njop_bumi_beban'), 
              func.coalesce(SpptOpBersama.njop_bng_beban_sppt,0).label('njop_bng_beban'),
              Kelurahan.nm_kelurahan.label('nm_kelurahan'), 
              Kecamatan.nm_kecamatan.label('nm_kecamatan'), 
              Dati2.nm_dati2.label('nm_dati2'),
              func.max(PembayaranSppt.tgl_pembayaran_sppt).label('tgl_bayar'),
              func.sum(func.coalesce(PembayaranSppt.jml_sppt_yg_dibayar,0)).label('jml_sppt_yg_dibayar'),
              func.sum(func.coalesce(PembayaranSppt.denda_sppt,0)).label('denda_sppt'),).\
              outerjoin(DatObjekPajak, and_(
                            cls.kd_propinsi==DatObjekPajak.kd_propinsi,
                            cls.kd_dati2==DatObjekPajak.kd_dati2,
                            cls.kd_kecamatan==DatObjekPajak.kd_kecamatan,
                            cls.kd_kelurahan==DatObjekPajak.kd_kelurahan,
                            cls.kd_blok==DatObjekPajak.kd_blok,
                            cls.no_urut==DatObjekPajak.no_urut,
                            cls.kd_jns_op==DatObjekPajak.kd_jns_op,
                            )).\
              outerjoin(SpptOpBersama, and_(
                  cls.kd_propinsi==SpptOpBersama.kd_propinsi,
                  cls.kd_dati2==SpptOpBersama.kd_dati2,
                  cls.kd_kecamatan==SpptOpBersama.kd_kecamatan,
                  cls.kd_kelurahan==SpptOpBersama.kd_kelurahan,
                  cls.kd_blok==SpptOpBersama.kd_blok,
                  cls.no_urut==SpptOpBersama.no_urut,
                  cls.kd_jns_op==SpptOpBersama.kd_jns_op,
                  cls.thn_pajak_sppt==SpptOpBersama.thn_pajak_sppt)).\
              outerjoin(PembayaranSppt,and_(
                  cls.kd_propinsi==PembayaranSppt.kd_propinsi,
                  cls.kd_dati2==PembayaranSppt.kd_dati2,
                  cls.kd_kecamatan==PembayaranSppt.kd_kecamatan,
                  cls.kd_kelurahan==PembayaranSppt.kd_kelurahan,
                  cls.kd_blok==PembayaranSppt.kd_blok,
                  cls.no_urut==PembayaranSppt.no_urut,
                  cls.kd_jns_op==PembayaranSppt.kd_jns_op,
                  cls.thn_pajak_sppt==PembayaranSppt.thn_pajak_sppt
                  )).\
              filter(cls.kd_propinsi == Kelurahan.kd_propinsi, 
                    cls.kd_dati2 == Kelurahan.kd_dati2, 
                    cls.kd_kecamatan == Kelurahan.kd_kecamatan, 
                    cls.kd_kelurahan == Kelurahan.kd_kelurahan,).\
              filter(cls.kd_propinsi == Kecamatan.kd_propinsi, 
                    cls.kd_dati2 == Kecamatan.kd_dati2, 
                    cls.kd_kecamatan == Kecamatan.kd_kecamatan,).\
              filter(cls.kd_propinsi == Dati2.kd_propinsi, 
                    cls.kd_dati2 == Dati2.kd_dati2,).\
              group_by(cls.kd_propinsi, cls.kd_dati2, cls.kd_kecamatan, cls.kd_kelurahan, cls.kd_blok,
                    cls.no_urut, cls.kd_jns_op, 
                    cls.thn_pajak_sppt, 
                    cls.luas_bumi_sppt, 
                    cls.njop_bumi_sppt, 
                    cls.luas_bng_sppt, 
                    cls.njop_bng_sppt, 
                    cls.nm_wp_sppt,
                    cls.jln_wp_sppt, 
                    cls.blok_kav_no_wp_sppt,
                    cls.rw_wp_sppt, 
                    cls.rt_wp_sppt, 
                    cls.kelurahan_wp_sppt,
                    cls.kota_wp_sppt, 
                    cls.kd_pos_wp_sppt, 
                    cls.npwp_sppt,
                    cls.no_persil_sppt,
                    cls.pbb_yg_harus_dibayar_sppt, 
                    cls.status_pembayaran_sppt,
                    DatObjekPajak.jalan_op, 
                    DatObjekPajak.blok_kav_no_op, 
                    DatObjekPajak.rt_op, 
                    DatObjekPajak.rw_op,
                    SpptOpBersama.luas_bumi_beban_sppt, 
                    SpptOpBersama.luas_bng_beban_sppt, 
                    SpptOpBersama.njop_bumi_beban_sppt, 
                    SpptOpBersama.njop_bng_beban_sppt,
                    Kelurahan.nm_kelurahan, 
                    Kecamatan.nm_kecamatan, 
                    Dati2.nm_dati2,
                    )
        return query.filter(
                    cls.kd_propinsi == fxNop.kd_propinsi,
                    cls.kd_dati2 == fxNop.kd_dati2,
                    cls.kd_kecamatan == fxNop.kd_kecamatan,
                    cls.kd_kelurahan == fxNop.kd_kelurahan,
                    cls.kd_blok == fxNop.kd_blok,
                    cls.no_urut == fxNop.no_urut,
                    cls.kd_jns_op == fxNop.kd_jns_op,
                    cls.thn_pajak_sppt==p_tahun)
    
        
    # @classmethod
    # def get_by_kelurahan_thn(cls, p_kode, p_tahun):
        # pkey = FixLength(DESA)
        # pkey.set_raw(p_kode)
        # query = cls.query_data()
        # return query.filter_by(kd_propinsi = pkey['kd_propinsi'], 
                            # kd_dati2 = pkey['kd_dati2'], 
                            # kd_kecamatan = pkey['kd_kecamatan'], 
                            # kd_kelurahan = pkey['kd_kelurahan'], 
                            # thn_pajak_sppt = p_tahun)
                            
    # @classmethod
    # def get_by_kecamatan_thn(cls, p_kode, p_tahun):
        # pkey = FixLength(KECAMATAN)
        # pkey.set_raw(p_kode)
        # query = cls.query_data()
        # return query.filter_by(kd_propinsi = pkey['kd_propinsi'], 
                            # kd_dati2 = pkey['kd_dati2'], 
                            # kd_kecamatan = pkey['kd_kecamatan'], 
                            # kd_kelurahan = pkey['kd_kelurahan'], 
                            # thn_pajak_sppt = p_tahun)
                            
    # @classmethod
    # def get_rekap_by_kecamatan_thn(cls, p_kode, p_tahun):
        # pkey = FixLength(KECAMATAN)
        # pkey.set_raw(p_kode)
        # query = pbbDBSession.query(cls.kd_propinsi, cls.kd_dati2, cls.kd_kecamatan, cls.kd_kelurahan, 
                               # func.sum(cls.pbb_yg_harus_dibayar_sppt).label('tagihan')).\
                               # group_by(cls.kd_propinsi, cls.kd_dati2, cls.kd_kecamatan, cls.kd_kelurahan)
        # return query.filter_by(kd_propinsi = pkey['kd_propinsi'], 
                            # kd_dati2 = pkey['kd_dati2'], 
                            # kd_kecamatan = pkey['kd_kecamatan'], 
                            # thn_pajak_sppt = p_tahun)

    # @classmethod
    # def get_rekap_by_tahun(cls, p_tahun):
        # query = pbbDBSession.query(cls.kd_propinsi, cls.kd_dati2, cls.kd_kecamatan,  
                               # func.sum(cls.pbb_yg_harus_dibayar_sppt).label('tagihan')).\
                               # group_by(cls.kd_propinsi, cls.kd_dati2, cls.kd_kecamatan)
        # return query.filter_by(thn_pajak_sppt = p_tahun)

class SpptOpBersama(pbbBase, CommonModel):
    __tablename__ = 'sppt_op_bersama'
    kd_propinsi = Column(String(2), primary_key=True)
    kd_dati2 = Column(String(2), primary_key=True)
    kd_kecamatan = Column(String(3), primary_key=True)
    kd_kelurahan = Column(String(3), primary_key=True)
    kd_blok = Column(String(3), primary_key=True)
    no_urut = Column(String(4), primary_key=True)
    kd_jns_op = Column(String(1), primary_key=True)
    thn_pajak_sppt = Column(String(4), primary_key=True)
    kd_kls_tanah = Column(String(3))
    thn_awal_kls_tanah = Column(String(4))
    kd_kls_bng = Column(String(3))
    thn_awal_kls_bng = Column(String(4))
    luas_bumi_beban_sppt = Column(Float)
    luas_bng_beban_sppt = Column(Float)
    njop_bumi_beban_sppt = Column(Float)
    njop_bng_beban_sppt = Column(Float)
    __table_args__ = PBB_ARGS
    
    def __init__(cls):
        pass
    
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
    
    def __init__(cls):
        pass
        
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
    def __init__(cls):
        pass
    
    
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
    def query(cls):
        return pbbDBSession.query(cls)
        
    @classmethod
    def query_id(cls, id):
        fxBayar = FixBayar(id)
        return cls.query().filter(
                cls.kd_propinsi == fxBayar.kd_propinsi,
                cls.kd_dati2 == fxBayar.kd_dati2,
                cls.kd_kecamatan == fxBayar.kd_kecamatan,
                cls.kd_kelurahan == fxBayar.kd_kelurahan,
                cls.kd_blok == fxBayar.kd_blok,
                cls.no_urut == fxBayar.no_urut,
                cls.kd_jns_op == fxBayar.kd_jns_op,
                cls.thn_pajak_sppt == fxBayar.thn_pajak_sppt,
                cls.thn_pajak_sppt==fxBayar.thn_pajak_sppt,
                cls.kd_kanwil==fxBayar.kd_kanwil,
                cls.kd_kantor==fxBayar.kd_kantor,
                cls.kd_tp==fxBayar.kd_tp,
                cls.pembayaran_sppt_ke==fxBayar.pembayaran_sppt_ke,)
    
    @classmethod
    def query_by_nop(cls, nop):
        fxNop = FixNop(nop)
        return cls.query().\
            filter(cls.kd_propinsi == fxNop.kd_propinsi,
                cls.kd_dati2 == fxNop.kd_dati2,
                cls.kd_kecamatan == fxNop.kd_kecamatan,
                cls.kd_kelurahan == fxNop.kd_kelurahan,
                cls.kd_blok == fxNop.kd_blok,
                cls.no_urut == fxNop.no_urut,
                cls.kd_jns_op == fxNop.kd_jns_op)
                
    @classmethod
    def reversal(cls, id):
        fxBayar = FixBayar(id)
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
        fxNop = FixNop(nop)
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
        
        
    # @classmethod
    # def get_by_nop(cls, p_nop):
        # pkey = FixLength(NOP)
        # pkey.set_raw(p_nop)
        # query = cls.query_data()
        # return query.filter_by(kd_propinsi = pkey['kd_propinsi'], 
                            # kd_dati2 = pkey['kd_dati2'], 
                            # kd_kecamatan = pkey['kd_kecamatan'], 
                            # kd_kelurahan = pkey['kd_kelurahan'], 
                            # kd_blok = pkey['kd_blok'], 
                            # no_urut = pkey['no_urut'], 
                            # kd_jns_op = pkey['kd_jns_op'],)
    # @classmethod
    # def get_by_nop_thn(cls, p_nop, p_tahun):
        # query = cls.get_by_nop(p_nop)
        # return query.filter_by(thn_pajak_sppt = p_tahun)
        
    # @classmethod
    # def get_by_kelurahan(cls, p_kode, p_tahun):
        # pkey = FixLength(DESA)
        # pkey.set_raw(p_kode)
        # query = cls.query_data()
        # return query.filter_by(kd_propinsi = pkey['kd_propinsi'], 
                            # kd_dati2 = pkey['kd_dati2'], 
                            # kd_kecamatan = pkey['kd_kecamatan'], 
                            # kd_kelurahan = pkey['kd_kelurahan'], 
                            # thn_pajak_sppt = p_tahun)
                            
    # @classmethod
    # def get_by_kecamatan(cls, p_kode, p_tahun):
        # pkey = FixLength(KECAMATAN)
        # pkey.set_raw(p_kode)
        # query = cls.query_data()
        # return query.filter_by(kd_propinsi = pkey['kd_propinsi'], 
                            # kd_dati2 = pkey['kd_dati2'], 
                            # kd_kecamatan = pkey['kd_kecamatan'], 
                            # kd_kelurahan = pkey['kd_kelurahan'], 
                            # thn_pajak_sppt = p_tahun)
    
    # @classmethod
    # def get_by_tanggal(cls, p_kode, p_tahun):
        # pkey = DateVar
        # p_kode = re.sub("[^0-9]", "", p_kode)
        # pkey.set_raw(p_kode)
        # query = cls.query_data()
        # return query.filter_by(tgl_pembayaran_sppt = pkey.get_value)
                            
    # @classmethod
    # def get_rekap_by_kecamatan(cls, p_kode, p_tahun):
        # pkey = FixLength(KECAMATAN)
        # pkey.set_raw(p_kode)
        # query = pbbDBSession.query(cls.kd_propinsi, cls.kd_dati2, cls.kd_kecamatan, cls.kd_kelurahan, 
                               # func.sum(cls.denda_sppt).label('denda'),
                               # func.sum(cls.pbb_yg_dibayar_sppt).label('jumlah') ).\
                               # group_by(cls.kd_propinsi, cls.kd_dati2, cls.kd_kecamatan, cls.kd_kelurahan)
        # return query.filter_by(kd_propinsi = pkey['kd_propinsi'], 
                            # kd_dati2 = pkey['kd_dati2'], 
                            # kd_kecamatan = pkey['kd_kecamatan'], 
                            # thn_pajak_sppt = p_tahun)

    # @classmethod
    # def get_rekap_by_thn(cls, p_tahun):
        # query = pbbDBSession.query(cls.kd_propinsi, cls.kd_dati2, cls.kd_kecamatan,  
                               # func.sum(cls.denda_sppt).label('denda'),
                               # func.sum(cls.pbb_yg_dibayar_sppt).label('jumlah')).\
                               # group_by(cls.kd_propinsi, cls.kd_dati2, cls.kd_kecamatan)
        # return query.filter_by(thn_pajak_sppt = p_tahun)
        
                    
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
    def __init__(cls):
        pass
