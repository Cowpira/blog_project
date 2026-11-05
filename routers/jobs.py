import io
import uuid
from typing import List
from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session
from post_dao import developers_dao, jobs_dao, portfolio_dao
from routers import post
from routers.login import limiter
from data_model.models import Developer, Employee, Person
from data_model.schemas import JobResponse
from services import helper, http_responses
from services.authentication import get_current_user
from services.db_connection import get_db
from datetime import datetime
from xhtml2pdf import pisa
from jinja2 import Template


public_api= APIRouter() # public routers
restrict_api= APIRouter()  # router for authenticated users

contracts= ['1099', 'W2', 'C2C']
durations= ['Full-Time', 'Part-Time', 'Internship', 'Temporary']
states= ['Arizona', 'Atlanta', 'California', 'Colorado', 'Florida', 'Massachusetts', 'Maryland', 
        'Mississipi', 'New York', 'New Jersey', 'Texas', 'Tenese', 'Virginia', 'Washington']
locations= ['Hybrid', 'On-site', 'Remote']

# function to list all jobs
async def load_jobs(jobs, page, list, job_param, request, result, cur_user, db):
    if list and list >= 1:
        helper.total_items= list

    # return the list of jobs applied by an developer in
    jobs_applied= []
    if cur_user:
        jobs_applied= await jobs_dao.get_jobs_applies(cur_user, db)
    
    
    paginated_jobs= helper.pagination_settings(jobs, page, 'jobs', helper.total_items)
    return helper.templates.TemplateResponse("jobs.html", {'request': request, 'result': result, 'user_in': cur_user, 'job_param': job_param, 
                                                        'contracts': contracts, 'durations': durations, 'locations': locations, 'jobs': paginated_jobs, 
                                                        'states': states, 'limit_items': helper.limit_items, 'total_items': helper.total_items, 'jobs_applied': jobs_applied})

##############################################################################################################################
############################################### PUBLIC FUNCTIONS FOR ALL USERS  ##############################################

# function to list all jobs
@public_api.get('', include_in_schema= False, response_model=List[JobResponse])
async def list_jobs(request: Request, page: int= 1, list: int= 0, db: Session= Depends(get_db), 
                    cur_user: Developer= Depends(get_current_user)):
   
    jobs= await jobs_dao.list_all_jobs(db)
    return await load_jobs(jobs, page, list, '', request, '', cur_user, db)


##############################################################################################################################
################################ RESTRICTED FUNCTIONS FOR LOGGED IN DEVELOPERS OR EMPLOYEERS  ################################

# function to add new job
@restrict_api.get('/add_job', include_in_schema= False)
async def add_job(request: Request, cur_employee: Person= Depends(get_current_user),
                db: Session= Depends(get_db)):

    if not cur_employee:
        return await helper.login_expired()

    return helper.templates.TemplateResponse("post_job.html", {'request': request, 'result':'',
                                                                    'languages': post.languages, 'user_in': cur_employee})
        

#method to add new job
@restrict_api.post('/add_job')
@limiter.limit("3/hour") # limit post 3 jobs per hour
async def add_job(request: Request, db: Session= Depends(get_db), cur_user: Person= Depends(get_current_user)):

    if not cur_user:
        return await helper.login_expired()

    result= await jobs_dao.add_job(await request.form(), cur_user, db)

    if result.status_code == 404:
        return helper.templates.TemplateResponse("post_job.html", {'request': request, 'result': result,
                                                                'languages': post.languages, 'user_in': cur_user})
    else:
        jobs= await jobs_dao.list_all_jobs(db)
        return await load_jobs(jobs, 1, helper.total_items, None, request, result, cur_user, db)
    


# function to update a job
@restrict_api.get('/update_job/{job_id}', include_in_schema= False)
async def update_job(request: Request, job_id: uuid.UUID, cur_employee: Employee= Depends(get_current_user),
                db: Session= Depends(get_db)):
    if not cur_employee:
        return await helper.login_expired()
    
    edit_job= await jobs_dao.get_job_to_edit(job_id, db)
    return helper.templates.TemplateResponse("edit_job.html", {'request': request, 'result':'', 'edit_job': edit_job,
                                                                    'languages': post.languages, 'user_in': cur_employee})


