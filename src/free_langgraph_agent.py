"""
Free LangGraph Multi-Agent Medical Scheduling System
Uses mock LLM responses to demonstrate LangGraph + LangChain architecture without API costs.
"""

from typing import Dict, List, Optional, TypedDict, Annotated
from langgraph.graph import StateGraph, END  # type: ignore
from langgraph.prebuilt import ToolNode  # type: ignore
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage  # type: ignore
from langchain_core.prompts import ChatPromptTemplate  # type: ignore
from langchain_core.language_models.base import BaseLanguageModel  # type: ignore
from langchain_core.callbacks import CallbackManagerForLLMRun  # type: ignore
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

class MockLLM(BaseLanguageModel):  # type: ignore
    """
    Mock LLM for demonstration purposes - completely free!
    Provides realistic responses for the medical scheduling workflow.
    """
    
    class Config:
        arbitrary_types_allowed = True
        extra = "allow"
    
    @property
    def _llm_type(self) -> str:
        return "mock"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Set responses after initialization to avoid Pydantic restrictions
        object.__setattr__(self, 'agent_responses', {
            "greeting": [
                "Hello! Welcome to our medical practice. I'm your AI scheduling assistant, and I'm here to help you book an appointment today.\n\nI'll guide you through a quick process to:\n- Gather your basic information\n- Check our system for your records\n- Find the best available appointment time\n- Collect insurance information\n- Send you a confirmation\n\nTo get started, could you please tell me your full name and date of birth?",
                "Hi there! I'm here to help you schedule a medical appointment. Let's begin by collecting some basic information. What's your full name?",
                "Welcome! I'm your scheduling assistant. To help you book an appointment, I'll need some information. Can you please provide your full name and date of birth?"
            ],
            "patient_intake": [
                "Thank you for providing that information. I need to collect a few more details:\n\nCould you please provide:\n1. Your phone number\n2. Your email address\n\nThis will help us contact you about your appointment.",
                "Perfect! Now I need your contact information. Please provide your phone number and email address so we can send you appointment confirmations.",
                "Great! To complete your information, I'll need your phone number and email address for our records."
            ],
            "emr_lookup_new": [
                "Welcome to our practice! I don't see any previous records for you, so you'll be scheduled as a new patient.\n\nNew patient appointments are 60 minutes to allow time for a comprehensive evaluation. Let me find available appointment slots for you.",
                "I see you're a new patient - welcome! I've allocated 60 minutes for your initial consultation to ensure we have adequate time for your evaluation."
            ],
            "emr_lookup_returning": [
                "Great news! I found your records in our system. Welcome back!\n\nI can see you're a returning patient. I'll schedule a 30-minute follow-up appointment for you. Let me check available time slots.",
                "Welcome back! I found your previous visit records. I'll set up a 30-minute follow-up appointment for you."
            ],
            "scheduling": [
                "Here are the available appointment slots:\n\n1. Dr. Johnson - General Medicine\n   Date: 2025-09-05, Time: 09:00\n   Duration: 30 minutes\n\n2. Dr. Wilson - Internal Medicine\n   Date: 2025-09-05, Time: 10:30\n   Duration: 30 minutes\n\n3. Dr. Smith - Family Medicine\n   Date: 2025-09-06, Time: 14:00\n   Duration: 30 minutes\n\nPlease let me know which option works best for you, or if you'd like to see different dates.",
                "I found several available slots for you. Would you prefer a morning appointment (9 AM - 12 PM) or an afternoon appointment (2 PM - 5 PM)?",
                "Let me show you the available times. I have openings with Dr. Johnson tomorrow morning at 9:00 AM, or Dr. Wilson in the afternoon at 2:00 PM. Which would you prefer?"
            ],
            "insurance": [
                "Excellent! I've reserved your appointment. Now I need to collect your insurance information for billing purposes.\n\nPlease provide:\n1. Your insurance carrier (e.g., Blue Cross Blue Shield, Aetna, etc.)\n2. Your member ID (found on your insurance card)\n3. Group ID (if applicable)",
                "Perfect! Your appointment is reserved. Now for insurance verification, I need your insurance carrier name and member ID number.",
                "Great choice! I've blocked that time for you. To complete the booking, please provide your insurance information."
            ],
            "confirmation": [
                "🎉 Your appointment is confirmed! Here's your complete summary:\n\n**Appointment Details:**\n- Patient: [Patient Name]\n- Doctor: Dr. Johnson\n- Date: 2025-09-05\n- Time: 09:00\n- Duration: 30 minutes\n- Type: Follow-up\n\n**Important Reminders:**\n- Please arrive 15 minutes early for check-in\n- Bring a valid ID and insurance card\n- Contact us 24 hours in advance if you need to reschedule\n\nI'm sending a confirmation email with all these details.",
                "✅ APPOINTMENT CONFIRMED!\n\nYour appointment is all set! You'll receive a confirmation email shortly with all the details and important reminders.",
                "Perfect! Your appointment is booked and confirmed. A confirmation email is being sent to you now with all the details."
            ]
        })
        object.__setattr__(self, 'response_index', 0)
    
    def _call(self, prompt: str, stop: Optional[List[str]] = None, 
              run_manager: Optional[CallbackManagerForLLMRun] = None) -> str:
        """Generate mock responses based on the current conversation context"""
        
        # Analyze prompt to determine appropriate response type
        prompt_lower = prompt.lower()
        
        if "greeting" in prompt_lower or "welcome" in prompt_lower:
            response_type = "greeting"
        elif "patient intake" in prompt_lower or "collect" in prompt_lower:
            response_type = "patient_intake"
        elif "new patient" in prompt_lower:
            response_type = "emr_lookup_new"
        elif "returning patient" in prompt_lower:
            response_type = "emr_lookup_returning"
        elif "scheduling" in prompt_lower or "appointment" in prompt_lower:
            response_type = "scheduling"
        elif "insurance" in prompt_lower:
            response_type = "insurance"
        elif "confirmation" in prompt_lower:
            response_type = "confirmation"
        else:
            response_type = "greeting"  # Default
        
        # Get appropriate response
        agent_responses = object.__getattribute__(self, 'agent_responses')
        response_index = object.__getattribute__(self, 'response_index')
        
        responses = agent_responses.get(response_type, agent_responses["greeting"])
        response = responses[response_index % len(responses)]
        
        # Update response index
        object.__setattr__(self, 'response_index', response_index + 1)
        
        return response
    
    async def _acall(self, prompt: str, stop: Optional[List[str]] = None, 
                     run_manager: Optional[CallbackManagerForLLMRun] = None) -> str:
        """Async version of _call"""
        return self._call(prompt, stop, run_manager)
    
    def _generate(self, prompts, stop=None, run_manager=None, **kwargs):
        """Generate responses for multiple prompts"""
        from langchain_core.outputs import LLMResult, Generation  # type: ignore
        generations = []
        for prompt in prompts:
            response = self._call(prompt, stop, run_manager)
            generations.append([Generation(text=response)])
        return LLMResult(generations=generations)
    
    async def _agenerate(self, prompts, stop=None, run_manager=None, **kwargs):
        """Async version of _generate"""
        return self._generate(prompts, stop, run_manager, **kwargs)
    
    def predict(self, text: str, **kwargs) -> str:
        """Predict method for BaseLanguageModel compatibility"""
        return self._call(text)
    
    async def apredict(self, text: str, **kwargs) -> str:
        """Async predict method"""
        return self.predict(text, **kwargs)
    
    def predict_messages(self, messages, **kwargs):
        """Predict messages method"""
        from langchain_core.messages import AIMessage  # type: ignore
        if messages:
            last_message = messages[-1]
            if hasattr(last_message, 'content'):
                response = self._call(last_message.content)
            else:
                response = self._call(str(last_message))
        else:
            response = self._call("Hello")
        return AIMessage(content=response)
    
    async def apredict_messages(self, messages, **kwargs):
        """Async predict messages method"""
        return self.predict_messages(messages, **kwargs)
    
    def generate_prompt(self, prompts, stop=None, callbacks=None, **kwargs):
        """Generate prompt method"""
        return self._generate(prompts, stop=stop, callbacks=callbacks, **kwargs)
    
    async def agenerate_prompt(self, prompts, stop=None, callbacks=None, **kwargs):
        """Async generate prompt method"""
        return self.generate_prompt(prompts, stop=stop, callbacks=callbacks, **kwargs)
    
    def invoke(self, input, config=None, **kwargs):
        """Invoke method for BaseLanguageModel compatibility"""
        if isinstance(input, str):
            return self._call(input)
        else:
            return self._call(str(input))
    
    def __call__(self, prompt, **kwargs):
        """Make the LLM callable"""
        return self._call(prompt)

