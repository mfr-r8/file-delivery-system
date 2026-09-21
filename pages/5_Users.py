import streamlit as st
from utils.auth import init_session, is_admin, hash_password, admin_reset_password
from utils.sheets import read_tab, append_row, delete_row, log_action

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

with st.form("add_user_form"):
    st.markdown("### ➕ إضافة مستخدم جديد")
    c1, c2 = st.columns(2)
    new_email = c1.text_input("البريد الإلكتروني")
    new_name = c2.text_input("الاسم")
    new_password = c1.text_input("كلمة المرور", type="password")
    new_role = c2.selectbox("الدور", ["موظف", "مشرف", "مدير"])
    new_signature = st.text_input("التوقيع (يظهر في الإيصالات)")
    
    if st.form_submit_button("➕ إضافة", use_container_width=True):
        if new_email and new_name and new_password:
            users_df = read_tab("users")
            if not users_df.empty and new_email in users_df["الإيميل"].astype(str).values:
                st.error("⚠️ موجود بالفعل")
            else:
                append_row("users", {
                    "الإيميل": new_email,
                    "كلمة المرور": hash_password(new_password),
                    "الاسم": new_name,
                    "الدور": new_role,
                    "التوقيع": new_signature
                })
                log_action("إضافة مستخدم", target=new_email, details=new_role)
                st.success("✅ تمت الإضافة")
                st.rerun()
        else:
            st.error("⚠️ املأ الحقول")

st.markdown("---")
st.markdown("### 👥 قائمة المستخدمين")

users_df = read_tab("users")
if users_df.empty:
    st.info("لا يوجد مستخدمون")
else:
    for idx, row in users_df.iterrows():
        real_row_num = idx + 2
        with st.container():
            c1, c2, c3, c4, c5 = st.columns([3, 2, 2, 1, 1])
            c1.write(f"📧 **{row['الإيميل']}**")
            c2.write(f"👤 {row['الاسم']}")
            c3.write(f"🏷️ {row['الدور']}")
            
            is_self = row['الإيميل'] == user['email']
            if is_self:
                c4.write("🔒")
                c5.write("(أنت)")
            else:
                if c4.button("🔑", key=f"reset_{idx}", help="إعادة تعيين كلمة المرور"):
                    st.session_state[f"resetting_{idx}"] = True
                if c5.button("🗑️", key=f"del_{idx}", help="حذف"):
                    st.session_state[f"confirm_del_{idx}"] = True
                
                if st.session_state.get(f"resetting_{idx}"):
                    new_pw = st.text_input("كلمة المرور الجديدة", type="password", key=f"new_pw_{idx}")
                    cc1, cc2 = st.columns(2)
                    if cc1.button("✅ تعيين", key=f"ok_reset_{idx}", use_container_width=True, type="primary"):
                        r = admin_reset_password(row['الإيميل'], new_pw)
                        if "error" in r:
                            st.error(r["error"])
                        else:
                            log_action("إعادة تعيين كلمة مرور", target=row['الإيميل'])
                            st.success(r["message"])
                            st.session_state[f"resetting_{idx}"] = False
                            st.rerun()
                    if cc2.button("❌ إلغاء", key=f"cancel_reset_{idx}", use_container_width=True):
                        st.session_state[f"resetting_{idx}"] = False
                        st.rerun()
                
                if st.session_state.get(f"confirm_del_{idx}"):
                    st.warning(f"⚠️ حذف **{row['الاسم']}** نهائياً؟")
                    cc1, cc2 = st.columns(2)
                    if cc1.button("✅ نعم", key=f"ok_del_{idx}", use_container_width=True, type="primary"):
                        delete_row("users", real_row_num)
                        log_action("حذف مستخدم", target=str(row['الإيميل']))
                        st.session_state[f"confirm_del_{idx}"] = False
                        st.rerun()
                    if cc2.button("❌ لا", key=f"cancel_del_{idx}", use_container_width=True):
                        st.session_state[f"confirm_del_{idx}"] = False
                        st.rerun()
            st.markdown("---")
