#!/usr/bin/env python3

import os
import re
import json
import pathlib
import shutil
import traceback
import collections
import copy
import base64
from tqdm import tqdm

from dateutil import parser
import datetime

'''
message_id = {
    queue_id : {
        'client' : client,
        'daemon' : daemon,
        'sasl_m' : sasl_m'
        'sasl_u' : sasl_u,
        'from'   : mail_from,
        'size'   : size,
        'nrcpt'  : nrcpt,
        'xdata'  : {
            'number'   : {
                mail_to1 : {
                'daemon'         : daemon,
                'removed'        : 0/1,
                'orig_to'        : orig_to,
                'relay'          : relay,
                'delay'          : delay,
                'delays'         : delays,
                'dsn'            : dsn,:w
                'status'         : status,
                'deferred'       : 0/1,
                'deferred_count' : int
                }
            }
        }
    }
}
'''

queue_to_message_map = {}
message_id           = {}
        

postfix_log       = '/var/log/mail/fw2.log'
position_queue_id = 5                           # index as list - started from zero 
temp_dir          = '/tmp/abrakadabraka'

postfix_status = ['sent', 'deferred', 'bounced', 'expired']

ignored_recipients      = ['lapac@secar.cz', 'lapac-spamov@secar.cz', 'icinga@secar.cz']
ignored_relays          = ['192.168.0.207[192.168.0.207]:2600']

ok_relay_daemons        = ['postfix/smtp']

number_lines_all            = 0
number_lines_processed      = 0
number_lines_unprocessed    = 0
number_lines_with_exception = 0


bounced_emails_counter       = collections.Counter()
bounced_statistic_01_counter = {}
bounced_statistic_02_counter = {}

clients_to_recipients_counter       = {}
sasl_usernames_to_recipents_counter = {}

set_ok_recipients = set()

# counter for postfix clients who connect to postfix
most_active_postfix_clients = collections.Counter()
# counter for postfix clients who connect to postfix times number of recipients in one connect
most_active_postfix_clients_nrctp = collections.Counter()




def to_lowercase(my_string):
    try:
        return my_string.lower()
    except:
        print("uncaught exception: %s", traceback.format_exc())
        return False

def time_in_range(start: str, end: str, x: str):
    """Return true if x is in the range [start, end]"""
    start = parser.parse(start)
    end = parser.parse(end)
    x = parser.parse(x)
    if start <= end:
        return start <= x <= end
    else:
        return start <= x or x <= end

def base64_code(text: str) -> str:
    encodedBytes = base64.urlsafe_b64encode(text.encode("utf-8"))
    encodedStr = str(encodedBytes, "utf-8")
    return encodedStr

def base64_decode(encodedStr: str) -> str:
    decodedBytes = base64.urlsafe_b64decode(encodedStr)
    decodedStr = str(decodedBytes, "utf-8")
    return decodedStr

def is_it_queue_id(list, id_position):
    try:
        reg = re.compile('^[a-z0-9A-Z:]{15,17}$')
        id    = str(list[id_position])
        if (len(id) == 16 or len(id) == 17) and bool(reg.match(id)) and id[len(id) - 1] == ':' :
            return id[0:15]
        else:
            return False    
    except:
        return False

def return_queue_id(string):
  # remove last char ":" like 46pFfQ2frdz6tmD:
  return str(string).rstrip(':')

def return_message_id(item):
  # remove firtst 12 chars from string 'message-id=<9e5ae765acae8acd019aa360433351f1@secar.cz>' and last char ">"
  return item[12:len(item) - 1]



def create_directory(directory):
    path = pathlib.Path(directory)
    if path.is_dir():
        pass
    else:
        path.mkdir(parents=True, exist_ok=True)



def save_dict_to_file(dictionary, file):
    path = pathlib.Path(file)
    if path.parent.is_dir():
        pass
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
    f = open(file,"w+")
    f.write(str(dictionary))
    f.close



def load_dict_from_file(file):
    '''
    Load file and return saved python dictionary

    Parameters
    ----------
    file - file
        file to open

    Returns
    -------
    dictionary - dict
    '''

    try:
        f = open(file, "r+")
        return eval(f.read())
    except:
        return False



def delete_directory(dir_path):
    # Try to remove tree; if failed show an error using try...except on screen
    try:
        path = pathlib.Path(dir_path)
        if path.is_dir():
            shutil.rmtree(path)
    except OSError as e:
        print ("Error: %s - %s." % (e.filename, e.strerror))



def test_file_exist(file):
    return pathlib.Path(file).is_file()




def sort_counter_dict(counter_dict):
    '''
    This function return sorted Counter dict

    Parameters
    ----------
    counter_dict : collections.Counter()
        example:
            Counter({'key_01': 2, 'key_02': 8})

    Returns
    -------
    counter_dict : sorted collections.Counter()
        example: Counter({'key_08': 8, 'key_02': 2})
    '''
    try:
        # sort input collections.Counter() 
        my_var = collections.Counter(dict(counter_dict.most_common()))
        # clear input dict
        counter_dict.clear()
        # create new counter_dict from my_var
        for k,v in my_var.items():
            counter_dict[k] = v
        return counter_dict
    except:
        print("uncaught exception: %s", traceback.format_exc())




