import os
import uuid
from datetime import datetime, timedelta
from sqlalchemy import not_, func, between
from pyramid.view import (view_config,)
from pyramid.httpexceptions import ( HTTPFound, )
import colander
from deform import (Form, widget, ValidationFailure, )
from ...pbb.models import pbbDBSession
from ...pbb.models.pelayanan09 import Skkpp, Spmkp, PenerimaKompensasi
from ...pbb.models.pelayanan import PstPermohonan, PstDetail
from ...pbb.models.log_data import LogKeluaranPst
from ...pbb.models.ref import TempatPembayaran
from ...pbb.tools import JNS_RESKOM, fixNop, fixNopel, fixKantor
from ...tools import _DTstrftime, _DTnumber_format
from ...views.common import ColumnDT, DataTables
import re

SESS_ADD_FAILED  = 'Tambah Restitusi/Kompensasi gagal'
SESS_EDIT_FAILED = 'Edit Restitusi/Kompensasi gagal'

from ..views import PbbView

class F170902View(PbbView):
    def _init__(self,request):
        super(F170902View, self).__init__(request)
        
    @view_config(route_name="F170900", renderer="templates/home_restitusi.pt",
                 permission="F170900")
    def home(self):
        return dict(project = self.project)
        
    @view_config(route_name="F170902", renderer="templates/F170902/list.pt",
                 permission="F170902")
    def view(self):
        return dict(project = self.project)

    ##########
    # Action #
    ##########
    @view_config(route_name='F170902-act', renderer='json',
                 permission='F170902-act')
    def view_act(self):
        req = self.req
        ses = req.session
        params   = req.params
        url_dict = req.matchdict
        tahun = self.tahun
        #tahun = '2013'    
        html = {"code":-1,
                "msg":"Tidak Ditemukan"}
        if url_dict['id']=='grid':
            columns = [
                ColumnDT(func.concat(Skkpp.kd_kanwil,
                         func.concat(Skkpp.kd_kantor,
                         func.concat(Skkpp.thn_pelayanan,
                         func.concat(Skkpp.bundel_pelayanan, 
                         func.concat(Skkpp.no_urut_pelayanan, 
                         func.concat(Skkpp.kd_propinsi_pemohon, 
                         func.concat(Skkpp.kd_dati2_pemohon, 
                         func.concat(Skkpp.kd_kecamatan_pemohon,
                         func.concat(Skkpp.kd_kelurahan_pemohon,
                         func.concat(Skkpp.kd_blok_pemohon,
                         func.concat(Skkpp.no_urut_pemohon,
                                     Skkpp.kd_jns_op_pemohon))))))))))),
                         mData='id'),
                
                ColumnDT(func.concat(Skkpp.thn_pelayanan,
                         func.concat(".", 
                         func.concat(Skkpp.bundel_pelayanan, 
                         func.concat(".", 
                                     Skkpp.no_urut_pelayanan)))),
                         mData='nopel'),
                ColumnDT(func.concat(Skkpp.kd_propinsi_pemohon,
                         func.concat(".", 
                         func.concat(Skkpp.kd_dati2_pemohon, 
                         func.concat("-", 
                         func.concat(Skkpp.kd_kecamatan_pemohon,
                         func.concat(".", 
                         func.concat(Skkpp.kd_kelurahan_pemohon,
                         func.concat("-", 
                         func.concat(Skkpp.kd_blok_pemohon,
                         func.concat(".", 
                         func.concat(Skkpp.no_urut_pemohon,
                         func.concat(".", Skkpp.kd_jns_op_pemohon)))))))))))) ,
                         mData='nop'),
                ColumnDT(Skkpp.no_sk_skkpp, mData='nomor'),
                ColumnDT(func.to_char(Skkpp.tgl_sk_skkpp,'DD-MM-YYYY'), mData='tanggal'),
                ColumnDT(Skkpp.jns_keputusan_skkpp, mData='jenis'),
                ColumnDT(Skkpp.nilai_skkpp, mData='nilai'),
            ]

            query = pbbDBSession.query().select_from(Skkpp).\
                        filter(Skkpp.tgl_sk_skkpp.between(self.dt_awal, 
                                          self.dt_akhir+timedelta(days=1)),
                                   Skkpp.posted == self.posted)
                                 
            rowTable = DataTables(req.GET, query, columns)
            return rowTable.output_result()
        elif url_dict['id']=='nopel':
            nopel =  re.sub("\D", "", params["nopel"])
            if nopel:
                nopel = "%s%s%s" % (self.kd_kanwil, self.kd_kantor, nopel)
                q = PstPermohonan.get_by_code(nopel)
                if q and q.first():
                    html = {"code":0,
                            "msg":"Data Ditemukan"}
        elif url_dict['id']=='nop':
            nopel =  re.sub("\D", "", params["nopel"])
            nop =  re.sub("\D", "", params["nop"])
            if nop and nopel:
                nopel = "%s%s%s" % (self.kd_kanwil, self.kd_kantor, nopel)
                q = PstDetail.get_by_code(nopel,nop)
                if q and q.first():
                    row = q.first()
                    if row.kd_jns_pelayanan=="09":
                        html = {"code":0,
                                "msg":"Data Ditemukan"}
                        
        return html
        
        
    ##########
    # CSV #
    ##########
    @view_config(route_name='F170902-rpt', renderer='csv',
                 permission='F170902-rpt')
    def view_csv(self):
        req = self.req
        ses = self.ses
        params   = req.params
        url_dict = req.matchdict
        
        q = pbbDBSession.query(func.concat(Skkpp.thn_pelayanan,
                                func.concat(".", 
                                func.concat(Skkpp.bundel_pelayanan, 
                                func.concat(".", 
                                         Skkpp.no_urut_pelayanan)))).label('nopel'),
                            func.concat(Skkpp.kd_propinsi_pemohon,
                                func.concat(".", 
                                func.concat(Skkpp.kd_dati2_pemohon, 
                                func.concat("-", 
                                func.concat(Skkpp.kd_kecamatan_pemohon,
                                func.concat(".", 
                                func.concat(Skkpp.kd_kelurahan_pemohon,
                                func.concat("-", 
                                func.concat(Skkpp.kd_blok_pemohon,
                                func.concat(".", 
                                func.concat(Skkpp.no_urut_pemohon,
                                func.concat(".", Skkpp.kd_jns_op_pemohon)))))))))))).label('nop'),
                            Skkpp.no_sk_skkpp.label('nomor'),
                            func.to_char(Skkpp.tgl_sk_skkpp,'DD-MM-YYYY').label('tanggal'),
                            Skkpp.jns_keputusan_skkpp.label('jenis'),
                            Skkpp.nilai_skkpp.label('nilai')).\
                            filter(Skkpp.tgl_sk_skkpp.between(self.dt_awal, 
                                              self.dt_akhir+timedelta(days=1)),
                                   Skkpp.posted == self.posted)
        
        filename = 'F170902-rekap.csv'
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


    @view_config(route_name='F170902-add', renderer='templates/F170902/add.pt',
                 permission='F170902-add')
    def view_add(self):
        request = self.req
        form = get_form(request, AddSchema)
        if request.POST:
            if 'simpan' in request.POST:
                controls = request.POST.items()
                try:
                    c = form.validate(controls)
                except ValidationFailure, e:
                    return dict(form=form)				
                save_request(dict(controls), request)
            return route_list(request)
        elif SESS_ADD_FAILED in request.session:
            return session_failed(request, SESS_ADD_FAILED)
        #return dict(form=form.render())
        return dict(project = self.project,
                    form=form)
        
    @view_config(route_name='F170902-edt', renderer='templates/F170902/add.pt',
                 permission='F170902-edt')
    def view_edit(self):
        request = self.req
        row = query_id(request).first()
        if not row:
            return id_not_found(request)
        if row.posted:
            return id_posted(request)
    
        rowRestitusi = query_restitusi_id(request).first()
        rowKompensasi = query_kompensasi_id(request).first()
        
        form = get_form(request, EditSchema)
        if request.POST:
            if 'simpan' in request.POST:
                controls = request.POST.items()
                try:
                    c = form.validate(controls)
                except ValidationFailure, e:
                    return dict(form=form)
                save_request(dict(controls), request, row, rowRestitusi, rowKompensasi)
            return route_list(request)
        elif SESS_EDIT_FAILED in request.session:
            del request.session[SESS_EDIT_FAILED]
            return dict(form=form)
        values = row.to_dict()
        values["nop"] = fixNop.get_raw_dotted()
        values["nopel"] = fixNopel.get_raw_dotted()[6:]
        values["id"] = fixNopel.get_raw()
        values["tgl_sk_skkpp"] = values["tgl_sk_skkpp"].strftime("%d-%m-%Y")
        if rowRestitusi:
            values.update(rowRestitusi.to_dict())
            values["tgl_spmkp"] = values["tgl_spmkp"].strftime("%d-%m-%Y")
        if rowKompensasi:
            values.update(rowKompensasi.to_dict())
            #fixNop['kd_propinsi'] = rowKompensasi['kd_propinsi_kompensasi']
            values["nop_kompensasi"] = rowKompensasi.nop_kompensasi()
            
        form.set_appstruct(values)
        return dict(form=form)
    
    ##########
    # Delete #
    ##########    
    @view_config(route_name='F170902-del', renderer='templates/F170902/delete.pt',
                 permission='F170902-del')
    def view_delete(self):
        request = self.req
        id = request.matchdict['id']
        q = query_id(request)
        row = q.first()
        if not row:
            return id_not_found(request)
        if row.posted:
            return id_posted(request)
    
        form = Form(colander.Schema(), buttons=('hapus','batal'))
        if request.POST:
            if 'hapus' in request.POST:
                msg = 'Pembayaran ID %s  berhasil dihapus.' % (id)
                Spmkp.delete_id(id)
                PenerimaKompensasi.delete_id(id)
                q.delete()
                request.session.flash(msg)
            return route_list(request)
        return dict(project= self.project,
                    row=row,
                    id = id,
                    form=form.render())
    ###########
    # Posting #
    ###########
    @view_config(route_name='F170902-post', renderer='json',
                 permission='F170902-post')
    def view_posting(self):
        request = self.req
        url_dict = request.matchdict
        if request.POST:
            controls = dict(request.POST.items())
            if url_dict['id'] == 'post':
                n_id = n_id_not_found = n_row_zero = n_posted = 0
                msg = ""
                for id in controls['id'].split(","):
                    q = Skkpp.query_id(id)
                    row    = q.first()
                    if not row:
                        n_id_not_found += 1
                        continue

                    if self.posted==0 and row.posted:
                        n_posted = n_posted + 1
                        continue

                    if self.posted==1 and not row.posted:
                        n_posted = n_posted + 1
                        continue

                    n_id = n_id + 1

                    if request.session['posted']==0:
                        row.posted = 1 
                        #TODO: pass data to pembayaran_sppt
                    else:
                        row.posted = 0
                        
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
                    
