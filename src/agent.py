
"""
Medical Scheduling Agent - Free LangGraph + LangChain Implementation
Multi-agent orchestration system for medical appointment scheduling.
"""

from typing import Dict, List, Optional, Any
import json
import os

# Import our simple LangGraph implementation
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from simple_agent import simple_langgraph_agent

class LangGraphSchedulingAgent:
    """
    Medical Scheduling Agent using LangGraph + LangChain (Free Version)
    
    This demonstrates multi-agent orchestration using LangGraph concepts
    with zero API costs - completely free to run!
    """
    
    def __init__(self):
        """Initialize the free LangGraph-based scheduling agent"""
        self.agent = simple_langgraph_agent
        self.conversation_history = []
        
    def process_user_input(self, user_input: str) -> str:
        """
        Process user input through the LangGraph multi-agent workflow
        
        Args:
            user_input: User's message or input
            
        Returns:
            Agent's response
        """
        try:
            # Process through LangGraph workflow
            response = self.agent.process_user_input(user_input)
            
            # Store conversation history
            self.conversation_history.append({
                "user": user_input,
                "agent": response,
                "step": self.agent.state.current_step,
                "current_agent": self.get_conversation_state().get("current_agent", "unknown")
            })
            
            return response
            
        except Exception as e:
            error_response = f"I apologize, but I encountered an issue: {str(e)}. Let me help you start over with scheduling your appointment."
            self.agent.reset_conversation()  # Reset state on error
            return error_response
    
    def get_conversation_state(self) -> Dict[str, Any]:
        """Get current conversation state for UI display"""
        return self.agent.get_conversation_state()
    
    def get_appointment_summary(self) -> Optional[Dict[str, Any]]:
        """Get complete appointment summary if booking is complete"""
        return self.agent.get_appointment_summary()
    
    def reset_conversation(self):
        """Reset the conversation state"""
        self.agent.reset_conversation()
        self.conversation_history = []
    
    def export_conversation_data(self) -> Dict[str, Any]:
        """Export conversation data for records"""
        return {
            "conversation_history": self.conversation_history,
            "final_state": self.get_conversation_state(),
            "appointment_summary": self.get_appointment_summary()
        }

# Backwards compatibility class for existing code
class SchedulingAgent(LangGraphSchedulingAgent):
    """
    Backwards compatibility wrapper for the original SchedulingAgent class
    
    This ensures existing code continues to work while using the new
    LangGraph + LangChain implementation under the hood.
    """
    
    def __init__(self):
        super().__init__()
        # Legacy properties for backwards compatibility
        self.conversation_state = {
            'step': 'greeting',
            'patient_info': {},
            'appointment_info': {},
            'insurance_info': {}
        }
    
    def get_response(self, user_input: str) -> str:
        """Legacy method name - routes to new implementation"""
        response = self.process_user_input(user_input)
        
        # Update legacy state for backwards compatibility
        state = self.get_conversation_state()
        self.conversation_state.update({
            'step': state['step'],
            'patient_info': state['patient_info'],
            'appointment_info': state['appointment_info'],
            'insurance_info': state['insurance_info']
        })
        
        return response
    
    def validate_input(self, user_input: str, field_type: str) -> tuple:
        """Legacy validation method - now handled by LangChain tools"""
        # This is handled automatically by the validation tools in LangGraph
        return True, user_input
    
    def lookup_patient(self, name: str, dob: str) -> Optional[Dict]:
        """Legacy method - now handled by LangChain EMR lookup tool"""
        # This is handled by the EMR lookup agent in LangGraph
        return None
    
    def get_available_slots(self, doctor: Optional[str] = None, date: Optional[str] = None) -> List[Dict]:
        """Legacy method - now handled by LangChain scheduling tools"""
        # This is handled by the scheduling agent in LangGraph
        return []
    
    def generate_confirmation_summary(self) -> str:
        """Generate appointment confirmation summary"""
        patient_info = self.conversation_state['patient_info']
        appointment_info = self.conversation_state['appointment_info']
        insurance_info = self.conversation_state['insurance_info']
        
        summary = "📋 APPOINTMENT CONFIRMATION SUMMARY\n"
        summary += "=" * 40 + "\n\n"
        
        summary += f"👤 Patient: {patient_info.get('name', 'N/A')}\n"
        summary += f"📞 Phone: {patient_info.get('phone', 'N/A')}\n"
        summary += f"📧 Email: {patient_info.get('email', 'N/A')}\n\n"
        
        summary += f"🩺 Doctor: {appointment_info.get('doctor', 'N/A')}\n"
        summary += f"📅 Date: {appointment_info.get('date', 'N/A')}\n"
        summary += f"🕐 Time: {appointment_info.get('time', 'N/A')}\n"
        summary += f"⏱️ Duration: {appointment_info.get('duration', 30)} minutes\n\n"
        
        summary += f"🏥 Insurance: {insurance_info.get('carrier', 'N/A')}\n"
        summary += f"🆔 Member ID: {insurance_info.get('member_id', 'N/A')}\n"
        if insurance_info.get('group_id'):
            summary += f"👥 Group ID: {insurance_info['group_id']}\n"
        
        summary += "\nType 'CONFIRM' to finalize your appointment or 'CANCEL' to start over:"
        return summary