def sort_counter_dict_in_dict(counter_dict):
    '''
    This function return sorted dictionary

    Parameters
    ----------
    counter_dict : dict
        { key: {collections.Counter}}
            example:
                {'key_01': Counter({'inner_key_01': 2, 'inner_key_02': 1}), 'key_02': Counter({'inner_key_01': 4, 'inner_key_02': 2})}
        

    Returns
    -------
    counter_dict : sorted dict
        key      : key is based on the sum of inner Counter dict values
        value    : is original collections.Counter value for particular key
        example  : {'key_02': Counter({'inner_key_01': 4, 'inner_key_02': 2}), 'key_01': Counter({'inner_key_01': 2, 'inner_key_02': 1})}
    '''
    try:
        # sort input dict and record to new temp variable
        my_var = dict(sorted(counter_dict.items(), key=lambda x: sum(x[1].values()), reverse=True))
        # clear input dict 
        counter_dict.clear()
        # copy sorted kyes from temp dict to input dict
        for k,v in my_var.items():
            counter_dict[k] = collections.Counter(dict(v.most_common()))
        return counter_dict
    except:
        print("uncaught exception: %s", traceback.format_exc())
    


def what_is_after_mail_id(list, position):
    '''
    Retrun string based on string after queue-id in postfix log file

    Parameters
    ----------
    list : list 
        list from postfix log line
        examples: ['Oct', '9', '15:38:22', 'mailsever', 'postfix/smtpd[18579]:', '46pFfQ2frdz6tmD:', 'client=mailsever.secar.cz[192.168.0.207],', 'sasl_method=PLAIN,', 'sasl_username=manak@secar.cz']
                  ['Oct', '9', '15:38:22', 'mailsever', 'postfix/cleanup[18767]:', '46pFfQ2frdz6tmD:', 'message-id=<9e5ae765acae8acd019aa360433351f1@secar.cz>']
                  ['Oct', '9', '15:38:22', 'mailsever', 'postfix/qmgr[26649]:', '46pFfQ2frdz6tmD:', 'from=<manak@secar.cz>,', 'size=599,', 'nrcpt=7', '(queue', 'active)']
                  ['Oct', '9', '15:38:22', 'mailsever', 'postfix/pipe[16082]:', '46pFfQ2frdz6tmD:', 'to=<rama@secar.cz>,', 'relay=urob_filter,', 'delay=0.39,', 'delays=0.06/0.24/0/0.09,', 'dsn=2.0.0,', 'status=sent'] 

    position : int
        position of queue-id in list based on postfix log line 
        In list examples above is position queue id '5'                 
 
    Returns
    -------
    string
        string based on string following after queue-id in postfix log line    
    '''

    str = list[position + 1]
    if str.startswith('to=<'): return 'to'
    if str.startswith('from=<'): return 'from'
    if str.startswith('client='): return 'client'
    if str.startswith('uid=') and list[position - 1].startswith('postfix/pickup'): return 'uid'
    if str.startswith('message-id=<'): return 'message-id'
    if str.startswith('removed'): return 'removed'
    return False 




def client_to_map(list):
    '''
    This function examine only lines with 'client' string after queue-id in posftix log file
    Map a queue-id like '46pFfQ2frdz6tmD' to global dictionary 'queue_to_message_map' with client parameters like ip address and possible sasl method and username.
 
    Parameters
    ----------
    list : list
        the list from postfix log file with queue-id and client parameters (ip address and possible sasl method and username)
        example: ['Oct', '9', '15:38:22', 'mailsever', 'postfix/smtpd[18579]:', '46pFfQ2frdz6tmD:', 'client=mailsever.secar.cz[192.168.0.207],', 'sasl_method=PLAIN,', 'sasl_username=manak@secar.cz']
    
    Returns
    -------
    queue_to_message_map[queue_id] : add this value to global dictionary 'queue_to_message_map'
        example : add this value to queue_to_message_map[queue_id]
        {
            "client": "mailsever.secar.cz[192.168.0.207]",
            "daemon": "postfix/smtpd",
            "sasl_m": "PLAIN",
            "sasl_u": "manak@secar.cz"
        }
    '''

    queue_id = return_queue_id(list[position_queue_id])
    # remove firt 7 chars "client="
    client = list[position_queue_id + 1][7:]
    daemon = list[position_queue_id - 1].rstrip('][1234567890:')
    try:
        # remove firt 12 chars "sasl_method=" and last character ","
        sasl_method = list[position_queue_id + 2][12:].rstrip(',')
        # remove first 14 chars "sasl_username="
        sasl_username = list[position_queue_id + 3][14:]
        # if 'try' context is true, than after 'client' column follow 'sasl_method' and 'sasl_username' columns, so we must delete ',' - comma char in 'client' column
        client = client[0:len(client) - 1]
        queue_to_message_map[queue_id] = {'client': client, 'daemon': daemon, 'sasl_m': sasl_method, 'sasl_u': sasl_username}
        return True
    except IndexError:
        queue_to_message_map[queue_id] = {'client': client, 'daemon': daemon, 'sasl_m': '', 'sasl_u': ''}
        return True
    except:
        global number_lines_with_exception
        number_lines_with_exception += 1
        return False



