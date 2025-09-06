import streamlit as st  # type: ignore
import sys
import os
import time
import html

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from agent import LangGraphSchedulingAgent  # Use the new LangGraph implementation
from database import DatabaseManager
from calendar_integration import CalendarIntegration
from reminder_system import ReminderSystem
from utils import get_system_stats, log_activity
import pandas as pd  # type: ignore
from datetime import datetime, timedelta
import json
import re

# Enhanced CSS for better UI/UX
st.markdown("""
<style>
/* Progress indicator animations */
@keyframes pulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.1); }
    100% { transform: scale(1); }
}

/* Quick action button styling */
.stButton > button {
    transition: all 0.3s ease;
    border-radius: 10px;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
}

/* Enhanced chat styling with clear question/answer hierarchy */
.user-message {
    background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
    color: #1565c0;
    padding: 1rem;
    border-radius: 15px 15px 15px 5px;
    margin: 0.5rem 0 0.5rem 0;
    margin-left: 0;
    max-width: 80%;
    width: fit-content;
    min-width: 200px;
    animation: slideInLeft 0.3s ease;
    box-shadow: 0 2px 10px rgba(21, 101, 192, 0.2);
    border-left: 4px solid #1976d2;
    border: 1px solid #90caf9;
    word-wrap: break-word;
    display: inline-block;
}

.agent-message {
    background: linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%);
    color: #4a148c;
    padding: 1rem;
    border-radius: 15px 15px 5px 15px;
    margin: 0.5rem 0 1rem 0;
    margin-left: 0;
    max-width: 85%;
    width: fit-content;
    min-width: 250px;
    animation: slideInLeft 0.3s ease;
    box-shadow: 0 2px 10px rgba(74, 20, 140, 0.2);
    border: 1px solid #ce93d8;
    border-left: 4px solid #7b1fa2;
    word-wrap: break-word;
    display: inline-block;
}

@keyframes slideInRight {
    from { transform: translateX(50px); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
}

@keyframes slideInLeft {
    from { transform: translateX(-50px); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
}

/* Typing indicator */
.typing-indicator {
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 15px;
    margin: 0.5rem 0;
    margin-right: 20%;
    animation: pulse 1.5s infinite;
}

.typing-indicator::after {
    content: "AI is typing...";
    color: #666;
    font-style: italic;
}

/* Enhanced buttons */
.stButton > button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    border-radius: 25px;
    padding: 0.75rem 1.5rem;
    font-weight: 600;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    background: linear-gradient(135deg, #5a67d8 0%, #667eea 100%);
}

.stButton > button:active {
    transform: translateY(0);
    box-shadow: 0 2px 10px rgba(102, 126, 234, 0.3);
}

/* Smart suggestion pills */
.suggestion-pill {
    background: rgba(102, 126, 234, 0.1);
    border: 2px solid #667eea;
    color: #667eea;
    padding: 0.5rem 1rem;
    border-radius: 20px;
    margin: 0.25rem;
    cursor: pointer;
    transition: all 0.2s ease;
    display: inline-block;
}

.suggestion-pill:hover {
    background: #667eea;
    color: white;
    transform: scale(1.05);
}

/* Input field enhancements */
.stTextInput > div > div > input {
    border: 2px solid #e9ecef;
    border-radius: 25px;
    padding: 1rem;
    font-size: 1rem;
    transition: all 0.3s ease;
    background: #f8f9fa;
}

.stTextInput > div > div > input:focus {
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    background: white;
}

/* Quick actions bar */
.quick-actions {
    background: rgba(255, 255, 255, 0.9);
    backdrop-filter: blur(10px);
    border-radius: 15px;
    padding: 1rem;
    margin: 1rem 0;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.2);
}

/* Progress indicator enhancements */
.step-indicator {
    background: white;
    border-radius: 10px;
    padding: 0.5rem;
    margin: 0.25rem;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease;
}

.step-indicator.active {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    transform: scale(1.1);
}

.step-indicator.completed {
    background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
    color: white;
}

/* Chat container improvements */
.chat-container {
    max-height: 500px;
    overflow-y: auto;
    padding: 1rem;
    border-radius: 15px;
    background: linear-gradient(to bottom, #f8f9fa, #ffffff);
    border: 1px solid #e9ecef;
    margin: 1rem 0;
}

/* Mobile responsiveness */
@media (max-width: 768px) {
    .user-message, .agent-message {
        margin-left: 0;
        max-width: 90%;
        min-width: 150px;
        border-radius: 15px;
    }
    
    .stButton > button {
        width: 100%;
        margin: 0.25rem 0;
    }
    
    .quick-actions {
        padding: 0.5rem;
    }
}

/* Accessibility improvements */
.stButton > button:focus,
.suggestion-pill:focus {
    outline: 3px solid #667eea;
    outline-offset: 2px;
}

/* Loading animations */
@keyframes shimmer {
    0% { background-position: -200px 0; }
    100% { background-position: calc(200px + 100%) 0; }
}

.loading-shimmer {
    background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
    background-size: 200px 100%;
    animation: shimmer 1.5s infinite;
}

/* Form styling */
.stTextInput > div > div > input {
    border-radius: 8px;
    border: 2px solid #e0e0e0;
    transition: border-color 0.3s ease;
}

.stTextInput > div > div > input:focus {
    border-color: #007bff;
    box-shadow: 0 0 5px rgba(0,123,255,0.3);
}

/* Success/error message styling */
.success-message {
    background: linear-gradient(90deg, #28a745, #20c997);
    color: white;
    padding: 1rem;
    border-radius: 10px;
    margin: 1rem 0;
}

.warning-message {
    background: linear-gradient(90deg, #ffc107, #fd7e14);
    color: white;
    padding: 1rem;
    border-radius: 10px;
    margin: 1rem 0;
}

/* Tutorial styling */
.tutorial-box {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 1.5rem;
    border-radius: 15px;
    margin: 1rem 0;
}

/* Progress bar custom styling */
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, #007bff, #28a745);
}

/* Keyboard shortcuts styling */
.shortcut-hint {
    position: fixed;
    bottom: 20px;
    right: 20px;
    background: rgba(0, 0, 0, 0.8);
    color: white;
    padding: 10px;
    border-radius: 8px;
    font-size: 0.8rem;
    z-index: 1000;
    opacity: 0;
    transition: opacity 0.3s ease;
}

.shortcut-hint.show {
    opacity: 1;
}

/* Accessibility improvements */
.accessible-button {
    border: 2px solid transparent;
    transition: all 0.2s ease;
}

.accessible-button:focus {
    border-color: #007bff;
    box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
}

/* Mobile responsive improvements */
@media (max-width: 768px) {
    .chat-message {
        font-size: 0.9rem;
        padding: 0.8rem;
    }
    
    .stButton > button {
        font-size: 0.8rem;
        padding: 0.5rem;
    }
}
</style>

<script>
// Enhanced keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + Enter to send message
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        const sendButton = document.querySelector('button[kind="primary"]');
        if (sendButton) {
            sendButton.click();
        }
    }
    
    // Ctrl/Cmd + R to reset chat
    if ((e.ctrlKey || e.metaKey) && e.key === 'r') {
        e.preventDefault();
        const resetButton = document.querySelector('button[data-testid*="reset"]');
        if (resetButton) {
            resetButton.click();
        }
    }
    
    // Escape to focus input
    if (e.key === 'Escape') {
        const input = document.querySelector('input[type="text"]');
        if (input) {
            input.focus();
        }
    }
    
    // Show keyboard hints on Ctrl/Cmd + ?
    if ((e.ctrlKey || e.metaKey) && e.key === '/') {
        e.preventDefault();
        showKeyboardHints();
    }
});

function showKeyboardHints() {
    const hints = document.createElement('div');
    hints.className = 'shortcut-hint show';
    hints.innerHTML = `
        <strong>Keyboard Shortcuts:</strong><br>
        Ctrl/Cmd + Enter: Send message<br>
        Ctrl/Cmd + R: Reset chat<br>
        Escape: Focus input<br>
        Ctrl/Cmd + /: Show this help
    `;
    document.body.appendChild(hints);
    
    setTimeout(() => {
        hints.remove();
    }, 4000);
}

// Auto-save user preferences
function saveUserPreferences() {
    const preferences = {
        theme: 'default',
        autoSuggest: true,
        quickActions: true,
        savedAt: new Date().toISOString()
    };
    localStorage.setItem('schedulingAppPreferences', JSON.stringify(preferences));
}

// Load user preferences
function loadUserPreferences() {
    const saved = localStorage.getItem('schedulingAppPreferences');
    if (saved) {
        return JSON.parse(saved);
    }
    return null;
}

// Initialize preferences
document.addEventListener('DOMContentLoaded', function() {
    loadUserPreferences();
});
</script>
""", unsafe_allow_html=True)

