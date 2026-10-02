import time
import base64
from pathlib import Path
import pandas as pd
import streamlit as st

from sentiment_service import calculate_app_statistics, classify_sentiment
from ai_service import ask_dating_ai
from firebase_auth import login_user, register_user

st.set_page_config(
    page_title="Dating App Lifestyle Matcher",
    page_icon="💘",
    layout="centered",
    initial_sidebar_state="collapsed",
)

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""

def get_bg_image():
    path = Path(__file__).parent / "Gemini_Generated_Image_vmu55bvmu55bvmu5.jpg"
    if path.exists():
        return base64.b64encode(path.read_bytes()).decode()
    return None

BG_IMAGE = get_bg_image()

bg_css = f"""
<style>
.stApp {{
  background-color: #fff5f7;
  {f"background-image: linear-gradient(rgba(255, 245, 247, 0.85), rgba(255, 235, 240, 0.9)), url('data:image/png;base64,{BG_IMAGE}');" if BG_IMAGE else ""}
  background-size: cover;
  background-position: center;
  background-attachment: fixed;
  color: #4a3b40;
}}

header[data-testid="stHeader"] {{
  background: transparent !important;
}}
[data-testid="stMain"] {{
  background: transparent !important;
}}

h3, h2 {{
  color: #c73860;
  font-weight: 700;
  text-shadow: 0 2px 5px rgba(255, 182, 193, 0.4);
}}

/* ปรับสีตัวหนังสือในแท็บ (Tabs) ให้มองเห็นชัดเจนทั้งตอนเลือกและยังไม่เลือก */
.stTabs [data-baseweb="tab"] {{
  color: #8c5865 !important;
  font-weight: 600;
}}
.stTabs [data-baseweb="tab"] p {{
  color: #8c5865 !important;
}}
.stTabs [data-baseweb="tab"][aria-selected="true"] {{
  color: #c73860 !important;
  border-bottom-color: #c73860 !important;
}}
.stTabs [data-baseweb="tab"][aria-selected="true"] p {{
  color: #c73860 !important;
}}

div[data-testid="stChatMessage"] {{
  background-color: #ffffff !important;
  border: 1px solid rgba(255, 182, 193, 0.8);
  border-radius: 20px;
  padding: 14px;
  box-shadow: 0 4px 15px rgba(255, 182, 193, 0.25);
}}

div[data-testid="stChatMessage"] p, 
div[data-testid="stChatMessage"] span, 
div[data-testid="stChatMessage"] div {{
  color: #3b2d32 !important;
}}

div[data-testid="stChatInput"] {{
  background-color: #ffffff !important;
  border-radius: 25px !important;
  border: 2px solid #ffb3c6 !important;
  padding: 4px;
  box-shadow: 0 4px 15px rgba(255, 182, 193, 0.4);
}}

div[data-testid="stChatInput"] textarea {{
  background-color: transparent !important;
  color: #8c6870 !important;
  -webkit-text-fill-color: #8c6870 !important;
  caret-color: #c73860;
  font-weight: 500;
}}

div[data-testid="stChatInput"] textarea::placeholder {{
  color: #8c6870 !important;
  -webkit-text-fill-color: #8c6870 !important;
}}

div[data-testid="stChatInput"] button {{
  color: #ffffff !important;
  background-color: #ff6584 !important;
  border-radius: 50% !important;
}}
div[data-testid="stChatInput"] button:hover {{
  background-color: #d94e71 !important;
}}
</style>
"""

st.markdown(bg_css, unsafe_allow_html=True)

