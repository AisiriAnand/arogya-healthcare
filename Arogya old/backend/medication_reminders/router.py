from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from datetime import date, datetime

from .services import medication_service
from .models import (
    MedicationReminder, ReminderCreate, ReminderUpdate, ReminderResponse,
    MedicationLog, MedicationLogCreate, TodaySchedule, ReminderStats,
    NotificationSettings, NotificationSettingsUpdate,
    ReminderStatus, FrequencyType
)
from auth.router import get_current_user

router = APIRouter(prefix="/medication", tags=["medication"])

# Dependency to get user_id from authentication
def get_current_user_id(current_user: dict = Depends(get_current_user)):
    """Extract user_id from authenticated user"""
    return current_user["id"]

@router.post("/reminders", response_model=ReminderResponse)
async def create_reminder(
    reminder_data: ReminderCreate,
    user_id: str = Depends(get_current_user_id)
):
    """Create a new medication reminder"""
    try:
        reminder = medication_service.create_reminder(reminder_data, user_id)
        return medication_service._convert_to_response(reminder)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reminders", response_model=List[ReminderResponse])
async def get_reminders(
    status: Optional[ReminderStatus] = Query(None, description="Filter by reminder status"),
    user_id: str = Depends(get_current_user_id)
):
    """Get all medication reminders for the current user"""
    try:
        reminders = medication_service.get_user_reminders(user_id, status)
        return [medication_service._convert_to_response(r) for r in reminders]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reminders/{reminder_id}", response_model=ReminderResponse)
async def get_reminder(
    reminder_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Get a specific medication reminder"""
    try:
        reminder = medication_service.get_reminder(reminder_id)
        if not reminder:
            raise HTTPException(status_code=404, detail="Reminder not found")
        
        if reminder.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        return medication_service._convert_to_response(reminder)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/reminders/{reminder_id}", response_model=ReminderResponse)
async def update_reminder(
    reminder_id: str,
    update_data: ReminderUpdate,
    user_id: str = Depends(get_current_user_id)
):
    """Update an existing medication reminder"""
    try:
        reminder = medication_service.get_reminder(reminder_id)
        if not reminder:
            raise HTTPException(status_code=404, detail="Reminder not found")
        
        if reminder.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        updated_reminder = medication_service.update_reminder(reminder_id, update_data)
        if not updated_reminder:
            raise HTTPException(status_code=404, detail="Reminder not found")
        
        return medication_service._convert_to_response(updated_reminder)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/reminders/{reminder_id}")
async def delete_reminder(
    reminder_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Delete a medication reminder"""
    try:
        reminder = medication_service.get_reminder(reminder_id)
        if not reminder:
            raise HTTPException(status_code=404, detail="Reminder not found")
        
        if reminder.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        success = medication_service.delete_reminder(reminder_id)
        if not success:
            raise HTTPException(status_code=404, detail="Reminder not found")
        
        return {"message": "Reminder deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reminders/{reminder_id}/log", response_model=dict)
async def log_medication(
    reminder_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Log medication as taken"""
    try:
        reminder = medication_service.get_reminder(reminder_id)
        if not reminder:
            raise HTTPException(status_code=404, detail="Reminder not found")
        
        if reminder.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        log = medication_service.log_medication(reminder_id, user_id, "taken")
        return {"message": "Medication logged as taken", "log_id": log.id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/schedule/today", response_model=TodaySchedule)
async def get_today_schedule(
    user_id: str = Depends(get_current_user_id)
):
    """Get today's medication schedule"""
    try:
        schedule = medication_service.get_today_schedule(user_id)
        return schedule
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats", response_model=ReminderStats)
async def get_reminder_stats(
    user_id: str = Depends(get_current_user_id)
):
    """Get medication statistics for the current user"""
    try:
        stats = medication_service.get_user_stats(user_id)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/logs", response_model=List[dict])
async def get_medication_logs(
    user_id: str = Depends(get_current_user_id)
):
    """Get medication logs for the current user"""
    try:
        logs = [log for log in medication_service.logs.values() if log.user_id == user_id]
        logs.sort(key=lambda log: log.taken_at, reverse=True)
        
        return [
            {
                "id": log.id,
                "reminder_id": log.reminder_id,
                "taken_at": log.taken_at.isoformat(),
                "status": log.status,
                "notes": log.notes,
                "created_at": log.created_at.isoformat()
            }
            for log in logs
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/notifications/settings", response_model=NotificationSettings)
async def get_notification_settings(
    user_id: str = Depends(get_current_user_id)
):
    """Get notification settings for the current user"""
    try:
        settings = medication_service.get_notification_settings(user_id)
        return settings
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/notifications/settings", response_model=NotificationSettings)
async def update_notification_settings(
    settings_update: NotificationSettingsUpdate,
    user_id: str = Depends(get_current_user_id)
):
    """Update notification settings for the current user"""
    try:
        settings = medication_service.update_notification_settings(user_id, settings_update)
        return settings
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/notifications/test")
async def test_notification(
    user_id: str = Depends(get_current_user_id)
):
    """Send a test notification (for development/testing)"""
    try:
        # In a real implementation, this would trigger a push notification
        # For now, we'll just return a success response
        settings = medication_service.get_notification_settings(user_id)
        
        return {
            "message": "Test notification functionality",
            "settings": {
                "notifications_enabled": settings.enable_notifications,
                "sound_enabled": settings.sound_enabled,
                "vibration_enabled": settings.vibration_enabled
            },
            "note": "In production, this would send an actual notification to the user's device"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
