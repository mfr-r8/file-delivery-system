import streamlit as st
from utils.auth import init_session, authenticate
from utils.students import search_student
from utils.statement import generate_student_statement_html, get_submission

st.set_page_config(page_title="نظام تسليم الملفات", page_icon="📁", layout="wide")
init_session()

st.markdown("""
<style>
    * { font-family: 'Cairo', 'Tahoma', sans-serif; }
    .main-header {
        background: linear-gradient(135deg, #1a3a5c, #2b7a62);
        color: white; padding: 25px; border-radius: 15px;
        text-align: center; margin-bottom: 25px;
    }
    .stButton > button {
        background-color: #2b7a62; color: white;
        border-radius: 8px; padding: 10px 20px; font-weight: bold;
    }
    .info-box { background:#dbeafe; color:#1e40af; padding:15px; border-radius:8px; text-align:center; font-weight:bold; margin:10px 0;}
    .success-box { background:#d1fae5; color:#065f46; padding:15px; border-radius:8px; text-align:center; font-weight:bold; margin:10px 0;}
    .error-box { background:#fee2e2; color:#991b1b; padding:15px; border-radius:8px; text-align:center; font-weight:bold; margin:10px 0;}
    .warning-box { background:#fef3c7; color:#92400e; padding:15px; border-radius:8px; text-align:center; font-weight:bold; margin:10px 0;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <h1>📁 نظام تسليم ملفات الطلاب</h1>
    <p>كلية علوم الرياضة بنين - أبو قير</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🔍 استعلام طالب", "🖊️ دخول الموظفين"])

# ============ تبويب الطالب ============
with tab1:
    st.markdown("### 🔍 أدخل رقمك القومي أو رقم جلوس الثانوية العامة")
    col1, col2 = st.columns([4, 1])
    with col1:
        query = st.text_input(
            "الرقم القومي أو رقم الجلوس",
            placeholder="أدخل الرقم القومي (14 رقم) أو رقم الجلوس",
            label_visibility="collapsed",
            key="student_search_input"
        )
    with col2:
        search_btn = st.button("🔍 عرض بياناتي", use_container_width=True)

    if search_btn:
        if not query:
            st.warning("⚠️ الرجاء إدخال الرقم القومي أو رقم الجلوس")
        else:
            with st.spinner("جاري البحث..."):
                student = search_student(query)
                submission = None
                if student is not None:
                    submission = get_submission(student["الرقم القومي"])
            
            if student is None:
                st.markdown('<div class="error-box">⚠️ لم يتم العثور على طالب بهذا الرقم</div>', unsafe_allow_html=True)
            else:
                st.markdown(f"### 📄 {student['اسم الطالب']}")
                
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f'<div class="info-box"><b>رقم الجلوس:</b> {student["رقم الجلوس"]}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="info-box"><b>الرقم القومي:</b> {student["الرقم القومي"]}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="info-box"><b>المجموعة العلمية:</b> {student["المجموعة العلمية"]}</div>', unsafe_allow_html=True)
                with c2:
                    st.markdown(f'<div class="info-box"><b>الإدارة:</b> {student["الادارة"]}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="info-box"><b>المديرية:</b> {student["المديرية"]}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="info-box"><b>التوزيع:</b> {student["التوزيع"]}</div>', unsafe_allow_html=True)
                
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #1a3a5c, #2b7a62); color:white; padding:25px; border-radius:15px; text-align:center; margin:20px 0;">
                    <h2 style="margin:0;">📅 موعد تسليم الملف</h2>
                    <h1 style="margin:15px 0; font-size:32px;">يوم {student['يوم التسليم']}</h1>
                    <h3 style="margin:5px 0;">الموافق {student['تاريخ التسليم']}</h3>
                    <p style="margin:15px 0 0; font-size:18px;">اعتباراً من الساعة 9 صباحاً</p>
                </div>
                """, unsafe_allow_html=True)
                
                if submission is not None:
                    st.markdown(f'<div class="success-box">✅ تم تسليم ملفك بتاريخ: {submission["تاريخ التسليم الفعلي"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="warning-box">⏳ لم يتم تسليم الملف بعد</div>', unsafe_allow_html=True)
                
                st.markdown("---")
                st.markdown("### 🖨️ طباعة البيان")
                st.caption("اضغط 'فتح للطباعة' → سيُفتح في نافذة جديدة → اختر طباعة → Save as PDF")
                
                html_content = generate_student_statement_html(student, submission)
                
                with st.expander("👁️ معاينة البيان"):
                    st.components.v1.html(html_content, height=800, scrolling=True)
                
                c1, c2 = st.columns(2)
                with c1:
                    st.download_button(
                        "📥 تحميل البيان (HTML)",
                        data=html_content.encode("utf-8"),
                        file_name=f"بيان_تسليم_{student['رقم الجلوس']}.html",
                        mime="text/html",
                        use_container_width=True
                    )
                with c2:
                    st.markdown(
                        f'<a href="data:text/html;charset=utf-8,{html_content}" target="_blank" '
                        f'style="display:block; background:#2b7a62; color:white; padding:11px 20px; '
                        f'border-radius:8px; text-align:center; text-decoration:none; font-weight:bold;">'
                        f'🖨️ فتح للطباعة</a>',
                        unsafe_allow_html=True
                    )

# ============ تبويب الموظف ============
with tab2:
    if st.session_state.get("user") is None:
        st.markdown("### 🔐 تسجيل دخول الموظفين")
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            with st.form("staff_login"):
                email = st.text_input("📧 البريد الإلكتروني")
                password = st.text_input("🔒 كلمة المرور", type="password")
                if st.form_submit_button("🔓 دخول", use_container_width=True):
                    user = authenticate(email, password)
                    if user and user["role"] in ["مدير", "مشرف", "موظف"]:
                        st.session_state["user"] = user
                        st.rerun()
                    else:
                        st.error("❌ بيانات غير صحيحة")
    else:
        user = st.session_state["user"]
        st.markdown(f"### 👤 مرحباً {user['name']}")
        st.markdown(f"**الدور:** {user['role']}")
        
        st.markdown("---")
        st.markdown("### 🎯 الروابط السريعة")
        c1, c2 = st.columns(2)
        with c1:
            if user["role"] == "موظف":
                if st.button("📝 شاشة الموظف", use_container_width=True):
                    st.switch_page("pages/1_Employee.py")
            elif user["role"] in ["مدير", "مشرف"]:
                if st.button("📊 لوحة المشرف", use_container_width=True):
                    st.switch_page("pages/2_Supervisor.py")
        with c2:
            if user["role"] == "مدير":
                if st.button("👑 لوحة المدير", use_container_width=True):
                    st.switch_page("pages/3_Admin.py")
            if st.button("🔑 حسابي", use_container_width=True):
                st.switch_page("pages/4_MyAccount.py")
        
        st.markdown("---")
        if st.button("🚪 تسجيل الخروج", use_container_width=True):
            st.session_state["user"] = None
            st.rerun()

st.markdown("---")
st.markdown('<div style="text-align:center; color:#94a3b8; padding:15px; font-size:14px;">جميع الحقوق محفوظة © كلية علوم الرياضة بنين - أبو قير</div>', unsafe_allow_html=True)