def get_smart_suggestions(current_step, conversation_history):
    """Generate smart suggestions based on current step"""
    suggestions = []
    
    if current_step <= 1:  # Greeting
        suggestions = [
            "I need to schedule an appointment",
            "I'm a new patient and need to book an appointment",
            "I'm a returning patient for a follow-up",
            "I need to reschedule my existing appointment"
        ]
    elif current_step == 2:  # Patient info
        suggestions = [
            "My name is John Smith, phone 555-1234",
            "I'm Sarah Johnson, email sarah@email.com",
            "My information: Mike Davis, 555-9876, mike@email.com",
            "I'm already in your system under [Name]"
        ]
    elif current_step == 3:  # EMR lookup
        suggestions = [
            "Look me up by name: [Your Name]",
            "Search by phone: [Your Phone]",
            "Check under [Your Name]",
            "I was last seen in [Month/Year]"
        ]
    elif current_step == 4:  # Scheduling
        # Look for specific appointment options in recent conversation
        recent_text = ""
        if conversation_history:
            recent_text = " ".join([msg['content'] for msg in conversation_history[-2:]])
        
        # Generate contextual scheduling suggestions
        if "dr. johnson" in recent_text.lower():
            suggestions = [
                "I'll take the Dr. Johnson appointment on 2025-09-05 at 09:00 AM",
                "Book me with Dr. Johnson on September 5th at 9 AM",
                "The morning appointment with Dr. Johnson works for me",
                "I prefer the Dr. Johnson slot"
            ]
        elif "dr. wilson" in recent_text.lower():
            suggestions = [
                "I'll take the Dr. Wilson appointment on 2025-09-06 at 02:00 PM",
                "Book me with Dr. Wilson on September 6th at 2 PM",
                "The afternoon appointment with Dr. Wilson works for me",
                "I prefer the Dr. Wilson slot"
            ]
        else:
            # Generic scheduling suggestions
            suggestions = [
                "I prefer morning appointments",
                "I'm available afternoons",
                "Next week works for me",
                "I need it as soon as possible"
            ]
    elif current_step == 5:  # Insurance
        suggestions = [
            "I have Blue Cross Blue Shield",
            "I have Aetna insurance",
            "I have Medicare",
            "I'll pay out of pocket"
        ]
    elif current_step == 6:  # Confirmation
        suggestions = [
            "Yes, please confirm this appointment",
            "That time works perfectly",
            "Please send me a confirmation email",
            "Yes, I understand the appointment details"
        ]
    
    return suggestions

def update_current_step():
    """Update current step based on agent conversation state and conversation content"""
    if hasattr(st.session_state, 'agent'):
        conversation_state = st.session_state.agent.get_conversation_state()
        agent_step = conversation_state.get('step', 'greeting')
        
        # Map agent steps to UI steps
        step_mapping = {
            'greeting': 1,
            'patient_intake': 2,
            'emr_lookup': 3,
            'scheduling': 4,
            'insurance': 5,
            'confirmation': 6,
            'complete': 7
        }
        
        new_step = step_mapping.get(agent_step, 1)
        
        # Also check conversation content for more accurate step detection
        if hasattr(st.session_state, 'conversation_history') and st.session_state.conversation_history:
            # Look at recent messages to determine current step
            recent_messages = [msg['content'].lower() for msg in st.session_state.conversation_history[-3:]]
            combined_text = ' '.join(recent_messages)
            
            # Check for specific agent identifiers in recent messages
            if 'scheduling agent' in combined_text and any(keyword in combined_text for keyword in ['available slots', 'appointment', 'date:', 'time:']):
                new_step = max(new_step, 4)  # We're definitely in scheduling
            elif 'emr lookup agent' in combined_text:
                new_step = max(new_step, 3)  # We're in EMR lookup
            elif 'patient intake agent' in combined_text:
                new_step = max(new_step, 2)  # We're in patient intake
            elif 'insurance agent' in combined_text:
                new_step = max(new_step, 5)  # We're in insurance
            elif 'confirmation agent' in combined_text:
                new_step = max(new_step, 6)  # We're in confirmation
            
            # Additional content-based detection (as fallback)
            if any(keyword in combined_text for keyword in ['which appointment works', 'available slots', 'dr. johnson', 'dr. wilson']):
                new_step = max(new_step, 4)
            elif any(keyword in combined_text for keyword in ['insurance', 'coverage', 'member id']):
                new_step = max(new_step, 5)
            elif any(keyword in combined_text for keyword in ['confirm', 'confirmation', 'finalize']):
                new_step = max(new_step, 6)
        
        if new_step != st.session_state.current_step:
            st.session_state.current_step = new_step
            return True
    return False

def validate_phone(phone):
    """Validate phone number format"""
    phone_pattern = r'^\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})$'
    return re.match(phone_pattern, phone.strip()) is not None

def validate_email(email):
    """Validate email format"""
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_pattern, email.strip()) is not None

def format_phone(phone):
    """Format phone number to standard format"""
    digits = re.sub(r'[^\d]', '', phone)
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    return phone

def get_quick_forms(current_step):
    """Generate quick input forms based on current step"""
    if current_step == 2:  # Patient information
        return {
            'type': 'patient_info',
            'fields': ['name', 'phone', 'email', 'date_of_birth']
        }
    elif current_step == 4:  # Scheduling preferences
        return {
            'type': 'scheduling',
            'fields': ['preferred_date', 'preferred_time', 'doctor_preference']
        }
    elif current_step == 5:  # Insurance
        return {
            'type': 'insurance',
            'fields': ['insurance_carrier', 'member_id', 'group_number']
        }
    return None

def extract_appointment_details(conversation_history):
    """Extract appointment details from conversation history"""
    details = {}
    
    # Join all conversation text
    all_text = ' '.join([msg['content'] for msg in conversation_history])
    
    # Extract patient name
    name_match = re.search(r'name is ([A-Za-z\s]+)', all_text, re.IGNORECASE)
    if name_match:
        details['patient_name'] = name_match.group(1).strip()
    
    # Extract phone
    phone_match = re.search(r'phone.*?(\(?[\d\s\-\)\(]{10,15})', all_text, re.IGNORECASE)
    if phone_match:
        details['phone'] = phone_match.group(1).strip()
    
    # Extract email
    email_match = re.search(r'email.*?([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', all_text, re.IGNORECASE)
    if email_match:
        details['email'] = email_match.group(1).strip()
    
    # Extract doctor
    doctor_match = re.search(r'(dr\.\s*\w+)', all_text, re.IGNORECASE)
    if doctor_match:
        details['doctor'] = doctor_match.group(1).title()
    
    # Extract date
    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', all_text)
    if date_match:
        details['date'] = date_match.group(1)
    
    # Extract time
    time_match = re.search(r'(\d{1,2}:\d{2}\s*[APap][Mm])', all_text)
    if time_match:
        details['time'] = time_match.group(1)
    
    # Extract insurance
    insurance_match = re.search(r'(aetna|blue cross|medicare|anthem|cigna)', all_text, re.IGNORECASE)
    if insurance_match:
        details['insurance'] = insurance_match.group(1).title()
    
    return details

def save_patient_preferences(appointment_details):
    """Save patient information for future quick booking"""
    if appointment_details:
        st.session_state.saved_patient_info = {
            'name': appointment_details.get('patient_name'),
            'phone': appointment_details.get('phone'),
            'email': appointment_details.get('email'),
            'saved_at': datetime.now()
        }

def reset_conversation():
    """Reset conversation for new booking"""
    st.session_state.conversation_history = []
    st.session_state.conversation_started = False
    st.session_state.current_step = 1
    st.session_state.agent = LangGraphSchedulingAgent()

def quick_book_with_saved_info():
    """Start quick booking with saved patient information"""
    if 'saved_patient_info' in st.session_state and st.session_state.saved_patient_info:
        saved_info = st.session_state.saved_patient_info
        quick_message = f"I need to book an appointment. My name is {saved_info['name']}, phone {saved_info['phone']}, email {saved_info['email']}"
        
        reset_conversation()
        st.session_state.conversation_started = True
        
        # Add greeting and patient info in one go
        user_timestamp = datetime.now()
        st.session_state.conversation_history.append({
            'type': 'user',
            'content': quick_message,
            'timestamp': user_timestamp
        })
        
        agent_response = st.session_state.agent.process_user_input(quick_message)
        from datetime import timedelta
        agent_timestamp = user_timestamp + timedelta(seconds=5)
        st.session_state.conversation_history.append({
            'type': 'agent',
            'content': agent_response,
            'timestamp': agent_timestamp
        })

def extract_booking_info(conversation_history):
    """Extract booking information from conversation history"""
    info = {
        'patient_name': '',
        'reason': '',
        'doctor': '',
        'date': '',
        'time': ''
    }
    
    # Join all messages to search for patterns
    all_text = ' '.join([msg['content'] for msg in conversation_history])
    
    # Extract name (simple pattern matching)
    name_patterns = [
        r"my name is (\w+ \w+)",
        r"I'm (\w+ \w+)",
        r"this is (\w+ \w+)"
    ]
    for pattern in name_patterns:
        match = re.search(pattern, all_text, re.IGNORECASE)
        if match:
            info['patient_name'] = match.group(1)
            break
    
    # Extract reason
    reason_patterns = [
        r"appointment for (.+?)(?:\.|,|$)",
        r"need to see (?:a )?doctor (?:for|about) (.+?)(?:\.|,|$)",
        r"(?:checkup|consultation|visit) (?:for|about) (.+?)(?:\.|,|$)"
    ]
    for pattern in reason_patterns:
        match = re.search(pattern, all_text, re.IGNORECASE)
        if match:
            info['reason'] = match.group(1).strip()
            break
    
    # Extract doctor
    doctor_patterns = [
        r"Dr\. (\w+)",
        r"Doctor (\w+)"
    ]
    for pattern in doctor_patterns:
        match = re.search(pattern, all_text, re.IGNORECASE)
        if match:
            info['doctor'] = f"Dr. {match.group(1)}"
            break
    
    return info

