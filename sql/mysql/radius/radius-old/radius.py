#!/usr/bin/env python
import os
import sys
import MySQLdb
import string

file = "/etc/rc-local/skripty/mysql/vstupne_cisla.txt"

#tato funkcia nam zkontroluje,ci je tel.cislo v spravnom formate
#spravny format= True, nespravny format=False
def check_number_format(number):
    if (( number[0:3] != '420' ) or ( len(number) != 12 )):
        return False
    else:
        return True

def nacitaj_vstupne_data(subor):
    file_instance = open(subor, "r")
    obsah_suboru = file_instance.readlines() #toto nam vrati obash suboru ako zoznam,kde jeden zaznam v zozname je jeden riadok vratane znaku pre prechod na novy riadok
    for i in range(len(obsah_suboru)):
        obsah_suboru[i] = string.strip(obsah_suboru[i]) #zbavime sa znakov pre prechod na novy riadok
    file_instance.close() #zavrieme otvoreny subor
    return obsah_suboru #vratime obsah suboru(v nasom pripade tel.cisla) ako zoznam

#tato funkcia nam zkontroluje,ci sa dane tel.cislo v databaze v konkretnej tabulke nachadza alebo nie
#nachadza sa = True, nenachadza sa = False
def check_existence_in_table(number, table):
    radius_db = MySQLdb.connect(host="localhost", user="radius", passwd="20lenka10", db="radius")
    radius_cursor = radius_db.cursor()
    radius_cursor.execute(""" SELECT * FROM %s where UserName='%s' """ % (table, number) )
    pocet_riadkov = int(radius_cursor.rowcount)
    radius_cursor.close()
    radius_db.close()
    if pocet_riadkov == 1:
        return True
    elif pocet_riadkov == 0:
        return False
    else:
        print "cislo " ,number, " sa nachadza v tabulke " ,table, " viackrat"
        sys.exit(0)

#tato funkcia ma ako vstup zoznam tel.cislel a ako vystup tiez,ale premazane o tel.cisla ktore sa uz v databaze nachadzaju,naviac zkontrouje ci su tel.cisla v spravnom formate
def pretried_vstupne_data(zoznam):
    vysledny_zoznam = []
    for i in range(len(zoznam)):
        if check_number_format(zoznam[i]):
            continue
        else:
            print "cislo ", zoznam[i], " nema spravny format"
            sys.exit(1)
    for i in range(len(zoznam)):
        if ( check_existence_in_table(zoznam[i], 'radcheck') and check_existence_in_table(zoznam[i], 'radreply') and check_existence_in_table(zoznam[i], 'radusergroup')):
            print "!!! " + zoznam[i] + " uz v databaze je !!!"
            continue
        elif ( not(check_existence_in_table(zoznam[i], 'radcheck')) and not(check_existence_in_table(zoznam[i], 'radreply')) and not(check_existence_in_table(zoznam[i], 'radusergroup')) ):
            if zoznam[i] not in vysledny_zoznam: #testujem,ci sa v zozname nenachadza cislo viackrat,ak nie, tak ho pripojim k zoznamu
                vysledny_zoznam.append(zoznam[i])
        else:
            print "cislo " ,zoznam[i], " je v databaze radius zle zadane"
            sys.exit(1)
    return vysledny_zoznam

def set_next_id(tabulka):
    radius_db = MySQLdb.connect(host="localhost", user="radius", passwd="20lenka10", db="radius")
    radius_cursor = radius_db.cursor()
    radius_cursor.execute(""" SELECT MAX(id) FROM %s """ %(tabulka))
    result = radius_cursor.fetchall()
    result = result[0] #ak chceme cislo, musime toto urobit 2krat
    result = result[0]
    result = ( result + 1 ) #chceme dalsie id, takze zvysime o 1
    radius_cursor.close()
    radius_db.close()
    return result

