"""
Email templates for the AI Scheduling Agent
"""

def get_confirmation_template(appointment_data):
    """Get appointment confirmation email template"""
    return f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .header {{ background-color: #1f77b4; color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; }}
            .appointment-details {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; }}
            .footer {{ background-color: #6c757d; color: white; padding: 15px; text-align: center; }}
            .highlight {{ color: #1f77b4; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🏥 Appointment Confirmation</h1>
        </div>
        
        <div class="content">
            <p>Dear <span class="highlight">{appointment_data['patient_name']}</span>,</p>
            
            <p>Your appointment has been successfully scheduled. Here are the details:</p>
            
            <div class="appointment-details">
                <h3>📋 Appointment Details</h3>
                <p><strong>Confirmation Number:</strong> {appointment_data['appointment_id']}</p>
                <p><strong>Doctor:</strong> {appointment_data['doctor']}</p>
                <p><strong>Date:</strong> {appointment_data['date']}</p>
                <p><strong>Time:</strong> {appointment_data['time']}</p>
                <p><strong>Duration:</strong> {appointment_data['duration']} minutes</p>
            </div>
            
            <h3>📝 Important Reminders:</h3>
            <ul>
                <li>Please arrive <strong>15 minutes early</strong> for check-in</li>
                <li>Bring a valid <strong>photo ID</strong> and <strong>insurance card</strong></li>
                <li>Complete any required forms before your visit</li>
                <li>If you need to cancel or reschedule, please call us at least <strong>24 hours</strong> in advance</li>
            </ul>
            
            <div style="background-color: #d1ecf1; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <p><strong>📱 Reminder Notifications:</strong></p>
                <p>You will receive reminder notifications 24 hours and 2 hours before your appointment.</p>
            </div>
            
            <p>Thank you for choosing our healthcare services!</p>
        </div>
        
        <div class="footer">
            <p><strong>Healthcare Center</strong></p>
            <p>📞 Phone: (555) 123-4567 | 📧 Email: appointments@healthcarecenter.com</p>
            <p>🌐 Website: www.healthcarecenter.com</p>
        </div>
    </body>
    </html>
    """

def get_reminder_template(appointment_data, reminder_type='24hour'):
    """Get appointment reminder email template"""
    if reminder_type == '24hour':
        subject = "Appointment Reminder - Tomorrow"
        time_msg = "tomorrow"
        icon = "📅"
    else:
        subject = "Appointment Reminder - Today"
        time_msg = "today"
        icon = "⏰"
    
    return f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .header {{ background-color: #28a745; color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; }}
            .appointment-details {{ background-color: #e6f3ff; padding: 15px; border-radius: 5px; margin: 20px 0; }}
            .footer {{ background-color: #6c757d; color: white; padding: 15px; text-align: center; }}
            .highlight {{ color: #28a745; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>{icon} Appointment Reminder</h1>
        </div>
        
        <div class="content">
            <p>Dear <span class="highlight">{appointment_data['patient_name']}</span>,</p>
            
            <p>This is a friendly reminder that you have an appointment <strong>{time_msg}</strong>.</p>
            
            <div class="appointment-details">
                <h3>📋 Appointment Details</h3>
                <p><strong>Confirmation Number:</strong> {appointment_data['appointment_id']}</p>
                <p><strong>Doctor:</strong> {appointment_data['doctor']}</p>
                <p><strong>Date:</strong> {appointment_data['date']}</p>
                <p><strong>Time:</strong> {appointment_data['time']}</p>
            </div>
            
            <h3>📝 Please Remember:</h3>
            <ul>
                <li>Arrive <strong>15 minutes early</strong> for check-in</li>
                <li>Bring your <strong>photo ID</strong> and <strong>insurance card</strong></li>
                <li>Complete any required forms</li>
            </ul>
            
            <div style="background-color: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <p><strong>Need to Cancel or Reschedule?</strong></p>
                <p>Please call us at <strong>(555) 123-4567</strong> as soon as possible.</p>
            </div>
        </div>
        
        <div class="footer">
            <p><strong>Healthcare Center</strong></p>
            <p>📞 Phone: (555) 123-4567</p>
        </div>
    </body>
    </html>
    """

def get_intake_form_template(patient_data):
    """Get patient intake form email template"""
    return f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .header {{ background-color: #17a2b8; color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; }}
            .instructions {{ background-color: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0; }}
            .footer {{ background-color: #6c757d; color: white; padding: 15px; text-align: center; }}
            .highlight {{ color: #17a2b8; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📋 Patient Intake Form</h1>
        </div>
        
        <div class="content">
            <p>Dear <span class="highlight">{patient_data['name']}</span>,</p>
            
            <p>Thank you for scheduling your appointment with us. To help us provide you with the best possible care, 
            please complete the attached intake form and bring it with you to your appointment.</p>
            
            <div class="instructions">
                <h3>📝 Instructions:</h3>
                <ol>
                    <li>Print and complete the attached form</li>
                    <li>Bring the completed form to your appointment</li>
                    <li>If you have any questions, please call us at <strong>(555) 123-4567</strong></li>
                </ol>
            </div>
            
            <h3>📄 The form includes sections for:</h3>
            <ul>
                <li>Personal and contact information</li>
                <li>Medical history</li>
                <li>Current medications</li>
                <li>Insurance information</li>
                <li>Emergency contacts</li>
                <li>Reason for visit</li>
            </ul>
            
            <div style="background-color: #d1ecf1; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <p><strong>💡 Tip:</strong> Completing this form in advance will help reduce your wait time and ensure we have all the information needed for your care.</p>
            </div>
            
            <p>We look forward to seeing you soon!</p>
        </div>
        
        <div class="footer">
            <p><strong>Healthcare Center</strong></p>
            <p>📞 Phone: (555) 123-4567 | 📧 Email: appointments@healthcarecenter.com</p>
        </div>
    </body>
    </html>
    """

def get_cancellation_template(appointment_data):
    """Get appointment cancellation email template"""
    return f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .header {{ background-color: #dc3545; color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; }}
            .cancelled-details {{ background-color: #f8d7da; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #dc3545; }}
            .footer {{ background-color: #6c757d; color: white; padding: 15px; text-align: center; }}
            .highlight {{ color: #dc3545; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>❌ Appointment Cancellation</h1>
        </div>
        
        <div class="content">
            <p>Dear <span class="highlight">{appointment_data['patient_name']}</span>,</p>
            
            <p>This email confirms that your appointment has been <strong>cancelled</strong>:</p>
            
            <div class="cancelled-details">
                <h3>📋 Cancelled Appointment Details</h3>
                <p><strong>Confirmation Number:</strong> {appointment_data['appointment_id']}</p>
                <p><strong>Doctor:</strong> {appointment_data['doctor']}</p>
                <p><strong>Date:</strong> {appointment_data['date']}</p>
                <p><strong>Time:</strong> {appointment_data['time']}</p>
            </div>
            
            <h3>📞 Need to Schedule a New Appointment?</h3>
            <p>If you would like to schedule a new appointment, please contact us:</p>
            <ul>
                <li><strong>Phone:</strong> (555) 123-4567</li>
                <li><strong>Email:</strong> appointments@healthcarecenter.com</li>
                <li><strong>Online:</strong> Use our AI scheduling assistant</li>
            </ul>
            
            <div style="background-color: #d1ecf1; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <p><strong>🕐 Cancellation Policy:</strong> We appreciate at least 24 hours notice for cancellations to allow other patients to use the appointment slot.</p>
            </div>
        </div>
        
        <div class="footer">
            <p><strong>Healthcare Center</strong></p>
            <p>Thank you for informing us about the cancellation</p>
        </div>
    </body>
    </html>
    """

def get_rescheduling_template(old_appointment, new_appointment):
    """Get appointment rescheduling email template"""
    return f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .header {{ background-color: #ffc107; color: #212529; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; }}
            .old-appointment {{ background-color: #fff3cd; padding: 15px; border-radius: 5px; margin: 10px 0; border-left: 4px solid #ffc107; }}
            .new-appointment {{ background-color: #d4edda; padding: 15px; border-radius: 5px; margin: 10px 0; border-left: 4px solid #28a745; }}
            .footer {{ background-color: #6c757d; color: white; padding: 15px; text-align: center; }}
            .highlight {{ color: #ffc107; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🔄 Appointment Rescheduled</h1>
        </div>
        
        <div class="content">
            <p>Dear <span class="highlight">{new_appointment['patient_name']}</span>,</p>
            
            <p>Your appointment has been successfully <strong>rescheduled</strong>. Here are the updated details:</p>
            
            <div class="old-appointment">
                <h3>📅 Previous Appointment</h3>
                <p><strong>Date:</strong> {old_appointment['date']} at {old_appointment['time']}</p>
                <p><strong>Doctor:</strong> {old_appointment['doctor']}</p>
            </div>
            
            <div class="new-appointment">
                <h3>✅ New Appointment Details</h3>
                <p><strong>Confirmation Number:</strong> {new_appointment['appointment_id']}</p>
                <p><strong>Doctor:</strong> {new_appointment['doctor']}</p>
                <p><strong>Date:</strong> {new_appointment['date']}</p>
                <p><strong>Time:</strong> {new_appointment['time']}</p>
                <p><strong>Duration:</strong> {new_appointment['duration']} minutes</p>
            </div>
            
            <h3>📝 Important Reminders:</h3>
            <ul>
                <li>Please update your calendar with the new appointment time</li>
                <li>Arrive <strong>15 minutes early</strong> for check-in</li>
                <li>Bring your photo ID and insurance card</li>
            </ul>
            
            <div style="background-color: #d1ecf1; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <p><strong>📱 New Reminder Notifications:</strong></p>
                <p>You will receive new reminder notifications 24 hours and 2 hours before your rescheduled appointment.</p>
            </div>
        </div>
        
        <div class="footer">
            <p><strong>Healthcare Center</strong></p>
            <p>📞 Phone: (555) 123-4567</p>
        </div>
    </body>
    </html>
    """

# Template registry
EMAIL_TEMPLATES = {
    'confirmation': get_confirmation_template,
    'reminder_24h': lambda data: get_reminder_template(data, '24hour'),
    'reminder_2h': lambda data: get_reminder_template(data, '2hour'),
    'intake_form': get_intake_form_template,
    'cancellation': get_cancellation_template,
    'rescheduling': get_rescheduling_template
}