#######
# Add #
#######
def form_validator(form, value):
    if value["jns_keputusan_skkpp"]=="1":
        if not value["no_spmkp"] or not  value["tgl_spmkp"] \
           or not  value["no_rek_wp"] or not value["nm_bank_wp"]:
            exc = colander.Invalid(
                    form, 'Wajib diisi jika plihan Restitusi')
            
            if not value["no_spmkp"]:
                exc['no_spmkp'] = 'Required'
                
            if not value["tgl_spmkp"]:
                exc['tgl_spmkp'] = 'Required'
            
            if not value["no_rek_wp"]:
                exc['no_rek_wp'] = 'Required'
                
            if not value["nm_bank_wp"]:
                exc['nm_bank_wp'] = 'Required'
            
            raise exc    
            
    elif value["jns_keputusan_skkpp"]=="2":
        if not value["no_urut_penerima_kompensasi"] \
           or not value["no_urut_penerima_kompensasi"] \
           or not value["nop_kompensasi"] \
           or not value["thn_pajak_kompensasi"] \
           or not value["nilai_yang_dikompensasi"]:
            exc = colander.Invalid(
                    form, 'Wajib diisi jika plihan Kompensasi')
            
            if not value["no_urut_penerima_kompensasi"]:
                exc['no_urut_penerima_kompensasi'] = 'Required'
                
            if not value["nop_kompensasi"]:
                exc['nop_kompensasi'] = 'Required'
            
            if not value["thn_pajak_kompensasi"]:
                exc['thn_pajak_kompensasi'] = 'Required'
            
            if not value["nilai_yang_dikompensasi"]:
                exc['nilai_yang_dikompensasi'] = 'Required'
            
            raise exc    
            
            
