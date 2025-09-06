import re
import uuid
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import pandas as pd  # type: ignore

def generate_appointment_id() -> str:
    """Generate a unique appointment ID"""
    return str(uuid.uuid4())[:8].upper()

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone(phone: str) -> tuple[bool, str]:
    """Validate and format phone number"""
    # Remove all non-digits
    digits = re.sub(r'\D', '', phone)
    
    if len(digits) == 10:
        formatted = f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"
        return True, formatted
    elif len(digits) == 11 and digits[0] == '1':
        formatted = f"{digits[1:4]}-{digits[4:7]}-{digits[7:]}"
        return True, formatted
    else:
        return False, "Invalid phone number format"

def validate_date(date_str: str) -> tuple[bool, str]:
    """Validate and format date"""
    try:
        # Try different date formats
        formats = ['%Y-%m-%d', '%m/%d/%Y', '%m-%d-%Y', '%d/%m/%Y']
        
        for fmt in formats:
            try:
                date_obj = datetime.strptime(date_str, fmt)
                return True, date_obj.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        return False, "Invalid date format"
    except Exception:
        return False, "Invalid date"

def calculate_age(birth_date: str) -> int:
    """Calculate age from birth date"""
    try:
        birth = datetime.strptime(birth_date, '%Y-%m-%d')
        today = datetime.now()
        age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
        return age
    except ValueError:
        return 0

def format_appointment_time(time_str: str) -> str:
    """Format appointment time consistently"""
    try:
        # Parse various time formats
        time_formats = ['%H:%M', '%I:%M %p', '%I:%M%p', '%H%M']
        
        for fmt in time_formats:
            try:
                time_obj = datetime.strptime(time_str.upper(), fmt)
                return time_obj.strftime('%H:%M')
            except ValueError:
                continue
        
        return time_str  # Return original if parsing fails
    except Exception:
        return time_str

def get_business_days(start_date: datetime, num_days: int) -> List[datetime]:
    """Get list of business days starting from a date"""
    business_days = []
    current_date = start_date
    
    while len(business_days) < num_days:
        if current_date.weekday() < 5:  # Monday to Friday
            business_days.append(current_date)
        current_date += timedelta(days=1)
    
    return business_days

def time_until_appointment(appointment_date: str, appointment_time: str) -> Dict[str, Any]:
    """Calculate time until appointment"""
    try:
        appointment_datetime = datetime.strptime(
            f"{appointment_date} {appointment_time}", 
            "%Y-%m-%d %H:%M"
        )
        
        now = datetime.now()
        diff = appointment_datetime - now
        
        if diff.total_seconds() < 0:
            return {
                'status': 'past',
                'message': 'Appointment has passed'
            }
        
        days = diff.days
        hours, remainder = divmod(diff.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        
        return {
            'status': 'upcoming',
            'days': days,
            'hours': hours,
            'minutes': minutes,
            'total_hours': diff.total_seconds() / 3600,
            'message': f"{days} days, {hours} hours, {minutes} minutes"
        }
    
    except ValueError:
        return {
            'status': 'error',
            'message': 'Invalid date/time format'
        }

def load_config(config_file: str = 'config.json') -> Dict:
    """Load configuration from JSON file"""
    default_config = {
        'business_hours': {'start': '09:00', 'end': '17:00'},
        'appointment_duration': {'new_patient': 60, 'returning': 30},
        'reminder_times': [24, 2],  # hours before appointment
        'email_settings': {
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587
        },
        'doctors': [
            {'name': 'Dr. Johnson', 'specialty': 'Family Medicine'},
            {'name': 'Dr. Wilson', 'specialty': 'Internal Medicine'},
            {'name': 'Dr. Smith', 'specialty': 'Cardiology'}
        ]
    }
    
    try:
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)
                # Merge with defaults
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
        else:
            return default_config
    except Exception:
        return default_config

