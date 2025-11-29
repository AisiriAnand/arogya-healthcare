// Global Notification System - Works on all pages
class GlobalNotificationSystem {
    constructor() {
        this.isInitialized = false;
        this.checkInterval = null;
        this.minuteInterval = null;
    }

    // Initialize the notification system
    init() {
        if (this.isInitialized) return;
        
        const token = localStorage.getItem('access_token');
        if (!token) {
            console.log('User not authenticated, skipping notifications');
            return;
        }

        console.log('🔔 Initializing global notification system...');
        
        // Load reminders and start checking
        this.loadReminders();
        this.startNotificationChecking();
        
        // Check immediately
        this.checkExactTimeReminders();
        
        this.isInitialized = true;
    }

    // Load reminders from API
    async loadReminders() {
        try {
            const token = localStorage.getItem('access_token');
            const response = await fetch('http://localhost:5000/medication/reminders', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (response.ok) {
                const reminders = await response.json();
                localStorage.setItem('reminders', JSON.stringify(reminders));
                console.log(`📋 Loaded ${reminders.length} reminders for notifications`);
                return reminders;
            }
        } catch (error) {
            console.error('❌ Error loading reminders for notifications:', error);
        }
        return [];
    }

    // Start notification checking intervals
    startNotificationChecking() {
        // Check every 30 seconds
        this.checkInterval = setInterval(() => {
            this.checkExactTimeReminders();
            this.checkSnoozedReminders();
        }, 30000);
        
        // Check every minute for precision
        this.minuteInterval = setInterval(() => {
            this.checkExactTimeReminders();
        }, 60000);
        
        console.log('⏰ Started notification checking intervals');
    }

    // Check for exact time reminders
    checkExactTimeReminders() {
        const now = new Date();
        const currentTime = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`;
        
        console.log(`🕐 Checking exact time reminders at ${currentTime}`);
        
        // Get reminders from localStorage
        const reminders = JSON.parse(localStorage.getItem('reminders') || '[]');
        
        reminders.forEach(reminder => {
            if (reminder.status === 'active') {
                reminder.reminder_times.forEach(time => {
                    const reminderTime = time.split(':').slice(0, 2).join(':'); // Get HH:MM format
                    
                    // Check if current time matches reminder time
                    if (reminderTime === currentTime) {
                        console.log(`⚠️ Exact time match: ${reminder.medication_name} at ${currentTime}`);
                        
                        // Check if we already notified for this time today
                        const notificationKey = `notified_${reminder.id}_${new Date().toDateString()}_${reminderTime}`;
                        const alreadyNotified = localStorage.getItem(notificationKey);
                        
                        if (!alreadyNotified) {
                            console.log(`🔔 Showing exact time notification for ${reminder.medication_name}`);
                            this.showMedicationNotification(reminder);
                            
                            // Mark as notified for this time
                            localStorage.setItem(notificationKey, 'true');
                            
                            // Clear old notification marks
                            this.clearOldNotificationMarks();
                        }
                    }
                });
            }
        });
    }

    // Check for snoozed reminders
    checkSnoozedReminders() {
        const now = new Date();
        
        // Check all snoozed reminders
        for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            if (key && key.startsWith('snooze_')) {
                try {
                    const snoozeData = JSON.parse(localStorage.getItem(key));
                    const nextNotificationTime = new Date(snoozeData.nextNotificationTime);
                    
                    // If it's time to show the notification again
                    if (now >= nextNotificationTime) {
                        console.log(`⏰ Reshowing snoozed reminder: ${snoozeData.medicationName}`);
                        
                        // Create reminder object for notification
                        const reminder = {
                            id: snoozeData.reminderId,
                            medication_name: snoozeData.medicationName,
                            dosage: 'Snoozed Reminder',
                            reminder_times: ['Now'],
                            notes: 'This was snoozed and is now being shown again'
                        };
                        
                        // Show notification
                        this.showMedicationNotification(reminder);
                        
                        // Remove snooze data
                        localStorage.removeItem(key);
                    }
                } catch (error) {
                    console.error('❌ Error checking snoozed reminder:', error);
                    localStorage.removeItem(key);
                }
            }
        }
    }

    // Show medication notification popup
    showMedicationNotification(reminder) {
        console.log(`🔔 Showing notification for: ${reminder.medication_name}`);
        
        // Remove any existing notifications
        const existingNotifications = document.querySelectorAll('.notification-modal');
        existingNotifications.forEach(n => n.remove());
        
        const notificationModal = document.createElement('div');
        notificationModal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 notification-modal';
        notificationModal.innerHTML = `
            <div class="bg-white rounded-lg p-6 max-w-md mx-4 shadow-2xl transform transition-all">
                <div class="flex items-center mb-4">
                    <div class="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mr-4 animate-pulse">
                        <svg class="w-6 h-6 text-red-600" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clip-rule="evenodd"/>
                        </svg>
                    </div>
                    <div>
                        <h3 class="text-lg font-bold text-gray-900">Medication Reminder</h3>
                        <p class="text-sm text-gray-600">It's time to take your medication</p>
                    </div>
                </div>
                
                <div class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
                    <h4 class="font-semibold text-blue-900">${reminder.medication_name}</h4>
                    <p class="text-blue-700">${reminder.dosage}</p>
                    ${reminder.notes ? `<p class="text-sm text-blue-600 mt-1">${reminder.notes}</p>` : ''}
                </div>
                
                <div class="flex space-x-2">
                    <button onclick="globalNotifications.confirmTakenFromNotification('${reminder.id}'); this.closest('.notification-modal').remove();" class="flex-1 bg-green-600 text-white py-2 rounded-lg hover:bg-green-700 transition">
                        ✓ Taken
                    </button>
                    <button onclick="globalNotifications.skipDoseFromNotification('${reminder.id}'); this.closest('.notification-modal').remove();" class="flex-1 bg-orange-600 text-white py-2 rounded-lg hover:bg-orange-700 transition">
                        Skip
                    </button>
                    <button onclick="globalNotifications.snoozeReminder('${reminder.id}', '${reminder.medication_name}'); this.closest('.notification-modal').remove();" class="flex-1 bg-gray-600 text-white py-2 rounded-lg hover:bg-gray-700 transition">
                        Later (5 min)
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(notificationModal);
        
        // Auto-remove after 2 minutes if no action
        setTimeout(() => {
            if (document.body.contains(notificationModal)) {
                notificationModal.remove();
            }
        }, 120000);
        
        // Play notification sound
        this.playNotificationSound();
    }

    // Snooze reminder - show again after 5 minutes
    snoozeReminder(reminderId, medicationName) {
        console.log(`⏰ Snoozing reminder ${reminderId} for ${medicationName} for 5 minutes`);
        
        // Store snooze info
        const snoozeKey = `snooze_${reminderId}`;
        const snoozeData = {
            reminderId: reminderId,
            medicationName: medicationName,
            snoozeTime: new Date().toISOString(),
            nextNotificationTime: new Date(Date.now() + 5 * 60 * 1000).toISOString() // 5 minutes from now
        };
        localStorage.setItem(snoozeKey, JSON.stringify(snoozeData));
        
        // Show confirmation
        this.showSnoozeConfirmation(medicationName);
    }

    // Show snooze confirmation
    showSnoozeConfirmation(medicationName) {
        // Remove existing confirmations
        const existingConfirmations = document.querySelectorAll('.snooze-confirmation');
        existingConfirmations.forEach(c => c.remove());
        
        const confirmation = document.createElement('div');
        confirmation.className = 'fixed top-4 right-4 bg-blue-50 border border-blue-200 rounded-lg p-4 shadow-lg z-50 snooze-confirmation';
        confirmation.innerHTML = `
            <div class="flex items-center">
                <svg class="h-5 w-5 text-blue-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clip-rule="evenodd"/>
                </svg>
                <div>
                    <p class="text-sm font-medium text-blue-800">Reminder Snoozed</p>
                    <p class="text-sm text-blue-600">${medicationName} reminder will show again in 5 minutes</p>
                </div>
            </div>
        `;
        
        document.body.appendChild(confirmation);
        
        // Remove after 3 seconds
        setTimeout(() => {
            if (document.body.contains(confirmation)) {
                confirmation.remove();
            }
        }, 3000);
    }

    // Enhanced notification sound with better audio
    playNotificationSound() {
        try {
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            
            // Create a more attention-grabbing sound pattern
            const playBeep = (frequency, duration, delay = 0) => {
                setTimeout(() => {
                    const oscillator = audioContext.createOscillator();
                    const gainNode = audioContext.createGain();
                    
                    oscillator.connect(gainNode);
                    gainNode.connect(audioContext.destination);
                    
                    oscillator.frequency.value = frequency;
                    oscillator.type = 'sine';
                    
                    gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
                    gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + duration/1000);
                    
                    oscillator.start(audioContext.currentTime);
                    oscillator.stop(audioContext.currentTime + duration/1000);
                }, delay);
            };
            
            // Play a pattern: high-low-high (like a phone ring)
            playBeep(1000, 200, 0);    // High beep
            playBeep(600, 200, 300);    // Low beep  
            playBeep(1000, 300, 600);   // High beep (longer)
            
            // Request notification permission if not granted
            if ("Notification" in window && Notification.permission === "default") {
                Notification.requestPermission();
            }
            
            // Also show browser notification if permitted
            if ("Notification" in window && Notification.permission === "granted") {
                new Notification("Medication Reminder", {
                    body: "Time to take your medication!",
                    icon: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='%23ef4444' viewBox='0 0 20 20'%3E%3Cpath fill-rule='evenodd' d='M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z' clip-rule='evenodd'/%3E%3C/svg%3E",
                    tag: "medication-reminder"
                });
            }
            
        } catch (error) {
            console.log('❌ Audio notification not supported:', error);
        }
    }

