from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

class CalendarIntegration:
    def __init__(self):
        self.doctors = {
            'Dr. Johnson': {
                'specialty': 'Family Medicine',
                'working_hours': {'start': '09:00', 'end': '17:00'},
                'working_days': [0, 1, 2, 3, 4],  # Monday to Friday
                'appointment_duration': {'new': 60, 'followup': 30}
            },
            'Dr. Wilson': {
                'specialty': 'Internal Medicine',
                'working_hours': {'start': '08:30', 'end': '16:30'},
                'working_days': [0, 1, 2, 3, 4],
                'appointment_duration': {'new': 60, 'followup': 30}
            },
            'Dr. Smith': {
                'specialty': 'Cardiology',
                'working_hours': {'start': '10:00', 'end': '18:00'},
                'working_days': [0, 1, 2, 3, 4],
                'appointment_duration': {'new': 75, 'followup': 45}
            }
        }
        
        # Mock existing appointments for demonstration
        self.existing_appointments = []
    
    def get_available_slots(self, doctor: Optional[str] = None, date: Optional[str] = None, 
                          duration: int = 30, num_days: int = 7) -> List[Dict]:
        """Get available appointment slots"""
        available_slots = []
        
        start_date = datetime.strptime(date, '%Y-%m-%d') if date else datetime.now() + timedelta(days=1)
        
        doctors_to_check = [doctor] if doctor else list(self.doctors.keys())
        
        for day_offset in range(num_days):
            current_date = start_date + timedelta(days=day_offset)
            
            # Skip weekends for now (can be configured per doctor)
            if current_date.weekday() >= 5:
                continue
                
            for doc_name in doctors_to_check:
                doctor_info = self.doctors[doc_name]
                
                # Check if doctor works on this day
                if current_date.weekday() not in doctor_info['working_days']:
                    continue
                
                slots = self._generate_slots_for_day(doc_name, current_date, duration)
                available_slots.extend(slots)
        
        return available_slots[:20]  # Return first 20 available slots
    
    def _generate_slots_for_day(self, doctor: str, date: datetime, duration: int) -> List[Dict]:
        """Generate available slots for a specific doctor and day"""
        slots = []
        doctor_info = self.doctors[doctor]
        
        # Parse working hours
        start_time = datetime.strptime(doctor_info['working_hours']['start'], '%H:%M').time()
        end_time = datetime.strptime(doctor_info['working_hours']['end'], '%H:%M').time()
        
        # Generate time slots
        current_time = datetime.combine(date.date(), start_time)
        end_datetime = datetime.combine(date.date(), end_time)
        
        while current_time + timedelta(minutes=duration) <= end_datetime:
            slot_time = current_time.time()
            
            # Check if slot is available (not booked)
            if self._is_slot_available(doctor, date.date(), slot_time, duration):
                slots.append({
                    'doctor': doctor,
                    'date': date.strftime('%Y-%m-%d'),
                    'time': slot_time.strftime('%H:%M'),
                    'duration': duration,
                    'available': True,
                    'specialty': doctor_info['specialty']
                })
            
            # Move to next slot (usually 15-30 minute intervals)
            current_time += timedelta(minutes=30)
        
        return slots
    
    def _is_slot_available(self, doctor: str, date, time, duration: int) -> bool:
        """Check if a specific time slot is available"""
        # Check against existing appointments
        for appointment in self.existing_appointments:
            if (appointment['doctor'] == doctor and 
                appointment['date'] == date.strftime('%Y-%m-%d')):
                
                # Parse appointment time
                appt_time = datetime.strptime(appointment['time'], '%H:%M').time()
                slot_time = time
                
                # Check for time conflicts
                appt_start = datetime.combine(date, appt_time)
                appt_end = appt_start + timedelta(minutes=appointment['duration'])
                
                slot_start = datetime.combine(date, slot_time)
                slot_end = slot_start + timedelta(minutes=duration)
                
                # If there's any overlap, slot is not available
                if (slot_start < appt_end and slot_end > appt_start):
                    return False
        
        return True
    
    def book_appointment(self, appointment_details: Dict) -> bool:
        """Book an appointment slot"""
        try:
            # Add to existing appointments to block the slot
            self.existing_appointments.append({
                'doctor': appointment_details['doctor'],
                'date': appointment_details['date'],
                'time': appointment_details['time'],
                'duration': appointment_details['duration'],
                'patient_name': appointment_details.get('patient_name', ''),
                'status': 'booked'
            })
            return True
        except Exception as e:
            print(f"Error booking appointment: {e}")
            return False
    
    def cancel_appointment(self, doctor: str, date: str, time: str) -> bool:
        """Cancel an appointment"""
        try:
            # Remove from existing appointments
            self.existing_appointments = [
                appt for appt in self.existing_appointments
                if not (appt['doctor'] == doctor and 
                       appt['date'] == date and 
                       appt['time'] == time)
            ]
            return True
        except Exception as e:
            print(f"Error cancelling appointment: {e}")
            return False
    
    def get_doctor_schedule(self, doctor: str, date: str) -> List[Dict]:
        """Get full schedule for a doctor on a specific date"""
        doctor_appointments = [
            appt for appt in self.existing_appointments
            if appt['doctor'] == doctor and appt['date'] == date
        ]
        
        return sorted(doctor_appointments, key=lambda x: x['time'])
    
    def get_next_available_slot(self, doctor: Optional[str] = None, duration: int = 30) -> Optional[Dict]:
        """Get the next available appointment slot"""
        available_slots = self.get_available_slots(doctor=doctor, duration=duration, num_days=14)
        
        if available_slots:
            return available_slots[0]
        
        return None
    
    def validate_appointment_time(self, doctor: str, date: str, time: str) -> Dict:
        """Validate if an appointment time is valid"""
        try:
            # Parse date and time
            appointment_date = datetime.strptime(date, '%Y-%m-%d')
            appointment_time = datetime.strptime(time, '%H:%M').time()
            
            # Check if doctor exists
            if doctor not in self.doctors:
                return {'valid': False, 'reason': 'Doctor not found'}
            
            doctor_info = self.doctors[doctor]
            
            # Check if it's a working day
            if appointment_date.weekday() not in doctor_info['working_days']:
                return {'valid': False, 'reason': 'Doctor not available on this day'}
            
            # Check working hours
            start_time = datetime.strptime(doctor_info['working_hours']['start'], '%H:%M').time()
            end_time = datetime.strptime(doctor_info['working_hours']['end'], '%H:%M').time()
            
            if not (start_time <= appointment_time <= end_time):
                return {'valid': False, 'reason': 'Time outside working hours'}
            
            # Check if slot is available
            if not self._is_slot_available(doctor, appointment_date.date(), appointment_time, 30):
                return {'valid': False, 'reason': 'Time slot already booked'}
            
            # Check if it's not in the past
            appointment_datetime = datetime.combine(appointment_date.date(), appointment_time)
            if appointment_datetime <= datetime.now():
                return {'valid': False, 'reason': 'Cannot book appointments in the past'}
            
            return {'valid': True, 'reason': 'Appointment time is valid'}
            
        except ValueError as e:
            return {'valid': False, 'reason': f'Invalid date/time format: {e}'}
    
    def get_calendar_summary(self, date: Optional[str] = None) -> Dict:
        """Get calendar summary for a specific date or today"""
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        summary = {
            'date': date,
            'doctors': {}
        }
        
        for doctor in self.doctors.keys():
            doctor_schedule = self.get_doctor_schedule(doctor, date)
            summary['doctors'][doctor] = {
                'total_appointments': len(doctor_schedule),
                'appointments': doctor_schedule,
                'available_slots': len(self._generate_slots_for_day(
                    doctor, datetime.strptime(date, '%Y-%m-%d'), 30
                ))
            }
        
        return summary
    
    def export_calendar_data(self, start_date: str, end_date: str) -> List[Dict]:
        """Export calendar data for a date range"""
        calendar_events = []
        
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        current_date = start
        while current_date <= end:
            date_str = current_date.strftime('%Y-%m-%d')
            
            for doctor in self.doctors.keys():
                appointments = self.get_doctor_schedule(doctor, date_str)
                
                for appointment in appointments:
                    calendar_events.append({
                        'title': f"Appointment - {appointment.get('patient_name', 'Patient')}",
                        'doctor': doctor,
                        'start': f"{date_str}T{appointment['time']}:00",
                        'end': f"{date_str}T{appointment['time']}:00",  # Would calculate end time
                        'description': f"Duration: {appointment['duration']} minutes"
                    })
            
            current_date += timedelta(days=1)
        
        return calendar_events
