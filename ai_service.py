import os, time
import pandas as pd
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")

def ask_dating_ai(question, app_name, stats, sample_reviews):
    if not KEY:
        raise ValueError("Missing GEMINI_API_KEY in .env")
    
    context = f"""Dating App Analytics Context:
App: {app_name}
Total Reviews Analyzed: {stats['total_reviews']:,}
Average Rating: {stats['avg_rating']:.2f} / 5.00
Positive Sentiment: {stats['positive_pct']:.1f}%
Neutral Sentiment: {stats['neutral_pct']:.1f}%
Negative Sentiment: {stats['negative_pct']:.1f}%
Total Thumbs Up on reviews: {stats['total_thumbs']:,}

Sample User Reviews:
{sample_reviews}"""

    prompt = f"""{context}

Question: {question}

คำชี้แจง:
- อธิบายเป็นภาษาไทยโดยอ้างอิงจากข้อมูลสถิติและตัวอย่างรีวิวที่กำหนดเท่านั้น
- สรุปประเด็นจุดเด่น (Pros) และข้อควรระวัง/ข้อเสีย (Cons) ให้ชัดเจน
- ห้ามใส่คำแนะนำหรือการันตีเกินจริง นำเสนอตามเนื้อหาจริงจากชุดข้อมูล"""

    client = genai.Client(api_key=KEY)
    last = None
    for delay in [0, 2, 4]:
        if delay: time.sleep(delay)
        try:
            res = client.models.generate_content(
                model=MODEL, contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction="You are an expert dating app market researcher and data analyst.",
                    temperature=0.25
                )
            )
            return res.text
        except Exception as e:
            last = e
            if "503" not in str(e) and "UNAVAILABLE" not in str(e): raise
    raise last