from pydantic import BaseModel
import datetime

class SearchVendorModel(BaseModel):
    location: list[float]
    service_type: str
    start_time: datetime.datetime
    end_time: datetime.datetime

class AddTimeSlotModel(BaseModel):
    start_time: datetime.datetime
    end_time: datetime.datetime
