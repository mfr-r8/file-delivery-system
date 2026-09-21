import streamlit as st
import bcrypt
from utils.sheets import read_tab, append_row, update_row


def hash_password(password):
    """تشفير كلمة المرور باستخدام bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(password, hashed):
    """التحقق من كلمة المرور - يدعم المشفرة والعادية"""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    except Exception:
        # كلمة مرور غير مشفرة (plain text)
        return password == hashed


def init_session():
    if "user" not in st.session_state:
        st.session_state["user"] = None


def authenticate(email, password):
    """المصادقة"""
    try:
        users_df = read_tab("users")
        
        if users_df.empty:
            return None
        
        # تنظيف أسماء الأعمدة
        users_df.columns = [str(c).strip() for c in users_df.columns]
        
        # تنظيف الإيميل
        users_df["الإيميل"] = users_df["الإيميل"].astype(str).str.strip()
        
        # البحث عن المستخدم
        email_clean = str(email).strip()
        user = users_df[users_df["الإيميل"] == email_clean]
        
        if user.empty:
            return None
        
        row = user.iloc[0]
        stored_password = str(row["كلمة المرور"]).strip()
        entered_password = str(password).strip()
        
        # التحقق من كلمة المرور
        if verify_password(entered_password, stored_password):
            return {
                "email": email_clean,
                "name": str(row["الاسم"]).strip(),
                "role": str(row["الدور"]).strip(),
                "signature": str(row.get("التوقيع", "")).strip()
            }
        return None
    except Exception:
        return None


def change_own_password(email, old_password, new_password):
    """تغيير كلمة المرور الخاصة"""
    try:
        users_df = read_tab("users")
        if users_df.empty:
            return {"error": "لا يوجد مستخدمون"}
        
        users_df.columns = [str(c).strip() for c in users_df.columns]
        users_df["الإيميل"] = users_df["الإيميل"].astype(str).str.strip()
        
        match = users_df[users_df["الإيميل"] == str(email).strip()]
        if match.empty:
            return {"error": "المستخدم غير موجود"}
        
        row = match.iloc[0]
        stored_password = str(row["كلمة المرور"]).strip()
        
        if not verify_password(str(old_password).strip(), stored_password):
            return {"error": "❌ كلمة المرور الحالية غير صحيحة"}
        
        if len(new_password) < 6:
            return {"error": "⚠️ كلمة المرور 6 أحرف على الأقل"}
        
        real_row_num = match.index[0] + 2
        updated = row.to_dict()
        updated["كلمة المرور"] = hash_password(new_password)
        update_row("users", real_row_num, updated)
        return {"success": True, "message": "✅ تم تغيير كلمة المرور"}
    except Exception as e:
        return {"error": f"خطأ: {e}"}


def admin_reset_password(target_email, new_password):
    """إعادة تعيين كلمة مرور مستخدم (للمدير)"""
    try:
        users_df = read_tab("users")
        if users_df.empty:
            return {"error": "لا يوجد مستخدمون"}
        
        users_df.columns = [str(c).strip() for c in users_df.columns]
        users_df["الإيميل"] = users_df["الإيميل"].astype(str).str.strip()
        
        match = users_df[users_df["الإيميل"] == str(target_email).strip()]
        if match.empty:
            return {"error": "المستخدم غير موجود"}
        
        if len(new_password) < 6:
            return {"error": "⚠️ كلمة المرور 6 أحرف على الأقل"}
        
        real_row_num = match.index[0] + 2
        updated = match.iloc[0].to_dict()
        updated["كلمة المرور"] = hash_password(new_password)
        update_row("users", real_row_num, updated)
        return {"success": True, "message": f"✅ تم التعيين لـ {target_email}"}
    except Exception as e:
        return {"error": f"خطأ: {e}"}


def is_admin():
    user = st.session_state.get("user")
    return user and user["role"] == "مدير"


def is_supervisor():
    user = st.session_state.get("user")
    return user and user["role"] in ["مدير", "مشرف"]


def is_staff():
    user = st.session_state.get("user")
    return user and user["role"] in ["مدير", "مشرف", "موظف"]
