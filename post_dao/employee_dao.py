from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.orm import Session
from data_model.models import Company, Employee, Person
from services import authentication, auth_settings, helper, http_responses
from routers import send_emails
from post_dao import message_dao


# function to create new employeer
async def create_employeer(new_employee, url_for, db: Session, bg_task):
   
    # check if employee email already exist in DB
    employee_found= await auth_settings.load_user(new_employee.get("email"), db)
  
    if employee_found:
        return http_responses.status_302_found("bi bi-envelope-slash-fill", "E-mail already registered!")
    
    elif not auth_settings.strong_password(new_employee.get("password")):
        return http_responses.status_406_not_acceptable("bi bi-file-earmark-lock2-fill", "The password doesn't meet strong password requirements!")
    
    elif new_employee.get("password") != new_employee.get("conf_password"):
        return http_responses.status_406_not_acceptable("bi bi-signpost-split-fill", "'Password' and 'Confirm Password' doesn't match!")
        
    else:
        # create an new employee instance
        employee= Employee(
            Employee_Id= new_employee.get("employee_id"),
            Position= new_employee.get("position"),
            First_Name= new_employee.get("first_name"),
            Last_Name= new_employee.get("last_name"),
            Phone= new_employee.get("phone"), 
            Email= new_employee.get("email"),
            Password= auth_settings.encrypt(new_employee.get("password")),
            Created= datetime.now(timezone.utc),
            Total_Messages= 0,
            Type= 'employeer'
        )

        # generating a secret token
        str_context= Person.get_user_context_str(employee, context= helper.VERIFY_ACCOUNT)
        employee.Token = auth_settings.encrypt(str_context)

        db.add(employee)
        db.commit()
        db.refresh(employee)

        # calling function to register system message to new employeers
        msg= f'Welcome to Future Programmers <span class="fw-light text-primary" {employee.First_Name} </span> <br> \
            Now you' +"'"+ 're ready to register the company <br> \
            Then you can start posting the positions available <br> <br> \
            <b clas="text-dark fw-bolder"> Thanks <b>'
        
        await message_dao.send_message(msg, 'FP System', None, employee.Id, -1, True, db)

        # calling function to generate and save new token
        token= await authentication.generate_save_new_token(employee.Id, db)
        
        # send email to activate employee account
        if await send_emails.activate_account(employee, token, url_for, bg_task):
            return http_responses.status_200_ok("bi bi-person-badge", 
                                                f"Welcome to Future Programmers {employee.Last_Name} <br> Check your email and follow instructios to activate your account")
        else:
            return http_responses.status_503_service_unavailable("bi bi-send-exclamation-fill", 
                                                                f"Account created but couldn't send activation link <br> Contact support to activate your account!")



# function to update employee data
async def update_employeer(new_data, cur_user, db: Session):
    try:
        # setting current user with new data
        cur_user.Employee_Id= new_data.get('employee_id')
        cur_user.First_Name= new_data.get('first_name')
        cur_user.Last_Name= new_data.get("last_name")
        cur_user.Position= new_data.get('position')
        cur_user.Phone= new_data.get('phone')
        cur_user.Email= new_data.get('email')

        db.add(cur_user)
        db.commit()
        db.refresh(cur_user)
        
        return http_responses.status_200_ok("bi bi-check2-circle", f"{cur_user.First_Name} your data was successfully updated")
    except ValueError:
        return http_responses.status_500_server_error("bi bi-database-fill-x", "Could not updated your data. Try again!")

    

# function to update employee password
async def employeer_update_password(cur_user, data, db: Session):
    employeer_found= await auth_settings.load_user(cur_user.Email, db)


    if employeer_found:
        # verify if current password is valid
        if not auth_settings.verify_pass(data.get("cur_password"), employeer_found.Password):
            return http_responses.status_404_not_found("bi bi-exclamation-diamond-fill", "Current password is not valid!")
        
        elif not auth_settings.strong_password(data.get("new_password")):
            return http_responses.status_406_not_acceptable("bi bi-file-earmark-lock2-fill", "New password doesn't meet strong password requirements!")
        
        elif not data.get("new_password") == data.get("conf_password"):
            return http_responses.status_406_not_acceptable("bi bi-file-earmark-lock2-fill", "'New Password' doesn't match 'Confirm Password'!")
        else:
            #resetting user password into DB
            employeer_found.Password= auth_settings.encrypt(data.get("new_password"))

            db.add(employeer_found)
            db.commit()
            db.refresh(employeer_found)

            return http_responses.status_200_ok("bi bi-check2-circle", "Password successfully updated")
    else:
        return http_responses.status_404_not_found("bi bi-envelope-exclamation", "E-mal address not found!")


# fnction to get employeer company
async def get_employee_company(employeer, db: Session):
    query= select(Company.Company).filter(Company.employee_id == employeer.Id)

    return db.execute(query).scalar()