import os
import uuid
from datetime import datetime, timedelta
from sqlalchemy import not_, func, between
from pyramid.view import (view_config,)
from pyramid.httpexceptions import ( HTTPFound, )
import colander
from deform import (Form, widget, ValidationFailure, )
from ...pbb.models import pbbDBSession
from ...pbb.models.tap import PembayaranSppt, Sppt
from ...pbb.models.ref import TempatPembayaran
from ...pbb.tools import JNS_RESKOM, clsNop, clsBank, fixKantor
from ...tools import _DTstrftime, _DTnumber_format
from ...views.common import ColumnDT, DataTables
from ..tools import DAFTAR_TP, dmy, dmy_to_date, clsBayar

import re

SESS_ADD_FAILED  = 'Tambah Pembayaran gagal'
SESS_EDIT_FAILED = 'Edit Pembayaran gagal'

from ..views import PbbView

class F160401View(PbbView): 
    def _init__(self,request):
        super(F160401View, self).__init__(request)
        
    @view_config(route_name="F160401", renderer="templates/F160401/list.pt",
                 permission="F160401")
    def view(self):
        return dict(project=self.project)

    ##########
    # Action #
    ##########
    @view_config(route_name='F160401-act', renderer='json',
                 permission='F160401-act')
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
                ColumnDT(func.concat(PembayaranSppt.kd_propinsi, 
                         func.concat(PembayaranSppt.kd_dati2, 
                         func.concat(PembayaranSppt.kd_kecamatan,
                         func.concat(PembayaranSppt.kd_kelurahan,
                         func.concat(PembayaranSppt.kd_blok,
                         func.concat(PembayaranSppt.no_urut,
                         func.concat(PembayaranSppt.kd_jns_op,
                         func.concat(PembayaranSppt.thn_pajak_sppt,
                         func.concat(PembayaranSppt.kd_kanwil,
                         func.concat(PembayaranSppt.kd_kantor, 
                         func.concat(PembayaranSppt.kd_tp, 
                                     PembayaranSppt.pembayaran_sppt_ke))))))))))),
                         mData='id'),
                
                ColumnDT(func.concat(PembayaranSppt.kd_propinsi,
                         func.concat(".", 
                         func.concat(PembayaranSppt.kd_dati2, 
                         func.concat("-", 
                         func.concat(PembayaranSppt.kd_kecamatan,
                         func.concat(".", 
                         func.concat(PembayaranSppt.kd_kelurahan,
                         func.concat("-", 
                         func.concat(PembayaranSppt.kd_blok,
                         func.concat(".", 
                         func.concat(PembayaranSppt.no_urut,
                         func.concat(".", PembayaranSppt.kd_jns_op)))))))))))) ,
                         mData='nop'),
                ColumnDT(PembayaranSppt.thn_pajak_sppt, mData="tahun"),
                ColumnDT(func.concat(PembayaranSppt.kd_kanwil,
                         func.concat(".", 
                         func.concat(PembayaranSppt.kd_kantor, 
                         func.concat(".", PembayaranSppt.kd_tp)))), mData="tp"),
                         
                ColumnDT(PembayaranSppt.pembayaran_sppt_ke, mData='ke'),
                ColumnDT(func.to_char(PembayaranSppt.tgl_pembayaran_sppt,'DD-MM-YYYY'), mData='tanggal'),
                ColumnDT(PembayaranSppt.denda_sppt, mData='denda'),
                ColumnDT(PembayaranSppt.jml_sppt_yg_dibayar, mData='bayar'),
            ]

            query = pbbDBSession.query().select_from(PembayaranSppt).\
                        filter(PembayaranSppt.tgl_pembayaran_sppt.between(
                                              self.dt_awal, self.dt_akhir,))
                                 
            rowTable = DataTables(req.GET, query, columns)
            return rowTable.output_result()
        elif url_dict['id']=='nop':
            tahun =  re.sub("\D", "", params["tahun"])
            nop =  re.sub("\D", "", params["nop"])
            tanggal =  dmy_to_date(params["tanggal"])
            if nop and tahun:
                piutang = Sppt.piutang(nop,tahun,tanggal)
                if piutang:
                    html = {"code":0,
                            "msg":"Data Ditemukan",
                            "data":{"pokok":piutang['pokok'],
                                    "denda":piutang['denda'],
                                    "jatuh_tempo":dmy(piutang['jatuh_tempo']),
                                    "ke":piutang["ke"]}}
                        
        return html
        
        
    ##########
    # CSV #
    ##########
    @view_config(route_name='F160401-csv', renderer='csv',
                 permission='F160401-csv')
    def view_csv(self):
        req = self.req
        ses = self.ses
        params   = req.params
        url_dict = req.matchdict
        
        q = pbbDBSession.query(
                        func.concat(PembayaranSppt.kd_propinsi,
                        func.concat(".", 
                        func.concat(PembayaranSppt.kd_dati2, 
                        func.concat("-", 
                        func.concat(PembayaranSppt.kd_kecamatan,
                        func.concat(".", 
                        func.concat(PembayaranSppt.kd_kelurahan,
                        func.concat("-", 
                        func.concat(PembayaranSppt.kd_blok,
                        func.concat(".", 
                        func.concat(PembayaranSppt.no_urut,
                        func.concat(".", PembayaranSppt.kd_jns_op)))))))))))).label('nop'),
                        PembayaranSppt.thn_pajak_sppt,
                        func.concat(PembayaranSppt.kd_kanwil,
                        func.concat(".", 
                        func.concat(PembayaranSppt.kd_kantor, 
                        func.concat(".", PembayaranSppt.kd_tp)))).label("TP"),
                        PembayaranSppt.pembayaran_sppt_ke.label('ke'),
                        func.to_char(PembayaranSppt.tgl_pembayaran_sppt,'DD-MM-YYYY').label('tanggal'),
                        PembayaranSppt.denda_sppt.label('denda'),
                        PembayaranSppt.jml_sppt_yg_dibayar.label('bayar'),
                        ).\
                        filter(PembayaranSppt.tgl_pembayaran_sppt.between(self.dt_awal, 
                                  self.dt_akhir,))
        
        filename = 'F160401.csv'
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


    @view_config(route_name='F160401-add', renderer='templates/F160401/add.pt',
                 permission='F160401-add')
    def view_add(self):
        request = self.req
        form = get_form(request, AddSchema)
        if request.POST:
            if 'simpan' in request.POST:
                controls = request.POST.items()
                try:
                    c = form.validate(controls)
                except ValidationFailure, e:
                    return dict(project=self.project,
                                form=form)				
                save_request(dict(controls), request)
            return route_list(request)
        elif SESS_ADD_FAILED in request.session:
            return session_failed(request, SESS_ADD_FAILED)
        #return dict(form=form.render())
        return dict(project=self.project,
                    form=form)
        
    @view_config(route_name='F160401-edt', renderer='templates/F160401/add.pt',
                 permission='F160401-edt')
    def view_edit(self):
        request = self.req
        row = query_id(request).first()

        if not row:
            return id_not_found(request)

        form = get_form(request, EditSchema)
        if request.POST:
            if 'simpan' in request.POST:
                controls = request.POST.items()
                try:
                    c = form.validate(controls)
                except ValidationFailure, e:
                    return dict(form=form)
                save_request(dict(controls), request, row)
            return route_list(request)
        elif SESS_EDIT_FAILED in request.session:
            del request.session[SESS_EDIT_FAILED]
            return dict(form=form)
        values = row.to_dict()
        values["nop"] = fixNop.get_raw_dotted()
        values["id"] = fixNopel.get_raw()
        values["tgl_pembayaran_sppt"] = dmy_to_date(values["tgl_pembayaran_sppt"])
        form.set_appstruct(values)
        return dict(project=self.project,
                    form=form)

    ##########
    # Delete #
    ##########    
    @view_config(route_name='F160401-del', renderer='templates/F160401/delete.pt',
                 permission='F160401-del')
    def view_delete(self):
        request = self.req
        id = request.matchdict['id']
        q = query_id(request)
        row = q.first()
        if not row:
            return id_not_found(request)
        
        form = Form(colander.Schema(), buttons=('reversal','batal'))
        if request.POST:
            if 'reversal' in request.POST:
                msg = 'Pembayaran ID %s senilai %s berhasil dibatalkan.' % (id, row.jml_sppt_yg_dibayar)
                PembayaranSppt.reversal(id)
                request.session.flash(msg)
            return route_list(request)
        return dict(project= self.project,
                    row=row,
                    id = id,
                    form=form.render())
        
