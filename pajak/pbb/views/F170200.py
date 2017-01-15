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
#from ...pbb.tools import FixSiklus
from ...tools import _DTstrftime, _DTnumber_format #, FixLength
#from ...views.base_views import base_view
from ...views.common import ColumnDT, DataTables
import re

SESS_ADD_FAILED  = 'Tambah Restitusi/Kompensasi gagal'
SESS_EDIT_FAILED = 'Edit Restitusi/Kompensasi gagal'

from ..views import PbbView
def deferred_jenis_id(node, kw):
    values = kw.get('jenis_id', [])
    return widget.SelectWidget(values=values)

class F170200View(PbbView):
    def _init__(self,request):
        super(F170200View, self).__init__(request)
        
    @view_config(route_name="F170200", renderer="templates/F170200/list.pt",
                 permission="F170200")
    def view(self):
        return dict(project='e-Restitusi')

    ##########
    # Action #
    ##########
    @view_config(route_name='F170200-act', renderer='json',
                 permission='F170200-act')
    def view_act(self):
        req = self.req
        ses = req.session
        params   = req.params
        url_dict = req.matchdict
        tahun = self.tahun
        #tahun = '2013'    
        if url_dict['id']=='grid':
            #pk_id = 'id' in params and params['id'] and int(params['id']) or 0
            if url_dict['id']=='grid':
                # defining columns
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
                            filter(SpptAkrual.posted == ses['posted'])
                                     
                rowTable = DataTables(req.GET, query, columns)
                return rowTable.output_result()
            

        row = save(request, values, row)
        
    # ###########
    # # Posting #
    # ###########
    # @view_config(route_name='F170200-post', renderer='json',
                 # permission='F170200-post')
    # def view_posting(self):
        # request = self.req
        # url_dict = request.matchdict
        # if request.POST:
            # controls = dict(request.POST.items())
            # if url_dict['id'] == 'post':
                # n_id = n_id_not_found = n_row_zero = n_posted = 0
                # msg = ""
                # for id in controls['id'].split(","):
                    # q = query_id(id)
                    # row    = q.first()
                    # if not row:
                        # n_id_not_found = n_id_not_found + 1
                        # continue

                    # if not row.pbb_yg_harus_dibayar_sppt:
                        # n_row_zero = n_row_zero + 1
                        # continue

                    # if request.session['posted']==0 and row.posted:
                        # n_posted = n_posted + 1
                        # continue

                    # if request.session['posted']==1 and not row.posted:
                        # n_posted = n_posted + 1
                        # continue

                    # n_id = n_id + 1

                    # #id_inv = row.id
                    
                    # if request.session['posted']==0:
                        # row.posted = 1 
                    # else:
                        # row.posted = 0
                    # pbbDBSession.flush()
                    
                # if n_id_not_found > 0:
                    # msg = '%s Data Tidak Ditemukan %s \n' % (msg,n_id_not_found)
                # if n_row_zero > 0:
                    # msg = '%s Data Dengan Nilai 0 sebanyak %s \n' % (msg,n_row_zero)
                # if n_posted>0:
                    # msg = '%s Data Tidak Di Proses %s \n' % (msg,n_posted)
                # msg = '%s Data Di Proses %s ' % (msg,n_id)
                
                # return dict(success = True,
                            # msg     = msg)
                            
            # return dict(success = False,
                    # msg     = 'Terjadi kesalahan proses')
                    

    ##########
    # CSV #
    ##########
    @view_config(route_name='F170200-rpt', renderer='csv',
                 permission='F170200-rpt')
    def view_csv(self):
        req = self.req
        ses = self.ses
        params   = req.params
        url_dict = req.matchdict
        
        q = pbbDBSession.query(func.concat(SpptAkrual.kd_propinsi,
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
                            filter(SpptAkrual.posted == ses['posted'])
        
        filename = 'F170200-rekap.csv'
        req.response.content_disposition = 'attachment;filename=' + filename
        rows = []
        header = []
       
        r = q.first()
        if r:
            header = r.keys()
            query = q.all()
            for item in query:
                rows.append(list(item))

            
        # override attributes of response

        return {
          'header': header,
          'rows': rows,
        }                
                    
########
# Edit #
########
def query_id(value):
    val = re.sub("\D", "", value)
    nop = FixLength(SIKLUS)
    nop.set_raw(val)
    #bayar = val[len(nop.get_raw()):]
    return pbbDBSession.query(SpptAkrual).\
           filter(SpptAkrual.kd_propinsi==nop['kd_propinsi'],
                  SpptAkrual.kd_dati2==nop['kd_dati2'],
                  SpptAkrual.kd_kecamatan==nop['kd_kecamatan'],
                  SpptAkrual.kd_kelurahan==nop['kd_kelurahan'],
                  SpptAkrual.kd_blok==nop['kd_blok'],
                  SpptAkrual.no_urut==nop['no_urut'],
                  SpptAkrual.kd_jns_op==nop['kd_jns_op'],
                  SpptAkrual.thn_pajak_sppt==nop['thn_pajak_sppt'],
                  SpptAkrual.siklus_sppt==nop['siklus_sppt'],
                  )
                  

def id_not_found(value):
    msg = 'NOP ID %s not found.' % value
    request.session.flash(msg, 'error')
    return route_list(request)

# ##########
# # CSV #
# ##########
# @view_config(route_name='F170200-rpt', renderer='csv',
             # permission='F170200-rpt')
# def view_csv(request):
    # ses = request.session
    # req = request
    # params   = req.params
    # url_dict = req.matchdict
    # tahun = 'tahun' in params and params['tahun'] or \
                # datetime.now().strftime('%Y')
    # tahun = '2013'        
    # 

    # r = q.first()
    # header = r.keys()
    # query = q.all()
    # rows = []
    # for item in query:
        # rows.append(list(item))

    # # override attributes of response
    # filename = 'F170200.csv'
    # request.response.content_disposition = 'attachment;filename=' + filename

    # return {
      # 'header': header,
      # 'rows': rows,
    # }

    
# #######
# # Add #
# #######
# def form_validator(form, value):
    # def err_kegiatan():
        # raise colander.Invalid(form,
            # 'Kegiatan dengan no urut tersebut sudah ada')

# class AddSchema(colander.Schema):
    # tahun       = colander.SchemaNode(
                            # colander.String())
    # uraian      = colander.SchemaNode(
                            # colander.String(),
                            # missing = colander.drop)
    # tahun_tetap = colander.SchemaNode(
                            # colander.String(),
                            # title = "Tahun Ketetapan")
    # nilai         = colander.SchemaNode(
                            # colander.String())
    
# class EditSchema(AddSchema):
    # id             = colander.SchemaNode(
                          # colander.Integer(),
                          # oid="id")

# def get_form(request, class_form):
    # schema = class_form(validator=form_validator)
    # schema = schema.bind(jenis_id=JENIS_ID,sumber_id=SUMBER_ID)
    # schema.request = request
    # return Form(schema, buttons=('simpan','batal'))

# def save(request, values, row=None):
    # if not row:
        # row = SpptAkrual()
    # row.from_dict(values)
    # pbbDBSession.add(row)
    # pbbDBSession.flush()
    # return row

# def save_request(values, request, row=None):
    # if 'id' in request.matchdict:
        # values['id'] = request.matchdict['id']
        # values['update_uid'] = request.user.id
        # values['updated'] = datetime.now()
    # else:
        # values['create_uid'] = request.user.id
        # values['created'] = datetime.now()
        # values['posted'] = 0
    # request.session.flash('Saldo Awal sudah disimpan.')
    # return row

# def route_list(request):
    # return HTTPFound(location=request.route_url('F170200'))

# def session_failed(request, session_name):
    # r = dict(form=request.session[session_name])
    # del request.session[session_name]
    # return r

# @view_config(route_name='F170200-view', renderer='templates/ketetapan/add.pt',
             # permission='F170200-view')
# def view_edit(request):
    # row = query_id(request).first()

    # if not row:
        # return id_not_found(request)
    # if row.posted:
        # request.session.flash('Data sudah diposting', 'error')
        # return route_list(request)

    # form = get_form(request, EditSchema)
    # if request.POST:
        # if 'simpan' in request.POST:
            # controls = request.POST.items()
            # try:
                # c = form.validate(controls)
            # except ValidationFailure, e:
                # return dict(form=form)
            # save_request(dict(controls), request, row)
        # return route_list(request)
    # elif SESS_EDIT_FAILED in request.session:
        # del request.session[SESS_EDIT_FAILED]
        # return dict(form=form)
    # values = row.to_dict()
    # form.set_appstruct(values)
    # return dict(form=form)


