
import os, uuid
from collections import defaultdict
from post_dao import post_dao, answer_dao, reply_dao
from data_model.models import Developer, Post
from data_model.schemas import New_Post, Post_Response
from services import helper, http_responses
from services.authentication import get_current_user
from services.db_connection import get_db
from routers.login import limiter
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Request, status


public_api= APIRouter()
restrict_api= APIRouter() 
search_post_api= APIRouter()

# globals variables
languages= ['Azure','AWS','Bootstrap','C_sharp','CSS','C_pp','FastAPI','Flask','HTML','Java','JS','MySQL','Python','Rust','SQL','Swift']


##############################################################################################################################
########################################## GLOBALS FUNCTIONS FOR ALL ROUTERS FILES  ##########################################

# function to list all posts
async def load_posts(page, list, request, msg, cur_user, db):
    posts_list= post_dao.list_posts(page, list, db)

    return helper.templates.TemplateResponse(
        "posts.html", {
            'request': request, 'languages': languages, 'user_in': cur_user, 'posts': posts_list,
            'msg': msg, 'allowed_limit': sorted(helper.ALLOWED_LIMITS), 
            'website_url': os.environ.get("website_url")
        }
    )


# function to load post view content
async def load_post_view_content(request, post_id, result, cur_user, db):
    post= await post_dao.get_post_by_id(post_id, db)
    answers= await answer_dao.answers_by_post_id(post_id, db) or []
    replies=  await reply_dao.replies_by_post_id(post_id, db) or []
    replies_by_answer= defaultdict(list)

    for reply in replies:
        replies_by_answer[reply.answer_id].append(reply)

    # geting replies answer ids
    replies_answer_ids= {r.answer_id for r in replies}

    return helper.templates.TemplateResponse(
        "view_post.html", {
            'request': request, 'languages': languages, 'user_in': cur_user, 'post': post, 'result': result,
            'title': request.query_params.get('title'), 'allowed_limit': helper.ALLOWED_LIMITS, 
            'answers': answers, 'replies_by_answer': replies_by_answer, 'replies_ids': replies_answer_ids
        }
    )


# function to load posts founs by tags or author
async def load_posts_found(request, posts_list, cur_user, tag): 
    return helper.templates.TemplateResponse(
        "posts_found.html", {
            'request': request, 'posts': posts_list, 'tag': tag, 'langs': languages,
            'user_in': cur_user, 'allowed_limit': sorted(helper.ALLOWED_LIMITS)
        }
    )   

##############################################################################################################################
############################################### PUBLIC FUNCTIONS FOR ALL USERS  ##############################################

# function to list all posts
@public_api.get('', response_model=Post_Response, include_in_schema= False, status_code=status.HTTP_200_OK)
async def list_posts(request: Request, page: int= 1, list: int= 6, 
                    db: Session= Depends(get_db), cur_user: Developer= Depends(get_current_user)):

    return await load_posts(page, list, request, '', cur_user, db)



# function to list post by ID
@public_api.get('/{post_id}', response_model=Post_Response, include_in_schema= False, status_code=status.HTTP_302_FOUND)
async def view_post(request: Request, post_id: uuid.UUID, db: Session= Depends(get_db), 
                    cur_user: Developer= Depends(get_current_user)):
    result= ''
    return await load_post_view_content(request, post_id, result, cur_user, db)
    


# function to search posts by tag
@search_post_api.get('', status_code=status.HTTP_200_OK, include_in_schema= False)
async def post_search(request: Request, tag: str | None= None, author_id: uuid.UUID | int=0, 
                    page: int= 1, list: int= 6, cur_user: Developer= Depends(get_current_user), db: Session= Depends(get_db)):
    # list all posts found and return as paginated
    input_param= request.query_params.get('input_param')
    data_set= await post_dao.search_post(languages, tag, input_param, page, list, author_id, db)

    if not tag: tag= input_param

    if data_set:
        return await load_posts_found(request, data_set, cur_user, tag)
    else:
        if input_param in languages:
            tag= input_param

        if tag == 'C_sharp': tag= 'C#' 
        elif tag == 'C_pp': tag= 'C++'
        return await load_posts(page, list, request, f"No {tag} post found!", cur_user, db)


