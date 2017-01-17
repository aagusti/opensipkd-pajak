import sys
import re
import os
import xlrd
from email.utils import parseaddr
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from xlrd import open_workbook, xldate_as_tuple
import colander
import locale
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

from ...views.common import ColumnDT, DataTables    
from ...tools import (dict_to_str, create_now, UploadFiles, get_settings, 
    file_type, dmy, dmy_to_date)
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
            columns, query = get_columns(req)
            qry = query.filter(TmpPendataan.tgl_proses.between(self.dt_awal,self.dt_akhir))
            rowTable = DataTables(req.GET, qry, columns)
            return rowTable.output_result()
        
        elif url_dict['act']=='grid1':
            cari = 'cari' in req.params and req.params['cari'] or ''
            columns, query = get_columns(req)
            
            qry = query.filter(TmpPendataan.tgl_proses.between(ddate_from,ddate_to))
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
        return self.posting(nops)
        
    def posting(self, nops):
        error = 0
        sukses = 0
        nop_error = []
        for nop in nops:
            query = TmpPendataan.query_id(nop).\
                        filter_by(status = 0)
            row = query.first()
            if row and row.no_bumi: 
                data=row.to_dict()
                
                subjekPajak = DatSubjekPajak.query_id(data['subjek_pajak_id']).\
                                first()
                if not subjekPajak:
                    subjekPajak = DatSubjekPajak()
                subjekPajak.from_dict(data)
                pbbDBSession.add(subjekPajak)
                try:
                    pbbDBSession.flush()
                except Exception as e:
                    s = str(e)
                    return dict(success=False,
                                msg = "Error Data Subjek Pajak NOP Msg: %s  " %s)
                
                datObjekPajak = DatObjekPajak.query_id(nop).\
                                    first()
                if not datObjekPajak:
                    datObjekPajak=DatObjekPajak()
                datObjekPajak.from_dict(data)
                pbbDBSession.add(datObjekPajak)
                pbbDBSession.flush()
                
                #--------------------------- Dat OP Bumi -------------------------------#       
                datOpBumi = DatOpBumi.query_id(nop, row.no_bumi).first() 
                if not datOpBumi:
                    datOpBumi=DatOpBumi()
                datOpBumi.from_dict(data)
                pbbDBSession.add(datOpBumi)
                try:
                    pbbDBSession.flush()
                except Exception as e:
                    s = str(e)
                    return dict(success=False,
                                msg = "Error Data Objek Pajak NOP Msg: %s  " %s)
                
                row_dicted = dict(id = nop,
                                  total_luas_bumi = row.luas_bumi)
                DatObjekPajak.set_luas_bumi(row_dicted)
        
                # sql = "Declare out1 number;" \
                      # "Begin "\
                      # "PENENTUAN_NJOP_BUMI('{kd_propinsi}','{kd_dati2}','{kd_kecamatan}','{kd_kelurahan}',"\
                                          # "'{kd_blok}','{no_urut}','{kd_jns_op}','{thn_pajak}','{kunci}',out1);"\
                      # "End;"                                      
                # pbbDBSession.execute(sql.format(kd_propinsi=data['kd_propinsi'],
                                      # kd_dati2=data['kd_dati2'],
                                      # kd_kecamatan=data['kd_kecamatan'],
                                      # kd_kelurahan=data['kd_kelurahan'],
                                      # kd_blok=data['kd_blok'],
                                      # no_urut=data['no_urut'],
                                      # kd_jns_op=data['kd_jns_op'],
                                      # thn_pajak=datetime.now().strftime('%Y'),
                                      # kunci=1))

                #------------- Dat OP Bangunan ------------#            
                if row.no_bng > 0:
                    datOpBangunan = DatOpBangunan.query_id(nop,row.no_bng).first() 
                    if not datOpBangunan:
                        datOpBangunan=DatOpBangunan()
                    datOpBangunan.from_dict(data)
                    pbbDBSession.add(datOpBangunan)
                    try:
                        pbbDBSession.flush()
                        
                    except Exception as e:
                        s = str(e)
                        return dict(success=False,
                                    msg = "Error Data Bangunan NOP Msg: %s  " %s)
                    
                    total_luas_bng = DatOpBangunan.total_luas_bng(row_dicted['id']).scalar()
                    row_dicted['total_luas_bng'] = total_luas_bng
                    DatObjekPajak.set_luas_bng(row_dicted)
        
                    # sql = "Declare out1 number;" \
                          # "Begin "\
                          # "PENENTUAN_NJOP_BNG('{kd_propinsi}','{kd_dati2}','{kd_kecamatan}','{kd_kelurahan}',"\
                                              # "'{kd_blok}','{no_urut}','{kd_jns_op}','{thn_pajak}','{kunci}',out1);"\
                          # "End;"                                      
                    # pbbDBSession.execute(sql.format(kd_propinsi=data['kd_propinsi'],
                                          # kd_dati2=data['kd_dati2'],
                                          # kd_kecamatan=data['kd_kecamatan'],
                                          # kd_kelurahan=data['kd_kelurahan'],
                                          # kd_blok=data['kd_blok'],
                                          # no_urut=data['no_urut'],
                                          # kd_jns_op=data['kd_jns_op'],
                                          # thn_pajak=datetime.now().strftime('%Y'),
                                          # kunci=1))
                    
                    
                    #------------- Dat KD Fasilitas ------------#
                    if not row.kd_fasilitas or row.kd_fasilitas=='00':
                        return dict(success=False,
                                    msg = "Error Fasilitas Harus Diisi NOP  %s" % nop)
                    
                    if row.kd_fasilitas and row.kd_fasilitas!='00':
                        datFasilitasBangunan = DatFasilitasBangunan.query_id(nop,row.no_bng, 
                            row.kd_fasilitas).first()
                                
                        if not datFasilitasBangunan:
                            datFasilitasBangunan=DatFasilitasBangunan()
                        datFasilitasBangunan.from_dict(data)
                        pbbDBSession.add(datFasilitasBangunan)
                        try:
                            pbbDBSession.flush()
                        except Exception as e:
                            s = str(e)
                        
                row.status=1
                row.tgl_proses=datetime.now()
                pbbDBSession.add(row)
                try:
                    pbbDBSession.flush()
                except Exception as e:
                    s = str(e)
                    return dict(success=False,
                                msg = "Error Data Fasilitas NOP Msg: %s  " %s)
                
                sukses += 1
            else:
                return dict(success=False, msg='Error Posting Sensus NOP : %s Bumi Tidak Ditemukan' % nop)     
        return dict(success=True, msg='Sensus NOP : %s Sukses' % sukses )     

    ##########################
    #Upload
    ##########################
    @view_config(route_name='pbb-sensus-upload', renderer='templates/sensus/upload.pt',
        permission='pbb-sensus-upload')
    def view_upload(self):
        request = self.req
        form = get_form(request, UploadSchema)   
        if request.POST:
            if 'upload' in request.POST:
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
        qry = qry.filter(TmpPendataan.tgl_proses.between(self.dt_awal,self.dt_akhir))
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
        form = get_form(request, EditSchema) #
        values= {}
        if request.POST:
            if 'simpan' or 'post' in request.POST:
                controls = request.POST.items()
                try:
                    c = form.validate(controls)
                except ValidationFailure, e:
                    return dict(row=row,form=form)

                    # request.session[SESS_EDIT_FAILED] = e.render()               
                    # return HTTPFound(location=request.route_url('user-edit',
                                      # id=row.id))
                         
                save_request(dict(controls), request, row)
                msg = '%s dengan id %s telah berhasil.' % (request.title, nop_formatted(row))
            if 'post' in request.POST:
                values = dict(controls)
                ids = "%s%s%s%s%s%s%s%s.%s.%s.%s" % (row.kd_propinsi, row.kd_dati2, 
                        row.kd_kecamatan, row.kd_kelurahan, row.kd_blok, 
                        row.no_urut, row.kd_jns_op, row.thn_pendataan,
                        values['no_bumi'],values['no_bng'],values['kd_fasilitas'],)
                
                self.posting([ids])
                
            return route_list(request)
        
        values = row.to_dict()
        #return dict(form=form.render(appstruct=values))
        #------------------DAT OBJEK PAJAK--------------------------------------
        op = pbbDBSession.query(
                DatObjekPajak.subjek_pajak_id.label('old_subjek_pajak_id'),
                DatObjekPajak.no_formulir_spop.label('old_no_formulir_spop'),
                DatObjekPajak.no_persil.label('old_no_persil'),
                DatObjekPajak.jalan_op.label('old_jalan_op'),
                DatObjekPajak.blok_kav_no_op.label('old_blok_kav_no_op'),
                DatObjekPajak.rw_op.label('old_rw_op'),
                DatObjekPajak.rt_op.label('old_rt_op'),
                DatObjekPajak.kd_status_cabang.label('old_kd_status_cabang'),
                DatObjekPajak.kd_status_wp.label('old_kd_status_wp'),
                DatObjekPajak.status_peta_op.label('old_status_peta_op'),
                DatObjekPajak.jns_transaksi_op.label('old_jns_transaksi_op'),
                func.to_char(DatObjekPajak.tgl_pendataan_op,'DD-MM-YYYY').label('old_tgl_pendataan_op'),
                DatObjekPajak.nip_pendata.label('old_nip_pendata'),
                func.to_char(DatObjekPajak.tgl_pemeriksaan_op,'DD-MM-YYYY').label('old_tgl_pemeriksaan_op'),
                DatObjekPajak.nip_pemeriksa_op.label('old_nip_pemeriksa_op'),
                func.to_char(DatObjekPajak.tgl_perekaman_op,'DD-MM-YYYY').label('old_tgl_perekaman_op'),
                DatObjekPajak.nip_perekam_op.label('old_nip_perekam_op'),
             ).filter(
                DatObjekPajak.kd_propinsi==row.kd_propinsi,
                DatObjekPajak.kd_dati2==row.kd_dati2,
                DatObjekPajak.kd_kecamatan==row.kd_kecamatan,
                DatObjekPajak.kd_kelurahan==row.kd_kelurahan,
                DatObjekPajak.kd_blok==row.kd_blok,
                DatObjekPajak.no_urut==row.no_urut,
                DatObjekPajak.kd_jns_op==row.kd_jns_op,
             ).first()
        if op:
            values.update(op._asdict())
            subjek_pajak_id = op.old_subjek_pajak_id
        else:
            subjek_pajak_id = row.subjek_pajak_id
        
        #return dict(form=form.render(appstruct=values))
        #------------------DAT OBJEK PAJAK--------------------------------------
        sp = pbbDBSession.query(
                #DatSubjekPajak.subjek_pajak_id.label('old_subjek_pajak_id'),
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
             ).filter(DatSubjekPajak.subjek_pajak_id==subjek_pajak_id).first()
        if sp:
            values.update(sp._asdict())
        
        #------------------DAT OP BUMI--------------------------------------
        op_bm = pbbDBSession.query(
                DatOpBumi.no_bumi.label('old_no_bumi'),
                DatOpBumi.kd_znt.label('old_kd_znt'),
                DatOpBumi.luas_bumi.label('old_luas_bumi'),
                DatOpBumi.jns_bumi.label('old_jns_bumi'),
                DatOpBumi.nilai_sistem_bumi.label('old_nilai_sistem_bumi'),
             ).filter(
                DatOpBumi.kd_propinsi==row.kd_propinsi,
                DatOpBumi.kd_dati2==row.kd_dati2,
                DatOpBumi.kd_kecamatan==row.kd_kecamatan,
                DatOpBumi.kd_kelurahan==row.kd_kelurahan,
                DatOpBumi.kd_blok==row.kd_blok,
                DatOpBumi.no_urut==row.no_urut,
                DatOpBumi.kd_jns_op==row.kd_jns_op,
                DatOpBumi.no_bumi==row.no_bumi,
             ).first()
        if op_bm:
            values.update(op_bm._asdict())
        #------------------DAT OP BANGUNAN-------------------------------------
        op_bng = pbbDBSession.query(
                DatOpBangunan.no_bng.label('old_no_bng'),
                DatOpBangunan.kd_jpb.label('old_kd_jpb'),
                DatOpBangunan.no_formulir_lspop.label('old_no_formulir_lspop'),
                DatOpBangunan.thn_dibangun_bng.label('old_thn_dibangun_bng'),
                DatOpBangunan.thn_renovasi_bng.label('old_thn_renovasi_bng'),
                DatOpBangunan.luas_bng.label('old_luas_bng'),
                DatOpBangunan.jml_lantai_bng.label('old_jml_lantai_bng'),
                DatOpBangunan.kondisi_bng.label('old_kondisi_bng'),
                DatOpBangunan.jns_konstruksi_bng.label('old_jns_konstruksi_bng'),
                DatOpBangunan.kd_dinding.label('old_kd_dinding'),
                DatOpBangunan.kd_lantai.label('old_kd_lantai'),
                DatOpBangunan.kd_langit_langit.label('old_kd_langit_langit'),
                DatOpBangunan.nilai_sistem_bng.label('old_nilai_sistem_bng'),
                DatOpBangunan.jns_transaksi_bng.label('old_jns_transaksi_bng'),
                func.to_char(DatOpBangunan.tgl_pendataan_bng,'DD-MM-YYYY').label('old_tgl_pendataan_bng'),
                DatOpBangunan.nip_pendata_bng.label('old_nip_pendata_bng'),
                func.to_char(DatOpBangunan.tgl_pemeriksaan_bng,'DD-MM-YYYY').label('old_tgl_pemeriksaan_bng'),
                DatOpBangunan.nip_pemeriksa_bng.label('old_nip_pemeriksa_bng'),
                func.to_char(DatOpBangunan.tgl_perekaman_bng,'DD-MM-YYYY').label('old_tgl_perekaman_bng'),
                DatOpBangunan.nip_perekam_bng.label('old_nip_perekam_bng'),
             ).filter(
                DatOpBangunan.kd_propinsi==row.kd_propinsi,
                DatOpBangunan.kd_dati2==row.kd_dati2,
                DatOpBangunan.kd_kecamatan==row.kd_kecamatan,
                DatOpBangunan.kd_kelurahan==row.kd_kelurahan,
                DatOpBangunan.kd_blok==row.kd_blok,
                DatOpBangunan.no_urut==row.no_urut,
                DatOpBangunan.kd_jns_op==row.kd_jns_op,
                DatOpBangunan.no_bng==row.no_bng,
             ).first()
        if op_bng:
            values.update(op_bng._asdict())

        #------------------DAT FASILITAS BANGUNAN-------------------------------------
        op_fas = pbbDBSession.query(
                DatFasilitasBangunan.kd_fasilitas.label('old_kd_fasilitas'),
                DatFasilitasBangunan.jml_satuan.label('old_jml_satuan'),
             ).filter(
                DatOpBangunan.kd_propinsi==row.kd_propinsi,
                DatOpBangunan.kd_dati2==row.kd_dati2,
                DatOpBangunan.kd_kecamatan==row.kd_kecamatan,
                DatOpBangunan.kd_kelurahan==row.kd_kelurahan,
                DatOpBangunan.kd_blok==row.kd_blok,
                DatOpBangunan.no_urut==row.no_urut,
                DatOpBangunan.kd_jns_op==row.kd_jns_op,
                DatOpBangunan.no_bng==row.no_bng,
             ).first()
        if op_fas:
            values.update(op_fas._asdict())
        values['tgl_pendataan_op'] = dmy(values['tgl_pendataan_op'])
        values['tgl_pemeriksaan_op'] = dmy(values['tgl_pemeriksaan_op'])
        values['tgl_perekaman_op'] = dmy(values['tgl_perekaman_op'])
        values['tgl_pendataan_bng'] = dmy(values['tgl_pendataan_bng'])
        values['tgl_pemeriksaan_bng'] = dmy(values['tgl_pemeriksaan_bng'])
        values['tgl_perekaman_bng'] = dmy(values['tgl_perekaman_bng'])
                        
        values['id'] = id #FixNop(id).get_raw()
        values['nop'] = nop_formatted(id)
        
        form.set_appstruct(values)
        return dict(row=row,form=form)
        
