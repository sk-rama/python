import sys
print(sys.path)

import pytest
import factory
from faker import Faker

import sqlalchemy as db
from sqlalchemy.orm import sessionmaker
import radius
import config as cfg


engine = db.create_engine(cfg.SQLALCHEMY_DATABASE_URI)
Session = sessionmaker()



class RadReplyFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = radius.RadReply

    id = '9999'
    attribute = Faker().first_name_male()
    username = Faker().last_name_male()
    op = '='
    value = Faker().ipv4_private(network=False, address_class="a") 


@pytest.fixture(scope='module')
def connection():
    connection = engine.connect()
    yield connection
    connection.close()

@pytest.fixture(scope='function')
def session(connection):
    transaction = connection.begin()
    session = Session(bind=connection)
    RadReplyFactory._meta.sqlalchemy_session = session
    yield session
    session.close()
    transaction.rollback()

def test_conection(connection):
    assert connection

def test_session(session):
    assert session

def test_test_same_max_id(session):
    result = radius.test_same_max_id(session)
    assert True == result

def test_case_01(session):
    user = RadReplyFactory.create()
    print(user)
    assert session.query(radius.RadReply).filter(radius.RadReply.username == user.username).one()
    radius.delete_tel_number(session, user.username, radius.RadReply.username)
    assert None == session.query(radius.RadReply).filter(radius.RadReply.username == user.username).one_or_none()
