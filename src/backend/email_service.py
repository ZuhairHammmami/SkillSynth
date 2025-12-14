# src/backend/email_service.py

import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# تأكد من أن مكتبة python-dotenv مثبتة وأن load_dotenv() يتم استدعاؤها
# في مكان ما عند بدء التشغيل (ملف database.py يفعل ذلك بالفعل)

def send_password_reset_email(recipient_email: str, reset_link: str):
    """
    يرسل بريدًا إلكترونيًا لإعادة تعيين كلمة المرور باستخدام SendGrid.
    يقرأ مفتاح API بشكل آمن من متغيرات البيئة.
    """
    sendgrid_api_key = os.getenv("SENDGRID_API_KEY")

    if not sendgrid_api_key:
        print("ERROR: SENDGRID_API_KEY is not set in the .env file.")
        # في تطبيق حقيقي، قد ترسل تنبيهًا هنا
        return False

    # ملاحظة مهمة: هذا البريد يجب أن يكون موثقًا كـ "Single Sender" في حسابك على SendGrid
    from_email = 'zuhairprogramer@gmail.com' 

    message = Mail(
        from_email=from_email,
        to_emails=recipient_email,
        subject='[SkillSynth] Password Reset Request',
        html_content=f"""
        <div style="font-family: sans-serif; text-align: center; padding: 20px;">
            <h2>Password Reset Request</h2>
            <p>We received a request to reset the password for your SkillSynth account.</p>
            <p>Please click the button below to set a new password. This link is valid for 15 minutes.</p>
            <a href="{reset_link}" 
               style="background-color: #007bff; color: white; padding: 15px 25px; text-align: center; text-decoration: none; display: inline-block; border-radius: 5px; font-size: 16px;">
               Reset Password
            </a>
            <p style="margin-top: 20px; font-size: 12px; color: #888;">
                If you did not request a password reset, please ignore this email.
            </p>
        </div>
        """
    )
    
    try:
        sg = SendGridAPIClient(sendgrid_api_key)
        response = sg.send(message)
        
        # استجابة 202 تعني أن SendGrid قبل الطلب بنجاح
        if response.status_code == 202:
            print(f"INFO: Password reset email successfully queued for {recipient_email}")
            return True
        else:
            print(f"ERROR: Failed to send email via SendGrid. Status: {response.status_code}")
            print(f"Body: {response.body}")
            return False
    except Exception as e:
        print(f"ERROR: An exception occurred while sending email with SendGrid: {e}")
        return False