def uid_to_map(list):
    '''
    This function examine only lines with 'uid' string after queue-id in posftix log file
    Map a queue-id like '46yC992mfYz6w2Y' to global dictionary 'queue_to_message_map' with client parameters like ip address and possible sasl method and username.

    Parameters
    ----------
    list : list
        the list from postfix log file with queue-id and client parameters (ip address and possible sasl method and username)
                 ['Oct', '9', '15:14:05', 'mailsever', 'postfix/pickup[14101]:', '46yC992mfYz6w2Y:', 'uid=1003', 'from=<manak@secar.cz>']
   
    Returns
    -------
    queue_to_message_map[queue_id] : add this value to global dictionary 'queue_to_message_map'
        example : add this value to queue_to_message_map[queue_id]
        {
            "client": "uid=1003",
            "daemon": "postfix/pickup",
            "sasl_m": "",
            "sasl_u": ""
        }
    '''
    queue_id = return_queue_id(list[position_queue_id])
    client = list[position_queue_id + 1]
    daemon = list[position_queue_id - 1].rstrip('][1234567890:')
    try:
        sasl_method = ''
        sasl_username = ''
        queue_to_message_map[queue_id] = {'client': client, 'daemon': daemon, 'sasl_m': sasl_method, 'sasl_u': sasl_username}
        return True
    except IndexError:
        queue_to_message_map[queue_id] = {'client': client, 'daemon': daemon, 'sasl_m': '', 'sasl_u': ''}
        return True
    except:
        global number_lines_with_exception
        number_lines_with_exception += 1
        return False



def get_massage_id_from_dict(queue_id):
    '''
    return 'message-id' value from global dictionary 'queue_to_message_map' for any postfix queue-id

    Parameters
    ----------
    queue_id : str
        key from global dictionary 'queue_to_message_map'
        example of queue_to_message_map dict:
        {
            "82pFfQ2frdz6tAb": {
                "client": "mailsever.secar.cz[192.168.0.207],",
                "daemon": "postfix/smtpd",
                "message-id": "46pGq33BSPz8wCn@mailserver1-dmz.secar.cz",
                "sasl_m": "PLAIN",
                "sasl_u": "manak@secar.cz"
            },
            "46pFfQ3slxz6tmd": {
                "client": "localhost[127.0.0.1]",
                "daemon": "postfix/smtpd",
                "message-id": "9e5ae765acae8acd019aa360433351f1@secar.cz",
                "sasl_m": "",
                "sasl_u": ""
            }
        }

    Returns
    -------
    message-id : str
        string value from queue_to_message_map[queue_id]['message-id']
        for example for queue-id '46pFfQ2frdz6tmD' return message-id '46pGq33BSPz8wCn@mailserver1-dmz.secar.cz'
    '''
    try:
        return queue_to_message_map[queue_id]['message-id']
    except:
        return False





def parse_line_with_message_id(list):
    '''
    This is function for examine only postfix log lines with 'message-id' string
    1) In first step we add to queue_to_message_map[queue_id] a "message-id" key with value message-id from postfix log line
    2) Later we save message-id data as dictionary to pathlib.Path(temp_dir, message-id)

    Parameters
    ----------
    list : list
        the list from postfix log file
        example: ['Oct', '9', '15:38:26', 'mailsever', 'postfix/cleanup[18805]:', '46pFfV5Wtzz6tlv:', 'message-id=<9e5ae765acae8acd019aa360433351f1@secar.cz>']

    Returns
    -------
    queue_to_message_map : global dictionary 
    {
        "46pFfQ2frdz6tmD": {
                "client": "mailsever.secar.cz[192.168.0.207],",
                "daemon": "postfix/smtpd",
                "message-id": "9e5ae765acae8acd019aa360433351f1@secar.cz",
                "sasl_m": "PLAIN",
                "sasl_u": "manak@secar.cz"
        },
        "46pFfQ3slxz6tmd": {
                "client": "localhost[127.0.0.1]",
                "daemon": "postfix/smtpd",
                "message-id": "9e5ae765acae8acd019aa360433351f1@secar.cz",
                "sasl_m": "",
                "sasl_u": ""
        }
    }
            
    file : save_dict_to_file(temp_dict, pathlib.Path(temp_dir, msg_id))
    '''
    
    try:
        # 1) First step
        # retrieve message-id 
        msg_id = return_message_id(list[position_queue_id + 1])
        # retrieve queue id
        queue_id = return_queue_id(list[position_queue_id])
        # map queue id to message-id in queue_to_message_map dictionary
        queue_to_message_map[queue_id] = {**queue_to_message_map[queue_id], **{'message-id': msg_id}}
        
        # 2) Second step
        # create temporary dictonary with queue id data from queue_to_message_map dictionary 
        temp_dict = {**queue_to_message_map[queue_id]}
        # delete 'message-id' key from temp_dict
        del temp_dict['message-id']
        # save file name with message-id to variable file
        file = pathlib.Path(temp_dir, base64_code(msg_id))
        # test a variable file exist
        if test_file_exist(file):
            loaded_dict = load_dict_from_file(file)
            loaded_dict[msg_id][queue_id] = temp_dict
            save_dict_to_file(loaded_dict, file)
        else:
            loaded_dict = {}
            loaded_dict.setdefault(msg_id, {})[queue_id] = temp_dict
            save_dict_to_file(loaded_dict, file)
    except:
        global number_lines_with_exception
        number_lines_with_exception += 1
        #print(f"Posftix log file for 'message-id' item: For queue_id: {queue_id} I can not find particular message-id")
        #print("uncaught exception: %s", traceback.format_exc())
        return False