def get_columns(request):
    columns = []
    columns.append(ColumnDT(   func.concat(TmpPendataan.kd_propinsi,
                               func.concat(TmpPendataan.kd_dati2,
                               func.concat(TmpPendataan.kd_kecamatan,
                               func.concat(TmpPendataan.kd_kelurahan,
                               func.concat(TmpPendataan.kd_blok,
                               func.concat(TmpPendataan.no_urut, 
                               func.concat(TmpPendataan.kd_jns_op,
                               func.concat(TmpPendataan.thn_pendataan,
                               func.concat('.',
                               func.concat(TmpPendataan.no_bumi,
                               func.concat('.',
                               func.concat(TmpPendataan.no_bng,
                               func.concat('.',
                                           TmpPendataan.kd_fasilitas)
                               
                            )))))))))))), mData='id'))
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
    columns.append(ColumnDT(TmpPendataan.no_bumi,   mData='bumi'))
    columns.append(ColumnDT(TmpPendataan.no_bng,   mData='bng'))
    columns.append(ColumnDT(TmpPendataan.kd_fasilitas,   mData='fas'))
    columns.append(ColumnDT(TmpPendataan.thn_pendataan,   mData='tahun'))
    columns.append(ColumnDT(TmpPendataan.subjek_pajak_id,   mData='subjek_pajak_id'))
    columns.append(ColumnDT(TmpPendataan.nm_wp,             mData='nm_wp'))
    columns.append(ColumnDT(TmpPendataan.no_formulir_spop,  mData='no_formulir_spop'))
    columns.append(ColumnDT(TmpPendataan.no_formulir_lspop, mData='no_formulir_lspop'))
    columns.append(ColumnDT(TmpPendataan.jalan_op,          mData='jalan_op'))
    columns.append(ColumnDT(func.to_char(TmpPendataan.tgl_pendataan_op,'DD-MM-YYYY'),  mData='tgl_pendataan_op')) #filter=_DTdate
    columns.append(ColumnDT(func.to_char(TmpPendataan.tgl_proses,'DD-MM-YYYY'),        mData='tgl_proses')) #   filter=_DTdate
    columns.append(ColumnDT(TmpPendataan.status,            mData='status'))
    
    query = pbbDBSession.query().select_from(TmpPendataan).\
        filter(TmpPendataan.status == request.session['posted'])
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
    subjek_pajak_id = colander.SchemaNode(colander.String())
    no_formulir_spop = colander.SchemaNode(colander.String())
    no_persil = colander.SchemaNode(colander.String(), missing = unicode(''))
    jalan_op = colander.SchemaNode(colander.String())
    blok_kav_no_op = colander.SchemaNode(colander.String(), missing = unicode(''))
    rw_op = colander.SchemaNode(colander.String(), missing = unicode('00'))
    rt_op = colander.SchemaNode(colander.String(), missing = unicode('000'))
    kd_status_cabang = colander.SchemaNode(colander.Integer())
    kd_status_wp = colander.SchemaNode(colander.String())
    # total_luas_bumi = colander.SchemaNode(colander.Integer(), missing = 0)
    # total_luas_bng = colander.SchemaNode(colander.Integer(), missing = 0)
    # njop_bumi = colander.SchemaNode(colander.Integer(), missing = 0)
    # njop_bng = colander.SchemaNode(colander.Integer(), missing = 0)
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
    # old_total_luas_bumi = colander.SchemaNode(colander.Integer(), 
        # oid = "old_total_luas_bumi", missing = 0)
    # old_total_luas_bng = colander.SchemaNode(colander.Integer(), 
        # oid = "old_total_luas_bng", missing = 0)
    # old_njop_bumi = colander.SchemaNode(colander.Integer(), 
        # oid = "old_njop_bumi", missing = 0)
    # old_njop_bng = colander.SchemaNode(colander.Integer(), 
        # oid = "old_njop_bng", missing = 0)
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
    # kd_propinsi = colander.SchemaNode(colander.String(), missing = unicode(''))
    # kd_dati2 = colander.SchemaNode(colander.String(), missing = unicode(''))
    # kd_kecamatan = colander.SchemaNode(colander.String(), missing = unicode(''))
    # kd_kelurahan = colander.SchemaNode(colander.String(), missing = unicode(''))
    # kd_blok = colander.SchemaNode(colander.String(), missing = unicode(''))
    # no_urut = colander.SchemaNode(colander.String(), missing = unicode(''))
    # kd_jns_op = colander.SchemaNode(colander.String(), missing = unicode(''))
    no_bumi = colander.SchemaNode(colander.Integer(), missing = 0, oid = "no_bumi")
    kd_znt = colander.SchemaNode(colander.String(), missing = unicode(''))
    luas_bumi = colander.SchemaNode(colander.Integer(), missing = 0)
    jns_bumi = colander.SchemaNode(colander.String(), missing = unicode(''))
    #nilai_sistem_bumi = colander.SchemaNode(colander.Integer(), missing = 0)
    def get_data(self):
        pass
        
