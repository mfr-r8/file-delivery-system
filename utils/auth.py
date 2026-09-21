import streamlit as st
from utils.sheets import read_tab, append_row, update_row


def init_session():
    if "user" not in st.session_state:
        st.session_state["user"] = None


def authenticate(email, password):
    """المصادقة - مقارنة مباشرة بدون تشفير"""
    users_df = read_tab("users")
    
    if users_df.empty:
        return None
    
    # تنظيف أسماء الأعمدة من أي مسافات
    users_df.columns = [str(c).strip() for c in users_df.columns]
    
    # البحث عن المستخدم
    users_df["الإيميل"] = users_df["الإيميل"].astype(str).str.strip()
    user = users_df[users_df["الإيميل"] == str(email).strip()]
    
    if user.empty:
        return None
    
    row = user.iloc[0]
    stored_password = str(row["كلمة المرور"]).strip()
    
    # مقارنة مباشرة
    if str(password).strip() == stored_password:
        return {
            "email": email,
            "name": str(row["الاسم"]).strip(),
            "role": str(row["الدور"]).strip(),
            "signature": str(row.get("التوقيع", "")).strip()
        }
    return None


def create_default_admin():
    """إنشاء مدير افتراضي إذا كانت الورقة فارغة"""
    try:
        users_df = read_tab("users")
        if users_df.empty:
            append_row("users", {
                "الإيميل": "admin@delivery.com",
                "كلمة المرور": "admin123",
                "الاسم": "مدير النظام",
                "الدور": "مدير",
                "التوقيع": "مدير النظام"
            })
    except Exception:
        pass


def change_own_password(email, old_password, new_password):
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


def admin_reset_password(target_email, new_password):
    users_df = read_tab("users")
    if users_df.empty:
        return {"error": "لا يوجد مستخدمون"}
    users_df.columns = [str(c).strip() for c in users_df.columns]
    users_df["الإيميل"] = users_df["الإيميل"].astype(str).str.strip()
    match = users_df[users_df["الإميل"] == str(target_email).strip()] if "الإميل" in users_df.columns else users_df[users_df["الإيميل"] == str(target_email).strip()]
    if match.empty:
        return {"error": "المستخدم غير موجود"}
    if len(new_password) < 6:
        return {"error": "⚠️ كلمة المرور 6 أحرف على الأقل"}
    real_row_num = match.index[0] + 2
    updated = match.iloc[0].to_dict()
    updated["كلمة المرور"] = new_password
    update_row("users", real_row_num, updated)
    return {"success": True, "message": f"✅ تم التعيين لـ {target_email}"}


def hash_password(password):
    """احتفظت بالدالة للتوافق لكنها لم تعد تستخدم تشفير"""
    return password


def is_admin():
    user = st.session_state.get("user")
    return user and user["role"] == "مدير"


def is_staff():
    user = st.session_state.get("user")
    return user and user["role"] in ["مدير", "مشرف", "موظف"]