@colander.deferred
def deferred_jns_reskom(node, kw):
    values = kw.get('list_reskom', [])
    return widget.SelectWidget(values=values)
    
DAFTAR_TP = pbbDBSession.query(TempatPembayaran.kd_tp,TempatPembayaran.nm_tp).\
                    order_by(TempatPembayaran.kd_tp).all()
                    
@colander.deferred
def deferred_tp(node, kw):
    values = kw.get('list_tp', [])
    return widget.SelectWidget(values=values)
    
class AddSchema(colander.Schema):
    nopel = colander.SchemaNode(
                            colander.String(),
                            oid = "nopel",
                            title = "No. Pelayanan",)
    nop = colander.SchemaNode(
                            colander.String(),
                            oid = "nop",
                            title = "NOP",)
                            
    kd_tp = colander.SchemaNode(
                            colander.String(),
                            widget=deferred_tp,
                            oid = "kd_tp",
                            title = "Bank TP",)
    no_sk_skkpp = colander.SchemaNode(
                            colander.String(),
                            oid = "no_sk_skkpp",
                            title = "Nomor SK",)
    tgl_sk_skkpp = colander.SchemaNode(
                            colander.String(),
                            oid = "tgl_sk_skkpp",
                            title = "Tanggal SK",)
    jns_keputusan_skkpp = colander.SchemaNode(
                            colander.String(),
                            widget=deferred_jns_reskom,
                            oid = "jns_keputusan_skkpp",
                            title = "Jenis SK",)
    kpkn = colander.SchemaNode(
                            colander.String(),
                            oid = "kpkn",
                            title = "Kantor Pencairan",)
    nilai_skkpp = colander.SchemaNode(
                            colander.Integer(),
                            oid = "nilai_skkpp",
                            title = "Nilai",)
                            
    no_spmkp = colander.SchemaNode(
                            colander.String(),
                            oid = "no_spmkp",
                            missing=unicode(''),
                            title = "Nomor SPM",)
    tgl_spmkp = colander.SchemaNode(
                            colander.String(),
                            oid = "tgl_spmkp",
                            missing=unicode(''),
                            title = "Tanggal SPM",)
    no_rek_wp = colander.SchemaNode(
                            colander.Integer(),
                            oid = "no_rek_wp",
                            missing=unicode(''),
                            title = "Rekening WP",)
    nm_bank_wp = colander.SchemaNode(
                            colander.String(),
                            oid = "nm_bank_wp",
                            missing=unicode(''),
                            title = "Bank WP",)
                            
    no_urut_penerima_kompensasi = colander.SchemaNode(
                            colander.Integer(),
                            oid = "no_urut_penerima_kompensasi",
                            missing=unicode(''),
                            title = "Nomor Urut",)
    nop_kompensasi = colander.SchemaNode(
                            colander.String(),
                            oid = "nop_kompensasi",
                            missing=unicode(''),
                            title = "NOP",)
    thn_pajak_kompensasi = colander.SchemaNode(
                            colander.String(),
                            oid = "thn_pajak_kompensasi",
                            missing=unicode(''),
                            title = "Tahun Pajak",)
    nilai_yang_dikompensasi = colander.SchemaNode(
                            colander.Integer(),
                            missing=unicode(''),
                            oid = "nilai_yang_dikompensasi",
                            title = "Nilai",)
  
    # tgl_rekam_skkp = colander.SchemaNode(
                            # colander.Date())
    # nip_rekam_skkp = colander.SchemaNode(
                            # colander.String())

