#Tools PBB Constanta yang digunakan di PBB karena dalam PBB primary Key 
#Banyak terdiri dari beberapa field
from types import (
    StringType,
    UnicodeType)
from ..tools import FixLength
from models import pbbDBSession
from models.ref import TempatPembayaran
from models.pegawai import DatLogin
from datetime import timedelta, datetime
import re
PROPINSI = [('kd_propinsi', 2, 'N'),]

DATI2 = list(PROPINSI)
DATI2.append(('kd_dati2', 2, 'N'))

KECAMATAN = list(DATI2)
KECAMATAN.append(('kd_kecamatan', 3, 'N'))

KELURAHAN = list(KECAMATAN)
KELURAHAN.append(('kd_kelurahan', 3, 'N'))
    
BLOK = list(KELURAHAN)
BLOK.append(('kd_blok', 3, 'N'))
    
NOP = list(BLOK)
NOP.extend([('no_urut', 4, 'N'),
            ('kd_jns_op', 1, 'N')])
    
SPPT  = list(NOP)
SPPT.append(('thn_pajak_sppt', 4, 'N'))

KANTOR = [('kd_kanwil', 2, 'N'),
          ('kd_kantor', 2, 'N')]
          
BANK = list(KANTOR)
BANK.append(('kd_tp', 2, 'N'))

BAYAR = list(SPPT)
BAYAR.extend(BANK)
BAYAR.append(('pembayaran_sppt_ke',3,'N'))    

SIKLUS = list(SPPT)
SIKLUS.append(('siklus_sppt',3,'N'))
             
NOPEL = list(KANTOR)
NOPEL.extend([('tahun',4,'N'),
              ('bundel',4,'N'),
              ('urut',3,'N')])
NOPELDET = list(NOPEL)
NOPELDET.extend(list(NOP))

# fixKantor = FixLength(KANTOR)
# fixBank = FixLength(BANK)
# fixNopel = FixLength(NOPEL)
# fixNop   = FixLength(NOP)
# fixSiklus = FixLength(SIKLUS)
# fixBayar  = FixLength(BAYAR)
# fixSPPT = FixLength(SPPT)

def get_value(obj,struct):
    raw = ""
    for name, typ, size in struct:
        raw  += obj[name]
    return raw

    
class SetFixLength(FixLength):
    def __init__(self, raw, struct):
        super(SetFixLength,self).__init__(struct)
        raw = re.sub("\D","",raw)
        self.set_raw(raw)
        for name, typ, size in struct:
            setattr(self, name, self[name])
        
class BaseFixLength(SetFixLength):
    def __init__(self, raw):
        super(BaseFixLength,self).__init__(raw, self.get_structure())
        raw = re.sub("\D","",raw)
        self.set_raw(raw)
        
    def get_structure(self):
        pass

class FixKantor(BaseFixLength):
    def get_structure(self):
        return KANTOR

class FixBank(BaseFixLength):
    def get_structure(self):
        return BANK
        
       
class FixNop(BaseFixLength):
    def get_structure(self):
        return NOP
        
class FixSppt(BaseFixLength):
    def get_structure(self):
        return SPPT

class FixSiklus(BaseFixLength):
    def get_structure(self):
        return SIKLUS
        
class FixBayar(BaseFixLength):
    def get_structure(self):
        return BAYAR
    
    def get_sppt(self):
        return get_value(self, SPPT)
                
    def get_bank(self):
        return get_value(self, BANK)
    
        
class FixNopel(BaseFixLength):
        
    def get_structure(self):
        return NOPEL

    def get_kantor(self):
        return get_value(self, KANTOR)
        
class FixNopelDetail(BaseFixLength):
    def get_structure(self):
        return NOPELDET

    def get_nopel(self):
        return get_value(self, NOPEL)
    
    def get_nop(self):
        return get_value(self, NOP)
        
def hitung_denda(piutang_pokok, jatuh_tempo, tanggal=None):
    persen_denda = 2
    max_denda = 24
    #jatuh_tempo = jatuh_tempo.date()
    tanggal = tanggal.date()
    if not tanggal:
        tanggal = datetime.now().date()
    if tanggal < jatuh_tempo: #+ timedelta(days=1):
        return 0
    
    kini = datetime.now()
    x = (kini.year - jatuh_tempo.year) * 12
    y = kini.month - jatuh_tempo.month
    bln_tunggakan = x + y + 1
    if kini.day <= jatuh_tempo.day:
        bln_tunggakan -= 1
    if bln_tunggakan < 1:
        bln_tunggakan = 0
    if bln_tunggakan > max_denda:
        bln_tunggakan = max_denda
        
    return bln_tunggakan * persen_denda / 100.0 * piutang_pokok

def nop_formatted(row):
    if type(row) in (StringType, UnicodeType):
        row = FixNop(row)
    return "%s.%s-%s.%s-%s.%s.%s" % (row.kd_propinsi, row.kd_dati2, row.kd_kecamatan,
                row.kd_kelurahan, row.kd_blok, row.no_urut, row.kd_jns_op)
                
def nop_to_id(row):
    if type(row) in (StringType, UnicodeType):
        row = FixNop(row)
    return "%s%s%s%s%s%s%s" % (row.kd_propinsi, row.kd_dati2, row.kd_kecamatan,
                row.kd_kelurahan, row.kd_blok, row.no_urut, row.kd_jns_op)
                
def pbb_nip(user_name):
    if user_name == 'admin':
        return '060000000000000000'
    row = pbbDBSession.query(DatLogin).\
            filter_by(nm_login = user_name.upper()).first()
    if row:
        return row.nip
    return
# JEnis REstitusi Kompensasi    
JNS_RESKOM =(
    (0,'Pilih Jenis'),
    (1,'Restitusi'),
    (2,'Kompensasi'),
    (3,'Disumbangkan'),
    (4,'Koreksi'),)

JENIS_ID = (
    (1, 'Tagihan'),
    (2, 'Piutang'),
    (3, 'Ketetapan'))


SUMBER_ID = (
    (4, 'Manual'),
    (1, 'PBB'),
    )    
    
DAFTAR_TP = pbbDBSession.query(TempatPembayaran.kd_tp,TempatPembayaran.nm_tp).\
                    order_by(TempatPembayaran.kd_tp).all()