##############################################################################################################################
################################ RESTRICTED FUNCTIONS FOR LOGGED IN DEVELOPERS OR EMPLOYEERS  ################################
# function to add new question
@restrict_api.get('/post-question/{post_id}', include_in_schema= False)
async def post_question(post_id: uuid.UUID | int, request: Request, cur_user: Developer= Depends(get_current_user), 
                   db: Session= Depends(get_db)):
    edit_post= None

    # if user try to update a post search the post to be updated
    if post_id != 0:
        edit_post= await post_dao.get_post_to_edit(post_id, db)

    return helper.templates.TemplateResponse("post_question.html", 
                                            {'request': request, 'edit_post': edit_post, 'data': '', 
                                            'user_in': cur_user, 'languages': languages, 'result': ''})

@restrict_api.post('/post-question/{post_id}', response_model=New_Post, status_code=status.HTTP_201_CREATED, include_in_schema=True)
@limiter.limit("3/hour") # limit 3 post request per hour
async def post_question(post_id: uuid.UUID | int, request: Request, 
                        cur_user: Developer= Depends(get_current_user), db: Session= Depends(get_db)):
    if cur_user:
        # calling function to commit the new post in to DB
        post= await post_dao.add_post(request.form(), cur_user, db)

        if type(post) is not Post:
            return helper.templates.TemplateResponse(
                "post_question.html", {
                    'request': request, 'edit_post': '', 'post_id': 0, 'data': request.form(),
                    'result': post, 'languages': languages, 'user_in': cur_user, 'post_id': post_id
                }
            )
        else:
            result= http_responses.status_200_ok("bi bi-check2-circle", f"'{post.Title}' added successfully")
            return await load_post_view_content(request, post.Id, result, cur_user, db)
    else:
        return await helper.login_expired()
    


# function to update question
@restrict_api.post('/post-question/update-post/{post_id}', include_in_schema= False)
@limiter.limit("5/hour") # limit 5 update request per hour
async def update_post(post_id: uuid.UUID, request: Request, cur_user: Developer= Depends(get_current_user), 
                    db: Session= Depends(get_db)):
    edit_post= None

    if cur_user:
        data= await request.form()
        result= await post_dao.update_post(post_id, data, db)

        if result.status_code != 200:
            return helper.templates.TemplateResponse(
                "post_question.html", {
                    'request': request, 'edit_post': edit_post, 'result': result, 'data': data,
                    'post_id': post_id, 'languages': languages, 'user_in': cur_user
                }
            )
        else:
            return await load_post_view_content(request, post_id, result, cur_user, db)
    else:
        return await helper.login_expired()
    


# function to close a post by ID
@restrict_api.post('/close_post/{post_id}', status_code=status.HTTP_200_OK, include_in_schema= False)
async def close_post(post_id: uuid.UUID, request: Request, cur_user: Developer= Depends(get_current_user), 
                           db: Session= Depends(get_db)):
    if cur_user:
        result= post_dao.post_close(post_id, db)
        return await load_post_view_content(request, post_id, result, cur_user, db)
    else:
        return helper.login_expired()
    


# function to delete a post by ID
@restrict_api.delete('/{post_id}', include_in_schema= False)
def delete_post(post_id: uuid.UUID, db: Session= Depends(get_db)):
    return post_dao.remove_post(post_id, db)



# function to list all posts by developer
@restrict_api.get('/my_posts/{page}&{list}', include_in_schema= False)
async def my_posts(request: Request, page: int= 1,  list: int=4, db: Session= Depends(get_db), 
                    cur_user: Developer= Depends(get_current_user)):
    if cur_user:
        result= await post_dao.search_post(languages, None, None, page, list, cur_user.Id, db)

        return helper.templates.TemplateResponse(
            "my_posts.html", {
                'request': request, 'result': result, 'my_posts': result,
                'user_in': cur_user, 'allowed_limit': helper.ALLOWED_LIMITS
            }
        )
    else:
        return await helper.login_expired()