import os
from services import email_settings


APP_NAME: str= "Future Programmers"
WEBSITE_URL: str| None= os.environ.get('website_url')
FP_IMG_URL: str| None= os.environ.get('fp_img_url')


def email_data(user, url_link, image):
    data= {
        'app_name': APP_NAME,
        'user_name': user.First_Name,
        'user_type': user.Type,
        'url_link': url_link,
        'icon_img': image,
        'fp_logo': FP_IMG_URL + 'future_prog.png'
    }
    return data



# method to send activation email to user or employee
async def activate_account(user, token, url_for, bg_task):
    # image for the emal template
    if user.Type == "developer":
        icon_img= FP_IMG_URL + 'programmers.png'
    else:
        icon_img= FP_IMG_URL + 'new_employeer.png'

    activate_url= url_for("request_activate_account", user_id=user.Id, token=token)

    try:
        email_settings.send_email(
            recipients= [user.Email],
            subject= f'Account Activation Request - {APP_NAME}',
            template_name= 'emails/account_activation.html',
            context= email_data(user, activate_url, icon_img), 
            bg_task= bg_task
        )
        return True
    except ValueError as error:
        return error



# method to send congratulations email 
async def activate_success(user, bg_task):
    link= f'{WEBSITE_URL}/home'

    #cehck if the object is a user or employee
    if user.Type == 'developer':
        icon_img= FP_IMG_URL + 'user_success.png'
        email_template= 'emails/success_activated_user.html'
    else:
        icon_img= FP_IMG_URL + 'employee_success.png'
        email_template= 'emails/success_activated_employee.html'
        await register_your_company(user, bg_task)

    try:
        email_settings.send_email(
            recipients= [user.Email],
            subject= f'Account Activated Successfully - {APP_NAME}',
            template_name= email_template,
            context= email_data(user, link, icon_img),
            bg_task= bg_task
        )
        return True
    except ValueError as error:
        return error



# method to send verufication email 
async def deactivate_account(user, bg_task):
    activate_url= f'{WEBSITE_URL}/contact'
    
    # image for the emal template
    icon_img= FP_IMG_URL + 'deactivate.png'

    try:
        email_settings.send_email(
            recipients= [user.Email],
            subject= f'Account Deactivated - {APP_NAME}',
            template_name= 'emails/account_deactivation.html',
            context= email_data(user, activate_url, icon_img),
            bg_task= bg_task
        )
        return True
    except ValueError as error:
        return error



# method to send recover email password
async def recover_password_link(url, token, user_obj, bg_task):
    #recover_password link
    reset_url= url("verifying_user", user_email=user_obj.Email, token= token)
    
    # image for the emal template
    icon_img= FP_IMG_URL + 'reset-password.png'
    
    try:
        email_settings.send_email(
            recipients= [user_obj.Email],
            subject= f'Reset Password - {APP_NAME}',
            template_name= 'emails/recorver_password.html',
            context= email_data(user_obj,reset_url, icon_img),
            bg_task= bg_task
        )
        return True
    except ValueError as error:
        return error



# method to send message password updated
async def password_updated(user, bg_task):
    link= f'{WEBSITE_URL}/home'

    # image for the emal template
    icon_img= FP_IMG_URL + 'password_reseted.png'

    try:
        email_settings.send_email(
            recipients= [user.Email],
            subject= f'Password Updated Successfully - {APP_NAME}',
            template_name= 'emails/password_updated.html',
            context= email_data(user, link, icon_img),
            bg_task= bg_task
        )
        return True
    except ValueError as error:
        return error



# method to send user contact email
async def user_contact(data, bg_task):
    sender= 'celio_cali@icloud.com'

    content= {
        'app_name': APP_NAME,
        'url_link': WEBSITE_URL,
        'fp_logo': FP_IMG_URL + 'future_prog.png',
        'user_name': data.get('first_name'),
        'topic': data.get('contact_topic'),
        'phone': data.get('phone'),
        'email': data.get('email-address'),
        'message': data.get('message'),
        # image for the emal template
        'icon_img': FP_IMG_URL + 'chat-box.png'
    }
   
    try:
        email_settings.send_email(
            recipients= [data.get('email-address'), sender],
            subject= f'Contact Reveived - {APP_NAME}',
            template_name= 'emails/user_contact.html',
            context= content,
            bg_task= bg_task
        )
        return True
    except ValueError as error:
        return error

    

# function to send email for employee to register the company
async def register_your_company(employeer, bg_task):
    link= f'{WEBSITE_URL}/home'

    # image for the emal template
    icon_img= FP_IMG_URL + 'company.png'
    email_template= 'emails/register_company.html'

    try:
        email_settings.send_email(
            recipients= [employeer.Email],
            subject= f'Register your Company - {APP_NAME}',
            template_name= email_template,
            context= email_data(employeer, link, icon_img),
            bg_task= bg_task
        )
        return True
    except ValueError as error:
        return error