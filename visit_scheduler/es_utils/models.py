import pydantic
from enum import Enum
import datetime
ES_INDEX_VENDORS = "vendors"
ES_INDEX_TIME_SLOTS = "time_slots"
TIME_SLOT_DURATION = 15

class VendorModel(pydantic.BaseModel):
    name: str
    location: list[float]
    user_id: str
    rating: float = 0.0
    rating_amount: int = 0
    service_types: list[str]

class TimeSlotStatus(str, Enum):
    AVAILABLE = "available"
    BOOKED = "booked"
    PENDING = "pending"

class TimeSlotModel(pydantic.BaseModel):
    vendor_id: str
    start_time: datetime.datetime
    end_time: datetime.datetime
    status: TimeSlotStatus

class RatingModel(pydantic.BaseModel):
    vendor_id: str
    rating: float
    rating_amount: int


