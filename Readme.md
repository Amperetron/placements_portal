# Placement Portal Application
The Goal of this project was to develop a web-based platform that streamlines and manages campus recruitment activities for institutes, companies, and students.

###NOTE
> This project is just a prototype and not under active development


---

## Problem Statement

Many institutes still rely on spreadsheets, emails, or manual processes to manage placement activities. This leads to:

- Difficulty in managing company approvals  
- Inefficient tracking of student applications  
- Duplicate registrations  
- Poor maintenance of placement records  

This project aims to build a centralized system to solve these issues efficiently.
---

## Solution

The **Placement Portal Application** is a role-based web system that connects:

-  Admin (Institute Placement Cell)  
-  Companies  
-  Students  

It automates placement workflows including company approvals, job postings, student applications, and recruitment tracking.

---

## Core Features

### Authentication
- Role-based login system (Admin, Company, Student)
- Registration allowed for Company and Student
- Admin is pre-defined (no registration)

---

### Admin Functionalities
- Approve/reject company registrations  
- Approve/reject placement drives  
- View all students, companies, and applications  
- Search students (name, ID, contact)  
- Search companies (name)  
- Blacklist or deactivate users  
- Dashboard analytics:
  - Total students  
  - Total companies  
  - Total applications  
  - Total placement drives  

---

### 🏢 Company Functionalities
- Register and manage profile  
- Login after admin approval  
- Create, edit, delete, and close placement drives  
- View applicants per drive  
- Shortlist candidates  
- Update application status:
  - Shortlisted  
  - Selected  
  - Rejected  

---

### Student Functionalities
- Register and manage profile  
- Upload resume  
- View approved placement drives  
- Apply for drives  
- Track application status  
- View placement history  

---

## Additional Functionalities

- Prevent duplicate applications  
- Only approved companies can create drives  
- Dynamic application status updates  
- Maintain complete placement history  
- Admin access to all historical data  
---

## Tech Stack

**Backend:**
- Flask  

**Frontend:**
- Jinja2 Templates  
- HTML  
- CSS  
- Bootstrap  

**Database:**
- SQLite  

---

## Installation & Setup

```bash
# Clone repository
git clone https://github.com/your-username/placement-portal

# Navigate into project
cd placement-portal

# Install dependencies
pip install -r requirements.txt
```

# Run the application
python app.py
