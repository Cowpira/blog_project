from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from sqlalchemy import select
from sqlalchemy.orm import Session
from data_model.models import Person
from services import auth_settings, http_responses
from routers import send_emails


# function to find user by ID
def get_user_by_id(user_id, db: Session):
    account= db.execute(select(Person).where(Person.Id == user_id))
    return account.scalar()


# function to activate employee account
async def activate_users_account(user_id, token, bg_task, db: Session):
    filter= db.execute(select(Person).where(Person.Id == user_id))
    account= filter.scalar()

    hashed_token= await auth_settings.validate_reset_token(token, db)

    # calling function to verify token
    if not account or not hashed_token:
        return http_responses.status_406_not_acceptable("bi bi-slash-circle-fill", "Account not found or invalid Reset Token!")
    
    elif hashed_token.Expires_At.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        # if token time expired we delete it from db
        auth_settings.delete_previous_token(user_id, db)
        return http_responses.status_406_not_acceptable("bi bi-clock-history", "Token has exired!")
    
    # verify if account is already active
    elif account.Active:
        return http_responses.status_202_accepted("bi bi-person-fill-exclamation", "Account already activated")
    else:
        account.Active= True
        # getting time zone for Texas
        tz_texas = ZoneInfo("America/Chicago")
        account.Activated_Date= datetime.now(tz_texas)

        db.add(account)
        db.commit()
        db.refresh(account)

        # call function to delete token
        auth_settings.delete_previous_token(user_id, db)

        # sending confirmation email
        await send_emails.activate_success(account, bg_task)
        return http_responses.status_200_ok("bi bi-check2-circle", "Account successfully activated")