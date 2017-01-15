import sys
import re
import os
import xlrd
from email.utils import parseaddr
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from xlrd import open_workbook, xldate_as_tuple
import colander
from deform import (
    Form,
    widget,
    ValidationFailure,
    FileData,
    )
from deform.interfaces import FileUploadTempStore
from ..models import (
    pbbDBSession,
    #nop, NOP
    )
from ..models.pendataan import (
    DatObjekPajak, DatSubjekPajak, DatOpBumi, DatOpBangunan, 
    DatFasilitasBangunan, TmpPendataan
    )
    
from sqlalchemy import func, cast, String, BigInteger, tuple_, or_, not_
from sqlalchemy.sql.expression import between
from sqlalchemy.sql import text

from datatables import ColumnDT, DataTables    
from ...tools import dict_to_str, create_now, UploadFiles, get_settings, file_type #,_DTnumberformat,
from time import gmtime, strftime
from datetime import datetime
#from ...security import group_finder
from ..tools import FixNop, nop_formatted
SESS_ADD_FAILED = 'Gagal tambah Data Sensus'
SESS_EDIT_FAILED = 'Gagal edit Data Sensus'

from ..views import PbbView

class SensusView(PbbView):
    def _init__(self,request):
        super(SensusView, self).__init__(request)
        
    ########                    
    # List #
    ########    
    @view_config(route_name='pbb-sensus', renderer='templates/sensus/list.pt',
                 permission="pbb-sensus")
    def view(self):
        return dict(project=self.project )

    ##########                   
    # Action #
    ##########      
    @view_config(route_name='pbb-sensus-act', renderer='json',
                 permission="pbb-sensus-act")
    def view_act(self):
        req = self.req
        ses = req.session
        params   = req.params
        url_dict = req.matchdict 

        if url_dict['id'] == 'grid':
            columns, query = get_columns()
            qry = query.filter(TmpPendataan.tgl_pendataan_op.between(self.dt_awal,self.dt_akhir))
            rowTable = DataTables(req.GET, qry, columns)
            return rowTable.output_result()
        
        elif url_dict['act']=='grid1':
            cari = 'cari' in req.params and req.params['cari'] or ''
            columns, query = get_columns()
            
            qry = query.filter(TmpPendataan.tgl_pendataan_op.between(ddate_from,ddate_to))
            rowTable = DataTables(req.GET, TmpPendataan, qry, columns)
            return rowTable.output_result()
            
    ##########################
    #Upload
    ##########################
    @view_config(route_name='pbb-sensus-post', renderer='json',
        permission='pbb-sensus-post')
    def view_post(self):
        req = self.req
        ses = req.session
        params   = req.params
        url_dict = req.matchdict 

        if url_dict['id'] == 'post':
            nops = req.params['id'].split(',')
        else:
            nops = [url_dict['id']]
        error = 0
        sukses = 0
        nop_error = []
        for n in nops:
            nop = FixNop(n)
            query = TmpPendataan.query_id(n).\
                        filter_by(status == 0)
                        
            row = query.first()
            if row: 
                data=row.to_dict()
                
                subjekPajak = DatSubjekPajak.query_id(data['subjek_pajak_id']).\
                                first()
                if not subjekPajak:
                    subjekPajak = SubjekPajak()
                subjekPajak.from_dict(data)
                pbbDBSession.add(subjekPajak)
                pbbDBSession.flush()
                
                datObjekPajak = DatObjekPajak.query_id(n).\
                                    first()
                if not datObjekPajak:
                    datObjekPajak=DatObjekPajak()
                datObjekPajak.from_dict(data)
                pbbDBSession.add(datObjekPajak)
                pbbDBSession.flush()
                
                #--------------------------- Dat OP Bumi -------------------------------#       
                #--- NJOP bumi  = (nir * 1000) * luas bumi -----------------------------#     
                #--- nilai_bumi_per_m2  = (nilai_bumi_total / luas_bumi_total) * 1000 --#
                if not data['no_bumi']:
                    pbbDBSession.rollback()
                    error += 1
                    nop_error.append(n)
                    continue
                    
                datOpBumi = pbbDBSession.query(DatOpBumi).\
                                       filter(DatOpBumi.kd_propinsi==data['kd_propinsi'],
                                              DatOpBumi.kd_dati2==data['kd_dati2'],
                                              DatOpBumi.kd_kecamatan==data['kd_kecamatan'],
                                              DatOpBumi.kd_kelurahan==data['kd_kelurahan'],
                                              DatOpBumi.kd_blok==data['kd_blok'],
                                              DatOpBumi.no_urut==data['no_urut'],
                                              DatOpBumi.kd_jns_op==data['kd_jns_op'],
                                              DatOpBumi.no_bumi==data['no_bumi']).\
                                       first() 
                if not datBumi:
                    datBumi=DatBumi()
                datBumi.from_dict(data)
                pbbDBSession.add(datBumi)
                pbbDBSession.flush()
                sql = "Declare out1 number;" \
                      "Begin "\
                      "PENENTUAN_NJOP_BUMI('{kd_propinsi}','{kd_dati2}','{kd_kecamatan}','{kd_kelurahan}',"\
                                          "'{kd_blok}','{no_urut}','{kd_jns_op}','{thn_pajak}','{kunci}',out1);"\
                      "End;"                                      
                pbbDBSession.execute(sql.format(kd_propinsi=data['kd_propinsi'],
                                      kd_dati2=data['kd_dati2'],
                                      kd_kecamatan=data['kd_kecamatan'],
                                      kd_kelurahan=data['kd_kelurahan'],
                                      kd_blok=data['kd_blok'],
                                      no_urut=data['no_urut'],
                                      kd_jns_op=data['kd_jns_op'],
                                      thn_pajak=datetime.now().strftime('%Y'),
                                      kunci=1))

                if data['no_bng'] > 0:
                    #------------- Dat OP Bangunan ------------#            
                    datBangunan = pbbDBSession.query(DatBangunan).\
                                           filter(DatBangunan.kd_propinsi==data['kd_propinsi'],
                                                  DatBangunan.kd_dati2==data['kd_dati2'],
                                                  DatBangunan.kd_kecamatan==data['kd_kecamatan'],
                                                  DatBangunan.kd_kelurahan==data['kd_kelurahan'],
                                                  DatBangunan.kd_blok==data['kd_blok'],
                                                  DatBangunan.no_urut==data['no_urut'],
                                                  DatBangunan.kd_jns_op==data['kd_jns_op'],
                                                  DatBangunan.no_bng==data['no_bng']).\
                                           first() 
                    if not datBangunan:
                        datBangunan=DatBangunan()
                    datBangunan.from_dict(data)
                    pbbDBSession.add(datBangunan)
                    pbbDBSession.flush()
                    sql = "Declare out1 number;" \
                          "Begin "\
                          "PENENTUAN_NJOP_BNG('{kd_propinsi}','{kd_dati2}','{kd_kecamatan}','{kd_kelurahan}',"\
                                              "'{kd_blok}','{no_urut}','{kd_jns_op}','{thn_pajak}','{kunci}',out1);"\
                          "End;"                                      
                    pbbDBSession.execute(sql.format(kd_propinsi=data['kd_propinsi'],
                                          kd_dati2=data['kd_dati2'],
                                          kd_kecamatan=data['kd_kecamatan'],
                                          kd_kelurahan=data['kd_kelurahan'],
                                          kd_blok=data['kd_blok'],
                                          no_urut=data['no_urut'],
                                          kd_jns_op=data['kd_jns_op'],
                                          thn_pajak=datetime.now().strftime('%Y'),
                                          kunci=1))
                    
                    
                    #------------- Dat KD Fasilitas ------------#            
                    datFasilitas = pbbDBSession.query(DatFasilitas).\
                                           filter(DatFasilitas.kd_propinsi==data['kd_propinsi'],
                                                  DatFasilitas.kd_dati2==data['kd_dati2'],
                                                  DatFasilitas.kd_kecamatan==data['kd_kecamatan'],
                                                  DatFasilitas.kd_kelurahan==data['kd_kelurahan'],
                                                  DatFasilitas.kd_blok==data['kd_blok'],
                                                  DatFasilitas.no_urut==data['no_urut'],
                                                  DatFasilitas.kd_jns_op==data['kd_jns_op'],
                                                  DatFasilitas.no_bng==data['no_bng'],
                                                  DatFasilitas.kd_fasilitas==data['kd_fasilitas']).\
                                           first() 
                    if not datFasilitas:
                        datFasilitas=DatFasilitas()
                    datFasilitas.from_dict(data)
                    pbbDBSession.add(datFasilitas)
                    pbbDBSession.flush()
                    
                row.status=1
                row.tgl_proses=datetime.now()
                pbbDBSession.add(row)
                pbbDBSession.flush()
                
                sukses += 1
                
                # try:
                    # pbbDBSession.commit()
                # except:
                    # pbbDBSession.rollback()
                    # pbbDBSession.rollback()
                    # pbbDBSession.rollback()
                    # pbbDBSession.rollback()
                    # pbbDBSession.rollback()
                    # return dict(status=0, message='Sensus NOP : %s Gagal' %nop.get_raw())
            # else:
                # return dict(status=1, message='NOP : %s sudah pernah di Sensus' %nop.get_raw()) 
            if error>0:
                return dict(status=0, message='Sensus# %s Sukses %s Error NOP# %s' % (sukses, error, ", ".join(nop_error)))     
                
            return dict(status=1, message='Sensus NOP : %s Sukses' % sukses )     
            
        
    ##########################
    #Upload
    ##########################
    @view_config(route_name='pbb-sensus-upload', renderer='templates/sensus/upload.pt',
        permission='pbb-sensus-upload')
    def view_upload(self):
        request = self.req
        form = get_form(request, UploadSchema)   
        if request.POST:
            print "*********************************************"
            if 'upload' in request.POST:
                print "********************************************* Upload"
                controls = request.POST.items()
                upload_request(dict(controls), request)
                    
            return route_list(request)
        elif SESS_ADD_FAILED in request.session:
            return session_failed(request, SESS_ADD_FAILED)
        return dict(form=form)
                                                                                                                                                                                               
    ########                    
    # CSV  #
    ########          
    @view_config(route_name='pbb-sensus-csv', renderer='csv')
    def view_csv(self):
        req = self.req
        ses = req.session
        params = req.params
        url_dict = req.matchdict 
            
        #if url_dict['csv'] == 'transaksi':
        #columns, 
        qry = TmpPendataan.query_data()
        qry = qry.filter(TmpPendataan.tgl_pendataan_op.between(self.dt_awal,self.dt_akhir))
        r = qry.first()

        header = r.keys()
        query = qry.all()
        rows = []
        for item in query:
            rows.append(list(item))

        # override attributes of response
        filename = 'Data_Pendataan|%s|%s.csv' %(self.awal, self.akhir)
        req.response.content_disposition = 'attachment;filename=' + filename

        return {
          'header': header,
          'rows'  : rows,
        }

    ##########
    # Delete #
    ##########
    @view_config(route_name='pbb-sensus-delete', renderer='templates/sensus/delete.pt',
                 permission='pbb-sensus-delete')
    def view_delete(self):
        request = self.req
        nop = request.matchdict['id']
        q = query_id(nop)
        row = q.first()

        if not row:
            return id_not_found(request)
        if row.status:
            request.session.flash('Data sudah diposting', 'error')
            return route_list(request)

        form = Form(colander.Schema(), buttons=('hapus','cancel'))
        values= {}
        if request.POST:
            if 'hapus' in request.POST:
                msg = '%s dengan id %s telah berhasil.' % (request.title, nop_formatted(row))
                q.delete()
                pbbDBSession.flush()
                request.session.flash(msg)
            return route_list(request)
        return dict(project=request.session['project'], row=row,form=form.render())
        # elif url_dict['act'] == 'delete':
            # nop = clsNop(req.params['id'])
            # query = pbbDBSession.query(TmpPendataan).\
                        # filter_by(kd_propinsi    = nop['kd_propinsi'],
                                  # kd_dati2       = nop['kd_dati2'],
                                  # kd_kecamatan   = nop['kd_kecamatan'],
                                  # kd_kelurahan   = nop['kd_kelurahan'],
                                  # kd_blok        = nop['kd_blok'],
                                  # no_urut        = nop['no_urut'], 
                                  # kd_jns_op      = nop['kd_jns_op'])
            # row = query.first()  
            # print "---- ROW delete --- ",row.to_dict()
            # if row:
                # query.delete()
                # pbbDBSession.flush()
                # try:
                    # pbbDBSession.commit()
                # except:
                    # pbbDBSession.rollback()
                    # return dict(status=0, message='Data Pendataan Sensus NOP : %s gagal dihapus.' %nop.get_raw())
            # return dict(status=1, message='Data Pendataan Sensus NOP : %s sudah dihapus.' %nop.get_raw())   


    ##########
    # Add #
    ##########
    @view_config(route_name='pbb-sensus-add', renderer='templates/sensus/add.pt',
                 permission='pbb-sensus-add')
    def view_add(self):
        request = self.req
        id = request.matchdict['id']
        q = query_id(id)
        row = q.first()

        if not row:
            return id_not_found(request)
        if row.status:
            request.session.flash('Data sudah diposting', 'error')
            return route_list(request)

        form = Form(colander.Schema(), buttons=('simpan','posting','cancel'))
        values= {}
        if request.POST:
            if 'simpan' or 'post' in request.POST:
                msg = '%s dengan id %s telah berhasil.' % (request.title, nop_formatted(row))
                # q.delete()
                # pbbDBSession.flush()
                request.session.flash(msg)
            if 'post' in request.POST:
                pass
            return route_list(request)
        return dict(project=request.session['project'], row=row,form=form.render())
            
    ##########
    # Edit #
    ##########
    @view_config(route_name='pbb-sensus-edit', renderer='templates/sensus/edit.pt',
                 permission='pbb-sensus-edit')
    def view_edit(self):
        request = self.req
        id = request.matchdict['id']
        q = query_id(id)
        row = q.first()

        if not row:
            return id_not_found(request)
        if row.status:
            request.session.flash('Data sudah diposting', 'error')
            return route_list(request)

        form = Form(colander.Schema(), buttons=('simpan','posting','cancel'))
        values= {}
        if request.POST:
            if 'simpan' or 'post' in request.POST:
                msg = '%s dengan id %s telah berhasil.' % (request.title, nop_formatted(row))
                # q.delete()
                # pbbDBSession.flush()
                request.session.flash(msg)
            if 'post' in request.POST:
                pass
            return route_list(request)
        return dict(project=request.session['project'], row=row,form=form.render())
            
    ##########
    # Verify #
    ##########
    @view_config(route_name='pbb-sensus-verify', renderer='templates/sensus/verify.pt',
                 permission='pbb-sensus-verify')
    def view_verify(self):
        request = self.req
        id = request.matchdict['id']
        q = query_id(id)
        row = q.first()

        if not row:
            return id_not_found(request)
        if row.status:
            request.session.flash('Data sudah diposting', 'error')
            return route_list(request)

        #form = Form(colander.Schema(), buttons=('simpan','posting','cancel'))
        form = get_form(request, VerifySchema)
        values= {}
        if request.POST:
            if 'simpan' or 'post' in request.POST:
                msg = '%s dengan id %s telah berhasil.' % (request.title, nop_formatted(row))
                # q.delete()
                # pbbDBSession.flush()
                request.session.flash(msg)
                
            if 'post' in request.POST:
                pass
            return route_list(request)
        
        values = row.to_dict()
        #return dict(form=form.render(appstruct=values))
        sp = pbbDBSession.query(
                DatSubjekPajak.subjek_pajak_id.label('old_subjek_pajak_id'),
                DatSubjekPajak.nm_wp.label('old_nm_wp'),
                DatSubjekPajak.jalan_wp.label('old_jalan_wp'),
                DatSubjekPajak.blok_kav_no_wp.label('old_blok_kav_no_wp'),
                DatSubjekPajak.rw_wp.label('old_rw_wp'),
                DatSubjekPajak.rt_wp.label('old_rt_wp'),
                DatSubjekPajak.kelurahan_wp.label('old_kelurahan_wp'),
                DatSubjekPajak.kota_wp.label('old_kota_wp'),
                DatSubjekPajak.kd_pos_wp.label('old_kd_pos_wp'),
                DatSubjekPajak.telp_wp.label('old_telp_wp'),
                DatSubjekPajak.npwp.label('old_npwp'),
                DatSubjekPajak.status_pekerjaan_wp.label('old_status_pekerjaan_wp'),
             ).filter(DatSubjekPajak.subjek_pajak_id==row.subjek_pajak_id).first()
        values.update(sp._asdict())
        form.set_appstruct(values)
        return dict(row=row,form=form)
        
