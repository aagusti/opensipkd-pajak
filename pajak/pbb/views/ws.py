import sys
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
    MSG_OK,
    MSG_DATA_INVALID,
    )
from pyramid_rpc.jsonrpc import jsonrpc_method
from pyramid.view import (view_config,)
from datetime import datetime
import re
from ..models import pbbDBSession
from ..models.tap import (
    Sppt,
    )
from ..models.pendataan import DatObjekPajak
    
from ...tools import FixLength
from ..views import PbbView
log = logging.getLogger(__name__)

def show_error():
    f = StringIO()
    traceback.print_exc(file=f)
    log.error(f.getvalue())
    f.close()
    
class WsPbbView(PbbView):
    def _init__(self,request):
        super(WsPbbView, self).__init__(request)
        
    @view_config(route_name="pbb-ws", renderer="templates/ws.pt")
    def view(self):
        return dict(project=self.project)
        
@jsonrpc_method(method='get_sppt_bayar', endpoint='ws_pbb')
def get_sppt_bayar(request, data):
    #Digunakan untuk generator info nop
    #parameter kode, [tahun], [count]
    #Contoh Parameter
    #Memperoleh Nop Tahun Tertentu            nop, tahun
    #Memperoleh Daftar Daftar Nop              nop
    
    resp,user = auth_from_rpc(request)
    if resp['code'] != 0:
        return resp
    try:
        ret_data =[]
        for r in data:
            p_kode = re.sub('[^0-9]','', r['kode'])
            query = Sppt.get_bayar(p_kode)
            p_count = 'count' in r and r['count'] or 0
            p_tahun = 'tahun' in r and r['tahun'] or datetime.now().strftime('%Y')
            if int(p_count) and int(p_tahun):
                p_tahun_awal = str(int(p_tahun)-int(p_count)+1)
                query = query.filter(Sppt.thn_pajak_sppt.between(p_tahun_awal,p_tahun))
            elif p_tahun:
                query.filter(Sppt.thn_pajak_sppt==p_tahun)
            query = query.order_by(Sppt.thn_pajak_sppt.desc())    
            row  =  query.first()
            if not row:
                resp['code'] = CODE_NOT_FOUND 
                resp['message'] = 'DATA TIDAK DITEMUKAN'
                return resp

            fields = row.keys()
            rows = query.all()
            if rows:
                for row in rows:
                    ret_data.append(dict(zip(fields,row)))
    except:
        show_error()
        return dict(code = CODE_DATA_INVALID, message = MSG_DATA_INVALID)
    
    params = dict(data=ret_data)
    return dict(code = CODE_OK, message = 'Data Submitted',params = params)
    
@jsonrpc_method(method='get_info_op', endpoint='ws_pbb')
def get_info_op(request, data):
    #Digunakan untuk generator info nop
    #parameter kode, [tahun]
    #Contoh Parameter
    #Memperoleh Nop Tertentu            nop, tahun
    #Memperoleh Daftar Nop              nop
    
    resp,user = auth_from_rpc(request)
    if resp['code'] != 0:
        return resp
    try:
        ret_data =[]
        for r in data:
            query = Sppt.get_info_op(r['kode'])
            if 'tahun' in r and r['tahun']:
                query.filter(Sppt.thn_pajak_sppt==r['tahun'])
            row  =  query.first()
            if not row:
                resp['code'] = CODE_NOT_FOUND 
                resp['message'] = 'DATA TIDAK DITEMUKAN'
                return resp

            fields = row.keys()
            rows = query.all()
            if rows:
                for row in rows:
                    ret_data.append(dict(zip(fields,row)))
    except:
        show_error()
        return dict(code = CODE_DATA_INVALID, message = 'Data Invalid')
    
    params = dict(data=ret_data)
    return dict(code = CODE_OK, message = MSG_OK,params = params)
    
@jsonrpc_method(method='get_dop_bphtb', endpoint='ws_pbb')
def get_dop_bphtb(request, data):
    #Digunakan untuk info nop pbb
    #parameter kode, [tahun]
    #Contoh Parameter
    #Memperoleh Nop Tertentu            nop, tahun
    #Memperoleh Daftar Nop              nop
    resp,user = auth_from_rpc(request)
    if resp['code'] != 0:
        return resp
    try:
        ret_data =[]
        for r in data:
            #if Sppt.count(r['kode'])>0:
            #    query = Sppt.get_info_op_bphtb(r['kode'],r['tahun'])
            #else:
            query = DatObjekPajak.get_info_op_bphtb(r['kode'])
            row  =  query.first()
            if not row:
                resp['code'] = CODE_NOT_FOUND 
                resp['message'] = 'DATA TIDAK DITEMUKAN'
                return resp
            fields = row.keys()
            rows = query.all()
            if rows:
                for row in rows:
                    ret_data.append(dict(zip(fields,row)))
    except:
        show_error()
        return dict(code = CODE_DATA_INVALID, message = 'Data Invalid')
    params = dict(data=ret_data)
    return dict(code = CODE_OK, message = MSG_OK,params = params)    

@jsonrpc_method(method='get_piutang_by_nop', endpoint='ws_pbb')
def get_piutang_by_nop(request, data):
    #Digunakan untuk menghitung piutang berdasarkan nop dan tahun selama periode tertentu
    #paramter input nop tahun akhir jumlah tahun yang dihitung
    # resp, user = auth_from_rpc(request)
    # if resp['code'] != 0:
        # return resp
    try:
        ret_data =[]
        for r in data:
            query = Sppt.get_piutang(r['kode'],r['tahun'],r['count'])
            row  =  query.first()
            if not row:
                resp['code'] = CODE_NOT_FOUND 
                resp['message'] = 'DATA TIDAK DITEMUKAN'
                return resp

            fields = row.keys()
            rows = query.all()
            if rows:
                for row in rows:
                    ret_data.append(dict(zip(fields,row)))
    except:
        show_error()
        return dict(code = CODE_DATA_INVALID, message = 'Data Invalid')
    
    params = dict(data=ret_data)
    return dict(code = CODE_OK, message = 'Data Submitted',params = params)    
    
