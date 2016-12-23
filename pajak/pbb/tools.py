#Tools PBB Constanta yang digunakan di PBB karena dalam PBB primary Key 
#Banyak terdiri dari beberapa field
from ..tools import *
from models import pbbDBSession
from models.ref import TempatPembayaran
from datetime import timedelta
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
NOPELDET = list(KANTOR)
NOPELDET.extend(list(NOP))

fixKantor = FixLength(KANTOR)
fixBank = FixLength(BANK)
fixNopel = FixLength(NOPEL)
fixNop   = FixLength(NOP)
fixSiklus = FixLength(SIKLUS)
fixBayar  = FixLength(BAYAR)
fixSPPT = FixLength(SPPT)

class clsKode(object):
    def __init__(self, kode, obj):
        kode = re.sub("\D","",kode)
        fKode = FixLength(obj)
        fKode.set_raw(kode)
        self.kode = fKode
        
    def get_raw(self):
        return self.kode.get_raw()
        
class clsKantor(clsKode):
    def __init__(self, kode):
        super(clsKantor,self).__init__(kode, KANTOR)
        #Set Local Variable
        self.kd_kanwil=self.kode['kd_kanwil']
        self.kd_kantor=self.kode['kd_kantor']

class clsBank(clsKantor, clsKode):
    def __init__(self, kode):
        clsKantor.__init__(self, kode)
        clsKode.__init__(self, kode, BANK)
        #Set Local Variable
        self.kd_tp = self.kode['kd_tp']
        
class clsNop(clsKode):
    def __init__(self, kode):
        clsKode.__init__(self, kode, NOP)
        #Set Local Variable
        self.kd_propinsi=self.kode['kd_propinsi']
        self.kd_dati2=self.kode['kd_dati2']
        self.kd_kecamatan=self.kode['kd_kecamatan']
        self.kd_kelurahan=self.kode['kd_kelurahan']
        self.kd_blok=self.kode['kd_blok']
        self.no_urut=self.kode['no_urut']
        self.kd_jns_op=self.kode['kd_jns_op']
        
class clsSppt(clsNop, clsKode):
    def __init__(self, kode):
        clsNop.__init__(self, kode)
        clsKode.__init__(self, kode, SPPT)

        #Set Local Variable
        self.thn_pajak_sppt=self.kode['thn_pajak_sppt']

class clsBayar(clsSppt, clsBank, clsKode):
    def __init__(self, kode):
        kode = re.sub("\D","", kode)
        clsSppt.__init__(self, kode)
        clsBank.__init__(self, kode[18:24])
        clsKode.__init__(self, kode, BAYAR)
        
        #Set Local Variable
        self.pembayaran_sppt_ke=self.kode['pembayaran_sppt_ke']
    def get_sppt(self):
        return self.get_raw()[:22]
    
    def get_bank(self):
        return self.get_raw()[22:28]
    
    def get_tp(self):
        return self.get_raw()[28:]

class clsNopel(clsKantor, clsKode):
    def __init__(self, kode):
        clsKantor.__init__(self, kode)
        clsKode.__init__(self, kode, NOPEL)
        
        #Set Local Variable
        self.tahun = self.kode['tahun'] 
        self.bundel = self.kode['bundel'] 
        self.urut = self.kode['urut'] 
        
    def get_kantor(self):
        return self.get_raw()[:4]
        
class clsNopelDetail(clsNopel, clsNop, clsKode):
    def __init__(self, kode):
        kode = re.sub("\D","", kode)
        clsNopel.__init__(self, kode)
        clsBank.__init__(self, kode[11:29])
        clsKode.__init__(self, kode, NOPELDET)
        
    def get_nopel(self):
        return self.get_raw()[4:11]
    
    def get_nop(self):
        return self.get_raw()[11:]
     
# kantor = clsBank('61.01.01')
# print kantor.get_raw()
# sys.exit()
        
# nop =  clsNop('61.01.001.001.0001.0')
# print nop.get_raw()
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
