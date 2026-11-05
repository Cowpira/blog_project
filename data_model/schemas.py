from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from uuid import UUID


# token schema
class Token(BaseModel):
    Access_token: str
    Token_Type: str= "Bearer"


# login schema
class Login(BaseModel):
    Email: EmailStr
    Password: str


# recover account link schema
class Recover_Password(BaseModel):
    Email: EmailStr= Field(max_length= 120)


# set new password from recover link schema
class Password_Reset(BaseModel):
    Token: str
    New_Password: str
    Conf_Password: str


# update password schema (authenticated)
class Update_Password(BaseModel):
    Current_Password: str
    New_Password: str


#  activate account schema
class Activate_User(BaseModel):
    Token: str
    Email: EmailStr
    User_Id: UUID


# PERSON parent schema
class Person(BaseModel):
   First_Name: str= Field(min_length=3, max_length=25)
   Last_Name: str= Field(min_length=2, max_length=25)
   Phone: str= Field(max_length=14)
   Email: str= Field(max_length=100)
   Password: str= Field(max_length=100)
   Created: datetime


# new developer schema
class New_Developer(Person):
    Address: str= Field(min_length= 5, max_length= 100)
    Cod_Title: str= Field(min_length=3, max_length=100)
    Cod_Lang: str
    Years_Exp: int
    Image: str
    Img_Path: str= Field(max_length=200)

    # adding fields for the work experiece 1
    Company1: str= Field(min_length=3, max_length= 50)
    Position1: str= Field(min_length= 3, max_length= 50)
    Started1: str
    Ended1: str
    Contribution1: str= Field(max_length=700)

    
# developer output data schema 
class Dev_Response(New_Developer):
    model_config= ConfigDict(from_attributes=True)

    Id: UUID 
    Activated_Date: datetime | None
    


# update developer schema
class Update_Developer(BaseModel):
    First_Name: str= Field(min_length=3, max_length=25)
    Last_Name: str= Field(min_length=2, max_length=25)
    Address: str= Field(min_length= 5, max_length= 100)
    Phone: str= Field(max_length=14)
    Email: str= Field(max_length=100)


# update developer work experience 1
class Update_Work1(BaseModel):
    Company1: str= Field(min_length=3, max_length= 50)
    Position1: str= Field(min_length= 3, max_length= 50)
    Started1: str
    Ended1: str
    Contribution1: str= Field(max_length=700)


# new employeer schema
class New_Employeer(Person):
   Employee_ID: str= Field(max_length=15)
   Position: str= Field(min_length=4, max_length=70)


# employeer output data schema
class Employeer_Response(New_Employeer):
    model_config= ConfigDict(from_attributes=True)

    Id: UUID
    Activated_Date: datetime | None



# new post schema
class New_Post(BaseModel):
    Title: str=Field(min_length=5, max_length=70)
    Tag: str
    Question: str=Field(min_length=10, max_length=500) 
    Posted: datetime
    Opened: bool
    Last_Update: datetime

    # enherite values from developer
    author: Dev_Response
    

# post output data schema
class Post_Response(New_Post):
    model_config= ConfigDict(from_attributes=True)

    Id: int


class CompanyResponse(BaseModel):
    Id: UUID
    Company: str
    About: str
    Website: Optional[str] = None
    Country: Optional[str] = None
    State: Optional[str] = None
    City: Optional[str] = None
    Created_Date: datetime
    Image: Optional[str] = None
    Img_Path: str

    class Config:
        from_attributes = True


class JobResponse(BaseModel):
    Id: UUID
    Title: str
    Lang_Requirements: List[str]
    Location: str
    Contract: str
    Duration: str
    Payment_Type: str
    Salary_Start: int
    Salary_End: int
    Other_Requirements: Optional[str] = None
    Description: str
    Benefits: Optional[str] = None
    Status: Optional[str] = None
    Closed: bool
    Posted_Date: datetime
    company_id: UUID
    
    # O NOME DEVE SER EXATAMENTE O DO RELATIONSHIP NO MODEL JOBS
    job_belongs_company: Optional[CompanyResponse] = None

    class Config:
        from_attributes = True