from datetime import datetime
#import re
from ...views.base_views import BaseView
from ...pbb.tools import fixKantor
BPHTB_SELF = ('1')

class PbbView(BaseView):
    def __init__(self, request):
        super(PbbView, self).__init__(request)
        self.kd_kantor = 'kd_kantor' in self.ses and self.ses['kd_kantor'] or '01'
        self.kd_kanwil = 'kd_kanwil' in self.ses and self.ses['kd_kanwil'] or '01'
        self.ses['kd_kantor'] = self.kd_kantor
        self.ses['kd_kanwil'] = self.kd_kanwil
        fixKantor.set_raw('%s%s' %(self.kd_kanwil,self.kd_kantor))
        self.project = "project" in self.ses and self.ses["project"] or None
        if "project" in self.params and self.params["project"]:
            self.project = "project" in self.params and self.params["project"]
            self.ses["project"] = self.project