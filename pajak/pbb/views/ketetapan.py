import os
import uuid
from datetime import datetime, timedelta
from sqlalchemy import not_, func, between
from pyramid.view import (view_config,)
from pyramid.httpexceptions import ( HTTPFound, )
import colander
from deform import (Form, widget, ValidationFailure, )
from ...pbb.models import pbbDBSession
from ...pbb.models.tap import SpptAkrual
from ...pbb.tools import FixSiklus
from ...tools import _DTstrftime, _DTnumber_format #, FixLength
#from ...views.base_views import base_view
from ...views.common import ColumnDT, DataTables
#from ..tools import FixSiklus
import re
from ...report_tools import (
        open_rml_row, open_rml_pdf, pdf_response, 
        csv_response, csv_rows)
        
SESS_ADD_FAILED  = 'Tambah Ketetapan gagal'
SESS_EDIT_FAILED = 'Edit Ketetapan gagal'

from ..views import PbbView
def deferred_jenis_id(node, kw):
    values = kw.get('jenis_id', [])
    return widget.SelectWidget(values=values)

class KetetapanView(PbbView):
    def _init__(self,request):
        super(KetetapanView, self).__init__(request)
        
    @view_config(route_name="pbb-ketetapan", renderer="templates/ketetapan/list.pt",
                 permission="pbb-ketetapan")
    def view(self):
        return dict(project=self.project )

    ##########
    # Action #
    ##########
    @view_config(route_name='pbb-ketetapan-act', renderer='json',
                 permission='pbb-ketetapan-act')
    def view_act(self):
        url_dict = self.req.matchdict
        if url_dict['id']=='grid':
            if url_dict['id']=='grid':
                columns = [
                    ColumnDT(func.concat(SpptAkrual.kd_propinsi,
                             func.concat(SpptAkrual.kd_dati2, 
                             func.concat(SpptAkrual.kd_kecamatan,
                             func.concat(SpptAkrual.kd_kelurahan,
                             func.concat(SpptAkrual.kd_blok,
                             func.concat(SpptAkrual.no_urut,
                             func.concat(SpptAkrual.kd_jns_op,
                             func.concat(SpptAkrual.thn_pajak_sppt,
                             SpptAkrual.siklus_sppt)))))))) ,
                             mData='id', global_search=True),
                    ColumnDT(func.concat(SpptAkrual.kd_propinsi,
                             func.concat(".", 
                             func.concat(SpptAkrual.kd_dati2, 
                             func.concat("-", 
                             func.concat(SpptAkrual.kd_kecamatan,
                             func.concat(".", 
                             func.concat(SpptAkrual.kd_kelurahan,
                             func.concat("-", 
                             func.concat(SpptAkrual.kd_blok,
                             func.concat(".", 
                             func.concat(SpptAkrual.no_urut,
                             func.concat(".", SpptAkrual.kd_jns_op)))))))))))) ,
                             mData='nop', global_search=True),
                    ColumnDT(SpptAkrual.thn_pajak_sppt, mData='tahun', global_search=True),
                    ColumnDT(SpptAkrual.siklus_sppt, mData='siklus', global_search=True),
                    ColumnDT(SpptAkrual.nm_wp_sppt, mData='nama_wp', global_search=True),
                    ColumnDT(SpptAkrual.pbb_yg_harus_dibayar_sppt, mData='nilai', global_search=False),
                    ColumnDT(func.to_char(SpptAkrual.tgl_terbit_sppt,'DD-MM-YYYY'), mData='tgl_terbit', global_search=True),
                    ColumnDT(func.to_char(SpptAkrual.tgl_cetak_sppt,'DD-MM-YYYY'), mData='tgl_cetak', global_search=True),
                    ColumnDT(func.to_char(SpptAkrual.create_date,'DD-MM-YYYY'), mData='tgl_proses', global_search=True),
                    ColumnDT(SpptAkrual.posted, mData='posted', global_search=True)
                ]

                query = pbbDBSession.query().select_from(SpptAkrual).\
                            filter(SpptAkrual.create_date.between(self.dt_awal, 
                                              self.dt_akhir+timedelta(days=1),)).\
                            filter(SpptAkrual.posted == self.posted)
                                     
                rowTable = DataTables(self.req.GET, query, columns)
                return rowTable.output_result()
            
    ###########
    # Posting #
    ###########
    @view_config(route_name='pbb-ketetapan-post', renderer='json',
                 permission='pbb-ketetapan-post')
    def view_posting(self):
        request = self.req
        url_dict = request.matchdict
        if request.POST:
            controls = dict(request.POST.items())
            if url_dict['id'] == 'post':
                n_id = n_id_not_found = n_row_zero = n_posted = 0
                msg = ""
                for id in controls['id'].split(","):
                    q = query_id(id)
                    row    = q.first()
                    if not row:
                        n_id_not_found = n_id_not_found + 1
                        continue

                    if not row.pbb_yg_harus_dibayar_sppt:
                        n_row_zero = n_row_zero + 1
                        continue

                    if request.session['posted']==0 and row.posted:
                        n_posted = n_posted + 1
                        continue

                    if request.session['posted']==1 and not row.posted:
                        n_posted = n_posted + 1
                        continue

                    n_id = n_id + 1

                    #id_inv = row.id
                    
                    if self.posted==1:
                        row.posted = 0 
                    else:
                        row.posted = 1
                        
                    pbbDBSession.flush()
                    
                if n_id_not_found > 0:
                    msg = '%s Data Tidak Ditemukan %s \n' % (msg,n_id_not_found)
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
    @view_config(route_name='pbb-ketetapan-rpt', 
                 permission='pbb-ketetapan-rpt')
    def view_csv(self):
        url_dict = self.req.matchdict
        query = pbbDBSession.query(func.concat(SpptAkrual.kd_propinsi,
                            func.concat(".", 
                            func.concat(SpptAkrual.kd_dati2, 
                            func.concat("-", 
                            func.concat(SpptAkrual.kd_kecamatan,
                            func.concat(".", 
                            func.concat(SpptAkrual.kd_kelurahan,
                            func.concat("-", 
                            func.concat(SpptAkrual.kd_blok,
                            func.concat(".", 
                            func.concat(SpptAkrual.no_urut,
                            func.concat(".", SpptAkrual.kd_jns_op)))))))))))).label('nop'),
                            SpptAkrual.thn_pajak_sppt,
                            SpptAkrual.siklus_sppt,
                            SpptAkrual.nm_wp_sppt,
                            SpptAkrual.luas_bumi_sppt,
                            SpptAkrual.luas_bng_sppt,
                            SpptAkrual.pbb_yg_harus_dibayar_sppt).\
                            filter(SpptAkrual.create_date.between(self.dt_awal, 
                                              self.dt_akhir+timedelta(days=1),)).\
                            filter(SpptAkrual.posted == self.posted)
        if url_dict['rpt']=='csv' :
            filename = 'ketetapan.csv'
            return csv_response(self.req, csv_rows(query), filename)

        if url_dict['rpt']=='pdf' :
            _here = os.path.dirname(__file__)
            path = os.path.join(os.path.dirname(_here), 'static')
            print "XXXXXXXXXXXXXXXXXXX", os.path

            #logo = path + "/img/logo.png"
            #line = path + "/img/line.png"
            #logo = self.req.static_url('static/img/logo.png')
            #line = self.req.static_url('static/img/line.png')
            logo = "http://192.168.56.3:6543/static/img/logo.png"
            line = "http://192.168.56.3:6543/static/img/line.png"

            path = os.path.join(os.path.dirname(_here), 'reports')
            rml_row = open_rml_row(path+'/pbb_ketetapan.row.rml')
            
            rows=[]
            for r in query.all():
                s = rml_row.format(nop=r.nop, thn_pajak_sppt=r.thn_pajak_sppt, siklus_sppt=r.siklus_sppt,   
                                   nm_wp_sppt=r.nm_wp_sppt,  
                                   luas_bumi_sppt=r.luas_bumi_sppt, luas_bng_sppt=r.luas_bng_sppt, pbb_yg_harus_dibayar_sppt=r.pbb_yg_harus_dibayar_sppt)
                rows.append(s)
            
            pdf, filename = open_rml_pdf(path+'/pbb_ketetapan.rml', rows=rows, 
                                company=self.req.company,
                                departement = self.req.departement,
                                logo = logo,
                                line = line,
                                address = self.req.address)
            return pdf_response(self.req, pdf, filename)
            
########
# Edit #
########
def query_id(id):
    nop = FixSiklus(id)
    return pbbDBSession.query(SpptAkrual).\
           filter(SpptAkrual.kd_propinsi==nop.kd_propinsi,
                  SpptAkrual.kd_dati2==nop.kd_dati2,
                  SpptAkrual.kd_kecamatan==nop.kd_kecamatan,
                  SpptAkrual.kd_kelurahan==nop.kd_kelurahan,
                  SpptAkrual.kd_blok==nop.kd_blok,
                  SpptAkrual.no_urut==nop.no_urut,
                  SpptAkrual.kd_jns_op==nop.kd_jns_op,
                  SpptAkrual.thn_pajak_sppt==nop.thn_pajak_sppt,
                  SpptAkrual.siklus_sppt==nop.siklus_sppt,
                  )
                  

def id_not_found(value):
    msg = 'NOP ID %s not found.' % value
    request.session.flash(msg, 'error')
    return route_list(request)