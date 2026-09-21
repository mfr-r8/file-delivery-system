import streamlit as st
from utils.auth import init_session
from utils.students import search_student
from utils.statement import get_submission, record_submission
from utils.sheets import read_tab
from datetime import datetime

st.set_page_config(page_title="شاشة الموظف", page_icon="📝", layout="wide")
init_session()

user = st.session_state.get("user")
if not user or user["role"] not in ["مدير", "مشرف", "موظف"]:
    st.error("🔐 يجب تسجيل الدخول أولاً")
    st.stop()

st.title("📝 شاشة الموظف - تسجيل التسليم")

c1, c2, c3 = st.columns(3)
if c1.button("🏠 الرئيسية", use_container_width=True):
    st.switch_page("app.py")
c2.markdown(f"👤 **{user['name']}** — {user['role']}")
if c3.button("🚪 خروج", use_container_width=True):
    st.session_state["user"] = None
    st.switch_page("app.py")

st.markdown("---")

today = datetime.now().strftime("%Y-%m-%d")
subs_df = read_tab("submissions")

my_today = 0
if not subs_df.empty:
    subs_df["تاريخ التسليم الفعلي"] = subs_df["تاريخ التسليم الفعلي"].astype(str)
    my_today = len(subs_df[
        (subs_df["الموظف"] == user["name"]) &
        (subs_df["تاريخ التسليم الفعلي"].str.startswith(today))
    ])

c1, c2, c3 = st.columns(3)
c1.metric("📊 إنجازي اليوم", my_today)
c2.metric("📅 اليوم", today)
c3.metric("👤 اسمي", user["name"])

st.markdown("---")
st.markdown("### 🔍 البحث عن طالب")

col1, col2 = st.columns([4, 1])
with col1:
    query = st.text_input(
        "الرقم القومي أو رقم الجلوس",
        placeholder="أدخل الرقم القومي أو رقم الجلوس",
        label_visibility="collapsed",
        key="employee_search"
    )
with col2:
    search_btn = st.button("🔍 بحث", use_container_width=True, key="btn_search")

if search_btn:
    if not query:
        st.warning("⚠️ أدخل الرقم")
    else:
        with st.spinner("جاري البحث..."):
            student = search_student(query)
            submission = None
            if student is not None:
                submission = get_submission(student["الرقم القومي"])
        st.session_state["current_student"] = student.to_dict() if student is not None else None
        st.session_state["current_submission"] = submission.to_dict() if submission is not None else None

if st.session_state.get("current_student"):
    student = st.session_state["current_student"]
    submission = st.session_state.get("current_submission")
    
    st.markdown("---")
    st.markdown("### 📄 بيانات الطالب")
    
    c1, c2 = st.columns(2)
    with c1:
        st.write(f"**الاسم:** {student['اسم الطالب']}")
        st.write(f"**رقم الجلوس:** {student['رقم الجلوس']}")
        st.write(f"**الرقم القومي:** {student['الرقم القومي']}")
    with c2:
        st.write(f"**المجموعة العلمية:** {student['المجموعة العلمية']}")
        st.write(f"**الإدارة:** {student['الادارة']}")
        st.write(f"**المديرية:** {student['المديرية']}")
    
    st.markdown(f"""
    <div style="background:#dbeafe; padding:15px; border-radius:10px; text-align:center; margin:15px 0;">
        <h3 style="margin:0; color:#1e40af;">📅 موعد التسليم المحدد</h3>
        <p style="font-size:20px; margin:10px 0 0; font-weight:bold;">يوم {student['يوم التسليم']} الموافق {student['تاريخ التسليم']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    if submission is not None:
        st.error(f"⚠️ تم تسجيل تسليم هذا الطالب مسبقاً")
        st.write(f"**التاريخ:** {submission['تاريخ التسليم الفعلي']}")
        st.write(f"**الموظف:** {submission['الموظف']}")
    else:
        st.success("✅ الطالب لم يسلّم ملفه بعد — يمكن التسجيل الآن")
        
        st.markdown("### ✍️ تسجيل التسليم")
        with st.form("record_submission_form"):
            notes = st.text_area("ملاحظات (اختياري)", height=80)
            submitted = st.form_submit_button("✅ تسجيل تسليم الملف", use_container_width=True, type="primary")
            
            if submitted:
                result = record_submission(student, user["name"], notes)
                if "error" in result:
                    st.error(result["error"])
                else:
                    st.success(result["message"])
                    st.balloons()
                    st.session_state["current_student"] = None
                    st.session_state["current_submission"] = None
                    st.rerun()
