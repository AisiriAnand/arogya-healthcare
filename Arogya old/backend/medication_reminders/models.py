from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, time, date
from enum import Enum

class FrequencyType(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    AS_NEEDED = "as_needed"
    CUSTOM = "custom"

class ReminderStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    PAUSED = "paused"
    DISCONTINUED = "discontinued"

class MedicationReminder(BaseModel):
    id: str
    user_id: str
    medication_name: str = Field(..., min_length=1, max_length=100)
    dosage: str = Field(..., min_length=1, max_length=50)
    frequency: FrequencyType
    reminder_times: List[time]  # List of times for daily reminders
    start_date: date
    end_date: Optional[date] = None
    ringtone: str = "default"
    notes: Optional[str] = Field(None, max_length=500)
    status: ReminderStatus = ReminderStatus.ACTIVE
    created_at: datetime
    updated_at: datetime
    next_dose_time: Optional[datetime] = None
    total_doses: int = 0
    taken_doses: int = 0
    missed_doses: int = 0

class ReminderCreate(BaseModel):
    medication_name: str = Field(..., min_length=1, max_length=100)
    dosage: str = Field(..., min_length=1, max_length=50)
    frequency: FrequencyType
    reminder_times: List[time]
    start_date: date
    end_date: Optional[date] = None
    ringtone: str = "default"
    notes: Optional[str] = Field(None, max_length=500)

class ReminderUpdate(BaseModel):
    medication_name: Optional[str] = Field(None, min_length=1, max_length=100)
    dosage: Optional[str] = Field(None, min_length=1, max_length=50)
    frequency: Optional[FrequencyType] = None
    reminder_times: Optional[List[time]] = None
    end_date: Optional[date] = None
    ringtone: Optional[str] = None
    notes: Optional[str] = Field(None, max_length=500)
    status: Optional[ReminderStatus] = None

class ReminderResponse(BaseModel):
    id: str
    medication_name: str
    dosage: str
    frequency: FrequencyType
    reminder_times: List[str]  # Formatted as strings for JSON
    start_date: str
    end_date: Optional[str]
    ringtone: str
    notes: Optional[str]
    status: ReminderStatus
    created_at: str
    updated_at: str
    next_dose_time: Optional[str]
    total_doses: int
    taken_doses: int
    missed_doses: int
    completion_rate: float  # Percentage

class MedicationLog(BaseModel):
    id: str
    reminder_id: str
    user_id: str
    scheduled_time: datetime
    taken_time: Optional[datetime]
    status: str  # "taken", "skipped", "missed"
    notes: Optional[str]
    created_at: datetime

class MedicationLogCreate(BaseModel):
    reminder_id: str
    scheduled_time: datetime
    taken_time: Optional[datetime]
    status: str  # "taken", "skipped", "missed"
    notes: Optional[str]

class TodaySchedule(BaseModel):
    date: str
    reminders: List[ReminderResponse]
    total_medications: int
    taken_today: int
    pending_today: int
    missed_today: int

class ReminderStats(BaseModel):
    total_reminders: int
    active_reminders: int
    completed_today: int
    pending_today: int
    missed_today: int
    weekly_adherence: float  # Percentage
    monthly_adherence: float  # Percentage

class NotificationSettings(BaseModel):
    user_id: str
    enable_notifications: bool = True
    sound_enabled: bool = True
    vibration_enabled: bool = True
    reminder_advance_minutes: int = 5  # Minutes before to remind
    quiet_hours_enabled: bool = False
    quiet_hours_start: Optional[time] = None
    quiet_hours_end: Optional[time] = None

class NotificationSettingsUpdate(BaseModel):
    enable_notifications: Optional[bool] = None
    sound_enabled: Optional[bool] = None
    vibration_enabled: Optional[bool] = None
    reminder_advance_minutes: Optional[int] = None
    quiet_hours_enabled: Optional[bool] = None
    quiet_hours_start: Optional[time] = None
    quiet_hours_end: Optional[time] = None
