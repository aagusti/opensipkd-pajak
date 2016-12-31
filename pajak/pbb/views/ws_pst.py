###############################################################################
# Modul WSDL pbb_pst.py digunakan untuk memproses data pelayanan online ke    #
# SIM PBB                                                                     #
# Module ini terdiri dari 3 method yaitu                                      #
# 1. Menerima Data PST dari sistem online                                     #
# 2. Memperoleh data tracking                                                 #
# 3. Memperoleh posisi terakhir berkas pelayanan                              #
###############################################################################
import logging
import traceback
from StringIO import StringIO
from ...ws_tools import (
    auth_from_rpc,
    LIMIT,
    CODE_OK,
    CODE_NOT_FOUND,
    CODE_DATA_INVALID, 
    CODE_INVALID_LOGIN,
    CODE_NETWORK_ERROR,
    MSG_NOT_FOUND,
    MSG_DATA_INVALID,
    MSG_INVALID_LOGIN,
    MSG_NETWORK_ERROR,    
    )
    
from pyramid_rpc.jsonrpc import jsonrpc_method
from ..models import pbbDBSession
from ..models.pelayanan import (
    PstPermohonan,
    PstLampiran,
    PstDetail,
    PstDataOpBaru,
    PstPermohonanPengurangan,
    MaxUrutPstOl,
    )
from ...tools import FixLength
from datetime import (datetime, timedelta)

log = logging.getLogger(__name__)


################################################################################
#Methode set_pst ini dipanggil pada saat data pelayanan online di approve 
#Parameter
#kd_kanwil                  : kd_kanwil 
#kd_kantor                  : kd_kantor 
#thn_pelayanan              : thn_pelayanan 
#bundel_pelayanan           : bundel_pelayanan 
#no_urut_pelayanan          : no_urut_pelayanan 
#*parameter diatas isi datanya kosong pada saat data permohonan baru dan diisi 
# jika diupdate datanya
#no_srt_permohonan          : {no_srt_permohonan}
#tgl_surat_permohonan       : {tgl_surat_permohonan}
#nama_pemohon               : {nama_pemohon}
#alamat_pemohon             : {alamat_pemohon}
#keterangan_pst             : {keterangan_pst}
#status_kolektif            : {status_kolektif}
#kd_propinsi_pemohon        : {kd_propinsi_pemohon}
#kd_dati2_pemohon           : {kd_dati2_pemohon}
#kd_kecamatan_pemohon       : {kd_kecamatan_pemohon}
#kd_kelurahan_pemohon       : {kd_kelurahan_pemohon}
#kd_blok_pemohon            : {kd_blok_pemohon}
#no_urut_pemohon            : {no_urut_pemohon}
#kd_jns_op_pemohon          : {kd_jns_op_pemohon}
#kd_jns_pelayanan           : {kd_jns_pelayanan}
#thn_pajak_permohonan       : {thn_pajak_permohonan}
#l_permohonan               : {l_permohonan}
#l_surat_kuasa              : {l_surat_kuasa}
#l_ktp_wp                   : {l_ktp_wp}
#l_sertifikat_tanah         : {l_sertifikat_tanah}
#l_sppt                     : {l_sppt}
#l_imb                      : {l_imb}
#l_akte_jual_beli           : {l_akte_jual_beli}
#l_sk_pensiun               : {l_sk_pensiun}
#l_sppt_stts                : {l_sppt_stts}
#l_stts                     : {l_stts}
#l_sk_pengurangan           : {l_sk_pengurangan}
#l_sk_keberatan             : {l_sk_keberatan}
#l_skkp_pbb                 : {l_skkp_pbb}
#l_spmkp_pbb                : {l_spmkp_pbb}
#l_lain_lain                : {l_lain_lain}
#l_sket_tanah               : {l_sket_tanah}
#l_sket_lurah               : {l_sket_lurah}
#l_npwpd                    : {l_npwpd}
#l_penghasilan              : {l_penghasilan}
#l_cagar                    : {l_cagar}
#jns_pengurangan            : {jns_pengurangan}
#pct_permohonan_pengurangan : {pct_permohonan_pengurangan}
def pstdataopbaru(r):
    return r['kd_jns_pelayanan']=='01'
    
def pstpengurangan(r):
    return r['kd_jns_pelayanan'] in ['08','10'] 

