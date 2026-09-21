import gspread
import streamlit as st
import pandas as pd
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from datetime import datetime

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]


@st.cache_resource
def _get_creds():
    return Credentials.from_service_account_info(
        dict(st.secrets["gcp_service_account"]),
        scopes=SCOPES
    )


@st.cache_resource
def get_gspread_client():
    return gspread.authorize(_get_creds())


@st.cache_resource
def get_drive_service():
    return build('drive', 'v3', credentials=_get_creds())


@st.cache_resource
def get_system_spreadsheet():
    file_id = st.secrets["files"]["system_file_id"]
    return get_gspread_client().open_by_key(file_id)


def _get_worksheet(tab_name):
    try:
        ss = get_system_spreadsheet()
        return ss.worksheet(tab_name)
    except Exception:
        return None


def read_tab(tab_name):
    try:
        ws = _get_worksheet(tab_name)
        if ws is None:
            return pd.DataFrame()
        data = ws.get_all_records()
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"خطأ في قراءة {tab_name}: {e}")
        return pd.DataFrame()


def append_row(tab_name, row_dict):
    try:
        ws = _get_worksheet(tab_name)
        if ws is None:
            return False
        headers = ws.row_values(1)
        ws.append_row([row_dict.get(h, "") for h in headers])
        return True
    except Exception as e:
        st.error(f"خطأ في الإضافة: {e}")
        return False


def update_row(tab_name, row_index, row_dict):
    try:
        ws = _get_worksheet(tab_name)
        if ws is None:
            return False
        headers = ws.row_values(1)
        ws.update(f"A{row_index}", [[row_dict.get(h, "") for h in headers]])
        return True
    except Exception as e:
        st.error(f"خطأ في التحديث: {e}")
        return False


def delete_row(tab_name, row_index):
    try:
        ws = _get_worksheet(tab_name)
        if ws is None:
            return False
        ws.delete_rows(row_index)
        return True
    except Exception as e:
        st.error(f"خطأ في الحذف: {e}")
        return False


def log_action(action_type, target="", details=""):
    try:
        user = st.session_state.get("user")
        append_row("audit", {
            "التاريخ": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "الإيميل": user.get("email", "") if user else "",
            "الاسم": user.get("name", "") if user else "",
            "نوع العملية": action_type,
            "الهدف": target,
            "التفاصيل": details
        })
    except Exception:
        pass


def list_sheets_in_folder():
    """جلب ملفات الطلاب بناءً على المعرّفات مباشرة (بدون بحث في المجلد)"""
    result = []
    
    # ملف الطلاب
    try:
        students_id = st.secrets["files"]["students_file_id"]
        client = get_gspread_client()
        sh = client.open_by_key(students_id)
        result.append({
            "id": students_id,
            "name": sh.title,
            "modifiedTime": ""
        })
    except Exception as e:
        st.error(f"خطأ في فتح ملف الطلاب: {e}")
    
    return result


def read_sheet_raw(file_id):
    try:
        client = get_gspread_client()
        sh = client.open_by_key(file_id)
        ws = sh.get_worksheet(0)
        return ws.get_all_values()
    except Exception as e:
        st.error(f"خطأ في القراءة: {e}")
        return []


def delete_file_by_id(file_id):
    try:
        get_drive_service().files().delete(fileId=file_id).execute()
        return True
    except Exception as e:
        st.error(f"خطأ: {e}")
        return False
