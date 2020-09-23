#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import socket
import time
import datetime
import calendar
import os
import os.path
import subprocess
import smtplib
import email.mime.text
import logging
import shutil


###############    Premenne, ktore musim upravit alebo skontrolovat    #########################################
mysql_user = '--user=root'
mysql_pass = '--password=20jarka14'
mysql_host = '--host=localhost'
mysql_prog = '/usr/bin/mysql'
mysql_shdb = 'show databases'
mysqldump_prog = '/usr/bin/mysqldump'
mysql_nezalohuj_dbname = []             #definuj nazvy databaz ako list-mena databaz musia byt ako string a su case sensitive, napr. mysql_nezalohuj_dbname = ["phpmyadmin", "information_schema"]

dsmc_prog = '/opt/tivoli/tsm/client/ba/bin/dsmc'
dsmc_error_log_file = '/var/log/tsm/dsmc-errorlogname.log'
dsmc_moj_log_file = '/var/log/tsm/dsmc-mojLogFile.log'

mail_komu = ['rama@secar.cz']

nazov_servra = socket.gethostname()                                    #vrati napr. xyz.secar.cz - nazov servra
zalohovaci_adresar = os.path.join('/mnt/nfs_backup', nazov_servra, 'mysql')

zoznam_adresarov_na_zalohu = [ os.path.join(zalohovaci_adresar, '*'), os.path.join('/var/lib/mysql', '*')]              #zalohujeme adresar s mysqldump, adresar /etc a adresar s datovymi subormi mysql


#-------------------------------------------------------------------------------------------------#
odesilaci_email_adresa = socket.gethostname() + '@secar.cz'             #vrati napr. xyz@secar.cz
dnesny_datum_bez_casu = datetime.date.today()
dnesny_datum_s_casom = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())




