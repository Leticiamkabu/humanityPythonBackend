from pydantic import BaseModel
from enum import Enum


class ItemCategory(str, Enum):
    CLOTHS = "CLOTHS"
    HOME_APPLIANCES = "HOME_APPLIANCES"
    ELECTRONICS = "ELECTRONICS"
    FURNITURE = "FURNITURE"
    CONSTRUCTION_TOOLS = "CONSTRUCTION_TOOLS"
    BOOKS = "BOOKS"
    LEARNING_MATERIALS = "LEARNING_MATERIAL"
    

  
class YearsUsed(str, Enum):
    ONE_TO_FIVE_YEARS = "ONE_TO_FIVE_YEARS"
    SIX_TO_TEN_YEARS = "SIX_TO_TEN_YEARS"
    ELEVEN_AND_ABOVE = "ELEVEN_AND_ABOVE"
    
    



class Items(BaseModel):
    name: str
    category: ItemCategory
    description: str
    phone_number:str
    email: str
    location: str
    yearsUsed: YearsUsed
    username: str
    # picture: str

# name: str = Form(...),
#     category: ItemCategory = Form(...),
#     description: str = Form(...),
#     phone_number: str = Form(...),
#     email: str = Form(...),
#     location: str = Form(...),
#     yearsUsed: YearsUsed = Form(...),
#     userName: str = Form(...),



    
