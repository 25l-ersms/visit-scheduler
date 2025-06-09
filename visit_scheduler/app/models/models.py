import datetime

from pydantic import BaseModel


class SearchVendorModel(BaseModel):
    location_lat: float
    location_lon: float
    service_type: str
    start_time: datetime.datetime
    end_time: datetime.datetime


class AddTimeSlotModel(BaseModel):
    start_time: datetime.datetime
    end_time: datetime.datetime
    vendor_name: str


class UserSessionData(BaseModel):
    user_id: str
    user_email: str
    cookie_token: str

class TimeSlotModel(BaseModel):
    vendor_email: str
    start_time: datetime.datetime
    end_time: datetime.datetime
    status: str


class BookTimeSlotModel(BaseModel):
    time_slot_ids: list[str]

class VisitBookingModel(BaseModel):
    start_time: datetime.datetime
    end_time: datetime.datetime
    vendor_email: str