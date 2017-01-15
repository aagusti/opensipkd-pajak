from datetime import datetime
#import re
from ...views.base_views import BaseView
BPHTB_SELF = ('1')

class BphtbView(BaseView):
    def __init__(self, request):
        super(BphtbView, self).__init__(request)
            