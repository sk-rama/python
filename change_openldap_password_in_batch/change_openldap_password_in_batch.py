#! /usr/bin/env python3

# must run apt-get install python3-ldap3 command on debian system

import ldap3
import hashlib
import string
import random
import base64
import pprint

LDAP_ADMIN = 'cn=admin,dc=secar,dc=boh'
LDAP_PASSW = 'password'
LDAP_SERVER = '192.168.0.207'
LDAP_PORT = 389
LDAP_SEARCH_BASE = 'ou=mailaccounts,dc=secar,dc=boh'
LDAP_SEARCH_SCOPE = 'SUBTREE'
#LDAP_SEARCH_FILTER = '(mailForwardingAddress=*@secar2.cz)'
LDAP_SEARCH_FILTER = '(mail=rama-sms@secar.cz)'

# For what DN not change ldap password
WHITELIST_DN = [
                'uid=tiskarna-pardubice,ou=mailaccounts,dc=secar,dc=boh', 
                'external-suppliers,ou=mailaccounts,dc=secar,dc=boh', 
                'uid=icinga-imap-lan,ou=mailaccounts,dc=secar,dc=boh',
                'uid=tankovaci_karty,ou=mailaccounts,dc=secar,dc=boh',
                'uid=spravce,ou=mailaccounts,dc=secar,dc=boh',
                'uid=systems,ou=mailaccounts,dc=secar,dc=boh'
               ]


HASH_FUNCTION = ldap3.HASHED_MD5

'''
Algorithms names are defined in the ldap3 module. You can choose between:

    HASHED_NONE (no hashing is performed, password is sent in plain text)
    HASHED_MD5
    HASHED_SHA
    HASHED_SHA256
    HASHED_SHA384
    HASHED_SHA512
    HASHED_SALTED_MD5
    HASHED_SALTED_SHA
    HASHED_SALTED_SHA256
    HASHED_SALTED_SHA384
    HASHED_SALTED_SHA512
'''



def openldap_md5_hash(text: str):
    hash = hashlib.md5(text.encode('utf-8')).digest()
    encodedBytes = base64.b64encode(hash)
    encodedStr = ''.join(['{MD5}', str(encodedBytes, "utf-8")])
    encodedBytes = base64.b64encode(encodedStr.encode("utf-8"))
    return str(encodedBytes, "utf-8")


def create_random_string(string_lenght):
    chars = string.punctuation + string.ascii_letters + string.digits
    return ''.join(random.SystemRandom().choice(chars) for _ in range(string_lenght))


def ldap_connection(f):
    """
    Supply the decorated function with a ldap database connection.
    """

    def with_connection_(*args, **kwargs):
        ldap3.set_config_parameter('DEFAULT_SERVER_ENCODING', 'utf-8')
        ldap3.set_config_parameter('DEFAULT_CLIENT_ENCODING', 'utf-8')
        server = ldap3.Server(host=LDAP_SERVER, port=LDAP_PORT, use_ssl=False, get_info='ALL')
        con = ldap3.Connection(server, user=LDAP_ADMIN, password=LDAP_PASSW, auto_bind=True, client_strategy='SYNC', collect_usage=True)

        try:
            rv = f(con, *args, **kwargs)
        except Exception:
            raise
        finally:
            con.unbind()
    
        print(con.usage)
        return rv

    return with_connection_


def ldap_search(ldap_conn):
    entry_list = ldap_conn.extend.standard.paged_search(
        search_base   = LDAP_SEARCH_BASE,
        search_filter = LDAP_SEARCH_FILTER,
        search_scope  = LDAP_SEARCH_SCOPE,
        attributes    = [ldap3.ALL_ATTRIBUTES],
        generator     = False
    )
    dn_list = [entry['dn'] for entry in entry_list]
    # remove items from WHITELIST_DN 
    for item in dn_list:
        if item in WHITELIST_DN:
            dn_list.remove(item)
    return dn_list, entry_list


def ldap_modify_dn(ldap_conn, dn, modify_dict):
    '''
    # e.g. ldap_conn.modify('cn=user1,ou=users,o=company', {'givenName': [ldap3.(MODIFY_REPLACE, ['givenname-1-replaced'])],
                                                            'sn': [(ldap3.MODIFY_REPLACE, ['sn-replaced'])] 
                                                           }
           )
    '''
    print(f'Modify dn: {dn}')
    pprint.pprint(modify_dict, stream=None, indent=4, width=180, depth=None)
    print('\n')
    ldap_conn.modify(dn, modify_dict)


def change_password(ldap_conn, dn):
    rand_string  = create_random_string(128)
    new_password = ldap3.utils.hashed.hashed(HASH_FUNCTION, rand_string)
    print(f'Change password for user: {dn}')
    print(f'New password is:          {rand_string}\n')
    ldap_conn.modify(dn, {'userPassword': [(ldap3.MODIFY_REPLACE, [new_password])]}) 


@ldap_connection
def change_password_in_bach(ldap_conn):
    dn_list, entry_list = ldap_search(ldap_conn)
    if dn_list:    # check if list is not empty
        for dn in dn_list:
            change_password(ldap_conn, dn)
    else:
        print('dn list is empty')


if __name__ == "__main__":
    change_password_in_bach()