def zapis_do_log_file(log_file, retazec_na_zapis):
    try:
        retazec_na_zapis = str(retazec_na_zapis) 
        retazec_na_zapis = retazec_na_zapis.splitlines()
        for lines in retazec_na_zapis:
            logging.basicConfig(filename=log_file, level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
            logging.info(lines)
        return True
    except:
        print('""" Chyba vo funkcii zapis_do_log_file(log_file, retazec_na_zapis) """ ')
        sys.exit(1)


def posli_mail_o_zalohe(od_koho, komu, subject, text):
    msg = email.mime.text.MIMEText(text)
    msg['Subject'] = subject
    msg['From'] = od_koho
    msg['To'] = komu
    msg.set_charset("utf-8")
    s = smtplib.SMTP('localhost')
    s.sendmail(od_koho, komu, msg.as_string())
    s.quit()

def posli_mail_na_zoznam_emailu(od_koho, komu, subject, text):
#    fix_encoding = lambda vystup: vystup.decode('utf8', 'ignore')
#    posli_text = fix_encoding(text)
    for i in range(len(komu)):
        msg = email.mime.text.MIMEText(text, 'plain', 'utf8')
        msg['Subject'] = subject
        msg['From'] = od_koho
        msg['To'] = komu[i]
        s = smtplib.SMTP('localhost')
        s.sendmail(od_koho, komu[i], msg.as_string())
        s.quit()


def vytvor_adresar(cesta_k_adresaru):
    if os.path.exists(cesta_k_adresaru):
        pass
    else:
        os.umask(0)  
        os.makedirs(cesta_k_adresaru, 0o777)
    return cesta_k_adresaru



def vymaz_adresar_rekurzivne(adresar):
    try:
        shutil.rmtree(adresar, ignore_errors=True)
        return True
    except:
        print(' """ Chyba vo funkcii vymaz_adresar_rekurzivne(adresar) """ ')
        sys.exit(1)



def vrat_zoznam_databaz():
    try:
        vystup = subprocess.check_output([mysql_prog, mysql_user, mysql_pass, mysql_host, '-Bse', mysql_shdb])
        vystup.strip()
        vystup = vystup.splitlines()
        vystup = [item.decode(encoding='utf-8', errors='ignore') for item in vystup]
        if len(mysql_nezalohuj_dbname) == 0:
            return vystup
        else:
            for item in mysql_nezalohuj_dbname:
                vystup.remove(item)
            return vystup
    except:
        print(' """ Chyba vo funkcii vrat_zoznam_databaz() """ ')
        sys.exit(1)


def zalohuj_adresare_do_tsm(zoznam_adresarov):
    ''' Vykona zalohu adresarov pomocou tsm prikazu dsmc

    Keyword arguments:
    zoznam_adresarov -- zoznam adresarov ktore sa maju zalohovat ako list

    dsmc_prog -- globalna premenna definuje cestu k prikazu dsmc
    dsmc_error_log_file -- globalna premenna definuje cestu k errologu prikazu dsmc

    Returns: list [vystup, prikaz]
    vystup -- string, ktory uchovava vystup z vykonaneho programu
    prikaz -- string, ktory uchovava prikaz, ktory sa vykonal 
    '''
    #try:
    zoznam_adresarov_ako_string = "'" + "' '".join(map(str, zoznam_adresarov)) + "'"
    prikaz = dsmc_prog + " incr " + zoznam_adresarov_ako_string + " -subdir=yes" + " -errorlogname=" + dsmc_error_log_file
    vystup = subprocess.check_output(prikaz, shell=True)
    vystup = vystup.decode(encoding='utf-8', errors='ignore')
    return [vystup, prikaz]
    #except:
    #    print(' """ Chyba vo funkcii zalohuj_adresare_do_tsm """ ')
    #    sys.exit(1)


def zaloha_databaz():
    try:
        zoznam_databaz = vrat_zoznam_databaz()
        zapis_do_log_file(dsmc_moj_log_file, "zalohujem databazy {0}".format(str(zoznam_databaz)))
        for i in range(len(zoznam_databaz)):
            databaza = zoznam_databaz[i]
            adresar_kam = os.path.join(zalohovaci_adresar, zoznam_databaz[i])                #kam zalohujem - uplna cesta k adresaru do ktoreho zalohujem
            meno_zalohovaneho_suboru = zoznam_databaz[i] + '.sql'
            vytvor_adresar(adresar_kam)
            prikaz = mysqldump_prog + ' ' + mysql_user + ' ' + mysql_pass + ' --databases ' + zoznam_databaz[i] + ' --single-transaction -c --add-drop-table --add-locks > ' + os.path.join(adresar_kam, meno_zalohovaneho_suboru)
            zapis_do_log_file(dsmc_moj_log_file, "provadim prikaz {0}".format(prikaz))
            os.system(prikaz)
            zapis_do_log_file(dsmc_moj_log_file, "zaloha databazy {0} bola uspesna a zapisana do suboru {1}".format(databaza, os.path.join(adresar_kam, meno_zalohovaneho_suboru)))
        #teraz zazalohujem vsetky databazy:
        prikaz = mysqldump_prog + ' ' + mysql_user + ' ' + mysql_pass + ' --single-transaction --all-databases -c --add-drop-table --add-locks > ' + zalohovaci_adresar + '/mysqldump-all.sql'
        zapis_do_log_file(dsmc_moj_log_file, "provadim prikaz {0}".format(prikaz))
        os.system(prikaz)
        zapis_do_log_file(dsmc_moj_log_file, "zaloha celej mysql databazy bola uspesne ulozena do suboru {0}".format(os.path.join(zalohovaci_adresar, 'mysqldump-all.sql')))
        zapis_do_log_file(dsmc_moj_log_file, "\n\n")
        zapis_do_log_file(dsmc_moj_log_file, "vykonavam prikaz dsmc na zalohu")
        vystup_z_programu = zalohuj_adresare_do_tsm(zoznam_adresarov_na_zalohu)
        zapis_do_log_file(dsmc_moj_log_file, "vykonal som prikaz {0}".format(vystup_z_programu[1]))  
        zapis_do_log_file(dsmc_moj_log_file, vystup_z_programu[0])
        zapis_do_log_file(dsmc_moj_log_file, "\n\n")
        posli_mail_na_zoznam_emailu(odesilaci_email_adresa, mail_komu, 'uspesne - zaloha mysql databaz', vystup_z_programu[0])
        zapis_do_log_file(dsmc_moj_log_file, "mazem zalohovaci adresar {0}".format(zalohovaci_adresar))
        vymaz_adresar_rekurzivne(zalohovaci_adresar)
        zapis_do_log_file(dsmc_moj_log_file, "zalohovaci adresar {0} je zmazany".format(zalohovaci_adresar))
        zapis_do_log_file(dsmc_moj_log_file, "\n\n\n\n\n")
    except:
        posli_mail_na_zoznam_emailu(odesilaci_email_adresa, mail_komu, '!!! chyba zalohy !!!', 'zaloha mysql databaz sa nepodarila')
        exctype, value = sys.exc_info()[:2]
        zapis_do_log_file(dsmc_moj_log_file, "!!! E R R O R !!!")
        zapis_do_log_file(dsmc_moj_log_file, str(exctype))
        zapis_do_log_file(dsmc_moj_log_file, str(value))
        sys.exit(1)


zaloha_databaz()
#zalohuj_adresare_do_tsm(zoznam_adresarov_na_zalohu)
