#!/usr/bin/env python

import os
import re
import os.path




directory = ['/mnt/secar/lapac/Maildir/cur', '/mnt/secar/lapac/Maildir/new', '/mnt/secar/lapac-spamov/Maildir/cur', '/mnt/secar/lapac-spamov/Maildir/new']
regex_pattern = '((From: )|(To: ))([\w =?\-"<@>\.])*(celartrace@gsc.com|vystavba@secar.cz|monika.minarikova@kaktus.cz|owncloud@secar.cz|it@secar.cz|it.support@secar.cz|vision@sherlogvision.cz|nagios@monitor.secar.cz|hd@secar.cz|movistar@sherlogtrace.cz|helpdesk@kswr.cz|mkubes@kswr.cz|traceonline@sherlogtrace.cz|test@kaktus.cz|sherloggps@sherlogtrace.cz|sherlogtrace@sherlogtrace.cz|mexico@sherlogtrace.cz|localiza@sherlogtrace.cz|movistargps@sherlogtrace.cz|icinga@secar.cz|restaurace-historie@seznam.cz|info@secar.cz|info@sherlog.cz|traceonline@secar.cz|carcontrol@o2.cz|carcontrol@o2.sk|carcontrol@o2.com|plazsent@secar.cz|thajsky-raj.cz|alza.cz|movistar.pe|movistar.cl|telefonica.com|sherlog.pe|secarstar.cl|sherlogmexico.com|sherlogcolombia.com|movistar.col|kasa.cz|gme.cz|mironet.cz|amplion.cz|sms.sms|czc.cz|yahoogroups.com|slevomat.cz|test@secar.cz|revize@sherlog.cz|wd@herlog.cz|altamirano@sherlog.com|asistentka.raynet.cz|booking.com|ceskaposta@cpost.cz|spravazeleznic.cz|ucs@secar.cz|teltonika-iot-group.com|webdispecink.cz|noreply|fakturace.se.klient@sherlog.cz|wd.ext@kswr.cz){1,1}'




def zmaz_subor(file_path):
    os.remove(file_path)

def najdi_text_v_subore(subor, regex_text):
    reg = re.compile(regex_text, re.IGNORECASE)
    fileHandle = open(subor, "r")
    fileContent = fileHandle.read()
    fileHandle.close()
    reg_vyraz_from_reg = reg.search(fileContent)
    if reg_vyraz_from_reg:
        print reg_vyraz_from_reg.group() 
        return True
    else:
        return False


def list_files_in_directory_no_recursive(adresar):
    # returns a list of names (with extension, with full path) of all files
    # in folder path
    files = []
    for name in os.listdir(adresar):
        if os.path.isfile(os.path.join(adresar, name)):
            full_path_file = os.path.join(adresar, name)
            files.append(full_path_file)
    return files


def zmaz_subory_z_adresarov(zoznam_adresarov, regex_text):
    files = []
    dict_pocet_zmazanych_suborov_v_adresary = dict()
    for adresar in zoznam_adresarov:
        pocitadlo = 0
        all_files = list_files_in_directory_no_recursive(adresar)
        for i in range(len(all_files)):
            if os.path.isfile(all_files[i]):
                if najdi_text_v_subore(all_files[i], regex_text):
                    files.append(all_files[i])
                    print("mazem " + str(i) + "subor s cestou " + all_files[i] + "\n")
                    zmaz_subor(all_files[i])
                    pocitadlo += 1
        dict_pocet_zmazanych_suborov_v_adresary[adresar] = pocitadlo
    print dict_pocet_zmazanych_suborov_v_adresary
    return files




 
zmaz_subory_z_adresarov(directory, regex_pattern)
