import uuid
from io import BytesIO
from pathlib import Path
from PIL import Image, ImageOps
from sqlalchemy.orm import Session
from data_model.models import Developer


# setting the directory to save images
DEV_IMG_DIR= Path("uploaded_dev_images")
COMP_IMG_DIR= Path("uploaded_comp_images")



# function to verify and process images before save
def image_process(directory, content: bytes):
    with Image.open(BytesIO(content)) as original_img:
        # fixing orientation to prevent image rotating 
        img= ImageOps.exif_transpose(original_img)

        # resize image and keeping its quality
        img= ImageOps.fit(img, (320, 320), method=Image.Resampling.LANCZOS)

        # convert image to RGBA
        if img.mode in ("RGBA", "LA", "P"):
            img= img.convert("RGBA")

        # create a image unique name
        file_name= f"{uuid.uuid4().hex}.png"
        file_path= directory / file_name
        
        # check if directory exits
        directory.mkdir(parents=True, exist_ok=True)

        # save the Image with generated name into the directory
        img.save(file_path, "PNG", quality=85, optimize=True)
       
    return file_name



# function to delete old profile image
def image_deletion(file_name: str | None, directory, model_obj, db:Session) -> bool:
    if file_name is None:
        return False


    file_path= directory / file_name

    # if we find the image path we delete it
    if file_path.exists():
        file_path.unlink()

        # # add default image to profile image
        if type(model_obj) == Developer:
            model_obj.Image= "unisex.png" 
            model_obj.Img_Path= "uploaded_dev_images/unisex.png"


        db.commit()
        db.refresh(model_obj)

        return True
    else:
        return False