#######
# Add #
#######
def form_validator(form, value):
    pass
    # if value["jns_keputusan_skkpp"]=="1":
        # if not value["no_spmkp"] or not  value["tgl_spmkp"] \
           # or not  value["no_rek_wp"] or not value["nm_bank_wp"]:
            # exc = colander.Invalid(
                    # form, 'Wajib diisi jika plihan Restitusi')
            
            # if not value["no_spmkp"]:
                # exc['no_spmkp'] = 'Required'
                
            # if not value["tgl_spmkp"]:
                # exc['tgl_spmkp'] = 'Required'
            
            # if not value["no_rek_wp"]:
                # exc['no_rek_wp'] = 'Required'
                
            # if not value["nm_bank_wp"]:
                # exc['nm_bank_wp'] = 'Required'
            
            # raise exc    
 
            
            
@colander.deferred
def deferred_jns_reskom(node, kw):
    values = kw.get('list_reskom', [])
    return widget.SelectWidget(values=values)
    
                    
@colander.deferred
def deferred_tp(node, kw):
    values = kw.get('list_tp', [])
    return widget.SelectWidget(values=values)
    
class AddSchema(colander.Schema):
    tgl_pembayaran_sppt = colander.SchemaNode(
                            colander.String(),
                            oid = "tgl_pembayaran_sppt",
                            title = "Tgl. Bayar",)
    nop = colander.SchemaNode(
                            colander.String(),
                            oid = "nop",
                            title = "NOP",)
    thn_pajak_sppt = colander.SchemaNode(
                            colander.String(),
                            oid = "thn_pajak_sppt",
                            title = "Tahun Pajak",)
                            
    piutang_pokok = colander.SchemaNode(
                            colander.Integer(),
                            oid = "piutang_pokok",
                            title = "Pokok Pajak",)
    
    piutang_denda = colander.SchemaNode(
                            colander.Integer(),
                            oid = "piutang_denda",
                            title = "Denda Pajak",)
    
    jumlah_piutang = colander.SchemaNode(
                            colander.Integer(),
                            oid = "jumlah_piutang",
                            title = "Jumlah Piutang",)
                            
    jatuh_tempo = colander.SchemaNode(
                            colander.String(),
                            oid = "jatuh_tempo",
                            title = "Tgl. Jatuh Tempo",)
    
    # status = colander.SchemaNode(
                            # colander.String(),
                            # oid = "status",
                            # title = "Status",)
    
    pembayaran_sppt_ke = colander.SchemaNode(
                            colander.Integer(),
                            oid = "pembayaran_sppt_ke",
                            title = "Pembayaran SPPT Ke",)
    
    bayar_pokok = colander.SchemaNode(
                            colander.Integer(),
                            oid = "bayar_pokok",
                            title = "Pembayaran Pokok",)
    
    denda_sppt = colander.SchemaNode(
                            colander.Integer(),
                            oid = "denda_sppt",
                            title = "Pembayaran Denda",)
    jml_sppt_yg_dibayar = colander.SchemaNode(
                            colander.Integer(),
                            oid = "jml_sppt_yg_dibayar",
                            title = "Jumlah Bayar",)
    
    kd_tp = colander.SchemaNode(
                            colander.String(),
                            widget=deferred_tp,
                            oid = "kd_tp",
                            title = "Bank TP",)
    

