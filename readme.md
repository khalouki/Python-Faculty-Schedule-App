# 🎓 Faculty Schedule Management Web Application

A **web application for managing faculty schedules** built with **Flask** and HTML templates.  

This project is designed for:

- **Students**: to check their class schedules  
- **Teachers**: to view their teaching schedules  
- **Admin staff**: to create, edit, and manage schedules  

It demonstrates **backend development with Flask**, **role-based functionality**, **template rendering**, and **basic web security practices** with a **MySQL database**.

---

## ✨ Features

- 🗓️ View schedules by user type (student/teacher)  
- 👩‍🏫 Admin can add, edit, or delete schedules  
- 🔐 User authentication for students, teachers, and admins  
- 🛡️ Security measures:
  - Parameterized queries to prevent SQL Injection
  - Input validation and escaping to prevent XSS
  - Secure password hashing

---

## 🖼️ Screenshots
<p align="center">
  <img src="https://github.com/user-attachments/assets/b508cd14-7388-4fcc-828d-7c9c19fbacbc" width="450" />
  <img src="https://github.com/user-attachments/assets/cf7a3e64-da7b-4a20-95c4-0b3dda68832b" width="450" />
  <img src="https://github.com/user-attachments/assets/b75944ff-6ff2-4a32-a9b6-21a298baa10f"  width="450" />
  <img src="https://github.com/user-attachments/assets/8d815a36-0ba8-4953-92c3-ffe3376fddbd"  width="450" />
</p>
---

## 🛠️ Tech Stack

- **Backend**: Python, Flask  
- **Frontend**: HTML, CSS, Jinja2 templates  
- **Database**: MySQL  
- **Security**: Parameterized queries, input sanitization, password hashing  

---

## 📂 Project Structure

```bash
faculty-management/
│
├── core/                 # Main Flask app folder
├── pattern/              # Helper functions / business logic
├── routes/               # Flask route definitions
├── static/               # CSS, JS, images
├── templates/            # HTML templates
├── app.py                # 
└── requirements.txt      # Python dependencies
