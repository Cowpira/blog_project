from services import authentication, helper, image_utils, auth_settings, http_responses
from routers import send_emails
from post_dao import portfolio_dao, message_dao
from data_model.models import Developer, Work, Person
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload
from datetime import datetime, timezone



# function to list users
async def list_users(db: Session):
    query= select(Developer)

    return db.execute(query).scalars().all()


# function to retrieve 3 random developer from developers in DB
async def get_random_developers(db: Session):
    try:
        query= select(Developer).order_by(func.random()).limit(4)

        result= db.execute(query).scalars().all()
        return result
    except ValueError:
        return http_responses.status_204_no_content("bi bi-clipboard-x-fill", "No developers found!")



# function to create a new developer
async def create_user(new_dev, url_for, bg_task, db: Session):
    title= None
    coding_language= None

    # getting title and coding 
    if new_dev.get("title") != "" and new_dev.get("prog_language") != "":
        title= new_dev.get("title")
        coding_language= new_dev.get("prog_language")
    else:
        title= new_dev.get("input_title")
        coding_language= new_dev.get("input_prog_language")

    
    result= db.execute(select(Person).filter(Person.Email == new_dev.get("email")))
    dev_found= result.scalar()

    # verify if email already registered or password is strong
    if dev_found:
        return http_responses.status_204_no_content("bi bi-envelope-slash-fill", "E-mail already registered!")
    
    elif not auth_settings.strong_password(new_dev.get("password")):
        return http_responses.status_406_not_acceptable("bi bi-file-earmark-lock2-fill", "The password doesn't meet strong password requirements!")
    
    elif new_dev.get("password") != new_dev.get("conf_password"):
        return http_responses.status_406_not_acceptable("bi bi-signpost-split-fill", "'Password' and 'Confirm Password' doesn't match!")

    else:
        if new_dev.get("gender") == "":
            gender= 'U'  
        else: gender= new_dev.get("gender")

        # create an instance of the new developer
        developer= Developer(
            First_Name= new_dev.get("first_name"),
            Last_Name= new_dev.get("last_name"),
            Address= new_dev.get("address"),
            Phone= new_dev.get("phone"),
            Cod_Title= title,
            Cod_Lang= coding_language,
            Years_Exp= new_dev.get("experience"),
            Email= new_dev.get("email"),
            Password= auth_settings.encrypt(new_dev.get("password")),
            Created= datetime.now(timezone.utc),
            Type= 'developer',
            Gender= gender
        )
        
        str_context= Person.get_user_context_str(developer, context= helper.VERIFY_ACCOUNT)
        developer.Token = auth_settings.encrypt(str_context)

        # setting profile image according to developer gender
        if new_dev.get("gender") == "M":
            developer.Image= "male.png"
            developer.Img_Path= "uploaded_dev_images/male.png"
        elif new_dev.get("gender") == "F":
            developer.Image= "female.png"
            developer.Img_Path= "uploaded_dev_images/female.png"
        else:
            developer.Image= "unisex.png"
            developer.Img_Path= "uploaded_dev_images/unisex.png"
        
        # comiting developer into DB
        db.add(developer)
        db.commit()
        db.refresh(developer)

        # calling function to register system message to new employeers
        msg= f'Welcome to Future Programmers <span class="fw-light text-primary"> {developer.First_Name} </span> <br><br> \
            Your account is ready to post questions, answer posts and create your resume profile. <br><br> \
            <b class="text-dark fw-bolder"> Congratulations </b>'
        
        await message_dao.send_message(msg, 'FP System', None, developer.Id, -1, True, db)

        # after we add the new user we save the work position due to relatinship User -> Work
        exp1= Work(
            # getting user ocupation
            Company1= new_dev.get('company'),
            Position1= new_dev.get('position'),
            Started1= new_dev.get('started'),
            Ended1= new_dev.get('ended'),
            Contribution1= new_dev.get('contribution'),
            dev_id= developer.Id
        )

        # comiting work into DB
        db.add(exp1)
        db.commit()
        db.refresh(exp1)

        # calling function to generate and save new token
        token= await authentication.generate_save_new_token(developer.Id, db)
    
        # send email to activate user account
        if  await send_emails.activate_account(developer, token, url_for, bg_task):
            return http_responses.status_200_ok("bi bi-person-badge", 
                                                f"Welcome to Future Programmers {developer.Last_Name} <br> Follow instructios in the e-mail to activate your account")
        else:
            return http_responses.status_503_service_unavailable("bi bi-send-exclamation-fill", 
                                                                 f"Account created but couldn't send activation link <br> Contact support to activate your account!")
    


