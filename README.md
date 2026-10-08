📚 Student Grouping System

A web-based Student Grouping System built using Flask (Python) and MySQL that automates the process of creating balanced student groups for academic projects. The system includes role-based access for Admin/Teacher and Students, along with secure login and database integration.

🚀 Features
👨‍🏫 Admin / Teacher Panel
Secure login system
Add, update, delete student records
Automatically generate student groups
View all created groups
Assign students into balanced groups

👨‍🎓 Student Panel
Login system for students.
View assigned group details
View group members
Access personal profile information

⚙️ System Features
Role-based authentication (Admin / Student)
Automatic group generation algorithm
MySQL database integration
CRUD operations for student data
Session management for security
🛠️ Tech Stack

Frontend:

HTML
CSS
JavaScript
Bootstrap (optional for UI styling)

Backend:

Python (Flask Framework)

Database:

MySQL
📁 Project Structure
Student-Grouping-System/
│
├── app.py                  # Main Flask application
├── templates/              # HTML files
│   ├── login.html
│   ├── admin_dashboard.html
│   ├── student_dashboard.html
│   ├── groups.html
│
├── static/                 # CSS, JS, Images
│   ├── style.css
│
├── database.sql            # MySQL database schema
├── requirements.txt        # Python dependencies
└── README.md

The system automatically:

Fetches all students from the database
Shuffles or sorts them
Divides them into equal groups (e.g., 4–5 students per group)
Assigns a group_id to each student
Stores updated group data in MySQL

This ensures fair and balanced grouping.

This project is for academic purposes only.