import os
import uuid
from datetime import datetime
from sqlalchemy import not_, func, between
from pyramid.view import (view_config,)
from pyramid.httpexceptions import ( HTTPFound, )
import colander
from deform import (Form, widget, ValidationFailure, )
from ...pbb.models import pbbDBSession
from ...pbb.models.tap import SaldoAwal
#from ...tools import _DTstrftime, _DTnumber_format
#from ...views.base_views import base_view
from ...views.common import ColumnDT, DataTables
from ...report_tools import (
        open_rml_row, open_rml_pdf, pdf_response, 
        csv_response, csv_rows)
    
SESS_ADD_FAILED  = 'Tambah Saldo Awal gagal'
SESS_EDIT_FAILED = 'Edit Saldo Awal gagal'

from ..views import PbbView

class SaldoAwalView(PbbView):
    def _init__(self,request):
        super(SaldoAwalView, self).__init__(request)
    @view_config(route_name="pbb-akrual", renderer="templates/home_akrual.pt",
                 permission="pbb-akrual")
    def akrual(self):
        return dict(project=self.project)
                 
    @view_config(route_name="pbb-sa", renderer="templates/saldo_awal/list.pt",
                 permission="pbb-sa")
    def view(self):
        request = self.req
        return dict(project=request.session['project'])

    ##########
    # Action #
    ##########
    @view_config(route_name='pbb-sa-act', renderer='json',
                 permission='pbb-sa-act')
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
                columns.append(ColumnDT(SaldoAwal.id, mData='id'))
                columns.append(ColumnDT(SaldoAwal.tahun, mData='tahun'))
                columns.append(ColumnDT(SaldoAwal.uraian, mData='uraian'))
                columns.append(ColumnDT(SaldoAwal.tahun_tetap, mData='tahun_tetap'))
                columns.append(ColumnDT(SaldoAwal.nilai, mData='nilai'))
                columns.append(ColumnDT(SaldoAwal.posted, mData='posted'))

                query = pbbDBSession.query().select_from(SaldoAwal).\
                                  filter(SaldoAwal.tahun==self.tahun,
                                         SaldoAwal.posted==self.posted
                                        )
                rowTable = DataTables(req.GET, query, columns)
                return rowTable.output_result()
                
    @view_config(route_name='pbb-sa-add', renderer='templates/saldo_awal/add.pt',
                 permission='pbb-sa-add')
    def view_add(self):
        request = self.req
        form = get_form(request, AddSchema)
        if request.POST:
            if 'simpan' in request.POST:
                controls = request.POST.items()
                controls_dicted = dict(controls)
                
                try:
                    c = form.validate(controls)
                except ValidationFailure, e:
                    return dict(form=form)
                    
                row = save_request(controls_dicted, request)
                #return HTTPFound(location=request.route_url('pbb-sa-edit',id=row.id))
            return route_list(request)
        elif SESS_ADD_FAILED in request.session:
            del request.session[SESS_ADD_FAILED]
        return dict(form=form)

    @view_config(route_name='pbb-sa-edit', renderer='templates/saldo_awal/add.pt',
                 permission='pbb-sa-edit')
    def view_edit(self):
        request = self.request
        row = query_id(request).first()

        if not row:
            return id_not_found(request)
        if row.posted:
            request.session.flash('Data sudah diposting', 'error')
            return route_list(request)

        form = get_form(request, EditSchema)
        if request.POST:
            if 'simpan' in request.POST:
                controls = request.POST.items()
                try:
                    c = form.validate(controls)
                except ValidationFailure, e:
                    return dict(project=request.session['project'], form=form)
                save_request(dict(controls), request, row)
            return route_list(request)
        elif SESS_EDIT_FAILED in request.session:
            del request.session[SESS_EDIT_FAILED]
            return dict(form=form)
        values = row.to_dict()
        form.set_appstruct(values)
        return dict(project=request.session['project'], form=form)

    ##########
    # Delete #
    ##########
    @view_config(route_name='pbb-sa-delete', renderer='templates/saldo_awal/delete.pt',
                 permission='pbb-sa-delete')
    def view_delete(self):
        request = self.req
        q = query_id(request)
        row = q.first()

        if not row:
            return id_not_found(request)
        if row.posted:
            request.session.flash('Data sudah diposting', 'error')
            return route_list(request)

        form = Form(colander.Schema(), buttons=('hapus','cancel'))
        values= {}
        if request.POST:
            if 'hapus' in request.POST:
                msg = '%s dengan id %s telah berhasil.' % (request.title, row.id)
                q.delete()
                pbbDBSession.flush()
                request.session.flash(msg)
            return route_list(request)
        return dict(project=request.session['project'], row=row,form=form.render())

    ###########
    # Posting #
    ###########
    @view_config(route_name='pbb-sa-post', renderer='json',
                 permission='pbb-sa-post')
    def view_posting(self):
        request = self.req
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
    @view_config(route_name='pbb-sa-rpt', 
                 permission='pbb-sa-rpt')
    def view_csv(self):
        query = pbbDBSession.query(SaldoAwal.id,
                      SaldoAwal.tahun,
                      SaldoAwal.uraian,
                      SaldoAwal.tahun_tetap,
                      SaldoAwal.nilai,
                      SaldoAwal.posted).\
              filter(SaldoAwal.tahun==str(self.tahun))
              
        url_dict = self.req.matchdict
        if url_dict['rpt']=='csv' :
            filename = 'saldo_awal.csv'
            return csv_response(self.req, csv_rows(query), filename)

        if url_dict['rpt']=='pdf' :
            _here = os.path.dirname(__file__)
            path = os.path.join(os.path.dirname(_here), 'static')
            print "XXXXXXXXXXXXXXXXXXX", os.path

            logo = os.path.abspath("pajak/static/img/logo.png")
            line = os.path.abspath("pajak/static/img/line.png")

            path = os.path.join(os.path.dirname(_here), 'reports')
            rml_row = open_rml_row(path+'/pbb_saldo_awal.row.rml')
            
            rows=[]
            for r in query.all():
                s = rml_row.format(id=r.id, tahun=r.tahun, uraian=r.uraian, tahun_tetap=r.tahun_tetap, nilai=r.nilai, posted=r.posted)
                rows.append(s)
            
            pdf, filename = open_rml_pdf(path+'/pbb_saldo_awal.rml', rows=rows, 
                                company=self.req.company,
                                departement = self.req.departement,
                                logo = logo,
                                line = line,
                                address = self.req.address)
            return pdf_response(self.req, pdf, filename)

