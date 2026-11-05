# for older python versions to accept forwarding class references
from __future__ import annotations 
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy import JSON, DateTime, ForeignKey, Integer, Numeric, String, Boolean, Text, Uuid
from sqlalchemy.orm import relationship, Mapped, mapped_column
from services.db_connection import Base, engine
from typing import List
import uuid


# BASE CLASS PERSON (parant class for developers & employees)
class Person(Base):
    __tablename__= 'person'

    Id: Mapped[uuid.UUID]= mapped_column(Uuid(as_uuid=True), primary_key= True, nullable=False, index=True, default=uuid.uuid4)
    First_Name: Mapped[str]= mapped_column(String(25), nullable= False)
    Last_Name: Mapped[str]= mapped_column(String(25))
    Phone: Mapped[str]= mapped_column(String(14)) 
    Email: Mapped[str]= mapped_column(String(70), nullable= False, unique= True)
    Password: Mapped[str]= mapped_column(String(200), nullable= False)  
    Token: Mapped[str]= mapped_column(String(100))
    Active: Mapped[bool]= mapped_column(Boolean, default= False)
    Activated_Date: Mapped[datetime]= mapped_column(DateTime(timezone=True), nullable= True)
    Deactivated_Date: Mapped[datetime]= mapped_column(DateTime(timezone= True), nullable=True)
    Created: Mapped[datetime]= mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    Total_Messages: Mapped[int]= mapped_column(Integer, default= 0)

    # try to refactor the code to eliminated that method and use the same method in user
    def get_user_context_str(self, context: str):
        if self.Created:
            return f"{context}{self.Password[-6:]}{self.Created.strftime('%m%d%Y%H%M%S')}".strip()
    

    # discriminator column for person type
    Type: Mapped[str]= mapped_column(String(10))
    __mapper_args__={
        "polymorphic_on": Type,
        "polymorphic_identity": 'person'
    }

    # relationships one to many
    answers: Mapped[List["Answer"]]= relationship(back_populates= "write_answer", cascade= "all, delete-orphan")
    messages: Mapped[List["Message"]]= relationship(back_populates= "msg_sender", cascade= "all, delete-orphan")
    login_track: Mapped[List["Login_Track"]]= relationship(back_populates= "users_login")
    login_errors_track: Mapped[List["Login_Errors_Track"]]= relationship(back_populates= "login_tries")
    reset_tokens: Mapped[List["Password_Reset_Token"]]= relationship(back_populates= "user", cascade= "all, delete-orphan")


# USERS TABLE
class Developer(Person):
    __tablename__= "developer"
    
    Id: Mapped[uuid.UUID]= mapped_column(ForeignKey("person.Id"), primary_key= True, index=True, nullable= False)
    Address: Mapped[str]= mapped_column(String(50))
    Has_Resume: Mapped[bool]= mapped_column(Boolean, default= False)
    Cod_Title: Mapped[str]= mapped_column(String(100))
    Cod_Lang: Mapped[str]= mapped_column(String(100))
    Years_Exp: Mapped[int]= mapped_column(Integer)
    Gender: Mapped[str]= mapped_column(String(1), default='U')
    Image: Mapped[str]= mapped_column(String(200), nullable= True, default= None)
    Img_Path: Mapped[str]= mapped_column(String(100))
       

    # defining the polymorphism from class model Person
    __mapper_args__={ "polymorphic_identity": "developer" }

    # relationships one to many
    posts: Mapped[List["Post"]]= relationship(back_populates= "author", cascade= "all, delete-orphan")
    responses: Mapped[List["Response"]]= relationship(back_populates= "write_response", cascade= "all, delete-orphan")

    # defining Education, Certification, Front-End, Back-End, Database, Cloud, Work, Project, Post, Answer, Response relationships
    educations: Mapped[List["Education"]]= relationship(back_populates= "write_education", cascade= "all, delete-orphan")
    certifications: Mapped["Certification"]= relationship(back_populates= "write_certification", cascade= "all, delete-orphan")
    front_end: Mapped["Front_End"]= relationship(back_populates= "write_frontend", cascade= "all, delete-orphan")
    back_ends: Mapped["Back_End"]= relationship(back_populates= "write_backend", cascade= "all, delete-orphan")
    databases: Mapped["Database"]= relationship(back_populates= "write_database", cascade= "all, delete-orphan")
    clouds: Mapped["Cloud"]= relationship(back_populates= "write_cloud", cascade= "all, delete-orphan")
    works: Mapped["Work"]= relationship(back_populates= "write_work", cascade= "all, delete-orphan")
    projects: Mapped["Project"]= relationship(back_populates= "write_project", cascade= "all, delete-orphan")
    applicant_dev: Mapped[List["Job_Application"]]= relationship(back_populates= "dev_applied", cascade= "all, delete-orphan")
    