def get_columns():
    columns = []
    columns.append(ColumnDT(func.concat(TmpPendataan.kd_propinsi,
                               func.concat(TmpPendataan.kd_dati2,
                               func.concat(TmpPendataan.kd_kecamatan,
                               func.concat(TmpPendataan.kd_kelurahan,
                               func.concat(TmpPendataan.kd_blok,
                               func.concat(TmpPendataan.no_urut, 
                               TmpPendataan.kd_jns_op)))))), mData='id'))
    columns.append(ColumnDT(func.concat(TmpPendataan.kd_propinsi,
                               func.concat('.',
                               func.concat(TmpPendataan.kd_dati2,
                               func.concat('-',
                               func.concat(TmpPendataan.kd_kecamatan,
                               func.concat('.',
                               func.concat(TmpPendataan.kd_kelurahan,
                               func.concat('-',
                               func.concat(TmpPendataan.kd_blok,
                               func.concat('.',
                               func.concat(TmpPendataan.no_urut, 
                               func.concat('.',
                               TmpPendataan.kd_jns_op)))))))))))), mData='nop'))
    columns.append(ColumnDT(TmpPendataan.subjek_pajak_id,   mData='subjek_pajak_id'))
    columns.append(ColumnDT(TmpPendataan.nm_wp,             mData='nm_wp'))
    columns.append(ColumnDT(TmpPendataan.no_formulir_spop,  mData='no_formulir_spop'))
    columns.append(ColumnDT(TmpPendataan.no_formulir_lspop, mData='no_formulir_lspop'))
    columns.append(ColumnDT(TmpPendataan.jalan_op,          mData='jalan_op'))
    columns.append(ColumnDT(func.to_char(TmpPendataan.tgl_pendataan_op,'DD-MM-YYYY'),  mData='tgl_pendataan_op')) #filter=_DTdate
    columns.append(ColumnDT(func.to_char(TmpPendataan.tgl_proses,'DD-MM-YYYY'),        mData='tgl_proses')) #   filter=_DTdate
    columns.append(ColumnDT(TmpPendataan.status,            mData='status'))
    
    query = pbbDBSession.query().select_from(TmpPendataan)    
    return columns, query

                

