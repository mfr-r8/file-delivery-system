import streamlit as st
from utils.auth import init_session, is_admin
from utils.sheets import list_sheets_in_folder, delete_file_by_id, read_tab, log_action

st.set_page_config(page_title="لوحة المدير", page_icon="👑", layout="wide")
init_session()

if not is_admin():
    st.error("🔐 للمدير فقط")
    st.stop()

user = st.session_state["user"]
st.title("👑 لوحة المدير")

c1, c2, c3 = st.columns(3)
if c1.button("🏠 الرئيسية", use_container_width=True):
    st.switch_page("app.py")
c2.markdown(f"👤 **{user['name']}**")
if c3.button("🚪 خروج", use_container_width=True):
    st.session_state["user"] = None
    st.switch_page("app.py")

st.markdown("---")

tab1, tab2, tab3 = st.tabs(["📁 ملفات التسليم", "👥 المستخدمون", "📜 سجل النشاط"])

with tab1:
    st.markdown("### 📁 إدارة ملفات التسليم")
    st.info("""
    **لإضافة ملف جديد:**
    1. افتح Google Drive → مجلد النظام.
    2. ارفع ملف Excel وحوّله إلى Google Sheets (يدوياً أو عبر Colab).
    3. ارجع هنا واضغط **🔄 تحديث القائمة**.
    """)
    
    if st.button("🔄 تحديث القائمة", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 📋 الملفات الحالية")
    
    files = list_sheets_in_folder()
    if not files:
        st.warning("لا توجد ملفات")
    else:
        for f in files:
            with st.container():
                c1, c2 = st.columns([5, 1])
                with c1:
                    modified = f.get('modifiedTime', '')[:10]
                    st.write(f"📄 **{f['name']}** — {modified}")
                with c2:
                    if st.button("🗑️ حذف", key=f"del_{f['id']}"):
                        st.session_state[f"confirm_del_{f['id']}"] = True
                
                if st.session_state.get(f"confirm_del_{f['id']}"):
                    st.warning(f"⚠️ حذف **{f['name']}** نهائياً؟")
                    cc1, cc2 = st.columns(2)
                    if cc1.button("✅ نعم", key=f"yes_{f['id']}", use_container_width=True, type="primary"):
                        if delete_file_by_id(f['id']):
                            log_action("حذف ملف", target=f['name'])
                            st.session_state[f"confirm_del_{f['id']}"] = False
                            st.cache_data.clear()
                            st.rerun()
                    if cc2.button("❌ لا", key=f"no_{f['id']}", use_container_width=True):
                        st.session_state[f"confirm_del_{f['id']}"] = False
                        st.rerun()
                st.markdown("---")

with tab2:
    if st.button("👉 الانتقال إلى إدارة المستخدمين", use_container_width=True):
        st.switch_page("pages/5_Users.py")

with tab3:
    st.markdown("### 📜 آخر 200 عملية")
    audit_df = read_tab("audit")
    if audit_df.empty:
        st.info("لا توجد عمليات")
    else:
        st.dataframe(audit_df.tail(200).iloc[::-1], use_container_width=True, height=500)
        csv = audit_df.to_csv(index=False).encode("utf-8-sig")
        st.download_button("📥 تحميل السجل", csv, "audit.csv", "text/csv")