# EDUCATION TABLE
class Education(Base):
    __tablename__= "educations"

    Id: Mapped[uuid.UUID]= mapped_column(Uuid(as_uuid=True), primary_key= True, index=True, nullable=False, default=uuid.uuid4)
    School: Mapped[str]= mapped_column(String(100), nullable= False)
    Education_Type: Mapped[str]= mapped_column(String(70), nullable= False)
    Graduated_At: Mapped[str]= mapped_column(String(70))
    Grad_Status: Mapped[str]= mapped_column(String(20))
    New_Education: Mapped[str]= mapped_column(String(1200))

    # defining Education & User relationship
    dev_id: Mapped[uuid.UUID]= mapped_column(ForeignKey("developer.Id"), nullable= False, index=True)
    write_education: Mapped["Developer"]= relationship(back_populates= "educations")



# CERTIFICATION TABLE
class Certification(Base):
    __tablename__= "certifications"

    Id: Mapped[uuid.UUID]= mapped_column(Uuid(as_uuid=True), primary_key= True, index=True, nullable=False, default=uuid.uuid4)
    Certification1: Mapped[str]= mapped_column(String(60))
    Cert1_Date: Mapped[str]= mapped_column(String(10))

    Certification2: Mapped[str]= mapped_column(String(60))
    Cert2_Date: Mapped[str]= mapped_column(String(10))

    Certification3: Mapped[str]= mapped_column(String(60))
    Cert3_Date: Mapped[str]= mapped_column(String(10))

    # defining Certification & User relationship
    dev_id: Mapped[uuid.UUID]= mapped_column(ForeignKey("developer.Id"), nullable= False, index=True, unique=True)
    write_certification: Mapped["Developer"]= relationship(back_populates= "certifications")



# FRONT-END TABLE
class Front_End(Base):
    __tablename__= "front_end"

    Id: Mapped[uuid.UUID]= mapped_column(Uuid(as_uuid=True), primary_key= True, index=True, nullable=False, default=uuid.uuid4)
    Frontend_Lang1: Mapped[str]= mapped_column(String(60))
    Exp_Frontend1: Mapped[int]= mapped_column(Integer)

    Frontend_Lang2: Mapped[str]= mapped_column(String(60))
    Exp_Frontend2: Mapped[int]= mapped_column(Integer)

    Frontend_Lang3: Mapped[str]= mapped_column(String(60))
    Exp_Frontend3: Mapped[int]= mapped_column(Integer)

    # defining Front-End & User relationship
    dev_id: Mapped[uuid.UUID]= mapped_column(ForeignKey("developer.Id"), nullable= False, index=True, unique=True)
    write_frontend: Mapped["Developer"]= relationship(back_populates= "front_end")



# BACK-END TABLE
class Back_End(Base):
    __tablename__= "back_ends"

    Id: Mapped[uuid.UUID]= mapped_column(Uuid(as_uuid=True), primary_key= True, index=True, nullable=False, default=uuid.uuid4)
    Backend_Lang1: Mapped[str]= mapped_column(String(100))
    Exp_Backend1: Mapped[int]= mapped_column(Integer)

    Backend_Lang2: Mapped[str]= mapped_column(String(100))
    Exp_Backend2: Mapped[int]= mapped_column(Integer)

    Backend_Lang3: Mapped[str]= mapped_column(String(100))
    Exp_Backend3: Mapped[int]= mapped_column(Integer)

    # defining Front-End & User relationship
    dev_id: Mapped[uuid.UUID]= mapped_column(ForeignKey("developer.Id"), nullable= False, index=True, unique=True)
    write_backend: Mapped["Developer"]= relationship(back_populates= "back_ends")



