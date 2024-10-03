from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from sqlalchemy.orm import Session
import uuid
import os

from sqlalchemy import select, or_
import requests
from passlib.context import CryptContext
import bcrypt
import random
# from utils.minio_util import upload_file



from sqlalchemy.future import select

from models.itemsModel import *
from schemas.itemsSchema import *
from database.databaseConnection import SessionLocal
# from security.auth import *
# from security.error_handling import *
# from security.auth_bearer import jwtBearer

# # logs
# from logging_lib import LogConfig
# from logging.config import dictConfig
import logging

# email
# from emails import *
# from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
# from smtplib import SMTPException
import os
import string


# file upload
from fastapi import UploadFile,status, File, Form
# from utils.minio_util import upload_file

import re
from sqlalchemy.sql import func
import base64


# # loging config
# dictConfig(LogConfig().dict())
logger = logging.getLogger("Humanity App")



# create a connection to the database
async def get_db():
    db = SessionLocal()
    try:
        yield db

    finally:
        await db.close()

db_dependency = Annotated[Session, Depends(get_db)]




router = APIRouter()




# Create item
@router.post("/item/create_item") #done and used
async def create_item(db: db_dependency, item_data: Items_Model): #item_data: Items_Model = Depends(Items_schema)
    logger.info("Endpoint: create_item")

    
    # Create a new item instance
    new_item_data = Item(
        name=item_data.name,
        category=item_data.category,
        description=item_data.description,
        phone_number=item_data.phone_number,
        email=item_data.email,
        location=item_data.location,
        yearsUsed=item_data.yearsUsed,
        username=item_data.username,
    )

    print("1")
    print(new_item_data.name)
    # Add the new item to the database session and commit
    db.add(new_item_data)
    print("2")
    await db.commit()  # Commit to save the item to get its ID
    # await db.refresh(new_item_data) 

    # logger.info("Item created and saved in the database with ID: %s", new_item_data.id)

    
    return {"message": "Item creation successful", "Item_data" : new_item_data}



# Create item image
@router.post("/item/create_item_image")   #done and used
async def create_item_image(db: db_dependency, item_id : str = Form(...),  file: UploadFile = File(...)):


    # Validate file type (e.g., images only)
    allowed_file_types = ["image/jpeg", "image/png", "image/gif"]
    if file.content_type not in allowed_file_types:
        raise HTTPException(status_code=400, detail="Unsupported file type. Allowed types: jpeg, png, gif.")
    
    # Read the file content as binary data
    try:
        image_data = await file.read()
        
        # Convert to Base64
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        # Create an image instance and associate it with the new item
        new_image = ItemImage(
            item_id=item_id,
            image=image_base64,
            image_filename=file.filename
        )
        
        # Add the new image to the database
        db.add(new_image)
        await db.commit()

        logger.info("Item image created and saved in the database with ID: %s", new_image.id)

        return {
            "message": "Item image creation successful",
            "item_image_id": new_image.id,
            "filename": file.filename
        }             


    except Exception as e:
        # Handle errors (like commit failures)
        logger.error(f"Error creating item image: {e}")
        raise HTTPException(status_code=500, detail="Failed to create item image")



        
    # #  Read the file content as binary data
    # image_data = await file.read()
    
    # # Convert to Base64
    # image_base64 = base64.b64encode(image_data).decode('utf-8')
    
    # # Create an image instance and associate it with the new item
    # new_image = ItemImage(
    #     item_id=item_id,  # Use new_item_data.id here
    #     image=image_base64,
    #     image_filename=file.filename
    # )
    
    # # Add the new image to the database
    # db.add(new_image)
    # await db.commit()
    
    # logger.info("Item image created and saved in the database with ID: %s", new_image.id)

    # return {"message": "Item image creation successful", "item_image_id": new_image.id}



# get all_items
@router.get("/item/get_all_items") 
async def get_all_items( db: db_dependency):

    items = await db.execute(select(Item))
    items_data = items.scalars().all()
    
    if items_data  is None:
        raise HTTPException(status_code=200, detail="No user data exists", data = items_data)
    
    return items_data 

# get all_items_Images
@router.get("/item/get_items_images_by_id/{item_id}") 
async def get_items_images_by_id( item_id : str, db: db_dependency):


    item_image = await db.execute(select(ItemImage).where(ItemImage.item_id == item_id))
    item_image_data = item_image.scalar()
    
    if item_image_data  is None:
        raise HTTPException(status_code=200, detail="item with provided name does not exist", data = item_image_data)
    
    return item_image_data 
    

