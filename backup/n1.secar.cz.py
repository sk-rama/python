#!/usr/bin/env python3

import os
import os.path
import sys
import logging
import pathlib
import traceback 
import subprocess
import smtplib
import email.mime.text
import socket
from datetime import datetime

# parameters for remote copy with ssh and tar
#-------------------------------------------------------------------------------------------------#
srv_hostname       = 'websystem-test.secar.cz'
srv_ip             = '192.168.221.54'
dirs_to_backup     = ['/etc/init.d', '/usr/lib/ssl']
pattern_to_exclude = ['/etc/rc-local/*']
today              = datetime.utcnow().strftime('%Y-%m-%d')
backup_dir         = os.path.join('/var/backup', today, srv_hostname)
log_file           = os.path.join('/var/backup', today, srv_hostname,  '.'.join([srv_hostname, 'log']))

# parameters for ssh
#-------------------------------------------------------------------------------------------------#
ssh_user = 'rrastik'
ssh_key  = '/home/rrastik/.ssh/id_rsa'

# parameters for email
#-------------------------------------------------------------------------------------------------#
enable_email = True
mail_to      = ['manak@sherlog.cz']
mail_from    = 'websystem-test@secar.cz'

# parameters for mysql dump
#-------------------------------------------------------------------------------------------------#
enable_mysql = True
mysql_user = 'root'
mysql_pass = 'password'
mysql_host = 'localhost'
mysql_prog = '/usr/bin/mysql'
mysqldump_prog = '/usr/bin/mysqldump'
mysql_nezalohuj_dbname = []             #definuj nazvy databaz ako list-mena databaz musia byt ako string a su case sensitive, napr. mysql_nezalohuj_dbname = ["phpmyadmin", "information_schema"]



def send_email(From, To, Subject, Message):
  for i in range(len(To)):
    msg = email.mime.text.MIMEText(Message, 'plain', 'utf8')
    msg['Subject'] = Subject
    msg['From'] = From
    msg['To'] = To[i]
    s = smtplib.SMTP('localhost')
    s.sendmail(From, To[i], msg.as_string())
    s.quit()

def return_mysql_databases():
  try:
    mysql_cmd = ' '.join([mysql_prog, ''.join(['--user=', mysql_user]), ''.join(['--password=', mysql_pass]), ''.join(['--host=', mysql_host]), '-Bse', '"show databases"'])
    command = " ".join(['ssh', '-i', ssh_key, '-l', ssh_user, srv_ip, ''.join(["'", mysql_cmd, "'"]) ])
    output = subprocess.run(command, capture_output=True, universal_newlines=True, shell=True)
    return_string = output.stdout
    return_string.strip()
    return_list = return_string.splitlines()
    if len(mysql_nezalohuj_dbname) == 0:
      return return_list
    else:
      for item in mysql_nezalohuj_dbname:
        return_list.remove(item)
        return return_list
  except:
    print(' """ Chyba vo funkcii vrat_zoznam_databaz() """ ')
    sys.exit(1)

def backup_db(db):
  try:
    bck_dir = os.path.join(backup_dir, 'mysql')
    make_dir(bck_dir)  
    mysqldump_cmd = ' '.join([mysqldump_prog, ''.join(['--user=', mysql_user]), ''.join(['--password=', mysql_pass]), '--databases', db, '--single-transaction -c --add-drop-table --add-locks | gzip '])
    command = " ".join(['ssh', '-i', ssh_key, '-l', ssh_user, srv_ip, ''.join(["'", mysqldump_cmd, "'"]), '>', os.path.join(bck_dir, ''.join([db, '.gzip'])) ])   
    output = subprocess.run(command, capture_output=True, universal_newlines=True, shell=True)
    return output
  except:
    logger.error('backup failed')
    logger.error("uncaught exception: %s", traceback.format_exc())
    return False

def backup_all_db():
  try:
    bck_dir = os.path.join(backup_dir, 'mysql')
    make_dir(bck_dir)
    mysqldump_cmd = ' '.join([mysqldump_prog, ''.join(['--user=', mysql_user]), ''.join(['--password=', mysql_pass]), '--single-transaction --all-databases -c --add-drop-table --add-locks | gzip '])
    command = " ".join(['ssh', '-i', ssh_key, '-l', ssh_user, srv_ip, ''.join(["'", mysqldump_cmd, "'"]), '>', os.path.join(bck_dir, ''.join(['all_databases', '.gzip'])) ])
    output = subprocess.run(command, capture_output=True, universal_newlines=True, shell=True)
    return output
  except:
    logger.error('backup failed')
    logger.error("uncaught exception: %s", traceback.format_exc())
    return False


def make_tar_exclude(dir_list):
  try:
    excl_lst = [ ''.join(['--exclude=', dir]) for dir in dir_list ]
    return ' '.join(excl_lst)
  except OSError as e:
    logger.error(e, exc_info=True)
  except:
    logger.error("uncaught exception: %s", traceback.format_exc())
    return False

def make_dir(full_path):
  path = pathlib.Path(full_path)
  path.mkdir(parents=True, exist_ok=True)

def ssh_backup():
  try:
    tar_patter_excluded = make_tar_exclude(pattern_to_exclude)
    command = " ".join(['ssh', '-i', ssh_key, '-l', ssh_user, srv_ip, '"tar', tar_patter_excluded, '--ignore-failed-read -v -czf -', ' '.join(dirs_to_backup), '"', '>', ''.join([backup_dir, '/', srv_hostname, '.tgz']) ])
    output = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True)
    #logger.info(f'standart output is: {output.stdout}')
    logger.info(f'standart error is: {output.stderr}')
    logger.info(f'return code is: {output.returncode}')
    logger.info(f'executed command was: {output.args}')
    if output.stderr:
      logger.error(f'previous command was executed with ERRORS')
    if enable_email:
      if output.stderr:
        send_email(mail_from, mail_to, 'ERROR - backup of directories', "\n".join([output.stdout, output.stderr, f"return code for {command} is {output.returncode}"]))
      else:
        send_email(mail_from, mail_to, 'OK - backup of directories', "\n".join([output.stdout, output.stderr, f"return code for {command} is {output.returncode}"]))  
    return True
  except:
    logger.error('backup failed')
    logger.error("uncaught exception: %s", traceback.format_exc())
    if enable_email:
      send_email(mail_from, mail_to, 'ERROR - backup of directories', traceback.format_exc())
    return False
  

if __name__ == '__main__':
  make_dir(backup_dir)
  logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s %(name)s %(process)d %(levelname)s %(message)s', datefmt='%Y:%m:%d %H:%M:%S')
  logger = logging.getLogger(__name__)
  ssh_backup()
  print(return_mysql_databases())
  print(backup_db('zzz'))
  print(backup_all_db())
