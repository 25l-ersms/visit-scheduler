from fastapi import APIRouter

from visit_scheduler.app.models.models import InsertModel
from visit_scheduler.es_utils.search import get_all
from visit_scheduler.es_utils.add import add_element

router = APIRouter(
    prefix="/visits",
    tags=["visits"],
    responses={404: {"description": "Not found"}}
)


@router.get("/all", response_model=None) # TODO change to real response model
async def add_comment():
    return get_all()

@router.post("/add", response_model=None) # TODO change to real response model
async def add_comment(data: InsertModel):
    return add_element(data)