def parse_line_with_from(list):
    '''
    Parameters
    ----------
    list : list
        the list based on line from postfix log file with 'from=<manak@secar.cz>,' record
        example: ['Oct', '9', '15:38:22', 'mailsever', 'postfix/qmgr[26649]:', '46pFfQ2frdz6tmD:', 'from=<manak@secar.cz>,', 'size=599,', 'nrcpt=7', '(queue', 'active']

    Returns
    -------
    message_id[msg_id][queue_id] = {**message_id[msg_id][queue_id], **{'from': msg_from, 'size': msg_size, 'nrcpt': msg_nrcpt}}
        Add 'from', 'msg_size' and 'nrcpt' keys to 'message_id'[msg_id][queue_id] global dictionary
    '''
    try:
        # examine queue-id from postfix log line
        queue_id = return_queue_id(list[position_queue_id])
        # return message-id for particular queue-id
        msg_id   = get_massage_id_from_dict(queue_id)
        # return mail from postfix log line
        msg_from = list[position_queue_id + 1]
        # code msg_id to base64 urlsafe
        file = base64_code(msg_id)
        # remove first 6 chars from string like 'from=<manak@secar.cz>,' and 2 last chars '>,'
        msg_from = msg_from[6:len(msg_from) - 2] 
        if not list[position_queue_id + 2].startswith('status=expired'):
            # return message size from postfix log line
            msg_size = list[position_queue_id + 2]
            # remove first 5 chars from string like 'size=599,' and 1 last chars ',' 
            msg_size = int(msg_size[5:len(msg_size) - 1])
            # return number of recipients
            msg_nrcpt = list[position_queue_id + 3]
            # remove first 6 chars from string like 'nrcpt=7' and convert it to int
            msg_nrcpt = int(msg_nrcpt[6:])
            # load particular file with name as msg_id
            loaded_dict = load_dict_from_file(pathlib.Path(temp_dir, file))
            # add dict {'from': msg_from, 'size': msg_size, 'nrcpt': msg_nrcpt} to
            loaded_dict[msg_id][queue_id] = { **loaded_dict[msg_id][queue_id], **{'from': to_lowercase(msg_from), 'size': msg_size, 'nrcpt': msg_nrcpt}}  
            # save temp_dict to file with name as msg_id
            save_dict_to_file(loaded_dict, pathlib.Path(temp_dir, file))
        else:
            pass
    except:
        global number_lines_with_exception
        number_lines_with_exception += 1
        #print(f"Posftix log file for 'from' item: For queue_id: {queue_id} I can not find particular message-id")
        return False



def parse_line_with_to(list):
    try:
        # examine queue-id from postfix log line
        queue_id = return_queue_id(list[position_queue_id])
        # return message-id for particular queue-id
        msg_id   = get_massage_id_from_dict(queue_id)
        # return mail from postfix log line
        msg_to = list[position_queue_id + 1]
        # remove first 4 chars from string like 'to=<rama@secar.cz>,' and 2 last chars '>,'
        msg_to = to_lowercase(msg_to[4:len(msg_to) - 2])
        # save a daemon string
        msg_daemon = list[position_queue_id - 1].rstrip('][1234567890:')
        # code msg_id to base64 urlsafe
        file = base64_code(msg_id)
        # we can try load file with particular message-id
        if test_file_exist(pathlib.Path(temp_dir, file)):
            loaded_dict = load_dict_from_file(pathlib.Path(temp_dir, file))
        # we create a temporary dictionary
        temp_dict = {'daemon': msg_daemon, 'relay': '', 'orig_to': '', 'relay': '', 'delay': '', 'delays': '', 'dsn': '', 'deferred': 0, 'deferred_count': 0, 'status': '', 'xmessage': ''}
        for counter, item in enumerate(list[(position_queue_id + 2):], start = position_queue_id + 2): 
            if '=' in item:
                temp_list = item.split('=', maxsplit=1)
                if temp_list[0] == 'orig_to':
                    temp_dict['orig_to'] = temp_list[1][1:len(temp_list[1]) - 2]
                if temp_list[0] == 'relay':
                    temp_dict['relay'] = temp_list[1][0:len(temp_list[1]) - 1] 
                if temp_list[0] == 'delay':
                    temp_dict['delay'] = temp_list[1][0:len(temp_list[1]) - 1]
                if temp_list[0] == 'delays':
                    temp_dict['delays'] = temp_list[1][0:len(temp_list[1]) - 1]
                if temp_list[0] == 'dsn': 
                    temp_dict['dsn'] = temp_list[1][0:len(temp_list[1]) - 1]
                if temp_list[0] == 'status':
                    temp_dict['status'] = temp_list[1]
                    #temp_dict['xmessage'] = ' '.join(list[counter + 1:])
                    if temp_list[1] == 'deferred':
                        temp_dict['deferred'] = 1
                        temp_dict['deferred_count'] = 1
                        #try:
                        #    temp_dict['deferred_count'] = loaded_dict[msg_id][queue_id]['xdata'][number][msg_to]['deferred_count'] + 1
                        #except KeyError:
                        #    temp_dict['deferred_count'] = 1
                        #except:
                        #    temp_dict['deferred_count'] = False
        # we can try examine if 'xdata' exist in loaded_dict[msg_id][queue_id]
        if 'xdata' in loaded_dict[msg_id][queue_id]:
            for item in loaded_dict[msg_id][queue_id]['xdata']:
                if msg_to in loaded_dict[msg_id][queue_id]['xdata'][item] and loaded_dict[msg_id][queue_id]['xdata'][item][msg_to]['orig_to'] == temp_dict['orig_to']:
                    number = item
                    if temp_dict['deferred'] == 1:
                        temp_dict['deferred_count'] = loaded_dict[msg_id][queue_id]['xdata'][item][msg_to]['deferred_count'] + 1
                    break
                else:
                    # we cannot find particular number-id and create new
                    number = str(len(loaded_dict[msg_id][queue_id]['xdata']) + 1)
        else:
            number = '1'
        loaded_dict[msg_id].setdefault(queue_id, {}).setdefault('xdata', {}).setdefault(number, {})[msg_to] = {**temp_dict}
        save_dict_to_file(loaded_dict, pathlib.Path(temp_dir, file))
    except:
        global number_lines_with_exception
        number_lines_with_exception += 1
        #print(f"Posftix log file for 'to' item: For queue_id: {queue_id} I can not find particular message-id")
        #print("uncaught exception: %s", traceback.format_exc())
        return False