def save_config(config: Dict, config_file: str = 'config.json'):
    """Save configuration to JSON file"""
    try:
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception:
        return False

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file operations"""
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Remove leading/trailing whitespace and dots
    filename = filename.strip('. ')
    
    # Limit length
    if len(filename) > 255:
        filename = filename[:255]
    
    return filename

def export_to_csv(data: List[Dict], filename: str, fieldnames: Optional[List[str]] = None) -> bool:
    """Export data to CSV file"""
    try:
        if not data:
            return False
        
        df = pd.DataFrame(data)
        
        if fieldnames:
            # Reorder columns if fieldnames provided
            df = df.reindex(columns=fieldnames, fill_value='')
        
        df.to_csv(filename, index=False)
        return True
    
    except Exception as e:
        print(f"Error exporting to CSV: {e}")
        return False

def export_to_excel(data: List[Dict], filename: str, sheet_name: str = 'Sheet1') -> bool:
    """Export data to Excel file"""
    try:
        if not data:
            return False
        
        df = pd.DataFrame(data)
        df.to_excel(filename, sheet_name=sheet_name, index=False)
        return True
    
    except Exception as e:
        print(f"Error exporting to Excel: {e}")
        return False

def parse_natural_language_date(date_str: str) -> Optional[str]:
    """Parse natural language date inputs"""
    date_str = date_str.lower().strip()
    today = datetime.now()
    
    # Handle common phrases
    if date_str in ['today']:
        return today.strftime('%Y-%m-%d')
    elif date_str in ['tomorrow']:
        return (today + timedelta(days=1)).strftime('%Y-%m-%d')
    elif date_str in ['next week']:
        return (today + timedelta(days=7)).strftime('%Y-%m-%d')
    elif 'next monday' in date_str:
        days_ahead = 0 - today.weekday()
        if days_ahead <= 0:  # Target day already happened this week
            days_ahead += 7
        return (today + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
    
    # Try to parse as regular date
    is_valid, formatted_date = validate_date(date_str)
    if is_valid:
        return formatted_date
    
    return None

def parse_natural_language_time(time_str: str) -> Optional[str]:
    """Parse natural language time inputs"""
    time_str = time_str.lower().strip()
    
    # Handle common phrases
    time_mappings = {
        'morning': '09:00',
        'noon': '12:00',
        'afternoon': '14:00',
        'evening': '17:00'
    }
    
    if time_str in time_mappings:
        return time_mappings[time_str]
    
    # Try to parse as regular time
    return format_appointment_time(time_str)

def get_available_time_slots(start_time: str = '09:00', end_time: str = '17:00', 
                           duration: int = 30, existing_appointments: Optional[List] = None) -> List[str]:
    """Generate available time slots"""
    if existing_appointments is None:
        existing_appointments = []
    
    slots = []
    start = datetime.strptime(start_time, '%H:%M')
    end = datetime.strptime(end_time, '%H:%M')
    
    current = start
    while current + timedelta(minutes=duration) <= end:
        slot_time = current.strftime('%H:%M')
        
        # Check if slot conflicts with existing appointments
        is_available = True
        for appointment in existing_appointments:
            appt_time = datetime.strptime(appointment.get('time', ''), '%H:%M')
            appt_duration = appointment.get('duration', 30)
            
            appt_end = appt_time + timedelta(minutes=appt_duration)
            slot_end = current + timedelta(minutes=duration)
            
            # Check for overlap
            if current < appt_end and slot_end > appt_time:
                is_available = False
                break
        
        if is_available:
            slots.append(slot_time)
        
        current += timedelta(minutes=30)  # 30-minute intervals
    
    return slots

def log_activity(action: str, details: Optional[Dict] = None, log_file: str = 'activity.log'):
    """Log system activity"""
    timestamp = datetime.now().isoformat()
    
    log_entry = {
        'timestamp': timestamp,
        'action': action,
        'details': details or {}
    }
    
    try:
        # Append to log file
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    except Exception as e:
        print(f"Error logging activity: {e}")

def get_system_stats() -> Dict:
    """Get system statistics"""
    try:
        # Get the directory of this file and construct paths relative to the project root
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        
        patients_file = os.path.join(project_root, 'data', 'patients.csv')
        appointments_file = os.path.join(project_root, 'data', 'appointments.csv')
        
        # Load data files
        patients_df = pd.read_csv(patients_file) if os.path.exists(patients_file) else pd.DataFrame()
        appointments_df = pd.read_csv(appointments_file) if os.path.exists(appointments_file) else pd.DataFrame()
        
        stats = {
            'total_patients': len(patients_df),
            'total_appointments': len(appointments_df),
            'confirmed_appointments': len(appointments_df[appointments_df['status'] == 'Confirmed']) if not appointments_df.empty else 0,
            'pending_appointments': len(appointments_df[appointments_df['status'] == 'Pending']) if not appointments_df.empty else 0,
            'today_appointments': 0
        }
        
        # Count today's appointments
        if not appointments_df.empty:
            today = datetime.now().strftime('%Y-%m-%d')
            stats['today_appointments'] = len(appointments_df[appointments_df['date'] == today])
        
        return stats
    
    except Exception as e:
        print(f"Error getting system stats: {e}")
        return {
            'total_patients': 0,
            'total_appointments': 0,
            'confirmed_appointments': 0,
            'pending_appointments': 0,
            'today_appointments': 0
        }