tmpstore = FileUploadTempStore()
             
class UploadSchema(colander.Schema):
    moneywidget = widget.MoneyInputWidget(
                  size=20, 
                  options={'allowZero':True,
                           'precision':0})
    attachment  = colander.SchemaNode(
                  FileData(),
                  widget=widget.FileUploadWidget(tmpstore),
                  validator = None,
                  title="Upload File Excel",
                  #oid = "attachment"
                  )
#######    
# Add #
#######
class DatSubjekPajakSchema(colander.Schema):
    subjek_pajak_id = colander.SchemaNode(colander.String())
    nm_wp = colander.SchemaNode(colander.String())
    jalan_wp = colander.SchemaNode(colander.String())
    blok_kav_no_wp = colander.SchemaNode(colander.String())
    rw_wp = colander.SchemaNode(colander.String())
    rt_wp = colander.SchemaNode(colander.String())
    kelurahan_wp = colander.SchemaNode(colander.String())
    kota_wp = colander.SchemaNode(colander.String())
    kd_pos_wp  = colander.SchemaNode(colander.String(),
                    missing=unicode(''),)
    telp_wp = colander.SchemaNode(colander.String(),
                    missing=unicode(''),)
    npwp = colander.SchemaNode(colander.String(),
                    missing=unicode(''),)
    status_pekerjaan_wp = colander.SchemaNode(colander.String())
    def get_data(self):
        pass
        