# function to update developer data
async def update_developer(new_data, cur_user, db: Session):
    try:
        # getting user personal data
        cur_user.First_Name= new_data.get('first_name')
        cur_user.Last_Name= new_data.get('last_name')
        cur_user.Address= new_data.get('address')
        cur_user.Phone= new_data.get('phone')
        cur_user.Email= new_data.get('email')

        # setting profile image according to developer gender
        if cur_user.Gender != new_data.get("gender"):
            cur_user.Gender= new_data.get("gender")

        elif cur_user.Image in ['male.png', 'female.png', 'unisex.png']:
            if new_data.get("gender") == 'M':
                cur_user.Image= "male.png"
                cur_user.Img_Path= "uploaded_dev_images/male.png"

            elif new_data.get("gender") == "F" and 'female' not in cur_user.Img_Path:
                cur_user.Image= "female.png"
                cur_user.Img_Path= "uploaded_dev_images/female.png"
            else:
                cur_user.Image= "unisex.png"
                cur_user.Img_Path= "uploaded_dev_images/unisex.png"


        db.add(cur_user)
        db.commit()
        db.refresh(cur_user)
        
        return http_responses.status_200_ok("bi bi-check2-circle", f"{cur_user.First_Name} your data was successfully updated")
    except ValueError:
        return http_responses.status_500_server_error("bi bi-database-fill-exclamation", "Couldn't update your data. Try again")
    


# function to update developer ocupation
async def update_ocupation(data, dev_id, db: Session):
    # find ocupation according to developer ID
    result= db.execute(select(Work).filter(Work.dev_id == dev_id))
    experience_found= result.scalar()

    # if work experience if found update
    if experience_found:
        experience_found.Company1= data.get('company')
        experience_found.Position1= data.get('position')
        experience_found.Started1= data.get('started')
        experience_found.Ended1= data.get('ended')
        experience_found.Contribution1= data.get('contribution')

        db.add(experience_found)
        db.commit()
        db.refresh(experience_found)
        
        return http_responses.status_200_ok("bi bi-check2-circle", "Ocupation successfully updated")
    else:
        return http_responses.status_404_not_found("bi bi-ban", "Ocupation not found")
    


# function to update developer programming level
async def update_coding_level(cur_user, user_data, db: Session):
    try:
        # setting developer coding level
        cur_user.Cod_Title= user_data.get('cod_title')
        cur_user.Cod_Lang= user_data.get('cod_lang')
        cur_user.Years_Exp= user_data.get('years_exp')

        db.add(cur_user)
        db.commit()
        db.refresh(cur_user)
        
        return http_responses.status_200_ok("bi bi-check2-circle", "Code level successfully updated")
    except ValueError:
        return http_responses.status_500_server_error("bi bi-database-fill-exclamation", "Coding level couldn't be updated!")
    


# function to delete developer account
def delete(cur_user, db: Session):
    if cur_user:
        db.delete(cur_user, synchronize_session=False)
        db.commit()
        return http_responses.status_200_ok("bi bi-check2-circle", "Your account was successfully removed")
    else:
        return http_responses.status_401_unauthorized("bi bi-person-fill-slash", "You're not authorized to do this action!")



# function to get developer data from user in session
async def developer_by_id(dev_id, db: Session):
    try:
        query= select(Developer).filter(Developer.Id == dev_id)
        dev_found= db.execute(query).scalar()
        return dev_found
    except ValueError:
        return http_responses.status("", f"Developer with {dev_id} don't exist!")



