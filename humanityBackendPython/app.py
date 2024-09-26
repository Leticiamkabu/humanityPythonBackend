
from dotenv import load_dotenv

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from controllers import authenticationController
from fastapi_login import LoginManager






SECRET = "super-secret-key"
manager = LoginManager(SECRET, '/login')




load_dotenv()



app = FastAPI(
    title= "Humanity App",
    version="0.0.1",
    description="FastAPI Application",
    openapi_tags=[
        {
            "name": "Home",
            "description": "Check health of the API"
        }
    ]
)



# from decouple import config
# JWT_SECRET = config("secret")
# JWT_ALGORITHM = config("algorithm")



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(authenticationController.router, tags=["Authentication"])