class OldDatSubjekPajakSchema(DatSubjekPajakSchema):
    old_subjek_pajak_id = colander.SchemaNode(colander.String(), 
        missing = unicode(''), oid = "old_subjek_pajak_id")
    old_nm_wp = colander.SchemaNode(colander.String(), 
        missing = unicode(''), oid="old_nm_wp")
    old_jalan_wp = colander.SchemaNode(colander.String(), 
        missing = unicode(''), oid="old_jalan_wp")
    old_blok_kav_no_wp = colander.SchemaNode(colander.String(), 
        missing = unicode(''), oid="old_blok_kav_no_wp")
    old_rw_wp = colander.SchemaNode(colander.String(), 
        missing = unicode(''), oid="old_rw_wp")
    old_rt_wp = colander.SchemaNode(colander.String(), 
        missing = unicode(''), oid="old_rt_wp")
    old_kelurahan_wp = colander.SchemaNode(colander.String(), 
        missing = unicode(''), oid="old_kelurahan_wp")
    old_kota_wp = colander.SchemaNode(colander.String(), 
        missing = unicode(''), oid="old_kota_wp")
    old_kd_pos_wp  = colander.SchemaNode(colander.String(), 
        missing=unicode(''), oid="old_kd_pos_wp")
    old_telp_wp = colander.SchemaNode(colander.String(), 
        missing=unicode(''), oid="old_telp_wp")
    old_npwp = colander.SchemaNode(colander.String(), 
        missing=unicode(''), oid="old_npwp")
    old_status_pekerjaan_wp = colander.SchemaNode(colander.String(), 
        missing = unicode(''), oid="old_status_pekerjaan_wp")
    def get_data(self):
        pass
            
