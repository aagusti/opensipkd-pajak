import os
import uuid
from datetime import datetime, timedelta
from sqlalchemy import not_, func, between
from pyramid.view import (view_config,)
from pyramid.httpexceptions import ( HTTPFound, )
import colander
from deform import (Form, widget, ValidationFailure, )
from ..models import pbbDBSession
from ..models.pendataan import (
    DatSubjekPajak, DatObjekPajak, DatOpBumi, DatOpBangunan)
#from ...pbb.models.tap import SpptAkrual
from ...pbb.tools import nop_to_id
from ...tools import _DTstrftime, _DTnumber_format #, FixLength
#from ...views.base_views import base_view
from ...views.common import ColumnDT, DataTables
#from ..tools import FixSiklus
import re
from ...report_tools import (
        open_rml_row, open_rml_pdf, pdf_response, 
        csv_response, csv_rows)
        
from ...bphtb.models import bphtbDBSession
from ...bphtb.models.transaksi import Ppat, SspdBphtb
#import transaction        
SESS_ADD_FAILED  = 'Tambah Ketetapan gagal'
SESS_EDIT_FAILED = 'Edit Ketetapan gagal'

from ..views import PbbView
class KetetapanView(PbbView):
    def _init__(self,request):
        super(KetetapanView, self).__init__(request)
        
    @view_config(route_name="F910103", renderer="templates/F910103/list.pt",
                 permission="F910103")
    def view(self):
        return dict(project=self.project )

    ##########
    # Action #
    ##########
    @view_config(route_name='F910103-act', renderer='json',
                 permission='F910103-act')
    def view_act(self):
        url_dict = self.req.matchdict
        if url_dict['act']=='grid':
            if url_dict['act']=='grid':
                columns = [
                    ColumnDT(SspdBphtb.id, mData='id', global_search=False),
                    ColumnDT(func.concat(SspdBphtb.tahun,
                             func.concat(".", 
                             func.concat(SspdBphtb.kode,
                             func.concat(".", SspdBphtb.no_sspd)))) 
                             , mData='sspd_no'),
                    ColumnDT(SspdBphtb.wp_nama, mData='wp_nama'),
                    ColumnDT(func.concat(SspdBphtb.kd_propinsi,
                             func.concat(".", 
                             func.concat(SspdBphtb.kd_dati2, 
                             func.concat("-", 
                             func.concat(SspdBphtb.kd_kecamatan,
                             func.concat(".", 
                             func.concat(SspdBphtb.kd_kelurahan,
                             func.concat("-", 
                             func.concat(SspdBphtb.kd_blok,
                             func.concat(".", 
                             func.concat(SspdBphtb.no_urut,
                             func.concat(".", SspdBphtb.kd_jns_op)))))))))))) ,
                             mData='nop', global_search=True),
                    ColumnDT(SspdBphtb.thn_pajak_sppt, mData='tahun', global_search=True),
                    ColumnDT(SspdBphtb.bphtb_harus_dibayarkan, mData='terhutang', global_search=True),
                    ColumnDT(SspdBphtb.status_pembayaran, mData='bayar', global_search=True),
                    ColumnDT(func.to_char(SspdBphtb.verifikasi_date,'DD-MM-YYYY'), mData='verifikasi_date', global_search=True),
                    ColumnDT(func.to_char(SspdBphtb.verifikasi_bphtb_date,'DD-MM-YYYY'), mData='verifikasi_bphtb_date', global_search=True),
                    ColumnDT(SspdBphtb.status_validasi, mData='status_validasi', global_search=True),
                    ColumnDT(SspdBphtb.no_ajb, mData='no_ajb', global_search=True),
                    ColumnDT(func.to_char(SspdBphtb.tgl_ajb,'DD-MM-YYYY'), mData='tgl_ajb', global_search=True),
                    ColumnDT(SspdBphtb.posted, mData='posted', global_search=True),
                    ColumnDT(Ppat.nama, mData='ppat_nama', global_search=True),
                    ColumnDT(Ppat.kode, mData='ppat_kode', global_search=True),
                ]
                query = bphtbDBSession.query().select_from(SspdBphtb).\
                            join(Ppat).\
                            filter(SspdBphtb.tgl_transaksi.between(self.dt_awal, 
                                              self.dt_akhir+timedelta(days=1),)).\
                            filter(SspdBphtb.posted==2)
                rowTable = DataTables(self.req.GET, query, columns)
                return rowTable.output_result()
            
    ##########
    # CSV #
    ##########
    @view_config(route_name='F910103-rpt', 
                 permission='F910103-rpt')
    def view_csv(self):
        url_dict = self.req.matchdict
        query = bphtbDBSession.query(
                SspdBphtb.id, 
                func.concat(SspdBphtb.tahun,
                    func.concat(".", 
                    func.concat(SspdBphtb.kode,
                    func.concat(".", SspdBphtb.no_sspd)))).label('sspd_no'),
                SspdBphtb.wp_nama.label('wp_nama'),
                func.concat(SspdBphtb.kd_propinsi,
                     func.concat(".", 
                     func.concat(SspdBphtb.kd_dati2, 
                     func.concat("-", 
                     func.concat(SspdBphtb.kd_kecamatan,
                     func.concat(".", 
                     func.concat(SspdBphtb.kd_kelurahan,
                     func.concat("-", 
                     func.concat(SspdBphtb.kd_blok,
                     func.concat(".", 
                     func.concat(SspdBphtb.no_urut,
                     func.concat(".", SspdBphtb.kd_jns_op)))))))))))).label('nop'),
                SspdBphtb.thn_pajak_sppt.label('tahun'),
                SspdBphtb.bphtb_harus_dibayarkan.label('terhutang'),
                SspdBphtb.status_pembayaran.label('bayar'),
                func.to_char(SspdBphtb.verifikasi_date,'DD-MM-YYYY').label('tgl_approval'),
                func.to_char(SspdBphtb.verifikasi_bphtb_date,'DD-MM-YYYY').label('tgl_verifikasi'),
                SspdBphtb.status_validasi.label('status_validasi'),
                SspdBphtb.no_ajb.label('no_ajb'),
                func.to_char(SspdBphtb.tgl_ajb,'DD-MM-YYYY').label('tgl_ajb'),
                SspdBphtb.posted.label('posted'),
                Ppat.nama.label('ppat_nama'),
                Ppat.kode.label('ppat_kode'),).\
                join(Ppat).\
                filter(SspdBphtb.tgl_transaksi.between(self.dt_awal, 
                    self.dt_akhir+timedelta(days=1),)).\
                filter(SspdBphtb.posted==2)
        if url_dict['rpt']=='csv' :
            filename = 'F910103.csv'
            return csv_response(self.req, csv_rows(query), filename)
            