def calculate_booking_completion(booking_info):
    """Calculate booking completion percentage"""
    total_fields = len(booking_info)
    completed_fields = sum(1 for value in booking_info.values() if value and value.strip())
    return completed_fields / total_fields if total_fields > 0 else 0

# Page configuration
st.set_page_config(
    page_title="AI Scheduling Agent",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-container {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border: 1px solid #dee2e6;
    }
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 18px 18px 5px 18px;
        margin: 0.8rem 0;
        margin-left: 0;
        max-width: 80%;
        width: fit-content;
        min-width: 200px;
        text-align: left;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        animation: slideInLeft 0.3s ease-out;
        word-wrap: break-word;
        display: inline-block;
    }
    
    .agent-message {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        color: #495057;
        padding: 1rem;
        border-radius: 15px 15px 5px 15px;
        margin: 0.5rem 0;
        margin-left: 0;
        max-width: 85%;
        width: fit-content;
        min-width: 250px;
        animation: slideInLeft 0.3s ease-out;
        border-left: 4px solid #007acc;
        word-wrap: break-word;
        display: inline-block;
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        text-align: center;
        animation: fadeIn 0.5s ease-out;
    }
    
    .quick-action-btn {
        background: linear-gradient(135deg, #007acc 0%, #005a9e 100%);
        color: white;
        border: none;
        padding: 0.75rem;
        border-radius: 10px;
        cursor: pointer;
        transition: all 0.3s ease;
        width: 100%;
        font-weight: 500;
    }
    
    .quick-action-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 122, 204, 0.3);
    }
    
    .floating-help {
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: #007acc;
        color: white;
        border-radius: 50%;
        width: 60px;
        height: 60px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        z-index: 1000;
        font-size: 1.5rem;
    }
    
    .floating-help:hover {
        background: #005a9e;
        transform: scale(1.1);
    }
    
    .progress-indicator {
        background: linear-gradient(90deg, #007acc, #28a745);
        height: 4px;
        border-radius: 2px;
        margin: 0.5rem 0;
    }
    
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.875rem;
        font-weight: 500;
    }
    
    .status-active {
        background: #d4edda;
        color: #155724;
    }
    
    .status-completed {
        background: #cce5ff;
        color: #004085;
    }
    
    .status-pending {
        background: #fff3cd;
        color: #856404;
    }
    .stats-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        color: #212529;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
        border: 1px solid #e9ecef;
        transition: transform 0.2s ease;
    }
    .stats-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.15);
    }
    .quick-action-btn {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.8rem 1.5rem;
        border-radius: 25px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    .quick-action-btn:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    /* Ensure text visibility in all containers */
    .stTextInput input {
        color: #212529 !important;
        background-color: #ffffff !important;
        border-radius: 10px !important;
        border: 2px solid #e9ecef !important;
        transition: border-color 0.3s ease !important;
    }
    .stTextInput input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
    }
    .stTextArea textarea {
        color: #212529 !important;
        background-color: #ffffff !important;
        border-radius: 10px !important;
        border: 2px solid #e9ecef !important;
    }
    /* Animations */
    @keyframes slideInRight {
        from { opacity: 0; transform: translateX(30px); }
        to { opacity: 1; transform: translateX(0); }
    }
    @keyframes slideInLeft {
        from { opacity: 0; transform: translateX(-30px); }
        to { opacity: 1; transform: translateX(0); }
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    /* Fix any dark mode issues */
    [data-testid="stChatMessage"] {
        background-color: #ffffff;
        color: #212529;
    }
    /* Enhance buttons */
    .stButton button {
        border-radius: 20px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    .stButton button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2) !important;
    }
    /* Enhance info boxes */
    .stAlert {
        border-radius: 15px !important;
        animation: fadeIn 0.5s ease-out;
    }
</style>

<script>
document.addEventListener('keydown', function(e) {
    // Ctrl + / for help
    if (e.ctrlKey && e.key === '/') {
        alert('Keyboard Shortcuts:\\n\\n• Enter - Send message\\n• Ctrl+/ - Show this help\\n• Esc - Clear input\\n\\nQuick Actions:\\n• Use buttons for instant booking\\n• Follow suggestions for faster responses');
        e.preventDefault();
    }
    
    // Esc to clear input
    if (e.key === 'Escape') {
        const inputs = document.querySelectorAll('input[type="text"]');
        inputs.forEach(input => input.value = '');
    }
});

// Auto-focus on input field
function focusInput() {
    const input = document.querySelector('input[type="text"]');
    if (input && !input.value) {
        input.focus();
    }
}