class DatObjekPajakSchema(colander.Schema):
    no_objek_pajak = colander.SchemaNode(colander.String())
    subjek_pajak_id = colander.SchemaNode(colander.String())
    no_formulir_spop = colander.SchemaNode(colander.String())
    no_persil = colander.SchemaNode(colander.String(), missing = unicode(''))
    jalan_op = colander.SchemaNode(colander.String())
    blok_kav_no_op = colander.SchemaNode(colander.String(), missing = unicode(''))
    rw_op = colander.SchemaNode(colander.String(), missing = unicode('00'))
    rt_op = colander.SchemaNode(colander.String(), missing = unicode('000'))
    kd_status_cabang = colander.SchemaNode(colander.Integer())
    kd_status_wp = colander.SchemaNode(colander.String())
    total_luas_bumi = colander.SchemaNode(colander.Integer(), missing = 0)
    total_luas_bng = colander.SchemaNode(colander.Integer(), missing = 0)
    njop_bumi = colander.SchemaNode(colander.Integer(), missing = 0)
    njop_bng = colander.SchemaNode(colander.Integer(), missing = 0)
    status_peta_op = colander.SchemaNode(colander.Integer(), missing = 0)
    jns_transaksi_op = colander.SchemaNode(colander.String())
    tgl_pendataan_op = colander.SchemaNode(colander.String())
    nip_pendata = colander.SchemaNode(colander.String())
    tgl_pemeriksaan_op = colander.SchemaNode(colander.String())
    nip_pemeriksa_op = colander.SchemaNode(colander.String())
    tgl_perekaman_op = colander.SchemaNode(colander.String(), missing = unicode(''))
    nip_perekam_op = colander.SchemaNode(colander.String(), missing = unicode(''))
    def get_data(self):
        pass