def parse_line_with_remove(list):
    '''
    This is function remove particular queue-id from global dictionary 'queue_to_message_map'

    Parameters
    ----------
    list : list
        the list from postfix log file
        example: Oct  9 15:38:20 mailsever postfix/qmgr[26649]: 46pFfN2Tfjz6tmD: removed

    Returns
    -------
    True : bool
        We return True if remove queue-id form 'queue_to_message_map' global dictionary was successfull
    False : bool
        Another we return False
    '''
    try:
        # examine queue-id from postfix log line
        queue_id = return_queue_id(list[position_queue_id])
        del queue_to_message_map[queue_id]
        return True
    except IndexError:
        return False
    except:
        global number_lines_with_exception
        number_lines_with_exception += 1
        return False



def most_active_posftix_clients(file_dict, counter_dict):
    '''
    This function take a dict and update global collections.Counter counter_dict
    We count the postfix 'clients' that connect to postfix and try send emails

    Parameters
    ----------
    file_dict : dictionary
        It is dictionary loaded from file
    counter_dict : collections.Counter
        It is global variable from collections.Counter where we update a counters from 'file_dict' 

    Returns
    -------
    counter_dict : collections.Counter
        key     : the key is a client name
        value   : is the number of 'clients' that connect to postfix and try send emails
        example : Counter({'unknown[192.168.221.124]': 20030, 'unknown[192.168.221.126]': 14276, 'unknown[192.168.221.239]': 2761}) 
    '''
    try:
        # get a 'message_id' fr0m 'file_dict' - it is first key in dictionary  
        message_id = list(file_dict.keys())[0]
        # get a first queue_id from the 'message-id'
        first_queue_id = list(file_dict[message_id].keys())[0]
        # get a 'client' value from first queue_id in the 'message_id'
        client = file_dict[message_id][first_queue_id]['client']
        # update global collections.Counter with 'client' value and counter 1
        counter_dict.update({client: 1})
    except:
        #print(file_dict)
        #print("uncaught exception: %s", traceback.format_exc())
        return False




def most_active_posftix_clients_with_number_emails(file_dict, counter_dict):
    '''
    This function take a dict and update global collections.Counter counter_dict
    We count the postfix 'clients' that connect to postfix and try send emails (one client can send N emails in one connect session)

    Parameters
    ----------
    file_dict : dictionary
        It is dictionary loaded from file
    counter_dict : collections.Counter
        It is global variable from collections.Counter where we update a counters from 'file_dict'

    Returns
    -------
    counter_dict : collections.Counter
        key     : the key is a client name
        value   : is the number of all emails that client (in the key) attempts to send
        example : Counter({'unknown[192.168.221.124]': 20408, 'unknown[192.168.221.126]': 14499, 'unknown[192.168.221.239]': 2761})
    '''
    try:
        # get a 'message_id' fr0m 'file_dict' - it is first key in dictionary
        msg_id = list(file_dict.keys())[0]
        # get a first queue_id from the 'msg-id'
        first_queue_id = list(file_dict[msg_id].keys())[0]
        # get a 'client' value from first queue_id in the 'msg_id'
        client = file_dict[msg_id][first_queue_id]['client']
        # get 'client' emails count in one session
        nrcpt = int(file_dict[msg_id][first_queue_id]['nrcpt'])
        # update global collections.Counter with 'client' value and number of emails
        counter_dict.update({client: nrcpt})
    except:
        #print("uncaught exception: %s", traceback.format_exc())
        return False



