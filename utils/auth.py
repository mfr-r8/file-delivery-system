import streamlit as st
from utils.sheets import read_tab, append_row, update_row


def init_session():
    if "user" not in st.session_state:
        st.session_state["user"] = None


def authenticate(email, password):
    """المصادقة - مع دخول احتياطي ثابت"""
    
    # ===== دخول احتياطي ثابت (يعمل دائماً) =====
    email_clean = str(email).strip().lower()
    password_clean = str(password).strip()
    
    if email_clean == "admin@delivery.com" and password_clean == "admin123":
        return {
            "email": "admin@delivery.com",
            "name": "مدير النظام",
            "role": "مدير",
            "signature": "مدير النظام"
        }
    
    # ===== محاولة القراءة من Google Sheets =====
    try:
        users_df = read_tab("users")
        
        if users_df.empty:
            return None
        
        # تنظيف أسماء الأعمدة
        users_df.columns = [str(c).strip() for c in users_df.columns]
        
        # تنظيف الإيميل
        users_df["الإيميل"] = users_df["الإيميل"].astype(str).str.strip().str.lower()
        
        # البحث
        user = users_df[users_df["الإيميل"] == email_clean]
        
        if user.empty:
            return None
        
        row = user.iloc[0]
        stored_password = str(row["كلمة المرور"]).strip()
        
        if password_clean == stored_password:
            return {
                "email": email_clean,
                "name": str(row["الاسم"]).strip(),
                "role": str(row["الدور"]).strip(),
                "signature": str(row.get("التوقيع", "")).strip()
            }
        return None
    except Exception:
        return None


def create_default_admin():
    pass


def change_own_password(email, old_password, new_password):
    if str(email).strip().lower() == "admin@delivery.com":
        if str(old_password).strip() == "admin123":
            st.session_state["admin_new_password"] = str(new_password).strip()
            return {"success": True, "message": "✅ تم تغيير كلمة المرور (للجلسة الحالية)"}
        return {"error": "❌ كلمة المرور الحالية غير صحيحة"}
    
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
        if str(old_password).strip() != str(row["كلمة المرور"]).strip():
            return {"error": "❌ كلمة المرور الحالية غير صحيحة"}
        if len(new_password) < 6:
            return {"error": "⚠️ كلمة المرور 6 أحرف على الأقل"}
        real_row_num = match.index[0] + 2
        updated = row.to_dict()
        updated["كلمة المرور"] = new_password
        update_row("users", real_row_num, updated)
        return {"success": True, "message": "✅ تم تغيير كلمة المرور"}
    except Exception as e:
        return {"error": f"خطأ: {e}"}


def admin_reset_password(target_email, new_password):
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
        updated["كلمة المرور"] = new_password
        update_row("users", real_row_num, updated)
        return {"success": True, "message": f"✅ تم التعيين لـ {target_email}"}
    except Exception as e:
        return {"error": f"خطأ: {e}"}


def hash_password(password):
    return password


def is_admin():
    user = st.session_state.get("user")
    return user and user["role"] == "مدير"


def is_staff():
    user = st.session_state.get("user")
    return user and user["role"] in ["مدير", "مشرف", "موظف"]