# function to update a job
@restrict_api.post('/update_job/{job_id}', include_in_schema=False)
@limiter.limit("5/hour") # limit update 5 jobs per hour
async def update_job(request: Request, job_id: uuid.UUID, cur_employee: Employee= Depends(get_current_user),
                    db: Session= Depends(get_db)):
    if not cur_employee:
        return await helper.login_expired()
    
    result= await jobs_dao.update_job(await request.form(), job_id, db)

    if result.status_code == 200:
        jobs= await jobs_dao.list_all_jobs(db)
        return await load_jobs(jobs, 1, helper.total_items, None, request, result, cur_employee, db)
    else:
        edit_job= await jobs_dao.get_job_to_edit(job_id, db)
        return helper.templates.TemplateResponse("edit_job.html", {'request': request, 'result':'', 'edit_job': edit_job,
                                                                'languages': post.languages, 'user_in': cur_employee}) 



# function to search jobs by parameter
@public_api.get('/seach_jobs/{page}&{list}&{job_param}', include_in_schema=False)
async def seach_jobs(request: Request, job_param: str= None, page: int=1, list: int=0, 
                    cur_user: Person= Depends(get_current_user), db: Session= Depends(get_db)):

    # list all jobs found by parameter 
    jobs_found= jobs_dao.search_jobs(job_param, contracts, durations, states, locations, db)
    result= None
    
    if not jobs_found:
        result= http_responses.status_204_no_content("bi bi-bookmark-x-fill", f"Sorry. No jobs found for {job_param}!")
        jobs_found= await jobs_dao.list_all_jobs(db)

    return await load_jobs(jobs_found, page, list, job_param, request, result, cur_user, db)
    


# function to list all jobs posted by a employee
@restrict_api.get('/my_jobs', include_in_schema=False)
async def my_jobs(request: Request, cur_employee: Employee= Depends(get_current_user), 
                db: Session= Depends(get_db)):
    
    if not cur_employee:
        return await helper.login_expired()
    
    result= await jobs_dao.list_jobs_by_employee(cur_employee, db)
    return helper.templates.TemplateResponse("my_jobs.html", {'request': request, 'result':result, 
                                                            'user_in': cur_employee})
    


# function to close a job
@restrict_api.get('/close_job/{job_id}', include_in_schema=False)
async def close_job(request: Request, job_id: uuid.UUID, cur_employee: Employee= Depends(get_current_user), 
                db: Session= Depends(get_db)):
    if not cur_employee:
        return await helper.login_expired()
    
    jobs= await jobs_dao.list_all_jobs(db)
    result= await jobs_dao.close_job(job_id, db)

    return await load_jobs(jobs, 1, helper.total_items, None, request, result, cur_employee, db)



# function to apply a developer into a jop
@restrict_api.post('/job_apply/{job_id}', include_in_schema= False)
async def job_apply(request: Request, job_id: uuid.UUID, cur_dev: Developer= Depends(get_current_user),
                db: Session= Depends(get_db)):
    if not cur_dev:
        return await helper.login_expired()
    
    jobs= await jobs_dao.list_all_jobs(db)
    result= await jobs_dao.apply_dev_job(job_id, cur_dev, db)

    return await load_jobs(jobs, 1, helper.total_items, None, request, result, cur_dev, db)



# function to list all job applicants
@restrict_api.get('/job_applicants/{job_id}', include_in_schema= False)
async def job_applicants(request: Request, job_id: uuid.UUID, cur_emp: Employee= Depends(get_current_user),
                        db: Session= Depends(get_db)):
    if not cur_emp:
        return await helper.login_expired()
    
    result= await jobs_dao.list_job_applicants(job_id, db)
    return helper.templates.TemplateResponse("job_applicants.html", { "request": request, 'result': result, 
                                                                    'user_in': cur_emp})



# function to generate and format the resume PDF to be downloaded
@restrict_api.get('/download_dev_resume/{dev_id}', include_in_schema= False)
async def download_dev_resume(dev_id: uuid.UUID, cur_emp: Employee= Depends(get_current_user),
                              db: Session= Depends(get_db)):
    if not cur_emp:
        return await helper.login_expired()

    # formating developer resume PDF
    developer= await developers_dao.developer_by_id(dev_id, db)
    dev_resume= await portfolio_dao.resume_by_dev_id(dev_id, db)

    
    # caling method that format pdf
    pdf_bytes= dev_resume_pdf(developer, dev_resume)


    # return the pdf file 64 base to be downloaded into user URL
    date= datetime.now().strftime("%b_%d_%Y")
    headers= {'Content-Disposition': f'attachment; filename="{developer.First_Name}_resume_{date}.pdf"',
              'Content-Length': str(len(pdf_bytes))}

    return Response(content= pdf_bytes, media_type= "application/pdf", headers= headers)