#tato funkcia nam vrati nasledujucu ip adresu od adresy s najvacsim id v tabulke radreply
def set_next_ip():
    radius_db = MySQLdb.connect(host="localhost", user="radius", passwd="20lenka10", db="radius")
    radius_cursor = radius_db.cursor()
    radius_cursor.execute("SELECT MAX(id) FROM radreply")
    result = radius_cursor.fetchall()
    result = result[0] #ak chceme cislo, musime toto urobit 2krat
    result = result[0]
    radius_cursor.execute(""" SELECT Value FROM radreply where id='%s' """ %(result))
    result = radius_cursor.fetchall()
    result = result[0] #ak chceme iba ip adresu,musime toto urobit 2krat
    result = result[0]
    result = string.split(result, '.') #rozdelime ip adresu na seznam 4 cisel
    ip1 = int(result[0]); ip2 = int(result[1]); ip3 = int(result[2]); ip4 = int(result[3])
    if ( ip4 == 254 ):
        ip4 = 1
        ip3 = ( ip3 + 1 )
    else:
        ip4 = ( ip4 + 1 )
        ip3 = ip3
    ip1 = repr(ip1); ip2 = repr(ip2); ip3 = repr(ip3); ip4 = repr(ip4) #to iste by urobilo: ip1 = `ip1`; ip2 = `ip2; ip3 = `ip3`; ip4 = `ip4`
    radius_cursor.close()
    radius_db.close()
    return string.join([ip1, ip2, ip3, ip4], '.')

def vloz_do_radcheck(cislo):
    hodnota_id = set_next_id('radcheck')
    hodnota_username = cislo
    hodnota_attribute = "Password"
    hodnota_op = "=="
    hodnota_value = "password"
    radius_db = MySQLdb.connect(host="localhost", user="radius", passwd="20lenka10", db="radius")
    radius_cursor = radius_db.cursor()
    radius_cursor.connection.autocommit(True)
    radius_cursor.execute("INSERT INTO radcheck (id, username, attribute, op, value) VALUES (%s, %s, %s, %s, %s)", (hodnota_id, hodnota_username, hodnota_attribute, hodnota_op, hodnota_value))
    radius_cursor.close()
    radius_db.close()
    return 0

def vloz_do_radusergroup(cislo):
    hodnota_id = set_next_id('radusergroup')
    hodnota_username = cislo
    hodnota_groupname = "O2"
    radius_db = MySQLdb.connect(host="localhost", user="radius", passwd="20lenka10", db="radius")
    radius_cursor = radius_db.cursor()
    radius_cursor.connection.autocommit(True)
    #radius_cursor.execute("INSERT INTO usergroup (id, UserName, GroupName) VALUES (%s, %s, %s)", (hodnota_id, hodnota_UserName, hodnota_GroupName))
    radius_cursor.execute("INSERT INTO radusergroup (id, username, groupname, priority) VALUES (%s, %s, %s, %s)", (hodnota_id, hodnota_username, hodnota_groupname, '1'))
    radius_cursor.close()
    radius_db.close()
    return 0

def vloz_do_radreply(cislo):
    hodnota_id = set_next_id('radreply')
    hodnota_username = cislo
    hodnota_attribute = "Framed-IP-Address"
    hodnota_op = "="
    hodnota_value = set_next_ip()
    radius_db = MySQLdb.connect(host="localhost", user="radius", passwd="20lenka10", db="radius")
    radius_cursor = radius_db.cursor()
    radius_cursor.connection.autocommit(True)
    radius_cursor.execute("INSERT INTO radreply (id, username, attribute, op, value) VALUES (%s, %s, %s, %s, %s)", (hodnota_id, hodnota_username, hodnota_attribute, hodnota_op, hodnota_value))
    radius_cursor.close()
    radius_db.close()
    return 0


def vloz_do_radius_zo_suboru():
    tel_cisla = pretried_vstupne_data(nacitaj_vstupne_data(file))
    for i in range(len(tel_cisla)):
        if vloz_do_radcheck(tel_cisla[i]) == 0:
            print "+++ tel.cislo " + tel_cisla[i] + " uspesne vlozene do tabulky radcheck +++"
        if vloz_do_radusergroup(tel_cisla[i]) == 0:
            print "+++ tel.cislo " + tel_cisla[i] + " uspesne vlozene do tabulky radusergroup +++"
        if vloz_do_radreply(tel_cisla[i]) == 0:
            print "+++ tel.cislo " + tel_cisla[i] + " uspesne vlozene do tabulky radreply +++"
        print ""
        print ""

vloz_do_radius_zo_suboru()
#set_next_ip()
