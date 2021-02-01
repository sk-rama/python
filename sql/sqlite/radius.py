#!venv/bin/python3

import sys
import ipaddress
import sqlalchemy as db
import random
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import select, func, exists
import pandas as pd
import config as cfg


Base = declarative_base()


class RadCheck(Base):
    __tablename__ = 'radcheck'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    attribute = db.Column(db.String, default = 'Password')
    op = db.Column(db.String, default = '==')
    value = db.Column(db.String, default = 'password')
 
    def __repr__(self):
        return(f"RadCheck(id={self.id}, username={self.username}, attribute={self.attribute}, op={self.op}, value={self.value})\n")



class RadReply(Base):
    __tablename__ = 'radreply'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    attribute = db.Column(db.String, default='Framed-IP-Address')
    op = db.Column(db.String, default='=')
    value = db.Column(db.String, default='0.0.0.0')

    def __repr__(self):
        return(f"RadCheck(id={self.id}, username={self.username}, attribute={self.attribute}, op={self.op}, value={self.value})\n")



class RadUserGroup(Base):
    __tablename__ = 'radusergroup'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    groupname = db.Column(db.String, default = 'secar')
    priority = db.Column(db.Integer, default = 1)

    def __repr__(self):
        return(f"RadUserGroup(id={self.id}, username={self.username}, groupname={self.groupname}, priority={self.priority})\n")


def get_next_ip_address(db_session):
    last_ip_list = db_session.query(RadReply).order_by(RadReply.id.desc()).limit(1)
    last_ip = last_ip_list[0].value
    ip = ipaddress.ip_address(last_ip)
    if str(ip).endswith('254'):
        return str(ip + 3)
    else:
        return str(ip + 1) 

def get_max_from_column(db_session, model_column: str):
    result = db_session.query(model_column).all()
    result = [value for value, in result]
    return max(result)

def test_same_max_id(db_session):
    return True if get_max_from_column(db_session, RadCheck.id) == get_max_from_column(db_session, RadReply.id) == get_max_from_column(db_session, RadUserGroup.id) else False

def delete_tel_number(db_session, number: str, model_column: str):
    query = db_session.query(model_column).filter(model_column==number)
    query.delete()

def get_value_from_column(db_session, model:str, model_column: str, question: str):
    result = db_session.query(model).filter(model_column==question).one()
    return result.value

def get_value_from_column2(db_session, model:str, model_column: str, question: str):
    #result = db_session.query(model).filter(model_column==question).one()
    result = db_session.query(eval(model)).filter(eval(model + '.' + model_column)==question).one()
    return result.value

def exist_in_db(db_session, numbers):
    try:
        for number in numbers:
            query1 = db_session.query(exists().where(RadCheck.username == str(number))).scalar()
            query2 = db_session.query(exists().where(RadReply.username == str(number))).scalar()
            query3 = db_session.query(exists().where(RadUserGroup.username == str(number))).scalar()
            if query1 or query2 or query3:
                print(f'\n \033[0;31m tel. cislo {number} se uz v databaze nachazi !!! \033[0m \n')
                return True
        return False
    except:
        print('Nastala chyba')
        
        
        

def add_to_db(db_session, tel_number):
    test_same_max_id(db_session)

    id = get_max_from_column(session, RadCheck.id) + 1

    model_1 = RadCheck(id = id, username = str(tel_number))
    model_2 = RadReply(id = id, username = str(tel_number), value = get_next_ip_address(session))
    model_3 = RadUserGroup(id = id, username = str(tel_number))

    session.add(model_1)
    session.add(model_2)
    session.add(model_3)
    

if __name__ == "__main__":
    df = pd.read_csv('vstupne_cisla.csv', header=None, names=['tel. number'])
    tel_numbers = df['tel. number'].unique()
   
    engine = db.create_engine(cfg.SQLITE_ENGINE, echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()

    if test_same_max_id(session):
        print('\033[0;32m nejvetsi ID ve vsech tabulkach je stejne \033[0m')
    else:
        print(f'\n \033[0;31m nejvetsi ID ve vsech tabulkach neni stejne !!! \033[0m \n')
        sys.exit(0)

    if exist_in_db(session, tel_numbers):
        sys.exit(0)

    for number in tel_numbers:
        #add_to_db(session, number)
        pass
         
    #print(session.query(RadCheck).all())
    #print(session.query(RadCheck).get(5))
    #print(session.query(RadReply).get(5))
    #print(test_same_max_id(session))
    
    
    #rad1_1 = RadCheck('420111222333')
    #session.add(rad1_1)
    #rad1_2 = RadReply(username='420111222333')
    #session.add(rad1_2)
    #rad1_3 = RadUserGroup('420111222333')
    #session.add(rad1_3)
    
    session.commit()
    #print(engine.table_names())
    #last = session.query(RadReply).order_by(RadReply.id.desc()).limit(1)
    #print(last[0].value)
    
    #print(get_next_ip_address(session))
    #print(get_max_from_column(session, RadReply.id))
    print(get_value_from_column(session, RadReply, RadReply.username, "420735792264"))
    print(get_value_from_column2(session, 'RadReply', 'username', "420735792264"))