# function to format developer resume PDF
def dev_resume_pdf(dev, dev_resume):

    # extracting each model from resume list
    edu, cert, front, back, databases, clouds, works, projects= None, None, None, None, None, None, None, None
    
    edu= dev_resume.get("education") if isinstance(dev_resume, dict) else getattr(dev_resume, "education", None)
    cert= dev_resume.get("certifications") if isinstance(dev_resume, dict) else getattr(dev_resume, "certifications", None)
    front= dev_resume.get("front_end") if isinstance(dev_resume, dict) else getattr(dev_resume, "front_end", None)
    back= dev_resume.get("back_end") if isinstance(dev_resume, dict) else getattr(dev_resume, "back_end", None)
    databases= dev_resume.get("databases") if isinstance(dev_resume, dict) else getattr(dev_resume, "databases", None) 
    clouds= dev_resume.get("clouds") if isinstance(dev_resume, dict) else getattr(dev_resume, "clouds", None) 
    works= dev_resume.get("works") if isinstance(dev_resume, dict) else getattr(dev_resume, "works", None)
    projects= dev_resume.get("projects") if isinstance(dev_resume, dict) else getattr(dev_resume, "projects", None)

    html_resume_template_str="""
        <html>
            <head>
                <meta charset="utf-8">
                <style>
                    @page { size: A4; margin: 15mm; }
                    body {
                        font-family: Helvetica, Arial, sans-serif;
                        color: #212121;
                    }
                    .header-name { 
                        font-size: 23px; 
                        color: #fb5607; 
                        text-align: center;
                        font-weight: bolder;
                    }
                   
                    .badge {
                        background-color: #f8f9fa;
                        border: .6px solid #ced4da;
                        color: #6c757d;
                        border-radius: 5px;
                        font-weight: 500;
                        padding-top: 7px;
                        margin-bottom: 8px;
                        width: 100px;
                        height: 13px;
                        text-align: center;
                    }

                    .label{ 
                        font-family: Arial; 
                        font-weight: 500;
                        font-size: 10px; 
                        color: #757575; 
                    }

                    .label-data{ color: #2980b9; font-size: 12px; }
                    p { margin: 0 0 5px 0; }

                    .hr_style {
                        position: relative;
                        width: 90%;
                        margin-left: 105px;
                        top: -9px;
                        border-top: .7px solid #adb5bd; 
                    }
                    
                    .pill {
                        margin-bottom: 8px;
                        border-radius: 8px;
                        padding: 4px 17px;
                        font-size: 9px;
                        font-weight: bold;
                    }

                    .recent-exp{ background-color: #27ae60; color: #FFFF; }
                    .prev-exp{ background-color: #f48c06; color: #FFFF; }
                    .prior-exp{ background-color: #ef233c; color: #FFFF; }
                    .skill-color{background-color: #000814; color: #e85d04;}
                    
                    /* table to perfect align data into PDF */
                    .table-layout {
                        width: 100%;
                        margin-bottom: 5px;
                    }
                    .table-layout td {
                        width: 50%;
                        vertical-align: top;
                    }
                </style>
            </head>

            <body>
                <div class="header-name">
                    {{ dev.First_Name }} {{ dev.Last_Name }}'s Resume
                </div>

                <!-- =======================  RESUME PERSONAL DATA ======================= -->
                <p class="badge text-dark"> Personal </p> <p class="hr_style"></p>
                   
                <table class="table-layout">
                    <tr>
                        <td>
                            <span class="label">Name:</span>
                            <p class="label-data">{{ dev.First_Name }} {{ dev.Last_Name }}</p>
                        </td>
                        <td>
                            <span class="label">Address:</span>
                            <p class="label-data">{{ dev.Address or 'Not provided' }}</p>
                        </td>
                    </tr>

                    <tr> <td></td> </tr>
                    <tr>
                        <td>
                            <span class="label">Email:</span>
                            <p class="label-data">{{ dev.Email }}</p>
                        </td>
                        <td>
                            <span class="label">Phone:</span>
                            <p class="label-data">{{ dev.Phone or 'Not provided' }}</p>
                        </td>
                    </tr>
                </table>

                <!-- ======================= PROFESSIONAL TITLE ======================= -->
                <p class="badge text-dark"> Professional </p> <p class="hr_style"></p>
                
                <table class="table-layout">
                    <tr>
                        <td>
                            <span class="label">Title:</span>
                            <p class="label-data">{{ dev.Cod_Title or 'Not provided' }}</p>
                        </td>
                        <td>
                            <span class="label">Language:</span>
                            <p class="label-data">{{ dev.Cod_Lang or 'Not provided' }}</p>
                        </td>
                        <td>
                            <span class="label">Experience:</span>
                            <p class="label-data">{{ dev.Years_Exp or '0' }}</p>
                        </td>
                    </tr>
                </table>
                
                <!-- =======================  RESUME WORK EXPERIENCE ======================= -->
                <p class="badge text-dark"> Experiences </p> <p class="hr_style"></p>
                
                {% for i in range(1, 4) %}
                    {% if works['Company'~i] %}
                        <table class="table-layout">
                            <tr>
                                <td colspan="5" align="center">
                                    {% if i == 1 %}
                                        <span class="pill recent-exp">Most Recent</span> <br>
                                    {% endif %}
                                    
                                    {% if i == 2 %}
                                        <span class="pill prev-exp">Previous Role</span> <br>
                                    {% endif %}

                                    {% if i == 3 %}
                                        <span class="pill prior-exp">Prior Experience</span> <br>
                                    {% endif %}
                                </td>
                            </tr>

                            <tr>
                                <td style="width: 35%;">
                                    <span class="label">Company:</span> 
                                    <p class="label-data">{{ works['Company'~i] }}</p>
                                </td>

                                <td style="width: 35%;">
                                    <span class="label">Position:</span> 
                                    <p class="label-data">{{ works['Position'~i] }}</p>
                                </td>

                                <td style="width: 20%;">
                                    <span class="label">Started:</span> 
                                    <p class="label-data">{{ works['Started'~i] or 'Not informed' }}</p>
                                </td>

                                <td style="width: 10%;">
                                    <span class="label">Ended:</span> 
                                    <p class="label-data">{{ works['Ended'~i] or 'Present' }}</p>
                                </td>
                            </tr>
                            <tr> <td></td> </tr>

                            <tr>
                                <td colspan="5">
                                    <span class="label">Contribution & Growth:</span> 
                                    <p class="label-data">{{ works['Contribution'~i] or 'No contributions informed' }}</p>
                                </td>
                            </tr>
                        </table>
                    {% endif %}
                {% endfor %}

                <!-- =======================  RESUME CERTIFICATIONS ======================= -->
            
                {% if cert.Certification1 or cert.Certification2 or cert.Certification3 %}
                    <p class="badge text-dark"> Certification </p> <p class="hr_style"></p>
                
                    {% for i in range(1, 4) %}
                        {% if cert['Certification'~i] %}
                            <table class="table-layout">
                                <tr>
                                    <td>
                                        <span class="label">Certification:</span> 
                                        <p class="label-data">{{ cert['Certification'~i] }}</p>
                                    </td>
                                    <td>
                                        <span class="label">Expires:</span> 
                                        <p class="label-data">{{ cert['Cert' ~i~ '_Date'] }}</p>
                                    </td>
                                </tr>
                            </table>
                        {% endif %}
                    {% endfor %}
                {% endif %}

                <!-- =======================  RESUME PROJECTS ======================= -->
                {% if proj.Project1 or proj.Project2 or proj.Project3 %}
                    <p class="badge text-dark"> Projects </p> <p class="hr_style"></p>
                
                    {% for i in range(1, 4) %}
                        {% if proj['Project'~i] and proj['Prj_Desc'~i] %}
                            <table class="table-layout">
                                <tr>
                                    <td colspan="5" align="center">
                                        <span class="pill skill-color"> Project {{i}} </span>
                                    </td>
                                </tr>

                                <tr>
                                    <td>
                                        <span class="label">Name:</span> 
                                        <p class="label-data">{{ proj['Project'~i] }}</p>
                                    </td>
                                    <td>
                                        <span class="label">Access link:</span> 
                                        <p class="label-data">{{ proj['Link'~i] }}</p>
                                    </td>
                                </tr>
                                <tr> <td></td> </tr>

                                <tr>
                                    <td colspan="5">
                                        <span class="label">Description:</span> 
                                        <p class="label-data">{{ proj['Prj_Desc'~i] }}</p>
                                    </td>
                                </tr>
                            </table>
                        {% endif %}
                    {% endfor %}
                {% endif %}

                <!-- =======================  RESUME SKILLS ======================= -->
                {% if (front.Project1 or front.Project2 or front.Project3) 
                    or (back.Backend_Lang1 or back.Backend_Lang2 or back.Backend_Lang3)
                    or (databases.Database1 or databases.Database2 or databases.Database3)
                    or (clouds.Cloud1 or clouds.Cloud2 or clouds.Cloud3)  %}

                    <p class="badge text-dark"> Skills </p> <p class="hr_style"></p>

                
                    <table class="table-layout">
                        {% if front.Frontend_Lang1 or front.Frontend_Lang2 or front.Frontend_Lang3 %}
                            <tr>
                                <td colspan="5" align="center">
                                    <div class="text-center">
                                        <span class="pill skill-color"> Front-End </span>
                                    </div>
                                </td>
                            </tr>

                            {% for i in range(1, 4) %}
                                {% if front['Frontend_Lang'~i] %}
                                    <tr>
                                        <td colspan="2" align="center">
                                            <span class="label">Language:</span> 
                                            <p class="label-data">{{ front['Frontend_Lang'~i] }}</p>
                                        </td>

                                        <td colspan="1" align="center">
                                            <span class="label">Experience:</span> 
                                            <p class="label-data">{{ front['Exp_Frontend'~i] or 0 }} years</p>
                                        </td>
                                    </tr>
                                    <tr> <td></td> </tr>
                                {% endif %}
                            {% endfor %}
                        {% endif %}

                        {% if back.Backend_Lang1 or back.Backend_Lang2 or back.Backend_Lang3 %}
                            <tr>
                                <td colspan="5" align="center">
                                    <span class="pill skill-color"> Back-End </span>
                                </td>
                            </tr>

                            {% for i in range(1, 4) %}
                                {% if back['Backend_Lang'~i] %}
                                    <tr>
                                        <td colspan="2" align="center">
                                            <span class="label">Language:</span> 
                                            <p class="label-data">{{ back['Backend_Lang'~i] }}</p>
                                        </td>

                                        <td colspan="1" align="center">
                                            <span class="label">Experience:</span> 
                                            <p class="label-data">{{ back['Exp_Backend'~i] or 0 }} years</p>
                                        </td>
                                    </tr>
                                    <tr> <td></td> </tr>
                                {% endif %}
                            {% endfor %}
                        {% endif %}

                        {% if databases.Database1 or databases.Database2 or databases.Database3 %}
                            <tr>
                                <td colspan="5" align="center">
                                    <span class="pill skill-color"> Database </span>
                                </td>
                            </tr>

                            {% for i in range(1, 4) %}
                                {% if databases['Database'~i] %}
                                    <tr>
                                        <td colspan="2" align="center">
                                            <span class="label">Language:</span> 
                                            <p class="label-data">{{ databases['Database'~i] }}</p>
                                        </td>

                                        <td colspan="1" align="center">
                                            <span class="label">Experience:</span> 
                                            <p class="label-data">{{ databases['Exp_Database'~i] or 0 }} years</p>
                                        </td>
                                    </tr>
                                    <tr> <td></td> </tr>
                                {% endif %}
                            {% endfor %}
                        {% endif %}
                        
                        {% if clouds.Cloud1 or clouds.Cloud2 or clouds.Cloud3 %}
                            <tr>
                                <td colspan="5" align="center">
                                    <span class="pill skill-color"> Cloud </span>
                                </td>
                            </tr>
                        
                            {% for i in range(1, 4) %}
                                {% if clouds['Cloud'~i] %}
                                    <tr>
                                        <td colspan="2" align="center">
                                            <span class="label">Language:</span> 
                                            <p class="label-data">{{ clouds['Cloud'~i] }}</p>
                                        </td>

                                        <td colspan="1" align="center">
                                            <span class="label">Experience:</span> 
                                            <p class="label-data">{{ clouds['Exp_Cloud'~i] or 0 }} years</p>
                                        </td>
                                    </tr>
                                    <tr> <td></td> </tr>
                                {% endif %}
                            {% endfor %}
                        {% endif %}
                    </table>
                {% endif %}

                <!-- =======================  RESUME PROJECTS ======================= -->
                {% if clouds.Other_Skills %}  
                    <p class="badge text-dark"> Other Skills </p> <p class="hr_style"></p>

                    <table class="table-layout">
                        <tr>
                            <td colspan="5">
                                <p class="label-data">{{ clouds.Other_Skills }}</p>
                            </td>
                        </tr>
                    </table>
                {% endif %}
            </body>
        </html
    
    """

    temlate= Template(html_resume_template_str)
    render_html= temlate.render(
        dev= dev, edu= edu, cert= cert, front= front, back= back, 
        databases= databases, clouds= clouds, works= works, proj= projects
    )

    # processing binary into memory RAM
    pdf_buffer= io.BytesIO()
    pisa_status= pisa.CreatePDF(io.StringIO(render_html), dest= pdf_buffer)

    if pisa_status.err:
        return { "error": "Could not compile HTML to PDF bytes!" }

    pdf_bytes= pdf_buffer.getvalue()
    return pdf_bytes