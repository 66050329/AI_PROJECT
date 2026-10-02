import os
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# ปรับวิธีดึงค่าให้ปลอดภัยและไม่พังทันทีถ้าหาไม่เจอ
API_KEY = ""
try:
    if "FIREBASE_API_KEY" in st.secrets:
        API_KEY = st.secrets["FIREBASE_API_KEY"].strip()
except Exception:
    pass

if not API_KEY:
    API_KEY = os.getenv("FIREBASE_API_KEY", "").strip()

BASE_URL = "https://identitytoolkit.googleapis.com/v1/accounts"

ERROR_MESSAGES = {
    "EMAIL_EXISTS": "อีเมลนี้ถูกสมัครไว้แล้ว",
    "OPERATION_NOT_ALLOWED": "Firebase ยังไม่ได้เปิด Email/Password sign-in",
    "TOO_MANY_ATTEMPTS_TRY_LATER": "มีการลองหลายครั้งเกินไป กรุณารอสักครู่แล้วลองใหม่",
    "EMAIL_NOT_FOUND": "ไม่พบบัญชีผู้ใช้นี้",
    "INVALID_PASSWORD": "รหัสผ่านไม่ถูกต้อง",
    "INVALID_LOGIN_CREDENTIALS": "อีเมลหรือรหัสผ่านไม่ถูกต้อง",
    "USER_DISABLED": "บัญชีนี้ถูกระงับการใช้งาน",
    "WEAK_PASSWORD": "รหัสผ่านต้องมีอย่างน้อย 6 ตัวอักษร",
    "INVALID_EMAIL": "รูปแบบอีเมลไม่ถูกต้อง",
}

def _ensure_key():
    if not API_KEY:
        raise RuntimeError("ไม่พบ FIREBASE_API_KEY กรุณาตรวจสอบการตั้งค่า Secrets บน Streamlit Cloud อีกครั้ง")

def _post(action, email, password):
    _ensure_key()
    url = f"{BASE_URL}:{action}?key={API_KEY}"
    response = requests.post(
        url,
        json={"email": email, "password": password, "returnSecureToken": True},
        timeout=20,
    )
    data = response.json()
    if response.ok:
        return data

    code = data.get("error", {}).get("message", "FIREBASE_AUTH_ERROR")
    short_code = code.split(" : ", 1)[0]
    raise RuntimeError(ERROR_MESSAGES.get(short_code, code))

def register_user(email, password):
    return _post("signUp", email.strip(), password)

def login_user(email, password):
    return _post("signInWithPassword", email.strip(), password)