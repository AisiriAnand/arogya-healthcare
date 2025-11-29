from pydantic import BaseModel, Field
from datetime import datetime, date, time
from typing import List, Optional
from enum import Enum

class FrequencyType(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    AS_NEEDED = "as_needed"

class ReminderStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class ReminderCreate(BaseModel):
    medication_name: str = Field(..., min_length=1, max_length=100)
    dosage: str = Field(..., min_length=1, max_length=50)
    frequency: FrequencyType
    reminder_times: List[str]
    start_date: str
    end_date: Optional[str] = None
    ringtone: str = "default"
    notes: Optional[str] = None

class ReminderUpdate(BaseModel):
    medication_name: Optional[str] = Field(None, min_length=1, max_length=100)
    dosage: Optional[str] = Field(None, min_length=1, max_length=50)
    frequency: Optional[FrequencyType] = None
    reminder_times: Optional[List[str]] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    ringtone: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[ReminderStatus] = None

class MedicationReminder(BaseModel):
    id: str
    user_id: str
    medication_name: str
    dosage: str
    frequency: FrequencyType
    reminder_times: List[time]
    start_date: date
    end_date: Optional[date]
    ringtone: str
    notes: Optional[str]
    status: ReminderStatus
    created_at: datetime
    updated_at: datetime
    next_dose_time: Optional[datetime]
    total_doses: int
    taken_doses: int
    missed_doses: int

class ReminderResponse(BaseModel):
    id: str
    user_id: str
    medication_name: str
    dosage: str
    frequency: str
    reminder_times: List[str]
    start_date: str
    end_date: Optional[str]
    ringtone: str
    notes: Optional[str]
    status: str
    created_at: str
    updated_at: str
    next_dose_time: Optional[str]
    total_doses: int
    taken_doses: int
    missed_doses: int

class MedicationLogCreate(BaseModel):
    reminder_id: str
    taken_at: datetime
    status: str
    notes: Optional[str] = None

class MedicationLog(BaseModel):
    id: str
    reminder_id: str
    user_id: str
    taken_at: datetime
    status: str
    notes: Optional[str]
    created_at: datetime

class TodaySchedule(BaseModel):
    date: str
    reminders: List[ReminderResponse]

class ReminderStats(BaseModel):
    total_reminders: int
    active_reminders: int
    completed_today: int
    missed_today: int
    adherence_rate: float

class NotificationSettings(BaseModel):
    user_id: str
    enable_notifications: bool = True
    sound_enabled: bool = True
    vibration_enabled: bool = True
    reminder_advance_minutes: int = 5

class NotificationSettingsUpdate(BaseModel):
    enable_notifications: Optional[bool] = None
    sound_enabled: Optional[bool] = None
    vibration_enabled: Optional[bool] = None
    reminder_advance_minutes: Optional[int] = None