# DATABASE TABLE
class Database(Base):
    __tablename__= "databases"

    Id: Mapped[uuid.UUID]= mapped_column(Uuid(as_uuid=True), primary_key= True, index=True, nullable=False, default=uuid.uuid4)
    Database1: Mapped[str]= mapped_column(String(60))
    Exp_Database1: Mapped[int]= mapped_column(Integer)

    Database2: Mapped[str]= mapped_column(String(60))
    Exp_Database2: Mapped[int]= mapped_column(Integer) 

    Database3: Mapped[str]= mapped_column(String(60))
    Exp_Database3: Mapped[int]= mapped_column(Integer)

    # defining Database & User relationship
    dev_id: Mapped[uuid.UUID]= mapped_column(ForeignKey("developer.Id"), nullable= False, index=True, unique=True)
    write_database: Mapped["Developer"]= relationship(back_populates= "databases")



# CLOUD TABLE
class Cloud(Base):
    __tablename__= "clouds"

    Id: Mapped[uuid.UUID]= mapped_column(Uuid(as_uuid=True), primary_key= True, index=True, nullable=False, default=uuid.uuid4)
    Cloud1: Mapped[str]= mapped_column(String(60))
    Exp_Cloud1: Mapped[int]= mapped_column(Integer)

    Cloud2: Mapped[str]= mapped_column(String(60))
    Exp_Cloud2: Mapped[int]= mapped_column(Integer)

    Cloud3: Mapped[str]= mapped_column(String(60))
    Exp_Cloud3: Mapped[int]= mapped_column(Integer)

    # column to add others skills
    Other_Skills: Mapped[str]= mapped_column(String(300))

    # defining Database & User relationship
    dev_id: Mapped[uuid.UUID]= mapped_column(ForeignKey("developer.Id"), nullable= False, index=True, unique=True)
    write_cloud: Mapped["Developer"]= relationship(back_populates= "clouds")



# WORK TABLE
class Work(Base):
    __tablename__= "works"
    
    Id: Mapped[uuid.UUID]= mapped_column(Uuid(as_uuid=True), primary_key= True, index=True, nullable=False, default=uuid.uuid4)
    Company1: Mapped[str]= mapped_column(String(100))
    Position1: Mapped[str]= mapped_column(String(100))
    Started1: Mapped[str]= mapped_column(String(10))
    Ended1: Mapped[str]= mapped_column(String(10))
    Contribution1: Mapped[str]= mapped_column(String(500)) 

    Company2: Mapped[str | None]= mapped_column(String(100), nullable=True)
    Position2: Mapped[str | None]= mapped_column(String(100), nullable=True)
    Started2: Mapped[str | None]= mapped_column(String(10), nullable=True)
    Ended2: Mapped[str | None]= mapped_column(String(10), nullable=True)
    Contribution2: Mapped[str | None]= mapped_column(String(500), nullable=True)

    Company3: Mapped[str | None]= mapped_column(String(100), nullable=True)
    Position3: Mapped[str | None]= mapped_column(String(100), nullable=True)
    Started3: Mapped[str | None]= mapped_column(String(10), nullable=True)
    Ended3: Mapped[str | None]= mapped_column(String(10), nullable=True)
    Contribution3: Mapped[str | None]= mapped_column(String(500), nullable=True)

    # defining Work & User relationship
    dev_id: Mapped[uuid.UUID]= mapped_column(ForeignKey("developer.Id"), nullable= False, index=True, unique=True)
    write_work: Mapped["Developer"]= relationship(back_populates= "works")



# PROJECT TABLE
class Project(Base):
    __tablename__= "projects"

    Id: Mapped[uuid.UUID]= mapped_column(Uuid(as_uuid=True), primary_key= True, index=True, nullable=False, default=uuid.uuid4)
    Project1: Mapped[str]= mapped_column(String(60))
    Link1: Mapped[str]= mapped_column(String(100)) 
    Prj_Desc1: Mapped[str]= mapped_column(String(300)) 

    Project2: Mapped[str]= mapped_column(String(60)) 
    Link2: Mapped[str]= mapped_column(String(100)) 
    Prj_Desc2: Mapped[str]= mapped_column(String(300)) 

    Project3: Mapped[str]= mapped_column(String(60)) 
    Link3: Mapped[str]= mapped_column(String(100)) 
    Prj_Desc3: Mapped[str]= mapped_column(String(300))

    # defining Project & User relationship
    dev_id: Mapped[uuid.UUID]= mapped_column(ForeignKey("developer.Id"), nullable= False, index=True, unique=True)
    write_project: Mapped["Developer"]= relationship(back_populates= "projects")



