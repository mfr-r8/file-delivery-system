import html
from datetime import datetime


def generate_student_statement_html(student, submission=None):
    name = html.escape(str(student.get("اسم الطالب", "")))
    seat = html.escape(str(student.get("رقم الجلوس", "")))
    nid = html.escape(str(student.get("الرقم القومي", "")))
    college = html.escape(str(student.get("الكلية", "")))
    science_group = html.escape(str(student.get("المجموعة العلمية", "")))
    admin = html.escape(str(student.get("الادارة", "")))
    directorate = html.escape(str(student.get("المديرية", "")))
    day = html.escape(str(student.get("يوم التسليم", "")))
    date = html.escape(str(student.get("تاريخ التسليم", "")))
    
    if submission is not None:
        submission_status = f"""
        <div class="status-box success">
            ✅ تم تسليم الملف بتاريخ {html.escape(str(submission.get('تاريخ التسليم الفعلي', '')))}
            <br>الموظف المستلم: {html.escape(str(submission.get('الموظف', '')))}
        </div>
        """
    else:
        submission_status = '<div class="status-box pending">⏳ لم يتم تسليم الملف بعد</div>'
    
    return f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<title>بيان تسليم ملف - {name}</title>
<style>
    * {{ font-family: 'Segoe UI', 'Tahoma', 'Arial', sans-serif; box-sizing: border-box; }}
    body {{ padding: 20px; max-width: 1000px; margin: auto; color: #1a3a5c; background: white; }}
    .header {{ text-align: center; border-bottom: 3px double #1a3a5c; padding-bottom: 15px; margin-bottom: 20px; }}
    .header h1 {{ color: #1a3a5c; margin: 5px 0; font-size: 24px; }}
    .header h2 {{ color: #2b7a62; margin: 5px 0; font-size: 18px; }}
    .header p {{ color: #64748b; margin: 5px 0; font-size: 14px; }}
    .student-info {{ background: #f0f4f8; padding: 15px; border-radius: 10px; margin: 15px 0; }}
    .student-info table {{ width: 100%; border-collapse: collapse; }}
    .student-info td {{ padding: 6px 10px; }}
    .student-info td:first-child {{ font-weight: bold; color: #2b7a62; width: 150px; }}
    .delivery-date {{ background: linear-gradient(135deg, #1a3a5c, #2b7a62); color: white; padding: 20px; border-radius: 10px; text-align: center; margin: 20px 0; }}
    .delivery-date h2 {{ margin: 0; font-size: 22px; }}
    .delivery-date h3 {{ margin: 10px 0 0; font-size: 28px; }}
    .delivery-date p {{ margin: 10px 0 0; font-size: 18px; }}
    .section {{ margin: 20px 0; padding: 15px; background: #f8fafc; border-radius: 10px; border-right: 5px solid #2b7a62; }}
    .section h3 {{ margin-top: 0; color: #1a3a5c; }}
    .section ol {{ padding-right: 25px; margin: 10px 0; }}
    .section li {{ margin: 6px 0; line-height: 1.6; }}
    .steps-table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
    .steps-table th {{ background: #2b7a62; color: white; padding: 10px; }}
    .steps-table td {{ padding: 10px; border: 1px solid #cbd5e1; text-align: center; }}
    .steps-table tr:nth-child(even) {{ background: #f8fafc; }}
    .note {{ background: #fef3c7; border-right: 5px solid #f59e0b; padding: 15px; border-radius: 8px; margin: 20px 0; font-weight: bold; color: #92400e; }}
    .status-box {{ padding: 15px; border-radius: 10px; text-align: center; font-weight: bold; margin: 15px 0; }}
    .status-box.success {{ background: #d1fae5; color: #065f46; border: 2px solid #10b981; }}
    .status-box.pending {{ background: #fef3c7; color: #92400e; border: 2px solid #f59e0b; }}
    .footer {{ text-align: center; color: #64748b; margin-top: 30px; padding-top: 15px; border-top: 1px solid #cbd5e1; font-size: 12px; }}
    .print-btn {{ display: block; margin: 20px auto; padding: 14px 40px; background: #2b7a62; color: white; border: none; border-radius: 8px; font-size: 16px; font-weight: bold; cursor: pointer; }}
    .print-btn:hover {{ background: #1e5c4a; }}
    @media print {{
        body {{ padding: 0; }}
        .no-print {{ display: none !important; }}
    }}
</style>
</head>
<body>
    <button class="print-btn no-print" onclick="window.print()">🖨️ طباعة / حفظ كـ PDF</button>

    <div class="header">
        <h1>جامعة الإسكندرية</h1>
        <h2>كلية علوم الرياضة بنين - أبو قير</h2>
        <p>بيان تسليم ملف الطالب المستجد</p>
    </div>

    <div class="student-info">
        <table>
            <tr><td>الاسم:</td><td>{name}</td></tr>
            <tr><td>رقم الجلوس:</td><td>{seat}</td></tr>
            <tr><td>الرقم القومي:</td><td>{nid}</td></tr>
            <tr><td>الكلية:</td><td>{college}</td></tr>
            <tr><td>المجموعة العلمية:</td><td>{science_group}</td></tr>
            <tr><td>الإدارة:</td><td>{admin}</td></tr>
            <tr><td>المديرية:</td><td>{directorate}</td></tr>
        </table>
    </div>

    <div class="delivery-date">
        <h2>📅 موعد تسليم الملف</h2>
        <h3>يوم {day}</h3>
        <p>الموافق {date} — اعتباراً من الساعة 9 صباحاً</p>
    </div>

    {submission_status}

    <div class="section">
        <h3>🔰 أولاً: ملف التجنيد</h3>
        <p>توضع في ملف شفاف (بيكسولة):</p>
        <ol>
            <li>صورة من شهادة الثانوية العامة (عدد 2)</li>
            <li>صورة من شهادة الميلاد الحديثة بها الرقم الثلاثي (عدد 2)</li>
            <li>صورة من بطاقة الرقم القومي (عدد 2)</li>
            <li>استمارة 6 أو 7 جند (عدد 4)</li>
        </ol>
    </div>

    <div class="section">
        <h3>📋 ثانياً: ملف شؤون الطلاب</h3>
        <p>توضع في ملف شفاف (بيكسولة):</p>
        <ol>
            <li>استمارة الكشف الطبي (لائق) مختومة</li>
            <li>أصل شهادة الثانوية العامة مختومة + 3 صور منها</li>
            <li>أصل شهادة الميلاد الحديثة + 3 صور منها</li>
            <li>نسخ من صورة الرقم القومي</li>
            <li>نسخة من استمارة رفع صور من الأصول على موقع MIS</li>
            <li>إيصال دفع المصروفات</li>
            <li>صور شخصية حديثة مكتوب عليها اسم الطالب وتاريخ العام الدراسي</li>
            <li>صورة بطاقة الأسرة (الأب - الأم - الإخوة) في حالة صغار السن</li>
            <li>شهادة الميلاد + شهادة الوفاة (في حالة صغار السن)</li>
            <li>استمارة التربية العسكرية مع ملء البيانات بها</li>
        </ol>
        <p><strong>💡 نصيحة:</strong> احضر قلمك معك.</p>
    </div>

    <div class="section">
        <h3>🚶 خطوات التسليم</h3>
        <table class="steps-table">
            <thead>
                <tr><th>#</th><th>الخطوة</th><th>المكان</th></tr>
            </thead>
            <tbody>
                <tr><td>1</td><td>الحضور في الموعد المحدد لكل طالب</td><td>بوابة الكلية</td></tr>
                <tr><td>2</td><td>الانتظار في القاعة</td><td>بجوار قسم شؤون الطلاب</td></tr>
                <tr><td>3</td><td>استلام إيصالات المصاريف والذهاب لدفعها</td><td>قسم الخزينة</td></tr>
                <tr><td>4</td><td>تسليم ملف التجنيد</td><td>قسم التجنيد بالكلية</td></tr>
                <tr><td>5</td><td>العودة لاستقبال دفتر التأمين الطبي للطالب</td><td>قاعة تسليم الملف</td></tr>
            </tbody>
        </table>
    </div>

    <div class="note">
        ⚠️ برجاء الالتزام بالمواعيد حتى يتسنى لنا مساعدتكم في تسليم الملف بسهولة ويسر.
    </div>

    <div class="footer">
        جميع الحقوق محفوظة © كلية علوم الرياضة بنين - أبو قير<br>
        هذا البيان صادر إلكترونياً من نظام تسليم الملفات
    </div>

    <button class="print-btn no-print" onclick="window.print()">🖨️ طباعة / حفظ كـ PDF</button>
</body>
</html>"""


def get_submission(national_id):
    from utils.sheets import read_tab
    subs = read_tab("submissions")
    if subs.empty:
        return None
    subs["الرقم القومي"] = subs["الرقم القومي"].astype(str).str.strip()
    match = subs[subs["الرقم القومي"] == str(national_id).strip()]
    if match.empty:
        return None
    return match.iloc[0]


def record_submission(student, employee_name, notes=""):
    from utils.sheets import append_row, log_action
    from datetime import datetime
    
    national_id = str(student.get("الرقم القومي", "")).strip()
    
    existing = get_submission(national_id)
    if existing is not None:
        return {"error": f"⚠️ تم تسجيل تسليم هذا الطالب مسبقاً بتاريخ: {existing['تاريخ التسليم الفعلي']}"}
    
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    append_row("submissions", {
        "الرقم القومي": national_id,
        "رقم الجلوس": str(student.get("رقم الجلوس", "")),
        "اسم الطالب": str(student.get("اسم الطالب", "")),
        "يوم التسليم المحدد": str(student.get("يوم التسليم", "")),
        "تاريخ التسليم المحدد": str(student.get("تاريخ التسليم", "")),
        "تاريخ التسليم الفعلي": now,
        "الموظف": employee_name,
        "ملاحظات": notes
    })
    
    log_action("تسجيل تسليم ملف", target=str(student.get("اسم الطالب", "")), details=f"الرقم: {national_id}")
    
    return {"success": True, "message": f"✅ تم تسجيل التسليم بنجاح بتاريخ {now}", "timestamp": now}
