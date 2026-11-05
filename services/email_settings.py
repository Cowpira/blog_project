import os
import dotenv
from pathlib import Path
from fastapi import BackgroundTasks
from fastapi_mail import FastMail, MessageSchema, MessageType, ConnectionConfig
from pydantic import SecretStr

#loading env file
dotenv.load_dotenv()

# setting variables with .env values
email= os.environ.get('EMAIL')
password= os.getenv('EMAIL_PASSWORD')


conf= ConnectionConfig(
    #email authentications
    MAIL_FROM= str(email),
    MAIL_USERNAME= str(email),
    MAIL_PASSWORD= SecretStr(str(password)),
    MAIL_FROM_NAME= "Future Programmers",

    #email provider config
    MAIL_PORT= 587,
    MAIL_SERVER= 'mail.deliveryti.com',

    #email security
    MAIL_STARTTLS= False,
    MAIL_SSL_TLS= False,
    VALIDATE_CERTS= True,

    #email settings main folder
    TEMPLATE_FOLDER= Path(__file__).parent.parent / 'templates',
)

fm= FastMail(conf)

#method to send emails
def send_email(recipients: list, subject: str, template_name: str, context: dict, bg_task: BackgroundTasks):
    
    message= MessageSchema(
        subject= subject,
        recipients= recipients,
        template_body= context,
        subtype= MessageType.html
    )
    bg_task.add_task(fm.send_message, message, template_name= template_name)