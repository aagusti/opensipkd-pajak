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
        
    @view_config(route_name="F910102", renderer="templates/F910102/list.pt",
                 permission="F910102")
    def view(self):
        return dict(project=self.project )

    ##########
    # Action #
    ##########
    @view_config(route_name='F910102-act', renderer='json',
                 permission='F910102-act')
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
                            filter(SspdBphtb.posted==1)
                rowTable = DataTables(self.req.GET, query, columns)
                return rowTable.output_result()
            
    ###########
    # Posting #
    ###########
    @view_config(route_name='F910102-post', renderer='json',
                 permission='F910102-post')
    def view_posting(self):
        request = self.req
        url_dict = request.matchdict
        if request.POST:
            controls = dict(request.POST.items())
            if url_dict['id'] == 'post':
                n_id = n_id_not_found = n_sukses = 0
                n_subjek = n_objek = n_bumi = n_bng= 0 
                msg = ""
                for id in controls['id'].split(","):
                    q = query_id(id)
                    row    = q.first()
                    if not row:
                        n_id_not_found += 1
                        continue
                    #Parse Dat Subjel Pajak As PBB DSP
                    ##################################################
                    #UPDATE SUBJEK PAJAK
                    ##################################################
                    id = re.sub('\D',"",row.wp_identitas.upper())
                    if not id:
                        return dict(
                            success = False,
                            msg = "Subjek Pajak ID#{id} Tidak Boleh Kosong {nama}".\
                                format(id = id,
                                    nama = row.wp_nama.upper(), 
                                    ))
                        
                    row_sp = DatSubjekPajak.query_id(id).first()
                    no_formulir_spop = str(row.tahun)+'8'+str(row.kode)+str(row.no_sspd).zfill(5)    
                    no_formulir_lspop = str(row.tahun)+'7'+str(row.kode)+str(row.no_sspd).zfill(5)    
                    id = nop_to_id(row)
                    row_pbb = {
                        'id': id,
                        'subjek_pajak_id': re.sub('\D',"",row.wp_identitas.upper()),
                        'nm_wp'          : row.wp_nama.upper(),
                        'jalan_wp'       : row.wp_alamat.upper()[:30],
                        'blok_kav_no_wp' : row.wp_blok_kav.upper()[:15],
                        'rw_wp'          : row.wp_rw.upper()[-2:0],
                        'rt_wp'          : row.wp_rt.upper()[-3:0],
                        'kelurahan_wp'   : row.wp_kelurahan.upper()[:30],
                        'kota_wp'        : row.wp_kota.upper()[:30],
                        'kd_pos_wp'      : row.wp_kdpos.upper(),
                        'telp_wp'        : hasattr(row,'wp_telp') and row.wp_telp.upper() or None,
                        'npwp'           : re.sub('\D',"",row.wp_npwp.upper()),
                        'kecamatan_wp'   : row.wp_kecamatan.upper(),
                        'provinsi_wp'    :  row.wp_provinsi.upper(),
                        ########################################################
                        'kd_propinsi': row.kd_propinsi,
                        'kd_dati2': row.kd_dati2,
                        'kd_kecamatan': row.kd_kecamatan,
                        'kd_kelurahan': row.kd_kelurahan,
                        'kd_blok': row.kd_blok,
                        'no_urut': row.no_urut,
                        'kd_jns_op': row.kd_jns_op,
                        'no_formulir_spop': no_formulir_spop, #row. "2000.0001.001" 	2016.8109.420
                        #'no_persil': row.
                        'jalan_op': row.op_alamat.upper()[:30],
                        'blok_kav_no_op': row.op_blok_kav.upper()[:15],
                        'rw_op': row.op_rw.upper()[-2:0],
                        'rt_op': row.op_rt.upper()[-3:0],
                        #'kd_status_cabang': row.
                        #'kd_status_wp': row.
                        #'total_luas_bumi': row.
                        #'total_luas_bng': row.
                        #'njop_bumi': row.
                        #'njop_bng': row.
                        #'status_peta_op': row.
                        #'jns_transaksi_op': row.
                        'tgl_pendataan_op': row.verifikasi_date,
                        #'nip_pendata': row.
                        'tgl_pemeriksaan_op': row.verifikasi_bphtb_date,
                        #'nip_pemeriksa_op': row.
                        'tgl_perekaman_op': datetime.now(),
                        'nip_perekam_op': request.user.nip_pbb(),
                        ########################################################
                        'no_bumi': 1,
                        #row_pbb['kd_znt'] =
                        'luas_bumi': row.bumi_luas,
                        #row_pbb['jns_bumi'] =
                        #row_pbb['nilai_sistem_bumi'] =
                        ########################################################
                        'no_bng': 1,
                        'no_formulir_lspop': no_formulir_lspop,
                        'luas_bng': row.bng_luas,
                        'tgl_pendataan_bng': row.verifikasi_date,
                        #'nip_pendata_bng': row.
                        'tgl_pemeriksaan_bng': row.verifikasi_bphtb_date,
                        #'nip_pemeriksa_bng': row.
                        'tgl_perekaman_bng': datetime.now(),
                        'nip_perekam_bng': request.user.nip_pbb()
                        }
                    if not DatSubjekPajak.add_dict(row_pbb, row_sp): 
                        return dict(
                            success = False,
                            msg = "Subjek Pajak ID#{id} Tidak Bisa Di Update {nama}".\
                                format(id = row.wp_identitas,
                                    nama = row.wp_nama.upper(), 
                                    ))
                    #transaction.commit()
                    
                    ##################################################
                    #UPDATE OBJEK PAJAK
                    ##################################################
                    id = nop_to_id(row)
                    row_dop = DatObjekPajak.query_id(id).first()
                    if not row_dop:
                        return dict(
                            success = False,
                            msg = "Objek Pajak ID#{id} Tidak Ditemukan {nama}".\
                                format(id = id,
                                    nama = row.wp_nama.upper(),
                                    ))
                    if not request.user.nip_pbb():
                        return dict(
                            success = False,
                            msg = "NIP tidak ditemukan User#{user}".\
                                format(
                                    user = request.user.nice_username(),
                                    ))
                    
                    if not DatObjekPajak.add_dict(row_pbb, row_dop): 
                        return dict(
                            success = False,
                            msg = "Objek Pajak ID#{id} Tidak Bisa Di Update {nama}".\
                                format(
                                    id = id,
                                    nama = row.wp_nama
                                    ))
                    #transaction.commit()
                                    
                    ##################################################
                    #UPDATE OBJEK BUMI
                    ##################################################
                    if row.bumi_luas>0:
                        row_dom = DatOpBumi.query_id(id,1).first()
                        if not row_dom:
                            return dict(
                                success = False,
                                msg = "Objek Pajak Bumi ID#{id} Tidak Ditemukan {nama}".\
                                    format(id = id,
                                        nama = row.wp_nama.upper(),
                                        ))
                    
                        if not DatOpBumi.add_dict(row_pbb, row_dom): 
                            return dict(
                                success = False,
                                msg = "Objek Pajak ID#{id} Tidak Bisa Di Update {nama}".\
                                    format(
                                        id = id,
                                        nama = row.wp_nama
                                        ))
                    #transaction.commit()
                    ##################################################
                    #UPDATE OBJEK BANGUNAN
                    ##################################################
                    if row.bng_luas>0:
                        row_dog = DatOpBangunan.query_id(id,1).first()
                        if not row_dog:
                            return dict(
                                success = False,
                                msg = "Objek Pajak Bumi ID#{id} Tidak Ditemukan {nama}".\
                                    format(id = id,
                                        nama = row.wp_nama.upper(),
                                        ))
                    
  
                        if not DatOpBangunan.add_dict(row_pbb, row_dog): 
                            return dict(
                                success = False,
                                msg = "Objek Bangunan ID#{id} Tidak Bisa Di Update {nama}".\
                                    format(
                                        id = id,
                                        nama = row.wp_nama
                                        ))
                        #transaction.commit()

                    # pbbDBSession.flush()
                    #Update BPHTB
                    row.posted = 2
                    bphtbDBSession.add(row)
                    bphtbDBSession.flush()
                    n_sukses += 1
                    
                msg = '%s Data Di Proses' % (n_sukses)
                
                return dict(success = True,
                            msg     = msg)
                            
            return dict(success = False,
                    msg     = 'Terjadi kesalahan proses')

    ##########
    # CSV #
    ##########
    @view_config(route_name='F910102-rpt', 
                 permission='F910102-rpt')
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
                filter(SspdBphtb.posted==1)
        if url_dict['rpt']=='csv' :
            filename = 'F910102.csv'
            return csv_response(self.req, csv_rows(query), filename)
            
########
# Edit #
########
def query_id(id):
    #nop = FixSiklus(id)
    return bphtbDBSession.query(SspdBphtb).\
           filter(SspdBphtb.id==id)                  

def id_not_found(value):
    msg = 'NOP ID %s not found.' % value
    request.session.flash(msg, 'error')
    return route_list(request)