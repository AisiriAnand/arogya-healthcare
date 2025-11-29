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

router = APIRouter(prefix="/medication", tags=["medication"])

# Dependency to get user_id (in real app, this would come from authentication)
def get_current_user_id():
    # For demo purposes, return a fixed user ID
    # In production, this would extract from JWT token or session
    return "demo_user_123"

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
        if not reminder or reminder.user_id != user_id:
            raise HTTPException(status_code=404, detail="Reminder not found")
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
    """Update a medication reminder"""
    try:
        reminder = medication_service.get_reminder(reminder_id)
        if not reminder or reminder.user_id != user_id:
            raise HTTPException(status_code=404, detail="Reminder not found")
        
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
        if not reminder or reminder.user_id != user_id:
            raise HTTPException(status_code=404, detail="Reminder not found")
        
        success = medication_service.delete_reminder(reminder_id)
        if not success:
            raise HTTPException(status_code=404, detail="Reminder not found")
        
        return {"message": "Reminder deleted successfully"}
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

@router.post("/reminders/{reminder_id}/log")
async def log_medication(
    reminder_id: str,
    status: str,  # "taken", "skipped", "missed"
    notes: Optional[str] = None,
    user_id: str = Depends(get_current_user_id)
):
    """Log medication taken, skipped, or missed"""
    try:
        if status not in ["taken", "skipped", "missed"]:
            raise HTTPException(status_code=400, detail="Invalid status. Must be 'taken', 'skipped', or 'missed'")
        
        log = medication_service.log_medication_taken(reminder_id, user_id, status, notes)
        if not log:
            raise HTTPException(status_code=404, detail="Reminder not found")
        
        return {"message": f"Medication {status} successfully", "log_id": log.id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats", response_model=ReminderStats)
async def get_medication_stats(
    user_id: str = Depends(get_current_user_id)
):
    """Get medication adherence statistics"""
    try:
        stats = medication_service.get_reminder_stats(user_id)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/upcoming", response_model=List[ReminderResponse])
async def get_upcoming_reminders(
    hours_ahead: int = Query(default=24, description="Hours ahead to look for reminders"),
    user_id: str = Depends(get_current_user_id)
):
    """Get upcoming medication reminders"""
    try:
        if hours_ahead < 1 or hours_ahead > 168:  # Max 1 week
            raise HTTPException(status_code=400, detail="hours_ahead must be between 1 and 168")
        
        reminders = medication_service.get_upcoming_reminders(user_id, hours_ahead)
        return [medication_service._convert_to_response(r) for r in reminders]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/notifications/settings", response_model=NotificationSettings)
async def get_notification_settings(
    user_id: str = Depends(get_current_user_id)
):
    """Get notification settings for the user"""
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
    """Update notification settings for the user"""
    try:
        settings = medication_service.update_notification_settings(user_id, settings_update)
        return settings
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/logs", response_model=List[MedicationLog])
async def get_medication_logs(
    start_date: Optional[date] = Query(None, description="Start date filter"),
    end_date: Optional[date] = Query(None, description="End date filter"),
    reminder_id: Optional[str] = Query(None, description="Filter by specific reminder"),
    user_id: str = Depends(get_current_user_id)
):
    """Get medication logs for the user"""
    try:
        logs = [log for log in medication_service.logs.values() if log.user_id == user_id]
        
        # Apply filters
        if reminder_id:
            logs = [log for log in logs if log.reminder_id == reminder_id]
        
        if start_date:
            logs = [log for log in logs if log.scheduled_time.date() >= start_date]
        
        if end_date:
            logs = [log for log in logs if log.scheduled_time.date() <= end_date]
        
        # Sort by scheduled time (newest first)
        logs.sort(key=lambda log: log.scheduled_time, reverse=True)
        
        return logs[:100]  # Limit to last 100 logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test-notification")
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