class OldDatOpBumiSchema(DatOpBumiSchema):
    old_kd_znt = colander.SchemaNode(colander.String(), 
        oid = "", missing = unicode(''))
    old_luas_bumi = colander.SchemaNode(colander.Integer(), 
        oid = "", missing = unicode(''))
    old_jns_bumi = colander.SchemaNode(colander.String(), 
        oid = "", missing = unicode(''))
    # old_nilai_sistem_bumi = colander.SchemaNode(colander.Integer(), 
        # oid = "", missing = 0)
    def get_data(self):
        pass
        
class DatOpBangunanSchema(DatObjekPajakSchema):
    # kd_propinsi = colander.SchemaNode(colander.String(), missing = unicode(''))
    # kd_dati2 = colander.SchemaNode(colander.String(), missing = unicode(''))
    # kd_kecamatan = colander.SchemaNode(colander.String(), missing = unicode(''))
    # kd_kelurahan = colander.SchemaNode(colander.String(), missing = unicode(''))
    # kd_blok = colander.SchemaNode(colander.String(), missing = unicode(''))
    # no_urut = colander.SchemaNode(colander.String(), missing = unicode(''))
    # kd_jns_op = colander.SchemaNode(colander.String(), missing = unicode(''))
    no_bng = colander.SchemaNode(colander.Integer(), missing = unicode(''), oid = "no_bng")
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
    # nilai_sistem_bng = colander.SchemaNode(colander.Integer(), missing=0)
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
    # old_nilai_sistem_bng = colander.SchemaNode(colander.Integer(), 
        # oid = "old_nilai_sistem_bng", missing=0)
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
    # kd_propinsi = colander.SchemaNode(colander.String(), missing = unicode(''))
    # kd_dati2 = colander.SchemaNode(colander.String(), missing = unicode(''))
    # kd_kecamatan = colander.SchemaNode(colander.String(), missing = unicode(''))
    # kd_kelurahan = colander.SchemaNode(colander.String(), missing = unicode(''))
    # kd_blok = colander.SchemaNode(colander.String(), missing = unicode(''))
    # no_urut = colander.SchemaNode(colander.String(), missing = unicode(''))
    # kd_jns_op = colander.SchemaNode(colander.String(), missing = unicode(''))
    # no_bng = colander.SchemaNode(colander.Integer(), missing = 0)
    kd_fasilitas = colander.SchemaNode(colander.String(), missing = unicode('00'), oid = "kd_fasilitas")
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