class OldDatObjekPajakSchema(DatObjekPajakSchema):
    old_subjek_pajak_id = colander.SchemaNode(colander.String(), 
        oid = "old_subjek_pajak_id", missing = unicode(''))
    old_no_formulir_spop = colander.SchemaNode(colander.String(), 
        oid = "old_no_formulir_spop", missing = unicode(''))
    old_no_persil = colander.SchemaNode(colander.String(), 
        oid = "old_no_persil", missing = unicode(''))
    old_jalan_op = colander.SchemaNode(colander.String(), 
        oid = "old_jalan_op", missing = unicode(''))
    old_blok_kav_no_op = colander.SchemaNode(colander.String(), 
        oid = "old_blok_kav_no_op", missing = unicode(''))
    old_rw_op = colander.SchemaNode(colander.String(), 
        oid = "old_rw_op", missing = unicode(''))
    old_rt_op = colander.SchemaNode(colander.String(), 
        oid = "old_rt_op", missing = unicode(''))
    old_kd_status_cabang = colander.SchemaNode(colander.Integer(), 
        oid = "old_kd_status_cabang", missing = 0)
    old_kd_status_wp = colander.SchemaNode(colander.String(), 
        oid = "old_kd_status_wp", missing = unicode(''))
    old_total_luas_bumi = colander.SchemaNode(colander.Integer(), 
        oid = "old_total_luas_bumi", missing = 0)
    old_total_luas_bng = colander.SchemaNode(colander.Integer(), 
        oid = "old_total_luas_bng", missing = 0)
    old_njop_bumi = colander.SchemaNode(colander.Integer(), 
        oid = "old_njop_bumi", missing = 0)
    old_njop_bng = colander.SchemaNode(colander.Integer(), 
        oid = "old_njop_bng", missing = 0)
    old_status_peta_op = colander.SchemaNode(colander.Integer(), 
        oid = "old_status_peta_op", missing = unicode('0'))
    old_jns_transaksi_op = colander.SchemaNode(colander.String(), 
        oid = "old_jns_transaksi_op", missing = unicode(''))
    old_tgl_pendataan_op = colander.SchemaNode(colander.String(), 
        oid = "old_tgl_pendataan_op", missing = unicode(''))
    old_nip_pendata = colander.SchemaNode(colander.String(), 
        oid = "old_nip_pendata", missing = unicode(''))
    old_tgl_pemeriksaan_op = colander.SchemaNode(colander.String(), 
        oid = "old_tgl_pemeriksaan_op", missing = unicode(''))
    old_nip_pemeriksa_op = colander.SchemaNode(colander.String(), 
        oid = "old_nip_pemeriksa_op", missing = unicode(''))
    old_tgl_perekaman_op = colander.SchemaNode(colander.String(), 
        oid = "old_tgl_perekaman_op", missing = unicode(''))
    old_nip_perekam_op = colander.SchemaNode(colander.String(), 
        oid = "old_nip_perekam_op", missing = unicode(''))
    def get_data(self):
        pass

class DatOpBumiSchema(colander.Schema):
    kd_propinsi = colander.SchemaNode(colander.String(), missing = unicode(''))
    kd_dati2 = colander.SchemaNode(colander.String(), missing = unicode(''))
    kd_kecamatan = colander.SchemaNode(colander.String(), missing = unicode(''))
    kd_kelurahan = colander.SchemaNode(colander.String(), missing = unicode(''))
    kd_blok = colander.SchemaNode(colander.String(), missing = unicode(''))
    no_urut = colander.SchemaNode(colander.String(), missing = unicode(''))
    kd_jns_op = colander.SchemaNode(colander.String(), missing = unicode(''))
    no_bumi = colander.SchemaNode(colander.Integer(), missing = 0)
    kd_znt = colander.SchemaNode(colander.String(), missing = unicode(''))
    luas_bumi = colander.SchemaNode(colander.Integer(), missing = 0)
    jns_bumi = colander.SchemaNode(colander.String(), missing = unicode(''))
    nilai_sistem_bumi = colander.SchemaNode(colander.Integer(), missing = 0)
    def get_data(self):
        pass
        
class OldDatOpBumiSchema(DatOpBumiSchema):
    old_kd_znt = colander.SchemaNode(colander.String(), 
        oid = "", missing = unicode(''))
    old_luas_bumi = colander.SchemaNode(colander.Integer(), 
        oid = "", missing = unicode(''))
    old_jns_bumi = colander.SchemaNode(colander.String(), 
        oid = "", missing = unicode(''))
    old_nilai_sistem_bumi = colander.SchemaNode(colander.Integer(), 
        oid = "", missing = 0)
    def get_data(self):
        pass
        