# หน้าจอเข้าสู่ระบบ / สมัครสมาชิก
if not st.session_state.authenticated:
    st.markdown("<h2 style='text-align: center;'>💘 Dating App Matcher - เข้าสู่ระบบ</h2>", unsafe_allow_html=True)
    
    tab_login, tab_register = st.tabs(["🔐 เข้าสู่ระบบ", "📝 สมัครสมาชิก"])
    
    with tab_login:
        st.write("กรุณากรอกอีเมลและรหัสผ่านเพื่อเข้าใช้งานระบบ")
        login_email = st.text_input("อีเมล", key="login_email")
        login_password = st.text_input("รหัสผ่าน", type="password", key="login_password")
        
        if st.button("เข้าสู่ระบบ", use_container_width=True):
            try:
                res = login_user(login_email, login_password)
                st.session_state.authenticated = True
                st.session_state.user_email = res.get("email", login_email)
                st.success("เข้าสู่ระบบสำเร็จ!")
                time.sleep(0.8)
                st.rerun()
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาด: {e}")

    with tab_register:
        st.write("สร้างบัญชีผู้ใช้งานใหม่ (รหัสผ่านต้องมีอย่างน้อย 6 ตัวอักษร)")
        reg_email = st.text_input("อีเมล", key="reg_email")
        reg_password = st.text_input("รหัสผ่าน", type="password", key="reg_password")
        
        if st.button("สมัครสมาชิก", use_container_width=True):
            try:
                register_user(reg_email, reg_password)
                st.success("สมัครสมาชิกสำเร็จ! สามารถสลับไปที่แท็บ 'เข้าสู่ระบบ' เพื่อใช้งานได้เลยครับ")
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาด: {e}")
                
    st.stop()

@st.cache_data
def load_data():
    dfs = []
    if Path("DatingAppReviewsDataset_p1.csv.xlsx").exists():
        dfs.append(pd.read_excel("DatingAppReviewsDataset_p1.csv.xlsx"))
    for i in range(2, 6):
        csv_path = f"DatingAppReviewsDataset_p{i}.csv"
        if Path(csv_path).exists():
            dfs.append(pd.read_csv(csv_path))
            
    if not dfs:
        raise FileNotFoundError("ไม่พบไฟล์ข้อมูลพาร์ทย่อยในโปรเจกต์")
        
    df = pd.concat(dfs, ignore_index=True)
    df['Sentiment'] = df['Rating'].apply(classify_sentiment)
    return df

with st.spinner("กำลังเตรียมระบบวิเคราะห์ข้อมูลรีวิว..."):
    try:
        df = load_data()
    except Exception as e:
        st.error(f"ไม่พบไฟล์ข้อมูลในโปรเจกต์: {e}")
        st.stop()

stats, processed_df = calculate_app_statistics(df)

st.sidebar.success(f"เข้าสู่ระบบด้วย: {st.session_state.user_email}")
if st.sidebar.button("ออกจากระบบ"):
    st.session_state.authenticated = False
    st.session_state.user_email = ""
    st.rerun()

