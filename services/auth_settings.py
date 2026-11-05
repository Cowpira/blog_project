from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.orm import Session
from data_model.models import Person
from sqlalchemy import delete as sql_delete
from data_model.models import Password_Reset_Token
import logging
import bcrypt
import hashlib
import secrets
bcrypt.__about__ = bcrypt

SPECIAL_CHARACTER= ['@', '#', '$', '%', '=', '!', '?', ':', '.', '-', '_']


class Config():
    orm_mode=True

#method to hash password
pwd_cxt = CryptContext(schemes=["bcrypt"], deprecated="auto")


# method to encrypt password
def encrypt(password) -> str:
    return pwd_cxt.hash(password)



# function to veryfy user passkey for login, recover account, reset password
def verify_pass(input_key, hashed_key) -> bool:
    return pwd_cxt.verify(input_key, hashed_key)



# function to generate random token for reset password verification
def generate_reset_token() -> str:
    # generate 64 chars token
    return secrets.token_urlsafe(32)



# function to hash reset token
def hash_reset_token(token: str) -> str:
    # receive a token and hashed to prevent brute force attack
    return hashlib.sha256(token.encode()).hexdigest()



# function to validate plain token with hashed token
async def validate_reset_token(token, db: Session) -> Password_Reset_Token:
    hash_token= hash_reset_token(token)
    result= db.execute(select(Password_Reset_Token).where(Password_Reset_Token.Token_Hash == hash_token))
    data_token= result.scalars().first()

    return data_token if data_token else False



# function to delete previous and used tokens
def delete_previous_token(user_id, db: Session):
    result= sql_delete(Password_Reset_Token).where(Password_Reset_Token.User_Id == user_id)
    db.execute(result)
    db.commit()



# function to verury if user entered a strong password with matching pattern
def strong_password(password) -> bool:
    if len(password) < 8:
        return False
    
    if not any(char.isupper() for char in password):
        return False
    
    if not any(char.islower() for char in password):
        return False
    
    if not any(char.isdigit() for char in password):
        return False
    
    if not any(char in SPECIAL_CHARACTER for char in password):
        return False

    return True



# function to load obj user
async def load_user(email: str, db: Session):
    try:
        # load object with user loged in data
        result= db.execute(select(Person).where(Person.Email == email))
        return result.scalar()

    except Exception as user_exec:
        logging.info(f'Username: {email} not found or not registered!!')
        return user_exec