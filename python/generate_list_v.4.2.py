import json
import urllib3
import urllib.request
import requests 
import sys
import os
import time
try:
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials
except ModuleNotFoundError:
    print('Module gspread is not installed. Please run "sudo apt install python3-pip && pip3 install gspread && pip3 install --upgrade oauth2client "')
    exit()
try:
    import ocscred_config as cfg
except ModuleNotFoundError:
    print('Configuration file "ocscred_config.py" does not exists.')
    exit()

timestr = time.strftime("%Y%m%d-%H%M%S")
CSV_output = 'output-' + timestr + '.csv'
TXT_output = 'soft_list-' + timestr + '.txt'

### OCS configuration ###
OCS_JSON_KEY = 'NAME'
OCS_HOST = (cfg.ocs_cred['host'])
OCS_USER = (cfg.ocs_cred['user'])
OCS_PASSWORD = (cfg.ocs_cred['passwd'])
URL_ListID = OCS_HOST + '/ocsapi/v1/computers/listID'
URL_Computer = OCS_HOST + '/ocsapi/v1/computer/'

### Google configuration ###
GoogleDOC_name = (cfg.google_conf['GoogleDOC_name'])
scope = (cfg.google_conf['scope'])
GSCN = (cfg.google_conf['GSCN'])
GoogleAPI_cred = (cfg.google_conf['GoogleAPI_cred'])
try:
    creds = ServiceAccountCredentials.from_json_keyfile_name(GoogleAPI_cred, scope)
except FileNotFoundError:
    print('File ' + GoogleAPI_cred + ' doesn`t exists.' )
    exit()
except NotImplementedError:
    print('No key in PEM format was detected in file ' + GoogleAPI_cred )
    exit()
client = gspread.authorize(creds)

urllib3.disable_warnings()

if os.path.exists(CSV_output):
  os.remove(CSV_output)
if os.path.exists(TXT_output):
  os.remove(TXT_output)

def whitelist_func():
    
    try:
        sheet = client.open(GoogleDOC_name).sheet1
    except:
        print('Name of the spreadsheet ' + GoogleDOC_name + ' is incorrect.')
        exit()
    whitelist = sheet.get_all_records()

    list2 = []
    list2_tmp = []
    try:
        for z in whitelist:
            var_tmp = json.dumps(z[GSCN], sort_keys=True)
            var = var_tmp.replace('"','')
            if var != None:
                list2_tmp.append(var)
    except KeyError:
        print('Column name is not the same in ' + GoogleDOC_name + ' and GSCN variable defined in ocscred_config.py file')
        exit()
    list2 = [item.lower() for item in list2_tmp]
    list2.sort()
    return list2

def get_ListID_json():
    r=requests.get(url = URL_ListID, auth=(OCS_USER, OCS_PASSWORD), verify=False)
    Data_ListID = r.json()
    Data_ListID_json = json.loads(Data_ListID)
    return Data_ListID_json

def get_computer_software_list(x):
    Data_ComputerID_json = get_computer_json(x)
    Software_name = Data_ComputerID_json[str(id)]['softwares']
    list1 = []
    list1_tmp= []
    for y in Software_name:
        var = (y[OCS_JSON_KEY])
        if var != None:
            list1_tmp.append(var)
    list1 = [item.lower() for item in list1_tmp]
    list1.sort()
    return list1

def get_computer_json(x):
    URL_ComputerID= URL_Computer + str(id)
    s=requests.get(url = URL_ComputerID, auth=(OCS_USER, OCS_PASSWORD), verify=False)
    Data_ComputerID = s.json()
    Data_ComputerID_json = json.loads(Data_ComputerID)
    return Data_ComputerID_json

def get_tag(x):
    Data_ComputerID_json = get_computer_json(x)
    accountinfo_json=Data_ComputerID_json[str(id)]['accountinfo']
    for tg in accountinfo_json:
        TAG_VAR=(tg['TAG'])
        print("### " + TAG_VAR + " ###", file=open(TXT_output,"a"))
        print("\n", file=open(TXT_output,"a"))
    return TAG_VAR

def generate_txt(lista_gotowa):
    for soft in lista_gotowa:
        print(soft, file=open(TXT_output,"a"))
    print("======================================\n", file=open(TXT_output,"a"))

def generate_csv(lista_gotowa):
    with open(CSV_output, 'a') as f:
        f.write(TAG_VAR+',')
    with open(CSV_output, 'a') as f:
        f.write(str(lista_gotowa))
    with open(CSV_output, 'a') as f:
        f.write("\n")

def check_url(x):
    try:
        if urllib.request.urlopen(x).getcode() == 200:
            print('Adres ' + x + ' jest prawidowy')
    except urllib.error.URLError: 
        print('Requested URL ' + x + ' cannot be found')
        exit()

check_url(scope)
check_url(OCS_HOST)

item_count = len(get_ListID_json())
count = 0
print("Liczba stacji roboczych w OCS: " + str(item_count))
list2 = whitelist_func()

for x in get_ListID_json():
    count = (count + 1)
    percent = (count * 100 // item_count)
    print('Postep wykonania skryptu: ' + str(percent) + '%')
    id=(x['ID'])
    TAG_VAR = get_tag(x)
    print('Aktualnie przetwarzam stacje robocza: ' + TAG_VAR)
    list1 = get_computer_software_list(x)
    lista_gotowa = list(set(list1) - set(list2))
    generate_csv(lista_gotowa)
    generate_txt(lista_gotowa)