# POSTS TABLE
class Post(Base):
    __tablename__ = "posts"

    Id: Mapped[uuid.UUID]= mapped_column(Uuid(as_uuid=True), primary_key= True, index=True, nullable=False, default=uuid.uuid4)
    Title: Mapped[str]= mapped_column(String(70))
    Tag: Mapped[List[str]]= mapped_column(JSON, default="")
    Question: Mapped[str]= mapped_column(Text)
    Posted: Mapped[datetime | None]= mapped_column(DateTime(timezone=True), nullable= True)
    Opened: Mapped[bool]= mapped_column(Boolean, default= True)
    Last_Update: Mapped[datetime | None]= mapped_column(DateTime(timezone=True), nullable= True)
    Closed_Date: Mapped[datetime | None]= mapped_column(DateTime(timezone=True), nullable=True)
    Total_Answer: Mapped[int]= mapped_column(Integer, default=0)

    # defining User & Post relationship
    dev_id: Mapped[uuid.UUID]= mapped_column(ForeignKey("developer.Id"), nullable= False, index=True)
    author: Mapped["Developer"]= relationship(back_populates= "posts") 

    # defining User & Answer relationship
    answer_post: Mapped[List["Answer"]]= relationship("Answer", back_populates= "comment", cascade= "all, delete-orphan")
    

# ANSWERS TABLE
class Answer(Base):
    __tablename__ = "answers"

    Id: Mapped[uuid.UUID]= mapped_column(Uuid(as_uuid=True), primary_key= True, index=True, nullable=False, default=uuid.uuid4)
    Tag: Mapped[List[str]]= mapped_column(JSON, default="")
    Answer: Mapped[str]= mapped_column(Text, nullable= False)
    Posted: Mapped[datetime]= mapped_column(DateTime(timezone=True), nullable=True)
    Good: Mapped[str | None]= mapped_column(String(1), nullable=True)

    # defining Answer & Post relationship
    post_id: Mapped[uuid.UUID]= mapped_column(ForeignKey("posts.Id"), nullable= False, index=True)
    comment: Mapped["Post"]= relationship(back_populates= "answer_post")

    # defining Answer & User relationship
    dev_id: Mapped[uuid.UUID]= mapped_column(ForeignKey("person.Id"), nullable= False, index=True)
    write_answer: Mapped["Person"]= relationship(back_populates= "answers")

    # defining Answer & Response relationship
    reply_to_answer: Mapped[List["Response"]]= relationship(back_populates= "comment_response", cascade= "all, delete-orphan")



# RESPONSES TABLE
class Response(Base):
    __tablename__ = "responses"

    Id: Mapped[uuid.UUID]= mapped_column(Uuid(as_uuid=True), primary_key= True, index=True, nullable=False, default=uuid.uuid4)
    Tag: Mapped[List[str]]= mapped_column(JSON, default="")
    Response: Mapped[str]= mapped_column(Text, nullable= False)
    Posted: Mapped[datetime | None]= mapped_column(DateTime(timezone=True), nullable=True)

    # defining Response & Answer relationship
    answer_id: Mapped[uuid.UUID]= mapped_column(ForeignKey("answers.Id"), nullable= False, index=True)
    comment_response: Mapped["Answer"]= relationship(back_populates= "reply_to_answer")

    # defining Response & Developer relationship
    dev_id: Mapped[uuid.UUID]= mapped_column(ForeignKey("developer.Id"), nullable= False, index=True)
    write_response: Mapped["Developer"]= relationship(back_populates= "responses")



