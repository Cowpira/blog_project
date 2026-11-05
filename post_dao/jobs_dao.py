from datetime import datetime, timezone
from sqlalchemy import Integer, cast, or_, select
from sqlalchemy.orm import Session, aliased, joinedload, selectinload
from data_model.models import Company, Developer, Jobs, Job_Application
from services import http_responses


# function to list all jobs
async def list_all_jobs(db: Session):
    try:
        query= select(Jobs) \
        .options(joinedload(Jobs.job_belongs_company)) \
        .order_by(Jobs.Posted_Date.desc())

        return db.execute(query).scalars().all()
    except ValueError:
        return http_responses.status_204_no_content("bi bi-clipboard-x-fill", "There is no job available yet!")



# function to create a new hob
async def add_job(data, cur_employee, db: Session):
    query= select(Company).where(Company.employee_id == cur_employee.Id)
    company_found= db.execute(query).scalar()

    if company_found:
        job= Jobs(
            Title= data.get("title"),
            Location= data.get("work_location"),
            Contract= data.get("contract"),
            Lang_Requirements= data.get("tags_selected"),
            Other_Requirements= data.get("requirements"),
            Payment_Type= data.get("payment"),
            Salary_Start= data.get("minSalary"),
            Salary_End= data.get("maxSalary"),
            Description= data.get("description"),
            Benefits= data.get("benefits"),
            Status= data.get("job_status"),
            Closed= False,
            Posted_Date= datetime.now(timezone.utc),
            employeer_id= cur_employee.Id,
            company_id= company_found.Id
        )
        
        db.add(job)
        db.commit()
        db.refresh(job)

        return http_responses.status_200_ok("bi bi-check2-all", f"{job.Title} successfully posted")
    else:
        return http_responses.status_404_not_found("bi bi-building-fill-exclamation", 
                                                f"Sorry, {cur_employee.First_Name} you didn't register a company!")



# function to get all jobs by employee ID
async def list_jobs_by_employee(cur_employee, db: Session):
    query= select(Jobs).where(Jobs.employeer_id == cur_employee.Id).order_by(Jobs.Posted_Date.desc())
    jobs_found= db.execute(query).scalars().all()

    return jobs_found if jobs_found else \
    http_responses.status_204_no_content("bi bi-clipboard-x-fill", "Sorry, you have not post job yet!")
        


# function to find post to be edit
async def get_job_to_edit(id, db: Session):
    query= select(Jobs).where(Jobs.Id == id)
    job_found= db.execute(query).scalar()

    if not job_found:
        return http_responses.status_404_not_found("bi bi-ban", f"Job with ID:{id} not found!")
    else:
        return job_found
    


# function to edit job
async def update_job(job_data, job_id, db: Session):
    try:
        query= select(Jobs).where(Jobs.Id == job_id)
        job_found= db.execute(query).scalar()

        if job_found:
            job_found.Status= job_data.get("job_status")
            job_found.Title= job_data.get("title")
            job_found.Location= job_data.get("work_location")
            job_found.Contract= job_data.get("contract")
            job_found.Lang_Requirements= job_data.get("tags_selected")
            job_found.Other_Requirements= job_data.get("requirements")
            job_found.Payment_Type= job_data.get("payment")
            job_found.Salary_Start= job_data.get("minSalary")
            job_found.Salary_End= job_data.get("maxSalary")
            job_found.Description= job_data.get("description")
            job_found.Benefits= job_data.get("benefits")

            if 'Closed' in job_data.get("job_status"):
                job_found.Closed= True
            else: 
                job_found.Closed= False
                

            db.commit()
            db.refresh(job_found)

            return http_responses.status_200_ok("bi bi-check2-all", f"Job {job_found.Title} successfully updated")
        else:
            return http_responses.status_404_not_found("bi bi-ban", f"Job ID:{job_id} not found!")
    except ValueError:
        return http_responses.status_500_server_error("bi bi-database-exclamation", "Sorry, we could not process this action. Try again!")
        


# function to search job by Title, or Company
async def search_jobs(job_param, contracts, durations, states, locations, db:Session):
    if not job_param:
            return []
    
    param= job_param.strip()

    query= select(Jobs).join(Jobs.job_belongs_company)

    if param in contracts:
        query= query.where(Jobs.Contract.ilike(param))
    
    elif param in durations:
        query= query.where(Jobs.Duration.ilike(param))

    elif param in locations:
            query= query.where(Jobs.Location.ilike(param))
            
    elif param in states:
        query= query.where(Company.State.ilike(param))

    else:
        query= query.where(
            or_(
                Company.Company.ilike(param),
                Company.Country.ilike(param)
            )
        )

    query= query.options(joinedload(Jobs.job_belongs_company)) \
        .order_by(Jobs.Posted_Date.desc())

    job_found= db.execute(query).scalars().all()
    
    return job_found if job_found else []