@jsonrpc_method(method='get_sppt_dop', endpoint='ws_pbb')
def get_sppt_dop(request, data):
    #Digunakan untuk menghitung piutang berdasarkan nop dan tahun selama periode tertentu
    # paramter input nop tahun akhir jumlah tahun yang dihitung
    resp,user = auth_from_rpc(request)
    if resp['code'] != 0:
        return resp
    try:
        ret_data =[]
        for r in data:
            query = Sppt.get_dop(r['kode'],r['tahun'])
            row  =  query.first()
            if not row:
                resp['code'] = CODE_NOT_FOUND 
                resp['message'] = 'DATA TIDAK DITEMUKAN'
                return resp

            fields = row.keys()
            rows = query.all()
            if rows:
                for row in rows:
                    ret_data.append(dict(zip(fields,row)))
    except:
        show_error()
        return dict(code = CODE_DATA_INVALID, message = 'Data Invalid')
    
    params = dict(data=ret_data)
    return dict(code = CODE_OK, message = 'Data Submitted',params = params)    
    

@jsonrpc_method(method='get_sppt', endpoint='ws_pbb')
def get_sppt(request, data):
    #Digunakan untuk generator sppt per nop
    #parameter kode, [tahun]
    #Contoh Parameter
    #Memperoleh Nop Tertentu            nop, tahun
    #Memperoleh Daftar Nop              nop
    #Memperoleh Daftar Nop Perdesa      kd_desa, tahun
    #Memperoleh Daftar Nop Perkelurahan kd_kelurahan, tahun
    
    resp,user = auth_from_rpc(request)
    if resp['code'] != 0:
        return resp
    try:
        ret_data =[]
        for r in data:
          
            if len(r['kode'])==7: #kode= 7 digit berarti nop per kecamatan
                rows = Sppt.get_nop_by_kecamatan(r['kode'],r['tahun']).all()
            if len(r['kode'])==10: #kode= 10 digit berarti nop per desa
                rows = Sppt.get_nop_by_kelurahan(r['kode'],r['tahun']).all()
            else:
                if 'tahun' in r and r['tahun']:
                    rows = Sppt.get_by_nop_thn(r['kode'],r['tahun']).all()
                else:
                    rows = Sppt.get_by_nop(r['kode']).all()
            if rows:
                for row in rows:
                    ret_data.append(row.to_dict())
    except:
        show_error()
        return dict(code = CODE_DATA_INVALID, message = 'Data Invalid')
    
    params = dict(data=ret_data)
    return dict(code = CODE_OK, message = 'Data Submitted',params = params)

@jsonrpc_method(method='get_sppt_rekap_desa', endpoint='ws_pbb')
def get_sppt_rekap_desa(request, data):
    resp,user = auth_from_rpc(request)
    if resp['code'] != 0:
        return resp
    #try:
    if 1==1:
        ret_data =[]
        for r in data:
            query = Sppt.get_rekap_desa(r['kode'],r['tahun'])
            fields = query.first().keys()
            rows = query.all()
            if rows:
                for row in rows:
                    ret_data.append(dict(zip(fields,row)))
    #except:
    #    return dict(code = CODE_DATA_INVALID, message = 'Data Invalid')
    
    params = dict(data=ret_data)
    return dict(code = CODE_OK, message = 'Data Submitted',params = params)
    
@jsonrpc_method(method='get_sppt_rekap_kecamatan', endpoint='ws_pbb')
def get_sppt_rekap_kecamatan(request, data):
    resp,user = auth_from_rpc(request)
    if resp['code'] != 0:
        return resp
    #try:
    if 1==1:
        ret_data =[]
        for r in data:
            query = Sppt.get_rekap_kec(r['tahun'])
            fields = query.first().keys()
            rows = query.all()
            if rows:
                for row in rows:
                    ret_data.append(dict(zip(fields,row)))
    #except:
    #    return dict(code = CODE_DATA_INVALID, message = 'Data Invalid')
    
    params = dict(data=ret_data)
    return dict(code = CODE_OK, message = MSG_OK, params = params)
    
@jsonrpc_method(method='get_dop', endpoint='ws_pbb')
def get_dop(request, data):
    #Digunakan untuk generator info nop
    #parameter kode, [tahun]
    #Contoh Parameter
    #Memperoleh Nop Tertentu            nop, tahun
    #Memperoleh Daftar Nop              nop
    resp,user = auth_from_rpc(request)
    if resp['code'] != 0:
        return resp
    try:
    #if 1==1:
        ret_data =[]
        for r in data:
          
            if len(r['kode'])==7: #kode= 7 digit berarti nop per kecamatan
                rows = DatObjekPajak.get_by_kecamatan(r['kode']).all()
            if len(r['kode'])==10: #kode= 10 digit berarti nop per desa
                rows = DatObjekPajak.get_by_kelurahan(r['kode']).all()
            else:
                rows = DatObjekPajak.get_by_nop(r['kode']).all()
            if rows:
                for row in rows:
                    ret_data.append(row.to_dict())
    except:
        return dict(code = CODE_DATA_INVALID, message = MSG_INVALID)
    
    params = dict(data=ret_data)
    return dict(code = CODE_OK, message = message_ok, params = params)
