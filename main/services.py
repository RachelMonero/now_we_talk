import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os


# sending email service
def email_service(receiver_email, subject, message):
    
    admin_email = "for.dev.practice@gmail.com"
    admin_password = "dqsr fqkb wuwp nxph"

    try:
        email_msg =MIMEMultipart()
        email_msg["From"] = admin_email
        email_msg["To"] = receiver_email
        email_msg["Subject"] = subject
        email_msg.attach(MIMEText(message,"plain"))
    
        server = smtplib.SMTP("smtp.gmail.com",587)
        server.starttls()
        server.login(admin_email, admin_password)
        server.sendmail(admin_email, receiver_email, email_msg.as_string())
        server.quit()
    except Exception as e:
        print(f"Failed to send email: {e}")    

# service to convert language code to language
def language_code_coversion(language):
    
    match language:
        case "ar":
            return "Arabic"
        case "bg":
            return "Bulgarian"
        case "zh-CN":
            return "Chinese (PRC)"
        case "zh-TW":
            return "Chinese (Taiwan)"
        case "nl":
            return "Dutch"
        case "en":
            return "English"
        case "fil":
            return "Filipino"
        case "fr":
            return "French"
        case "de":
            return "German"
        case "el":
            return "Greek"
        case "iw":
            return "Hebrew"
        case "hi":
            return "Hindi"
        case "hu":
            return "Hungarian"
        case "id":
            return "Indonesian"
        case "it":
            return "Italian"
        case "ja":
            return "Japanese"
        case "ko":
            return "Korean"
        case "ms":
            return "Malay"
        case "no":
            return "Norwegian"
        case "pl":
            return "Polish"
        case "pt-BR":
            return "Portugese (Brazil)"
        case "pt-PT":
            return "Portuguese (Portugal)"
        case "ro":
            return "Romanian"
        case "ru":
            return "Russian"
        case "es":
            return "Spanish"
        case "sv":
            return "Swedish"
        case "th":
            return "Thai"
        case "tr":
            return "Turkish"
        case "uk":
            return "Ukrainian"
        case "vi":
            return "Vietnamese"