# get item by id

@router.get("/item/get_item_by_id/{item_id}")
async def get_item_by_id(item_id: uuid.UUID, db: db_dependency):
    # Get the item by its ID
    item = await db.get(Item, item_id)
    
    if item is None:
        raise HTTPException(status_code=404, detail="Item with the given ID does not exist")

    # Fetch the corresponding image
    item_image_query = await db.execute(select(ItemImage).where(ItemImage.item_id == str(item_id)))
    item_image_data = item_image_query.scalar()

    if item_image_data is None:
        raise HTTPException(status_code=404, detail="Item image with the given ID does not exist")
    
    # Create the item information object
    item_info = {
        "id": str(item.id),
        "name": item.name,
        "description": item.description,
        "phone_number": item.phone_number,
        "location": item.location,
        "image": f"data:image/png;base64,{item_image_data.image}" if item_image_data.image else None,
        "image_filename": item_image_data.image_filename if item_image_data.image_filename else None
    }

    return item_info  # Return the item information as a dictionary

    



@router.get("/item/get_all_items_with_images") # done and used
async def get_all_items_with_images(db: db_dependency):
    # Get all items
    items = await db.execute(select(Item))
    items_data = items.scalars().all()
    
    if not items_data:
        raise HTTPException(status_code=404, detail="No items found")

    # Prepare a list to hold items with images
    items_with_images = []
    
    for item in items_data:
        # For each item, get the associated image
        item_image_query = await db.execute(select(ItemImage).where(ItemImage.item_id == str(item.id)))
        item_image_data = item_image_query.scalar()
        
        # Add item details and image to the result
        item_info = {
            # "id": item.id,
            # "name": item.name,
            # "description": item.description,
            # "phone_number": item.phone_number,
            "id": item.id,
            "name": item.name,
            "description": item.description,
            "phone_number": item.phone_number,
            "category": item.category,
            "email" : item.email,
            "yearsUsed" : item.yearsUsed,
            "location" : item.location,
            "image": f"data:image/png;base64,{item_image_data.image}" if item_image_data else None,
            "image_filename": item_image_data.image_filename if item_image_data else None
        }
        items_with_images.append(item_info)

    return items_with_images



@router.get("/item/get_all_items_with_images_by_username/{username}") # 
async def get_all_items_with_images_by_username(username: str , db: db_dependency):
    # Get all items
    items = await db.execute(select(Item).where(Item.username == username))
    items_data = items.scalars().all()
    
    if not items_data:
        raise HTTPException(status_code=404, detail="No items found")

    # Prepare a list to hold items with images
    items_with_images = []
    
    for item in items_data:
        # For each item, get the associated image
        item_image_query = await db.execute(select(ItemImage).where(ItemImage.item_id == str(item.id)))
        item_image_data = item_image_query.scalar()
        
        # Add item details and image to the result
        item_info = {
            "id": item.id,
            "name": item.name,
            "description": item.description,
            "phone_number": item.phone_number,
            "category": item.category,
            "email" : item.email,
            "yearsUsed" : item.yearsUsed,
            "location" : item.location,
            "image": f"data:image/png;base64,{item_image_data.image}" if item_image_data else None,
            "image_filename": item_image_data.image_filename if item_image_data else None
        }
        items_with_images.append(item_info)

    return items_with_images



# get item by name
@router.get("/item/get_item_by_name")
async def get_item_by_name(item_name: str ,db: db_dependency):

    item = await db.execute(select(Item).where(Item.name == item_name))
    item_data = item.scalar()
    
    if item_data  is None:
        raise HTTPException(status_code=200, detail="item with provided name does not exist", data = item_data)
    
    return item_data 



# get item by location
@router.get("/item/get_item_by_location")
async def get_item_by_location(item_location: str ,db: db_dependency):

    item = await db.execute(select(Item).where(Item.location == item_location))
    item_data = item.scalars().all()
    
    if item_data  is None:
        raise HTTPException(status_code=200, detail="item with provided name does not exist", data = item_data)
    
    return item_data 



# get total number of items
@router.get("/item/get_total_number_of_items")
async def get_total_number_of_items(db: db_dependency):

    result = await db.execute(select(func.count(Item.id)))
    total_items = result.scalar()  

    return {"total_items": total_items}


# update item by id


