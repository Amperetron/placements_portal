from flask import render_template,request,redirect,url_for,flash,send_file
from io import BytesIO
from flask_login import login_user, logout_user, login_required, current_user
from controller.models import db,User,Student,Application,Company,Job
from datetime import datetime
from sqlalchemy import or_

#Routes
def register_routes(app):
    @app.route('/')
    def home():
        return render_template('base.html')

    #Login page and authentication
    @app.route('/login',methods=['POST','GET'])
    def login():
        if request.method=='POST':
            email = request.form["email"]
            password = request.form["password"]
            user=User.query.filter_by(email=email).first()

            if not user or not user.check_password(password):
                flash('Invalid username or password','danger')
                return redirect(url_for('login'))
            
            #Blacklisting Logic
            if user.is_blacklisted:
                flash("You are blacklisted","danger")
                return redirect(url_for("login"))
            
            login_user(user)

            if user.role=="admin":
                    return redirect(url_for('admin_dashboard'))
            elif user.role=="student":
                    return redirect(url_for('student_dashboard'))
            elif user.role=="company":
                    if not user.is_approved:
                        flash("Please wait for admin's approval","warning")
                        return redirect(url_for("login"))
                    return redirect(url_for('company_dashboard'))
                    
            
        return render_template("login.html")

    #Register page
    @app.route('/register',methods=['POST','GET'])
    def register():
        role=None
        if request.method=='POST':
            email = request.form["email"]
            name=request.form["name"]
            password = request.form["password"]
            role=request.form["role"]

            #Checks if there is user already in db
            existing_user=User.query.filter_by(email=email).first()
            if existing_user:
                flash('User exists already','danger')
                return redirect(url_for('register'))
            
            #Creates an instance of user in db
            new_user=User(email=email,name=name,role=role)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()

            # create student profile
            if role == "student":
                student = Student(
                    sdept="Not Set",
                    user_id=new_user.id
                )
                db.session.add(student)


            # create company profile
            elif role == "company":
                company = Company(
                    cwebsite=request.form["cwebsite"],
                    hrcontact=request.form["hrcontact"],
                    user_id=new_user.id
                )
                db.session.add(company)

            db.session.commit()
            #Sucess msg after account creation and redirecting to login page
            flash('Account created successfully','success')
            return redirect(url_for('login'))
        return render_template("register.html")
    
    #Admin dashboard
    @app.route('/admin/dashboard')
    @login_required
    def admin_dashboard():
        if current_user.role != "admin":
            return "Unauthorized", 403
        students = Student.query.all()
        companies=Company.query.all()
        applications=Application.query.all()
        drives=Job.query.all()
        return render_template("admin_dash.html"
                               ,students=students
                               ,companies=companies
                               ,applications=applications
                               ,drives=drives)

    #Admin Students
    @app.route('/admin/students')
    @login_required
    def admin_students():
        if current_user.role != "admin":
            return "Unauthorized", 403
        search = request.args.get("search")

        if search:
            students = Student.query.join(User).filter(
                or_(
                    User.name.ilike(f"%{search}%"),
                    User.email.ilike(f"%{search}%"),
                    Student.sphone.ilike(f"%{search}%"),
                    Student.id.ilike(f"%{search}%")
                )
            ).all()
        else:
            students = Student.query.all()
        return render_template("admin_students.html", students=students)


    #Admin Company
    @app.route('/admin/company')
    @login_required
    def admin_company():
        if current_user.role != "admin":
            return "Unauthorized", 403

        search = request.args.get("search")

        if search:
            companies = Company.query.join(User).filter(
            User.name.ilike(f"%{search}%")
        ).all()
        else:
            companies = Company.query.all()

        return render_template("admin_company.html", companies=companies)

    #Admin Application
    @app.route('/admin/application')
    @login_required
    def admin_application():
        if current_user.role != "admin":
            return "Unauthorized", 403
        applications = Application.query.all()

        return render_template("admin_application.html",applications=applications)

    #Admin Drive page
    @app.route('/admin/drives')
    @login_required
    def admin_drives():
        if current_user.role != "admin":
            return "Unauthorized", 403
        drives = Job.query.all()
        return render_template('admin_drives.html',drives=drives)

    #Drive details
    @app.route('/drive/<int:id>')
    @login_required
    def view_drive(id):
        drive = Job.query.get_or_404(id)

        # Students → only approved drives
        if current_user.role == "student" and not drive.status=="approved":
            return "Unauthorized", 403

        # Company → only their own drives
        if current_user.role == "company":
            if drive.cid != current_user.company.id:
                return "Unauthorized", 403

        return render_template('drive_view.html', drive=drive)

    #Approve Drive Route
    @app.route("/drive/approve/<int:id>")
    @login_required
    def approve_drive(id):
        if current_user.role != "admin":
            return "Unauthorized", 403
        drive=Job.query.filter_by(id=id).first_or_404()
        drive.status="approved"
        db.session.commit()
        return redirect(url_for("admin_drives"))

    #Reject Drive Route
    @app.route("/drive/reject/<int:id>")
    @login_required
    def reject_drive(id):
        if current_user.role != "admin":
            return "Unauthorized", 403
        drive=Job.query.filter_by(id=id).first_or_404()
        drive.status="rejected"
        db.session.commit()
        return redirect(url_for("admin_drives"))

    #Student Homepage
    @app.route('/student/dashboard')
    @login_required
    def student_dashboard():
        if current_user.role != "student":
            return "Unauthorized", 403
        drives=Job.query.filter_by(status="approved").all()
        applications = Application.query.filter_by(
            sid=current_user.student.id
        ).all()
        applied_job_ids = {app.jid for app in applications}
        application_dates = {app.jid: app.application_date for app in applications}
        application_status = {app.jid: app.status for app in applications}
        return render_template("student_dash.html",drives=drives,applied_job_ids=applied_job_ids,application_dates=application_dates,application_status=application_status)

     #History of applied drives of student
    @app.route('/student/history')
    @login_required
    def history_data():
        if current_user.role != "student":
            return "Unauthorized", 403
        drives=Job.query.filter_by(status="approved").all()
        applications = Application.query.filter_by(
            sid=current_user.student.id
        ).all()
        applied_job_ids = {app.jid for app in applications}
        application_dates = {app.jid: app.application_date for app in applications}
        application_status = {app.jid: app.status for app in applications}
        return render_template("student_history.html",drives=drives,applied_job_ids=applied_job_ids,application_status=application_status,application_dates=application_dates)


    #View Resume from student's pov
    @app.route('/resume/<int:student_id>')
    @login_required
    def view_resume(student_id):
        student = Student.query.get_or_404(student_id)

    # If student is logged in → only allow their own resume
        if current_user.role == "student":
            if current_user.student.id != student_id:
             return "Unauthorized", 403

        if not student.resume:
            return "No resume uploaded", 404

        return send_file(
        BytesIO(student.resume),
        download_name="resume.pdf",
        as_attachment=False
    )

    #Edit profile
    @app.route('/student/profile', methods=['GET','POST'])
    @login_required
    def edit_profile():
        if current_user.role != "student":
            return "Unauthorized", 403

        student = current_user.student
        if request.method == 'POST':
            current_user.name = request.form["name"]

            if request.form["passwd"]:
                current_user.set_password(request.form["passwd"])
            student.sphone = int(request.form["sphone"]) if request.form["sphone"] else None
            student.sdept = request.form["sdept"]
            student.scgpa = request.form["scgpa"]
            file = request.files.get("resume")
            if file and file.filename != "":
                student.resume = file.read()
            db.session.commit()
            flash("Student profile updated", "success")
            return redirect(url_for("student_dashboard"))
        return render_template("student_edit_profile.html", student=student)
    
    @app.route('/company/profile', methods=['GET','POST'])
    @login_required
    def edit_profile_company():
        if current_user.role != "company":
            return "Unauthorized", 403

        company = current_user.company
        if request.method == 'POST':
            print(request.form)
            current_user.name = request.form["name"]

            if request.form["passwd"]:
                current_user.set_password(request.form["passwd"])
            company.hrcontact = int(request.form["hrcontact"]) if request.form["hrcontact"] else None
            company.cwebsite = request.form["website"]
            db.session.commit()
            
            flash("Company profile updated", "success")
            return redirect(url_for("company_dashboard"))
        return render_template("company_edit_profile.html", company=company)


    #Company Homepage
    @app.route('/company/dashboard')
    @login_required
    def company_dashboard():
        if current_user.role != "company":
            return "Unauthorized", 403
        company = Company.query.filter_by(user_id=current_user.id).first()
        drives = Job.query.filter_by(cid=company.id).all()
        # Extracts all drives,store in form of list and by using that list all applicants are displayed in dashboard
        drive_ids = [drive.id for drive in drives]
        total_applicants = Application.query.filter(
    Application.jid.in_(drive_ids)
).count()
        return render_template("company_dash.html",drives=drives,total_applicants=total_applicants)
    
    
    @app.route('/company/applicants/<int:id>')
    @login_required
    def drive_applicants(id):
       if current_user.role != "company":
            return "Unauthorized", 403
       drive = Job.query.filter_by(id=id).first_or_404()
       applications = Application.query.filter_by(
    jid=drive.id
).all()
       return render_template('drive_applicants.html',drive=drive,applications=applications)

    #Closing drives
    @app.route('/company/complete_drive/<int:id>')
    @login_required
    def close_drive(id):
        if current_user.role != "company":
            return "Unauthorized", 403
        drive = Job.query.get_or_404(id)
        drive.status = "Closed"
        db.session.commit()
        return redirect(url_for("company_dashboard"))

    #Delete drive
    @app.route('/company/delete_drive/<int:id>')
    @login_required
    def drive_delete(id):
        if current_user.role != "company":
            return "Unauthorized", 403
        company = Company.query.filter_by(user_id=current_user.id).first()
        drive = Job.query.filter_by(id=id, cid=company.id).first_or_404()
        db.session.delete(drive)
        db.session.commit()
        flash("Drive deleted successfully","danger")
        return redirect(url_for('company_dashboard'))

    #Create Drive
    @app.route('/company/drive',methods=['GET','POST'])
    @login_required
    def company_drive():
        if current_user.role != "company":
            return "Unauthorized", 403
        if request.method=='POST':
            jtitle=request.form["jtitle"]
            jdesc=request.form["jdesc"]
            salary=request.form["salary"]
            location=request.form["location"]
            deadline_str=request.form["deadline"]
            deadline = datetime.strptime(deadline_str, "%Y-%m-%d").date()

            company = Company.query.filter_by(user_id=current_user.id).first()
            new_drive = Job(
            jtitle=jtitle,
            jdesc=jdesc,
            deadline=deadline,
            salary=salary,
            location=location,
            cid=company.id,
            )
            db.session.add(new_drive)
            db.session.commit()
            flash('Drive created successfully','success')
            return redirect(url_for("company_dashboard"))
        return render_template("company_drive.html")

    #Edit Drive
    @app.route('/company/drive/<int:id>', methods=['GET','POST'])
    @login_required
    def edit_drive(id):
        if current_user.role != "company":
            return "Unauthorized", 403
        company = Company.query.filter_by(user_id=current_user.id).first()
        drive = Job.query.filter_by(id=id, cid=company.id).first_or_404()
        if request.method == 'POST':
            drive.jtitle = request.form["jtitle"]
            drive.jdesc = request.form["jdesc"]
            drive.salary=request.form["salary"]
            deadline_str = request.form["deadline"]
            drive.deadline = datetime.strptime(deadline_str, "%Y-%m-%d").date()
            db.session.commit()
            flash("Drive updated successfully", "success")
            return redirect(url_for("company_dashboard"))
        return render_template("company_drive_edit.html", drive=drive)


    #BlackList Student Route
    @app.route("/student/blacklist/<int:id>")
    @login_required
    def blacklist_student(id):
        if current_user.role != "admin":
            return "Unauthorized", 403

        student = User.query.filter_by(id=id, role="student").first_or_404()
        student.is_blacklisted = True
        student.is_approved=False
        db.session.commit()
        return redirect(url_for("admin_students"))

    #Approve Student Route
    @app.route("/student/approve/<int:id>")
    @login_required
    def approve_student(id):
        if current_user.role != "admin":
            return "Unauthorized", 403

        student = User.query.filter_by(id=id, role="student").first_or_404()
        student.is_blacklisted = False
        student.is_approved=True
        db.session.commit()
        return redirect(url_for("admin_students"))

    #BlackList Company Route
    @app.route("/company/blacklist/<int:id>")
    @login_required
    def blacklist_company(id):
        if current_user.role != "admin":
            return "Unauthorized", 403

        company = User.query.filter_by(id=id, role="company").first_or_404()
        company.is_blacklisted = True
        company.is_approved=False
        db.session.commit()
        return redirect(url_for("admin_company"))

    #Approve Company Route
    @app.route("/company/approve/<int:id>")
    @login_required
    def approve_company(id):
        if current_user.role != "admin":
            return "Unauthorized", 403
        company = User.query.filter_by(id=id, role="company").first_or_404()
        company.is_blacklisted = False
        company.is_approved=True
        db.session.commit()
        return redirect(url_for("admin_company"))

    #Apply Drive Route
    @app.route('/apply/<int:id>')
    @login_required
    def apply_drive(id):
        if current_user.role != "student":
            return "Unauthorized", 403

        drive = Job.query.get_or_404(id)
        student = current_user.student

        # Check if already applied
        existing = Application.query.filter_by(
            jid=drive.id,
            sid=student.id
        ).first()

        if existing:
            return redirect(url_for("student_dashboard"))

        # Create application only if not exists
        application = Application(
            jid=drive.id,
            sid=student.id,
            application_date=datetime.now().date(),
            status="applied"
        )

        db.session.add(application)
        db.session.commit()

        return redirect(url_for("student_dashboard"))

    #Shortlist applicant route
    @app.route('/company/shortlist/<int:drive_id>/<int:student_id>')
    @login_required
    def shortlist_app(drive_id, student_id):
        if current_user.role != "company":
            return "Unauthorized", 403

        application = Application.query.filter_by(
        jid=drive_id,
        sid=student_id
    ).first_or_404()

        application.status = "shortlisted"
        db.session.commit()

        return redirect(url_for("drive_applicants", id=drive_id))
    #Select applicant
    @app.route('/company/approve/<int:drive_id>/<int:student_id>')
    @login_required
    def select_app(drive_id, student_id):
        if current_user.role != "company":
            return "Unauthorized", 403

        application = Application.query.filter_by(
        jid=drive_id,
        sid=student_id
    ).first_or_404()

        application.status = "selected"
        db.session.commit()

        return redirect(url_for("drive_applicants", id=drive_id))
    
    
    #Reject applicant route
    @app.route('/company/reject/<int:drive_id>/<int:student_id>')
    @login_required
    def reject_app(drive_id, student_id):
        if current_user.role != "company":
            return "Unauthorized", 403

        application = Application.query.filter_by(
        jid=drive_id,
        sid=student_id
    ).first_or_404()

        application.status = "rejected"
        db.session.commit()

        return redirect(url_for("drive_applicants", id=drive_id))
    
    
    # Logout route
    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        return redirect(url_for("home"))