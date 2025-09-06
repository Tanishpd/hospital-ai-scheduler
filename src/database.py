import pandas as pd  # type: ignore
import csv
import os
from datetime import datetime
from typing import Dict, List, Optional, Union

class DatabaseManager:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.patients_file = os.path.join(data_dir, "patients.csv")
        self.appointments_file = os.path.join(data_dir, "appointments.csv")
        self.ensure_files_exist()
    
    def ensure_files_exist(self):
        """Ensure CSV files exist with proper headers"""
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Check and create patients.csv
        if not os.path.exists(self.patients_file):
            with open(self.patients_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'patient_id', 'name', 'dob', 'doctor', 'last_visit', 
                    'phone', 'email', 'insurance_carrier', 'member_id', 'group_id'
                ])
        
        # Check and create appointments.csv
        if not os.path.exists(self.appointments_file):
            with open(self.appointments_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'appointment_id', 'patient_id', 'patient_name', 'doctor', 
                    'date', 'time', 'duration', 'status', 'insurance_verified', 'confirmation_sent'
                ])
    
    def load_patients(self) -> pd.DataFrame:
        """Load patients from CSV file"""
        try:
            return pd.read_csv(self.patients_file)
        except (FileNotFoundError, pd.errors.EmptyDataError):
            return pd.DataFrame(columns=[
                'patient_id', 'name', 'dob', 'doctor', 'last_visit', 
                'phone', 'email', 'insurance_carrier', 'member_id', 'group_id'
            ])
    
    def load_appointments(self) -> pd.DataFrame:
        """Load appointments from CSV file"""
        try:
            return pd.read_csv(self.appointments_file)
        except (FileNotFoundError, pd.errors.EmptyDataError):
            return pd.DataFrame(columns=[
                'appointment_id', 'patient_id', 'patient_name', 'doctor', 
                'date', 'time', 'duration', 'status', 'insurance_verified', 'confirmation_sent'
            ])
    
    def search_patient(self, name: str, dob: Optional[str] = None) -> Optional[Dict]:
        """Search for patient by name and optionally DOB"""
        patients_df = self.load_patients()
        
        if patients_df.empty:
            return None
        
        # Normalize search terms
        name_clean = name.strip().lower()
        
        # Search conditions
        name_condition = patients_df['name'].str.lower().str.contains(name_clean, na=False)
        
        if dob:
            dob_condition = patients_df['dob'] == dob
            result = patients_df[name_condition & dob_condition]
        else:
            result = patients_df[name_condition]
        
        if not result.empty:
            return result.iloc[0].to_dict()
        
        return None
    
    def add_patient(self, patient_data: Dict) -> str:
        """Add new patient to database"""
        patients_df = self.load_patients()
        
        # Generate new patient ID
        if patients_df.empty:
            new_id = 1
        else:
            new_id = patients_df['patient_id'].max() + 1
        
        patient_data['patient_id'] = new_id
        
        # Add to dataframe and save
        new_patient_df = pd.DataFrame([patient_data])
        patients_df = pd.concat([patients_df, new_patient_df], ignore_index=True)
        patients_df.to_csv(self.patients_file, index=False)
        
        return str(new_id)
    
    def add_appointment(self, appointment_data: Dict) -> bool:
        """Add new appointment to database"""
        try:
            appointments_df = self.load_appointments()
            
            # Add timestamp
            appointment_data['created_at'] = datetime.now().isoformat()
            
            # Add to dataframe and save
            new_appointment_df = pd.DataFrame([appointment_data])
            appointments_df = pd.concat([appointments_df, new_appointment_df], ignore_index=True)
            appointments_df.to_csv(self.appointments_file, index=False)
            
            return True
        except Exception as e:
            print(f"Error adding appointment: {e}")
            return False
    
    def get_appointments_by_date(self, date: str) -> List[Dict]:
        """Get all appointments for a specific date"""
        appointments_df = self.load_appointments()
        
        if appointments_df.empty:
            return []
        
        date_appointments = appointments_df[appointments_df['date'] == date]
        return date_appointments.to_dict('records')
    
    def get_patient_appointments(self, patient_id: str) -> List[Dict]:
        """Get all appointments for a specific patient"""
        appointments_df = self.load_appointments()
        
        if appointments_df.empty:
            return []
        
        patient_appointments = appointments_df[appointments_df['patient_id'] == patient_id]
        return patient_appointments.to_dict('records')
    
    def update_appointment_status(self, appointment_id: str, status: str) -> bool:
        """Update appointment status"""
        try:
            appointments_df = self.load_appointments()
            
            if appointment_id in appointments_df['appointment_id'].values:
                appointments_df.loc[appointments_df['appointment_id'] == appointment_id, 'status'] = status
                appointments_df.to_csv(self.appointments_file, index=False)
                return True
            
            return False
        except Exception as e:
            print(f"Error updating appointment status: {e}")
            return False
    
    def export_appointments_to_excel(self, output_file: Optional[str] = None) -> Optional[str]:
        """Export appointments to Excel file"""
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"appointments_export_{timestamp}.xlsx"
        
        appointments_df = self.load_appointments()
        
        if not appointments_df.empty:
            appointments_df.to_excel(output_file, index=False)
            return output_file
        else:
            return None
    
    def get_database_stats(self) -> Dict:
        """Get database statistics"""
        patients_df = self.load_patients()
        appointments_df = self.load_appointments()
        
        stats = {
            'total_patients': len(patients_df),
            'total_appointments': len(appointments_df),
            'confirmed_appointments': len(appointments_df[appointments_df['status'] == 'Confirmed']) if not appointments_df.empty else 0,
            'pending_appointments': len(appointments_df[appointments_df['status'] == 'Pending']) if not appointments_df.empty else 0
        }
        
        return stats
    
    def generate_synthetic_data(self, num_patients: int = 50):
        """Generate synthetic patient data for testing"""
        import random
        from datetime import datetime, timedelta
        
        first_names = [
            'John', 'Jane', 'Michael', 'Sarah', 'David', 'Emily', 'Robert', 'Lisa',
            'Christopher', 'Amanda', 'Matthew', 'Ashley', 'Daniel', 'Jessica', 'James'
        ]
        
        last_names = [
            'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller',
            'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez'
        ]
        
        doctors = ['Dr. Johnson', 'Dr. Wilson', 'Dr. Smith', 'Dr. Brown', 'Dr. Davis']
        
        insurance_carriers = [
            'Blue Cross Blue Shield', 'Aetna', 'UnitedHealth', 'Cigna', 
            'Kaiser Permanente', 'Humana', 'Anthem', 'Medicaid', 'Medicare'
        ]
        
        patients_data = []
        
        for i in range(num_patients):
            # Generate random patient data
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            name = f"{first_name} {last_name}"
            
            # Random DOB between 1940 and 2005
            start_date = datetime(1940, 1, 1)
            end_date = datetime(2005, 12, 31)
            time_between = end_date - start_date
            days_between = time_between.days
            random_days = random.randrange(days_between)
            dob = start_date + timedelta(days=random_days)
            
            # Random last visit in the past 2 years
            last_visit = datetime.now() - timedelta(days=random.randint(1, 730))
            
            patient = {
                'patient_id': i + 1,
                'name': name,
                'dob': dob.strftime('%Y-%m-%d'),
                'doctor': random.choice(doctors),
                'last_visit': last_visit.strftime('%Y-%m-%d'),
                'phone': f"555-{random.randint(1000, 9999)}",
                'email': f"{first_name.lower()}.{last_name.lower()}@email.com",
                'insurance_carrier': random.choice(insurance_carriers),
                'member_id': f"{random.choice(['BC', 'AET', 'UH', 'CIG', 'KP'])}{random.randint(100000000, 999999999)}",
                'group_id': f"GRP{random.randint(100, 999)}"
            }
            
            patients_data.append(patient)
        
        # Save to CSV
        patients_df = pd.DataFrame(patients_data)
        patients_df.to_csv(self.patients_file, index=False)
        
        print(f"Generated {num_patients} synthetic patient records")
        return patients_df
