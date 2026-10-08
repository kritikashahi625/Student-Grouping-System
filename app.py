from flask import Flask, request, render_template, redirect, url_for, session, flash
import mysql.connector
from math import sqrt

app = Flask(__name__)
app.secret_key = "supersecretkey"

# ------------------------ DB CONNECTION ------------------------
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="studentgrouper",
        use_pure=True
    )

# ------------------------ INIT DB ------------------------
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255),
        email VARCHAR(255),
        password VARCHAR(255),
        Communication_Skills FLOAT,
        Leadership FLOAT,
        Technical_Skill FLOAT,
        Teamwork FLOAT,
        Problem_Solving_Skill FLOAT,
        Creativity_Skill FLOAT,
        Adaptability_Skill FLOAT,
        Attendance FLOAT,
        cluster INT DEFAULT -1
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS teachers (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100),
        email VARCHAR(100) UNIQUE,
        password VARCHAR(255)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS student_groups (
        id INT AUTO_INCREMENT PRIMARY KEY,
        group_number INT,
        member_name VARCHAR(255)
    )
    """)

    conn.commit()
    cursor.close()
    conn.close()

init_db()

# ------------------------ HOME ------------------------
@app.route("/")
def home():
    return render_template("index.html")

# ------------------------ LOGIN ------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        if email == "admin@school.com" and password == "admin123":
            session["user_role"] = "admin"
            return redirect(url_for("admin_dashboard"))

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM students WHERE email=%s", (email,))
        student = cursor.fetchone()

        cursor.execute("SELECT * FROM teachers WHERE email=%s", (email,))
        teacher = cursor.fetchone()

        cursor.close()
        conn.close()

        if student and student["password"] == password:
            session["user_role"] = "student"
            session["user_id"] = student["id"]
            return redirect(url_for("student_dashboard"))

        if teacher and teacher["password"] == password:
            session["user_role"] = "teacher"
            session["user_id"] = teacher["id"]
            return redirect(url_for("teacher_dashboard"))

        flash("Invalid email or password", "error")
        return redirect(url_for("login"))

    return render_template("login.html")

# ------------------------ LOGOUT ------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ------------------------ DASHBOARDS ------------------------
@app.route("/student")
def student_dashboard():
    if session.get("user_role") != "student":
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Get logged-in student
    student_id = session.get("user_id")
    cursor.execute("SELECT * FROM students WHERE id=%s", (student_id,))
    student = cursor.fetchone()

    # Get group (only group number)
    cursor.execute("SELECT group_number FROM student_groups WHERE member_name=%s", (student["name"],))
    group = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template(
        "student_dashboard.html",
        student=student,
        group=group
    )
def get_group_members(student_name):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Get student's group number
    cursor.execute("SELECT group_number FROM student_groups WHERE member_name=%s", (student_name,))
    row = cursor.fetchone()
    if not row:
        cursor.close()
        conn.close()
        return []

    group_number = row["group_number"]

    # Get all members in the same group
    cursor.execute("SELECT member_name FROM student_groups WHERE group_number=%s", (group_number,))
    members = [r["member_name"] for r in cursor.fetchall()]

    cursor.close()
    conn.close()
    return members



@app.route("/admin")
def admin_dashboard():
    if session.get("user_role") != "admin":
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM teachers")
    total_teachers = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT group_number) FROM student_groups")
    total_groups = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return render_template("admindashboard.html",
                           total_students=total_students,
                           total_teachers=total_teachers,
                           total_groups=total_groups)

# ------------------------ STUDENTS ------------------------
@app.route("/admin/students")
def students():
    if session.get("user_role") != "admin":
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM students")
    data = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("students.html", students=data)

# ------------------------ ADD STUDENT ------------------------
@app.route("/admin/add-student", methods=["POST"])
def add_student():
    if session.get("user_role") != "admin":
        return redirect(url_for("login"))

    student = request.form
    name = student.get("name")
    email = student.get("email")
    password = student.get("password", "student123")  # default password

    if not name or not email:
        flash("Name and Email are required!", "error")
        return redirect(url_for("students"))

    communication = float(student.get("Communication_Skills", 0))
    leadership = float(student.get("Leadership", 0))
    technical = float(student.get("Technical_Skill", 0))
    teamwork = float(student.get("Teamwork", 0))
    problem_solving = float(student.get("Problem_Solving_Skill", 0))
    creativity = float(student.get("Creativity_Skill", 0))
    adaptability = float(student.get("Adaptability_Skill", 0))
    attendance = float(student.get("Attendance", 0))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO students (
            name, email, password, Communication_Skills, Leadership, Technical_Skill,
            Teamwork, Problem_Solving_Skill, Creativity_Skill, Adaptability_Skill, Attendance
        ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        name, email, password, communication, leadership, technical, teamwork,
        problem_solving, creativity, adaptability, attendance
    ))
    conn.commit()
    cursor.close()
    conn.close()

    flash(f"Student {name} added successfully!", "success")
    return redirect(url_for("students"))

# ------------------------ ✅ ADMIN TEACHERS ------------------------
@app.route("/admin/teachers")
def teachers():
    if session.get("user_role") != "admin":
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM teachers")
    data = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("teachers.html", teachers=data)

# ------------------------ ADD TEACHER ------------------------
@app.route("/admin/add-teacher", methods=["POST"])
def add_teacher():
    if session.get("user_role") != "admin":
        return redirect(url_for("login"))

    name = request.form.get("name")
    email = request.form.get("email")
    password = request.form.get("password")

    if not name or not email or not password:
        flash("All fields are required!", "error")
        return redirect(url_for("teachers"))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO teachers (name, email, password) VALUES (%s, %s, %s)",
        (name, email, password)
    )
    conn.commit()
    cursor.close()
    conn.close()

    flash("Teacher added successfully!", "success")
    return redirect(url_for("teachers"))

# ------------------------ DELETE TEACHER ------------------------
@app.route("/admin/delete-teacher/<int:id>")
def delete_teacher(id):
    if session.get("user_role") != "admin":
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM teachers WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()

    flash("Teacher deleted successfully!", "success")
    return redirect(url_for("teachers"))

# ------------------------ TEACHER VIEW ------------------------
@app.route("/teacher/teachers")
def teacher_teachers():
    if session.get("user_role") != "teacher":
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM teachers")
    data = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("teachers.html", teachers=data)


# ------------------------ KNN FUNCTIONS ------------------------
from math import sqrt

def euclidean_distance(s1, s2):
    features = [
        "Communication_Skills", "Leadership", "Technical_Skill",
        "Teamwork", "Problem_Solving_Skill", "Creativity_Skill",
        "Adaptability_Skill", "Attendance"
    ]
    return sqrt(sum((s1[f] - s2[f])**2 for f in features))

def knn_grouping(students, k=3):
    groups = []
    students_copy = students.copy()

    while students_copy:
        s = students_copy[0]
        if len(students_copy) < k:
            group = students_copy
            students_copy = []
        else:
            distances = [(other, euclidean_distance(s, other)) for other in students_copy[1:]]
            distances.sort(key=lambda x: x[1])
            group = [s] + [d[0] for d in distances[:k-1]]
            for member in group:
                students_copy.remove(member)
        groups.append(group)
    return groups

# ------------------------ FLASK ROUTE ------------------------
@app.route("/admin/generate-groups", methods=["POST"])
def generate_groups():
    if session.get("user_role") != "admin":
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()

    if len(students) < 3:
        flash("Need at least 3 students!", "danger")
        cursor.close()
        conn.close()
        return redirect(url_for("students"))

    # Clear previous groups
    cursor.execute("DELETE FROM student_groups")
    conn.commit()

    # Ensure skill values are numbers
    for s in students:
        for f in ["Communication_Skills", "Leadership", "Technical_Skill",
                  "Teamwork", "Problem_Solving_Skill", "Creativity_Skill",
                  "Adaptability_Skill", "Attendance"]:
            if s[f] is None:
                s[f] = 0

    # Generate groups using KNN
    grouped_students = knn_grouping(students, k=3)

    # Insert into DB
    for group_number, group in enumerate(grouped_students, start=1):
        for s in group:
            cursor.execute(
                "INSERT INTO student_groups (group_number, member_name) VALUES (%s,%s)",
                (group_number, s["name"])
            )

    conn.commit()
    cursor.close()
    conn.close()

    flash("Groups generated successfully!", "success")
    return redirect(url_for("view_groups"))

# ------------------------ VIEW GROUPS ------------------------
@app.route("/admin/view-groups")
def view_groups():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM student_groups")
    all_students = cursor.fetchall()
    cursor.close()
    conn.close()

    groups = {}
    for s in all_students:
        group_number = s['group_number']
        if group_number not in groups:
            groups[group_number] = []
        groups[group_number].append(s['member_name'])

    return render_template("generated_groups.html", groups=groups)  

@app.route("/admin/delete-student/<int:id>")
def delete_student(id):
    if session.get("user_role") != "admin":
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM students WHERE id = %s", (id,))
    conn.commit()

    cursor.close()
    conn.close()

    flash("Student deleted successfully!", "success")
    return redirect(url_for("students"))

@app.route("/teacher/view-students")
def view_students():
    if session.get("user_role") != "teacher":
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("teacher_dashboard.html", students=students)

# Teacher Dashboard
@app.route("/teacher/dashboard")
def teacher_dashboard():
    if session.get("user_role") != "teacher":
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch students
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()

    # Fetch groups
    cursor.execute("SELECT group_number, member_name FROM student_groups")
    raw_groups = cursor.fetchall()
    groups = {}
    for row in raw_groups:
        groups.setdefault(row['group_number'], []).append(row['member_name'])

    cursor.close()
    conn.close()

    return render_template(
        "teacher_dashboard.html",
        students=students,
        groups=groups
    )

# Generate groups (teacher)
@app.route("/teacher/generate-groups", methods=["POST"])
def teacher_generate_groups():
    if session.get("user_role") != "teacher":
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch all students
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()

    # Check minimum students
    if len(students) < 3:
        flash("Need at least 3 students!", "danger")
        cursor.close()
        conn.close()
        return redirect(url_for("teacher_dashboard"))

    # Clear previous groups
    cursor.execute("DELETE FROM student_groups")
    conn.commit()

    # ✅ FIX 1: Handle NULL values
    for s in students:
        for f in ["Communication_Skills", "Leadership", "Technical_Skill",
                  "Teamwork", "Problem_Solving_Skill", "Creativity_Skill",
                  "Adaptability_Skill", "Attendance"]:
            if s[f] is None:
                s[f] = 0

    # ✅ FIX 2: SORT students (HIGH → LOW)
    students.sort(key=lambda s: (
        s["Communication_Skills"] +
        s["Leadership"] +
        s["Technical_Skill"] +
        s["Teamwork"] +
        s["Problem_Solving_Skill"] +
        s["Creativity_Skill"] +
        s["Adaptability_Skill"] +
        s["Attendance"]
    ), reverse=True)

    # ✅ KNN FUNCTIONS (clean)
    def euclidean_distance(s1, s2):
        features = ["Communication_Skills", "Leadership", "Technical_Skill",
                    "Teamwork", "Problem_Solving_Skill", "Creativity_Skill",
                    "Adaptability_Skill", "Attendance"]
        return sum((s1[f] - s2[f])**2 for f in features) ** 0.5

    def knn_grouping(students, k=3):
        groups = []
        students_copy = students.copy()

        while students_copy:
            s = students_copy[0]

            if len(students_copy) < k:
                group = students_copy
                students_copy = []
            else:
                distances = [
                    (other, euclidean_distance(s, other))
                    for other in students_copy[1:]
                ]
                distances.sort(key=lambda x: x[1])

                group = [s] + [d[0] for d in distances[:k-1]]

                for member in group:
                    students_copy.remove(member)

            groups.append(group)

        return groups

    # Generate groups
    grouped_students = knn_grouping(students, k=3)

    # Insert into DB
    group_number = 1
    for group in grouped_students:
        for s in group:
            cursor.execute(
                "INSERT INTO student_groups (group_number, member_name) VALUES (%s,%s)",
                (group_number, s["name"])
            )
        group_number += 1

    conn.commit()
    cursor.close()
    conn.close()

    flash("Groups generated successfully!", "success")
    return redirect(url_for("teacher_dashboard"))

@app.route("/teacher/add-student", methods=["POST"])
def teacher_add_student():
    if session.get("user_role") != "teacher":
        return redirect(url_for("login"))

    student = request.form
    name = student.get("name")
    email = student.get("email")

    if not name or not email:
        flash("Name and Email are required!", "error")
        return redirect(url_for("teacher_dashboard"))

    communication = float(student.get("Communication_Skills", 0))
    leadership = float(student.get("Leadership", 0))
    technical = float(student.get("Technical_Skill", 0))
    teamwork = float(student.get("Teamwork", 0))
    problem_solving = float(student.get("Problem_Solving_Skill", 0))
    creativity = float(student.get("Creativity_Skill", 0))
    adaptability = float(student.get("Adaptability_Skill", 0))
    attendance = float(student.get("Attendance", 0))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO students (
            name, email, Communication_Skills, Leadership, Technical_Skill,
            Teamwork, Problem_Solving_Skill, Creativity_Skill, Adaptability_Skill, Attendance
        ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        name, email, communication, leadership, technical, teamwork,
        problem_solving, creativity, adaptability, attendance
    ))
    conn.commit()
    cursor.close()
    conn.close()

    flash(f"Student {name} added successfully!", "success")
    return redirect(url_for("teacher_dashboard"))

@app.route("/teacher/delete-student/<int:id>")
def teacher_delete_student(id):
    if session.get("user_role") != "teacher":
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()

    flash("Student deleted successfully!", "success")
    return redirect(url_for("teacher_dashboard"))

    
# ------------------------ RUN ------------------------
if __name__ == "__main__":
    app.run(debug=True)