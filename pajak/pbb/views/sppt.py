import os
import uuid
from datetime import datetime
from sqlalchemy import not_, func, between
from pyramid.view import (view_config,)
from pyramid.httpexceptions import ( HTTPFound, )
import colander
from deform import (Form, widget, ValidationFailure, )
from ...pbb.models import pbbDBSession
from ...pbb.models.tap import Sppt
#from ...tools import _DTstrftime, _DTnumber_format
#from ...views.base_views import base_view
from ...views.common import ColumnDT, DataTables
from ..views import PbbView

SESS_ADD_FAILED  = 'Tambah Saldo Awal gagal'
SESS_EDIT_FAILED = 'Edit Saldo Awal gagal'

class SpptView(PbbView):
    def _init__(self,request):
        super(SpptView, self).__init__(request)
        
    @view_config(route_name="pbb-sppt", renderer="templates/sppt/list.pt",
                 permission="pbb-sppt")
    def view(self):
        return dict(project=self.project)

    ##########
    # Action #
    ##########
    @view_config(route_name='pbb-sppt-act', renderer='json',
                 permission='pbb-sppt-act')
    def view_act(self):
        req = self.req
        ses = req.session
        params   = req.params
        url_dict = req.matchdict
        if url_dict['id']=='grid':
            #pk_id = 'id' in params and params['id'] and int(params['id']) or 0
            if url_dict['id']=='grid':
                # defining columns
                columns = []
                columns.append(ColumnDT(func.concat(Sppt.kd_propinsi,
                                        func.concat(".", 
                                        func.concat(Sppt.kd_dati2, 
                                        func.concat("-", 
                                        func.concat(Sppt.kd_kecamatan,
                                        func.concat(".", 
                                        func.concat(Sppt.kd_kelurahan,
                                        func.concat("-", 
                                        func.concat(Sppt.kd_blok,
                                        func.concat(".", 
                                        func.concat(Sppt.no_urut,
                                        func.concat(".", Sppt.kd_jns_op)))))))))))) ,
                                        mData='nop', global_search=True))
                columns.append(ColumnDT(Sppt.thn_pajak_sppt, mData='tahun', global_search=True))
                columns.append(ColumnDT(Sppt.nm_wp_sppt, mData='nama_wp', global_search=True))
                columns.append(ColumnDT(Sppt.luas_bumi_sppt, mData='luas_bumi', global_search=True))
                columns.append(ColumnDT(Sppt.luas_bng_sppt, mData='luas_bng', global_search=False))
                columns.append(ColumnDT(Sppt.pbb_yg_harus_dibayar_sppt, mData='nilai', global_search=False))

                query = pbbDBSession.query().select_from(Sppt).\
                                     filter(Sppt.thn_pajak_sppt==str(self.tahun))
                rowTable = DataTables(req.GET, query, columns)
                return rowTable.output_result()

###########
# Posting #
###########
@view_config(route_name='pbb-sppt-post', renderer='json',
             permission='pbb-sppt-post')
def view_posting(request):
    if request.POST:
        controls = dict(request.POST.items())
        for id in controls['id'].split(","):
            row    = query_id(id).first()
            if not row:
                n_id_not_found = n_id_not_found + 1
                continue

            if not row.nilai:
                n_row_zero = n_row_zero + 1
                continue

            if request.session['posted']==0 and row.posted:
                n_posted = n_posted + 1
                continue

            if request.session['posted']==1 and not row.posted:
                n_posted = n_posted + 1
                continue

            n_id = n_id + 1

            id_inv = row.id
            
            if request.session['posted']==0:
                pass 
            else:
                pass
                
        if n_id_not_found > 0:
            msg = '%s Data Tidan Ditemukan %s \n' % (msg,n_id_not_found)
        if n_row_zero > 0:
            msg = '%s Data Dengan Nilai 0 sebanyak %s \n' % (msg,n_row_zero)
        if n_posted>0:
            msg = '%s Data Tidak Di Proses %s \n' % (msg,n_posted)
        msg = '%s Data Di Proses %s ' % (msg,n_id)
        
        return dict(success = True,
                    msg     = msg)
                    
    return dict(success = False,
                msg     = 'Terjadi kesalahan proses')

##########
# CSV #
##########
@view_config(route_name='pbb-sppt-csv', renderer='csv',
             permission='pbb-sppt-csv')
def view_csv(request):
    ses = request.session
    req = request
    params   = req.params
    url_dict = req.matchdict
    tahun = 'tahun' in params and params['tahun'] or \
                datetime.now().strftime('%Y')
    tahun = '2013'        
    q = pbbDBSession.query(func.concat(Sppt.kd_propinsi,
                           func.concat(".", 
                           func.concat(Sppt.kd_dati2, 
                           func.concat("-", 
                           func.concat(Sppt.kd_kecamatan,
                           func.concat(".", 
                           func.concat(Sppt.kd_kelurahan,
                           func.concat("-", 
                           func.concat(Sppt.kd_blok,
                           func.concat(".", 
                           func.concat(Sppt.no_urut,
                           func.concat(".", Sppt.kd_jns_op)))))))))))),
                           Sppt.thn_pajak_sppt,
                           Sppt.nm_wp_sppt,
                           Sppt.luas_bumi_sppt,
                           Sppt.luas_bng_sppt,
                           Sppt.pbb_yg_harus_dibayar_sppt).\
                  filter(Sppt.thn_pajak_sppt==tahun)

    r = q.first()
    header = r.keys()
    query = q.all()
    rows = []
    for item in query:
        rows.append(list(item))

    # override attributes of response
    filename = 'pbb-sppt.csv'
    request.response.content_disposition = 'attachment;filename=' + filename

    return {
      'header': header,
      'rows': rows,
    }
