import streamlit as st
from utils.auth import init_session, is_admin, hash_password, admin_reset_password
from utils.sheets import read_tab, append_row, delete_row, update_row, log_action

st.set_page_config(page_title="إدارة المستخدمين", page_icon="👥", layout="wide")
init_session()

if not is_admin():
    st.error("🔐 للمدير فقط")
    st.stop()

user = st.session_state["user"]
st.title("👥 إدارة المستخدمين")

c1, c2, c3 = st.columns(3)
if c1.button("🏠 الرئيسية", use_container_width=True):
    st.switch_page("app.py")
c2.markdown(f"👤 **{user['name']}**")
if c3.button("🚪 خروج", use_container_width=True):
    st.session_state["user"] = None
    st.switch_page("app.py")

st.markdown("---")

# ============ إضافة مستخدم جديد ============
with st.form("add_user_form"):
    st.markdown("### ➕ إضافة مستخدم جديد")
    
    c1, c2 = st.columns(2)
    new_email = c1.text_input("📧 البريد الإلكتروني", placeholder="example@alexu.edu.eg")
    new_name = c2.text_input("👤 الاسم الكامل", placeholder="أحمد محمد علي")
    
    new_password = c1.text_input("🔒 كلمة المرور", type="password", placeholder="6 أحرف على الأقل")
    new_role = c2.selectbox("🎭 الدور", ["موظف", "مشرف", "مدير"])
    
    new_signature = st.text_input("✍️ التوقيع (يظهر في الإيصالات)", placeholder="أ. أحمد محمد")
    
    if st.form_submit_button("➕ إضافة المستخدم", use_container_width=True, type="primary"):
        if not new_email or not new_name or not new_password:
            st.error("⚠️ املأ جميع الحقول الإلزامية")
        elif len(new_password) < 6:
            st.error("⚠️ كلمة المرور 6 أحرف على الأقل")
        else:
            users_df = read_tab("users")
            existing_emails = []
            if not users_df.empty:
                existing_emails = users_df["الإيميل"].astype(str).str.strip().tolist()
            
            if new_email.strip() in existing_emails:
                st.error(f"⚠️ البريد `{new_email}` مسجل مسبقاً")
            else:
                append_row("users", {
                    "الإيميل": new_email.strip(),
                    "كلمة المرور": new_password,
                    "الاسم": new_name.strip(),
                    "الدور": new_role,
                    "التوقيع": new_signature.strip() if new_signature else new_name.strip()
                })
                log_action("إضافة مستخدم", target=new_email, details=f"الدور: {new_role}")
                st.success(f"✅ تمت إضافة {new_name} بنجاح")
                st.balloons()
                st.rerun()

st.markdown("---")

# ============ قائمة المستخدمين ============
st.markdown("### 👥 المستخدمون الحاليون")

users_df = read_tab("users")
if users_df.empty:
    st.info("لا يوجد مستخدمون بعد")
else:
    # إحصائيات
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📊 الإجمالي", len(users_df))
    c2.metric("👑 مديرون", len(users_df[users_df["الدور"] == "مدير"]))
    c3.metric("📋 مشرفون", len(users_df[users_df["الدور"] == "مشرف"]))
    c4.metric("👨‍💼 موظفون", len(users_df[users_df["الدور"] == "موظف"]))
    
    st.markdown("---")
    
    # عرض كل مستخدم
    for idx, row in users_df.iterrows():
        real_row_num = idx + 2
        
        with st.container():
            c1, c2, c3, c4, c5, c6 = st.columns([3, 2, 2, 1, 1, 1])
            
            c1.write(f"📧 **{row['الإيميل']}**")
            c2.write(f"👤 {row['الاسم']}")
            c3.write(f"🏷️ {row['الدور']}")
            
            is_self = str(row['الإيميل']).strip() == str(user['email']).strip()
            
            if is_self:
                c4.write("🔒")
                c5.write("(أنت)")
            else:
                # زر إعادة تعيين كلمة المرور
                if c4.button("🔑", key=f"reset_{idx}", help="إعادة تعيين كلمة المرور"):
                    st.session_state[f"resetting_{idx}"] = True
                
                # زر حذف
                if c5.button("🗑️", key=f"del_{idx}", help="حذف المستخدم"):
                    st.session_state[f"confirm_del_{idx}"] = True
            
            # نموذج إعادة التعيين
            if st.session_state.get(f"resetting_{idx}"):
                st.markdown("---")
                st.markdown(f"**🔑 إعادة تعيين كلمة المرور لـ {row['الاسم']}**")
                
                new_pw = st.text_input(
                    "كلمة المرور الجديدة",
                    type="password",
                    key=f"new_pw_{idx}",
                    placeholder="6 أحرف على الأقل"
                )
                
                cc1, cc2 = st.columns(2)
                if cc1.button("✅ تعيين", key=f"ok_reset_{idx}", use_container_width=True, type="primary"):
                    if not new_pw or len(new_pw) < 6:
                        st.error("⚠️ 6 أحرف على الأقل")
                    else:
                        real_row_num2 = idx + 2
                        updated = row.to_dict()
                        updated["كلمة المرور"] = new_pw
                        update_row("users", real_row_num2, updated)
                        log_action("إعادة تعيين كلمة مرور", target=str(row['الإيميل']))
                        st.success(f"✅ تم تعيين كلمة المرور لـ {row['الاسم']}")
                        st.session_state[f"resetting_{idx}"] = False
                        st.rerun()
                
                if cc2.button("❌ إلغاء", key=f"cancel_reset_{idx}", use_container_width=True):
                    st.session_state[f"resetting_{idx}"] = False
                    st.rerun()
                st.markdown("---")
            
            # تأكيد الحذف
            if st.session_state.get(f"confirm_del_{idx}"):
                st.warning(f"⚠️ هل تريد حذف **{row['الاسم']}** ({row['الإيميل']}) نهائياً؟")
                
                cc1, cc2 = st.columns(2)
                if cc1.button("✅ نعم احذف", key=f"ok_del_{idx}", use_container_width=True, type="primary"):
                    real_row_num2 = idx + 2
                    delete_row("users", real_row_num2)
                    log_action("حذف مستخدم", target=str(row['الإيميل']))
                    st.session_state[f"confirm_del_{idx}"] = False
                    st.success("✅ تم الحذف")
                    st.rerun()
                
                if cc2.button("❌ إلغاء", key=f"cancel_del_{idx}", use_container_width=True):
                    st.session_state[f"confirm_del_{idx}"] = False
                    st.rerun()
            
            st.markdown("---")
