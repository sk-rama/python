#!/usr/bin/env python3

import zeep
import json
from datetime import datetime
import pathlib

#--- WSDL Parameters ---#
#my_json = { "&seznam_vsech_bounced_emailu": ["fm@secar.czc", "jefe.transportes@alimentoscielo.com", "joacod63@gimail.com"] }
# for test
wsdl_test = 'http://192.168.221.145/EmailySluzba/Emaily.svc?wsdl'
client_test = zeep.Client(wsdl=wsdl_test)
# for EU
wsdl_eu = 'http://192.168.221.124/EmailySluzba/Emaily.svc?wsdl'
client_eu = zeep.Client(wsdl=wsdl_eu)
# for LATAM
wsdl_latam = 'http://192.168.221.126/EmailySluzba/Emaily.svc?wsdl'
client_latam = zeep.Client(wsdl=wsdl_latam)


sender_list = ['carcontrol@o2.cz', 'carcontrol@o2.sk', 'movistar@sherlogtrace.cz', 'mexico@sherlogtrace.cz', 'peru@sherlgotrace.cz', 'movistargps@sherlogtrace.cz', 'sherloggps@sherlogtrace.cz', 'traceonline@sherlogtrace.cz', 'localiza@sherlogtrace.cz', 'sherlogtrace@sherlogtrace.cz', 'testserver@sherlogtrace.cz', 'traceonline@secar.cz', 'test@secar.cz', 'vision@sherlogvision.cz', 'celartrace@gsc.com', 'test@kaktus.cz', 'test@kswr.cz', 'info@sherlog.cz']
bounced_treshold      = 4 
current_time          = datetime.utcnow().strftime('%Y-%m-%d_%H:%M:%S.%f')[:-7]
backup_dir            = '/etc/rc-local/skripty/python/mail_stat/backup/'

backup_file_wcf       = pathlib.Path(backup_dir, ".".join([datetime.utcnow().strftime('%Y-%m-%d_%H:%M:%S.%f')[:-7], 'wcf_file']))
backup_file_bounced   = pathlib.Path(backup_dir, ".".join([datetime.utcnow().strftime('%Y-%m-%d_%H:%M:%S.%f')[:-7], 'bounced_emails']))
backup_file_ok_emails = pathlib.Path(backup_dir, ".".join([datetime.utcnow().strftime('%Y-%m-%d_%H:%M:%S.%f')[:-7], 'ok_emails']))

file_with_bounced = 'bounced_statistic_01_counter.txt'
file_with_ok_recipients = 'set_ok_recipients.txt'

def function1():
    bounced_emails = [] 
    f_ok = open(file_with_ok_recipients, 'r+')
    list_ok = json.loads(f_ok.read())
    f_bounced = open(file_with_bounced, 'r+')
    dict_bounced = json.loads(f_bounced.read())
    a = dict()
    for item in sender_list: 
        if item in dict_bounced:
            a[item] = dict_bounced[item]
    if len(a) == 0:
        return bounced_emails, list_ok, a
    else:
        for m_key in a:
            for s_key in a[m_key]:
                if ( a[m_key][s_key] >= bounced_treshold and str(s_key) not in list_ok ):
                    bounced_emails.append(s_key)
        return bounced_emails, list_ok, a


def save_object(my_obj, file):
    path = pathlib.Path(file)
    if path.parent.is_dir():
        pass
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
    f = open(file,"w+")
    temp_obj = json.dumps(my_obj, indent=4, sort_keys=False)
    f.write(str(temp_obj))
    f.close
           

if __name__ == "__main__":
    wcf_list, my_ok, my_bounced = function1()
    my_json = { "&seznam_vsech_bounced_emailu": wcf_list }
    save_object(wcf_list, backup_file_wcf)
    save_object(my_ok, backup_file_ok_emails)
    save_object(my_bounced, backup_file_bounced)
    print(client_test.service.BlackListAktualizovat(heslo="emaily123", json_black_list=json.dumps(my_json, indent=1)))
    print(client_eu.service.BlackListAktualizovat(heslo="emaily123", json_black_list=json.dumps(my_json, indent=1)))
    print(client_latam.service.BlackListAktualizovat(heslo="emaily123", json_black_list=json.dumps(my_json, indent=1)))
