from sqlalchemy import select
from data_model import models
from sqlalchemy.orm import Session
from services import http_responses
import asyncio



# method to create portfolio
async def save_portfolio(data, cur_user, db: Session):
    
    if cur_user.Has_Resume:
        return http_responses.status_406_not_acceptable("", "Portfolio already saved. Try to update")
    else:

        result = await asyncio.gather(
            # call function to save education
            save_education(data, cur_user, db),

            # call function to save certification
            save_certification(data, cur_user, db),

            # call function to save front end
            save_front_end(data, cur_user, db),

            # call function to save back end
            save_back_end(data, cur_user, db),

            # call function to save database
            save_database(data, cur_user, db),

            # call function to save cloud
            save_cloud(data, cur_user, db),

            # call function to save work experiences
            save_work_experiences(data, cur_user, db),

            # call function to save projects
            save_projects(data, cur_user, db)
        )

        cur_user.Has_Resume= True

        db.commit()
        db.refresh(cur_user)

        if result:
            return http_responses.status_200_ok("bi bi-check2-circle", "Portfolio added successfully")

        else:
            return http_responses.status_500_server_error("bi bi-database-fill-exclamation", "Coudn't add your portfolio. Try again")
 


# function to save education
async def save_education(data, cur_user, db):
    if len(data.get("school")) >= 10:
        # getting education data
        education= models.Education(
            School= data.get("school"),
            Education_Type= data.get("education_type"),
            Graduated_At= data.get("graduated_at"),
            Grad_Status= data.get("grad_status"),
            New_Education= data.get("other_education"),
            dev_id= cur_user.Id
        )

        db.add(education)
        db.commit()
        db.refresh(education)
        await asyncio.sleep(1)
        return True
    else:
        return False



# function to save certification
async def save_certification(data, cur_user, db):
    certification= models.Certification(
        Certification1= data.get("certification1"), 
        Cert1_Date= data.get("cert1_date"), 

        Certification2= data.get("certification2"), 
        Cert2_Date= data.get("cert2_date"), 

        Certification3= data.get("certification3"), 
        Cert3_Date= data.get("cert3_date"),

        dev_id= cur_user.Id
    )

    db.add(certification)
    db.commit()
    db.refresh(certification)
    await asyncio.sleep(1)
    return True



# function to save front end
async def save_front_end(data, cur_user, db):
    lang1= str(data.get("frontend-lang1") or "").strip()
    lang2= str(data.get("frontend-lang2") or "").strip()
    lang3= str(data.get("frontend-lang3") or "").strip()

    if lang1 or lang2 or lang3:
        front_end= models.Front_End(
            Frontend_Lang1= lang1, 
            Exp_Frontend1= data.get("exp_frontend1"), 

            Frontend_Lang2= lang2, 
            Exp_Frontend2= data.get("exp_frontend2"), 

            Frontend_Lang3= lang3, 
            Exp_Frontend3= data.get("exp_frontend3"),

            dev_id= cur_user.Id
        )

        db.add(front_end)
        db.commit()
        db.refresh(front_end)
        await asyncio.sleep(1)
    else:
        return True



# function to save front end
async def save_back_end(data, cur_user, db):
    back1= str(data.get("backend-lang1") or "").strip()
    back2= str(data.get("backend-lang2") or "").strip()
    back3= str(data.get("backend-lang3") or "").strip()

    if back1 or back2 or back3:
        back_end= models.Back_End(
            Backend_Lang1= back1, 
            Exp_Backend1= data.get("exp_backend1"), 

            Backend_Lang2= back2, 
            Exp_Backend2= data.get("exp_backend2"), 

            Backend_Lang3= back3, 
            Exp_Backend3= data.get("exp_backend3"),

            dev_id= cur_user.Id
        )

        db.add(back_end)
        db.commit()
        db.refresh(back_end)
        await asyncio.sleep(1)
    else:
        return True



