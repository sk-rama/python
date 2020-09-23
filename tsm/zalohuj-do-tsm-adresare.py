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

dsmc_prog = '/opt/tivoli/tsm/client/ba/bin/dsmc'
dsmc_error_log_file = '/var/log/tsm/dsmc-errorlogname.log'
dsmc_moj_log_file = '/var/log/tsm/dsmc-mojLogFile.log'

mail_komu = ['rama@secar.cz']

nazov_servra = socket.gethostname()                                    #vrati napr. xyz.secar.cz - nazov servra

zoznam_adresarov_na_zalohu = [ os.path.join('/etc', '*'), os.path.join('/var/www', '*')]             #zalohujeme adresar s mysqldump, adresar /etc a adresar s datovymi subormi mysql


#-------------------------------------------------------------------------------------------------#
odesilaci_email_adresa = socket.gethostname() + '@secar.cz'             #vrati napr. xyz@secar.cz
dnesny_datum_bez_casu = datetime.date.today()
dnesny_datum_s_casom = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())



# create custom logger
# logger = logging.getLogger('my_logger_name')
logger = logging.getLogger('directory_backup')

# create handlers (FileHandlers in our program)
handler_info = logging.FileHandler(dsmc_moj_log_file)
handler_info.setLevel(logging.INFO)
handler_error = logging.FileHandler(dsmc_error_log_file)
handler_error.setLevel(logging.ERROR) 

# Create formatters and add it to handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler_info.setFormatter(formatter)
handler_error.setFormatter(formatter)

# add handlers to the logger
logger.addHandler(handler_info)
logger.addHandler(handler_error)

# The root logger always defaults to WARNING level
logger.setLevel("INFO")


def zapis_do_log_file(log_file, retazec_na_zapis):
    try:
        retazec_na_zapis = str(retazec_na_zapis) 
        retazec_na_zapis = retazec_na_zapis.splitlines()
        for lines in retazec_na_zapis:
            logging.basicConfig(filename=log_file, level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
            logging.info(lines)
        return True
    except:
        print(' """ Chyba vo funkcii zapis_do_log_file(log_file, retazec_na_zapis) """ ')
        sys.exit(1)


def posli_mail_na_zoznam_emailu(od_koho, komu, subject, text):
    for i in range(len(komu)):
        msg = email.mime.text.MIMEText(text, 'plain', 'utf8')
        msg['Subject'] = subject
        msg['From'] = od_koho
        msg['To'] = komu[i]
        s = smtplib.SMTP('localhost')
        s.sendmail(od_koho, komu[i], msg.as_string())
        s.quit()


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
    try:
        zoznam_adresarov_ako_string = "'" + "' '".join(map(str, zoznam_adresarov)) + "'"
        prikaz = dsmc_prog + " incr " + zoznam_adresarov_ako_string + " -subdir=yes" + " -errorlogname=" + dsmc_error_log_file
        vystup = subprocess.check_output(prikaz, shell=True)
        vystup = vystup.decode(encoding='utf-8', errors='ignore')
        return [vystup, prikaz]
    except Exception as e:
        print(' """ Chyba vo funkcii zalohuj_adresare_do_tsm """ ')
        return [vystup, prikaz]
        sys.exit(4)


def main():
    try:
        logger.info("\n\n")
        logger.info("--------------------------------------------------------------")
        logger.info("Zacinam zalohovat adresare:")
        logger.info(zoznam_adresarov_na_zalohu)
        vystup_z_programu = zalohuj_adresare_do_tsm(zoznam_adresarov_na_zalohu)
        logger.info("vykonal som prikaz {0}".format(vystup_z_programu[1]))  
        logger.info(vystup_z_programu[0])
        logger.info("\n\n")
        logger.info("odesilam email o zalohe")
        posli_mail_na_zoznam_emailu(odesilaci_email_adresa, mail_komu, 'uspesne - zaloha adresarov', vystup_z_programu[0])
        logger.info("email o zalohe je odoslany")
    except Exception as e:
        logger.error("Zalohovani Adresaru se nezdarilo")
        logger.error("Odesilam email o nezdarenem zalohovani adresaru")
        posli_mail_na_zoznam_emailu(odesilaci_email_adresa, mail_komu, '!!! chyba zalohy !!!', 'zaloha adresarov sa nepodarila')
        exc_type, exc_value, exc_traceback = sys.exc_info()
        logger.error("!!! E R R O R !!!")
        logger.error(str(exc_type))
        logger.error(str(exc_value))
        logger.error(str(exc_traceback))
        logger.error(str(e))
        sys.exit(1)



if __name__ == "__main__":
    main()