class AddSchema(OldDatSubjekPajakSchema, OldDatObjekPajakSchema, OldDatOpBumiSchema,
                   OldDatOpBangunanSchema, OldDatFasilitasBangunanSchema):
    nop = colander.SchemaNode(colander.String()) 
    def get_data(self):
        pass    

class EditSchema(AddSchema):
    id = colander.SchemaNode(colander.String(), 
        missing = unicode(''), oid="id")
    def get_data(self):
        pass    
        
def get_form(request, class_form):
    schema = class_form()
    schema = schema.bind()
    schema.request = request
    return Form(schema, buttons=('upload','batal')) 
    
def save(values, user, row=None):
    if not row:
        row = TmpPendataan()
    if values['tgl_pendataan_bng']=='None':
         del values['tgl_pendataan_bng']
    else:
       values['tgl_pendataan_bng'] = dmy_to_date(values['tgl_pendataan_bng'])
       
    if values['tgl_pemeriksaan_bng']=='None':
         del values['tgl_pemeriksaan_bng']
    else:
       values['tgl_pemeriksaan_bng'] = dmy_to_date(values['tgl_pemeriksaan_bng'])
    
    if values['tgl_perekaman_bng']=='None':
         del values['tgl_perekaman_bng']
    else:
       values['tgl_pemeriksaan_bng'] = dmy_to_date(values['tgl_pemeriksaan_bng'])
    
    values['tgl_pendataan_op'] = dmy_to_date(values['tgl_pendataan_op'])
    values['tgl_pemeriksaan_op'] = dmy_to_date(values['tgl_pemeriksaan_op'])
    values['tgl_perekaman_op'] = dmy_to_date(values['tgl_perekaman_op'])
         
    row.from_dict(values)     
    pbbDBSession.add(row)
    pbbDBSession.flush()
    return row
    
