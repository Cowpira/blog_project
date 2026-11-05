from data_model.models import Company
from sqlalchemy import func, select
from datetime import datetime, timezone
from sqlalchemy.orm import Session, load_only
from services import helper, http_responses, image_utils


# function to add employeer company
async def add_new_company(file, data, cur_employeer, db: Session):
    query= select(Company).where(Company.Company == data.get("company"))
    company_found= db.execute(query).scalar()

    if company_found:
        return http_responses.status_302_found("bi bi-ban", f"Company {company_found.Company} alredy registered!")
    else:
        new_company= Company(
            Company= data.get("company"),
            About= data.get("about"),
            Website= data.get("website"),
            Country= data.get("country"),
            State= data.get("state"),
            City= data.get("city"),
            Created_Date= datetime.now(timezone.utc),
            Image= "default.png",
            Img_Path= "uploaded_comp_images/default.png",
            employee_id= cur_employeer.Id
        )

        if not new_company.Website.startswith(("http://", "https://")): 
            new_company.Website= f"http://{new_company.Website}"

        db.add(new_company)
        db.commit()

        # update developer account to add the company to his/her account
        cur_employeer.Work_At= new_company.Company
        
        db.add(cur_employeer)
        db.commit()
        db.refresh(cur_employeer)

        # after save the company we send the company as paramather to save company logo
        query= select(Company).where(Company.employee_id == cur_employeer.Id)
        company= db.execute(query).scalar() 

        # send image to be processed and saved
        result= await helper.process_img(image_utils.COMP_IMG_DIR, file, company, db)

        if result:
            return http_responses.status_200_ok("bi bi-check2-all", f"Company {new_company.Company} added successfully")
        else:
            return http_responses.status_200_ok("bi bi-check2-all", f"Company {new_company.Company} added, but failed to add company's logo!")



# function to add employeer company
async def update_company(file, data, cur_employeer, db: Session):
    query= select(Company).where(Company.employee_id == cur_employeer.Id)
    company_found= db.execute(query).scalar()

    if not company_found:
        return http_responses.status_404_not_found("bi bi-ban", f"Company {company_found.Company} not found!")
    else:
        company_found.Company= data.get("company")
        company_found.About= data.get("about")
        
        if not data.get("website").startswith(("http://", "https://")): 
            company_found.Website= "http://" + data.get("website")
        else:
            company_found.Website= data.get("website")

        company_found.Country= data.get("country")
        company_found.State= data.get("state")
        company_found.City= data.get("city")

        db.add(company_found)
        db.commit()
        db.refresh(company_found)

        # send image to be processed and saved
        result= await helper.process_img(image_utils.COMP_IMG_DIR, file, company_found, db)

        if result:
            return http_responses.status_200_ok("bi bi-check2-all", f"Company {company_found.Company} updated successfully")
        else:
            return http_responses.status_200_ok("bi bi-check2-all", f"Company {company_found.Company} updated, but failed to update company's logo!")
        


# function to find company registered by current employeer logged in
async def get_company(employee_id, db: Session):
    query= select(Company).where(Company.employee_id == employee_id)

    return db.execute(query).scalar()



# function to retrieve 3 random developer from developers in DB
async def get_random_companies(db: Session):
    query= select(Company).options(load_only(Company.Company, Company.Img_Path))\
        .order_by(func.random()).limit(10)
    result= db.execute(query).scalars().all()

    if len(result) > 0:
        return result
    else:
        return http_responses.status_204_no_content("bi bi-clipboard-x-fill", "No company found!")
