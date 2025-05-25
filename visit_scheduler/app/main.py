import threading
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from visit_scheduler.kafka_utils.consumer import enable_listen_to_kafka
from visit_scheduler.package_utils.logger_conf import logger

from visit_scheduler.app.routers import visits
from visit_scheduler.package_utils.settings import VisitSchedulerSettings

# from fastapi.security import OAuth2PasswordBearer
@asynccontextmanager
async def lifespan(turbo_app: FastAPI) -> AsyncGenerator[None, Any]:
    logger.info("Starting Kafka consumer thread...")
    thread = threading.Thread(target=enable_listen_to_kafka, daemon=True)
    thread.start()
    yield  # App runs while this context is active
    logger.info("App is shutting down.")

app = FastAPI(root_path=VisitSchedulerSettings().ROOT_PATH, lifespan=lifespan)
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token") # TODO setup OAuth and uncomment this line

app.include_router(visits.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