class DatOpBangunanSchema(DatObjekPajakSchema):
    kd_propinsi = colander.SchemaNode(colander.String(), missing = unicode(''))
    kd_dati2 = colander.SchemaNode(colander.String(), missing = unicode(''))
    kd_kecamatan = colander.SchemaNode(colander.String(), missing = unicode(''))
    kd_kelurahan = colander.SchemaNode(colander.String(), missing = unicode(''))
    kd_blok = colander.SchemaNode(colander.String(), missing = unicode(''))
    no_urut = colander.SchemaNode(colander.String(), missing = unicode(''))
    kd_jns_op = colander.SchemaNode(colander.String(), missing = unicode(''))
    no_bng = colander.SchemaNode(colander.Integer(), missing = unicode(''))
    kd_jpb = colander.SchemaNode(colander.String(), missing = unicode(''))
    no_formulir_lspop = colander.SchemaNode(colander.String(), missing = unicode(''))
    thn_dibangun_bng = colander.SchemaNode(colander.String(), missing = unicode(''))
    thn_renovasi_bng = colander.SchemaNode(colander.String(), missing=unicode(''))
    luas_bng = colander.SchemaNode(colander.Integer(), missing = 0)
    jml_lantai_bng = colander.SchemaNode(colander.Integer(), missing = 0)
    kondisi_bng = colander.SchemaNode(colander.String(), missing = unicode(''))
    jns_konstruksi_bng = colander.SchemaNode(colander.String(), missing = unicode(''))
    jns_atap_bng = colander.SchemaNode(colander.String(), missing = unicode(''))
    kd_dinding = colander.SchemaNode(colander.String(), missing = unicode(''))
    kd_lantai = colander.SchemaNode(colander.String(), missing = unicode(''))
    kd_langit_langit = colander.SchemaNode(colander.String(), missing = unicode(''))
    nilai_sistem_bng = colander.SchemaNode(colander.Integer(), missing=0)
    jns_transaksi_bng = colander.SchemaNode(colander.String(), missing = unicode(''))
    tgl_pendataan_bng = colander.SchemaNode(colander.String(), missing = unicode(''))
    nip_pendata_bng = colander.SchemaNode(colander.String(), missing = unicode(''))
    tgl_pemeriksaan_bng = colander.SchemaNode(colander.String(), missing = unicode(''))
    nip_pemeriksa_bng = colander.SchemaNode(colander.String(), missing = unicode(''))
    tgl_perekaman_bng = colander.SchemaNode(colander.String(), missing=unicode(''))
    nip_perekam_bng = colander.SchemaNode(colander.String(), missing=unicode(''))
    def get_data(self):
        pass
        
class OldDatOpBangunanSchema(DatOpBangunanSchema):
    old_kd_jpb = colander.SchemaNode(colander.String(), 
        oid = "old_kd_jpb", missing = unicode(''))
    old_no_formulir_lspop = colander.SchemaNode(colander.String(), 
        oid = "old_no_formulir_lspop", missing = unicode(''))
    old_thn_dibangun_bng = colander.SchemaNode(colander.String(), 
        oid = "old_thn_dibangun_bng", missing = unicode(''))
    old_thn_renovasi_bng = colander.SchemaNode(colander.String(), 
        oid = "old_thn_renovasi_bng", missing=unicode(''))
    old_luas_bng = colander.SchemaNode(colander.Integer(), 
        oid = "old_luas_bng", missing = unicode(''))
    old_jml_lantai_bng = colander.SchemaNode(colander.Integer(), 
        oid = "old_jml_lantai_bng", missing = unicode(''))
    old_kondisi_bng = colander.SchemaNode(colander.String(), 
        oid = "old_kondisi_bng", missing = unicode(''))
    old_jns_konstruksi_bng = colander.SchemaNode(colander.String(), 
        oid = "old_jns_konstruksi_bng", missing = unicode(''))
    old_jns_atap_bng = colander.SchemaNode(colander.String(), 
        oid = "old_jns_atap_bng", missing = unicode(''))
    old_kd_dinding = colander.SchemaNode(colander.String(), 
        oid = "old_kd_dinding", missing = unicode(''))
    old_kd_lantai = colander.SchemaNode(colander.String(), 
        oid = "old_kd_lantai", missing = unicode(''))
    old_kd_langit_langit = colander.SchemaNode(colander.String(), 
        oid = "old_kd_langit_langit", missing = unicode(''))
    old_nilai_sistem_bng = colander.SchemaNode(colander.Integer(), 
        oid = "old_nilai_sistem_bng", missing=0)
    old_jns_transaksi_bng = colander.SchemaNode(colander.String(), 
        oid = "old_jns_transaksi_bng", missing = unicode(''))
    old_tgl_pendataan_bng = colander.SchemaNode(colander.String(), 
        oid = "old_tgl_pendataan_bng", missing = unicode(''))
    old_nip_pendata_bng = colander.SchemaNode(colander.String(), 
        oid = "old_nip_pendata_bng", missing = unicode(''))
    old_tgl_pemeriksaan_bng = colander.SchemaNode(colander.String(), 
        oid = "old_tgl_pemeriksaan_bng", missing = unicode(''))
    old_nip_pemeriksa_bng = colander.SchemaNode(colander.String(), 
        oid = "old_nip_pemeriksa_bng", missing = unicode(''))
    old_tgl_perekaman_bng = colander.SchemaNode(colander.String(), 
        oid = "old_tgl_perekaman_bng", missing=unicode(''))
    old_nip_perekam_bng = colander.SchemaNode(colander.String(), 
        oid = "old_nip_perekam_bng", missing=unicode(''))
    def get_data(self):
        pass
        
