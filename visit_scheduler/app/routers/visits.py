import os

import requests
from elastic_transport import ObjectApiResponse
from fastapi import APIRouter, Depends, HTTPException

from visit_scheduler.app.models.models import (
    AddTimeSlotModel,
    BookTimeSlotModel,
    SearchVendorModel,
    UserSessionData,
    VisitBookingModel,
)
from visit_scheduler.app.security import get_current_user
from visit_scheduler.es_utils.handler import (
    add_time_slot,
    change_es_time_slot_status,
    get_all_time_slots,
    get_time_slot,
    search_vendors,
)
from visit_scheduler.es_utils.models import BaseTimeSlotModel, TimeSlotStatus

router = APIRouter(prefix="/visits", tags=["visits"], responses={404: {"description": "Not found"}})


@router.get("/all", response_model=None)
async def get_all_slots(
    _: UserSessionData = Depends(get_current_user),
) -> ObjectApiResponse:
    return get_all_time_slots()


@router.post("/search", response_model=None)
async def end_search_vendors(data: SearchVendorModel, _: UserSessionData = Depends(get_current_user)) -> None:
    return search_vendors(data)


@router.post("/add_time_slot", response_model=None)
async def end_add_time_slot(data: AddTimeSlotModel, user: UserSessionData = Depends(get_current_user)) -> None:
    return add_time_slot(
        BaseTimeSlotModel(
            vendor_email=user.user_email,
            start_time=data.start_time,
            end_time=data.end_time,
            status=TimeSlotStatus.AVAILABLE,
            vendor_name=data.vendor_name,
        )
    )


@router.post("/book_time_slot", response_model=None)
async def end_book_time_slot(data: BookTimeSlotModel, user: UserSessionData = Depends(get_current_user)) -> None:
    time_slot = get_time_slot(data.time_slot_ids)
    booking_data = VisitBookingModel(
        start_time=time_slot.start_time, end_time=time_slot.end_time, vendor_email=time_slot.vendor_email
    )
    # Convert datetime objects to ISO format strings
    booking_dict = booking_data.model_dump()
    booking_dict["start_time"] = booking_dict["start_time"].isoformat()
    booking_dict["end_time"] = booking_dict["end_time"].isoformat()

    reservation_result = requests.post(
        f"{os.getenv('VISIT_MANAGER_URL')}/user/book_visit",
        json=booking_dict,
        cookies={"access_token": user.cookie_token},
    )
    if reservation_result.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to book time slot")
    change_es_time_slot_status(data.time_slot_ids, TimeSlotStatus.BOOKED)
    return reservation_result.json()
