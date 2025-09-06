"""
Simple Free LangGraph Implementation for Medical Scheduling
Uses basic Python classes to demonstrate LangGraph + LangChain concepts without external dependencies.
"""

from typing import Dict, List, Optional, Any
import json
import random
from datetime import datetime, timedelta
from database import DatabaseManager

class MockAppointmentState:
    """Simple state management for the appointment workflow"""
    def __init__(self):
        self.messages = []
        self.current_step = "start"
        self.patient_info = {}
        self.appointment_info = {}
        self.insurance_info = {}
        self.conversation_history = []
        self.current_field = ""  # Track which field we're currently asking for
        self.pending_fields = []   # Track what info we still need

class MockMessage:
    """Simple message class"""
    def __init__(self, content: str, message_type: str = "human"):
        self.content = content
        self.type = message_type

class SimpleLangGraphAgent:
    """
    Simplified LangGraph + LangChain Implementation
    Demonstrates multi-agent orchestration without complex dependencies
    """
    
    def __init__(self):
        """Initialize the free multi-agent system"""
        self.agents = {
            "greeting": self.greeting_agent,
            "patient_intake": self.patient_intake_agent,
            "emr_lookup": self.emr_lookup_agent,
            "scheduling": self.scheduling_agent,
            "insurance": self.insurance_agent,
            "confirmation": self.confirmation_agent
        }
        
        # Initialize database manager
        self.db_manager = DatabaseManager()
        
        # Agent workflow order
        self.workflow = [
            "greeting", "patient_intake", "emr_lookup", 
            "scheduling", "insurance", "confirmation"
        ]
        
        self.current_agent_index = 0
        self.state = MockAppointmentState()
        
        # Define required fields for each step
        self.required_fields = {
            "patient_intake": ["name", "phone", "email"],
            "insurance": ["carrier", "member_id"]
        }
        
        # User-friendly field names
        self.field_prompts = {
            "name": "What's your full name?",
            "phone": "What's your phone number?", 
            "email": "What's your email address?",
            "carrier": "What's your insurance carrier (e.g., Blue Cross, Aetna, etc.)?",
            "member_id": "What's your insurance member ID number?"
        }
        
        # Mock responses for demonstration
        self.responses = {
            "greeting": [
                "Hello! Welcome to our medical practice. I'm your AI scheduling assistant powered by LangGraph + LangChain.\n\nI'll help you book an appointment step by step. Let's start with the basics - what's your full name?",
                "Hi! I'm your free LangGraph-powered scheduling assistant. To get started, could you please tell me your full name?"
            ]
        }
    
    def reset_state(self):
        """Reset the conversation state for a new interaction"""
        self.state = MockAppointmentState()
    
    def greeting_agent(self, user_input: str) -> str:
        """Greeting Agent - Handles initial patient interaction and determines request type"""
        user_input_lower = user_input.lower()
        
        # Check for cancellation requests
        if any(word in user_input_lower for word in ['cancel', 'cancellation', 'cancelled']):
            self.state.current_step = "cancellation"
            return """🚫 **Cancellation Agent**: I'll help you cancel your appointment.

To cancel your appointment, I'll need some information:

**Please provide your appointment details:**
1. Your full name
2. Appointment date (e.g., September 5, 2025)
3. Appointment time (e.g., 10:00 AM)
4. Doctor's name

Let's start - what's your full name?"""
        
        # Check for rescheduling requests  
        elif any(word in user_input_lower for word in ['reschedule', 'rescheduling', 'change', 'move']):
            self.state.current_step = "rescheduling"
            return """🔄 **Rescheduling Agent**: I'll help you reschedule your appointment.

To reschedule your appointment, I'll need some information:

**First, your current appointment details:**
1. Your full name
2. Current appointment date (e.g., September 5, 2025)
3. Current appointment time (e.g., 10:00 AM)
4. Doctor's name

Then I'll help you find a new time that works better for you.

Let's start - what's your full name?"""
        
        # Default to new appointment booking
        else:
            response = random.choice(self.responses["greeting"])
            self.state.current_step = "patient_intake"
            # Set up patient intake fields
            self.state.pending_fields = self.required_fields["patient_intake"].copy()
            self.state.current_field = self.state.pending_fields[0]  # Start with name
            
            # Clear any existing data
            self.state.patient_info = {}
            self.state.appointment_info = {}
            self.state.insurance_info = {}
            
            return f"🤖 **Greeting Agent**: {response}"
    
    def patient_intake_agent(self, user_input: str) -> str:
        """Patient Intake Agent - Collects patient information one field at a time"""
        
        # If no current field is set, start with name
        if not self.state.current_field or not self.state.pending_fields:
            self.state.pending_fields = self.required_fields["patient_intake"].copy()
            self.state.current_field = "name"
        
        # Process the current field
        if self.state.current_field == "name":
            # Extract name from user input
            name = user_input.strip()
            if len(name.split()) >= 2:  # Ensure at least first and last name
                self.state.patient_info["name"] = name.title()
                
                # Automatically search for existing patient by name
                patients_df = self.db_manager.load_patients()
                
                if not patients_df.empty:
                    # Search for patients with this name (case-insensitive)
                    mask = patients_df['name'].str.contains(name, case=False, na=False)
                    matching_patients = patients_df[mask]
                    
                    if len(matching_patients) == 1:
                        # Exactly one patient found - auto-populate details
                        patient = matching_patients.iloc[0]
                        self.state.patient_info["phone"] = patient['phone']
                        self.state.patient_info["email"] = patient['email']
                        
                        # Remove all fields since we have the data
                        self.state.pending_fields = []
                        self.state.current_field = ""
                        
                        # Automatically proceed to EMR lookup
                        self.state.current_step = "emr_lookup"
                        
                        return f"""✅ **Patient Intake Agent**: Welcome back, {name.title()}! 

I found your information in our system:
📞 **Phone:** {patient['phone']}
📧 **Email:** {patient['email']}

{self.emr_lookup_agent("")}"""
                        
                    elif len(matching_patients) > 1:
                        # Multiple patients found - ask for email to distinguish
                        phone_list = ""
                        email_list = ""
                        for idx, patient in matching_patients.iterrows():
                            phone_list += f"• {patient['phone']}\n"
                            email_list += f"• {patient['email']}\n"
                        
                        # Keep name but ask for email to distinguish
                        self.state.pending_fields.remove("name")
                        self.state.current_field = "email"
                        
                        return f"""✅ **Patient Intake Agent**: I found **{len(matching_patients)} patients** with the name "{name.title()}" in our system.

To identify your record, please provide your **email address**:

**Registered emails:**
{email_list}

What's your email address?"""
                        
                    else:
                        # No existing patient found - proceed with full intake
                        if "name" in self.state.pending_fields:
                            self.state.pending_fields.remove("name")
                        
                        # Set next field to phone
                        self.state.current_field = "phone"
                        
                        return f"""✅ **Patient Intake Agent**: Hello {name.title()}! I don't see you in our system yet, so I'll need to collect some basic information.

What's your phone number? (e.g., 555-123-4567)"""
                        
                else:
                    # No patients in database - proceed with full intake
                    if "name" in self.state.pending_fields:
                        self.state.pending_fields.remove("name")
                    
                    # Set next field to phone
                    self.state.current_field = "phone"
                    
                    return f"""✅ **Patient Intake Agent**: Hello {name.title()}! Welcome to our practice.

What's your phone number? (e.g., 555-123-4567)"""
                
            else:
                return f"📝 **Patient Intake Agent**: Please provide your full name (first and last name)."
                
        elif self.state.current_field == "phone":
            # Extract and validate phone number
            phone = ''.join(filter(str.isdigit, user_input))
            if len(phone) >= 10:
                # Format phone number
                formatted_phone = f"({phone[:3]}) {phone[3:6]}-{phone[6:10]}"
                
                # Check if this is for patient verification
                patient_name = self.state.patient_info.get("name", "")
                patient_email = self.state.patient_info.get("email", "")
                
                if patient_name and patient_email:
                    patients_df = self.db_manager.load_patients()
                    
                    if not patients_df.empty:
                        # Search for patient with name, email, and phone match
                        mask = (
                            patients_df['name'].str.contains(patient_name, case=False, na=False) &
                            patients_df['email'].str.contains(patient_email, case=False, na=False) &
                            patients_df['phone'].str.contains(phone, na=False)
                        )
                        matching_patient = patients_df[mask]
                        
                        if len(matching_patient) == 1:
                            # Found exact match - use existing patient data
                            patient = matching_patient.iloc[0]
                            self.state.patient_info["phone"] = patient['phone']
                            self.state.patient_info["email"] = patient['email']
                            
                            # Clear all pending fields
                            self.state.pending_fields = []
                            self.state.current_field = ""
                            
                            # Proceed to EMR lookup
                            self.state.current_step = "emr_lookup"
                            
                            return f"""✅ **Patient Intake Agent**: Great! I verified your identity, {patient_name}.

📞 **Phone:** {patient['phone']}
📧 **Email:** {patient['email']}

{self.emr_lookup_agent("")}"""
                        
                        else:
                            # No match found - treat as new patient
                            self.state.patient_info["phone"] = formatted_phone
                            if "phone" in self.state.pending_fields:
                                self.state.pending_fields.remove("phone")
                            
                            # Continue with next field or complete intake
                            if self.state.pending_fields:
                                self.state.current_field = self.state.pending_fields[0]
                                if self.state.current_field == "email":
                                    return f"""⚠️ **Patient Intake Agent**: I couldn't find an existing record with those details. I'll create a new patient record for you.

✅ **Phone:** {formatted_phone}

Now I need your email address:
What's your email address?"""
                                else:
                                    field_prompt = self.field_prompts.get(self.state.current_field, "Please provide the required information.")
                                    return f"""⚠️ **Patient Intake Agent**: I couldn't find an existing record with those details. I'll create a new patient record for you.

✅ **Phone:** {formatted_phone}

{field_prompt}"""
                            else:
                                # All fields collected, proceed to EMR lookup
                                self.state.current_step = "emr_lookup"
                                self.state.current_field = ""
                                return f"""⚠️ **Patient Intake Agent**: I couldn't find an existing record with those details. I'll create a new patient record for you.

✅ **Phone:** {formatted_phone}

{self.emr_lookup_agent("")}"""
                
                # Default phone handling for new patients
                self.state.patient_info["phone"] = formatted_phone
                if "phone" in self.state.pending_fields:
                    self.state.pending_fields.remove("phone")
            else:
                return f"📝 **Patient Intake Agent**: Please provide a valid phone number (10 digits)."
                
        elif self.state.current_field == "email":
            # Basic email validation
            if "@" in user_input and "." in user_input:
                email_input = user_input.lower().strip()
                
                # Check if this is for patient verification (multiple patients with same name)
                patient_name = self.state.patient_info.get("name", "")
                if patient_name:
                    patients_df = self.db_manager.load_patients()
                    
                    if not patients_df.empty:
                        # Search for patient with exact name and email match
                        mask = (
                            patients_df['name'].str.contains(patient_name, case=False, na=False) &
                            patients_df['email'].str.contains(email_input, case=False, na=False)
                        )
                        matching_patient = patients_df[mask]
                        
                        if len(matching_patient) == 1:
                            # Found exact match - auto-populate all details
                            patient = matching_patient.iloc[0]
                            self.state.patient_info["phone"] = patient['phone']
                            self.state.patient_info["email"] = patient['email']
                            
                            # Clear all pending fields
                            self.state.pending_fields = []
                            self.state.current_field = ""
                            
                            # Proceed to EMR lookup
                            self.state.current_step = "emr_lookup"
                            
                            return f"""✅ **Patient Intake Agent**: Perfect! I found your record, {patient_name}.

📞 **Phone:** {patient['phone']}
📧 **Email:** {patient['email']}

{self.emr_lookup_agent("")}"""
                        
                        elif len(matching_patient) == 0:
                            # Email not found - ask for phone number for additional verification
                            self.state.patient_info["email"] = email_input
                            if "email" in self.state.pending_fields:
                                self.state.pending_fields.remove("email")
                            
                            if "phone" not in self.state.pending_fields:
                                self.state.pending_fields.append("phone")
                            self.state.current_field = "phone"
                            
                            return f"""⚠️ **Patient Intake Agent**: I don't see that email in our records for {patient_name}.

Let me get your phone number to verify your identity:
What's your phone number? (e.g., 555-123-4567)"""
                        
                        else:
                            # Multiple matches still (shouldn't happen but handle gracefully)
                            self.state.patient_info["email"] = email_input
                            if "email" in self.state.pending_fields:
                                self.state.pending_fields.remove("email")
                            
                            return f"""✅ **Patient Intake Agent**: Thank you! Now I need your phone number to complete verification.

What's your phone number? (e.g., 555-123-4567)"""
                    
                # Default email handling for new patients
                self.state.patient_info["email"] = email_input
                if "email" in self.state.pending_fields:
                    self.state.pending_fields.remove("email")
            else:
                return f"📝 **Patient Intake Agent**: Please provide a valid email address."
        
        # Check if we have more fields to collect
        if self.state.pending_fields:
            # Move to next field
            self.state.current_field = self.state.pending_fields[0]
            field_prompt = self.field_prompts[self.state.current_field]
            return f"📝 **Patient Intake Agent**: Great! Now, {field_prompt}"
        else:
            # All patient info collected, automatically proceed to EMR lookup
            self.state.current_step = "emr_lookup"
            self.state.current_field = ""  # Clear current field
            
            # Automatically perform EMR lookup without waiting for user input
            return self.emr_lookup_agent("")
    
    def emr_lookup_agent(self, user_input: str) -> str:
        """EMR Lookup Agent - Searches electronic medical records"""
        # Default appointment type when called automatically
        appointment_type = "standard"
        duration = 30
        
        # Check for appointment type preferences in user input (if any)
        user_lower = user_input.lower()
        if any(word in user_lower for word in ["annual", "checkup", "physical", "routine"]):
            appointment_type = "annual_checkup"
            duration = 45
        elif any(word in user_lower for word in ["sick", "illness", "symptoms", "urgent"]):
            appointment_type = "sick_visit"
            duration = 20
        elif any(word in user_lower for word in ["follow", "followup", "follow-up"]):
            appointment_type = "follow_up"
            duration = 30
        elif any(word in user_lower for word in ["urgent", "emergency", "asap"]):
            appointment_type = "urgent_care"
            duration = 15
        
        # Simulate EMR lookup
        is_returning = random.choice([True, False])
        
        if is_returning:
            response = f"� **Patient Intake Agent**: Perfect! I have all your information:\n\n• Name: {self.state.patient_info['name']}\n• Phone: {self.state.patient_info['phone']}\n• Email: {self.state.patient_info['email']}\n\n�🔍 **EMR Lookup Agent**: Searching our Electronic Medical Records system...\n\n✅ **Search complete!** Great news! I found you're a returning patient, {self.state.patient_info.get('name', 'there')}! Welcome back.\n\n📋 **What type of appointment would you like?**\n• Annual checkup/physical\n• Sick visit\n• Follow-up appointment\n• Routine consultation\n\nPlease let me know what brings you in today!"
            self.state.appointment_info = {"duration": duration, "type": appointment_type}
        else:
            # For new patients, add extra time
            duration += 15
            response = f"📝 **Patient Intake Agent**: Perfect! I have all your information:\n\n• Name: {self.state.patient_info['name']}\n• Phone: {self.state.patient_info['phone']}\n• Email: {self.state.patient_info['email']}\n\n🔍 **EMR Lookup Agent**: Searching our Electronic Medical Records system...\n\n✅ **Search complete!** Welcome to our practice, {self.state.patient_info.get('name', 'there')}! You're a new patient.\n\n📋 **What type of appointment would you like?**\n• Annual checkup/physical (60 min)\n• Sick visit (35 min)\n• Follow-up appointment (45 min)\n• Routine consultation (45 min)\n\nAs a new patient, we'll include extra time for intake. Please let me know what brings you in today!"
            self.state.appointment_info = {"duration": duration, "type": f"new_patient_{appointment_type}"}
        
        self.state.current_step = "scheduling"
        return response
    
    def scheduling_agent(self, user_input: str) -> str:
        """Scheduling Agent - Handles appointment booking"""
        # Check for time preferences
        user_lower = user_input.lower()
        preferred_time = "morning"  # default
        preferred_doctor = None  # Changed to None to detect no preference
        
        # Check for doctor preferences
        if any(word in user_lower for word in ["female", "woman", "lady"]):
            preferred_doctor = "female"
            doctor_name = "Dr. Wilson"
        elif any(word in user_lower for word in ["johnson", "dr johnson", "dr. johnson"]):
            preferred_doctor = "johnson"
            doctor_name = "Dr. Johnson"
        elif any(word in user_lower for word in ["wilson", "dr wilson", "dr. wilson"]):
            preferred_doctor = "wilson"
            doctor_name = "Dr. Wilson"
        elif any(word in user_lower for word in ["smith", "dr smith", "dr. smith"]):
            preferred_doctor = "smith"
            doctor_name = "Dr. Smith"
        elif any(word in user_lower for word in ["brown", "dr brown", "dr. brown"]):
            preferred_doctor = "brown"
            doctor_name = "Dr. Brown"
        elif any(word in user_lower for word in ["davis", "dr davis", "dr. davis"]):
            preferred_doctor = "davis"
            doctor_name = "Dr. Davis"
        elif any(word in user_lower for word in ["any doctor", "anyone", "doesn't matter"]):
            preferred_doctor = "any"
            doctor_name = "Dr. Johnson"  # default
        else:
            # No specific doctor mentioned - show all available doctors
            preferred_doctor = None
            doctor_name = "Dr. Johnson"  # default
        
        # Check for time preferences
        if any(word in user_lower for word in ["afternoon", "pm", "after lunch", "later"]):
            preferred_time = "afternoon"
            default_time = "14:00"
            time_display = "2:00 PM"
        elif any(word in user_lower for word in ["morning", "am", "early", "before lunch"]):
            preferred_time = "morning"
            default_time = "09:00"
            time_display = "9:00 AM"
        elif any(word in user_lower for word in ["urgent", "asap", "emergency", "today"]):
            preferred_time = "urgent"
            default_time = "11:00"
            time_display = "11:00 AM (Next Available)"
        else:
            default_time = "09:00"
            time_display = "9:00 AM"
        
        # Get appointment details
        duration = self.state.appointment_info.get("duration", 30)
        appointment_type = self.state.appointment_info.get("type", "follow_up")
        
        # If no specific doctor mentioned, show all available doctors
        if preferred_doctor is None:
            response = f"📅 **Scheduling Agent**: Perfect! I'll help you schedule your {duration}-minute {appointment_type.replace('_', ' ')} appointment.\n\n👨‍⚕️ **Please choose your preferred doctor:**\n\n1. **Dr. Johnson** - Internal Medicine\n   📅 Sept 5, 2025 at 9:00 AM (30 min)\n   \n2. **Dr. Wilson** - Family Medicine  \n   📅 Sept 5, 2025 at 2:00 PM (30 min)\n   \n3. **Dr. Smith** - Cardiology\n   📅 Sept 6, 2025 at 10:00 AM (30 min)\n   \n4. **Dr. Brown** - Orthopedics\n   📅 Sept 6, 2025 at 3:00 PM (30 min)\n   \n5. **Dr. Davis** - Dermatology\n   📅 Sept 7, 2025 at 11:00 AM (30 min)\n\n💬 **Just type the doctor's name you prefer** (e.g., \"Dr. Johnson\" or \"I want Dr. Wilson\")"
            
            self.state.current_step = "scheduling_doctor_select"
            return response
        
        # If doctor is specified, proceed with booking
        return self.book_with_specific_doctor(preferred_doctor, doctor_name, preferred_time, default_time, time_display, duration, appointment_type)
    
    def book_with_specific_doctor(self, preferred_doctor, doctor_name, preferred_time, default_time, time_display, duration, appointment_type):
        """Handle booking with a specific doctor"""
        # Simulate appointment booking
        self.state.appointment_info.update({
            "doctor": doctor_name,
            "date": "2025-09-05", 
            "time": default_time,
            "time_preference": preferred_time,
            "doctor_preference": preferred_doctor,
            "appointment_id": f"APT-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
        })
        
        # Create customized response based on preferences
        if preferred_time == "urgent":
            response = f"📅 **Scheduling Agent**: I understand you need urgent care! Let me check our emergency slots...\n\n🆘 **URGENT APPOINTMENT AVAILABLE**\n\n1. {doctor_name} - Internal Medicine\n   📅 Date: September 4, 2025 (Tomorrow)\n   🕘 Time: {time_display}\n   ⏱️ Duration: {duration} minutes\n   🔥 Type: {appointment_type.replace('_', ' ').title()}\n\nThis urgent slot is reserved for you. Does this work?"
        elif preferred_doctor == "female":
            response = f"📅 **Scheduling Agent**: Perfect! I found appointments with our female physician Dr. Wilson:\n\n1. Dr. Wilson - Family Medicine (Female)\n   📅 Date: September 5, 2025\n   🕘 Time: {time_display}\n   ⏱️ Duration: {duration} minutes\n   👩‍⚕️ Female physician as requested\n\n2. Dr. Wilson - Family Medicine (Female)\n   📅 Date: September 6, 2025\n   🕘 Time: 10:00 AM\n   ⏱️ Duration: {duration} minutes\n\nI'll book you with Dr. Wilson for September 5th at {time_display}. Does this work for you?"
        elif preferred_doctor == "johnson":
            response = f"📅 **Scheduling Agent**: Excellent! Dr. Johnson is available for your appointment:\n\n1. Dr. Johnson - Internal Medicine\n   📅 Date: September 5, 2025\n   🕘 Time: {time_display}\n   ⏱️ Duration: {duration} minutes\n   👨‍⚕️ Dr. Johnson as specifically requested\n\nI'll book you with Dr. Johnson for September 5th at {time_display}. Does this work for you?"
        else:
            response = f"📅 **Scheduling Agent**: Great! I found {preferred_time} appointments for your {duration}-minute {appointment_type.replace('_', ' ')} appointment:\n\n1. {doctor_name} - Internal Medicine\n   📅 Date: September 5, 2025\n   🕘 Time: {time_display}\n   ⏱️ Duration: {duration} minutes\n\n2. Dr. Wilson - Family Medicine\n   📅 Date: September 6, 2025\n   🕘 Time: 8:30 AM\n   ⏱️ Duration: {duration} minutes\n\nI'll book you with {doctor_name} for September 5th at {time_display}. Does this work for you?"
        
        self.state.current_step = "scheduling_confirm"
        return response
        
    def handle_doctor_selection(self, user_input: str) -> str:
        """Handle doctor selection from the list"""
        user_lower = user_input.lower()
        
        # Map doctor selection to preferences
        if any(word in user_lower for word in ["johnson", "dr johnson", "dr. johnson", "1"]):
            preferred_doctor = "johnson"
            doctor_name = "Dr. Johnson"
        elif any(word in user_lower for word in ["wilson", "dr wilson", "dr. wilson", "2"]):
            preferred_doctor = "wilson"
            doctor_name = "Dr. Wilson"
        elif any(word in user_lower for word in ["smith", "dr smith", "dr. smith", "3"]):
            preferred_doctor = "smith"
            doctor_name = "Dr. Smith"
        elif any(word in user_lower for word in ["brown", "dr brown", "dr. brown", "4"]):
            preferred_doctor = "brown"
            doctor_name = "Dr. Brown"
        elif any(word in user_lower for word in ["davis", "dr davis", "dr. davis", "5"]):
            preferred_doctor = "davis"
            doctor_name = "Dr. Davis"
        else:
            # If no clear selection, ask again
            return f"📅 **Scheduling Agent**: I didn't catch which doctor you'd prefer. Please choose from:\n\n1. **Dr. Johnson** - Internal Medicine\n2. **Dr. Wilson** - Family Medicine  \n3. **Dr. Smith** - Cardiology\n4. **Dr. Brown** - Orthopedics\n5. **Dr. Davis** - Dermatology\n\n💬 Just type the doctor's name or number (e.g., \"Dr. Johnson\" or \"1\")"
        
        # Use default time preferences
        preferred_time = "morning"
        default_time = "09:00"
        time_display = "9:00 AM"
        duration = self.state.appointment_info.get("duration", 30)
        appointment_type = self.state.appointment_info.get("type", "follow_up")
        
        # Now book with the selected doctor
        return self.book_with_specific_doctor(preferred_doctor, doctor_name, preferred_time, default_time, time_display, duration, appointment_type)
        
    def handle_scheduling_confirmation(self, user_input: str) -> str:
        """Handle scheduling confirmation"""
        user_response = user_input.lower().strip()
        
        if any(word in user_response for word in ["yes", "ok", "good", "fine", "confirm", "sounds good"]):
            self.state.current_step = "insurance"
            # Set up insurance fields
            self.state.pending_fields = self.required_fields["insurance"].copy()
            self.state.current_field = self.state.pending_fields[0]  # Start with carrier
            
            return f"📅 **Scheduling Agent**: Excellent! Your appointment with Dr. Johnson is reserved for September 5th at 9:00 AM.\n\nNow I need to verify your insurance information. {self.field_prompts[self.state.current_field]}"
        else:
            return f"📅 **Scheduling Agent**: No problem! Let me know what time works better for you, or if you'd prefer a different doctor."
    
    def insurance_agent(self, user_input: str) -> str:
        """Insurance Agent - Verifies insurance coverage one field at a time"""
        # Process the current field
        if self.state.current_field == "carrier":
            # Handle different insurance types
            user_lower = user_input.lower()
            
            if any(word in user_lower for word in ["cash", "pay cash", "self pay", "no insurance"]):
                self.state.insurance_info = {
                    "carrier": "Self Pay",
                    "member_id": "CASH",
                    "verified": True,
                    "copay": "Full Payment Due"
                }
                self.state.current_step = "confirmation"
                return f"💳 **Insurance Agent**: Understood! You'll be paying cash for your appointment.\n\n💰 **Payment Information:**\n• Payment Method: Self Pay\n• Amount Due: Will be calculated at visit\n• Payment Options: Cash, Card, Check accepted\n\nLet me finalize your appointment..."
                
            elif any(word in user_lower for word in ["medicaid", "medicare", "government"]):
                carrier = "Medicare/Medicaid"
                copay = "$0-$10"
            elif any(word in user_lower for word in ["blue cross", "bcbs"]):
                carrier = "Blue Cross Blue Shield"
                copay = "$25"
            elif "aetna" in user_lower:
                carrier = "Aetna"
                copay = "$30"
            elif any(word in user_lower for word in ["united", "uhc"]):
                carrier = "United Healthcare"
                copay = "$25"
            elif any(word in user_lower for word in ["work", "employer", "company"]):
                carrier = "Employer Insurance"
                copay = "$20"
            else:
                carrier = user_input.strip().title()
                copay = "$25"
            
            # Store insurance carrier
            self.state.insurance_info["carrier"] = carrier
            self.state.insurance_info["copay"] = copay
            self.state.pending_fields.remove("carrier")
            
        elif self.state.current_field == "member_id":
            user_lower = user_input.lower()
            
            if any(phrase in user_lower for phrase in ["get my card", "find my card", "look for"]):
                return f"💳 **Insurance Agent**: No problem! Take your time to find your insurance card. I'll wait for your member ID when you're ready."
            elif any(phrase in user_lower for phrase in ["don't have", "forgot", "left at home", "without", "missing"]):
                # User doesn't have their member ID - skip this field and proceed
                self.state.insurance_info["member_id"] = "Will verify at appointment"
                self.state.pending_fields.remove("member_id")
                return f"💳 **Insurance Agent**: That's okay! We can verify your insurance at the appointment. I'll note that verification is needed.\n\nFor now, I'll proceed with the appointment booking."
            else:
                # Store member ID
                member_id = user_input.strip()
                if len(member_id) >= 3:  # More flexible validation
                    self.state.insurance_info["member_id"] = member_id
                    self.state.pending_fields.remove("member_id")
                else:
                    return f"💳 **Insurance Agent**: Please provide a valid member ID (at least 3 characters) or let me know if you don't have it with you."
        
        # Check if we have more fields to collect
        if self.state.pending_fields:
            # Move to next field
            self.state.current_field = self.state.pending_fields[0]
            field_prompt = self.field_prompts[self.state.current_field]
            return f"💳 **Insurance Agent**: Thank you! Now, {field_prompt}"
        else:
            # All insurance info collected, verify and move to confirmation
            self.state.insurance_info.update({
                "verified": True
            })
            self.state.current_step = "confirmation"
            
            carrier = self.state.insurance_info.get('carrier', 'Your Insurance')
            member_id = self.state.insurance_info.get('member_id', 'On File')
            copay = self.state.insurance_info.get('copay', '$25')
            
            return f"💳 **Insurance Agent**: Perfect! I have your insurance information:\n\n• Carrier: {carrier}\n• Member ID: {member_id}\n• Estimated Copay: {copay}\n\n✅ Insurance verification will be completed at your appointment.\n\nLet me finalize your appointment..."
    
    def confirmation_agent(self, user_input: str) -> str:
        """Confirmation Agent - Finalizes appointment and sends confirmations"""
        patient_name = self.state.patient_info.get("name", "Patient")
        doctor = self.state.appointment_info.get("doctor", "Dr. Johnson")
        date = self.state.appointment_info.get("date", "September 5, 2025")
        time = self.state.appointment_info.get("time", "9:00")
        duration = self.state.appointment_info.get("duration", 30)
        appointment_type = self.state.appointment_info.get("type", "follow_up")
        time_preference = self.state.appointment_info.get("time_preference", "morning")
        carrier = self.state.insurance_info.get("carrier", "Your Insurance")
        copay = self.state.insurance_info.get("copay", "$25")
        
        # Format time display
        if ":" in str(time):
            hour = int(time.split(":")[0])
            time_display = f"{hour}:00 {'AM' if hour < 12 else 'PM'}" if hour != 12 else "12:00 PM"
        else:
            time_display = f"{time} AM"
        
        # Create appointment type display
        type_display = appointment_type.replace('_', ' ').title()
        if time_preference == "urgent":
            type_display += " (URGENT)"
        
        # Save patient to database if not exists
        patient_data = {
            'name': patient_name,
            'dob': self.state.patient_info.get('dob', '1990-01-01'),
            'doctor': doctor,
            'last_visit': date,
            'phone': self.state.patient_info.get('phone', ''),
            'email': self.state.patient_info.get('email', ''),
            'insurance_carrier': carrier,
            'member_id': self.state.insurance_info.get('member_id', 'Will verify at appointment'),
            'group_id': self.state.insurance_info.get('group_id', '')
        }
        
        # Check if patient exists, if not add them
        existing_patient = self.db_manager.search_patient(patient_name)
        if not existing_patient:
            patient_id = self.db_manager.add_patient(patient_data)
        else:
            patient_id = existing_patient['patient_id']
        
        # Save appointment to database
        appointment_data = {
            'appointment_id': f"APT{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'patient_id': patient_id,
            'patient_name': patient_name,
            'doctor': doctor,
            'date': date,
            'time': time_display,
            'duration': f"{duration} minutes",
            'status': 'Confirmed',
            'insurance_verified': 'Pending' if 'Will verify' in self.state.insurance_info.get('member_id', '') else 'Verified',
            'confirmation_sent': True
        }
        
        # Save to database
        save_success = self.db_manager.add_appointment(appointment_data)
        
        response = f"""✅ **Confirmation Agent**: 🎉 Your appointment is fully booked!

📋 **APPOINTMENT SUMMARY**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👤 **Patient**: {patient_name}
🩺 **Doctor**: {doctor}
📅 **Date**: {date}
🕘 **Time**: {time_display}
⏱️ **Duration**: {duration} minutes
📋 **Type**: {type_display}
🕐 **Preference**: {time_preference.title()} appointments
💳 **Insurance**: {carrier}
💰 **Copay**: {copay}

📧 **Confirmation email** sent to {self.state.patient_info.get('email', 'your email')}!
📱 **SMS reminders** scheduled for {self.state.patient_info.get('phone', 'your phone')}!

**🤖 LangGraph Multi-Agent Workflow Complete!**
All 6 agents successfully orchestrated your appointment booking.

**📝 What to bring:**
• Insurance card (for verification)
• Photo ID
• List of current medications
• Copay payment

**⚠️ Appointment Policy:**
• Please arrive 15 minutes early
• 24-hour cancellation notice required
• Reschedule anytime by calling our office"""

        if save_success:
            response += f"\n\n💾 **Database Status**: ✅ Appointment saved successfully! (ID: {appointment_data['appointment_id']})"
        else:
            response += f"\n\n💾 **Database Status**: ⚠️ Appointment confirmed but database save failed. Please contact support."
        
        self.state.current_step = "complete"
        return response
    
    def process_user_input(self, user_input: str) -> str:
        """
        Process user input through the LangGraph multi-agent workflow
        This simulates the StateGraph orchestration
        """
        # Add user message to state
        self.state.messages.append(MockMessage(user_input, "human"))
        
        # Handle different conversation steps
        if self.state.current_step == "start":
            response = self.greeting_agent(user_input)
            
        elif self.state.current_step == "patient_intake":
            response = self.patient_intake_agent(user_input)
            
        elif self.state.current_step == "emr_lookup":
            # Ensure we have patient info before proceeding
            if not self.state.patient_info.get("name") or not self.state.patient_info.get("phone") or not self.state.patient_info.get("email"):
                # Reset to patient intake if missing info
                self.state.current_step = "patient_intake"
                self.state.pending_fields = self.required_fields["patient_intake"].copy()
                # Remove any fields we already have
                if self.state.patient_info.get("name"):
                    self.state.pending_fields.remove("name")
                if self.state.patient_info.get("phone"):
                    self.state.pending_fields.remove("phone")
                if self.state.patient_info.get("email"):
                    self.state.pending_fields.remove("email")
                
                if self.state.pending_fields:
                    self.state.current_field = self.state.pending_fields[0]
                    return f"📝 **Patient Intake Agent**: I still need some information. {self.field_prompts[self.state.current_field]}"
            
            response = self.emr_lookup_agent(user_input)
            
        elif self.state.current_step == "scheduling":
            response = self.scheduling_agent(user_input)
            
        elif self.state.current_step == "scheduling_doctor_select":
            response = self.handle_doctor_selection(user_input)
            
        elif self.state.current_step == "scheduling_confirm":
            response = self.handle_scheduling_confirmation(user_input)
            
        elif self.state.current_step == "insurance":
            response = self.insurance_agent(user_input)
            
        elif self.state.current_step == "confirmation":
            response = self.confirmation_agent(user_input)
            
        elif self.state.current_step == "cancellation":
            response = self.cancellation_agent(user_input)
            
        elif self.state.current_step == "rescheduling":
            response = self.rescheduling_agent(user_input)
            
        elif self.state.current_step == "complete":
            # Check if user wants to cancel, reschedule, or book a new appointment
            user_input_lower = user_input.lower()
            
            if any(word in user_input_lower for word in ['cancel', 'cancellation', 'cancelled']):
                # Reset state and go to cancellation
                self.reset_state()
                self.state.current_step = "cancellation"
                return """🚫 **Cancellation Agent**: I'll help you cancel your appointment.

To cancel your appointment, I'll need some information:

**Please provide your appointment details:**
1. Your full name
2. Appointment date (e.g., September 5, 2025)
3. Appointment time (e.g., 10:00 AM)
4. Doctor's name

Let's start - what's your full name?"""
            
            elif any(word in user_input_lower for word in ['reschedule', 'rescheduling', 'change', 'move']):
                # Reset state and go to rescheduling
                self.reset_state()
                self.state.current_step = "rescheduling"
                return """🔄 **Rescheduling Agent**: I'll help you reschedule your appointment.

To reschedule your appointment, I'll need some information:

**First, your current appointment details:**
1. Your full name
2. Current appointment date (e.g., September 5, 2025)
3. Current appointment time (e.g., 10:00 AM)
4. Doctor's name

Then I'll help you find a new time that works better for you.

Let's start - what's your full name?"""
            
            else:
                # Reset state for new appointment booking
                self.reset_state()
                response = self.greeting_agent(user_input)
                return response
            
        else:
            # Reset to start if we're in an unknown state
            response = "I'm not sure what step we're on. Let me start over. What's your full name?"
            self.state.current_step = "patient_intake"
            self.state.pending_fields = self.required_fields["patient_intake"].copy()
            self.state.current_field = self.state.pending_fields[0]
        
        # Add agent response to state
        self.state.messages.append(MockMessage(response, "ai"))
        
        return response
    
    def cancellation_agent(self, user_input: str) -> str:
        """Cancellation Agent - Handles appointment cancellation"""
        # Parse appointment details from user input
        user_input_lower = user_input.lower()
        
        # Basic name extraction
        if any(word in user_input_lower for word in ['my name is', 'i am', 'i\'m']) or (not self.state.patient_info.get("name") and not any(word in user_input_lower for word in ['september', 'october', 'november', 'december', 'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec', 'am', 'pm', ':', 'dr.', 'dr ', 'doctor'])):
            name = user_input.strip()
            # Simple extraction - can be enhanced
            if 'my name is' in user_input_lower:
                name = user_input[user_input_lower.find('my name is') + 10:].strip()
            elif 'i am' in user_input_lower:
                name = user_input[user_input_lower.find('i am') + 4:].strip()
            elif 'i\'m' in user_input_lower:
                name = user_input[user_input_lower.find('i\'m') + 3:].strip()
            
            if name:
                self.state.patient_info["name"] = name.title()
                
                # Automatically search for appointments by this name
                appointments_df = self.db_manager.load_appointments()
                
                if not appointments_df.empty:
                    # Search for confirmed appointments with this name
                    mask = (
                        appointments_df['patient_name'].str.contains(name, case=False, na=False) &
                        (appointments_df['status'] == 'Confirmed')
                    )
                    matching_appointments = appointments_df[mask]
                    
                    if len(matching_appointments) == 1:
                        # Exactly one appointment found - auto-populate details
                        appointment = matching_appointments.iloc[0]
                        self.state.appointment_info["date"] = appointment['date']
                        self.state.appointment_info["time"] = appointment['time']
                        self.state.appointment_info["doctor"] = appointment['doctor']
                        
                        # Proceed directly to cancellation
                        return self._process_cancellation_with_details(appointment)
                        
                    elif len(matching_appointments) > 1:
                        # Multiple appointments found - ask for clarification
                        appointments_list = ""
                        for idx, apt in matching_appointments.iterrows():
                            appointments_list += f"• **{apt['date']}** at **{apt['time']}** with **{apt['doctor']}**\n"
                        
                        return f"""✅ Thank you, {name.title()}! 

I found **{len(matching_appointments)} confirmed appointments** for you:

{appointments_list}

Which appointment would you like to cancel? Please specify:
- The **date** (e.g., "September 5, 2025")
- The **doctor's name** (e.g., "Dr. Johnson")
- Or the **time** (e.g., "10:00 AM")"""
                        
                    else:
                        # No appointments found
                        return f"""✅ Thank you, {name.title()}!

❌ I couldn't find any **confirmed appointments** under your name in our system.

This could be because:
• The appointment might already be cancelled
• The name might be spelled differently in our records
• The appointment might be under a different name

Please double-check:
1. **Full name spelling** (as it appears in your confirmation email)
2. **Appointment status** (check if it's already cancelled)

You can also provide your **appointment details manually**:
- Appointment date (e.g., September 5, 2025)
- Doctor's name (e.g., Dr. Johnson)"""
                        
                else:
                    return f"""✅ Thank you, {name.title()}!

❌ No appointments found in the system. Please verify your information or contact our office directly."""

        # Look for date information to narrow down multiple appointments
        elif any(word in user_input_lower for word in ['september', 'october', 'november', 'december', 'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']) and self.state.patient_info.get("name"):
            self.state.appointment_info["date"] = user_input.strip()
            
            # Try to find specific appointment with name and date
            name = self.state.patient_info["name"]
            appointments_df = self.db_manager.load_appointments()
            
            if not appointments_df.empty:
                mask = (
                    appointments_df['patient_name'].str.contains(name, case=False, na=False) &
                    appointments_df['date'].str.contains(user_input.strip(), case=False, na=False) &
                    (appointments_df['status'] == 'Confirmed')
                )
                matching_appointments = appointments_df[mask]
                
                if len(matching_appointments) == 1:
                    appointment = matching_appointments.iloc[0]
                    self.state.appointment_info["time"] = appointment['time']
                    self.state.appointment_info["doctor"] = appointment['doctor']
                    return self._process_cancellation_with_details(appointment)
                elif len(matching_appointments) > 1:
                    appointments_list = ""
                    for idx, apt in matching_appointments.iterrows():
                        appointments_list += f"• **{apt['time']}** with **{apt['doctor']}**\n"
                    
                    return f"""✅ Got it! Date: {user_input.strip()}

I found **{len(matching_appointments)} appointments** on this date:

{appointments_list}

Please specify the **time** or **doctor** to identify which appointment to cancel."""
                else:
                    return f"""❌ No confirmed appointments found for {name} on {user_input.strip()}. 

Please double-check the date or provide the doctor's name."""
            
            return f"""✅ Got it! Appointment date: {user_input.strip()}

Now please provide the **doctor's name** or **appointment time**."""

        # Look for time information
        elif any(word in user_input_lower for word in ['am', 'pm', ':']) or any(char.isdigit() for char in user_input):
            self.state.appointment_info["time"] = user_input.strip()
            
            # Try to find appointment with available info
            if self.state.patient_info.get("name"):
                return self._try_find_and_cancel_appointment()
            
            return f"""✅ Appointment time: {user_input.strip()}

Please provide the **doctor's name** to complete the cancellation."""

        # Look for doctor information
        elif any(word in user_input_lower for word in ['dr.', 'dr ', 'doctor', 'johnson', 'wilson', 'smith', 'brown', 'davis']):
            self.state.appointment_info["doctor"] = user_input.strip()
            
            # Try to find and cancel appointment
            if self.state.patient_info.get("name"):
                return self._try_find_and_cancel_appointment()
            
            return f"""✅ Doctor: {user_input.strip()}

Please provide your **full name** to locate the appointment."""
        
        else:
            return """❓ I need your appointment information to proceed with cancellation.

Please provide one of the following:
1. Your full name
2. Appointment date 
3. Appointment time
4. Doctor's name

You can say something like: "My name is John Smith" or "September 5th at 2 PM" """
    
    def _process_cancellation_with_details(self, appointment_row):
        """Helper method to process cancellation with appointment details"""
        appointment_id = appointment_row['appointment_id']
        success = self.db_manager.update_appointment_status(appointment_id, 'Cancelled')
        
        self.state.current_step = "complete"
        
        if success:
            cancellation_status = f"✅ **Database Status**: Appointment successfully cancelled (ID: {appointment_id})"
        else:
            cancellation_status = "⚠️ **Database Status**: Cancellation failed. Please contact support."
        
        return f"""✅ **Cancellation Confirmed!**

**Appointment Details Cancelled:**
👤 **Patient:** {appointment_row['patient_name']}
👨‍⚕️ **Doctor:** {appointment_row['doctor']}
📅 **Date:** {appointment_row['date']}
🕐 **Time:** {appointment_row['time']}

📧 **Confirmation email will be sent shortly.**

**Important Notes:**
• Your appointment has been successfully cancelled
• You will receive a cancellation confirmation email
• No cancellation fee applies (24+ hours notice provided)
• To schedule a new appointment, please use the 'Reset Chat' button

{cancellation_status}

Is there anything else I can help you with today?"""
    
    def _try_find_and_cancel_appointment(self):
        """Helper method to find and cancel appointment with available information"""
        patient_name = self.state.patient_info.get("name", "")
        appointment_date = self.state.appointment_info.get("date", "")
        appointment_time = self.state.appointment_info.get("time", "")
        doctor = self.state.appointment_info.get("doctor", "")
        
        appointments_df = self.db_manager.load_appointments()
        
        if not appointments_df.empty:
            # Build search mask
            mask = (appointments_df['status'] == 'Confirmed')
            
            if patient_name:
                mask = mask & appointments_df['patient_name'].str.contains(patient_name, case=False, na=False)
            if doctor:
                mask = mask & appointments_df['doctor'].str.contains(doctor, case=False, na=False)
            if appointment_date:
                mask = mask & appointments_df['date'].str.contains(appointment_date, case=False, na=False)
            if appointment_time:
                mask = mask & appointments_df['time'].str.contains(appointment_time, case=False, na=False)
            
            matching_appointments = appointments_df[mask]
            
            if len(matching_appointments) == 1:
                appointment = matching_appointments.iloc[0]
                # Fill in any missing details
                self.state.appointment_info["date"] = appointment['date']
                self.state.appointment_info["time"] = appointment['time']
                self.state.appointment_info["doctor"] = appointment['doctor']
                return self._process_cancellation_with_details(appointment)
            elif len(matching_appointments) > 1:
                # Multiple matches - need more info
                appointments_list = ""
                for idx, apt in matching_appointments.iterrows():
                    appointments_list += f"• **{apt['date']}** at **{apt['time']}** with **{apt['doctor']}**\n"
                
                return f"""I found **{len(matching_appointments)} appointments** matching your criteria:

{appointments_list}

Please provide more specific details to identify which appointment to cancel."""
            else:
                return """❌ No matching confirmed appointments found. Please verify your details:
• Patient name
• Appointment date
• Doctor name
• Appointment time"""
        
        return "❌ No appointments found in database."
    
    def rescheduling_agent(self, user_input: str) -> str:
        """Rescheduling Agent - Handles appointment rescheduling"""
        user_input_lower = user_input.lower()
        
        # Basic name extraction
        if any(word in user_input_lower for word in ['my name is', 'i am', 'i\'m']):
            name = user_input.strip()
            if 'my name is' in user_input_lower:
                name = user_input[user_input_lower.find('my name is') + 10:].strip()
            elif 'i am' in user_input_lower:
                name = user_input[user_input_lower.find('i am') + 4:].strip()
            elif 'i\'m' in user_input_lower:
                name = user_input[user_input_lower.find('i\'m') + 3:].strip()
            
            if name:
                self.state.patient_info["name"] = name.title()
                return f"""✅ Thank you, {name.title()}!

Now I need your **current** appointment details. Please provide:
📅 **Current appointment date** (e.g., September 5, 2025)"""
        
        # Look for date information
        elif any(word in user_input_lower for word in ['september', 'october', 'november', 'december', 'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']):
            self.state.appointment_info["current_date"] = user_input.strip()
            return f"""✅ Current appointment date: {user_input.strip()}

What time is your current appointment? (e.g., 10:00 AM, 2:30 PM)"""
        
        # Look for time information
        elif any(word in user_input_lower for word in ['am', 'pm', ':']) or any(char.isdigit() for char in user_input):
            self.state.appointment_info["current_time"] = user_input.strip()
            return f"""✅ Current appointment time: {user_input.strip()}

Which doctor is your current appointment with?
Available doctors:
• Dr. Johnson (Internal Medicine)
• Dr. Wilson (Family Medicine)
• Dr. Smith (Cardiology) 
• Dr. Brown (Orthopedics)
• Dr. Davis (Dermatology)"""
        
        # Look for doctor information
        elif any(word in user_input_lower for word in ['dr.', 'dr ', 'doctor', 'johnson', 'wilson', 'smith', 'brown', 'davis']):
            self.state.appointment_info["current_doctor"] = user_input.strip()
            
            # Now ask for new preferred times
            return f"""✅ Current doctor: {user_input.strip()}

Perfect! Now let's find a new time that works better for you.

**Preferred new appointment times:**
What days and times work best for you? 

For example:
• "Next Tuesday morning"
• "September 10th afternoon" 
• "Any day next week between 2-4 PM"
• "Flexible with timing"

What would you prefer?"""
        
        # Handle new time preferences
        elif 'flexible' in user_input_lower or 'any' in user_input_lower:
            # Generate some available options
            self.state.current_step = "complete"
            patient_name = self.state.patient_info.get("name", "Patient")
            current_date = self.state.appointment_info.get("current_date", "")
            current_time = self.state.appointment_info.get("current_time", "") 
            current_doctor = self.state.appointment_info.get("current_doctor", "")
            
            return f"""✅ **Rescheduling Confirmed!**

**Original Appointment (Cancelled):**
👤 **Patient:** {patient_name}
👨‍⚕️ **Doctor:** {current_doctor}
📅 **Date:** {current_date}
🕐 **Time:** {current_time}

**New Appointment Options:**
📅 **September 6, 2025 at 10:00 AM** with {current_doctor}
📅 **September 7, 2025 at 2:00 PM** with {current_doctor}
📅 **September 9, 2025 at 9:00 AM** with {current_doctor}

🎯 **I've tentatively scheduled you for September 6th at 10:00 AM.**

📧 **Confirmation details:**
• Original appointment cancelled
• New appointment confirmed
• Email confirmation will be sent
• Calendar invite included

Is this new time acceptable, or would you prefer one of the other options?"""
        
        else:
            return """❓ I need more information to reschedule your appointment.

Please provide:
1. Your full name
2. Current appointment date
3. Current appointment time  
4. Current doctor
5. Preferred new times

You can say: "My name is John Smith" or "September 5th at 2 PM" or "Next week works better" """
    
    def get_conversation_state(self) -> Dict[str, Any]:
        """Get current conversation state for UI display"""
        # Calculate progress based on current step
        step_progress = {
            "start": 0,
            "patient_intake": 20,
            "emr_lookup": 35,
            "scheduling": 50,
            "scheduling_confirm": 60,
            "insurance": 75,
            "confirmation": 90,
            "cancellation": 50,  # Cancellation workflow
            "rescheduling": 75,  # Rescheduling workflow 
            "complete": 100
        }
        
        progress = step_progress.get(self.state.current_step, 0)
        
        return {
            "step": self.state.current_step,
            "patient_info": self.state.patient_info,
            "appointment_info": self.state.appointment_info,
            "insurance_info": self.state.insurance_info,
            "progress": progress,
            "current_agent": self.state.current_step,
            "current_field": self.state.current_field,
            "pending_fields": self.state.pending_fields
        }
    
    def get_appointment_summary(self) -> Optional[Dict[str, Any]]:
        """Get complete appointment summary if booking is complete"""
        if self.state.current_step != "complete":
            return None
        
        return {
            "appointment_id": self.state.appointment_info.get("appointment_id"),
            "patient_name": self.state.patient_info.get("name", "Patient"),
            "doctor": self.state.appointment_info.get("doctor"),
            "date": self.state.appointment_info.get("date"),
            "time": self.state.appointment_info.get("time"),
            "duration": self.state.appointment_info.get("duration"),
            "type": self.state.appointment_info.get("type"),
            "insurance_carrier": self.state.insurance_info.get("carrier"),
            "copay": self.state.insurance_info.get("copay")
        }
    
    def reset_conversation(self):
        """Reset the conversation state"""
        self.current_agent_index = 0
        self.state = MockAppointmentState()

# Create global instance
simple_langgraph_agent = SimpleLangGraphAgent()
