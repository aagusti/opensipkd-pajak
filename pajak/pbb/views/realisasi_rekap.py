import os
import uuid
from datetime import datetime
from sqlalchemy import not_, func, between
from pyramid.view import (view_config,)
from pyramid.httpexceptions import ( HTTPFound, )
import colander
from deform import (Form, widget, ValidationFailure, )
from ..models import pbbDBSession
from ...pbb.tools import FixBank
from ..models.tap import PembayaranRekap, PembayaranSppt
from ...tools import _DTstrftime, _DTnumber_format
#from ...views.base_views import base_view
from ...views.common import ColumnDT, DataTables
import re
from ..views import PbbView
from ...report_tools import (
        open_rml_row, open_rml_pdf, pdf_response, 
        csv_response, csv_rows)
SESS_ADD_FAILED  = 'Tambah Saldo Awal gagal'
SESS_EDIT_FAILED = 'Edit Saldo Awal gagal'

class RealisasiRekapView(PbbView):
    def _init__(self,request):
        super(RealisasiRekap, self).__init__(request)
        
    @view_config(route_name="pbb-realisasi-rekap", renderer="templates/realisasi_rekap/list.pt",
                 permission="pbb-realisasi-rekap")
    def view_list(self):
        req = self.req
        ses = req.session
        params = req.params
        now = datetime.now()
        return dict(project=self.project)

    ##########
    # Action #
    ##########
    @view_config(route_name='pbb-realisasi-rekap-act', renderer='json',
                 permission='pbb-realisasi-rekap-act')
    def view_act(self):
        req = self.req
        ses = req.session
        params   = req.params
        url_dict = req.matchdict
        awal  = self.dt_awal
        akhir = self.dt_akhir
        if url_dict['id']=='grid':
            #pk_id = 'id' in params and params['id'] and int(params['id']) or 0
            if url_dict['id']=='grid':
                # defining columns
                columns = []
                columns.append(ColumnDT(PembayaranRekap.id, mData='id'))
                columns.append(ColumnDT(func.to_char(PembayaranRekap.tanggal,'DD-MM-YYYY'), mData='tanggal'))
                columns.append(ColumnDT(PembayaranRekap.kode, mData='kode'))
                columns.append(ColumnDT(PembayaranRekap.uraian, mData='uraian'))
                columns.append(ColumnDT(PembayaranRekap.bayar - PembayaranRekap.denda, mData='pokok'))
                columns.append(ColumnDT(PembayaranRekap.denda, mData='denda'))
                columns.append(ColumnDT(PembayaranRekap.bayar, mData='bayar'))
                columns.append(ColumnDT(PembayaranRekap.posted, mData='posted'))

                query = pbbDBSession.query().select_from(PembayaranRekap).\
                                     filter(PembayaranRekap.tanggal.between(awal,akhir)).\
                                     filter(PembayaranRekap.posted==self.posted)
                rowTable = DataTables(req.GET, query, columns)
                return rowTable.output_result()
                
    ###########
    # Posting #
    ###########
    @view_config(route_name='pbb-realisasi-rekap-post', renderer='json',
                 permission='pbb-realisasi-rekap-post')
    def view_posting(self):
        req = self.req
        ses = req.session
        params   = req.params
        url_dict = req.matchdict
        n_id_not_found = n_row_zero = n_posted = n_id = 0
        if req.POST:
            controls = dict(req.POST.items())
            awal  = self.dt_awal
            akhir = self.dt_akhir
            
            if url_dict['id']=='gen': #GENERATOR rekap penerimaan
                rows = pbbDBSession.query(PembayaranSppt.tgl_pembayaran_sppt.label('tanggal'),
                                          PembayaranSppt.kd_kanwil,
                                          PembayaranSppt.kd_kantor,
                                          PembayaranSppt.kd_tp,
                                          func.sum(PembayaranSppt.denda_sppt).label('denda'),
                                          func.sum(PembayaranSppt.jml_sppt_yg_dibayar).label('bayar'),
                                          ).\
                             filter(PembayaranSppt.tgl_pembayaran_sppt.between(awal,akhir),
                                    PembayaranSppt.posted==0).\
                             group_by(PembayaranSppt.tgl_pembayaran_sppt,
                                          PembayaranSppt.kd_kanwil,
                                          PembayaranSppt.kd_kantor,
                                          PembayaranSppt.kd_tp,
                                          )
                r = rows.first()
                if not r:
                    return dict(success = False,
                                msg     = 'Tidak ada data yang di proses')
                    
                headers = r.keys()
                bank = FixBank("")
                for row in rows.all():
                    row_dicted = dict(zip(row.keys(), row))
                    
                    bank.kode.from_dict(row_dicted)
                    row_dicted['uraian'] = "Penerimaan Tanggal {tanggal} Bank {bank}".\
                                           format(tanggal = row.tanggal.strftime('%d-%m-%Y'),
                                                  bank = bank.get_raw())
                    row_dicted['kode'] = "{tanggal}-{bank}".\
                                         format(tanggal = row.tanggal.strftime('%Y%m%d'),
                                                bank = bank.get_raw())
                    row_dicted['posted'] = 0
                    pembayaranRekap = PembayaranRekap()
                    pembayaranRekap.from_dict(row_dicted)
                    pbbDBSession.add(pembayaranRekap)
                    pbbDBSession.flush()
                    #row_dicted['tanggal']

                pbbDBSession.query(PembayaranSppt).\
                             filter(PembayaranSppt.posted == 0,
                                    PembayaranSppt.tgl_pembayaran_sppt.between(awal,akhir)).\
                             update({PembayaranSppt.posted: 2}, synchronize_session=False)
                return dict(success = True,
                                msg     = 'Proses Berhasil')
                                
            elif url_dict['id']=='del': #Hapus data rekap
                controls = dict(req.POST.items())
                n_id_not_found = n_posted = 0
                for id in controls['id'].split(","):
                    q = query_id(id)
                    for r in q.all():
                        print 'ID=', r.id
                        
                    row    = q.first()
                    if not row:
                        n_id_not_found = n_id_not_found + 1
                        continue

                    if row.posted:
                        n_posted = n_posted + 1
                        continue
                    n_id = n_id + 1
                    row_dicted = row.to_dict()
                    start_pos = -6
                    bank = FixBank(row_dicted['kode'][start_pos:])
                    #unposting data di Pembayaran SPPT
                    pbbDBSession.query(PembayaranSppt).\
                                 filter(PembayaranSppt.tgl_pembayaran_sppt == row.tanggal,
                                        PembayaranSppt.posted == 2,
                                        PembayaranSppt.kd_kanwil==bank.kd_kanwil,
                                        PembayaranSppt.kd_kantor==bank.kd_kantor,
                                        PembayaranSppt.kd_tp==bank.kd_tp,).\
                                 update({PembayaranSppt.posted:0}, synchronize_session=False)
                    q.delete()
                    pbbDBSession.flush()
                    
                msg = {}        
                if n_id_not_found > 0:
                    msg['id_not_found'] = {'msg': 'Data Tidan Ditemukan %s ' % (n_id_not_found),
                                           'count': n_id_not_found}
                if n_row_zero > 0:
                    msg['row_zero'] = {'msg': 'Data Dengan Nilai 0 sebanyak  %s ' % (n_row_zero),
                                       'count': n_row_zero}
                if n_posted>0:
                    msg['not_posted'] = {'msg': 'Data Tidak Di Proses %s \n' % (n_posted),
                                          'count': n_posted}
                msg['proses'] = {'msg': 'Data Di Proses %s ' % (n_id),
                                 'count':n_id}
                
                return dict(success = True,
                            msg     = msg)
            #POSTING Data                
            elif url_dict['id']=='post':
                controls = dict(req.POST.items())
                for id in controls['id'].split(","):
                    row    = query_id(id).first()
                    if not row:
                        n_id_not_found = n_id_not_found + 1
                        continue

                    if not row.bayar:
                        n_row_zero = n_row_zero + 1
                        continue

                    if not self.posted and row.posted:
                        n_posted = n_posted + 1
                        continue

                    if self.posted and not row.posted:
                        n_posted = n_posted + 1
                        continue

                    n_id = n_id + 1

                    #id_inv = row.id
                    
                    if self.posted:
                        row.posted = 0 
                    else:
                        row.posted = 1
                    pbbDBSession.add(row)
                    pbbDBSession.flush()
                    
                msg = {}        
                if n_id_not_found > 0:
                    msg['id_not_found'] = {'msg': 'Data Tidan Ditemukan %s ' % (n_id_not_found),
                                           'count': n_id_not_found}
                if n_row_zero > 0:
                    msg['row_zero'] = {'msg': 'Data Dengan Nilai 0 sebanyak  %s ' % (n_row_zero),
                                       'count': n_row_zero}
                if n_posted>0:
                    msg['not_posted'] = {'msg': 'Data Tidak Di Proses %s \n' % (n_posted),
                                          'count': n_posted}
                msg['proses'] = {'msg': 'Data Di Proses %s ' % (n_id),
                                 'count':n_id}
                
                return dict(success = True,
                            msg     = msg)
                        
        return dict(success = False,
                    msg     = 'Terjadi kesalahan proses')

    ##########
    # CSV #
    ##########
    @view_config(route_name='pbb-realisasi-rekap-rpt', 
                 permission='pbb-realisasi-rekap-rpt')
    def view_csv(self):
        url_dict = self.req.matchdict
        query = pbbDBSession.query(PembayaranRekap.tanggal,
                               PembayaranRekap.kode,
                               PembayaranRekap.uraian,
                               (PembayaranRekap.bayar - PembayaranRekap.denda).label("pokok"),
                               PembayaranRekap.denda,
                               PembayaranRekap.bayar).\
                      filter(PembayaranRekap.tanggal.between(self.dt_awal,self.dt_akhir),
                             PembayaranRekap.posted == self.posted)
        
        if url_dict['rpt']=='csv' :
            filename = 'pbb-realisasi-rekap.csv'
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
            rml_row = open_rml_row(path+'/pbb_realisasi_rekap.row.rml')
            
            rows=[]
            for r in query.all():
                s = rml_row.format(tanggal=r.tanggal, kode=r.kode, uraian=r.uraian, pokok=r.pokok,   
                                   denda=r.denda, bayar=r.bayar)
                rows.append(s)
            
            pdf, filename = open_rml_pdf(path+'/pbb_realisasi_rekap.rml', rows=rows, 
                                company=self.req.company,
                                departement = self.req.departement,
                                logo = logo,
                                line = line,
                                address = self.req.address)
            return pdf_response(self.req, pdf, filename)
                
def route_list(request):
    return HTTPFound(location=request.route_url('pbb-realisasi-rekap'))

def session_failed(request, session_name):
    r = dict(form=request.session[session_name])
    del request.session[session_name]
    return r

########
# Edit #
########
def query_id(id):
    return pbbDBSession.query(PembayaranRekap).\
           filter(PembayaranRekap.id==id)

def id_not_found(request):
    msg = 'User ID %s not found.' % request.matchdict['id']
    request.session.flash(msg, 'error')
    return route_list(request)


