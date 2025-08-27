from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr
from neondb import insert_enquiry, create_enquiry_table
import os
import requests
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# ✅ Secure CORS config — allow your real domain only
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://snapsecuretechnologies.com",
        "https://snap-frontend-ten.vercel.app",
        "https://snap-frontend-re7qlqu7g-snapsecures-projects.vercel.app",
        "https://www.snapsecuretechnologies.com",
        "https://snap-frontend-snapsecures-projects.vercel.app/",
        "https://snap-frontend-git-main-snapsecures-projects.vercel.app/",
        "https://snap-frontend-puyqyduin-snapsecures-projects.vercel.app/",
        "http://192.168.29.127:3000"
    ],
    allow_credentials=True,
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["*"],
)

# ✅ Pydantic schema
class Enquiry(BaseModel):
    name: str
    email: EmailStr
    phone_number: str
    message: str

# ✅ Telegram Notification Function
def notify_telegram(enquiry):
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ Telegram credentials not set")
        return

    message = (
        f"📩 New Enquiry Received\n\n"
        f"👤 Name: {enquiry.name}\n"
        f"📧 Email: {enquiry.email}\n"
        f"📞 Phone: {enquiry.phone_number}\n"
        f"📝 Message: {enquiry.message}"
    )

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}

    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print("✅ Telegram notification sent")
        else:
            print(f"❌ Telegram error: {response.text}")
    except Exception as e:
        print(f"❌ Telegram exception: {e}")

@app.get("/")
def root():
    return {"status": "API live"}

@app.on_event("startup")
def startup_event():
    create_enquiry_table()

@app.post("/enquiry")
def submit_enquiry(enquiry: Enquiry):
    try:
        print("📩 Received enquiry:", enquiry)

        # Save to DB
        insert_enquiry(
            name=enquiry.name,
            email=enquiry.email,
            phone=enquiry.phone_number,
            message=enquiry.message
        )

        # Telegram notification
        notify_telegram(enquiry)

        return {"message": "✅ Enquiry submitted successfully"}

    except Exception as e:
        print("❌ Enquiry submission failed:", str(e))  # Show the real issue
        raise HTTPException(status_code=500, detail="Internal Server Error")