def statistic_clients_to_recipients(file_dict, counter_dict):
    '''
    This function returns dictionary mappings between postfix clients and email recipients like:
    {'client_01': Counter({'recipient_email_01': int, 'recipient_email_02': int, ..., 'client_02': Counter({'recipient_email_01': int, 'recipient_email_02': int,...})}

    Parameters
    ----------
    file_dict : dictionary
        It is dictionary loaded from file
    counter_dict : dict
        { key: {collections.Counter}}
        It is global variable where we update a counters from 'file_dict'

    Returns
    -------
    counter_dict : collections.Counter
        key     : key is a postfix client (mostly ip address) 
        value   : is counter from collections.Counter where key is postfix client and value is counter for recipients emails 
        example : {
                  'unknown[192.168.0.1]': Counter({'krofta@secar2.cz': 1, 'cikhart@secar2.cz': 1, 'ruzicka@secar.cz': 1, 'sherlog@secar2.cz': 1}), 
                  'mailsever.secar.cz[192.168.0.207]': Counter({'rama@secar.cz': 3, 'rama@secar2.cz': 3}),
                  'uid=1003': Counter({'chalupa@secar2.cz': 1})
                  }
    '''
    try:
        # get a 'message_id' fr0m 'file_dict' - it is first key in dictionary
        msg_id = list(file_dict.keys())[0]
        # get a first queue_id from the 'message-id'
        first_queue_id = list(file_dict[msg_id].keys())[0]
        # get a 'client' value from first queue_id in the 'message_id'
        client = file_dict[msg_id][first_queue_id]['client']
        if 'xdata' in file_dict[msg_id][first_queue_id]:
            # search across all serial numbers
            for number in file_dict[msg_id][first_queue_id]['xdata']:
                msg_to = list(file_dict[msg_id][first_queue_id]['xdata'][number].keys())[0]
                if not msg_to in ignored_recipients:
                    counter_dict.setdefault(client, collections.Counter()).update({msg_to: 1})
    # If we want return a sorted dict based on number of recipeints count:
    # counter_dict = dict(sorted(counter_dict.items(), key=lambda x: sum(x[1].values()), reverse=True))
    # if we want return also counter like: Counter({('mailsever.secar.cz[192.168.0.207]', 6): 1, ('unknown[192.168.0.1]', 4): 1, ('uid=1003', 1): 1})
    # collections.Counter(sorted({key: sum(value.values()) for key, value in counter_dict.items()}.items(), key=lambda x: x[1], reverse=True))
    except:
        #print(file_dict)
        #print("uncaught exception: %s", traceback.format_exc())
        return False



def statistic_sasl_usernames_to_recipients(file_dict, counter_dict):
    '''
    This function returns dictionary mappings between postfix clients and email recipients like:
    {'sasl_username_01': Counter({'recipient_email_01': int, 'recipient_email_02': int, ..., 'sasl_username_02': Counter({'recipient_email_01': int, 'recipient_email_02': int,...})}

    Parameters
    ----------
    file_dict : dictionary
        It is dictionary loaded from file
    counter_dict : dict
        { key: {collections.Counter}}
        It is global variable where we update a counters from 'file_dict'

    Returns
    -------
    counter_dict : collections.Counter
        key     : key is a postfix client (mostly ip address)
        value   : is counter from collections.Counter where key is postfix client and value is counter for recipients emails
        example : {
                  'unknown[192.168.0.1]': Counter({'krofta@secar2.cz': 1, 'cikhart@secar2.cz': 1, 'ruzicka@secar.cz': 1, 'sherlog@secar2.cz': 1}),
                  'mailsever.secar.cz[192.168.0.207]': Counter({'rama@secar.cz': 3, 'rama@secar2.cz': 3}),
                  'uid=1003': Counter({'chalupa@secar2.cz': 1})
                  }
    '''
    # get a 'message_id' fr0m 'file_dict' - it is first key in dictionary
    msg_id = list(file_dict.keys())[0]
    # get a first queue_id from the 'message-id'
    first_queue_id = list(file_dict[msg_id].keys())[0]
    # test a 'file_dict' has non empty 'sasl_u' key
    if file_dict[msg_id][first_queue_id]['sasl_u'] == "":
        pass
    else:
        if 'xdata' in file_dict[msg_id][first_queue_id]:
            # search across all serial numbers
            for number in file_dict[msg_id][first_queue_id]['xdata']:
                # we record a recipient
                msg_to = list(file_dict[msg_id][first_queue_id]['xdata'][number].keys())[0]
                # we record a sasl_username
                sasl_username = file_dict[msg_id][first_queue_id]['sasl_u']
                # test a recipient is not in global ignored recipient list
                if not msg_to in ignored_recipients:
                    counter_dict.setdefault(sasl_username, collections.Counter()).update({msg_to: 1})




def count_bounced_emails(file_dict, counter_dict):
    '''
    This function counts all bounced emails

    Parameters
    ----------
    file_dict : dictionary
        It is dictionary loaded from file
    counter_dict : collections.Counter
        It is global variable from collections.Counter where we update a counters from 'file_dict'

    Returns
    -------
    counter_dict : collections.Counter
        key     : key is a email address that is bounced by postfix
        value   : is number how many was the email address (key) bounced
        example : Counter({'admin@movistar.com': 584, 'giancapellaro@pacificoasiste.com.pe': 378, 'operalta@pacificoasiste.com.pe': 378, 'michal.krp@pabk.sk': 177})
    '''
    try:
        # get a 'message_id' fr0m 'file_dict' - it is first key in dictionary
        msg_id = list(file_dict.keys())[0]
        # search for email status across all queue_id's
        for queue_id in file_dict[msg_id]:
            if 'xdata' in file_dict[msg_id][queue_id]:
                # search across all serial numbers
                for number in file_dict[msg_id][queue_id]['xdata']:
                    # search across all msg_to for particular queue_id
                    for msg_to in file_dict[msg_id][queue_id]['xdata'][str(number)]:
                        # test a queue_id with particular email address (mail to) was bounced
                        if file_dict[msg_id][queue_id]['xdata'][str(number)][msg_to]['status'] == 'bounced':
                            # if email address is bounced, we add counter 1 to particular email address
                            counter_dict.update({msg_to: 1})
    except:
        #print(file_dict)
        #print("uncaught exception: %s", traceback.format_exc())
        return False




