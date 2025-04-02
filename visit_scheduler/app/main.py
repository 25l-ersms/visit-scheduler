from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from visit_scheduler.app.routers import search_visit

# from fastapi.security import OAuth2PasswordBearer


app = FastAPI()
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token") # TODO setup OAuth and uncomment this line

app.include_router(search_visit.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
