import sys
import requests
import json
from tools import json_rpc_header
from config import (
    username,
    pass_encrypted,)


#url = 'http://rpc.bogorkota.net:6543/ws/pbb'
url = 'http://localhost:6543/pbb/api'
url = 'https://pajak.tangselkota.org/pbb/ws/api'
kode = '611001000100100010'
kode = '367605000500100040'
tahun = '2005'
method = 'get_sppt_dop'
username = 'admin'
username = 'bpn'
pass_encrypted = '$2b$12$8GYYsICY1tkALhGdz9xw3OHJy97GYW5FJYmeC1jeSLnVN597y9luO'
pass_encrypted = '$2b$12$AWdtBu31oPfB9zn97Owgd.75kpYlY/OxL38hi4jPICoWo554f6f7W'
argv = sys.argv
if argv[1:]:
    method = argv[1]
if argv[2:]:
    kode = argv[2]
if argv[3:]:
    tahun = argv[3]
if argv[4:]:    
    username = argv[4]
    pass_encrypted = str(argv[6])

def get_dict(method,params):
    return dict(jsonrpc = '2.0',
                method = method,
                params = params,
                id = 1)

piutang = dict(
                kode  = kode,
                tahun  = tahun,
                count  = 5
            )


row_dicted = [] #[data1]
row_dicted.append(piutang)

headers = json_rpc_header(username, pass_encrypted)
params = dict(data=row_dicted)

print "HEADERS", headers
print "PASSWORD", pass_encrypted

data = get_dict(method, params)

jsondata = json.dumps(data, ensure_ascii=False)
print('Send to {url}'.format(url=url))
print(jsondata)      
from datetime import datetime    
awal = datetime.now()
print awal
rows = requests.post(url, data=jsondata, headers=headers, verify=False)
print('Result:')
print(json.loads(rows.text))
akhir = datetime.now()
print akhir
print (akhir - awal)
