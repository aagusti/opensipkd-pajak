import os
import uuid
from datetime import datetime
from pyramid.view import (view_config,)
from pyramid.httpexceptions import ( HTTPFound, )
import colander
from deform import (Form, widget, ValidationFailure, )
from ...views.common import ColumnDT, DataTables

from sqlalchemy import not_, func, between
from ..models import bphtbDBSession
from ..models.transaksi import PembayaranBphtb, SspdBphtb
from ...tools import _DTstrftime, _DTnumber_format, FixLength
from ..views import BphtbView
import re
from ..views import BPHTB_SELF
from ...report_tools import (
        open_rml_row, open_rml_pdf, pdf_response, 
        csv_response, csv_rows)
    
class BphtbViewRealisasi(BphtbView):
    def __init__(self, request):
        super(BphtbViewRealisasi, self).__init__(request)
        
    @view_config(route_name="bphtb-realisasi", renderer="templates/realisasi/list.pt",
                 permission="bphtb-realisasi")
    def view_list(self):
        return dict(project='Integrasi',
                    posted = self.posted,
                    awal=self.awal,
                    akhir=self.akhir,
                    )

    ##########
    # Action #
    ##########
    @view_config(route_name='bphtb-realisasi-act', renderer='json',
                 permission='bphtb-realisasi-act')
    def view_act(self):
        url_dict = self.req.matchdict
        if url_dict['id']=='grid':
            if url_dict['id']=='grid':
                columns = [
                    ColumnDT(PembayaranBphtb.id, mData="id"),
                    ColumnDT(PembayaranBphtb.transno, mData="transno"),
                    ColumnDT(func.to_char(PembayaranBphtb.tanggal,"DD-MM-YYYY"), mData="tanggal"),
                    ColumnDT(func.concat(PembayaranBphtb.kd_propinsi,
                             func.concat(".", 
                             func.concat(PembayaranBphtb.kd_dati2, 
                             func.concat("-", 
                             func.concat(PembayaranBphtb.kd_kecamatan,
                             func.concat(".", 
                             func.concat(PembayaranBphtb.kd_kelurahan,
                             func.concat("-", 
                             func.concat(PembayaranBphtb.kd_blok,
                             func.concat(".", 
                             func.concat(PembayaranBphtb.no_urut,
                             func.concat(".", PembayaranBphtb.kd_jns_op)))))))))))) ,
                             mData='nop'),
                    ColumnDT(PembayaranBphtb.thn_pajak_sppt, mData='tahun'),
                    ColumnDT(PembayaranBphtb.pembayaran_ke, mData='ke'),
                    ColumnDT(PembayaranBphtb.wp_nama, mData='wp_nama'),
                    ColumnDT(func.concat(SspdBphtb.tahun,
                             func.concat(".", 
                             func.concat( func.lpad(SspdBphtb.kode, 2, '0'), 
                             func.concat(".", func.lpad(SspdBphtb.no_urut, 5, '0'))))),
                             mData="no_tagihan"),
                    #ColumnDT(PembayaranBphtb.no_tagihan, mData='no_tagihan'),
                    ColumnDT(PembayaranBphtb.bayar - PembayaranBphtb.denda, mData='pokok'),
                    ColumnDT(PembayaranBphtb.denda, mData='denda'),
                    ColumnDT(PembayaranBphtb.bayar, mData='bayar'),
                    ColumnDT(PembayaranBphtb.posted, mData='posted'),
                ]
                
                query = bphtbDBSession.query().select_from(PembayaranBphtb).\
                                     join(SspdBphtb).\
                                     filter(PembayaranBphtb.tanggal.between(self.dt_awal,self.dt_akhir)).\
                                     filter(PembayaranBphtb.posted == self.posted,
                                            SspdBphtb.kode!='1')
                
                rowTable = DataTables(self.req.GET, query, columns)
                return rowTable.output_result()
                # select b.id, b.transno, b.tanggal, get_nop_bank(b.id,true) as nop,
                # b.thn_pajak_sppt, b.wp_nama, b.bayar, b.no_tagihan
                # left join bphtb_sspd s on b.sspd_id=s.id
                # from bphtb_bank b

    ##########
    # CSV #
    ##########
    @view_config(route_name='bphtb-realisasi-rpt', renderer='csv',
                 permission='bphtb-realisasi-rpt')
    def view_csv(self):
        query = bphtbDBSession.query(PembayaranBphtb.id.label("id"),
                    PembayaranBphtb.transno.label("transno"),
                    func.to_char(PembayaranBphtb.tanggal,"DD-MM-YYYY").label("tanggal"),
                    func.concat(PembayaranBphtb.kd_propinsi,
                             func.concat(".", 
                             func.concat(PembayaranBphtb.kd_dati2, 
                             func.concat("-", 
                             func.concat(PembayaranBphtb.kd_kecamatan,
                             func.concat(".", 
                             func.concat(PembayaranBphtb.kd_kelurahan,
                             func.concat("-", 
                             func.concat(PembayaranBphtb.kd_blok,
                             func.concat(".", 
                             func.concat(PembayaranBphtb.no_urut,
                             func.concat(".", PembayaranBphtb.kd_jns_op)))))))))))).label('nop'),
                    PembayaranBphtb.thn_pajak_sppt.label('tahun'),
                    PembayaranBphtb.pembayaran_ke.label('ke'),
                    PembayaranBphtb.wp_nama.label('wp_nama'),
                    (PembayaranBphtb.bayar - PembayaranBphtb.denda).label('pokok'),
                    PembayaranBphtb.denda.label('denda'),
                    PembayaranBphtb.bayar.label('bayar'),
                    PembayaranBphtb.posted.label('posted')).\
                join(SspdBphtb).\
                filter(PembayaranBphtb.tanggal.between(self.dt_awal, self.dt_akhir),
                       SspdBphtb.kode!='1')
        url_dict = self.req.matchdict
        if url_dict['rpt']=='csv' :
            filename = 'bphtb_realisasi_ketetapan.csv'
            return csv_response(self.req, csv_rows(query), filename)

        if url_dict['rpt']=='pdf' :
            _here = os.path.dirname(__file__)
            path = os.path.join(os.path.dirname(_here), 'static')
            print "XXXXXXXXXXXXXXXXXXX", os.path

            logo = os.path.abspath("pajak/static/img/logo.png")
            line = os.path.abspath("pajak/static/img/line.png")

            path = os.path.join(os.path.dirname(_here), 'reports')
            rml_row = open_rml_row(path+'/bphtb_realisasi_ketetapan.row.rml')
            
            rows=[]
            for r in query.all():
                s = rml_row.format(nop=r.nop, tahun=r.tahun, ke=r.ke, wp_nama=r.wp_nama, pokok=r.pokok, denda=r.denda,   
                                   bayar=r.bayar, posted=r.posted)
                rows.append(s)
            
            pdf, filename = open_rml_pdf(path+'/bphtb_realisasi_ketetapan.rml', rows=rows, 
                                company=self.req.company,
                                departement = self.req.departement,
                                logo = logo,
                                line = line,
                                address = self.req.address)
            return pdf_response(self.req, pdf, filename)

    ###########
    # Posting #
    ###########
    @view_config(route_name='bphtb-realisasi-post', renderer='json',
                 permission='bphtb-realisasi-post')
    def view_posting(self):
        req = self.req
        ses = req.session
        params   = req.params
        url_dict = req.matchdict
        n_id_not_found = n_row_zero = n_posted = n_id = 0
        if req.POST:
            if url_dict['id']=='post':
                controls = dict(req.POST.items())
                for id in controls['id'].split(","):
                    q = query_id(id)
                    q = q.filter(PembayaranBphtb.tanggal.\
                          between(self.dt_awal,self.dt_akhir))
                    q = q.filter(PembayaranBphtb.posted == self.posted)
                    row    = q.first()
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
                        
                    if row.posted > 1:
                        n_posted = n_posted + 1
                        continue
                    
                    n_id = n_id + 1

                    #id_inv = row.id
                    
                    if self.posted:
                        row.posted = 0 
                    else:
                        row.posted = 1
                    
                    bphtbDBSession.add(row)
                    bphtbDBSession.flush()
                    
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
                
def route_list(request):
    return HTTPFound(location=request.route_url('bphtb-realisasi'))

def session_failed(request, session_name):
    r = dict(form=request.session[session_name])
    del request.session[session_name]
    return r

########
# Edit #
########
def query_id(value):
    return bphtbDBSession.query(PembayaranBphtb).\
           filter(PembayaranBphtb.id==value)

def id_not_found(request):
    msg = 'User ID %s not found.' % request.matchdict['id']
    request.session.flash(msg, 'error')
    return route_list(request)