@router.patch("/item/update_individual_item_fields/{item_id}")
async def update_item_details(item_id: str, user_input: dict, db: db_dependency):

    
    logger.info("Endpoint : update_user")
    
# await db.execute(select(Item).where(str(Item.id) == item_id))
    # query for user data
    item = await db.execute(select(Item).where(Item.id == uuid.UUID(item_id)))
    item_data = item.scalar() 
    print(item_data)
    print(item_data.id)
    logger.info("User data queried successfully")

        
    # convert user data and user input into a dictionary
    converted_item_data = item_data.__dict__
    inputs = user_input
       
        # copy converted user data
    result = converted_item_data.copy() 

        # check if user input key is found in the converted user data, if true initialize the converted use data key with the user inputs value
    for key, value in inputs.items():
        if key in result:
            result[key] = value  
            
        # replace the old user data with the new user data
    for key, value in result.items():
        setattr(item_data, key, value)
            
    logger.info("item data ready for storage")
        

    # save user data in database
    db.add(item_data)
    await db.commit()
    await db.refresh(item_data)
    logger.info("item data updated")
        
        
    return item_data
    


    
@router.patch("/item/update_item_image/{item_image_id}")
async def update_item_image(item_image_id: uuid.UUID, db: db_dependency, file: UploadFile = File(...)):

    
    logger.info("Endpoint : update_item_image")
    

    # query for user data
    item_image_data = await db.get(ItemImage, item_image_id)
    logger.info("Item image data queried successfully")

    image_data = await file.read()
    
    # Convert to Base64
    image_base64 = base64.b64encode(image_data).decode('utf-8')
    
    item_image_data.image_filename = file.filename
    item_image_data.image = image_base64

    db.add(item_image_data)
    await db.commit()
    await db.refresh(item_image_data)

    return "Item image updated successfully"


# delete item by id
@router.delete("/item/delete_item_by_id/{item_id}")
async def delete_item_by_id(item_id: str, db: db_dependency):

    item = await db.execute(select(Item).where(Item.id == uuid.UUID(item_id)))
    item_data = item.scalar_one_or_none()
    
    if item_data is None:
        raise HTTPException(status_code=404, detail="Item not found")

    item_image = await db.execute(select(ItemImage).where(ItemImage.item_id == str(item_id)))
    item_image_data = item_image.scalar_one_or_none()
    # Delete the user
    await db.delete(item_data)
    await db.delete(item_image_data)

    await db.commit()


    return "Item deleted successfully"








#     // Fetch items and initialize pagination
# async function fetchItems(isInitialLoad = false) {
#     const loadingMessage = '<h4>Loading Items...</h4>';

#     if (isInitialLoad) {
#         // Scenario 1: When the page loads, show loading in itemsContainer
#         const itemsContainer = document.getElementById('itemsContainer');
#         itemsContainer.innerHTML = loadingMessage;

#         try {
#             const response = await fetch('/item/get_all_items_with_images');

#             // Check if the response is okay (status in the range 200-299)
#             if (!response.ok) {
#                 throw new Error(`HTTP error! Status: ${response.status}`);
#             }

#             const items = await response.json();
#             renderItems(items); // Assuming renderItems() will render the items
#             setupPagination(); // Assuming setupPagination() will handle pagination

#         } catch (error) {
#             console.error('Error fetching items:', error);
#             itemsContainer.innerHTML = 'Error loading items';
#         }

#     } else {
#         // Scenario 2: When the overview button is clicked, show loading in dynamicContent
#         const dynamicContent = document.getElementById('dynamicContent');
#         dynamicContent.innerHTML = loadingMessage;

#         try {
#             const response = await fetch('/item/get_all_items_with_images');

#             // Check if the response is okay (status in the range 200-299)
#             if (!response.ok) {
#                 throw new Error(`HTTP error! Status: ${response.status}`);
#             }

#             const items = await response.json();
#             renderItems(items); // Render items in dynamicContent
#             setupPagination();

#         } catch (error) {
#             console.error('Error fetching items:', error);
#             dynamicContent.innerHTML = 'Error loading items';
#         }
#     }
# }
        
# // Call fetchItems(true) when the page loads
# window.addEventListener('load', function() {
#     fetchItems(true); // This is for the initial page load
# });

# // Adding event listener for the 'overview' button click
# // const overviewButton = document.getElementById('v-pills-overview-tab');
# // overviewButton.addEventListener('click', function() {
# //     fetchItems(false); // This is for the button click
# // });