def bounced_statistic_01(file_dict, counter_dict):
    '''
    This function parse all files with message-id and return a dictionary with Counter dict in the form:
    {'sender_01': Counter({'bounced_email_01': int, 'bounced_email_02': int, ..., 'sender02': Counter({'bounced_email_01': int, 'bounced_email_02': int,...})}

    Parameters
    ----------
    file_dict : dictionary
        It is dictionary loaded from file
    counter_dict : dict
        { key: {collections.Counter}}
        It is global variable where we update a counters from 'file_dict'

    Returns
    -------
    counter_dict : collections.Counter
        key     : key is a sender email address 
        value   : is counter from collections.Counter where key is bounced email address and value is number of bounced for this key 
        example : {
                  'hd@secar.cz': Counter({'kj@secar.cz': 16, 'info@securit.cez': 16}), 
                  'localiza@sherlogtrace.cz': Counter({'giancapellaro@pacificoasiste.com.pe': 378, 'operalta@pacificoasiste.com.pe': 378}),
                  'celartrace@gsc.com': Counter({'miguel.castro@kikes.com.co': 7}) 
                  }
    '''
    try:
        # get a 'message_id' fr0m 'file_dict' - it is first key in dictionary
        msg_id = list(file_dict.keys())[0]
        # search for email status across all queue_id's
        for queue_id in file_dict[msg_id]:
            if 'xdata' in file_dict[msg_id][queue_id]:
                # search across all serial numbers
                for number in file_dict[msg_id][queue_id]['xdata']:
                    # search across all msg_to for particular queue_id
                    for msg_to in file_dict[msg_id][queue_id]['xdata'][str(number)]:
                        if file_dict[msg_id][queue_id]['xdata'][str(number)][msg_to]['status'] == 'bounced':
                            mail_from =  file_dict[msg_id][queue_id]['from']
                            counter_dict.setdefault(mail_from, collections.Counter()).update({msg_to: 1})
    except:
        #print(file_dict)
        #print("uncaught exception: %s", traceback.format_exc())
        return False



def bounced_statistic_02(file_dict, counter_dict):
    '''
    This function parse all files with message-id and return a dictionary with Counter dict in the form:
    {'bounced_email_01': Counter({'sender_01': int, 'sender_02': int, ..., 'bounced_email_02': Counter({'sender_01': int, 'sender_02': int,...})}

    Parameters
    ----------
    file_dict : dictionary
        It is dictionary loaded from file
    counter_dict : dict
        { key: {collections.Counter}}
        It is global variable where we update a counters from 'file_dict'

    Returns
    -------
    counter_dict : dict({key: collections.Counter})
        key     : key is a bounced email address
        value   : is counter from collections.Counter where key is sender email address and value is number of sending emails for this key
        example : {
                  'kj@secar.cz': Counter({'hd@secar.cz': 16}), 
                  'giancapellaro@pacificoasiste.com.pe': Counter({'localiza@sherlogtrace.cz': 378}), 
                  'ondrej.lesniak@forch.sk': Counter({'sherlogtrace@sherlogtrace.cz': 1})
                  }
    '''
    try:
        # get a 'message_id' fr0m 'file_dict' - it is first key in dictionary
        msg_id = list(file_dict.keys())[0]
        # search for email status across all queue_id's
        for queue_id in file_dict[msg_id]:
            if 'xdata' in file_dict[msg_id][queue_id]:
                # search across all serial numbers
                for number in file_dict[msg_id][queue_id]['xdata']:
                    # search across all msg_to for particular queue_id
                    for msg_to in file_dict[msg_id][queue_id]['xdata'][str(number)]:
                        if file_dict[msg_id][queue_id]['xdata'][str(number)][msg_to]['status'] == 'bounced':
                            mail_to =  list(file_dict[msg_id][queue_id]['xdata'][str(number)].keys())[0]
                            mail_from = file_dict[msg_id][queue_id]['from']
                            counter_dict.setdefault(mail_to, collections.Counter()).update({mail_from: 1})
    except:
        #print(file_dict)
        #print("uncaught exception: %s", traceback.format_exc())
        return False




def return_ok_recipients(file_dict, var_set):
    '''
    This function return python set with emails that was successfull send to recipient

    Parameters
    ----------
    file_dict : dictionary
        It is dictionary loaded from file
    var_set : set
        It is global variable where we add unique emails

    Returns
    -------
    var_set : set
        It is global variable where we add unique emails
    '''
    try:
        # get a 'message_id' fr0m 'file_dict' - it is first key in dictionary
        msg_id = list(file_dict.keys())[0]
        # search across all queue_id's
        for queue_id in file_dict[msg_id]:
            if 'xdata' in file_dict[msg_id][queue_id]:
                # search across all serial numbers
                for number in file_dict[msg_id][queue_id]['xdata']:
                    # search across all msg_to for particular queue_id
                    for msg_to in file_dict[msg_id][queue_id]['xdata'][str(number)]:
                        if file_dict[msg_id][queue_id]['xdata'][str(number)][msg_to]['relay'] not in ignored_relays:
                            if file_dict[msg_id][queue_id]['xdata'][str(number)][msg_to]['daemon'] in ok_relay_daemons:
                                if file_dict[msg_id][queue_id]['xdata'][str(number)][msg_to]['status'] == 'sent':
                                    mail_to =  list(file_dict[msg_id][queue_id]['xdata'][str(number)].keys())[0]
                                    var_set.add(mail_to) 
    except:
        #print(file_dict)
        #print("uncaught exception: %s", traceback.format_exc())
        return False

    
    



