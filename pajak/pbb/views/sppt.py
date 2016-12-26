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
                               func.concat(".", Sppt.kd_jns_op)))))))))))),
                               Sppt.thn_pajak_sppt,
                               Sppt.nm_wp_sppt,
                               Sppt.luas_bumi_sppt,
                               Sppt.luas_bng_sppt,
                               Sppt.pbb_yg_harus_dibayar_sppt).\
                      filter(Sppt.thn_pajak_sppt==tahun)          
        if url_dict['rpt']=='csv' :
            filename = 'saldo_awal.csv'
            return csv_response(self.req, csv_rows(query), filename)