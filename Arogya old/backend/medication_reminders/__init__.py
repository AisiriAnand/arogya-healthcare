"""
Medication Reminders Module

This module provides comprehensive medication reminder functionality including:
- Creating and managing medication reminders
- Tracking medication adherence
- Notification settings and preferences
- Statistics and reporting
- Today's schedule and upcoming reminders
"""

from .models import (
    MedicationReminder, ReminderCreate, ReminderUpdate, ReminderResponse,
    MedicationLog, MedicationLogCreate, TodaySchedule, ReminderStats,
    NotificationSettings, NotificationSettingsUpdate,
    FrequencyType, ReminderStatus
)

from .services import medication_service, MedicationReminderService

__all__ = [
    # Models
    'MedicationReminder', 'ReminderCreate', 'ReminderUpdate', 'ReminderResponse',
    'MedicationLog', 'MedicationLogCreate', 'TodaySchedule', 'ReminderStats',
    'NotificationSettings', 'NotificationSettingsUpdate',
    'FrequencyType', 'ReminderStatus',
    
    # Services
    'medication_service', 'MedicationReminderService'
]
