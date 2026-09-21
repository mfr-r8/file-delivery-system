import streamlit as st
import pandas as pd
import re
from utils.sheets import list_sheets_in_folder, read_sheet_raw


def _extract_date_from_title(title_text):
    text = str(title_text).strip()
    days = ["السبت", "الأحد", "الاثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة"]
    day_name = ""
    for d in days:
        if d in text:
            day_name = d
            break
    date_str = ""
    m = re.search(r'(\d{1,2})\s*/\s*(\d{1,2})\s*/\s*(\d{4})', text)
    if m:
        date_str = f"{m.group(1)}/{m.group(2)}/{m.group(3)}"
    return day_name, date_str


def _clean_name(name):
    s = str(name).strip()
    s = s.replace("_x000D_", "").replace("<br>", "").strip()
    return s


def _load_from_sheet_raw(raw_values):
    students = []
    current_day = ""
    current_date = ""
    
    for row in raw_values:
        if not row or len(row) < 3:
            continue
        
        # كشف سطر العنوان
        found_title = False
        for cell in row:
            if "أسماء الطلاب المسموح لهم بتسليم" in str(cell):
                current_day, current_date = _extract_date_from_title(str(cell))
                found_title = True
                break
        if found_title:
            continue
        
        # تخطي صف العناوين
        if len(row) > 1 and "رقم جلوس" in str(row[1]):
            continue
        
        try:
            seat = str(row[1]).strip() if len(row) > 1 else ""
            name = _clean_name(row[2]) if len(row) > 2 else ""
            national_id = str(row[6]).strip() if len(row) > 6 else ""
            national_id = re.sub(r'\D', '', national_id)
            
            if not national_id or len(national_id) < 10:
                continue
            
            student = {
                "التوزيع": str(row[0]).strip() if len(row) > 0 else "",
                "رقم الجلوس": seat,
                "اسم الطالب": name,
                "المجموع": str(row[3]).strip() if len(row) > 3 else "",
                "الكلية": str(row[4]).strip() if len(row) > 4 else "",
                "المجموعة العلمية": str(row[5]).strip() if len(row) > 5 else "",
                "الرقم القومي": national_id,
                "الادارة": str(row[7]).strip() if len(row) > 7 else "",
                "المديرية": str(row[8]).strip() if len(row) > 8 else "",
                "يوم التسليم": current_day,
                "تاريخ التسليم": current_date,
                "_file": ""
            }
            students.append(student)
        except Exception:
            continue
    
    return students


@st.cache_data(ttl=600, show_spinner=False)
def load_all_students():
    files = list_sheets_in_folder()
    all_students = []
    for f in files:
        raw_values = read_sheet_raw(f['id'])
        if not raw_values:
            continue
        students = _load_from_sheet_raw(raw_values)
        for s in students:
            s["_file"] = f['name']
        all_students.extend(students)
    return pd.DataFrame(all_students) if all_students else pd.DataFrame()


def find_student_by_national_id(national_id):
    if not national_id:
        return None
    df = load_all_students()
    if df.empty:
        return None
    nid = re.sub(r'\D', '', str(national_id))
    match = df[df["الرقم القومي"] == nid]
    if match.empty:
        return None
    return match.iloc[0]


def find_student_by_seat(seat_number):
    if not seat_number:
        return None
    df = load_all_students()
    if df.empty:
        return None
    seat = re.sub(r'\D', '', str(seat_number))
    match = df[df["رقم الجلوس"] == seat]
    if match.empty:
        return None
    return match.iloc[0]


def search_student(query):
    if not query:
        return None
    q = re.sub(r'\D', '', str(query))
    if not q:
        return None
    if len(q) >= 10:
        return find_student_by_national_id(q)
    return find_student_by_seat(q)