st.markdown("""
### 💘 Dating App Lifestyle Matcher Bot
เล่าไลฟ์สไตล์ นิสัย หรือเป้าหมายในการหาคู่ของคุณให้ผมฟังได้เลยครับ แล้วผมจะวิเคราะห์จากรีวิวผู้ใช้งานจริง (Tinder, Bumble, Hinge) มาแนะนำว่าคุณเหมาะกับแอปไหน พร้อมสรุปรีวิวให้ฟังครับ!
""")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "สวัสดีครับ! ลองพิมพ์เล่าสั้นๆ ได้เลยครับว่าตัวตนและไลฟ์สไตล์ของคุณเป็นแบบไหน และกำลังมองหาความสัมพันธ์แบบใด (เช่น 'เป็นคนทำงานยุ่งๆ ชอบคนจริงจัง ไม่ชอบปัดเจอคนเล่นๆ', 'ชอบแนวสายฝอ ไลฟ์สไตล์คาเฟ่ ปาร์ตี้', หรือ 'ชอบคุยเปิดประเด็นยาวๆ') แล้วผมจะเลือกแอปที่ใช่มาให้ครับ"}
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if user_prompt := st.chat_input("พิมพ์เล่าไลฟ์สไตล์และความต้องการของคุณที่นี่..."):
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    with st.chat_message("assistant"):
        with st.spinner("กำลังวิเคราะห์ไลฟ์สไตล์และเปรียบเทียบรีวิวจากทั้ง 3 แอป..."):
            try:
                sample_tinder = processed_df[processed_df["App"] == "Tinder"]["Review"].dropna().sample(min(5, len(processed_df[processed_df["App"] == "Tinder"]))).tolist() if len(processed_df[processed_df["App"] == "Tinder"]) > 0 else []
                sample_bumble = processed_df[processed_df["App"] == "Bumble"]["Review"].dropna().sample(min(5, len(processed_df[processed_df["App"] == "Bumble"]))).tolist() if len(processed_df[processed_df["App"] == "Bumble"]) > 0 else []
                sample_hinge = processed_df[processed_df["App"] == "Hinge"]["Review"].dropna().sample(min(5, len(processed_df[processed_df["App"] == "Hinge"]))).tolist() if len(processed_df[processed_df["App"] == "Hinge"]) > 0 else []
                
                all_samples = f"--- Tinder Reviews ---\n" + "\n".join(sample_tinder) + \
                              f"\n\n--- Bumble Reviews ---\n" + "\n".join(sample_bumble) + \
                              f"\n\n--- Hinge Reviews ---\n" + "\n".join(sample_hinge)

                stats_summary = f"Tinder (Avg Rating: {stats.get('Tinder', {}).get('avg_rating', 0):.2f}, Pos: {stats.get('Tinder', {}).get('positive_pct', 0):.1f}%), " \
                                f"Bumble (Avg Rating: {stats.get('Bumble', {}).get('avg_rating', 0):.2f}, Pos: {stats.get('Bumble', {}).get('positive_pct', 0):.1f}%), " \
                                f"Hinge (Avg Rating: {stats.get('Hinge', {}).get('avg_rating', 0):.2f}, Pos: {stats.get('Hinge', {}).get('positive_pct', 0):.1f}%)"

                matching_prompt = f"""
ผู้ใช้งานพิมพ์เล่าไลฟ์สไตล์และความต้องการมาดังนี้: "{user_prompt}"

ข้อมูลสถิติของแอปทั้ง 3 (Tinder, Bumble, Hinge): {stats_summary}

ตัวอย่างรีวิวจากผู้ใช้งานจริง:
{all_samples}

คำชี้แจงในการตอบ:
1. วิเคราะห์ว่าจากไลฟ์สไตล์และความต้องการของผู้ใช้ **แอปพลิเคชันใด (Tinder, Bumble หรือ Hinge)** ที่เหมาะสมที่สุด พร้อมให้เหตุผลว่าทำไม
2. สรุปภาพรวมรีวิว (จุดเด่นและข้อควรระวัง) ของแอปที่แนะนำนั้นจากข้อมูลรีวิวจริง
3. แนะนำเสริมว่าถ้าอยากลองแอปอื่นในกลุ่ม มีข้อดีข้อเสียต่างกันอย่างไร
4. ตอบเป็นภาษาไทยด้วยน้ำเสียงที่เป็นกันเองและน่าเชื่อถือ
"""

                response_text = ask_dating_ai(matching_prompt, "All Apps (Tinder, Bumble, Hinge)", {"total_reviews": len(df), "avg_rating": 3.0, "positive_pct": 45, "neutral_pct": 10, "negative_pct": 45, "total_thumbs": 1000}, all_samples)
                
                st.markdown(response_text)
                st.session_state.messages.append({"role": "assistant", "content": response_text})
            except Exception as e:
                err_msg = f"ขออภัยครับ เกิดข้อผิดพลาดในการประมวลผล: {e} (แนะนำให้ลองใหม่อีกครั้ง)"
                st.error(err_msg)
                st.session_state.messages.append({"role": "assistant", "content": err_msg})