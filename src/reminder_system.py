import smtplib
import schedule  # type: ignore
import time
import os
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Dict, List, Optional
import pandas as pd  # type: ignore
from dotenv import load_dotenv  # type: ignore

load_dotenv()

class ReminderSystem:
    def __init__(self):
        self.email_user = os.getenv('EMAIL_USER', '')
        self.email_password = os.getenv('EMAIL_PASSWORD', '')
        self.smtp_server = 'smtp.gmail.com'
        self.smtp_port = 587
        
    def send_email(self, to_email: str, subject: str, body: str, attachment_path: Optional[str] = None) -> bool:
        """Send email with optional attachment"""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email_user
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add body to email
            msg.attach(MIMEText(body, 'html'))
            
            # Add attachment if provided
            if attachment_path and os.path.exists(attachment_path):
                with open(attachment_path, "rb") as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                    
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {os.path.basename(attachment_path)}'
                )
                msg.attach(part)
            
            # Gmail SMTP configuration
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_user, self.email_password)
            
            text = msg.as_string()
            server.sendmail(self.email_user, to_email, text)
            server.quit()
            
            return True
            
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    def send_appointment_confirmation(self, appointment_data: Dict) -> bool:
        """Send appointment confirmation email"""
        subject = "Appointment Confirmation - Healthcare Center"
        
        body = f"""
        <html>
        <head></head>
        <body>
            <h2>Appointment Confirmation</h2>
            <p>Dear {appointment_data['patient_name']},</p>
            
            <p>Your appointment has been successfully scheduled. Here are the details:</p>
            
            <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <p><strong>Confirmation Number:</strong> {appointment_data['appointment_id']}</p>
                <p><strong>Doctor:</strong> {appointment_data['doctor']}</p>
                <p><strong>Date:</strong> {appointment_data['date']}</p>
                <p><strong>Time:</strong> {appointment_data['time']}</p>
                <p><strong>Duration:</strong> {appointment_data['duration']} minutes</p>
            </div>
            
            <h3>Important Reminders:</h3>
            <ul>
                <li>Please arrive 15 minutes early for check-in</li>
                <li>Bring a valid photo ID and insurance card</li>
                <li>Complete any required forms before your visit</li>
                <li>If you need to cancel or reschedule, please call us at least 24 hours in advance</li>
            </ul>
            
            <p>You will receive reminder notifications closer to your appointment date.</p>
            
            <p>Thank you for choosing our healthcare services!</p>
            
            <p>Best regards,<br>
            Healthcare Center Team<br>
            Phone: (555) 123-4567<br>
            Email: appointments@healthcarecenter.com</p>
        </body>
        </html>
        """
        
        return self.send_email(appointment_data['patient_email'], subject, body)
    
    def send_appointment_reminder(self, appointment_data: Dict, reminder_type: str = '24hour') -> bool:
        """Send appointment reminder email"""
        if reminder_type == '24hour':
            subject = "Appointment Reminder - Tomorrow"
            time_msg = "tomorrow"
        else:
            subject = "Appointment Reminder - Today"
            time_msg = "today"
        
        body = f"""
        <html>
        <head></head>
        <body>
            <h2>Appointment Reminder</h2>
            <p>Dear {appointment_data['patient_name']},</p>
            
            <p>This is a friendly reminder that you have an appointment <strong>{time_msg}</strong>.</p>
            
            <div style="background-color: #e6f3ff; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <p><strong>Confirmation Number:</strong> {appointment_data['appointment_id']}</p>
                <p><strong>Doctor:</strong> {appointment_data['doctor']}</p>
                <p><strong>Date:</strong> {appointment_data['date']}</p>
                <p><strong>Time:</strong> {appointment_data['time']}</p>
            </div>
            
            <h3>Please Remember:</h3>
            <ul>
                <li>Arrive 15 minutes early for check-in</li>
                <li>Bring your photo ID and insurance card</li>
                <li>Complete any required forms</li>
            </ul>
            
            <p>If you need to cancel or reschedule, please call us at (555) 123-4567.</p>
            
            <p>Thank you!</p>
            
            <p>Healthcare Center Team</p>
        </body>
        </html>
        """
        
        return self.send_email(appointment_data['patient_email'], subject, body)
    
    def send_intake_form(self, patient_data: Dict, form_path: Optional[str] = None) -> bool:
        """Send patient intake form"""
        subject = "Patient Intake Form - Please Complete Before Your Visit"
        
        body = f"""
        <html>
        <head></head>
        <body>
            <h2>Patient Intake Form</h2>
            <p>Dear {patient_data['name']},</p>
            
            <p>Thank you for scheduling your appointment with us. To help us provide you with the best possible care, 
            please complete the attached intake form and bring it with you to your appointment.</p>
            
            <div style="background-color: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <p><strong>Instructions:</strong></p>
                <ul>
                    <li>Print and complete the attached form</li>
                    <li>Bring the completed form to your appointment</li>
                    <li>If you have any questions, please call us at (555) 123-4567</li>
                </ul>
            </div>
            
            <p>The form includes sections for:</p>
            <ul>
                <li>Personal and contact information</li>
                <li>Medical history</li>
                <li>Current medications</li>
                <li>Insurance information</li>
                <li>Emergency contacts</li>
            </ul>
            
            <p>We look forward to seeing you soon!</p>
            
            <p>Best regards,<br>
            Healthcare Center Team</p>
        </body>
        </html>
        """
        
        # Use the provided PDF form or create a default path
        if not form_path:
            form_path = "/Users/tanishpd/Downloads/New Patient Intake Form.pdf"
        
        return self.send_email(patient_data['email'], subject, body, form_path)
    
    def schedule_appointment_reminders(self, appointment_data: Dict):
        """Schedule automated reminders for an appointment"""
        appointment_datetime = datetime.strptime(
            f"{appointment_data['date']} {appointment_data['time']}", 
            "%Y-%m-%d %H:%M"
        )
        
        # Schedule 24-hour reminder
        reminder_24h = appointment_datetime - timedelta(hours=24)
        if reminder_24h > datetime.now():
            schedule.every().day.at(reminder_24h.strftime("%H:%M")).do(
                self.send_appointment_reminder, 
                appointment_data=appointment_data, 
                reminder_type='24hour'
            ).tag(f"reminder_24h_{appointment_data['appointment_id']}")
        
        # Schedule 2-hour reminder
        reminder_2h = appointment_datetime - timedelta(hours=2)
        if reminder_2h > datetime.now():
            schedule.every().day.at(reminder_2h.strftime("%H:%M")).do(
                self.send_appointment_reminder, 
                appointment_data=appointment_data, 
                reminder_type='2hour'
            ).tag(f"reminder_2h_{appointment_data['appointment_id']}")
    
    def check_and_send_reminders(self):
        """Check for upcoming appointments and send reminders"""
        try:
            # Load appointments
            appointments_df = pd.read_csv('data/appointments.csv')
            
            if appointments_df.empty:
                return
            
            now = datetime.now()
            
            for _, appointment in appointments_df.iterrows():
                if appointment['status'] != 'Confirmed':
                    continue
                
                appointment_datetime = datetime.strptime(
                    f"{appointment['date']} {appointment['time']}", 
                    "%Y-%m-%d %H:%M"
                )
                
                hours_until = (appointment_datetime - now).total_seconds() / 3600
                
                # Send 24-hour reminder
                if 23 <= hours_until <= 25:
                    appointment_dict = appointment.to_dict()
                    self.send_appointment_reminder(appointment_dict, '24hour')
                
                # Send 2-hour reminder
                elif 1.5 <= hours_until <= 2.5:
                    appointment_dict = appointment.to_dict()
                    self.send_appointment_reminder(appointment_dict, '2hour')
        
        except Exception as e:
            print(f"Error checking reminders: {e}")
    
    def start_reminder_service(self):
        """Start the automated reminder service"""
        # Schedule reminder checks every hour
        schedule.every().hour.do(self.check_and_send_reminders)
        
        print("Reminder service started. Checking for reminders every hour...")
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def send_cancellation_notification(self, appointment_data: Dict) -> bool:
        """Send appointment cancellation notification"""
        subject = "Appointment Cancellation Confirmation"
        
        body = f"""
        <html>
        <head></head>
        <body>
            <h2>Appointment Cancellation</h2>
            <p>Dear {appointment_data['patient_name']},</p>
            
            <p>This email confirms that your appointment has been cancelled:</p>
            
            <div style="background-color: #f8d7da; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <p><strong>Cancelled Appointment:</strong></p>
                <p><strong>Doctor:</strong> {appointment_data['doctor']}</p>
                <p><strong>Date:</strong> {appointment_data['date']}</p>
                <p><strong>Time:</strong> {appointment_data['time']}</p>
            </div>
            
            <p>If you would like to schedule a new appointment, please contact us at:</p>
            <ul>
                <li>Phone: (555) 123-4567</li>
                <li>Email: appointments@healthcarecenter.com</li>
            </ul>
            
            <p>Thank you!</p>
            
            <p>Healthcare Center Team</p>
        </body>
        </html>
        """
        
        return self.send_email(appointment_data['patient_email'], subject, body)
    
    def send_rescheduling_notification(self, old_appointment: Dict, new_appointment: Dict) -> bool:
        """Send appointment rescheduling notification"""
        subject = "Appointment Rescheduled - New Details"
        
        body = f"""
        <html>
        <head></head>
        <body>
            <h2>Appointment Rescheduled</h2>
            <p>Dear {new_appointment['patient_name']},</p>
            
            <p>Your appointment has been successfully rescheduled. Here are the updated details:</p>
            
            <div style="background-color: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <p><strong>Previous Appointment:</strong></p>
                <p>Date: {old_appointment['date']} at {old_appointment['time']}</p>
            </div>
            
            <div style="background-color: #d4edda; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <p><strong>New Appointment:</strong></p>
                <p><strong>Confirmation Number:</strong> {new_appointment['appointment_id']}</p>
                <p><strong>Doctor:</strong> {new_appointment['doctor']}</p>
                <p><strong>Date:</strong> {new_appointment['date']}</p>
                <p><strong>Time:</strong> {new_appointment['time']}</p>
            </div>
            
            <p>Please update your calendar and remember to arrive 15 minutes early.</p>
            
            <p>Thank you!</p>
            
            <p>Healthcare Center Team</p>
        </body>
        </html>
        """
        
        return self.send_email(new_appointment['patient_email'], subject, body)
    
    def get_email_templates(self) -> Dict:
        """Get available email templates"""
        return {
            'confirmation': 'Appointment confirmation with details',
            'reminder_24h': '24-hour appointment reminder',
            'reminder_2h': '2-hour appointment reminder',
            'intake_form': 'Patient intake form distribution',
            'cancellation': 'Appointment cancellation confirmation',
            'rescheduling': 'Appointment rescheduling notification'
        }