def get_form(request, class_form):
    schema = class_form(validator=form_validator)
    schema = schema.bind(list_reskom=JNS_RESKOM, list_tp=DAFTAR_TP)
    schema.request = request
    return Form(schema, buttons=('simpan','batal'))

def save(request, values, row=None):
    if not row:
        row = PembayaranSppt()
    
    tp = re.sub('\D',"",values["kd_tp"])
    
    fxBank = clsBank("%s%s" % (fixKantor.get_raw(), tp))
    
    nop = re.sub('\D',"",values["nop"])
    fxNop = clsNop(nop)
    values["kd_kanwil"] = fxBank.kd_kanwil
    values["kd_kantor"] = fxBank.kd_kantor
    values["kd_tp"] = fxBank.kd_tp
    values["kd_propinsi"] = fxNop.kd_propinsi
    values["kd_dati2"] = fxNop.kd_dati2
    values["kd_kecamatan"] = fxNop.kd_kecamatan
    values["kd_kelurahan"] = fxNop.kd_kelurahan
    values["kd_blok"] = fxNop.kd_blok
    values["no_urut"] = fxNop.no_urut
    values["kd_jns_op"] = fxNop.kd_jns_op
    values["nip_rekam_byr_sppt"] = request.user.nip_pbb()
    values["tgl_pembayaran_sppt"] = dmy_to_date(values["tgl_pembayaran_sppt"])
        
    row.from_dict(values)
    if not row.posted:
        row.posted = 0
        
    pbbDBSession.add(row)
    pbbDBSession.flush()
    return row

def save_request(values, request, row=None):
    save(request, values, row)
    request.session.flash('Data sudah disimpan.')
    return row

def route_list(request):
    return HTTPFound(location=request.route_url('F160401'))

def session_failed(request, session_name):
    r = dict(form=request.session[session_name])
    del request.session[session_name]
    return r
        
########
# Edit #
########
class EditSchema(AddSchema):
    id             = colander.SchemaNode(
                          colander.String(),
                          oid="id")

def query_id(request):
    val = request.matchdict['id']
    return PembayaranSppt.query_id(val)
         
def id_not_found(request):
    msg = 'Data ID %s not found.' % request.matchdict['id']
    request.session.flash(msg, 'error')
    return route_list(request)

 ########
# Edit #
########
class EditSchema(AddSchema):
    id             = colander.SchemaNode(
                          colander.String(),
                          oid="id")

   