# EMPLOYEES TABLE
class Employee(Person):
    __tablename__= "employeer"

    Id: Mapped[uuid.UUID]= mapped_column(ForeignKey("person.Id"), index=True, primary_key= True, nullable= False)
    Employee_Id: Mapped[str]= mapped_column(String(15), nullable= False)
    Position: Mapped[str]= mapped_column(String(50))
    Work_At: Mapped[str | None]= mapped_column(String(50), nullable=True)

    # defining Jobs relationships
    jobs: Mapped[List["Jobs"]]= relationship(back_populates= "add_job", cascade= "all, delete-orphan")
    company: Mapped["Company"]= relationship(back_populates= "work_for", cascade= "all, delete-orphan")

    # defining the polymorphism from class model Person
    __mapper_args__={ "polymorphic_identity": "employeer" }



# JOBS TABLE
class Company(Base):
    __tablename__= "company"

    Id: Mapped[uuid.UUID]= mapped_column(Uuid(as_uuid=True), nullable=False, index=True, primary_key= True, default=uuid.uuid4)
    Company: Mapped[str|None]= mapped_column(String(50), unique= True, nullable= False)
    About: Mapped[str]= mapped_column(Text)
    Website: Mapped[str | None]= mapped_column(String(100), unique= True)
    Country: Mapped[str | None]= mapped_column(String(70), nullable=True)
    State: Mapped[str | None]= mapped_column(String(70), nullable=True)
    City: Mapped[str | None]= mapped_column(String(100), nullable=True)
    Created_Date: Mapped[datetime]= mapped_column(DateTime(timezone= True), nullable= False, default=lambda: datetime.now(timezone.utc))

    Image: Mapped[str | None]= mapped_column(String(200), nullable= True, default= None)
    Img_Path: Mapped[str]= mapped_column(String(100))
    
    # defining Jobs relationships
    jobs: Mapped[List["Jobs"]]= relationship(back_populates= "job_belongs_company", cascade= "all, delete-orphan")
    
    # defining Company & Employee relationship
    employee_id: Mapped[uuid.UUID]= mapped_column(ForeignKey("employeer.Id"), nullable= False, index=True)
    work_for: Mapped["Employee"]= relationship(back_populates= "company") 



# MESSAGES TABLE TO LIST USERS AND EMPLOYEE
class Message(Base):
    __tablename__= "messages"

    Id: Mapped[uuid.UUID]= mapped_column(Uuid(as_uuid=True), primary_key= True, index=True, nullable=False, default=uuid.uuid4)
    Message_Content: Mapped[str]= mapped_column(Text, nullable= False)
    Send_Date: Mapped[datetime]= mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    System_Message: Mapped[bool]= mapped_column(Boolean, default= False)
    Viewed: Mapped[bool]= mapped_column(Boolean, default=False)
    To: Mapped[uuid.UUID]= mapped_column(Uuid(as_uuid=True), nullable= False)

    # defining Answer & User relationship
    Person_Id: Mapped[uuid.UUID | None]= mapped_column(ForeignKey("person.Id"), index=True)
    msg_sender: Mapped["Person"]= relationship(back_populates= "messages")

    Parent_Id: Mapped[uuid.UUID]= mapped_column(ForeignKey("messages.Id"), nullable=True)
    
    replies: Mapped[List["Message"]]= relationship("Message", back_populates="parent_msg", cascade="all, delete-orphan")
    parent_msg: Mapped[List["Message"]]= relationship("Message", back_populates="replies", remote_side=[Id])



# JOBS TABLE
class Jobs(Base):
    __tablename__= "jobs"

    Id: Mapped[uuid.UUID]= mapped_column(Uuid(as_uuid=True), primary_key= True, index=True, nullable=False, default=uuid.uuid4)
    Title: Mapped[str]= mapped_column(String(70))
    Lang_Requirements: Mapped[List[str]]= mapped_column(JSON, default="")
    Location: Mapped[str]= mapped_column(String(10))
    Contract: Mapped[str]= mapped_column(String(5))
    Duration: Mapped[str]= mapped_column(String(10), default='Full-Time', nullable=False)
    Payment_Type: Mapped[str]= mapped_column(String(10))
    Salary_Start: Mapped[Decimal]= mapped_column(Numeric(precision=9, scale=2))
    Salary_End: Mapped[Decimal]= mapped_column(Numeric(precision=9, scale=2))
    Other_Requirements: Mapped[str]= mapped_column(String(1000), nullable=True)
    Description: Mapped[str]= mapped_column(String(2000), nullable=False)
    Benefits: Mapped[str]= mapped_column(String(1000), nullable=True)
    Status: Mapped[str]= mapped_column(String(100), nullable=True) 
    Closed: Mapped[bool]= mapped_column(Boolean, default=False)
    Posted_Date: Mapped[datetime]= mapped_column(DateTime(timezone= True), nullable= False, default=lambda: datetime.now(timezone.utc))
    
    # defining Response & User relationship
    employeer_id: Mapped[uuid.UUID]= mapped_column(ForeignKey("employeer.Id"), nullable= False, index=True)
    add_job : Mapped["Employee"]= relationship(back_populates= "jobs")

    company_id: Mapped[uuid.UUID]= mapped_column(ForeignKey("company.Id"), nullable= False)
    job_belongs_company: Mapped["Company"]= relationship(back_populates="jobs")

    # defining Jobs relationships
    job_application: Mapped[List["Job_Application"]]= relationship(back_populates= "application_job", cascade= "all, delete-orphan")



