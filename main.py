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
    
    # جلب قيمة المستوى سواء كان اسم العمود level أو المستوى
    student_level = "غير محدد"
    if 'level' in df.columns:
        student_level = student_row.iloc[0]['level']
    elif 'المستوى' in df.columns:
        student_level = student_row.iloc[0]['المستوى']
    
    if pd.isna(student_level):
        student_level = "غير محدد"
    
    # المواد المتاحة هي الأعمدة باستثناء رقم الجلوس والاسم والمستوى
    excluded_cols = ['seat_number', 'name', 'level', 'المستوى']
    subjects = [col for col in df.columns if col not in excluded_cols]
    
    return {
        "seat_number": seat_number,
        "name": student_name,
        "level": str(student_level),
        "subjects": subjects
    }

@app.get("/api/student/grade")
def get_grade(seat_number: str = Query(...), subject: str = Query(...)):
    df = load_students_data()
    if df is None:
        raise HTTPException(status_code=500, detail="ملف البيانات غير موجود")
    
    seat_number = seat_number.strip()
    student_row = df[df['seat_number'].astype(str).str.strip() == seat_number]
    
    if student_row.empty:
        raise HTTPException(status_code=404, detail="بيانات غير موجودة")
    
    if subject not in df.columns:
        raise HTTPException(status_code=400, detail="المادة غير صحيحة")
    
    grade_val = student_row.iloc[0][subject]
    if pd.isna(grade_val):
        grade_val = "غير متوفرة"
        
    student_name = student_row.iloc[0]['name']
    
    return {
        "name": student_name,
        "subject": subject,
        "grade": grade_val
    }

@app.get("/", response_class=HTMLResponse)
def home():
    if os.path.exists("templates/index.html"):
        with open("templates/index.html", "r", encoding="utf-8") as f:
            return f.read()
    return "ملف الواجهة غير موجود"