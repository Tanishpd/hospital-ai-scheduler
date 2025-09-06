#!/usr/bin/env python3
"""
Script to generate doctor schedule Excel files
"""
import pandas as pd  # type: ignore
import os
from datetime import datetime, timedelta
import random

def create_doctor_schedules():
    """Create Excel files with doctor availability schedules"""
    
    # Ensure data directory exists
    os.makedirs('data/doctor_schedules', exist_ok=True)
    
    # Doctor information
    doctors = [
        {'name': 'Dr. Johnson', 'specialty': 'Internal Medicine', 'room': '101'},
        {'name': 'Dr. Wilson', 'specialty': 'Cardiology', 'room': '205'},
        {'name': 'Dr. Smith', 'specialty': 'Pediatrics', 'room': '302'},
        {'name': 'Dr. Davis', 'specialty': 'Dermatology', 'room': '150'},
        {'name': 'Dr. Brown', 'specialty': 'Orthopedics', 'room': '220'}
    ]
    
    # Generate schedules for next 30 days
    start_date = datetime.now().date()
    
    for doctor in doctors:
        schedule_data = []
        
        for day_offset in range(30):
            current_date = start_date + timedelta(days=day_offset)
            
            # Skip weekends for most doctors
            if current_date.weekday() >= 5:  # Saturday = 5, Sunday = 6
                if random.random() > 0.2:  # 20% chance of weekend availability
                    continue
            
            # Generate time slots for the day
            # Morning slots: 9:00 AM - 12:00 PM
            morning_slots = ['09:00', '09:30', '10:00', '10:30', '11:00', '11:30']
            
            # Afternoon slots: 2:00 PM - 5:00 PM  
            afternoon_slots = ['14:00', '14:30', '15:00', '15:30', '16:00', '16:30']
            
            all_slots = morning_slots + afternoon_slots
            
            # Randomly remove some slots to simulate existing appointments
            available_slots = [slot for slot in all_slots if random.random() > 0.3]
            
            for slot in available_slots:
                schedule_data.append({
                    'Date': current_date.strftime('%Y-%m-%d'),
                    'Day': current_date.strftime('%A'),
                    'Time': slot,
                    'Doctor': doctor['name'],
                    'Specialty': doctor['specialty'],
                    'Room': doctor['room'],
                    'Status': 'Available',
                    'Duration': '30 min',
                    'Notes': ''
                })
        
        # Create DataFrame and save to Excel
        df = pd.DataFrame(schedule_data)
        filename = f"data/doctor_schedules/{doctor['name'].replace(' ', '_')}_schedule.xlsx"
        
        # Create Excel file with multiple sheets
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Main schedule sheet
            df.to_excel(writer, sheet_name='Schedule', index=False)
            
            # Doctor info sheet
            doctor_info = pd.DataFrame([{
                'Doctor Name': doctor['name'],
                'Specialty': doctor['specialty'],
                'Room Number': doctor['room'],
                'Total Available Slots': len(df),
                'Schedule Period': f"{start_date} to {start_date + timedelta(days=29)}"
            }])
            doctor_info.to_excel(writer, sheet_name='Doctor_Info', index=False)
            
            # Weekly summary
            weekly_summary = df.groupby('Day').size().reset_index(name='Available_Slots')
            weekly_summary.to_excel(writer, sheet_name='Weekly_Summary', index=False)
        
        print(f"✅ Created schedule for {doctor['name']}: {filename}")
    
    # Create master schedule file with all doctors
    master_schedule = []
    for doctor in doctors:
        filename = f"data/doctor_schedules/{doctor['name'].replace(' ', '_')}_schedule.xlsx"
        doctor_df = pd.read_excel(filename, sheet_name='Schedule')
        master_schedule.append(doctor_df)
    
    # Combine all schedules
    master_df = pd.concat(master_schedule, ignore_index=True)
    master_df = master_df.sort_values(['Date', 'Time', 'Doctor'])
    
    # Save master schedule
    master_filename = "data/doctor_schedules/Master_Schedule.xlsx"
    with pd.ExcelWriter(master_filename, engine='openpyxl') as writer:
        master_df.to_excel(writer, sheet_name='All_Doctors', index=False)
        
        # Summary by doctor
        doctor_summary = master_df.groupby('Doctor').agg({
            'Date': 'nunique',
            'Time': 'count'
        }).rename(columns={'Date': 'Days_Available', 'Time': 'Total_Slots'}).reset_index()
        doctor_summary.to_excel(writer, sheet_name='Doctor_Summary', index=False)
    
    print(f"✅ Created master schedule: {master_filename}")
    print(f"📊 Total available slots across all doctors: {len(master_df)}")

if __name__ == "__main__":
    create_doctor_schedules()