# JOB APLICANTS TABLE
class Job_Application(Base):
    __tablename__= "jobs_application"

    Id: Mapped[uuid.UUID]= mapped_column(Uuid(as_uuid=True), primary_key= True, index=True, nullable=False, default=uuid.uuid4)
    Applied_Date: Mapped[datetime]= mapped_column(DateTime(timezone= True), nullable= False, default=lambda: datetime.now(timezone.utc))

    job_id: Mapped[uuid.UUID]= mapped_column(Uuid(as_uuid=True), ForeignKey("jobs.Id", ondelete="CASCADE"), nullable= False, index=True)
    application_job: Mapped["Jobs"]= relationship(back_populates="job_application")

    dev_id: Mapped[uuid.UUID]= mapped_column(Uuid(as_uuid=True), ForeignKey("developer.Id", ondelete="CASCADE"), nullable=False, index=True)
    dev_applied: Mapped["Developer"]= relationship(back_populates="applicant_dev")



# TRACK LOGIN TABLE
class Login_Track(Base):
    __tablename__= 'login_track'

    Id: Mapped[uuid.UUID]= mapped_column(Uuid(as_uuid=True), primary_key= True, index=True, nullable=False, default=uuid.uuid4)
    Ip_Address: Mapped[str]= mapped_column(String(30), nullable= False)
    Login_Location: Mapped[str]= mapped_column(String(50))
    Login_DateTime: Mapped[datetime]= mapped_column(DateTime(timezone= True), nullable= False, default=lambda: datetime.now(timezone.utc))

    # defining Login Track & User relationship
    user_id: Mapped[uuid.UUID]= mapped_column(ForeignKey("person.Id"), nullable= False)
    users_login: Mapped[List["Person"]]= relationship(back_populates= "login_track")



# TRACKING LOGIN ERROR TRIES
class Login_Errors_Track(Base):
    __tablename__= 'login_errors_track'

    Id: Mapped[uuid.UUID]= mapped_column(Uuid(as_uuid=True), primary_key= True, index=True, nullable=False, default=uuid.uuid4)
    Login_Tries: Mapped[int]= mapped_column(Integer, default= 0, nullable= False)

    # defining Login Track & User relationship
    user_id: Mapped[uuid.UUID]= mapped_column(ForeignKey("person.Id"), nullable= False)
    login_tries: Mapped[List["Person"]]= relationship(back_populates= "login_errors_track")



# PASSWORD RESET TABLE
class Password_Reset_Token(Base):
    __tablename__= 'password_reset_tokens'

    Id: Mapped[uuid.UUID]= mapped_column(Uuid(as_uuid=True), primary_key= True, nullable=False, index= True, default=uuid.uuid4)
    User_Id: Mapped[uuid.UUID]= mapped_column(ForeignKey("person.Id"), nullable= False)
    Token_Hash: Mapped[str]= mapped_column(String(64), unique= True, nullable= False)
    Expires_At: Mapped[datetime]= mapped_column(DateTime(timezone= True), nullable= False)
    Created_At: Mapped[datetime]= mapped_column(DateTime(timezone= True), default= lambda: datetime.now(timezone.utc))

    user: Mapped["Person"]= relationship(back_populates= "reset_tokens")



# command to create DB and all tables
Base.metadata.create_all(engine)