# function to delete job by ID
async def remove_job(job_id, db: Session):
    try:
        query= select(Jobs).where(Jobs.Id == job_id)
        job_found= db.execute(query).scalar()

        if job_found:
            title= job_found.Title

            db.delete(job_found)
            db.commit()
            
            return http_responses.status_200_ok("bi bi-check2-all", f"Job {title} successfully removed")
        else:
            return http_responses.status_404_not_found("bi bi-exclamation-triangle-fill", f"Job ID:{job_id} not found!")
    except Exception as ex:
        return http_responses.status_500_server_error("bi bi-database-fill-x", f"Couldn't delete the job. Error: {ex}!")



# function to search job by ID, Title, or Company
async def close_job(job_id, db: Session):
    try:
        query= select(Jobs).where(Jobs.Id == job_id)
        job_found= db.execute(query).scalar()

        if job_found:
            job_found.Closed= True
            job_found.Status= 'Closed for Applications'
            job_found.Posted_Date= datetime.now(timezone.utc)

            db.commit()
            db.refresh(job_found)

            return http_responses.status_200_ok("bi bi-check2-all", f"Job {job_found.Title} closed successfully")
        else:
            return http_responses.status_404_not_found("bi bi-exclamation-triangle-fill", f"Job ID:{job_id} not found!")
    except Exception as ex:
        return http_responses.status_500_server_error("bi bi-database-fill-x", f"Couldn't close the job. Error: {ex}!")



# function to apply a developer into a job position
async def apply_dev_job(job_id, cur_dev, db: Session):
    try:
        query= select(Job_Application).where(Job_Application.dev_id == cur_dev.Id, Job_Application.job_id == job_id)
        dev_applied= db.execute(query).scalar()

        j_query= select(Jobs).where(Jobs.Id == job_id)
        job_found= db.execute(j_query).scalar()

        if job_found:
            job_title= job_found.Title

        if dev_applied:
            return http_responses.status_302_found("bi bi-ban-fill", f"You have already applied for {job_title}!!")
        else:
            application= Job_Application( 
                Applied_Date= datetime.now(timezone.utc),
                job_id= job_id,
                dev_id= cur_dev.Id
            )

            db.add(application)
            db.commit()
            db.refresh(application)

            return http_responses.status_200_ok("bi bi-check2-all", f"Congrats {cur_dev.First_Name} you successfully applied for {job_title }. \n Good lucky")
    except ValueError:
        return http_responses.status_204_no_content("bi bi-clipboard-x-fill", "There is no job available yet!")
    


# function to list all jobs applications by developer ID
async def list_all_jobs_dev_application(cur_dev, db: Session):
    try:
        query= select(
            Company.Company.label("company_name"),
            Jobs.Title.label("job_position"),
            Job_Application.Applied_Date.label("applied_date"),
            Jobs.Status.label("job_status")  
        ) \
        .join(Jobs, Job_Application.job_id == Jobs.Id) \
        .join(Company, Jobs.company_id == Company.Id) \
        .filter(Job_Application.dev_id == cur_dev.Id) \
        .order_by(Job_Application.Applied_Date.desc())
        
        applications= db.execute(query).mappings().all()
        return applications
    except ValueError:
        return http_responses.status_204_no_content("bi bi-clipboard-x-fill", "Sorry, you haven't applied yet!!!")



# function to get all jobs applyed by a developer
async def get_jobs_applies(cur_dev, db: Session):
    try:
        query= select(Job_Application.job_id).filter(Job_Application.dev_id == cur_dev.Id)
        applic_found= db.execute(query).scalars().all()

        return applic_found
    except ValueError:
        return http_responses.status_503_service_unavailable("bi bi-database-fill-x", 
                                                            "Could not retrieve data. Try again!!!")



# function to get all developers that applied for a job
async def list_job_applicants(job_id, db: Session):
    dev_alias= aliased(Developer, flat=True)

    try:
        query= select(
                Jobs.Title.label("job_position"),
                dev_alias.Id.label('dev_id'),
                dev_alias.First_Name.label("f_name"),
                dev_alias.Last_Name.label("l_name"),
                Jobs.Status.label("job_status")  
            ) \
            .select_from(Job_Application) \
            .join(Job_Application.application_job) \
            .join(Job_Application.dev_applied.of_type(dev_alias)) \
            .filter(Job_Application.job_id == job_id) \
            .order_by(Job_Application.Applied_Date.desc())

        applicants_found= db.execute(query).all()

        return applicants_found
    except ValueError:
        return http_responses.status_503_service_unavailable("bi bi-database-fill-x", 
                                                            "Could not retrieve data. Try again!!!")