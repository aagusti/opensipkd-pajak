from datetime import datetime
from ...views.base_views import BaseView
from ...pbb.tools import FixKantor
from pyramid.view import view_config
from pyramid.httpexceptions import (
    HTTPFound,
    HTTPForbidden,
    )

class PbbView(BaseView):
    def __init__(self, request):
        super(PbbView, self).__init__(request)
        self.kd_kantor = 'kd_kantor' in self.ses and self.ses['kd_kantor'] or '01'
        self.kd_kanwil = 'kd_kanwil' in self.ses and self.ses['kd_kanwil'] or '01'
        self.ses['kd_kantor'] = self.kd_kantor
        self.ses['kd_kanwil'] = self.kd_kanwil
            
########
# Home #
########
class HomeView(PbbView):
    def __init__(self, request):
        super(HomeView, self).__init__(request)

    @view_config(route_name='F100000', renderer='templates/home.pt',
                 permission='')
    def view_home(self):
        return dict(project='pbb')

            