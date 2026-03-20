#!/usr/bin/python
# input file format: institution name, ip address, ip address change

import django
import sys
import os
import pandas as pd
import xlsxwriter

# format: serial id,cn name,en name,start ip,end ip
os.sys.path.append('../')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paywall2.settings')
django.setup()

from party.models import IpRange
from common.nstl_ip_row_check import (
    ip_check_error_row,
    normalize_excel_serial_id,
    validate_nstl_row_for_load,
)


# Begin main program:

# Open the source file and load into memory.
IpRangeFilename = sys.argv[1]

data = pd.read_excel(IpRangeFilename, index_col=None, usecols="A,B,C,D,E",
        na_filter=False)
output = []
errList = []
toExpire = set()
toIgnore = set()
count = 0
print(len(data))
for index, row in data.iterrows():
    serialId = normalize_excel_serial_id(row['serial id'])
    cn_name = row['cn name']
    en_name = row['en name']
    start = row['start ip']
    end = row['end ip']
    if count % 10 == 0:
        print(str(count) + '/' + str(len(data)))
    count += 1

    try:
        ok, err_rows, ign, exp, start_n, end_n = validate_nstl_row_for_load(
            serialId, cn_name, en_name, start, end, IpRange)
        errList.extend(err_rows)
        toIgnore.update(ign)
        toExpire.update(exp)
        if ok:
            output.append([serialId, cn_name, en_name, start_n, end_n])
    except Exception as e:
        errList.append(ip_check_error_row(serialId, cn_name, en_name, start, end, getattr(e, 'message', str(e))))
        continue

print('error IP ranges to ignore:' + ','.join(toIgnore))
print('total ' + str(len(toIgnore)))
print('IP ranges need to expire:' + ','.join(toExpire))
print('total ' + str(len(toExpire)))

df = pd.DataFrame(output,
    columns=['serial id', 'cn name', 'en name', 'start ip','end ip'])

errdf = pd.DataFrame(errList,
    columns=['serial id', 'cn name', 'en name', 'start ip', 'end ip', 'error', 'ip range id'])

df.to_excel('NSTL_all_ip_to_load.xlsx', engine='xlsxwriter', index=False)
errdf.to_excel('NSTL_all_ip_check_error.xlsx', engine='xlsxwriter', index=False)

# errlog.close()