@jsonrpc_method(method='set_pst', endpoint='ws_pbb')
def set_pst(request, data):
    #resp, user = auth_from_rpc(request)
    #print '---->', resp, data
    #if resp['code'] != 0:
    #    return resp
    #try:
    settings = request.registry.settings
        
    ret_data =[]
    for r in data['data']:
        if 1==1:
            if r['kd_kanwil'].strip() and r['kd_kantor'].strip() and r['thn_pelayanan'].strip() and\
               r['bundel_pelayanan'].strip() and r['no_urut_pelayanan'].strip():
               noPelayanan = (r['kd_kanwil'].strip(), r['kd_kantor'].strip(), r['thn_pelayanan'].strip(), 
                              r['bundel_pelayanan'].strip(), r['no_urut_pelayanan'].strip())
            else:
                noPelayanan = MaxUrutPstOl.get_nopel(request)
                r['kd_kanwil'] = noPelayanan[0]
                r['kd_kantor'] = noPelayanan[1] 
                r['thn_pelayanan'] = noPelayanan[2]
                r['bundel_pelayanan'] = noPelayanan[3] 
                r['no_urut_pelayanan'] = noPelayanan[4]
            
            #PstPermohonan
            pstPermohonan = PstPermohonan.get_by_nopel(r)
            if not pstPermohonan:
                pstPermohonan = PstPermohonan()
            r['tgl_terima_dokumen_wp'] = datetime.now()
            r['tgl_perkiraan_selesai'] = r['tgl_terima_dokumen_wp'] + timedelta(days=7)
            r['nip_penerima'] = 'nip_penerima' in settings \
                                 and settings['nip_penerima'] \
                                 or '090000000000000000'
            r['tgl_surat_permohonan'] = datetime.strptime(r['tgl_surat_permohonan'][:10],'%Y-%m-%d')                
            pstPermohonan.from_dict(r)
            pbb_DBSession.add(pstPermohonan)
            pbb_DBSession.flush()
            
            pstLampiran   = PstLampiran.get_by_nopel(r)
            if not pstLampiran:
                pstLampiran = PstLampiran()
            pstLampiran.from_dict(r)
            pbb_DBSession.add(pstLampiran)
            pbb_DBSession.flush()
            
            pstDetail     = PstDetail.get_by_nopel(r)
            if not pstDetail:
                pstDetail = PstDetail()
            r['kd_seksi_berkas']='80'
            r['tgl_selesai']=r['tgl_perkiraan_selesai']
            
            pstDetail.from_dict(r)
            pbb_DBSession.add(pstDetail)
            pbb_DBSession.flush()

            if pstdataopbaru(r):
                pstDataOpBaru  = PstDataOpBaru.get_by_nopel(r)
                if not pstDataOpBaru:
                    pstDataOpBaru = PstDataOpBaru()
                r['nama_wp_baru']=r['nama_pemohon']
                r['letak_op_baru']=r['alamat_pemohon']
                
                pstDataOpBaru.from_dict(r)
                pbb_DBSession.add(pstDataOpBaru)
                pbb_DBSession.flush()
                
            if pstpengurangan(r):
                pstPengurangan  = PstPengurangan.get_by_nopel(r)
                if not pstPengurangan:
                    pstPengurangan = PstPengurangan()
                r['nama_wp_baru']=r['nama_pemohon']
                r['letak_op_baru']=r['alamat_pemohon']
                
                pstPengurangan.from_dict(r)
                pbb_DBSession.add(pstPengurangan)
                pbb_DBSession.flush()
            
            ret_data.append(r)
            
        # except:
           # pbb_DBSession.rollback()
           # return dict(code = CODE_DATA_INVALID, message = MSG_DATA_INVALID)
    
    params = dict(data=ret_data)
    return dict(code = CODE_OK, message = 'Data Submitted',params = params)
    
@jsonrpc_method(method='get_pst_tracking', endpoint='ws_pbb')
def get_pst_tracking(request, data):
    #Digunakan untuk tracking data permohonan denga parameter
    #kd_kanwil                  : kd_kanwil 
    #kd_kantor                  : kd_kantor 
    #thn_pelayanan              : thn_pelayanan 
    #bundel_pelayanan           : bundel_pelayanan 
    #no_urut_pelayanan          : no_urut_pelayanan 
    #nop
    resp,user = auth_from_rpc(request)
    if resp['code'] != 0:
        return resp
    #try:
    if 1==1:
        ret_data =[]
        for r in data['data']:
            query  = PstDetail.get_tracking(r)
            row  =  query.first()
            if not row:
                resp['code'] = CODE_NOT_FOUND 
                resp['message'] = MSG_NOT_FOUND
                return resp

            fields = row.keys()
            rows = query.all()
            if rows:
                for row in rows:
                    ret_data.append(dict(zip(fields,row)))
    # except:
        # f = StringIO()
        # traceback.print_exc(file=f)
        # log.error(f.getvalue())
        # f.close()
        # return dict(code = CODE_DATA_INVALID, message = MSG_DATA_INVALID)
        
    params = dict(data=ret_data)
    return dict(code = CODE_OK, message = 'Data Submitted',params = params)    
    return dict(code = CODE_OK, message = 'Data Submitted',params = params)    

@jsonrpc_method(method='get_pst_position', endpoint='ws_pbb')
def get_pst_position(request, data):
    #Digunakan untuk tracking data permohonan denga parameter
    #kd_kanwil                  : kd_kanwil 
    #kd_kantor                  : kd_kantor 
    #thn_pelayanan              : thn_pelayanan 
    #bundel_pelayanan           : bundel_pelayanan 
    #no_urut_pelayanan          : no_urut_pelayanan 
    #nop
    resp,user = auth_from_rpc(request)
    if resp['code'] != 0:
        return resp
    if 1==1:
        ret_data =[]
        for r in data['data']:
            query  = PstDetail.get_position(r)
            row  =  query.first()
            if not row:
                resp['code'] = CODE_NOT_FOUND 
                resp['message'] = MSG_NOT_FOUND
                return resp

            fields = row.keys()
            rows = query.all()
            if rows:
                for row in rows:
                    ret_data.append(dict(zip(fields,row)))
    # except:
        # return dict(code = CODE_DATA_INVALID, message = MSG_DATA_INVALID)
    
    params = dict(data=ret_data)
    return dict(code = CODE_OK, message = 'Data Submitted',params = params)    
    