# function to search a developer by name or email
async def search_user(param, db: Session):
    search_param= f"%{param}%"

    query= select(Developer, Work.Company1.label("work_company")) \
    .join(Work, Developer.Id == Work.dev_id).filter(
        or_(
            Developer.First_Name.ilike(search_param),
            Developer.Email.ilike(search_param),
            Developer.Cod_Title.ilike(search_param),
            Developer.Cod_Lang.ilike(search_param),
            Work.Company1.ilike(search_param)
            
        )
    )
    return db.execute(query).scalars().all()



# function to activate developer account
async def activate_developer_account(context, email, bg_task, db: Session):
    dev_account = auth_settings.load_user(email, db)
    
    if dev_account:
        # verify if account is active    
        if dev_account.Active:
                return 'activated'
        elif not auth_settings.verify_pass(context, dev_account.Token):
            # verify if token is valid
            return 'TK'
        else:
            dev_account.Active= True
            dev_account.Activated_Date= datetime.now(timezone.utc)

            db.add(dev_account)
            db.commit()
            db.refresh(dev_account)

            #sending confirmation email
            await send_emails.activate_success(dev_account, bg_task)
            return 'success'
    else:
        return 'DB' # account not found



# function to deactivate developer account
async def deactivate(cur_user, bg_task, db: Session):
    query= select(Person).where(Person.Email == cur_user.Email)
    user_found= db.execute(query).scalar()

    if user_found:
        user_found.Active= False
        user_found.Deactivated_Date= datetime.now(timezone.utc)

        #send email to activate developer account
        if await send_emails.deactivate_account(user_found, bg_task):
            db.add(user_found)
            db.commit()
            db.refresh(user_found)

            return http_responses.status_301_moved_permanently("bi bi-clock-history", "We're sad that you left. Account deactivated")
        else:
            return http_responses.status_500_server_error("bi bi-envelope-exclamation", "Couldn't deactivate your account. Try again!")
    else:
        return http_responses.status_404_not_found("bi bi-person-fill-exclamation", "Could not deactiated account!")



# function to update developer password
async def developer_update_password(cur_user, user_data, bg_task, db:Session):
    # verify if current password is valid
    if not auth_settings.verify_pass(user_data.get("cur_password"), cur_user.Password):
        return http_responses.status_404_not_found("bi bi-exclamation-diamond-fill", "Current password is not valid!")
    
    elif not auth_settings.strong_password(user_data.get("new_password")):
        return http_responses.status_406_not_acceptable("bi bi-file-earmark-lock2-fill", "New password doesn't meet strong password requirements!")
    
    elif not user_data.get("new_password") == user_data.get("conf_password"):
        return http_responses.status_406_not_acceptable("bi bi-file-earmark-lock2-fill", "'New Password' doesn't match 'Confirm Password'!")
    else:
        # resetting developer password into DB
        cur_user.Password= auth_settings.encrypt(user_data.get("new_password"))
        db.add(cur_user)
        db.commit()
        db.refresh(cur_user)

        # sending recover password email
        if await send_emails.password_updated(cur_user, bg_task) is ValueError:
            
            return http_responses.status_503_service_unavailable("bi bi-send-exclamation-fill", 
                                                                "Password not updated, couldn't send confirmation email <br> Try again later!")
        else:
            return http_responses.status_200_ok("bi bi-check2-circle", "Password successfully updated")
        


# function to delete developer profile image
async def delet_profile_picture(cur_user, db):
    old_img= cur_user.Image

    if not cur_user.Image:
        return http_responses.status_400_bad_request("bi bi-person-exclamation", "No profile picture to delete!")
    

    if not old_img in ['male.png', 'female.png', 'unisex.png']:
        cur_user.Image= 'unisex.png'
        db.commit()
        db.refresh(cur_user)

        # delete old profile image
        
        if image_utils.image_deletion(old_img, image_utils.DEV_IMG_DIR, cur_user, db):
            return http_responses.status_200_ok("bi bi-aspect-ratio", "Profile image successfully removed")

    return http_responses.status_406_not_acceptable("bi bi-person-bounding-box", "Fefault profile image cannot be deleted!!")