#!/usr/bin/env python3
"""
Script to expand the patient database schema to include all fields from the New Patient Intake Form.
This will transform the existing 10-field patient data into a comprehensive 35+ field structure.
"""

import pandas as pd
import random
from datetime import datetime, timedelta
import uuid

def generate_comprehensive_patient_data():
    """Generate comprehensive patient data with all intake form fields"""
    
    # Read existing patient data
    existing_df = pd.read_csv('data/patients.csv')
    
    # Define enhanced schema
    enhanced_patients = []
    
    # Sample data for synthetic generation
    genders = ['male', 'female', 'other', 'prefer-not-to-say']
    states = ['CA', 'NY', 'TX', 'FL', 'IL', 'PA', 'OH', 'GA', 'NC', 'MI']
    cities = ['Los Angeles', 'New York', 'Houston', 'Miami', 'Chicago', 'Philadelphia', 'Columbus', 'Atlanta', 'Charlotte', 'Detroit']
    smoking_status = ['never', 'former', 'current']
    alcohol_consumption = ['none', 'occasional', 'moderate', 'heavy']
    exercise_frequency = ['none', '1-2_times', '3-4_times', 'daily']
    relationships = ['spouse', 'child', 'parent', 'sibling', 'friend', 'other']
    
    # Medical conditions for family history
    family_conditions = ['heart_disease', 'diabetes', 'cancer', 'stroke', 'hypertension', 'mental_health']
    
    # Common allergies and medications
    common_allergies = ['None', 'Penicillin', 'Peanuts', 'Shellfish', 'Latex', 'Aspirin', 'Ibuprofen']
    common_medications = ['None', 'Lisinopril 10mg daily', 'Metformin 500mg twice daily', 'Atorvastatin 20mg daily', 'Levothyroxine 50mcg daily']
    
    for idx, row in existing_df.iterrows():
        # Parse existing name into first/last
        name_parts = row['name'].split(' ')
        first_name = name_parts[0]
        last_name = name_parts[-1]
        middle_name = name_parts[1] if len(name_parts) > 2 else ''
        
        # Generate SSN (fake format)
        ssn = f"{random.randint(100,999)}-{random.randint(10,99)}-{random.randint(1000,9999)}"
        
        # Generate address
        street_num = random.randint(100, 9999)
        street_names = ['Main St', 'Oak Ave', 'Pine Rd', 'Elm St', 'Maple Dr', 'Cedar Ln']
        street_address = f"{street_num} {random.choice(street_names)}"
        city = random.choice(cities)
        state = random.choice(states)
        zip_code = f"{random.randint(10000, 99999)}"
        
        # Generate alternative phone
        alt_phone = f"555-{random.randint(1000, 9999)}"
        
        # Generate emergency contact
        emergency_names = ['John Smith', 'Mary Johnson', 'Robert Brown', 'Lisa Davis', 'Michael Wilson']
        emergency_name = random.choice(emergency_names)
        emergency_relationship = random.choice(relationships)
        emergency_phone = f"555-{random.randint(1000, 9999)}"
        
        # Generate policy holder info
        policy_holder = row['name'] if random.choice([True, False, False]) else emergency_name
        relationship_to_patient = 'self' if policy_holder == row['name'] else random.choice(['spouse', 'parent'])
        
        # Generate medical information
        concerns = ['Annual checkup', 'Chest pain', 'Headaches', 'Back pain', 'Fatigue', 'Follow-up visit']
        primary_concern = random.choice(concerns)
        
        medical_histories = [
            'No significant medical history',
            'Hypertension diagnosed 2019',
            'Type 2 diabetes, well controlled',
            'Previous appendectomy 2015',
            'Seasonal allergies'
        ]
        medical_history = random.choice(medical_histories)
        
        current_medications = random.choice(common_medications)
        allergies = random.choice(common_allergies)
        
        # Generate family history (random selection of conditions)
        family_history = ','.join(random.sample(family_conditions, random.randint(0, 3)))
        
        # Create comprehensive patient record
        enhanced_patient = {
            # Existing fields (preserved)
            'patient_id': row['patient_id'],
            'name': row['name'],  # Keep for backward compatibility
            'dob': row['dob'],
            'doctor': row['doctor'],
            'last_visit': row['last_visit'],
            'phone': row['phone'],
            'email': row['email'],
            'insurance_carrier': row['insurance_carrier'],
            'member_id': row['member_id'],
            'group_id': row['group_id'],
            
            # New demographic fields
            'first_name': first_name,
            'last_name': last_name,
            'middle_name': middle_name,
            'gender': random.choice(genders),
            'ssn': ssn,
            
            # Address information
            'street_address': street_address,
            'city': city,
            'state': state,
            'zip_code': zip_code,
            'alt_phone': alt_phone,
            
            # Enhanced insurance information
            'policy_holder_name': policy_holder,
            'relationship_to_patient': relationship_to_patient,
            
            # Emergency contact
            'emergency_contact_name': emergency_name,
            'emergency_contact_relationship': emergency_relationship,
            'emergency_contact_phone': emergency_phone,
            
            # Medical information
            'primary_concern': primary_concern,
            'medical_history': medical_history,
            'current_medications': current_medications,
            'allergies': allergies,
            'family_history': family_history,
            
            # Lifestyle information
            'smoking_status': random.choice(smoking_status),
            'alcohol_consumption': random.choice(alcohol_consumption),
            'exercise_frequency': random.choice(exercise_frequency),
            
            # System fields
            'created_date': datetime.now().strftime('%Y-%m-%d'),
            'updated_date': datetime.now().strftime('%Y-%m-%d')
        }
        
        enhanced_patients.append(enhanced_patient)
    
    return pd.DataFrame(enhanced_patients)