def parse_log_file():
  delete_directory(temp_dir)
  create_directory(temp_dir)
  tqdm_num_lines = tqdm(total = sum(1 for line in open(postfix_log)))
  with open(postfix_log) as file:
    for line in file:
      tqdm_num_lines.update(1)
      global number_lines_all
      number_lines_all += 1
      #print(f"spracovavam riadok:\n {line}")
      fields = line.strip().split()
      mail_id = is_it_queue_id(fields, position_queue_id)
      try:
        if mail_id:
          if what_is_after_mail_id(fields, position_queue_id) == 'client':
            client_to_map(fields)
          if what_is_after_mail_id(fields, position_queue_id) == 'uid':
            uid_to_map(fields)
          if what_is_after_mail_id(fields, position_queue_id) == 'message-id':
            parse_line_with_message_id(fields)
          if what_is_after_mail_id(fields, position_queue_id) == 'from':
            parse_line_with_from(fields)
          if what_is_after_mail_id(fields, position_queue_id) == 'to':
            parse_line_with_to(fields)
          global number_lines_processed
          number_lines_processed += 1 
        else:
          global number_lines_unprocessed
          number_lines_unprocessed += 1
      except:
        global number_lines_with_exception
        number_lines_with_exception += 1
    tqdm_num_lines.close()
  print(f"number of all lines in {postfix_log} is: {number_lines_all}")
  print(f"number of prcessed lines in {postfix_log} is: {number_lines_processed}")
  print(f"number of unprocessed lines in {postfix_log} is: {number_lines_unprocessed}")
  print(f"number of lines with exception is: {number_lines_with_exception}")
  #with open("msg_id.json", "w") as write_file:
  #    json.dump(message_id, write_file, indent=4, sort_keys=False)
  #with open("queue_id.json", "w") as write_file:
  #    json.dump(queue_to_message_map, write_file, indent=4, sort_keys=True)


def make_statistic():
    tqdm_number = tqdm(total = len([1 for name in os.listdir(temp_dir)]))
    print(f"I parse files in {temp_dir} and create a statistic for this file")
    for path in pathlib.Path(temp_dir).rglob("*"):
        if path.is_file():
            # print(f"I will parse file: {path}")
            loaded_dict = load_dict_from_file(path)
            # print(loaded_dict)
            most_active_posftix_clients(loaded_dict, most_active_postfix_clients)
            most_active_posftix_clients_with_number_emails(loaded_dict, most_active_postfix_clients_nrctp)
            count_bounced_emails(loaded_dict, bounced_emails_counter)
            bounced_statistic_01(loaded_dict, bounced_statistic_01_counter)
            bounced_statistic_02(loaded_dict, bounced_statistic_02_counter)
            statistic_clients_to_recipients(loaded_dict, clients_to_recipients_counter)
            statistic_sasl_usernames_to_recipients(loaded_dict, sasl_usernames_to_recipents_counter)
            return_ok_recipients(loaded_dict, set_ok_recipients)
        tqdm_number.update(1)
    tqdm_number.close()  
    #sort_counter_dict(most_active_postfix_clients_nrctp)
    #save_dict_to_file(json.dumps(most_active_postfix_clients_nrctp, indent=4, sort_keys=False), 'most_active_postfix_clients_nrctp.txt')
    print(bounced_emails_counter)
    sort_counter_dict(bounced_emails_counter)
    save_dict_to_file(json.dumps(bounced_emails_counter, indent=4, sort_keys=False), 'bounced_emails_counter.txt')
    sort_counter_dict_in_dict(bounced_statistic_01_counter)
    save_dict_to_file(json.dumps(bounced_statistic_01_counter, indent=4, sort_keys=False), 'bounced_statistic_01_counter.txt')
    sort_counter_dict_in_dict(bounced_statistic_02_counter)
    save_dict_to_file(json.dumps(bounced_statistic_02_counter, indent=4, sort_keys=False), 'bounced_statistic_02_counter.txt')
    sort_counter_dict_in_dict(clients_to_recipients_counter)
    save_dict_to_file(json.dumps(clients_to_recipients_counter, indent=4, sort_keys=False), 'clients_to_recipients_counter.txt')
    sort_counter_dict_in_dict(sasl_usernames_to_recipents_counter)
    save_dict_to_file(json.dumps(sasl_usernames_to_recipents_counter, indent=4, sort_keys=False), 'sasl_usernames_to_recipents_counter.txt')
    save_dict_to_file(json.dumps(list(set_ok_recipients), indent=4, sort_keys=False), 'set_ok_recipients.txt')
    #print(f"most active connected clients are: {most_active_postfix_clients}")
    #print("--------------------------------------------------------")
    #print(f"most active clients with number of emails that are attempt to send: {most_active_postfix_clients_nrctp}") 
    #print("--------------------------------------------------------")
    #print("--------------------------------------------------------")
    #print(f"bounced emails are: {bounced_emails_counter}")
    #print(f"number of all bounced emails is: {sum(bounced_emails_counter.values())}")
    #print(f"number of bounced emails is: {len(bounced_emails_counter)}")
    #print("--------------------------------------------------------")
    #print(f"statistic 01 for bounced emails is: {bounced_statistic_01_counter}")
    #print("--------------------------------------------------------")
    #print(f"statistic 02 for bounced emails is: {bounced_statistic_02_counter}")
    #print("--------------------------------------------------------")
    #print(f"clients to recipients mapping is: {clients_to_recipients_counter}")
    #print("--------------------------------------------------------")
    #print(f"sasl usernames to recipients mapping is: {sasl_usernames_to_recipents_counter}")


 

if __name__ == "__main__":
    parse_log_file()
    make_statistic()     
    