// Focus after page load
setTimeout(focusInput, 500);
</script>
""", unsafe_allow_html=True)

# Initialize session state
if 'agent' not in st.session_state:
    st.session_state.agent = LangGraphSchedulingAgent()
    st.session_state.db_manager = DatabaseManager()
    st.session_state.calendar = CalendarIntegration()
    st.session_state.reminder_system = ReminderSystem()
    st.session_state.conversation_history = []
    st.session_state.conversation_started = False
    st.session_state.current_step = 1
    st.session_state.total_steps = 6

# Sidebar
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1rem;">
        <h1>🏥</h1>
        <h3>AI Scheduling Assistant</h3>
        <p style="color: #666;">Powered by LangGraph + LangChain</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Step-by-Step Process Instructions
    st.markdown("### 📋 Booking Process")
    
    with st.expander("📝 Step-by-Step Guide", expanded=False):
        st.markdown("""
        **Follow these 6 easy steps to book your appointment:**
        
        **Step 1: Personal Information** 👤
        - Provide your full name
        - Share your phone number
        - Give us your email address
        
        **Step 2: Medical Details** 🏥
        - Describe your health concern
        - Mention any specific symptoms
        - Share relevant medical history
        
        **Step 3: Doctor Preference** 👩‍⚕️
        - Choose your preferred doctor
        - Or let us recommend based on your needs
        - View available specialists
        
        **Step 4: Schedule Selection** 📅
        - Pick your preferred date
        - Choose convenient time slot
        - Confirm availability
        
        **Step 5: Insurance Verification** 💳
        - Provide insurance carrier info
        - Share member ID and group number
        - Verify coverage details
        
        **Step 6: Final Confirmation** ✅
        - Review all appointment details
        - Confirm booking
        - Receive confirmation
        
        💡 **Pro Tips:**
        - Use the chat to provide info naturally
        - Smart suggestions will help you
        - Your progress is saved automatically
        """)
    
    st.markdown("---")
    
    # Quick Actions Section
    st.markdown("### ⚡ Quick Actions")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Reset Chat", use_container_width=True, key="sidebar_reset_btn"):
            reset_conversation()
            st.success("Chat reset! Ready for new booking.")
            time.sleep(1)
            st.rerun()
    
    with col2:
        if st.button("📋 View Appointments", use_container_width=True):
            st.info("Viewing all appointments...")
    
    # Quick Booking Section
    if 'saved_patient_info' in st.session_state and st.session_state.saved_patient_info:
        st.markdown("### 🚀 Express Booking")
        saved_info = st.session_state.saved_patient_info
        st.success(f"Welcome back, {saved_info['name']}!")
        
        if st.button("⚡ Quick Book", type="primary", use_container_width=True):
            quick_book_with_saved_info()
            st.rerun()
        
        st.caption(f"Saved: {saved_info['saved_at'].strftime('%m/%d/%Y')}")
    
    st.markdown("---")
    
    # Help & Tips Section
    st.markdown("### 💡 Tips & Help")
    
    with st.expander("🆘 Need Help?"):
        st.markdown("""
        **How to book an appointment:**
        1. Start with "Hello" or use Quick Actions
        2. Provide your information
        3. Choose appointment time
        4. Verify insurance
        5. Confirm booking
        
        **Quick tips:**
        - Use Smart Suggestions for faster input
        - Your info is saved for next time
        - Click help button (💡) for guidance
        """)
    
    with st.expander("📞 Available Doctors"):
        st.markdown("""
        **Our specialists:**
        • Dr. Johnson - Internal Medicine
        • Dr. Wilson - Cardiology  
        • Dr. Smith - Pediatrics
        • Dr. Davis - Dermatology
        • Dr. Brown - Orthopedics
        """)
    
    with st.expander("🕐 Office Hours"):
        st.markdown("""
        **Monday - Friday:** 8:00 AM - 6:00 PM
        **Saturday:** 9:00 AM - 2:00 PM
        **Sunday:** Closed
        
        **Emergency:** Call 911
        **After hours:** Use patient portal
        """)
    
    st.markdown("---")
    
    # System Status
    st.markdown("### 📊 System Status")
    st.success("🟢 All systems operational")
    st.caption("Last updated: Just now")
    
    # Quick Stats
    if st.session_state.conversation_history:
        msg_count = len(st.session_state.conversation_history)
        st.metric("Messages", msg_count)
        st.metric("Current Step", f"{st.session_state.current_step}/6")
    
    st.markdown("---")
    
    # Progress Tracker
    if st.session_state.conversation_started:
        st.markdown("### 📋 Booking Progress")
        
        steps = [
            "👋 Greeting",
            "📝 Patient Info", 
            "🔍 EMR Lookup",
            "📅 Scheduling",
            "🏥 Insurance",
            "✅ Confirmation"
        ]
        
        current_step = min(st.session_state.current_step, len(steps))
        
        for i, step in enumerate(steps, 1):
            if i < current_step:
                st.markdown(f"✅ {step}")
            elif i == current_step:
                st.markdown(f"🔄 **{step}** *(Current)*")
            else:
                st.markdown(f"⏳ {step}")
        
        # Progress bar
        progress = (current_step - 1) / (len(steps) - 1)
        st.progress(progress)
        st.caption(f"Step {current_step} of {len(steps)}")
        
        st.markdown("---")
    
    # Quick Tips
    st.markdown("### 💡 Quick Tips")
    with st.expander("🆕 First Time?"):
        st.markdown("""
        1. Click **New Appointment** to start
        2. Follow the prompts step by step
        3. Use suggested responses for speed
        4. Check progress in the sidebar
        """)
    
    with st.expander("⚡ Power User?"):
        st.markdown("""
        - Use Quick Actions for instant starts
        - Type naturally - AI understands context
        - Check other tabs for data insights
        - Reset chat anytime with Reset button
        """)
    
    with st.expander("🏥 Available Doctors"):
        st.markdown("""
        - **Dr. Johnson** - Internal Medicine
        - **Dr. Wilson** - Cardiology  
        - **Dr. Smith** - Pediatrics
        - **Dr. Davis** - Dermatology
        - **Dr. Brown** - Orthopedics
        """)
    
    st.markdown("---")
    
    # Live appointment summary (if in progress)
    if st.session_state.conversation_started and st.session_state.current_step >= 2:
        st.markdown("### 📋 Current Booking")
        
        # Extract info from conversation
        booking_info = extract_booking_info(st.session_state.conversation_history)
        
        if booking_info['patient_name']:
            st.markdown(f"**Patient:** {booking_info['patient_name']}")
        if booking_info['reason']:
            st.markdown(f"**Reason:** {booking_info['reason']}")
        if booking_info['doctor']:
            st.markdown(f"**Doctor:** {booking_info['doctor']}")
        if booking_info['date']:
            st.markdown(f"**Date:** {booking_info['date']}")
        if booking_info['time']:
            st.markdown(f"**Time:** {booking_info['time']}")
        
        # Show completion percentage
        completion = calculate_booking_completion(booking_info)
        st.progress(completion)
        st.caption(f"Booking {int(completion*100)}% complete")
    
    st.markdown("---")
    
    # System statistics
    st.markdown("### 📊 System Stats")
    stats = get_system_stats()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Patients", stats['total_patients'])
        st.metric("Confirmed", stats['confirmed_appointments'])
    with col2:
        st.metric("Total Appointments", stats['total_appointments'])
        st.metric("Today", stats['today_appointments'])
    
    st.markdown("---")
    
    # Quick actions
    st.subheader("⚡ Quick Actions")
    
    if st.button("🔄 Reset Conversation"):
        st.session_state.agent.reset_conversation()
        st.session_state.conversation_history = []
        st.session_state.conversation_started = False
        st.success("Conversation reset!")
        st.rerun()
    
    if st.button("📊 View Appointments"):
        st.session_state.show_appointments = True
    
    if st.button("👥 Generate Sample Data"):
        st.session_state.db_manager.generate_synthetic_data(20)
        st.success("Sample data generated!")
        st.rerun()
    
    st.markdown("---")
    
    # Configuration
    st.subheader("⚙️ Settings")
    
    # Email settings
    with st.expander("📧 Email Configuration"):
        email_user = st.text_input("Email Address", value="demo@healthcare.com")
        email_enabled = st.checkbox("Enable Email Notifications", value=True)
        
    # Doctor settings
    with st.expander("👨‍⚕️ Doctor Configuration"):
        st.write("Available Doctors:")
        st.write("• Dr. Johnson - Family Medicine")
        st.write("• Dr. Wilson - Internal Medicine") 
        st.write("• Dr. Smith - Cardiology")
    
    st.markdown("---")
    st.markdown("Built with ❤️ for healthcare efficiency")

# Main content area
st.markdown('<h1 class="main-header">🤖 AI Medical Scheduling Assistant</h1>', unsafe_allow_html=True)

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(["💬 Chat Interface", "📅 Appointments", "👥 Patients", "📊 Analytics"])

with tab1:
    # Welcome message first (always visible)
    if not st.session_state.conversation_history:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 2rem; border-radius: 15px; margin-bottom: 2rem; text-align: center; color: white;">
            <h2 style="margin: 0 0 1rem 0; color: white;">👋 Welcome to AI Scheduling!</h2>
            <p style="font-size: 1.1rem; margin: 0.5rem 0; opacity: 0.9;">
                I'm here to help you book appointments quickly and easily.
            </p>
            <p style="font-size: 1rem; margin: 0; opacity: 0.8;">
                💡 <strong>Get started:</strong> Type "Hello" in the chat below or use Quick Actions!
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Booking Progress - Moved to top for better visibility
    if st.session_state.conversation_started:
        st.markdown("### 📊 Booking Progress")
        
        # Update step before showing progress
        step_changed = update_current_step()
        
        # Debug info (remove this in production)
        if hasattr(st.session_state, 'agent'):
            conversation_state = st.session_state.agent.get_conversation_state()
            agent_step = conversation_state.get('step', 'greeting')
            st.caption(f"🔍 Debug: Agent Step = {agent_step}, UI Step = {st.session_state.current_step}")
        
        # Define steps with emojis and descriptions
        steps = [
            ("👋", "Greeting", "Initial contact"),
            ("📝", "Patient Info", "Personal details"),
            ("📅", "Scheduling", "Pick date & time"),
            ("🏥", "Insurance", "Coverage verification"),
            ("✅", "Confirmation", "Final approval")
        ]
        
        # Create progress bar
        current_step = min(st.session_state.current_step, len(steps))
        progress = (current_step - 1) / len(steps) if current_step <= len(steps) else 1.0
        
        st.progress(progress)
        
        # Show step indicators
        cols = st.columns(len(steps))
        for i, (emoji, title, desc) in enumerate(steps):
            with cols[i]:
                step_num = i + 1
                if step_num < current_step:
                    # Completed step
                    st.markdown(f"""
                    <div style="text-align: center;">
                        <div style="color: green; font-size: 1.5rem;">{emoji}</div>
                        <div style="color: green; font-weight: bold;">{title}</div>
                        <div style="color: gray; font-size: 0.8rem;">✓ Done</div>
                    </div>
                    """, unsafe_allow_html=True)
                elif step_num == current_step:
                    # Current step
                    st.markdown(f"""
                    <div style="text-align: center;">
                        <div style="color: blue; font-size: 1.5rem; animation: pulse 2s infinite;">{emoji}</div>
                        <div style="color: blue; font-weight: bold;">{title}</div>
                        <div style="color: blue; font-size: 0.8rem;">← Current</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # Future step
                    st.markdown(f"""
                    <div style="text-align: center;">
                        <div style="color: lightgray; font-size: 1.5rem;">{emoji}</div>
                        <div style="color: lightgray;">{title}</div>
                        <div style="color: lightgray; font-size: 0.8rem;">{desc}</div>
                    </div>
                    """, unsafe_allow_html=True)
        st.markdown("---")
    
    # This duplicate conversation section has been removed
    conversation_state = st.session_state.agent.get_conversation_state()
    current_step = st.session_state.current_step
    
    # Only show form if we're in patient info step and conversation has started
    if current_step == 2 and st.session_state.conversation_started:
        with st.expander("� Quick Info Form (Optional)", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Name", placeholder="📝 Required: First Last Name (e.g., John Smith)")
                phone = st.text_input("Phone", placeholder="📞 Required: 10-digit number (e.g., 555-123-4567)")
            with col2:
                email = st.text_input("Email", placeholder="📧 Required: Valid email (e.g., john.smith@email.com)")
                
            if st.button("📤 Submit All Info", type="primary"):
                if name and phone and email:
                    message = f"My name is {name}, phone {phone}, email {email}"
                    # Add to conversation
                    st.session_state.conversation_history.append({
                        'type': 'user',
                        'content': message,
                        'timestamp': datetime.now()
                    })
                    agent_response = st.session_state.agent.process_user_input(message)
                    st.session_state.conversation_history.append({
                        'type': 'agent',
                        'content': agent_response,
                        'timestamp': datetime.now()
                    })
                    st.rerun()
                else:
                    st.warning("Please fill in all fields")
    
    # Main Conversation Display Section
    st.markdown("---")
    
    if st.session_state.conversation_history:
        st.markdown("### 💬 Conversation")
        
        # Create a chat container for better styling
        chat_container = st.container()
        
        with chat_container:
            # Sort messages by timestamp to ensure proper chronological order
            sorted_conversation = sorted(st.session_state.conversation_history, 
                                       key=lambda x: x.get('timestamp', datetime.now()))
            
            # Display all messages in the conversation
            for i, message in enumerate(sorted_conversation):
                timestamp = message.get('timestamp', datetime.now()).strftime('%H:%M:%S')
                
                if message['type'] == 'user':
                    # Add a conversation divider before user questions (except the first one)
                    if i > 0:
                        st.markdown('<div style="border-top: 1px dashed #ccc; margin: 1.5rem 0 1rem 0; opacity: 0.5;"></div>', unsafe_allow_html=True)
                    
                    escaped_content = html.escape(message["content"])
                    
                    st.markdown(f'''
                    <div class="user-message">
                        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                            <div style="flex: 1;">
                                <strong>You</strong><br>
                                {escaped_content}
                            </div>
                            <div style="font-size: 0.8rem; opacity: 0.7; margin-left: 1rem;">
                                {timestamp}
                            </div>
                        </div>
                    </div>
                    ''', unsafe_allow_html=True)
                else:
                    # Detect agent type from message content
                    agent_emoji = "🤖"
                    agent_name = "AI Assistant"
                    if "greeting" in message["content"].lower():
                        agent_emoji = "👋"
                        agent_name = "Greeting Agent"
                    elif "patient" in message["content"].lower():
                        agent_emoji = "📝"
                        agent_name = "Patient Intake"
                    elif "schedule" in message["content"].lower():
                        agent_emoji = "📅"
                        agent_name = "Scheduling Agent"
                    elif "insurance" in message["content"].lower():
                        agent_emoji = "🏥"
                        agent_name = "Insurance Agent"
                    elif "confirm" in message["content"].lower():
                        agent_emoji = "✅"
                        agent_name = "Confirmation Agent"
                    
                    escaped_content = html.escape(message["content"])
                    
                    st.markdown(f'''
                    <div class="agent-message">
                        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                            <div style="flex: 1;">
                                <strong>{agent_emoji} {agent_name}</strong><br>
                                {escaped_content}
                            </div>
                            <div style="font-size: 0.8rem; opacity: 0.7; margin-left: 1rem;">
                                {timestamp}
                            </div>
                        </div>
                    </div>
                    ''', unsafe_allow_html=True)
                
                # Add minimal space after user messages (questions)
                if message['type'] == 'user':
                    st.markdown('<div style="margin: 0.3rem 0;"></div>', unsafe_allow_html=True)
                else:
                    # Add more space after agent responses for visual separation
                    st.markdown('<div style="margin: 0.8rem 0;"></div>', unsafe_allow_html=True)
    else:
        # Show helpful message when no conversation yet
        st.info("💡 **Start chatting!** Type a message below or click one of the Quick Action buttons to begin your appointment booking.")
    
    # Quick Actions Section - only show when no conversation has started
    if not st.session_state.conversation_history:
        st.markdown("### 🚀 Quick Actions")
        
        # Quick Actions Buttons - First Row
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📅 New Appointment", use_container_width=True, type="primary", key="new_apt_btn"):
                user_input = "I need to schedule a new appointment"
                st.session_state.conversation_history.append({
                    'type': 'user',
                    'content': user_input,
                    'timestamp': datetime.now()
                })
                st.session_state.conversation_started = True
                agent_response = st.session_state.agent.process_user_input(user_input)
                st.session_state.conversation_history.append({
                    'type': 'agent',
                    'content': agent_response,
                    'timestamp': datetime.now()
                })
                update_current_step()
                st.rerun()
        
        with col2:
            if st.button("🔄 Follow-up Visit", use_container_width=True, key="followup_btn"):
                user_input = "I need a follow-up appointment"
                st.session_state.conversation_history.append({
                    'type': 'user',
                    'content': user_input,
                    'timestamp': datetime.now()
                })
                st.session_state.conversation_started = True
                agent_response = st.session_state.agent.process_user_input(user_input)
                st.session_state.conversation_history.append({
                    'type': 'agent',
                    'content': agent_response,
                    'timestamp': datetime.now()
                })
                update_current_step()
                st.rerun()
        
        with col3:
            if st.button("🩺 Check-up", use_container_width=True, key="checkup_btn"):
                user_input = "I need an annual check-up"
                st.session_state.conversation_history.append({
                    'type': 'user',
                    'content': user_input,
                    'timestamp': datetime.now()
                })
                st.session_state.conversation_started = True
                agent_response = st.session_state.agent.process_user_input(user_input)
                st.session_state.conversation_history.append({
                    'type': 'agent',
                    'content': agent_response,
                    'timestamp': datetime.now()
                })
                update_current_step()
                st.rerun()
        
        # Quick Actions Buttons - Second Row
        col4, col5, col6 = st.columns(3)
        
        with col4:
            if st.button("🚨 Urgent Care", use_container_width=True, key="urgent_btn"):
                user_input = "I need urgent care"
                st.session_state.conversation_history.append({
                    'type': 'user',
                    'content': user_input,
                    'timestamp': datetime.now()
                })
                st.session_state.conversation_started = True
                agent_response = st.session_state.agent.process_user_input(user_input)
                st.session_state.conversation_history.append({
                    'type': 'agent',
                    'content': agent_response,
                    'timestamp': datetime.now()
                })
                update_current_step()
                st.rerun()
        
        with col5:
            if st.button("❌ Cancel Appointment", use_container_width=True, key="cancel_btn"):
                user_input = "I need to cancel my appointment"
                st.session_state.conversation_history.append({
                    'type': 'user',
                    'content': user_input,
                    'timestamp': datetime.now()
                })
                st.session_state.conversation_started = True
                agent_response = st.session_state.agent.process_user_input(user_input)
                st.session_state.conversation_history.append({
                    'type': 'agent',
                    'content': agent_response,
                    'timestamp': datetime.now()
                })
                update_current_step()
                st.rerun()
        
        with col6:
            if st.button("🔄 Reschedule", use_container_width=True, key="reschedule_btn"):
                user_input = "I need to reschedule my appointment"
                st.session_state.conversation_history.append({
                    'type': 'user',
                    'content': user_input,
                    'timestamp': datetime.now()
                })
                st.session_state.conversation_started = True
                agent_response = st.session_state.agent.process_user_input(user_input)
                st.session_state.conversation_history.append({
                    'type': 'agent',
                    'content': agent_response,
                    'timestamp': datetime.now()
                })
                update_current_step()
                st.rerun()
    
    # Contextual Quick Actions (when conversation is active)
    if st.session_state.conversation_started:
        conversation_state = st.session_state.agent.get_conversation_state()
        workflow_complete = conversation_state.get('step') == 'complete'
        
        if not workflow_complete:
            current_step = conversation_state.get('step', 'start')
            
            # Define context-aware quick actions
            quick_actions = []
            
            if current_step == 'scheduling_confirm':
                quick_actions = ["Yes, that works perfect", "I prefer a different time", "I need morning appointments", "I prefer afternoon slots"]
                
            elif current_step == 'scheduling':
                quick_actions = ["Morning preferred", "Afternoon preferred", "Any doctor is fine", "Female doctor preferred", "Dr. Johnson specifically"]
                
            elif current_step == 'scheduling_doctor_select':
                quick_actions = ["Dr. Johnson - Internal Medicine", "Dr. Wilson - Family Medicine", "Dr. Smith - Cardiology", "Dr. Brown - Orthopedics", "Dr. Davis - Dermatology"]
                
            elif current_step == 'emr_lookup':
                # Check if asking about appointment type specifically
                last_agent_message = ""
                for msg in reversed(st.session_state.conversation_history):
                    if msg['type'] == 'agent':
                        last_agent_message = msg['content'].lower()
                        break
                
                if 'appointment' in last_agent_message and ('type' in last_agent_message or 'checkup' in last_agent_message or 'physical' in last_agent_message):
                    # Appointment type selection
                    quick_actions = [
                        "📅 Annual checkup/physical (60 min)", 
                        "🤒 Sick visit (35 min)", 
                        "🔄 Follow-up appointment (45 min)", 
                        "💬 Routine consultation (45 min)"
                    ]
                else:
                    # General EMR lookup quick actions
                    quick_actions = ["Annual checkup", "Sick visit", "Follow-up appointment", "I need urgent care"]
                    
            elif current_step == 'insurance':
                current_field = conversation_state.get('current_field', '')
                if current_field == 'carrier':
                    quick_actions = ["Blue Cross Blue Shield", "Aetna", "United Healthcare", "Medicaid/Medicare", "I'll pay cash"]
                elif current_field == 'member_id':
                    quick_actions = ["Let me get my card", "I don't have it with me", "It's a work insurance plan"]
            
            # Show quick actions if available
            if quick_actions:
                st.markdown("### ⚡ Quick Actions")
                
                # Show in 2 rows if more than 4 actions
                if len(quick_actions) > 4:
                    # First row
                    cols1 = st.columns(min(4, len(quick_actions)))
                    for i, action in enumerate(quick_actions[:4]):
                        with cols1[i]:
                            if st.button(action, key=f"quick_{current_step}_{i}", use_container_width=True):
                                st.session_state.conversation_history.append({
                                    'type': 'user',
                                    'content': action,
                                    'timestamp': datetime.now()
                                })
                                agent_response = st.session_state.agent.process_user_input(action)
                                st.session_state.conversation_history.append({
                                    'type': 'agent',
                                    'content': agent_response,
                                    'timestamp': datetime.now()
                                })
                                update_current_step()
                                st.rerun()
                    
                    # Second row if needed
                    if len(quick_actions) > 4:
                        remaining = quick_actions[4:]
                        cols2 = st.columns(len(remaining))
                        for i, action in enumerate(remaining):
                            with cols2[i]:
                                if st.button(action, key=f"quick_{current_step}_{i+4}", use_container_width=True):
                                    st.session_state.conversation_history.append({
                                        'type': 'user',
                                        'content': action,
                                        'timestamp': datetime.now()
                                    })
                                    agent_response = st.session_state.agent.process_user_input(action)
                                    st.session_state.conversation_history.append({
                                        'type': 'agent',
                                        'content': agent_response,
                                        'timestamp': datetime.now()
                                    })
                                    update_current_step()
                                    st.rerun()
                else:
                    # Single row for 4 or fewer actions
                    cols = st.columns(len(quick_actions))
                    for i, action in enumerate(quick_actions):
                        with cols[i]:
                            if st.button(action, key=f"quick_{current_step}_{i}", use_container_width=True):
                                st.session_state.conversation_history.append({
                                    'type': 'user',
                                    'content': action,
                                    'timestamp': datetime.now()
                                })
                                agent_response = st.session_state.agent.process_user_input(action)
                                st.session_state.conversation_history.append({
                                    'type': 'agent',
                                    'content': agent_response,
                                    'timestamp': datetime.now()
                                })
                                update_current_step()
                                st.rerun()
    
    # Chat input moved to top (before conversation stats)
    st.markdown("---")
    
    # Check if workflow is complete
    conversation_state = st.session_state.agent.get_conversation_state()
    workflow_complete = conversation_state.get('step') == 'complete'
    
    # Dynamic placeholder text based on conversation state
    if not st.session_state.conversation_history:
        placeholder_text = "🚀 Type 'Hello' to start appointment booking"
    elif workflow_complete:
        placeholder_text = "✨ Type anything to book another appointment"
    else:
        # Get current conversation state for dynamic placeholders
        conversation_state = st.session_state.agent.get_conversation_state()
        current_step = conversation_state.get('step', 'start')
        current_field = conversation_state.get('current_field', '')
        
        # Dynamic placeholders based on current step
        if current_step == 'greeting':
            placeholder_text = "📝 Enter your full name (e.g., John Smith)"
        elif current_step == 'patient_intake':
            # Check the last agent message to understand what's being asked
            last_agent_message = ""
            for msg in reversed(st.session_state.conversation_history):
                if msg['type'] == 'agent':
                    last_agent_message = msg['content'].lower()
                    break
            
            # Provide specific guidance based on what's being asked
            if 'name' in last_agent_message and ('full' in last_agent_message or 'first' in last_agent_message):
                placeholder_text = "📝 Enter your full name (e.g., John Smith)"
            elif 'phone' in last_agent_message or 'number' in last_agent_message:
                placeholder_text = "📞 Enter phone number (e.g., 555-123-4567)"
            elif 'email' in last_agent_message:
                placeholder_text = "📧 Enter email address (e.g., john@email.com)"
            elif 'birth' in last_agent_message or 'dob' in last_agent_message or 'age' in last_agent_message:
                placeholder_text = "📅 Enter date of birth (MM/DD/YYYY)"
            elif 'address' in last_agent_message:
                placeholder_text = "🏠 Enter your address"
            elif 'insurance' in last_agent_message:
                placeholder_text = "🏥 Enter insurance information"
            elif 'symptom' in last_agent_message or 'reason' in last_agent_message or 'visit' in last_agent_message:
                placeholder_text = "🩺 Describe your symptoms or reason for visit"
            else:
                placeholder_text = "� Please provide the requested information"
        elif current_step == 'emr_lookup':
            # Check if asking about appointment type
            last_agent_message = ""
            for msg in reversed(st.session_state.conversation_history):
                if msg['type'] == 'agent':
                    last_agent_message = msg['content'].lower()
                    break
            
            if 'appointment' in last_agent_message and ('type' in last_agent_message or 'checkup' in last_agent_message):
                placeholder_text = "📅 Select appointment type from Quick Actions or describe what you need"
            else:
                placeholder_text = "🩺 Describe symptoms or reason for visit"
        elif current_step == 'scheduling':
            placeholder_text = "🕐 Specify time preference or doctor (e.g., morning, Dr. Johnson)"
        elif current_step == 'scheduling_doctor_select':
            placeholder_text = "👨‍⚕️ Choose your doctor (e.g., Dr. Johnson or 1)"
        elif current_step == 'scheduling_confirm':
            placeholder_text = "✅ Type 'yes' to confirm or suggest changes"
        elif current_step == 'insurance':
            if current_field == 'carrier':
                placeholder_text = "🏥 Enter insurance carrier (e.g., Blue Cross or cash pay)"
            elif current_field == 'member_id':
                placeholder_text = "🆔 Enter member ID (e.g., ABC123456789)"
            elif current_field == 'group_number':
                placeholder_text = "👥 Enter group number (e.g., GRP001)"
            else:
                placeholder_text = "💳 Provide insurance information"
        elif current_step == 'confirmation':
            placeholder_text = "🎯 Type 'confirm' to complete booking"
        else:
            placeholder_text = "💬 Type your message or use Quick Actions"
    
    # Display guidance text above input - make it more prominent
    st.markdown(f"""
    <div style="background: linear-gradient(90deg, #1f77b4, #ff7f0e); 
                padding: 12px; 
                border-radius: 8px; 
                margin-bottom: 10px;
                border-left: 4px solid #ffffff;">
        <h4 style="margin: 0; color: white; font-size: 16px;">
            💡 {placeholder_text}
        </h4>
    </div>
    """, unsafe_allow_html=True)
    
    # Use form for proper Enter key handling
    with st.form("chat_form", clear_on_submit=True):
        col1, col2 = st.columns([6, 1])
        
        with col1:
            user_input = st.text_input(
                "Message",
                value="",
                label_visibility="collapsed",
                key="chat_input"
            )
        
        with col2:
            submitted = st.form_submit_button("Send", type="primary", use_container_width=True)
        
        # Process input
        if submitted and user_input.strip():
            # Add user message with current timestamp
            user_timestamp = datetime.now()
            st.session_state.conversation_history.append({
                'type': 'user',
                'content': user_input,
                'timestamp': user_timestamp
            })
            
            st.session_state.conversation_started = True
            
            # Get agent response
            agent_response = st.session_state.agent.process_user_input(user_input)
            
            # Add agent response with a slight delay to ensure proper ordering
            from datetime import timedelta
            agent_timestamp = user_timestamp + timedelta(seconds=5)
            st.session_state.conversation_history.append({
                'type': 'agent',
                'content': agent_response,
                'timestamp': agent_timestamp
            })
            
            update_current_step()
            st.rerun()
    
    # Show conversation stats (moved to bottom)
    if st.session_state.conversation_history:
        total_messages = len(st.session_state.conversation_history)
        user_messages = len([m for m in st.session_state.conversation_history if m['type'] == 'user'])
        agent_messages = len([m for m in st.session_state.conversation_history if m['type'] == 'agent'])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.caption(f"💬 Total: {total_messages} messages")
        with col2:
            st.caption(f"👤 You: {user_messages} messages")
        with col3:
            st.caption(f"🤖 AI: {agent_messages} responses")
    
    # This duplicate chat interface section has been removed
# Removed problematic form code
#                col1, col2, col3 = st.columns(3)
#                with col1:
#                    pref_date = st.date_input("📅 Preferred Date", min_value=datetime.now().date())
#                with col2:
#                    pref_time = st.selectbox("🕐 Preferred Time", [
#                        "Morning (8 AM - 12 PM)", "Afternoon (12 PM - 5 PM)", 
#                        "Evening (5 PM - 8 PM)", "No preference"
#                    ])
#                with col3:
#                    doctor = st.selectbox("👨‍⚕️ Doctor Preference", [
#                        "Dr. Smith", "Dr. Johnson", "Dr. Brown", "Dr. Wilson", "Dr. Davis", "No preference"
#                    ])
#                
#                if st.button("🚀 Submit Scheduling Preferences", type="primary", use_container_width=True):
#                    message = f"I would like to schedule an appointment on {pref_date.strftime('%B %d, %Y')} during {pref_time.lower()}"
#                    if doctor != "No preference":
#                        message += f" with {doctor}"
#                    st.session_state.conversation_history.append({
#                        'type': 'user',
#                        'content': message,
#                        'timestamp': datetime.now()
#                    })
#                    agent_response = st.session_state.agent.process_user_input(message)
#                    st.session_state.conversation_history.append({
#                        'type': 'agent',
#                        'content': agent_response,
#                        'timestamp': datetime.now()
#                    })
#                    st.rerun()
#                    
#            elif quick_form['type'] == 'insurance':
#                col1, col2, col3 = st.columns(3)
#                with col1:
#                    carrier = st.selectbox("🏥 Insurance Carrier", [
#                        "Blue Cross Blue Shield", "Aetna", "Cigna", "UnitedHealth", 
#                        "Anthem", "Medicare", "Medicaid", "Other"
#                    ])
#                with col2:
#                    member_id = st.text_input("🆔 Member ID", placeholder="ABC123456789")
#                with col3:
#                    group_num = st.text_input("👥 Group Number", placeholder="GRP001")
#                
#                if st.button("🚀 Submit Insurance Info", type="primary", use_container_width=True):
#                    if carrier and member_id:
#                        message = f"My insurance carrier is {carrier}, member ID is {member_id}"
#                        if group_num:
#                            message += f", and group number is {group_num}"
#                        st.session_state.conversation_history.append({
#                            'type': 'user',
#                            'content': message,
#                            'timestamp': datetime.now()
#                        })
#                        agent_response = st.session_state.agent.process_user_input(message)
#                        st.session_state.conversation_history.append({
#                            'type': 'agent',
#                            'content': agent_response,
#                            'timestamp': datetime.now()
#                        })
#                        st.rerun()
#                    else:
#                        st.warning("Please fill in at least the carrier and member ID")

# Commented out problematic form code - syntax errors resolved
    
    # This duplicate quick actions section has been removed
    
    st.markdown("---")
    
    # Progress Indicator (removed duplicate booking progress section)
    if st.session_state.conversation_started:
        st.markdown("### 📊 Quick Progress Indicator")
        
        # Simple progress without duplicating the detailed section above
        current_step = min(st.session_state.current_step, 5)
        progress = (current_step - 1) / 4 if current_step <= 5 else 1.0
        st.progress(progress)
        st.caption(f"Step {current_step} of 5")
        st.markdown("---")
    
    # Chat interface  
    st.markdown("### 💬 Conversation")
    
    # Simple conversation navigation
    if st.session_state.conversation_history:
        col1, col2 = st.columns([3, 1])
        with col1:
            total_messages = len(st.session_state.conversation_history)
            st.caption(f"💬 {total_messages} messages • Step {st.session_state.current_step}/5")
        with col2:
            if st.button("� New Chat", help="Start fresh conversation", use_container_width=True):
                # Reset conversation
                st.session_state.conversation_history = []
                st.session_state.conversation_started = False
                st.session_state.current_step = 0
                st.session_state.agent = LangGraphSchedulingAgent()
                st.toast("🔄 New conversation started!", icon="✅")
                st.rerun()
    
    # Chat input interface (moved to top for immediate access)
    
    # Progress indicator for ongoing conversations
    if st.session_state.conversation_history:
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            total_messages = len(st.session_state.conversation_history)
            st.caption(f"💬 {total_messages} messages")
        with col2:
            st.caption(f"📍 Step {st.session_state.current_step}/5")
        with col3:
            if st.button("� Reset", help="Start fresh conversation", use_container_width=True):
                st.session_state.conversation_history = []
                st.session_state.conversation_started = False
                st.session_state.current_step = 0
                st.session_state.agent = LangGraphSchedulingAgent()
                st.toast("🔄 New conversation started!", icon="✅")
                st.rerun()
        st.markdown("---")
    
    chat_container = st.container()
    
    with chat_container:
        # Important notifications area
        if st.session_state.conversation_started:
            # Show step-specific tips
            if st.session_state.current_step == 1:
                st.info("💡 **Tip**: The greeting agent will welcome you and gather basic information.")
            elif st.session_state.current_step == 2:
                st.info("💡 **Tip**: Share your name, date of birth, and reason for visit.")
            elif st.session_state.current_step == 3:
                st.info("💡 **Tip**: The system is looking up your medical records.")
            elif st.session_state.current_step == 4:
                st.info("💡 **Tip**: Pick your preferred doctor, date, and time slot.")
            elif st.session_state.current_step == 5:
                st.info("💡 **Tip**: Verify your insurance information for coverage.")
            elif st.session_state.current_step == 6:
                st.success("🎉 **Almost done!** Your appointment is being confirmed.")
        
        # Check if workflow is complete and show completion notice
        conversation_state = st.session_state.agent.get_conversation_state()
        workflow_complete = conversation_state.get('step') == 'complete'
        
        if workflow_complete:
            st.success("🎉 **Appointment Successfully Booked!**")
            
            # Extract and display appointment details
            appointment_details = extract_appointment_details(st.session_state.conversation_history)
            
            if appointment_details:
                st.markdown("### 📋 Your Appointment Summary")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.info(f"""
                    **👤 Patient:** {appointment_details.get('patient_name', 'N/A')}
                    **📞 Phone:** {appointment_details.get('phone', 'N/A')}
                    **📧 Email:** {appointment_details.get('email', 'N/A')}
                    """)
                
                with col2:
                    st.info(f"""
                    **👨‍⚕️ Doctor:** {appointment_details.get('doctor', 'N/A')}
                    **📅 Date:** {appointment_details.get('date', 'N/A')}
                    **🕐 Time:** {appointment_details.get('time', 'N/A')}
                    **🏥 Insurance:** {appointment_details.get('insurance', 'N/A')}
                    """)
            
            st.markdown("### 🚀 What would you like to do next?")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("📅 Book Another Appointment", type="primary", use_container_width=True):
                    # Save current patient info for quick reuse
                    save_patient_preferences(appointment_details)
                    reset_conversation()
                    st.rerun()
            
            with col2:
                if st.button("✏️ Modify This Appointment", use_container_width=True):
                    st.session_state.conversation_history.append({
                        'type': 'user',
                        'content': 'I need to modify my appointment',
                        'timestamp': datetime.now()
                    })
                    agent_response = st.session_state.agent.process_user_input("I need to modify or reschedule my appointment")
                    st.session_state.conversation_history.append({
                        'type': 'agent',
                        'content': agent_response,
                        'timestamp': datetime.now()
                    })
                    st.rerun()
            
            with col3:
                if st.button("📧 Email Confirmation", use_container_width=True):
                    st.success("📧 Confirmation email sent!")
                    st.balloons()
            
            with col4:
                if st.button("🏠 Start Over", use_container_width=True):
                    reset_conversation()
                    st.rerun()
            
            # Quick booking for returning patients
            if 'saved_patient_info' in st.session_state and st.session_state.saved_patient_info:
                st.markdown("### ⚡ Express Booking")
                saved_info = st.session_state.saved_patient_info
                st.success(f"💡 **Welcome back {saved_info['name']}!** Your information is saved for faster booking.")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🚀 Quick Book with Saved Info", type="secondary", use_container_width=True):
                        quick_book_with_saved_info()
                        st.rerun()
                
                with col2:
                    if st.button("🗑️ Clear Saved Info", use_container_width=True):
                        del st.session_state.saved_patient_info
                        st.success("Saved information cleared!")
                        st.rerun()
        else:
            st.info("💡 **To book another appointment**, please click the 'Reset Chat' button in the sidebar.")
        
        # Conversation display moved to main section - no duplicate needed here

# Floating help button temporarily removed to fix syntax issues

with tab2:
    st.header("📅 Appointment Management")
    
    # Load appointments
    try:
        # Get correct path to appointments file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        appointments_file = os.path.join(project_root, 'data', 'appointments.csv')
        
        appointments_df = pd.read_csv(appointments_file)
        
        if not appointments_df.empty:
            st.subheader("Current Appointments")
            
            # Filter options
            col1, col2, col3 = st.columns(3)
            with col1:
                status_filter = st.selectbox("Filter by Status", 
                                           ['Active Only', 'All', 'Confirmed', 'Pending', 'Cancelled'], 
                                           index=0)  # Default to 'Active Only'
            with col2:
                doctor_filter = st.selectbox("Filter by Doctor", 
                                           ['All', 'Dr. Johnson', 'Dr. Wilson', 'Dr. Smith', 'Dr. Brown', 'Dr. Davis'])
            with col3:
                date_filter = st.date_input("Filter by Date", value=None)
            
            # Apply filters
            filtered_df = appointments_df.copy()
            
            # Handle status filtering with new 'Active Only' option
            if status_filter == 'Active Only':
                # Show only Confirmed and Pending appointments (exclude Cancelled)
                filtered_df = filtered_df[filtered_df['status'].isin(['Confirmed', 'Pending'])]
            elif status_filter != 'All':
                filtered_df = filtered_df[filtered_df['status'] == status_filter]
            
            if doctor_filter != 'All':
                filtered_df = filtered_df[filtered_df['doctor'] == doctor_filter]
            
            if date_filter:
                filtered_df = filtered_df[filtered_df['date'] == date_filter.strftime('%Y-%m-%d')]
            
            # Display appointments
            if not filtered_df.empty:
                # Add appointment statistics
                col1, col2, col3, col4 = st.columns(4)
                
                total_appointments = len(appointments_df)
                confirmed_count = len(appointments_df[appointments_df['status'] == 'Confirmed'])
                pending_count = len(appointments_df[appointments_df['status'] == 'Pending'])
                cancelled_count = len(appointments_df[appointments_df['status'] == 'Cancelled'])
                
                with col1:
                    st.metric("Total Appointments", total_appointments)
                with col2:
                    st.metric("✅ Confirmed", confirmed_count)
                with col3:
                    st.metric("⏳ Pending", pending_count)
                with col4:
                    st.metric("❌ Cancelled", cancelled_count)
                
                st.markdown("---")
                
                # Style the dataframe to highlight status
                def style_status(val):
                    if val == 'Confirmed':
                        return 'background-color: #d4edda; color: #155724;'  # Green
                    elif val == 'Pending':
                        return 'background-color: #fff3cd; color: #856404;'  # Yellow
                    elif val == 'Cancelled':
                        return 'background-color: #f8d7da; color: #721c24;'  # Red
                    return ''
                
                # Apply styling and display
                styled_df = filtered_df.style.map(style_status, subset=['status'])
                st.dataframe(styled_df, width='stretch')
                
                # Show filter info
                if status_filter == 'Active Only':
                    st.info("ℹ️ **Showing active appointments only**. To see cancelled appointments, change the status filter to 'Cancelled' or 'All'.")
                
                # Export options
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("📊 Export to Excel"):
                        excel_file = st.session_state.db_manager.export_appointments_to_excel()
                        if excel_file:
                            st.success(f"Exported to {excel_file}")
                        else:
                            st.error("No data to export")
                
                with col2:
                    csv_data = filtered_df.to_csv(index=False)
                    st.download_button(
                        label="📄 Download CSV",
                        data=csv_data,
                        file_name=f"appointments_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
            else:
                st.info("No appointments match the selected filters.")
                
        else:
            st.info("No appointments found. Start by booking an appointment in the Chat tab!")
            
    except FileNotFoundError:
        st.info("No appointment data available. Book your first appointment to see it here!")

with tab3:
    st.header("👥 Patient Management")
    
    # Load patients
    try:
        # Get correct path to patients file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        patients_file = os.path.join(project_root, 'data', 'patients.csv')
        
        patients_df = pd.read_csv(patients_file)
        
        if not patients_df.empty:
            st.subheader("Patient Database")
            
            # Search functionality
            search_term = st.text_input("🔍 Search patients by name or email...", placeholder="💡 Type patient name (e.g., 'John Smith') or email (e.g., 'john@email.com') to filter records")
            
            if search_term:
                mask = (patients_df['name'].str.contains(search_term, case=False, na=False) |
                       patients_df['email'].str.contains(search_term, case=False, na=False))
                display_df = patients_df[mask]
            else:
                display_df = patients_df
            
            st.dataframe(display_df, width='stretch')
            
            # Patient statistics
            st.subheader("📊 Patient Statistics")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Patients", len(patients_df))
            with col2:
                insurance_counts = patients_df['insurance_carrier'].value_counts()
                most_common_insurance = str(insurance_counts.index[0]) if not insurance_counts.empty else "N/A"
                st.metric("Most Common Insurance", most_common_insurance)
            with col3:
                doctor_counts = patients_df['doctor'].value_counts()
                most_popular_doctor = str(doctor_counts.index[0]) if not doctor_counts.empty else "N/A"
                st.metric("Most Popular Doctor", most_popular_doctor)
            with col4:
                # Calculate average patient age (simplified)
                st.metric("Database Size", f"{len(patients_df)} records")
                
        else:
            st.info("No patient data available.")
            
    except FileNotFoundError:
        st.info("No patient database found. Patients will be added as appointments are booked.")

with tab4:
    st.header("📊 Analytics Dashboard")
    
    try:
        # Load data with correct paths
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        appointments_file = os.path.join(project_root, 'data', 'appointments.csv')
        patients_file = os.path.join(project_root, 'data', 'patients.csv')
        
        appointments_df = pd.read_csv(appointments_file) if os.path.exists(appointments_file) else pd.DataFrame()
        patients_df = pd.read_csv(patients_file) if os.path.exists(patients_file) else pd.DataFrame()
        
        if not appointments_df.empty:
            # Appointment status distribution
            st.subheader("📈 Appointment Status Distribution")
            if 'status' in appointments_df.columns:
                status_counts = appointments_df['status'].value_counts()
                st.bar_chart(status_counts)
            
            # Doctor workload
            st.subheader("👨‍⚕️ Doctor Appointment Distribution")
            if 'doctor' in appointments_df.columns:
                doctor_counts = appointments_df['doctor'].value_counts()
                st.bar_chart(doctor_counts)
            
            # Recent activity
            st.subheader("📅 Recent Appointments")
            if 'date' in appointments_df.columns:
                # Convert date column to datetime for proper sorting
                appointments_df['date'] = pd.to_datetime(appointments_df['date'])
                recent_appointments = appointments_df.sort_values('date', ascending=False).head(5)
                st.dataframe(recent_appointments[['patient_name', 'doctor', 'date', 'time', 'status']], 
                           width='stretch')
        
        # System performance metrics
        st.subheader("⚡ System Performance")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            success_rate = (stats['confirmed_appointments'] / max(stats['total_appointments'], 1)) * 100
            st.metric("Booking Success Rate", f"{success_rate:.1f}%")
        
        with col2:
            avg_duration = 45  # Mock data
            st.metric("Avg. Appointment Duration", f"{avg_duration} min")
        
        with col3:
            response_time = 2.3  # Mock data
            st.metric("Avg. Response Time", f"{response_time}s")
            
    except Exception as e:
        st.error(f"Error loading analytics data: {e}")
        st.info("Analytics will be available once you have appointment data.")

# Footer with Dynamic Information
st.markdown("---")

# Get current conversation state for dynamic footer
if hasattr(st.session_state, 'agent') and st.session_state.conversation_started:
    conversation_state = st.session_state.agent.get_conversation_state()
    current_step = conversation_state.get('step', 'start')
    current_field = conversation_state.get('current_field', '')
    progress = conversation_state.get('progress', 0)
    
    # Get conversation stats
    msg_count = len(st.session_state.conversation_history) if st.session_state.conversation_history else 0
    user_msgs = len([m for m in st.session_state.conversation_history if m['type'] == 'user']) if st.session_state.conversation_history else 0
    
    # Generate context-sensitive hint
    hint_text = ""
    if current_step == 'patient_intake' and current_field:
        hints = {
            'name': "💡 Please provide your full name (first and last name)",
            'phone': "💡 Please provide your phone number (10 digits)",
            'email': "💡 Please provide your email address",
            'dob': "💡 Please provide your date of birth (MM/DD/YYYY)"
        }
        hint_text = hints.get(current_field, "")
    elif current_step == 'emr_lookup':
        hint_text = "🔍 We're searching our records for your information..."
    elif current_step == 'scheduling':
        hint_text = "📅 Specify your appointment preferences (time, doctor, etc.)"
    elif current_step == 'scheduling_doctor_select':
        hint_text = "�‍⚕️ Choose your preferred doctor from the list above"
    elif current_step == 'scheduling_confirm':
        hint_text = "✅ Review and confirm your appointment details"
    elif current_step == 'insurance':
        if current_field == 'carrier':
            hint_text = "💳 Select your insurance from Quick Actions or type the name"
        elif current_field == 'member_id':
            hint_text = "💳 Enter your member ID or use Quick Actions if you don't have it"
        else:
            hint_text = "💳 Please provide your insurance information"
    elif current_step == 'confirmation':
        hint_text = "✅ Your appointment is being finalized..."
    elif current_step == 'complete':
        hint_text = "🎉 Appointment booking complete! Use Reset Chat to book another"
    
    # Generate step information
    step_names = {
        'start': 'Getting Started',
        'patient_intake': 'Patient Information',
        'emr_lookup': 'Medical Records Search',
        'scheduling': 'Appointment Scheduling',
        'scheduling_doctor_select': 'Doctor Selection',
        'scheduling_confirm': 'Confirming Time',
        'insurance': 'Insurance Verification',
        'confirmation': 'Final Confirmation',
        'complete': 'Booking Complete'
    }
    
    current_step_name = step_names.get(current_step, 'In Progress')
    
    # Display dynamic footer
    progress_percent = f"{progress:.0f}"
    footer_html = f'''
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1rem; border-radius: 10px; margin: 1rem 0; text-align: center;">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
            <div style="flex: 1; min-width: 200px;">
                <strong>Progress:</strong> {current_step_name}<br>
                <div style="background: rgba(255,255,255,0.2); border-radius: 10px; height: 8px; margin: 5px 0;">
                    <div style="background: #4CAF50; height: 100%; border-radius: 10px; width: {progress}%; transition: width 0.3s;"></div>
                </div>
                <small>{progress_percent}% Complete</small>
            </div>
            <div style="flex: 2; min-width: 300px; margin: 0 1rem;">
                <div style="background: rgba(255,255,255,0.1); padding: 0.5rem; border-radius: 8px;">
                    {hint_text}
                </div>
            </div>
            <div style="flex: 1; min-width: 150px; text-align: right;">
                <strong>Conversation:</strong><br>
                <small>{msg_count} messages - {user_msgs} from you</small><br>
                <small>LangGraph + LangChain</small>
            </div>
        </div>
    </div>
    '''
    st.markdown(footer_html, unsafe_allow_html=True)
else:
    # Static footer when no conversation is started
    static_footer_html = '''
    <div style="text-align: center; color: #666; padding: 1rem; background: rgba(0,0,0,0.05); border-radius: 10px; margin: 1rem 0;">
        <p><strong>AI Scheduling Agent</strong> | Built with LangGraph + LangChain</p>
        <p>Features: Intelligent scheduling - Patient lookup - Automated reminders - Calendar integration</p>
        <p><strong>Get Started:</strong> Click "New Appointment" or type "Hello" to begin booking</p>
    </div>
    '''
    st.markdown(static_footer_html, unsafe_allow_html=True)

# Floating Help Widget & Notifications temporarily removed due to syntax issues

# End of file

