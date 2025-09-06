"""
LangGraph Multi-Agent Medical Scheduling System
Implements multi-agent orchestration with patient intake, scheduling, and confirmation agents.
"""

from typing import Dict, List, Optional, TypedDict, Annotated
from langgraph.graph import StateGraph, END  # type: ignore
from langgraph.prebuilt import ToolNode  # type: ignore
from langchain_ollama import OllamaLLM  # type: ignore
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage  # type: ignore
from langchain_core.prompts import ChatPromptTemplate  # type: ignore
import os
from dotenv import load_dotenv  # type: ignore

# Import our custom tools
from .langchain_tools import (
    lookup_patient_in_emr,
    get_comprehensive_patient_info,
    search_patients_by_criteria,
    get_doctor_availability,
    book_appointment,
    send_appointment_confirmation,
    validate_patient_information,
    get_insurance_verification_status
)

load_dotenv()

# Define the state structure for our multi-agent system
class AppointmentState(TypedDict):
    messages: Annotated[List, "The conversation messages"]
    current_step: str
    patient_info: Dict
    appointment_info: Dict
    insurance_info: Dict
    validation_errors: List[str]
    conversation_history: List[str]
    next_agent: Optional[str]

class MedicalSchedulingGraph:
    def __init__(self):
        """Initialize the LangGraph multi-agent system"""
        # Initialize Ollama LLM (free local model)
        self.llm = OllamaLLM(
            model="llama3.2:3b",  # Free lightweight model
            base_url="http://localhost:11434",  # Default Ollama server
            temperature=0.1
        )
        
        # Tools available to agents
        self.tools = [
            lookup_patient_in_emr,
            get_comprehensive_patient_info,
            search_patients_by_criteria,
            get_doctor_availability,
            book_appointment,
            send_appointment_confirmation,
            validate_patient_information,
            get_insurance_verification_status
        ]
        
        # Create the state graph
        self.graph = self._create_graph()
    
    def _create_graph(self):
        """Create and configure the LangGraph workflow"""
        workflow = StateGraph(AppointmentState)
        
        # Add agent nodes
        workflow.add_node("greeting_agent", self.greeting_agent)
        workflow.add_node("patient_intake_agent", self.patient_intake_agent)
        workflow.add_node("emr_lookup_agent", self.emr_lookup_agent)
        workflow.add_node("scheduling_agent", self.scheduling_agent)
        workflow.add_node("insurance_agent", self.insurance_agent)
        workflow.add_node("confirmation_agent", self.confirmation_agent)
        workflow.add_node("tools", ToolNode(self.tools))
        
        # Define the workflow edges
        workflow.set_entry_point("greeting_agent")
        
        # Greeting agent routes to patient intake
        workflow.add_edge("greeting_agent", "patient_intake_agent")
        
        # Patient intake routes to EMR lookup
        workflow.add_edge("patient_intake_agent", "emr_lookup_agent")
        
        # EMR lookup routes to scheduling
        workflow.add_edge("emr_lookup_agent", "scheduling_agent")
        
        # Scheduling routes to insurance
        workflow.add_edge("scheduling_agent", "insurance_agent")
        
        # Insurance routes to confirmation
        workflow.add_edge("insurance_agent", "confirmation_agent")
        
        # Confirmation can end or loop back based on validation
        workflow.add_conditional_edges(
            "confirmation_agent",
            self.should_continue,
            {
                "continue": "patient_intake_agent",
                "end": END
            }
        )
        
        # Tools node can route back to any agent based on context
        workflow.add_conditional_edges(
            "tools",
            self.route_after_tools,
            {
                "patient_intake_agent": "patient_intake_agent",
                "emr_lookup_agent": "emr_lookup_agent", 
                "scheduling_agent": "scheduling_agent",
                "insurance_agent": "insurance_agent",
                "confirmation_agent": "confirmation_agent",
                "end": END
            }
        )
        
        compiled_workflow = workflow.compile()
        return compiled_workflow
    
    def greeting_agent(self, state: AppointmentState) -> AppointmentState:
        """Handle initial patient greeting and introduction"""
        system_prompt = """You are a friendly medical receptionist AI assistant. 
        Your role is to:
        1. Greet the patient warmly
        2. Explain that you'll help them schedule an appointment
        3. Ask for their basic information to get started
        4. Set a welcoming, professional tone
        
        Keep your response concise and friendly. Do not ask for detailed information yet."""
        
        messages = state["messages"] if state["messages"] else []
        
        if not messages or len(messages) == 0:
            # Initial greeting
            greeting = """Hello! Welcome to our medical practice. I'm your AI scheduling assistant, and I'm here to help you book an appointment today. 

I'll guide you through a quick process to:
- Gather your basic information
- Check our system for your records
- Find the best available appointment time
- Collect insurance information
- Send you a confirmation

To get started, could you please tell me your full name and date of birth?"""
            
            messages.append(AIMessage(content=greeting))
        else:
            # Process patient's response
            prompt = ChatPromptTemplate.from_messages([
                SystemMessage(content=system_prompt),
                *messages
            ])
            
            response = self.llm.invoke(prompt.format_messages())
            messages.append(response)
        
        # Update state
        state["messages"] = messages
        state["current_step"] = "greeting_complete"
        state["conversation_history"] = state.get("conversation_history", []) + [
            "Greeting phase completed"
        ]
        
        return state
    
    def patient_intake_agent(self, state: AppointmentState) -> AppointmentState:
        """Collect and validate patient information"""
        system_prompt = """You are a patient intake specialist. Your role is to:
        1. Collect complete patient information: full name, date of birth, phone, email
        2. Validate the information format using the validate_patient_information tool
        3. Ask follow-up questions if information is missing or invalid
        4. Be thorough but patient-friendly
        
        Required information:
        - Full name (first and last)
        - Date of birth (YYYY-MM-DD format)
        - Phone number (10 digits)
        - Email address
        
        Use the validate_patient_information tool to check the data before proceeding."""
        
        messages = state["messages"]
        
        # Extract any patient info from conversation
        last_message = messages[-1].content if messages else ""
        
        # Check if we have enough information
        patient_info = state.get("patient_info", {})
        required_fields = ["name", "date_of_birth", "phone", "email"]
        missing_fields = [field for field in required_fields if not patient_info.get(field)]
        
        if missing_fields:
            # Ask for missing information
            prompt = ChatPromptTemplate.from_messages([
                SystemMessage(content=system_prompt),
                *messages
            ])
            
            response = self.llm.invoke(prompt.format_messages())
            messages.append(response)
            
            # Try to extract information from the response
            # This is simplified - in practice, you'd use more sophisticated parsing
            if "name" in missing_fields and any(word in last_message.lower() for word in ["name", "i'm", "i am"]):
                # Extract name logic here
                pass
        else:
            # Validate collected information
            validation = validate_patient_information.invoke({  # type: ignore
                "name": patient_info.get("name"),
                "phone": patient_info.get("phone"),
                "email": patient_info.get("email"),
                "date_of_birth": patient_info.get("date_of_birth")
            })
            
            if validation["valid"]:
                # Apply corrections
                patient_info.update(validation.get("corrections", {}))
                state["patient_info"] = patient_info
                
                confirmation = f"""Perfect! I have your information:
- Name: {patient_info['name']}
- Date of Birth: {patient_info['date_of_birth']}
- Phone: {patient_info['phone']}
- Email: {patient_info['email']}

Now let me check our system to see if you're an existing patient."""
                
                messages.append(AIMessage(content=confirmation))
                state["current_step"] = "patient_info_collected"
            else:
                # Handle validation errors
                error_msg = "I notice some issues with the information provided:\n"
                error_msg += "\n".join(f"- {error}" for error in validation["errors"])
                error_msg += "\n\nCould you please provide the correct information?"
                
                messages.append(AIMessage(content=error_msg))
                state["validation_errors"] = validation["errors"]
        
        state["messages"] = messages
        return state
    
    def emr_lookup_agent(self, state: AppointmentState) -> AppointmentState:
        """Look up patient in EMR system and classify as new/returning"""
        system_prompt = """You are an EMR lookup specialist. Your role is to:
        1. Search the Electronic Medical Records for the patient
        2. Classify them as new or returning patient
        3. Provide appropriate messaging based on their status
        4. Set appropriate appointment duration (60min new, 30min returning)
        
        Use the lookup_patient_in_emr tool with the patient's name and date of birth."""
        
        patient_info = state.get("patient_info", {})
        messages = state.get("messages", [])
        
        if patient_info.get("name") and patient_info.get("date_of_birth"):
            # Perform EMR lookup
            lookup_result = lookup_patient_in_emr.invoke({  # type: ignore
                "name": patient_info["name"],
                "date_of_birth": patient_info["date_of_birth"]
            })
            
            if lookup_result.get("found"):
                # Returning patient
                patient_info.update(lookup_result)
                welcome_msg = f"""Great news! I found your records in our system. Welcome back, {patient_info['name']}!

I can see you're a returning patient with Dr. {lookup_result.get('doctor', 'N/A')}. Your last visit was {lookup_result.get('last_visit', 'not specified')}.

I'll schedule a 30-minute follow-up appointment for you. Let me check available time slots."""
                
                state["appointment_info"] = {
                    "duration": 30,
                    "type": "follow_up",
                    "preferred_doctor": lookup_result.get('doctor')
                }
            else:
                # New patient
                welcome_msg = f"""Welcome to our practice, {patient_info['name']}! I don't see any previous records for you, so you'll be scheduled as a new patient.

New patient appointments are 60 minutes to allow time for a comprehensive evaluation. Let me find available appointment slots for you."""
                
                state["appointment_info"] = {
                    "duration": 60,
                    "type": "new_patient"
                }
            
            messages.append(AIMessage(content=welcome_msg))
            state["patient_info"] = patient_info
            state["current_step"] = "emr_lookup_complete"
        
        state["messages"] = messages
        return state
    
    def scheduling_agent(self, state: AppointmentState) -> AppointmentState:
        """Handle appointment scheduling and availability checking"""
        system_prompt = """You are a scheduling specialist. Your role is to:
        1. Get available appointment slots using get_doctor_availability tool
        2. Present options to the patient
        3. Book the appointment when patient confirms
        4. Handle scheduling conflicts and alternatives
        
        Consider:
        - Patient preferences for doctor/date
        - Appointment duration from previous agent
        - Available time slots
        
        Use get_doctor_availability and book_appointment tools as needed."""
        
        messages = state["messages"]
        appointment_info = state.get("appointment_info", {})
        patient_info = state.get("patient_info", {})
        
        # Check if appointment is already booked
        if appointment_info.get("appointment_id"):
            state["current_step"] = "appointment_booked"
            return state
        
        # Get available slots
        preferred_doctor = appointment_info.get("preferred_doctor")
        availability = get_doctor_availability.invoke({  # type: ignore
            "doctor_name": preferred_doctor,
            "preferred_date": None  # Could be extracted from conversation
        })
        
        if availability and not availability[0].get("error"):
            # Present options
            options_msg = "Here are the available appointment slots:\n\n"
            for i, slot in enumerate(availability[:5], 1):
                options_msg += f"{i}. Dr. {slot['doctor']} - {slot['specialty']}\n"
                options_msg += f"   Date: {slot['date']}, Time: {slot['time']}\n"
                options_msg += f"   Duration: {slot['duration_minutes']} minutes\n\n"
            
            options_msg += "Please let me know which option works best for you, or if you'd like to see different dates."
            
            messages.append(AIMessage(content=options_msg))
            state["appointment_info"]["available_slots"] = availability[:5]
        else:
            # No availability
            no_slots_msg = "I apologize, but I don't see any available slots at the moment. This could be due to:\n"
            no_slots_msg += "- High demand for appointments\n"
            no_slots_msg += "- System maintenance\n\n"
            no_slots_msg += "Would you like me to:\n"
            no_slots_msg += "1. Check for availability with a different doctor\n"
            no_slots_msg += "2. Look at dates further out\n"
            no_slots_msg += "3. Have our scheduling team contact you directly"
            
            messages.append(AIMessage(content=no_slots_msg))
        
        state["messages"] = messages
        state["current_step"] = "scheduling_in_progress"
        return state
    
    def insurance_agent(self, state: AppointmentState) -> AppointmentState:
        """Collect and verify insurance information"""
        system_prompt = """You are an insurance verification specialist. Your role is to:
        1. Collect patient insurance information
        2. Verify coverage using get_insurance_verification_status tool
        3. Inform patient about copays and coverage details
        4. Handle insurance-related questions
        
        Required information:
        - Insurance carrier name
        - Member ID
        - Group ID (optional)
        
        Use the get_insurance_verification_status tool to verify coverage."""
        
        messages = state["messages"]
        insurance_info = state.get("insurance_info", {})
        
        if not insurance_info.get("carrier") or not insurance_info.get("member_id"):
            # Ask for insurance information
            insurance_prompt = """Now I need to collect your insurance information for billing purposes.

Please provide:
1. Your insurance carrier (e.g., Blue Cross Blue Shield, Aetna, etc.)
2. Your member ID (found on your insurance card)
3. Group ID (if applicable - also on your insurance card)

This helps us verify your coverage and determine any copays."""
            
            messages.append(AIMessage(content=insurance_prompt))
        else:
            # Verify insurance
            verification = get_insurance_verification_status.invoke({  # type: ignore
                "insurance_carrier": insurance_info["carrier"],
                "member_id": insurance_info["member_id"],
                "group_id": insurance_info.get("group_id")
            })
            
            if verification.get("verified"):
                verify_msg = f"""Excellent! Your insurance has been verified:

- Carrier: {verification['carrier']}
- Coverage: {verification['coverage_type']}
- Copay: {verification['copay']}
- Remaining Deductible: {verification['deductible_remaining']}

Your insurance is active and covers this appointment."""
            else:
                verify_msg = f"""I'm having trouble verifying your insurance automatically. 

Status: {verification.get('status', 'Unknown')}
Message: {verification.get('message', 'Verification needed')}

Don't worry - you can still keep your appointment. Our billing team will contact you before your visit to resolve any insurance questions."""
            
            messages.append(AIMessage(content=verify_msg))
            state["insurance_info"] = verification
            state["current_step"] = "insurance_complete"
        
        state["messages"] = messages
        return state
    
    def confirmation_agent(self, state: AppointmentState) -> AppointmentState:
        """Provide final confirmation and send appointment details"""
        system_prompt = """You are a confirmation specialist. Your role is to:
        1. Provide complete appointment summary
        2. Send confirmation email using send_appointment_confirmation tool
        3. Give final instructions and next steps
        4. Ensure patient satisfaction
        
        Create a comprehensive summary and use send_appointment_confirmation to email details."""
        
        messages = state["messages"]
        patient_info = state.get("patient_info", {})
        appointment_info = state.get("appointment_info", {})
        insurance_info = state.get("insurance_info", {})
        
        # Create appointment summary
        if appointment_info.get("appointment_id"):
            summary = f"""🎉 Your appointment is confirmed! Here's your complete summary:

**Appointment Details:**
- Appointment ID: {appointment_info['appointment_id']}
- Patient: {patient_info.get('name', 'N/A')}
- Doctor: Dr. {appointment_info.get('doctor', 'N/A')}
- Date: {appointment_info.get('date', 'N/A')}
- Time: {appointment_info.get('time', 'N/A')}
- Duration: {appointment_info.get('duration_minutes', 30)} minutes
- Type: {appointment_info.get('type', 'N/A')}

**Insurance Information:**
- Carrier: {insurance_info.get('carrier', 'To be verified')}
- Copay: {insurance_info.get('copay', 'To be determined')}

**Important Reminders:**
- Please arrive 15 minutes early for check-in
- Bring a valid ID and insurance card
- Bring a list of current medications
- Contact us 24 hours in advance if you need to reschedule

I'm sending a confirmation email to {patient_info.get('email', 'your email')} with all these details."""
            
            # Send confirmation email
            if patient_info.get("email"):
                email_result = send_appointment_confirmation.invoke({  # type: ignore
                    "patient_email": patient_info["email"],
                    "appointment_details": appointment_info
                })
                
                if email_result.get("success"):
                    summary += f"\n\n✅ Confirmation email sent successfully to {patient_info['email']}!"
                else:
                    summary += f"\n\n⚠️ Note: There was an issue sending the email confirmation. Please save this information."
            
            summary += "\n\nIs there anything else I can help you with regarding your appointment?"
            
            messages.append(AIMessage(content=summary))
            state["current_step"] = "complete"
        
        state["messages"] = messages
        return state
    
    def should_continue(self, state: AppointmentState) -> str:
        """Determine if workflow should continue or end"""
        if state.get("current_step") == "complete":
            return "end"
        elif state.get("validation_errors"):
            return "continue"
        else:
            return "end"
    
    def route_after_tools(self, state: AppointmentState) -> str:
        """Route to appropriate agent after tool execution"""
        next_agent = state.get("next_agent")
        if next_agent:
            return next_agent
        
        current_step = state.get("current_step", "")
        
        if "patient_info" in current_step:
            return "emr_lookup_agent"
        elif "emr" in current_step:
            return "scheduling_agent"
        elif "scheduling" in current_step:
            return "insurance_agent"
        elif "insurance" in current_step:
            return "confirmation_agent"
        else:
            return "end"
    
    def process_message(self, user_input: str, current_state: Optional[AppointmentState] = None) -> AppointmentState:
        """Process a user message through the multi-agent workflow"""
        if current_state is None:
            current_state = {
                "messages": [HumanMessage(content=user_input)],
                "current_step": "start",
                "patient_info": {},
                "appointment_info": {},
                "insurance_info": {},
                "validation_errors": [],
                "conversation_history": [],
                "next_agent": None
            }
        else:
            current_state["messages"].append(HumanMessage(content=user_input))
        
        # Run the workflow
        try:
            result = self.graph.invoke(current_state)  # type: ignore
            return result  # type: ignore
        except Exception as e:
            # Fallback response if graph execution fails
            return {  # type: ignore
                "messages": current_state.get("messages", []) + [AIMessage(content=f"I apologize, but I encountered an issue processing your request. Please try again. Error: {str(e)}")],
                "current_agent": "greeting_agent",
                "patient_info": current_state.get("patient_info", {}),
                "appointment_details": current_state.get("appointment_details", {}),
                "workflow_complete": False,
                "conversation_history": current_state.get("conversation_history", []),
                "next_agent": "greeting_agent"
            }

# Create global instance
medical_scheduling_graph = MedicalSchedulingGraph()