def get_form(request, class_form):
    schema = class_form(validator=form_validator)
    schema = schema.bind(list_reskom=JNS_RESKOM, list_tp=DAFTAR_TP)
    schema.request = request
    return Form(schema, buttons=('simpan','batal'))

def save(request, values, row=None, rowRestitusi=None, rowKompensasi=None):
    if not row:
        row = Skkpp()
    
    nopel = re.sub('\D',"",values["nopel"])
    fixNopel.set_raw("%s%s" % (fixKantor.get_raw(), nopel))
    nop = re.sub('\D',"",values["nop"])
    fixNop.set_raw(nop)
    values["kd_kanwil"] = fixNopel["kd_kanwil"]
    values["kd_kantor"] = fixNopel["kd_kantor"]
    values["thn_pelayanan"] = fixNopel["tahun"]
    values["bundel_pelayanan"] = fixNopel["bundel"]
    values["no_urut_pelayanan"] = fixNopel["urut"]
    values["kd_propinsi_pemohon"] = fixNop["kd_propinsi"]
    values["kd_dati2_pemohon"] = fixNop["kd_dati2"]
    values["kd_kecamatan_pemohon"] = fixNop["kd_kecamatan"]
    values["kd_kelurahan_pemohon"] = fixNop["kd_kelurahan"]
    values["kd_blok_pemohon"] = fixNop["kd_blok"]
    values["no_urut_pemohon"] = fixNop["no_urut"]
    values["kd_jns_op_pemohon"] = fixNop["kd_jns_op"]
    values["tgl_rekam_skkp"] = datetime.now()
    values["nip_rekam_skkp"] = request.user.nip()
    values["tgl_sk_skkpp"] = datetime.strptime(values["tgl_sk_skkpp"], "%d-%m-%Y")
    if not row.posted:
        values["posted"] = 0
    
    row.from_dict(values)
    pbbDBSession.add(row)
    pbbDBSession.flush()
    if values["jns_keputusan_skkpp"]=="1": #restitusi
        if not rowRestitusi:
            rowRestitusi = Spmkp()
            
        values["tgl_spmkp"] = datetime.strptime(values["tgl_spmkp"], "%d-%m-%Y")
        values["tgl_rekam_spmkp"] = datetime.now()
        values["nip_rekam_spmkp"] = request.user.nip()
        rowRestitusi.from_dict(values)
        pbbDBSession.add(rowRestitusi)
        
        #hapus kompensasi
        qKompensasi = query_kompensasi_id(request)    
        if qKompensasi.first():
            qKompensasi.delete()
        pbbDBSession.flush()
            
    elif values["jns_keputusan_skkpp"]=="2": #kompensasi
        if not rowKompensasi:
            rowKompensasi = PenerimaKompensasi()
        
        nop = re.sub('\D',"",values["nop_kompensasi"])
        
        fixNop.set_raw(nop)
        values["kd_propinsi_kompensasi"] = fixNop["kd_propinsi"]
        values["kd_dati2_kompensasi"] = fixNop["kd_dati2"]
        values["kd_kecamatan_kompensasi"] = fixNop["kd_kecamatan"]
        values["kd_kelurahan_kompensasi"] = fixNop["kd_kelurahan"]
        values["kd_blok_kompensasi"] = fixNop["kd_blok"]
        values["no_urut_kompensasi"] = fixNop["no_urut"]
        values["kd_jns_op_kompensasi"] = fixNop["kd_jns_op"]
    
        rowKompensasi.from_dict(values)
        pbbDBSession.add(rowKompensasi)
        
        #hapus restitusi
        qRestitusi  = query_restitusi_id(request)
        if qRestitusi.first():
            qRestitusi.delete()
        pbbDBSession.flush()
        
    log_values = {"log_sppt":0, 
                "log_stts":0, 
                "log_dhkp":0, 
                "log_sk":1, 
                "log_status":0}
    LogKeluaranPst.pst_add_log_keluaran(log_values)
    
    return row

def save_request(values, request, row=None, rowRestitusi=None, rowKompensasi=None):
    save(request, values, row, rowRestitusi, rowKompensasi)
    request.session.flash('Data sudah disimpan.')
    return row

def route_list(request):
    return HTTPFound(location=request.route_url('F170902'))

def session_failed(request, session_name):
    r = dict(form=request.session[session_name])
    del request.session[session_name]
    return r
        
########
# Edit #
########
class EditSchema(AddSchema):
    id = colander.SchemaNode(
          colander.String(),
          oid="id")

def query_id(request):
    val = request.matchdict['id']
    return Skkpp.query_id(val)
    
def query_restitusi_id(request): #query realisasi
    val = request.matchdict['id']
    return Spmkp.query_id(val)
                
def query_kompensasi_id(request): #query realisasi
    val = request.matchdict['id']
    val = request.matchdict['id']
    return PenerimaKompensasi.query_id(val)
                
def id_not_found(request):
    msg = 'Data ID %s not found.' % request.matchdict['id']
    request.session.flash(msg, 'error')
    return route_list(request)

def id_posted(request):
    msg = 'Data ID %s sudah diposting.' % request.matchdict['id']
    request.session.flash(msg, 'error')
    return route_list(request)
