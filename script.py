from flask import Flask, request, jsonify
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import smtplib
from email.mime.text import MIMEText
from twilio.rest import Client

app = Flask(__name__)

# Google Sheets API Setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open("Boxing Club Leads").sheet1

# Telegram Bot Token
TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
TELEGRAM_CHAT_ID = "YOUR_TELEGRAM_CHAT_ID"

# Email Config
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_USER = "your_email@gmail.com"
EMAIL_PASSWORD = "your_password"

# Twilio WhatsApp API
TWILIO_ACCOUNT_SID = "YOUR_TWILIO_SID"
TWILIO_AUTH_TOKEN = "YOUR_TWILIO_AUTH_TOKEN"
TWILIO_WHATSAPP_NUMBER = "whatsapp:+YOUR_TWILIO_NUMBER"

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    requests.post(url, json=payload)

def send_email(to_email, subject, message):
    msg = MIMEText(message)
    msg["Subject"] = subject
    msg["From"] = EMAIL_USER
    msg["To"] = to_email
    
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(EMAIL_USER, EMAIL_PASSWORD)
    server.sendmail(EMAIL_USER, to_email, msg.as_string())
    server.quit()

def send_whatsapp_message(to_number, message):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    client.messages.create(
        from_=TWILIO_WHATSAPP_NUMBER,
        body=message,
        to=f"whatsapp:{to_number}"
    )

@app.route("/new_lead", methods=["POST"])
def new_lead():
    data = request.json
    name = data.get("name")
    phone = data.get("phone")
    email = data.get("email")
    city = data.get("city")
    training_type = data.get("training_type")
    
    # Save to Google Sheets
    sheet.append_row([name, phone, email, city, training_type])
    
    # Send Telegram Notification
    send_telegram_message(f"Новая заявка: {name}, {phone}, {email}, Город: {city}, Тренировка: {training_type}")
    
    # Send Auto Email
    send_email(email, "Добро пожаловать в наш боксерский клуб!", f"Спасибо за вашу заявку! Город: {city}, Тип тренировки: {training_type}.")
    
    # Send WhatsApp Message
    send_whatsapp_message(phone, f"Спасибо за вашу заявку! Город: {city}, Тренировка: {training_type}. Мы свяжемся с вами в ближайшее время.")
    
    return jsonify({"status": "success"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