# function to save database
async def save_database(data, cur_user, db):
    data_b1= str(data.get("database1") or "").strip()
    data_b2= str(data.get("database2") or "").strip()
    data_b3= str(data.get("database3") or "").strip()

    if data_b1 or data_b2 or data_b3:
        database= models.Database(
            Database1= data_b1, 
            Exp_Database1= data.get("exp_database1"), 

            Database2= data_b2, 
            Exp_Database2= data.get("exp_database2"), 

            Database3= data_b3, 
            Exp_Database3= data.get("exp_database3"),

            dev_id= cur_user.Id
        )

        db.add(database)
        db.commit()
        db.refresh(database)
        await asyncio.sleep(1)
    else:
        return True



# function to save database
async def save_cloud(data, cur_user, db):
    cloud1= str(data.get("cloud1") or "").strip()
    cloud2= str(data.get("cloud2") or "").strip()
    cloud3= str(data.get("cloud3") or "").strip()

    if cloud1 or cloud2 or cloud3:
        cloud= models.Cloud(
            Cloud1= cloud1, 
            Exp_Cloud1= data.get("exp_cloud1"),

            Cloud2= cloud2, 
            Exp_Cloud2= data.get("exp_cloud2"), 

            Cloud3= cloud3, 
            Exp_Cloud3= data.get("exp_cloud3"), 

            Other_Skills= data.get("other_skills"),
            dev_id= cur_user.Id
        ) 
        
        db.add(cloud)
        db.commit()
        db.refresh(cloud)
        await asyncio.sleep(1)
    else:
        return True



# function to save work experiences
async def save_work_experiences(data, cur_user, db:Session):
    # find the developer in and get the 1st job experience
    query= select(models.Work).filter(models.Work.dev_id == cur_user.Id)
    work_found= db.execute(query).scalar()
    if work_found:
        work_found.Company2= data.get("company2")
        work_found.Position2= data.get("position2")
        work_found.Started2= data.get("started2")
        work_found.Ended2= data.get("ended2")
        work_found.Contribution2= data.get("contribution2")

        work_found.Company3= data.get("company3")
        work_found.Position3= data.get("position3")
        work_found.Started3= data.get("started3")
        work_found.Ended3= data.get("ended3")
        work_found.Contribution3= data.get("contribution3")

        db.commit()
        db.refresh(work_found)
        await asyncio.sleep(1)
        return True



# function to save projects
async def save_projects(data, cur_user, db):
    projects= models.Project(
        Project1= data.get("project1"), 
        Link1= data.get("link1"), 
        Prj_Desc1= data.get("prj_desc1"), 

        Project2= data.get("project2"), 
        Link2= data.get("link2"), 
        Prj_Desc2= data.get("prj_desc2"), 

        Project3= data.get("project3"), 
        Link3= data.get("link3"), 
        Prj_Desc3= data.get("prj_desc3"),

        dev_id= cur_user.Id
    )

    db.add(projects)
    db.commit()
    db.refresh(projects)
    await asyncio.sleep(1)
    return True




# function to list all users data
def list_all_resume_data(db: Session):
    resume_data={
        "education": db.query(models.Education).all(),
        "certifications": db.query(models.Certification).all(),
        "front_end": db.query(models.Front_End).all(),
        "back_end": db.query(models.Back_End).all(),
        "databases": db.query(models.Database).all(),
        "clouds": db.query(models.Cloud).all(),
        "works": db.query(models.Work).all(),
        "projects": db.query(models.Project).all()
    }
    return resume_data
    


# function to get resume by developer ID
async def resume_by_dev_id(dev_id, db: Session):
    resume={
        "education": db.query(models.Education).filter(models.Education.dev_id == dev_id).first(),
        "certifications": db.query(models.Certification).filter(models.Certification.dev_id == dev_id).first(),
        "front_end": db.query(models.Front_End).filter(models.Front_End.dev_id == dev_id).first(),
        "back_end": db.query(models.Back_End).filter(models.Back_End.dev_id == dev_id).first(),
        "databases": db.query(models.Database).filter(models.Database.dev_id == dev_id).first(),
        "clouds": db.query(models.Cloud).filter(models.Cloud.dev_id == dev_id).first(),
        "works": db.query(models.Work).filter(models.Work.dev_id == dev_id).first(),
        "projects": db.query(models.Project).filter(models.Project.dev_id == dev_id).first()
    }
    return resume



# function to get works by developer ID
async def works_by_developer_id(dev_id, db: Session):
    try:
        return db.query(models.Work).filter(models.Work.dev_id == dev_id).first()
    except:
        return False