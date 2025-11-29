import json
import uuid
from datetime import datetime, date, time, timedelta
from typing import List, Optional, Dict
from pathlib import Path
from .models import (
    MedicationReminder, ReminderCreate, ReminderUpdate, ReminderResponse,
    MedicationLog, MedicationLogCreate, TodaySchedule, ReminderStats,
    NotificationSettings, NotificationSettingsUpdate,
    FrequencyType, ReminderStatus
)

class MedicationReminderService:
    def __init__(self):
        self.data_file = Path("medication_reminders/reminders_data.json")
        self.logs_file = Path("medication_reminders/medication_logs.json")
        self.settings_file = Path("medication_reminders/notification_settings.json")
        self.reminders: Dict[str, MedicationReminder] = {}
        self.logs: Dict[str, MedicationLog] = {}
        self.settings: Dict[str, NotificationSettings] = {}
        self.load_data()
    
    def load_data(self):
        """Load medication reminders, logs, and settings from JSON files"""
        try:
            # Load reminders
            if self.data_file.exists():
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for reminder_id, reminder_data in data.items():
                        reminder = MedicationReminder(**reminder_data)
                        self.reminders[reminder_id] = reminder
                        # Update next dose time
                        self._update_next_dose_time(reminder_id)
            else:
                self.reminders = {}
            
            # Load logs
            if self.logs_file.exists():
                with open(self.logs_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for log_id, log_data in data.items():
                        log = MedicationLog(**log_data)
                        self.logs[log_id] = log
            else:
                self.logs = {}
            
            # Load settings
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for user_id, settings_data in data.items():
                        settings = NotificationSettings(**settings_data)
                        self.settings[user_id] = settings
            else:
                # Create default settings for demo user
                self.settings["demo_user_123"] = NotificationSettings(
                    user_id="demo_user_123",
                    enable_notifications=True,
                    sound_enabled=True,
                    vibration_enabled=True,
                    reminder_advance_minutes=5
                )
            
            print(f"Loaded {len(self.reminders)} reminders, {len(self.logs)} logs, {len(self.settings)} user settings")
            
        except Exception as e:
            print(f"Error loading medication data: {e}")
            self.reminders = {}
            self.logs = {}
            # Create default settings
            self.settings["demo_user_123"] = NotificationSettings(
                user_id="demo_user_123",
                enable_notifications=True,
                sound_enabled=True,
                vibration_enabled=True,
                reminder_advance_minutes=5
            )
    
    def save_data(self):
        """Save medication reminders, logs, and settings to JSON files"""
        try:
            # Save reminders
            self.data_file.parent.mkdir(parents=True, exist_ok=True)
            reminders_data = {}
            for reminder_id, reminder in self.reminders.items():
                reminders_data[reminder_id] = reminder.dict()
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(reminders_data, f, indent=2, default=str)
            
            # Save logs
            logs_data = {}
            for log_id, log in self.logs.items():
                logs_data[log_id] = log.dict()
            with open(self.logs_file, 'w', encoding='utf-8') as f:
                json.dump(logs_data, f, indent=2, default=str)
            
            # Save settings
            settings_data = {}
            for user_id, settings in self.settings.items():
                settings_data[user_id] = settings.dict()
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings_data, f, indent=2, default=str)
                
        except Exception as e:
            print(f"Error saving medication data: {e}")
    
    def create_reminder(self, reminder_data: ReminderCreate, user_id: str) -> MedicationReminder:
        """Create a new medication reminder"""
        reminder_id = str(uuid.uuid4())
        now = datetime.now()
        
        # Convert string times to time objects
        reminder_times_objects = []
        for time_str in reminder_data.reminder_times:
            try:
                hour, minute = map(int, time_str.split(':'))
                reminder_times_objects.append(time(hour, minute))
            except ValueError:
                # If parsing fails, use current time
                reminder_times_objects.append(now.time())
        
        reminder = MedicationReminder(
            id=reminder_id,
            user_id=user_id,
            medication_name=reminder_data.medication_name,
            dosage=reminder_data.dosage,
            frequency=reminder_data.frequency,
            reminder_times=reminder_times_objects,
            start_date=datetime.strptime(reminder_data.start_date, "%Y-%m-%d").date(),
            end_date=datetime.strptime(reminder_data.end_date, "%Y-%m-%d").date() if reminder_data.end_date else None,
            ringtone=reminder_data.ringtone,
            notes=reminder_data.notes,
            status=ReminderStatus.ACTIVE,
            created_at=now,
            updated_at=now,
            next_dose_time=None,  # Will be calculated below
            total_doses=0,
            taken_doses=0,
            missed_doses=0
        )
        
        # Store reminder first
        self.reminders[reminder_id] = reminder
        
        # Calculate next dose time
        self._update_next_dose_time(reminder_id)
        
        # Save data
        self.save_data()
        
        return reminder
    
    def get_user_reminders(self, user_id: str, status: Optional[ReminderStatus] = None) -> List[MedicationReminder]:
        """Get all reminders for a user, optionally filtered by status"""
        reminders = [r for r in self.reminders.values() if r.user_id == user_id]
        
        if status:
            reminders = [r for r in reminders if r.status == status]
        
        # Sort by next dose time
        reminders.sort(key=lambda r: r.next_dose_time or datetime.max)
        return reminders
    
    def get_reminder(self, reminder_id: str) -> Optional[MedicationReminder]:
        """Get a specific reminder by ID"""
        return self.reminders.get(reminder_id)
    
    def update_reminder(self, reminder_id: str, update_data: ReminderUpdate) -> Optional[MedicationReminder]:
        """Update an existing reminder"""
        reminder = self.reminders.get(reminder_id)
        if not reminder:
            return None
        
        # Update fields
        if update_data.medication_name is not None:
            reminder.medication_name = update_data.medication_name
        if update_data.dosage is not None:
            reminder.dosage = update_data.dosage
        if update_data.frequency is not None:
            reminder.frequency = update_data.frequency
        if update_data.reminder_times is not None:
            reminder.reminder_times = update_data.reminder_times
        if update_data.start_date is not None:
            reminder.start_date = update_data.start_date
        if update_data.end_date is not None:
            reminder.end_date = update_data.end_date
        if update_data.ringtone is not None:
            reminder.ringtone = update_data.ringtone
        if update_data.notes is not None:
            reminder.notes = update_data.notes
        if update_data.status is not None:
            reminder.status = update_data.status
        
        reminder.updated_at = datetime.now()
        
        # Update next dose time
        self._update_next_dose_time(reminder_id)
        
        self.save_data()
        return reminder
    
    def delete_reminder(self, reminder_id: str) -> bool:
        """Delete a reminder"""
        if reminder_id in self.reminders:
            del self.reminders[reminder_id]
            self.save_data()
            return True
        return False
    
    def log_medication(self, reminder_id: str, user_id: str, status: str, notes: Optional[str] = None) -> MedicationLog:
        """Log medication intake"""
        log_id = str(uuid.uuid4())
        now = datetime.now()
        
        log = MedicationLog(
            id=log_id,
            reminder_id=reminder_id,
            user_id=user_id,
            taken_at=now,
            status=status,
            notes=notes,
            created_at=now
        )
        
        # Update reminder stats
        reminder = self.reminders.get(reminder_id)
        if reminder:
            reminder.total_doses += 1
            if status == "taken":
                reminder.taken_doses += 1
            elif status == "skipped":
                reminder.missed_doses += 1
            elif status == "missed":
                reminder.missed_doses += 1
            
            # Update next dose time
            self._update_next_dose_time(reminder_id)
        
        self.logs[log_id] = log
        self.save_data()
        return log
    
    def get_today_schedule(self, user_id: str) -> TodaySchedule:
        """Get today's medication schedule for a user"""
        today = date.today().isoformat()
        user_reminders = self.get_user_reminders(user_id, ReminderStatus.ACTIVE)
        
        # Filter reminders for today
        today_reminders = []
        for reminder in user_reminders:
            # Check if reminder is active for today
            if self._is_reminder_active_today(reminder):
                today_reminders.append(self._convert_to_response(reminder))
        
        return TodaySchedule(
            date=today,
            reminders=today_reminders
        )
    
    def get_user_stats(self, user_id: str) -> ReminderStats:
        """Get medication statistics for a user"""
        user_reminders = self.get_user_reminders(user_id)
        active_reminders = self.get_user_reminders(user_id, ReminderStatus.ACTIVE)
        
        # Get today's logs
        today = date.today()
        today_logs = [
            log for log in self.logs.values() 
            if log.user_id == user_id and log.taken_at.date() == today
        ]
        
        completed_today = len([log for log in today_logs if log.status == "taken"])
        missed_today = len([log for log in today_logs if log.status in ["skipped", "missed"]])
        
        # Calculate adherence rate
        total_doses = sum(reminder.total_doses for reminder in user_reminders)
        taken_doses = sum(reminder.taken_doses for reminder in user_reminders)
        adherence_rate = (taken_doses / total_doses * 100) if total_doses > 0 else 0.0
        
        return ReminderStats(
            total_reminders=len(user_reminders),
            active_reminders=len(active_reminders),
            completed_today=completed_today,
            missed_today=missed_today,
            adherence_rate=adherence_rate
        )
    
    def get_notification_settings(self, user_id: str) -> NotificationSettings:
        """Get notification settings for a user"""
        return self.settings.get(user_id, NotificationSettings(
            user_id=user_id,
            enable_notifications=True,
            sound_enabled=True,
            vibration_enabled=True,
            reminder_advance_minutes=5
        ))
    
    def update_notification_settings(self, user_id: str, settings_update: NotificationSettingsUpdate) -> NotificationSettings:
        """Update notification settings for a user"""
        current_settings = self.get_notification_settings(user_id)
        
        if settings_update.enable_notifications is not None:
            current_settings.enable_notifications = settings_update.enable_notifications
        if settings_update.sound_enabled is not None:
            current_settings.sound_enabled = settings_update.sound_enabled
        if settings_update.vibration_enabled is not None:
            current_settings.vibration_enabled = settings_update.vibration_enabled
        if settings_update.reminder_advance_minutes is not None:
            current_settings.reminder_advance_minutes = settings_update.reminder_advance_minutes
        
        self.settings[user_id] = current_settings
        self.save_data()
        return current_settings
    
    def _convert_to_response(self, reminder: MedicationReminder) -> ReminderResponse:
        """Convert MedicationReminder to ReminderResponse"""
        return ReminderResponse(
            id=reminder.id,
            user_id=reminder.user_id,
            medication_name=reminder.medication_name,
            dosage=reminder.dosage,
            frequency=reminder.frequency.value,
            reminder_times=[t.strftime("%H:%M:%S") for t in reminder.reminder_times],
            start_date=reminder.start_date.isoformat(),
            end_date=reminder.end_date.isoformat() if reminder.end_date else None,
            ringtone=reminder.ringtone,
            notes=reminder.notes,
            status=reminder.status.value,
            created_at=reminder.created_at.isoformat(),
            updated_at=reminder.updated_at.isoformat(),
            next_dose_time=reminder.next_dose_time.isoformat() if reminder.next_dose_time else None,
            total_doses=reminder.total_doses,
            taken_doses=reminder.taken_doses,
            missed_doses=reminder.missed_doses
        )
    
    def _update_next_dose_time(self, reminder_id: str):
        """Update the next dose time for a reminder"""
        reminder = self.reminders.get(reminder_id)
        if not reminder or reminder.status != ReminderStatus.ACTIVE:
            return
        
        now = datetime.now()
        next_dose = None
        
        for reminder_time in reminder.reminder_times:
            # Create datetime for today's reminder time
            today_reminder = now.replace(
                hour=reminder_time.hour,
                minute=reminder_time.minute,
                second=0,
                microsecond=0
            )
            
            # If today's time has passed, check tomorrow
            if today_reminder <= now:
                if reminder.frequency == FrequencyType.DAILY:
                    today_reminder += timedelta(days=1)
                elif reminder.frequency == FrequencyType.WEEKLY:
                    today_reminder += timedelta(weeks=1)
                elif reminder.frequency == FrequencyType.MONTHLY:
                    today_reminder += timedelta(days=30)
                # AS_NEEDED doesn't have a next dose
            
            # Find the earliest next dose
            if next_dose is None or today_reminder < next_dose:
                next_dose = today_reminder
        
        reminder.next_dose_time = next_dose
    
    def _is_reminder_active_today(self, reminder: MedicationReminder) -> bool:
        """Check if a reminder is active for today"""
        if reminder.status != ReminderStatus.ACTIVE:
            return False
        
        today = date.today()
        start_date = datetime.strptime(reminder.start_date, "%Y-%m-%d").date()
        
        if start_date > today:
            return False
        
        if reminder.end_date:
            end_date = datetime.strptime(reminder.end_date, "%Y-%m-%d").date()
            if end_date < today:
                return False
        
        return True

# Service instance
medication_service = MedicationReminderService()