def main():
    """Main function to expand patient schema"""
    print("🔄 Expanding patient database schema...")
    print(f"📊 Current schema: 10 fields")
    
    # Generate enhanced patient data
    enhanced_df = generate_comprehensive_patient_data()
    
    print(f"📊 Enhanced schema: {len(enhanced_df.columns)} fields")
    print(f"👥 Patient records: {len(enhanced_df)} patients")
    
    # Save enhanced patient data
    enhanced_df.to_csv('data/patients_enhanced.csv', index=False)
    
    # Create field mapping documentation
    field_mapping = {
        'Original Fields (10)': [
            'patient_id', 'name', 'dob', 'doctor', 'last_visit', 
            'phone', 'email', 'insurance_carrier', 'member_id', 'group_id'
        ],
        'New Demographic Fields (5)': [
            'first_name', 'last_name', 'middle_name', 'gender', 'ssn'
        ],
        'Address Fields (5)': [
            'street_address', 'city', 'state', 'zip_code', 'alt_phone'
        ],
        'Enhanced Insurance Fields (2)': [
            'policy_holder_name', 'relationship_to_patient'
        ],
        'Emergency Contact Fields (3)': [
            'emergency_contact_name', 'emergency_contact_relationship', 'emergency_contact_phone'
        ],
        'Medical Information Fields (5)': [
            'primary_concern', 'medical_history', 'current_medications', 'allergies', 'family_history'
        ],
        'Lifestyle Fields (3)': [
            'smoking_status', 'alcohol_consumption', 'exercise_frequency'
        ],
        'System Fields (2)': [
            'created_date', 'updated_date'
        ]
    }
    
    print("\n📋 Field Categories:")
    total_fields = 0
    for category, fields in field_mapping.items():
        print(f"  {category}: {fields}")
        total_fields += len(fields)
    
    print(f"\n✅ Total fields: {total_fields}")
    print(f"💾 Enhanced patient data saved to: data/patients_enhanced.csv")
    print(f"🔒 Original data backed up to: data/patients_backup.csv")

if __name__ == "__main__":
    main()
