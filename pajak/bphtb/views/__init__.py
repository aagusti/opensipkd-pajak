from datetime import datetime
#import re
from ...bphtb import BaseView
BPHTB_SELF = ('1')

class BphtbView(BaseView):
    def __init__(self, request):
        super(BphtbView, self).__init__(request)
        self.project = "project" in self.ses and self.ses["project"] or None
        if "project" in self.params and self.params["project"]:
            self.project = "project" in self.params and self.params["project"]
            self.ses["project"] = self.project