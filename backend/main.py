from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import get_connection, create_table

app = FastAPI()

# Frontend ko backend se connect karne ke liye
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database table create
create_table()


class Student(BaseModel):
    name: str
    email: str
    password: str
    district: str
    training: str


@app.get("/")
def home():
    return {"message": "SkillGap Backend is running"}


@app.post("/register")
def register_student(student: Student):

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO students
            (name, email, password, district, training)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                student.name,
                student.email,
                student.password,
                student.district,
                student.training,
            ),
        )

        connection.commit()

    except Exception:
        connection.close()
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    connection.close()

    return {
        "message": "Student registered successfully"
    }


class LoginData(BaseModel):
    email: str
    password: str


@app.post("/login")
def login_student(data: LoginData):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT id, name, email FROM students WHERE email = ? AND password = ?",
        (data.email, data.password)
    )

    student = cursor.fetchone()
    connection.close()

    if student is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    return {
        "message": "Login successful",
        "student_id": student[0],
        "name": student[1],
        "email": student[2]
    }


@app.get("/students/{student_id}")
def get_student(student_id: int):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT id, name, email, district, training, employment_status, skills, training_status, certification_status FROM students WHERE id = ?",
        (student_id,)
    )

    student = cursor.fetchone()

    connection.close()

    if student is None:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    return {
        "id": student[0],
        "name": student[1],
        "email": student[2],
        "district": student[3],
        "training": student[4],
        "employment_status":student[5],
        "skills": student[6],
        "training_status": student[7],
        "certification_status": student[8]
    }

class ProfileUpdateData(BaseModel):
    district: str
    training: str


@app.put("/students/{student_id}/profile")
def update_profile(student_id: int, data: ProfileUpdateData):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE students
        SET district = ?, training = ?
        WHERE id = ?
        """,
        (data.district, data.training, student_id)
    )

    connection.commit()

    if cursor.rowcount == 0:
        connection.close()
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    connection.close()

    return {
        "message": "Profile updated successfully"
    }  

@app.get("/officer/stats")
def get_officer_stats():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]

    cursor.execute("""
    SELECT COUNT(*) FROM students
    WHERE employment_status IN ('employed', 'self-employed', 'apprenticeship')
""")
    employed_students = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*) FROM students
        WHERE employment_status = 'not-employed'
    """)
    unemployed_students = cursor.fetchone()[0]

    if total_students > 0:
        employment_rate = round(
            (employed_students / total_students) * 100, 2
        )
    else:
        employment_rate = 0

    connection.close()

    return {
        "total_students": total_students,
        "employed_students": employed_students,
        "unemployed_students": unemployed_students,
        "employment_rate": employment_rate
    }
    
class EmploymentData(BaseModel):
    employment_status: str


@app.put("/students/{student_id}/employment")
def update_employment(student_id: int, data: EmploymentData):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE students
        SET employment_status = ?
        WHERE id = ?
        """,
        (data.employment_status, student_id)
    )

    connection.commit()

    if cursor.rowcount == 0:
        connection.close()
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    connection.close()

    return {
        "message": "Employment status updated successfully",
        "employment_status": data.employment_status
    }

class SkillsData(BaseModel):
    skills: str


@app.put("/students/{student_id}/skills")
def update_skills(student_id: int, data: SkillsData):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE students
        SET skills = ?
        WHERE id = ?
        """,
        (data.skills, student_id)
    )

    connection.commit()

    if cursor.rowcount == 0:
        connection.close()
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    connection.close()

    return {
        "message": "Skills updated successfully",
        "skills": data.skills
    }

@app.get("/officer/skill-gaps")
def get_skill_gaps():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT skills FROM students")
    rows = cursor.fetchall()

    connection.close()

    skill_count = {}

    for row in rows:
        skills = row[0]

        if skills:
            for skill in skills.split(","):
                skill = skill.strip()

                if skill:
                    skill_count[skill] = skill_count.get(skill, 0) + 1

    return {
        "skill_data": skill_count
    }

@app.get("/officer/skill-recommendations")
def get_skill_recommendations():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT skills FROM students")
    rows = cursor.fetchall()

    connection.close()

    recommendations = {}

    skill_map = {
        "Hardware Devloper": [
            "Embedded Systems",
            "Microcontrollers",
            "IoT"
        ],
        "Web Developer": [
            "JavaScript",
            "React",
            "Backend Development"
        ],
        "Python Developer": [
            "Python",
            "SQL",
            "APIs"
        ],
        "Data Analyst": [
            "Python",
            "SQL",
            "Data Visualization"
        ],
        "AI ML": [
    "Python",
    "Machine Learning",
    "Deep Learning"
],
       
    }

    for row in rows:

        skills = row[0]

        if not skills:
            continue

        for skill in skills.split(","):

            skill = skill.strip()

            if skill in skill_map:
                recommendations[skill] = skill_map[skill]

    return {
        "recommendations": recommendations
    }


@app.get("/officer/district-stats")
def get_district_stats():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            district,
            COUNT(*) AS total_students,
            SUM(
                CASE
                    WHEN employment_status = 'employed'
                    THEN 1
                    ELSE 0
                END
            ) AS employed_students
        FROM students
        WHERE district IS NOT NULL AND district != ''
        GROUP BY district
        ORDER BY total_students DESC
    """)

    rows = cursor.fetchall()
    connection.close()

    district_data = []

    for row in rows:
        district = row[0]
        total_students = row[1]
        employed_students = row[2] or 0

        if total_students > 0:
            employment_rate = round(
                (employed_students / total_students) * 100, 2
            )
        else:
            employment_rate = 0

        district_data.append({
            "district": district,
            "students": total_students,
            "employed": employed_students,
            "employment_rate": employment_rate
        })

    return {
        "district_data": district_data
    }

@app.get("/officer/district-stats")
def get_district_stats():

    connection = get_connection()
    cursor = connection.cursor()

    # district wala code...

    return {
        "district_data": district_data
    }


@app.get("/officer/training-stats")
def get_training_stats():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            training,
            COUNT(*) AS total_students,
            SUM(
                CASE
                    WHEN employment_status = 'employed'
                    THEN 1
                    ELSE 0
                END
            ) AS employed_students
        FROM students
        WHERE training IS NOT NULL AND training != ''
        GROUP BY training
        ORDER BY total_students DESC
    """)

    rows = cursor.fetchall()
    connection.close()

    training_data = []

    for row in rows:
        training = row[0]
        total_students = row[1]
        employed_students = row[2] or 0

        if total_students > 0:
            employment_rate = round(
                (employed_students / total_students) * 100, 2
            )
        else:
            employment_rate = 0

        training_data.append({
            "training": training,
            "students": total_students,
            "employed": employed_students,
            "employment_rate": employment_rate
        })

    return {
        "training_data": training_data
    } 

import json
import os

@app.get("/officer/government-skill-gaps")
def get_government_skill_gaps():

    file_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "government_skill_gap.json"
    )

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            government_data = json.load(file)

        return {
            "source": "Maharashtra Skill Gap Analysis Report 2023",
            "data": government_data
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Government data load failed: {str(error)}"
        )   



