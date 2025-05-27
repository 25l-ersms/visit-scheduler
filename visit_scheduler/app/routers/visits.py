from typing import Annotated

from elastic_transport import ObjectApiResponse
from fastapi import APIRouter, Depends

from visit_scheduler.app.models.models import AddTimeSlotModel, SearchVendorModel, UserSessionData
from visit_scheduler.app.security import get_current_user
from visit_scheduler.es_utils.handler import add_time_slot, get_all_time_slots, search_vendors
from visit_scheduler.es_utils.models import TimeSlotModel, TimeSlotStatus

router = APIRouter(prefix="/visits", tags=["visits"], responses={404: {"description": "Not found"}})


@router.get("/all", response_model=None)
async def get_all_slots(
    user: UserSessionData = Annotated[UserSessionData, Depends(get_current_user)],
) -> ObjectApiResponse:
    return get_all_time_slots()


@router.post("/search", response_model=None)
async def end_search_vendors(
    data: SearchVendorModel, user: UserSessionData = Annotated[UserSessionData, Depends(get_current_user)]
) -> None:
    return search_vendors(data)


@router.post("/add_time_slot", response_model=None)
async def end_add_time_slot(
    data: AddTimeSlotModel, user: UserSessionData = Annotated[UserSessionData, Depends(get_current_user)]
) -> None:
    return add_time_slot(
        TimeSlotModel(
            vendor_email=user.user_email,
            start_time=data.start_time,
            end_time=data.end_time,
            status=TimeSlotStatus.AVAILABLE,
        )
    )