# Define the state structure for our multi-agent system
class AppointmentState(TypedDict, total=False):
    messages: List  # type: ignore
    current_step: str  # type: ignore
    current_agent: str  # type: ignore
    patient_info: Dict  # type: ignore
    appointment_info: Dict  # type: ignore
    appointment_details: Dict  # type: ignore
    insurance_info: Dict  # type: ignore
    validation_errors: List[str]  # type: ignore
    conversation_history: List[str]  # type: ignore
    workflow_complete: bool  # type: ignore
    next_agent: str  # type: ignore
    next_agent: Optional[str]

class FreeMedicalSchedulingGraph:
    def __init__(self):
        """Initialize the free LangGraph multi-agent system"""
        # Initialize Mock LLM (completely free!)
        self.llm = MockLLM()
        
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
        
        compiled_workflow = workflow.compile()
        return compiled_workflow
    
    def greeting_agent(self, state: AppointmentState) -> AppointmentState:
        """Handle initial patient greeting and introduction"""
        messages = state.get("messages", [])
        
        if not messages or len(messages) == 0:
            # Generate greeting using mock LLM
            greeting = self.llm("Generate a greeting message for medical scheduling")
            messages.append(AIMessage(content=greeting))
        
        # Update state
        state["messages"] = messages
        state["current_step"] = "greeting_complete"
        state["conversation_history"] = state.get("conversation_history", []) + [
            "Greeting phase completed"
        ]
        
        return state
    
    def patient_intake_agent(self, state: AppointmentState) -> AppointmentState:
        """Collect and validate patient information"""
        messages = state.get("messages", [])
        
        # Extract patient info from last message if available
        last_message = messages[-1].content if messages else ""
        patient_info = state.get("patient_info", {})
        
        # Simple parsing for demo purposes
        if "name" not in patient_info and any(word in last_message.lower() for word in ["i'm", "my name is", "i am"]):
            # Try to extract name
            words = last_message.split()
            if len(words) >= 3:
                patient_info["name"] = " ".join(words[-2:]).title()
        
        # Mock response for collecting information
        intake_response = self.llm("Generate patient intake message for collecting information")
        messages.append(AIMessage(content=intake_response))
        
        state["messages"] = messages
        state["patient_info"] = patient_info
        state["current_step"] = "patient_info_collected"
        
        return state
    
    def emr_lookup_agent(self, state: AppointmentState) -> AppointmentState:
        """Look up patient in EMR system and classify as new/returning"""
        patient_info = state.get("patient_info", {})
        messages = state.get("messages", [])
        
        # Mock EMR lookup - randomly classify as new or returning
        import random
        is_returning = random.choice([True, False])
        
        if is_returning:
            lookup_response = self.llm("Generate returning patient welcome message")
            state["appointment_info"] = {"duration": 30, "type": "follow_up"}
        else:
            lookup_response = self.llm("Generate new patient welcome message")
            state["appointment_info"] = {"duration": 60, "type": "new_patient"}
        
        messages.append(AIMessage(content=lookup_response))
        state["messages"] = messages
        state["current_step"] = "emr_lookup_complete"
        
        return state
    
    def scheduling_agent(self, state: AppointmentState) -> AppointmentState:
        """Handle appointment scheduling and availability checking"""
        messages = state.get("messages", [])
        appointment_info = state.get("appointment_info", {})
        
        # Mock scheduling response
        scheduling_response = self.llm("Generate scheduling options message")
        messages.append(AIMessage(content=scheduling_response))
        
        # Mock appointment booking
        appointment_info.update({
            "doctor": "Dr. Johnson",
            "date": "2025-09-05",
            "time": "09:00",
            "appointment_id": "APT-20250905-0001"
        })
        
        state["messages"] = messages
        state["appointment_info"] = appointment_info
        state["current_step"] = "appointment_booked"
        
        return state
    
    def insurance_agent(self, state: AppointmentState) -> AppointmentState:
        """Collect and verify insurance information"""
        messages = state.get("messages", [])
        
        # Mock insurance collection
        insurance_response = self.llm("Generate insurance collection message")
        messages.append(AIMessage(content=insurance_response))
        
        # Mock insurance verification
        state["insurance_info"] = {
            "carrier": "Blue Cross Blue Shield",
            "member_id": "123456789",
            "verified": True,
            "copay": "$25"
        }
        
        state["messages"] = messages
        state["current_step"] = "insurance_complete"
        
        return state
    
    def confirmation_agent(self, state: AppointmentState) -> AppointmentState:
        """Provide final confirmation and send appointment details"""
        messages = state.get("messages", [])
        
        # Generate confirmation summary
        confirmation_response = self.llm("Generate appointment confirmation summary")
        messages.append(AIMessage(content=confirmation_response))
        
        state["messages"] = messages
        state["current_step"] = "complete"
        
        return state
    
    def should_continue(self, state: AppointmentState) -> str:
        """Determine if workflow should continue or end"""
        if state.get("current_step") == "complete":
            return "end"
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
            messages = current_state.get("messages", [])
            messages.append(HumanMessage(content=user_input))
            current_state["messages"] = messages  # type: ignore
        
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
free_medical_scheduling_graph = FreeMedicalSchedulingGraph()