class DatFasilitasBangunanSchema(colander.Schema):
    kd_propinsi = colander.SchemaNode(colander.String(), missing = unicode(''))
    kd_dati2 = colander.SchemaNode(colander.String(), missing = unicode(''))
    kd_kecamatan = colander.SchemaNode(colander.String(), missing = unicode(''))
    kd_kelurahan = colander.SchemaNode(colander.String(), missing = unicode(''))
    kd_blok = colander.SchemaNode(colander.String(), missing = unicode(''))
    no_urut = colander.SchemaNode(colander.String(), missing = unicode(''))
    kd_jns_op = colander.SchemaNode(colander.String(), missing = unicode(''))
    no_bng = colander.SchemaNode(colander.Integer(), missing = 0)
    kd_fasilitas = colander.SchemaNode(colander.String(), missing = unicode(''))
    jml_satuan = colander.SchemaNode(colander.Integer(), missing = 0)
    def get_data(self):
        pass
        
class OldDatFasilitasBangunanSchema(DatFasilitasBangunanSchema):
    old_kd_fasilitas = colander.SchemaNode(colander.String(), 
        oid = "old_kd_fasilitas", missing = unicode(''))
    old_jml_satuan = colander.SchemaNode(colander.Integer(), 
        oid = "old_jml_satuan", missing = 0)
    def get_data(self):
        pass

class VerifySchema(OldDatSubjekPajakSchema, OldDatObjekPajakSchema, OldDatOpBumiSchema,
                   OldDatOpBangunanSchema, OldDatFasilitasBangunanSchema):
    id = colander.SchemaNode(colander.Integer())
    def get_data(self):
        pass    
    
def get_form(request, class_form):
    schema = class_form()
    schema = schema.bind()
    schema.request = request
    return Form(schema, buttons=('upload','batal')) 
    
class DbUpload(UploadFiles):
    def __init__(self):
        settings = get_settings()
        dir_path = os.path.realpath(settings['static_files'])
        UploadFiles.__init__(self, dir_path)
        
    def save(self, request, names):
        print "********************************************* Save"
        fileslist = request.POST.getall(names)
        error = 0
        for f in fileslist:
            print f
            if not hasattr(f, 'filename'):
                continue
                
            fullpath = UploadFiles.save(self, f)
            book = open_workbook(fullpath)
            sheet_names = book.sheet_names()
            for sheet_name in sheet_names:
                print sheet_name
                xl_sheet = book.sheet_by_name(sheet_name)
                rows = xl_sheet.nrows
                cols =  xl_sheet.ncols
                print rows,cols
                if rows < 2:
                   continue
                
                if xl_sheet.cell(0,0).value.strip() == 'SUBJEK_PAJAK_ID':
                    for row in range(1,rows):
                        vals = {} 
                        for col in range(0,cols):
                            if col == 0:
                                #print '------------ kolom subjek ------ ',col
                                if xl_sheet.cell(row,col).value == '':
                                    val = "".join([str(xl_sheet.cell(row,12).value), 
                                                   str(xl_sheet.cell(row,13).value),
                                                   str(xl_sheet.cell(row,14).value),
                                                   str(xl_sheet.cell(row,15).value),
                                                   str(xl_sheet.cell(row,16).value),
                                                   str(xl_sheet.cell(row,17).value),
                                                   str(xl_sheet.cell(row,18).value)])
                                else:
                                    val = xl_sheet.cell(row,col).value
                            elif col in [11]: #integer as character 
                                try:
                                    val = str(int(xl_sheet.cell(row,col).value))
                                except:
                                    val = 0
                                    
                            elif col in [43, 44, 49, 50, 57, 66]:
                                try:
                                    val = int(xl_sheet.cell(row,col).value)
                                except:
                                    val = 0
                                    
                            elif col in [33,35,37]:
                                val = xldate_as_tuple(xl_sheet.cell(row,col).value,book.datemode)
                                val = datetime(*val)
                            elif col in [59,61,63]:
                                if xl_sheet.cell(row,col).value == '':
                                    val = None
                                else:
                                    val = xldate_as_tuple(xl_sheet.cell(row,col).value,book.datemode)
                                    val = datetime(*val)
                            else:
                                val = xl_sheet.cell(row,col).value
                            vals[xl_sheet.cell(0,col).value.lower()]=val
                        vals['status'] = 0    
                        tmp_pendataan = TmpPendataan()
                        tmp_pendataan.from_dict(vals)
                        tmp_pendataan.tgl_proses=datetime.now()
                        try:
                            pbbDBSession.add(tmp_pendataan)
                            pbbDBSession.flush()
                        except:
                            error += 1
                        #pbbDBSession.commit()
            return error
            
def upload_request(values, request, row=None):
    dbu = DbUpload()
    error = dbu.save(request, 'upload')
    if error >0:
        return request.session.flash('Data Temporary Pendataan sudah disimpan %s error.' % error)
        
    return request.session.flash('Data Temporary Pendataan sudah disimpan.')

def route_list(request):
    return HTTPFound(location=request.route_url('pbb-sensus'))
    
def session_failed(request, session_name):
    r = dict(form=request.session[session_name])
    del request.session[session_name]
    return r

########
# Edit #
########
def query_id(id):
    return TmpPendataan.query_id(id)

####MKL####