def save_request(values, request, row=None):
    if 'id' in request.matchdict:
        values['id'] = request.matchdict['id']
    row = save(values, request.user, row)
    request.session.flash('Pendataan %s berhasil disimpan.' % values['id'])

    
class DbUpload(UploadFiles):
    def __init__(self):
        settings = get_settings()
        dir_path = os.path.realpath(settings['static_files'])
        UploadFiles.__init__(self, dir_path)
        self.settings = settings
        
    def save(self, request, names):
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
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
                if rows < 2:
                   continue
                
                if str(xl_sheet.cell(0,0).value).strip().upper() == 'SUBJEK_PAJAK_ID':
                    for row in range(1,rows):
                        vals = {} 
                        for col in range(0,cols):
                            if col == 0:
                                #print '------------ subjek pajak di conversi dari nop ------ ',col
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
                                    
                            elif col in [39, 43, 44, 49, 50, 57, 66]: #39 44 no bng
                                try:
                                    val = int(xl_sheet.cell(row,col).value)
                                except:
                                    val = 0
                                    
                            elif col in [33,35,37]:
                                try:
                                    val = xldate_as_tuple(xl_sheet.cell(row,col).value,book.datemode)
                                    val = datetime(*val)
                                except:
                                    val = xl_sheet.cell(row,col).value.strip().title()
                                    try:
                                        val = datetime.strptime(val, '%d-%b-%y')
                                    except:
                                        val = datetime.now()
    
                            elif col in [59,61,63]:
                                if xl_sheet.cell(row,col).value == '':
                                    val = None
                                else:
                                    try:
                                        val = xldate_as_tuple(xl_sheet.cell(row,col).value,book.datemode)
                                        val = datetime(*val)
                                    except:
                                        val = xl_sheet.cell(row,col).value.strip().title()
                                        try:
                                            val = datetime.strptime(val, '%d-%b-%y')
                                        except:
                                            val = None
        
                            elif col in [65]:
                                if xl_sheet.cell(row,col).value == '': #kd_fasilitas
                                    val = '00'
                            else:
                                val = xl_sheet.cell(row,col).value
                            vals[xl_sheet.cell(0,col).value.lower()]=val
                        vals['status'] = 0
                        if 'thn_pendataan' not in vals:
                            vals['thn_pendataan'] = datetime.now().year
                        tmp_pendataan = TmpPendataan.query().filter_by(
                            kd_propinsi = vals['kd_propinsi'],
                            kd_dati2 = vals['kd_dati2'],
                            kd_kecamatan = vals['kd_kecamatan'],
                            kd_kelurahan = vals['kd_kelurahan'],
                            kd_blok = vals['kd_blok'],
                            no_urut = vals['no_urut'],
                            kd_jns_op = vals['kd_jns_op'],
                            no_bumi = vals['no_bumi'],
                            no_bng = vals['no_bng'],
                            kd_fasilitas = vals['kd_fasilitas'],
                            ).first()
                        
                        if not tmp_pendataan:
                            tmp_pendataan = TmpPendataan()
                            print '---------------------------------------------'

                        else:
                            print '**********************************************'

                        tmp_pendataan.from_dict(vals)
                        tmp_pendataan.tgl_proses=datetime.now()
                        try:
                            pbbDBSession.add(tmp_pendataan)
                            pbbDBSession.flush()
                        except:
                            error += 1
                        #pbbDBSession.commit()
            locale.setlocale(locale.LC_ALL, self.settings['localization'])        
            return error
        locale.setlocale(locale.LC_ALL, settings['localization'])        

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
