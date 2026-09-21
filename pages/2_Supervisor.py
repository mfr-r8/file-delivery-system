import streamlit as st
from utils.auth import init_session
from utils.sheets import read_tab
from utils.students import load_all_students

st.set_page_config(page_title="لوحة المشرف", page_icon="📊", layout="wide")
init_session()

user = st.session_state.get("user")
if not user or user["role"] not in ["مدير", "مشرف"]:
    st.error("🔐 للمدير أو المشرف فقط")
    st.stop()

st.title("📊 لوحة المشرف")

c1, c2, c3 = st.columns(3)
if c1.button("🏠 الرئيسية", use_container_width=True):
    st.switch_page("app.py")
c2.markdown(f"👤 **{user['name']}** — {user['role']}")
if c3.button("🚪 خروج", use_container_width=True):
    st.session_state["user"] = None
    st.switch_page("app.py")

st.markdown("---")

with st.spinner("جاري تحميل البيانات..."):
    students_df = load_all_students()
    subs_df = read_tab("submissions")

if students_df.empty:
    st.warning("⚠️ لا يوجد طلاب محمّلون")
    st.stop()

total = len(students_df)
submitted = 0
if not subs_df.empty:
    submitted_ids = set(subs_df["الرقم القومي"].astype(str))
    submitted = len(students_df[students_df["الرقم القومي"].astype(str).isin(submitted_ids)])

remaining = total - submitted

c1, c2, c3 = st.columns(3)
c1.metric("📊 إجمالي الطلاب", total)
c2.metric("✅ سلّموا", submitted)
c3.metric("⏳ لم يسلّموا", remaining)

st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs(["📋 كل الطلاب", "✅ الذين سلّموا", "⏳ الذين لم يسلّموا", "📅 حسب اليوم"])

with tab1:
    st.markdown("### 📋 كل الطلاب")
    search = st.text_input("🔍 بحث", key="sup_search")
    df_show = students_df.copy()
    if search:
        mask = df_show.astype(str).apply(lambda r: r.str.contains(search, case=False, na=False).any(), axis=1)
        df_show = df_show[mask]
    st.dataframe(df_show, use_container_width=True, height=500)
    csv = df_show.to_csv(index=False).encode("utf-8-sig")
    st.download_button("📥 تحميل CSV", csv, "students.csv", "text/csv")

with tab2:
    st.markdown("### ✅ الطلاب الذين سلّموا ملفاتهم")
    if subs_df.empty:
        st.info("لا يوجد تسليمات بعد")
    else:
        merged = subs_df.merge(
            students_df[["الرقم القومي", "اسم الطالب", "رقم الجلوس"]],
            on="الرقم القومي",
            how="left"
        )
        st.dataframe(merged, use_container_width=True, height=500)
        csv = merged.to_csv(index=False).encode("utf-8-sig")
        st.download_button("📥 تحميل CSV", csv, "submitted.csv", "text/csv")

with tab3:
    st.markdown("### ⏳ الطلاب الذين لم يسلّموا")
    if subs_df.empty:
        not_submitted = students_df
    else:
        submitted_ids = set(subs_df["الرقم القومي"].astype(str))
        not_submitted = students_df[~students_df["الرقم القومي"].astype(str).isin(submitted_ids)]
    st.dataframe(not_submitted, use_container_width=True, height=500)
    csv = not_submitted.to_csv(index=False).encode("utf-8-sig")
    st.download_button("📥 تحميل CSV", csv, "not_submitted.csv", "text/csv")

with tab4:
    st.markdown("### 📅 توزيع الطلاب حسب يوم التسليم")
    if "يوم التسليم" in students_df.columns:
        days_summary = students_df.groupby(["يوم التسليم", "تاريخ التسليم"]).size().reset_index(name="عدد الطلاب")
        st.dataframe(days_summary, use_container_width=True)
