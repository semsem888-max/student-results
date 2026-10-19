import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
import os

app = FastAPI(title="منصة نتائج الطلاب - إكسل")

EXCEL_FILE = "students.xlsx"

def load_students_data():
    if not os.path.exists(EXCEL_FILE):
        return None
    df = pd.read_excel(EXCEL_FILE, dtype=str)
    return df

@app.get("/api/student/search")
def search_student(seat_number: str = Query(...)):
    df = load_students_data()
    if df is None:
        raise HTTPException(status_code=500, detail="ملف البيانات غير موجود على السيرفر")
    
    seat_number = seat_number.strip()
    student_row = df[df['seat_number'].astype(str).str.strip() == seat_number]
    
    if student_row.empty:
        raise HTTPException(status_code=404, detail="رقم الجلوس غير موجود")
    
    student_name = student_row.iloc[0]['name']
    
    # تحديد المستوى
    student_level = "غير محدد"
    if 'level' in df.columns:
        student_level = student_row.iloc[0]['level']
    elif 'المستوى' in df.columns:
        student_level = student_row.iloc[0]['المستوى']
    
    if pd.isna(student_level):
        student_level = "غير محدد"
    
    # استخراج كافة المواد والدرجات الخاصة بالطلب
    excluded_cols = ['seat_number', 'name', 'level', 'المستوى']
    subject_cols = [col for col in df.columns if col not in excluded_cols]
    
    results = []
    for sub in subject_cols:
        val = student_row.iloc[0][sub]
        if pd.isna(val) or str(val).strip() == "":
            grade_str = "غير متوفرة"
        else:
            grade_str = str(val).strip()
            
        results.append({
            "subject": sub,
            "grade": grade_str
        })
    
    return {
        "seat_number": seat_number,
        "name": student_name,
        "level": str(student_level),
        "results": results
    }

@app.get("/", response_class=HTMLResponse)
def home():
    if os.path.exists("templates/index.html"):
        with open("templates/index.html", "r", encoding="utf-8") as f:
            return f.read()
    return "ملف الواجهة غير موجود"