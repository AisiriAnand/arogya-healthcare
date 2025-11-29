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
                self.settings = {}
            
            print(f"Loaded {len(self.reminders)} reminders, {len(self.logs)} logs, {len(self.settings)} user settings")
            
        except Exception as e:
            print(f"Error loading medication data: {e}")
            self.reminders = {}
            self.logs = {}
            self.settings = {}
    
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
        
        reminder = MedicationReminder(
            id=reminder_id,
            user_id=user_id,
            medication_name=reminder_data.medication_name,
            dosage=reminder_data.dosage,
            frequency=reminder_data.frequency,
            reminder_times=reminder_data.reminder_times,
            start_date=reminder_data.start_date,
            end_date=reminder_data.end_date,
            ringtone=reminder_data.ringtone,
            notes=reminder_data.notes,
            status=ReminderStatus.ACTIVE,
            created_at=now,
            updated_at=now,
            total_doses=0,
            taken_doses=0,
            missed_doses=0
        )
        
        # Calculate next dose time
        self._update_next_dose_time(reminder_id)
        
        self.reminders[reminder_id] = reminder
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
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            if hasattr(reminder, field):
                setattr(reminder, field, value)
        
        reminder.updated_at = datetime.now()
        
        # Recalculate next dose time if relevant fields changed
        if any(field in update_dict for field in ['frequency', 'reminder_times', 'start_date', 'end_date', 'status']):
            self._update_next_dose_time(reminder_id)
        
        self.save_data()
        return reminder
    
    def delete_reminder(self, reminder_id: str) -> bool:
        """Delete a reminder"""
        if reminder_id in self.reminders:
            del self.reminders[reminder_id]
            
            # Also delete associated logs
            log_ids_to_delete = [log_id for log_id, log in self.logs.items() if log.reminder_id == reminder_id]
            for log_id in log_ids_to_delete:
                del self.logs[log_id]
            
            self.save_data()
            return True
        return False
    
    def get_today_schedule(self, user_id: str) -> TodaySchedule:
        """Get today's medication schedule for a user"""
        today = date.today()
        today_str = today.isoformat()
        
        # Get active reminders for today
        today_reminders = []
        for reminder in self.reminders.values():
            if (reminder.user_id == user_id and 
                reminder.status == ReminderStatus.ACTIVE and
                reminder.start_date <= today and
                (reminder.end_date is None or reminder.end_date >= today)):
                
                # Check if reminder has doses scheduled for today
                if self._has_dose_today(reminder, today):
                    response = self._convert_to_response(reminder)
                    today_reminders.append(response)
        
        # Sort by reminder time
        today_reminders.sort(key=lambda r: r.next_dose_time or "23:59")
        
        # Calculate today's statistics
        taken_today = 0
        pending_today = 0
        missed_today = 0
        
        for reminder in today_reminders:
            # Get today's logs for this reminder
            reminder_logs = [log for log in self.logs.values() 
                           if log.reminder_id == reminder.id and 
                           log.scheduled_time.date() == today]
            
            taken_today += len([log for log in reminder_logs if log.status == "taken"])
            missed_today += len([log for log in reminder_logs if log.status == "missed"])
            
            # Calculate pending based on scheduled times
            now = datetime.now()
            for reminder_time_str in reminder.reminder_times:
                reminder_time = datetime.strptime(reminder_time_str, "%H:%M:%S").time()
                reminder_datetime = datetime.combine(today, reminder_time)
                
                if reminder_datetime > now:
                    pending_today += 1
        
        return TodaySchedule(
            date=today_str,
            reminders=today_reminders,
            total_medications=len(today_reminders),
            taken_today=taken_today,
            pending_today=pending_today,
            missed_today=missed_today
        )
    
    def log_medication_taken(self, reminder_id: str, user_id: str, status: str, notes: Optional[str] = None) -> Optional[MedicationLog]:
        """Log when medication is taken, skipped, or missed"""
        reminder = self.reminders.get(reminder_id)
        if not reminder or reminder.user_id != user_id:
            return None
        
        # Create log entry
        log_id = str(uuid.uuid4())
        now = datetime.now()
        
        log = MedicationLog(
            id=log_id,
            reminder_id=reminder_id,
            user_id=user_id,
            scheduled_time=reminder.next_dose_time or now,
            taken_time=now if status == "taken" else None,
            status=status,
            notes=notes,
            created_at=now
        )
        
        self.logs[log_id] = log
        
        # Update reminder statistics
        reminder.total_doses += 1
        if status == "taken":
            reminder.taken_doses += 1
        elif status == "missed":
            reminder.missed_doses += 1
        
        # Calculate next dose time
        self._update_next_dose_time(reminder_id)
        
        self.save_data()
        return log
    
    def get_reminder_stats(self, user_id: str) -> ReminderStats:
        """Get medication adherence statistics for a user"""
        user_reminders = [r for r in self.reminders.values() if r.user_id == user_id]
        active_reminders = [r for r in user_reminders if r.status == ReminderStatus.ACTIVE]
        
        # Today's stats
        today = date.today()
        completed_today = 0
        pending_today = 0
        missed_today = 0
        
        for reminder in active_reminders:
            reminder_logs = [log for log in self.logs.values() 
                           if log.reminder_id == reminder.id and 
                           log.scheduled_time.date() == today]
            
            completed_today += len([log for log in reminder_logs if log.status == "taken"])
            missed_today += len([log for log in reminder_logs if log.status == "missed"])
        
        # Calculate pending
        for reminder in active_reminders:
            if self._has_dose_today(reminder, today):
                pending_today += len(reminder.reminder_times)
        
        pending_today = pending_today - completed_today
        
        # Weekly adherence (last 7 days)
        weekly_adherence = self._calculate_adherence(user_id, days=7)
        
        # Monthly adherence (last 30 days)
        monthly_adherence = self._calculate_adherence(user_id, days=30)
        
        return ReminderStats(
            total_reminders=len(user_reminders),
            active_reminders=len(active_reminders),
            completed_today=completed_today,
            pending_today=max(0, pending_today),
            missed_today=missed_today,
            weekly_adherence=weekly_adherence,
            monthly_adherence=monthly_adherence
        )
    
    def get_notification_settings(self, user_id: str) -> NotificationSettings:
        """Get notification settings for a user"""
        if user_id not in self.settings:
            # Create default settings
            self.settings[user_id] = NotificationSettings(user_id=user_id)
            self.save_data()
        
        return self.settings[user_id]
    
    def update_notification_settings(self, user_id: str, settings_update: NotificationSettingsUpdate) -> NotificationSettings:
        """Update notification settings for a user"""
        if user_id not in self.settings:
            self.settings[user_id] = NotificationSettings(user_id=user_id)
        
        current_settings = self.settings[user_id]
        update_dict = settings_update.dict(exclude_unset=True)
        
        for field, value in update_dict.items():
            if hasattr(current_settings, field):
                setattr(current_settings, field, value)
        
        self.save_data()
        return current_settings
    
    def get_upcoming_reminders(self, user_id: str, hours_ahead: int = 24) -> List[MedicationReminder]:
        """Get reminders scheduled in the next N hours"""
        now = datetime.now()
        end_time = now + timedelta(hours=hours_ahead)
        
        upcoming = []
        for reminder in self.reminders.values():
            if (reminder.user_id == user_id and 
                reminder.status == ReminderStatus.ACTIVE and
                reminder.next_dose_time and
                now <= reminder.next_dose_time <= end_time):
                upcoming.append(reminder)
        
        upcoming.sort(key=lambda r: r.next_dose_time)
        return upcoming
    
    # Helper methods
    def _update_next_dose_time(self, reminder_id: str):
        """Calculate the next dose time for a reminder"""
        reminder = self.reminders.get(reminder_id)
        if not reminder or reminder.status != ReminderStatus.ACTIVE:
            return
        
        now = datetime.now()
        today = date.today()
        
        if reminder.frequency == FrequencyType.DAILY:
            # Find next scheduled time today or tomorrow
            for reminder_time in reminder.reminder_times:
                reminder_datetime = datetime.combine(today, reminder_time)
                if reminder_datetime > now:
                    reminder.next_dose_time = reminder_datetime
                    return
            
            # If no time left today, use first time tomorrow
            if reminder.reminder_times:
                tomorrow = today + timedelta(days=1)
                reminder.next_dose_time = datetime.combine(tomorrow, reminder.reminder_times[0])
        
        elif reminder.frequency == FrequencyType.WEEKLY:
            # For weekly, use next occurrence (simplified - same day next week)
            if reminder.reminder_times:
                next_week = today + timedelta(days=7)
                reminder.next_dose_time = datetime.combine(next_week, reminder.reminder_times[0])
        
        elif reminder.frequency == FrequencyType.AS_NEEDED:
            # As needed - no next dose time
            reminder.next_dose_time = None
        
        else:
            # Default to first reminder time
            if reminder.reminder_times:
                reminder.next_dose_time = datetime.combine(today, reminder.reminder_times[0])
    
    def _has_dose_today(self, reminder: MedicationReminder, target_date: date) -> bool:
        """Check if a reminder has doses scheduled for the target date"""
        if reminder.start_date > target_date:
            return False
        if reminder.end_date and reminder.end_date < target_date:
            return False
        
        if reminder.frequency == FrequencyType.DAILY:
            return True
        elif reminder.frequency == FrequencyType.WEEKLY:
            # Simplified - assume weekly means same day each week
            return True
        elif reminder.frequency == FrequencyType.MONTHLY:
            # Simplified - assume monthly means same day each month
            return True
        elif reminder.frequency == FrequencyType.AS_NEEDED:
            return False
        
        return True
    
    def _calculate_adherence(self, user_id: str, days: int) -> float:
        """Calculate medication adherence percentage over N days"""
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        user_reminders = [r for r in self.reminders.values() if r.user_id == user_id]
        active_reminders = [r for r in user_reminders if r.status == ReminderStatus.ACTIVE]
        
        total_scheduled = 0
        total_taken = 0
        
        for reminder in active_reminders:
            # Get logs for the period
            period_logs = [log for log in self.logs.values() 
                          if log.reminder_id == reminder.id and
                          start_date <= log.scheduled_time.date() <= end_date]
            
            total_scheduled += len(period_logs)
            total_taken += len([log for log in period_logs if log.status == "taken"])
        
        if total_scheduled == 0:
            return 0.0
        
        return (total_taken / total_scheduled) * 100
    
    def _convert_to_response(self, reminder: MedicationReminder) -> ReminderResponse:
        """Convert MedicationReminder to ReminderResponse"""
        completion_rate = 0.0
        if reminder.total_doses > 0:
            completion_rate = (reminder.taken_doses / reminder.total_doses) * 100
        
        return ReminderResponse(
            id=reminder.id,
            medication_name=reminder.medication_name,
            dosage=reminder.dosage,
            frequency=reminder.frequency,
            reminder_times=[t.strftime("%H:%M:%S") for t in reminder.reminder_times],
            start_date=reminder.start_date.isoformat(),
            end_date=reminder.end_date.isoformat() if reminder.end_date else None,
            ringtone=reminder.ringtone,
            notes=reminder.notes,
            status=reminder.status,
            created_at=reminder.created_at.isoformat(),
            updated_at=reminder.updated_at.isoformat(),
            next_dose_time=reminder.next_dose_time.isoformat() if reminder.next_dose_time else None,
            total_doses=reminder.total_doses,
            taken_doses=reminder.taken_doses,
            missed_doses=reminder.missed_doses,
            completion_rate=completion_rate
        )

# Service instance
medication_service = MedicationReminderService()
