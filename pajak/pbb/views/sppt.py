import os
import uuid
from datetime import datetime
from sqlalchemy import not_, func, between
from pyramid.view import (view_config,)
from pyramid.httpexceptions import ( HTTPFound, )
import colander
from deform import (Form, widget, ValidationFailure, )
from ...pbb.models import pbbDBSession
from ...pbb.models.tap import Sppt
#from ...tools import _DTstrftime, _DTnumber_format
#from ...views.base_views import base_view
from ...views.common import ColumnDT, DataTables
from ..views import PbbView

from ...os_reports import open_rml_row, open_rml_pdf, pdf_response, csv_response, csv_rows

SESS_ADD_FAILED  = 'Tambah Saldo Awal gagal'
SESS_EDIT_FAILED = 'Edit Saldo Awal gagal'

class SpptView(PbbView):
    def _init__(self,request):
        super(SpptView, self).__init__(request)
        
    @view_config(route_name="pbb-sppt", renderer="templates/sppt/list.pt",
                 permission="pbb-sppt")
    def view(self):
        return dict(project=self.project)

    ##########
    # Action #
    ##########
    @view_config(route_name='pbb-sppt-act', renderer='json',
                 permission='pbb-sppt-act')
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
                columns.append(ColumnDT(func.concat(Sppt.kd_propinsi,
                                        func.concat(".", 
                                        func.concat(Sppt.kd_dati2, 
                                        func.concat("-", 
                                        func.concat(Sppt.kd_kecamatan,
                                        func.concat(".", 
                                        func.concat(Sppt.kd_kelurahan,
                                        func.concat("-", 
                                        func.concat(Sppt.kd_blok,
                                        func.concat(".", 
                                        func.concat(Sppt.no_urut,
                                        func.concat(".", Sppt.kd_jns_op)))))))))))) ,
                                        mData='nop', global_search=True))
                columns.append(ColumnDT(Sppt.thn_pajak_sppt, mData='tahun', global_search=True))
                columns.append(ColumnDT(Sppt.nm_wp_sppt, mData='nama_wp', global_search=True))
                columns.append(ColumnDT(Sppt.luas_bumi_sppt, mData='luas_bumi', global_search=True))
                columns.append(ColumnDT(Sppt.luas_bng_sppt, mData='luas_bng', global_search=False))
                columns.append(ColumnDT(Sppt.pbb_yg_harus_dibayar_sppt, mData='nilai', global_search=False))

                query = pbbDBSession.query().select_from(Sppt).\
                                     filter(Sppt.thn_pajak_sppt==str(self.tahun))
                rowTable = DataTables(req.GET, query, columns)
                return rowTable.output_result()
                
    ##########
    # CSV #
    ##########
    @view_config(route_name='pbb-sppt-rpt', 
                 permission='pbb-sppt-rpt')
    def view_csv(self):
        url_dict = self.req.matchdict
        query = pbbDBSession.query(func.concat(Sppt.kd_propinsi,
                               func.concat(".", 
                               func.concat(Sppt.kd_dati2, 
                               func.concat("-", 
                               func.concat(Sppt.kd_kecamatan,
                               func.concat(".", 
                               func.concat(Sppt.kd_kelurahan,
                               func.concat("-", 
                               func.concat(Sppt.kd_blok,
                               func.concat(".", 
                               func.concat(Sppt.no_urut,
                               func.concat(".", Sppt.kd_jns_op)))))))))))).label('nop'),
                               Sppt.thn_pajak_sppt,
                               Sppt.nm_wp_sppt,
                               Sppt.luas_bumi_sppt,
                               Sppt.luas_bng_sppt,
                               Sppt.pbb_yg_harus_dibayar_sppt).\
                      filter(Sppt.thn_pajak_sppt==str(self.tahun)).\
                      order_by(Sppt.kd_kecamatan,Sppt.kd_kelurahan,Sppt.kd_blok,Sppt.no_urut).limit(5000)

        if url_dict['rpt']=='csv' :
            filename = 'pbb_sppt.csv'
            return csv_response(self.req, csv_rows(query), filename)

        if url_dict['rpt']=='pdf' :
            _here = os.path.dirname(__file__)
            path = os.path.join(os.path.dirname(_here), 'static')
            print "XXXXXXXXXXXXXXXXXXX", os.path

            logo = os.path.abspath("pajak/static/img/logo.png")
            line = os.path.abspath("pajak/static/img/line.png")

            path = os.path.join(os.path.dirname(_here), 'reports')
            rml_row = open_rml_row(path+'/pbb_sppt.row.rml')
            
            rows=[]
            for r in query.all():
                s = rml_row.format(nop=r.nop, thn_pajak_sppt=r.thn_pajak_sppt, nm_wp_sppt=r.nm_wp_sppt,  
                                   luas_bumi_sppt=r.luas_bumi_sppt, luas_bng_sppt=r.luas_bng_sppt, pbb_yg_harus_dibayar_sppt=r.pbb_yg_harus_dibayar_sppt)
                rows.append(s)
            
            pdf, filename = open_rml_pdf(path+'/pbb_sppt.rml', rows=rows, 
                                company=self.req.company,
                                departement = self.req.departement,
                                logo = logo,
                                line = line,
                                address = self.req.address)
            return pdf_response(self.req, pdf, filename)
