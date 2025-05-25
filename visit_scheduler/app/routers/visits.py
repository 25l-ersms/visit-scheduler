from elastic_transport import ObjectApiResponse
from fastapi import APIRouter

from visit_scheduler.app.models.models import SearchVendorModel, AddTimeSlotModel
from visit_scheduler.es_utils.handler import search_vendors, add_time_slot, get_all_time_slots
from visit_scheduler.es_utils.models import TimeSlotModel, TimeSlotStatus

router = APIRouter(prefix="/visits", tags=["visits"], responses={404: {"description": "Not found"}})


@router.get("/all", response_model=None)
async def get_all_slots() -> ObjectApiResponse:
    return get_all_time_slots()


@router.post("/search", response_model=None)
async def end_search_vendors(data: SearchVendorModel) -> None:
    return search_vendors(data)

@router.post("/add_time_slot", response_model=None)
async def end_add_time_slot(data: AddTimeSlotModel) -> None:
    vendor_id = "1" # change to reading from jwt token
    return add_time_slot(
        TimeSlotModel(vendor_id=vendor_id, start_time=data.start_time, end_time=data.end_time, status=TimeSlotStatus.AVAILABLE)
        )
