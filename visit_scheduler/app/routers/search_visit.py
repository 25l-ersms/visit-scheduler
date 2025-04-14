from elastic_transport import ObjectApiResponse
from fastapi import APIRouter

from visit_scheduler.app.models.models import InsertModel, SendModel
from visit_scheduler.es_utils.add import add_element
from visit_scheduler.es_utils.search import get_all
from visit_scheduler.kafka_utils.common import send_message

router = APIRouter(prefix="/visits", tags=["visits"], responses={404: {"description": "Not found"}})


@router.get("/all", response_model=None)  # TODO change to real response model
async def get_all_slots() -> ObjectApiResponse:
    return get_all()


@router.post("/add", response_model=None)  # TODO change to real response model
async def add_comment(data: InsertModel) -> None:
    return add_element(data)


@router.post("/send-msg", response_model=None)  # TODO change to real response model
async def send_msg(model: SendModel) -> None:
    return send_message(model.msg)
