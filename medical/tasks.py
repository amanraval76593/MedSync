from datetime import datetime
from django.core.mail import send_mail
from celery import shared_task
from django.utils.timezone import localtime,make_aware

# @shared_task
def send_visit_reminder(patient_email, doctor_name, visit_time, notes):
    subject = "Upcoming Appointment Reminder"
    if isinstance(visit_time, str):
        visit_time_obj = datetime.fromisoformat(visit_time)  # or use strptime for custom format
    else:
        visit_time_obj = visit_time  # already datetime

    # Ensure it's timezone-aware
    if visit_time_obj.tzinfo is None:
        visit_time_obj = make_aware(visit_time_obj)

    message = (
        f"Hello,\n\n"
        f"This is a reminder for your appointment with Dr. {doctor_name}.\n"
        f"Scheduled Time: {localtime(visit_time_obj).strftime('%Y-%m-%d %H:%M')}\n"
        f"Notes: {notes or 'N/A'}\n\n"
        f"Please be on time.\n\n"
        f"Regards,\nMedical App Team"
    )
    try:
        print(f"Sending email to: {patient_email}, Subject: {subject}, Message: {message}")
        send_mail(
            subject,
            message,
            None,
            [patient_email],
            fail_silently=False,
        )
    except Exception as e:
        print(f"Error sending email: {e}")
