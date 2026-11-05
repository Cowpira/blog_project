from datetime import datetime
import sys, os, pytest
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from starlette.testclient import TestClient
from data_model.models import User
from main import app
from services import db_connection, helper, auth_settings

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

FIRST_NAME= 'Celio'
LAST_NAME= 'Miller'
ADDRESS= '209 Street 113, Rockwall. Texas'
EMAIL= str.lower('celio_cali@icloud.com')
PASSWORD= 'Celio#100'
PHONE= '(999) 000-1111'


engine= create_engine('sqlite:///./BlogApplication.db')
Test_Session= sessionmaker(autocommit=False, autoflush=False, bind=engine)


# connecting to DB using the test session signature
@pytest.fixture(scope='function')
def test_session() -> Generator:
    session= Test_Session()

    try:
        yield session
    finally:
        session.close()


# method to create all the test tables and droping at the end
@pytest.fixture(scope='function')
def app_test():
    db_connection.Base.metadata.create_all(bind=engine)
    yield app
    db_connection.Base.metadata.drop_all(bind=engine)


# setting client to the test DB and defing the test_DB
@pytest.fixture(scope='function')
def client(app_test, test_session):
    def _test_db():
        try:
            yield test_session
        finally:
            pass

    # overriding the det_db method to test_db
    app_test.dependency_overrides[db_connection.get_db]= _test_db
    return TestClient(app_test)    


# setting authorized client to the test DB and defing the test_DB
@pytest.fixture(scope='function')
def authorized_client(app_test, test_session, verified_user):
    def _test_db():
        try:
            yield test_session
        finally:
            pass
    
    app_test.dependency_overrides[db_connection.get_db]= _test_db
    data= auth_settings.generate_tokens(verified_user) 
    client= TestClient(app_test)
    client.headers['Authorization']= f'Bearer {data["access_token"]}'
    return client


# defining a user instance
def obj_user():
    user= User(
        First_Name= FIRST_NAME,
        Last_Name= LAST_NAME,
        Address= ADDRESS,
        Email= EMAIL,
        Password= auth_settings.PassEncrypt(PASSWORD),
        Phone= PHONE,
        Created= globals.Cur_Date()
    )
    return user


# declaring new instance of USER not activated
@pytest.fixture(scope='function')
def user(test_session):
    user= obj_user()
    test_session.add(user)
    test_session.commit()
    test_session.refresh(user)
    return user


# setting USER  as active user but NOT verified
@pytest.fixture(scope='function')
def unverified_user(test_session):
    user= obj_user()
    user.Activated_Date= datetime.now()
    
    test_session.add(user)
    test_session.commit()
    test_session.refresh(user)
    return user


# setting USER as active and verified
@pytest.fixture(scope='function')
def verified_user(test_session):
    user= obj_user()
    user.Activated= True
    user.Activated_Date= datetime.now()
    
    test_session.add(user)
    test_session.commit()
    test_session.refresh(user)
    return user