#######
# Add #
#######
def form_validator(form, value):
    def err_kegiatan():
        raise colander.Invalid(form,
            'Kegiatan dengan no urut tersebut sudah ada')

class AddSchema(colander.Schema):
    tahun      = colander.SchemaNode(
                            colander.String())
    uraian      = colander.SchemaNode(
                            colander.String(),
                            missing = colander.drop)
    tahun_tetap         = colander.SchemaNode(
                            colander.String(),
                            title = "Tahun Ketetapan")
    nilai         = colander.SchemaNode(
                            colander.String())
    
class EditSchema(AddSchema):
    id             = colander.SchemaNode(
                          colander.Integer(),
                          oid="id")

def get_form(request, class_form):
    schema = class_form(validator=form_validator)
    schema = schema.bind(jenis_id=JENIS_ID,sumber_id=SUMBER_ID)
    schema.request = request
    return Form(schema, buttons=('simpan','batal'))

def save(request, values, row=None):
    if not row:
        row = SaldoAwal()
    row.from_dict(values)
    pbbDBSession.add(row)
    pbbDBSession.flush()
    return row

def save_request(values, request, row=None):
    if 'id' in request.matchdict:
        values['id'] = request.matchdict['id']
        values['update_uid'] = request.user.id
        values['updated'] = datetime.now()
    else:
        values['create_uid'] = request.user.id
        values['created'] = datetime.now()
        values['posted'] = 0
        
    row = save(request, values, row)
    request.session.flash('Saldo Awal sudah disimpan.')
    return row

def route_list(request):
    return HTTPFound(location=request.route_url('pbb-sa'))

def session_failed(request, session_name):
    r = dict(form=request.session[session_name])
    del request.session[session_name]
    return r


########
# Edit #
########
def query_id(request):
    return pbbDBSession.query(SaldoAwal).filter(SaldoAwal.id==request.matchdict['id'])

def id_not_found(request):
    msg = 'User ID %s not found.' % request.matchdict['id']
    request.session.flash(msg, 'error')
    return route_list(request)

