from datetime import datetime, timezone
import uuid
from services import http_responses
from data_model.models import Post, Developer
from sqlalchemy.orm import Session
from sqlalchemy import or_, select


# function to list all posts
def list_posts(db: Session):
    result= db.execute(select(Post))

    if result:
        return result.scalars().all()
    else:
        return http_responses.status_204_no_content("bi bi-clipboard-x-fill", "No post found <br> Try again!")



# function to create a new post
async def add_post(data, developer, db: Session):
    query= db.execute(select(Post).where(Post.Title == data.get("title")))
    post_found= query.scalar()

    if post_found:
        return http_responses.status_406_not_acceptable("bi bi-textarea-t", "Duplicated post 'Title' not allowed!")
    else:
        post= Post(
            Title= data.get("title"), 
            Tag= data.get("tags_selected"),
            Question= data.get("question"),
            Posted= datetime.now(timezone.utc), 
            Last_Update= datetime.now(timezone.utc),
            dev_id= developer.Id
        )
        
        db.add(post)
        db.commit()
        db.refresh(post)
        return post



# function to update a post
async def update_post(post_id, data, db: Session):
    query= select(Post).where(Post.Id == post_id)
    post_updated= db.execute(query).scalar()

    if not post_updated:
        return http_responses.status_404_not_found("bi bi-sign-no-parking", f"Post with ID:{id} not found!")
    else:
        post_updated.Title= data.get('edit-title')
        post_updated.Tag= data.get('edit-tags')
        post_updated.Question= data.get('edit-question')
        post_updated.Last_Update= datetime.now(timezone.utc)
            
        db.commit()
        return http_responses.status_200_ok("bi bi-check2-circle", f"'{post_updated.Title}' updated successfully")



# getting post by ID
async def get_post_by_id(post_id, db: Session):
    query= select(Post).where(Post.Id == post_id)
    post_found= db.execute(query).scalar()

    if post_found:
        return post_found
    else:
        return http_responses.status_404_not_found("bi bi-credit-card-2-front", f"No post found with ID: {post_id}")



# function to delete a post
def remove_post(id: int, db: Session):
    query= db.execute(select(Post).where(Post.Id == id))
    post_found= query.scalar()

    if post_found:
        db.delete(post_found)
        db.commit()

        return http_responses.status_200_ok("", f"Post ID:{id} removed succesfully")
    else:
        raise http_responses.status_404_not_found("bi bi-sign-no-parking", f"Post with ID:{id} not found!")



# function to find post to be edit
async def get_post_to_edit(id, db: Session):
    query= db.execute(select(Post).where(Post.Id == id))
    post_found= query.scalar()

    if not post_found:
        return http_responses.status_404_not_found("bi bi-sign-no-parking", f"Post with ID:{id} not found!")
    else:
        return post_found



# function to list post by Title, Tag, Author 
async def search_post(post_param, author_id, db: Session):
    param= f"%{post_param}%"

    if isinstance(author_id, str):
        author_uuid= uuid.UUID(author_id)
    else:
        author_uuid= author_id

    query= select(Post).join(Developer).where(or_(
        Post.dev_id == author_uuid,
        Post.Title.ilike(param), 
        Post.Tag.ilike(param), 
        Developer.First_Name.ilike(param), 
        Developer.Last_Name.ilike(param))).order_by(Post.Id.desc())
    
    posts= db.execute(query).scalars().all()

    if posts:
        return posts
    else:
        return False
        # http_responses.status_404_not_found("bi bi-credit-card-2-front", f"No post found for parameter: {post_param} !")



#function to update post to close state
def post_close(id, db: Session):
    query= select(Post).where(Post.Id == id)
    post_found= db.execute(query).scalar()
   
    if post_found:
        post_found.Opened= False
        post_found.Closed_Date= datetime.now(timezone.utc)
            
        db.commit()
        db.refresh(post_found)
        
        return http_responses.status_200_ok("bi bi-check2-circle", f"Post '{post_found.Title}' closed successfully")
    else:
        return http_responses.status_404_not_found("bi bi-sign-no-parking", f"Post with ID:{id} not found!")