    // Confirm taken from notification
    async confirmTakenFromNotification(reminderId) {
        try {
            const token = localStorage.getItem('access_token');
            const response = await fetch(`http://localhost:5000/medication/reminders/${reminderId}/log?taken`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (response.ok) {
                console.log('✅ Medication marked as taken');
                // Refresh reminders
                this.loadReminders();
            }
        } catch (error) {
            console.error('❌ Error logging medication:', error);
        }
    }

    // Skip dose from notification
    async skipDoseFromNotification(reminderId) {
        try {
            const token = localStorage.getItem('access_token');
            const response = await fetch(`http://localhost:5000/medication/reminders/${reminderId}/log?skipped`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (response.ok) {
                console.log('⏭️ Medication marked as skipped');
                // Refresh reminders
                this.loadReminders();
            }
        } catch (error) {
            console.error('❌ Error logging medication:', error);
        }
    }

    // Clear old notification marks to prevent memory buildup
    clearOldNotificationMarks() {
        const now = new Date();
        const twoHoursAgo = now.getTime() - (2 * 60 * 60 * 1000);
        
        for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            if (key && key.startsWith('notified_')) {
                try {
                    const parts = key.split('_');
                    if (parts.length >= 4) {
                        const dateStr = parts[2];
                        const timeStr = parts[3];
                        const notificationTime = new Date(`${dateStr} ${timeStr}:00`);
                        
                        if (notificationTime.getTime() < twoHoursAgo) {
                            localStorage.removeItem(key);
                        }
                    }
                } catch (error) {
                    localStorage.removeItem(key);
                }
            }
        }
    }

    // Stop notification checking
    stop() {
        if (this.checkInterval) {
            clearInterval(this.checkInterval);
            this.checkInterval = null;
        }
        if (this.minuteInterval) {
            clearInterval(this.minuteInterval);
            this.minuteInterval = null;
        }
        this.isInitialized = false;
        console.log('🛑 Notification system stopped');
    }
}

// Create global instance
const globalNotifications = new GlobalNotificationSystem();

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Check if user is authenticated
    const token = localStorage.getItem('access_token');
    if (token) {
        // Initialize notifications
        globalNotifications.init();
    }
});

// Make it globally available
window.globalNotifications = globalNotifications;
