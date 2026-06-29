from calendar import monthrange
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from datetime import datetime, date
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import os
from sqlalchemy import extract

app = Flask(__name__)

# ── Configuration ─────────────────────────────────────────────────────────────
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'change-me-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 'mysql+pymysql://root:@localhost:3306/eduprime'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER']         = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT']           = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS']        = True
app.config['MAIL_USERNAME']       = os.environ.get('MAIL_USERNAME', '')
app.config['MAIL_PASSWORD']       = os.environ.get('MAIL_PASSWORD', '')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'admissions@eduprime.com')

db   = SQLAlchemy(app)
mail = Mail(app)

# ── Frontend ──────────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')

# ══════════════════════════════════════════════════════════════════════════════
# MODELS
# ══════════════════════════════════════════════════════════════════════════════

class Inquiry(db.Model):
    __tablename__ = 'inquiries'
    id           = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_name = db.Column(db.String(120), nullable=False)
    grade        = db.Column(db.String(50),  nullable=False)
    parent_name  = db.Column(db.String(120), nullable=False)
    phone        = db.Column(db.String(20),  nullable=False)
    email        = db.Column(db.String(120), nullable=True)
    program      = db.Column(db.String(80),  nullable=True)
    message      = db.Column(db.Text,        nullable=True)
    status       = db.Column(db.String(30),  default='new')
    created_at   = db.Column(db.DateTime,    default=datetime.utcnow)

    def to_dict(self):
        return {'id': self.id, 'student_name': self.student_name,
                'grade': self.grade, 'parent_name': self.parent_name,
                'phone': self.phone, 'email': self.email or '',
                'program': self.program or '', 'message': self.message,
                'status': self.status, 'created_at': self.created_at.strftime('%d %b %Y, %H:%M')}

class Course(db.Model):
    __tablename__ = 'courses'
    id          = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title       = db.Column(db.String(120), nullable=False)
    stream      = db.Column(db.String(80),  nullable=False)
    description = db.Column(db.Text)
    duration    = db.Column(db.String(50))
    target      = db.Column(db.String(80))
    is_active   = db.Column(db.Boolean, default=True)
    def to_dict(self):
        return {'id': self.id, 'title': self.title, 'stream': self.stream,
                'description': self.description, 'duration': self.duration, 'target': self.target}

class Faculty(db.Model):
    __tablename__ = 'faculty'
    id            = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name          = db.Column(db.String(120), nullable=False)
    qualification = db.Column(db.String(200))
    experience    = db.Column(db.String(80))
    subject       = db.Column(db.String(100))
    is_active     = db.Column(db.Boolean, default=True)
    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'qualification': self.qualification,
                'experience': self.experience, 'subject': self.subject}

class Result(db.Model):
    __tablename__ = 'results'
    id           = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_name = db.Column(db.String(120), nullable=False)
    exam         = db.Column(db.String(80))
    score        = db.Column(db.String(80))
    rank         = db.Column(db.String(40))
    year         = db.Column(db.Integer)
    is_active    = db.Column(db.Boolean, default=True)
    def to_dict(self):
        return {'id': self.id, 'student_name': self.student_name, 'exam': self.exam,
                'score': self.score, 'rank': self.rank, 'year': self.year}

class Admin(db.Model):
    __tablename__ = 'admins'
    id       = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    def check_password(self, pw):
        return check_password_hash(self.password, pw)

# ── Attendance Models ─────────────────────────────────────────────────────────

class Student(db.Model):
    __tablename__ = 'students'
    id           = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id   = db.Column(db.String(20), unique=True, nullable=False)
    name         = db.Column(db.String(120), nullable=False)
    email        = db.Column(db.String(120), unique=True, nullable=False)
    password     = db.Column(db.String(200), nullable=False)
    grade        = db.Column(db.String(50))
    parent_name  = db.Column(db.String(120))
    parent_email = db.Column(db.String(120))
    phone        = db.Column(db.String(20))
    is_active    = db.Column(db.Boolean, default=True)
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)
    attendances  = db.relationship('Attendance', backref='student', lazy=True)
    def to_dict(self):
        return {'id': self.id, 'student_id': self.student_id, 'name': self.name,
                'email': self.email, 'grade': self.grade, 'parent_name': self.parent_name,
                'parent_email': self.parent_email, 'phone': self.phone}

class Teacher(db.Model):
    __tablename__ = 'teachers'
    id         = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name       = db.Column(db.String(120), nullable=False)
    email      = db.Column(db.String(120), unique=True, nullable=False)
    password   = db.Column(db.String(200), nullable=False)
    subject    = db.Column(db.String(100))
    is_active  = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    def check_password(self, pw):
        return check_password_hash(self.password, pw)

class Attendance(db.Model):
    __tablename__ = 'attendance'
    id         = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    date       = db.Column(db.Date, nullable=False)
    status     = db.Column(db.String(10), nullable=False)   # present / absent / late
    marked_by  = db.Column(db.String(50))
    note       = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint('student_id', 'date', name='uq_student_date'),)
    def to_dict(self):
        return {'id': self.id, 'student_id': self.student_id,
                'date': self.date.strftime('%d %b %Y'), 'status': self.status,
                'marked_by': self.marked_by, 'note': self.note}

# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated

def teacher_login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('teacher_logged_in'):
            return redirect(url_for('teacher_login'))
        return f(*args, **kwargs)
    return decorated

def student_login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('student_logged_in'):
            return redirect(url_for('student_login'))
        return f(*args, **kwargs)
    return decorated

from calendar import monthrange as _monthrange

@app.template_filter('get_first_weekday')
def get_first_weekday(month, year):
    # Returns 0=Sun ... 6=Sat offset for calendar grid
    return (_monthrange(year, month)[0] + 1) % 7

@app.template_filter('days_in_month')
def days_in_month_filter(month, year):
    return _monthrange(year, month)[1]

def get_monthly_summary(student_db_id, year, month):
    records = Attendance.query.filter(
        Attendance.student_id == student_db_id,
        extract('year',  Attendance.date) == year,
        extract('month', Attendance.date) == month,
    ).all()
    total   = len(records)
    present = sum(1 for r in records if r.status == 'present')
    absent  = sum(1 for r in records if r.status == 'absent')
    late    = sum(1 for r in records if r.status == 'late')
    pct     = round((present + late) / total * 100, 1) if total else 0
    return {'year': year, 'month': month, 'total': total,
            'present': present, 'absent': absent, 'late': late, 'percentage': pct}

def send_inquiry_email(inquiry):
    try:
        msg = Message(subject=f"New Inquiry from {inquiry.student_name}",
                      recipients=[app.config['MAIL_DEFAULT_SENDER']],
                      body=(f"Student : {inquiry.student_name}\nGrade   : {inquiry.grade}\n"
                            f"Parent  : {inquiry.parent_name}\nPhone   : {inquiry.phone}\n"
                            f"Message : {inquiry.message or '—'}\n"))
        mail.send(msg)
    except Exception as e:
        app.logger.warning(f"Mail not sent: {e}")

# ══════════════════════════════════════════════════════════════════════════════
# PUBLIC API
# ══════════════════════════════════════════════════════════════════════════════

@app.route('/api/courses')
def api_courses():
    return jsonify([c.to_dict() for c in Course.query.filter_by(is_active=True).all()])

@app.route('/api/attendance')
def api_attendance():
    student_id = request.args.get('student_id')
    query = Attendance.query
    if student_id:
        query = query.filter_by(student_id=student_id)
    return jsonify([a.to_dict() for a in query.all()])

@app.route('/api/students')
def api_students():
    return jsonify([s.to_dict() for s in Student.query.filter_by(is_active=True).order_by(Student.name).all()])

@app.route('/api/results')
def api_results():
    return jsonify([r.to_dict() for r in Result.query.filter_by(is_active=True).order_by(Result.year.desc()).all()])

@app.route('/api/inquiries', methods=['POST'])
def submit_inquiry():
    data = request.get_json(silent=True) or request.form
    required = ['student_name', 'grade', 'parent_name', 'phone']
    missing  = [f for f in required if not data.get(f, '').strip()]
    if missing:
        return jsonify({'success': False, 'error': f"Missing: {', '.join(missing)}"}), 400
    inquiry = Inquiry(
        student_name = data['student_name'].strip(),
        grade        = data['grade'].strip(),
        parent_name  = data['parent_name'].strip(),
        phone        = data['phone'].strip(),
        email        = data.get('email', '').strip() or None,
        program      = data.get('program', '').strip() or None,
        message      = data.get('message', '').strip() or None
    )
    db.session.add(inquiry); db.session.commit()
    send_inquiry_email(inquiry)
    return jsonify({'success': True, 'message': "Thank you! We'll contact you shortly.", 'id': inquiry.id}), 201

# ══════════════════════════════════════════════════════════════════════════════
# STUDENT PORTAL
# ══════════════════════════════════════════════════════════════════════════════

@app.route('/student/login', methods=['GET', 'POST'])
def student_login():
    # If already logged in, go to portal
    if session.get('student_logged_in'):
        if request.is_json:
            return jsonify({'success': True, 'redirect': url_for('student_attendance')})
        return redirect(url_for('student_attendance'))

    if request.method == 'POST':
        # Always try JSON first (modal fetch sends JSON)
        if request.is_json:
            data     = request.get_json(force=True, silent=True) or {}
            email    = str(data.get('email', '')).strip()
            password = str(data.get('password', '')).strip()
        else:
            email    = request.form.get('email', '').strip()
            password = request.form.get('password', '').strip()

        app.logger.info(f"Student login attempt: email='{email}'")
        student = Student.query.filter_by(email=email, is_active=True).first()
        app.logger.info(f"Student found: {student is not None}")

        if student and check_password_hash(student.password, password):
            session['student_logged_in'] = True
            session['student_id']        = student.id
            session['student_name']      = student.name
            app.logger.info(f"Student login SUCCESS for '{email}'")
            # Always return JSON (modal fetch expects it)
            return jsonify({'success': True, 'redirect': url_for('student_attendance')})

        app.logger.warning(f"Student login FAILED for '{email}'")
        return jsonify({'success': False, 'error': 'Invalid email or password. Please try again.'}), 401

    # GET request — redirect to homepage (login is handled via modal)
    return redirect(url_for('index'))

@app.route('/student/logout')
def student_logout():
    session.pop('student_logged_in', None)
    session.pop('student_id', None)
    session.pop('student_name', None)
    return redirect(url_for('student_login'))

@app.route('/student/attendance')
@student_login_required
def student_attendance():
    student = Student.query.get(session['student_id'])
    today   = date.today()
    year    = int(request.args.get('year',  today.year))
    month   = int(request.args.get('month', today.month))
    records = Attendance.query.filter(
        Attendance.student_id == student.id,
        extract('year',  Attendance.date) == year,
        extract('month', Attendance.date) == month,
    ).order_by(Attendance.date).all()
    summary = get_monthly_summary(student.id, year, month)
    monthly_summaries = []
    for i in range(5, -1, -1):
        m = today.month - i; y = today.year
        while m <= 0: m += 12; y -= 1
        monthly_summaries.append(get_monthly_summary(student.id, y, m))
    records_lookup = {r.date.strftime('%Y-%m-%d'): r.status for r in records}
    today_day      = today.day if (year == today.year and month == today.month) else -1
    return render_template('student/attendence.html', student=student, records=records,
                           summary=summary, monthly_summaries=monthly_summaries,
                           selected_year=year, selected_month=month,
                           records_lookup=records_lookup, today_day=today_day)

@app.route('/student/profile')
@student_login_required
def student_profile():
    student = Student.query.get(session['student_id'])
    return render_template('student/profile.html', student=student)

@app.route('/student/profile/edit', methods=['GET', 'POST'])
@student_login_required
def student_profile_edit():
    student = Student.query.get(session['student_id'])
    if request.method == 'POST':
        name         = request.form.get('name', '').strip()
        phone        = request.form.get('phone', '').strip()
        parent_name  = request.form.get('parent_name', '').strip()
        parent_email = request.form.get('parent_email', '').strip()

        if not name:
            flash('Name cannot be empty.', 'danger')
            return render_template('student/profile_edit.html', student=student)

        student.name         = name
        student.phone        = phone
        student.parent_name  = parent_name
        student.parent_email = parent_email

        # Password change — only if any password field is filled
        current_pw = request.form.get('current_password', '').strip()
        new_pw     = request.form.get('new_password', '').strip()
        confirm_pw = request.form.get('confirm_password', '').strip()

        if current_pw or new_pw or confirm_pw:
            if not check_password_hash(student.password, current_pw):
                flash('Current password is incorrect.', 'danger')
                return render_template('student/profile_edit.html', student=student)
            if new_pw != confirm_pw:
                flash('New passwords do not match.', 'danger')
                return render_template('student/profile_edit.html', student=student)
            if len(new_pw) < 6:
                flash('New password must be at least 6 characters.', 'danger')
                return render_template('student/profile_edit.html', student=student)
            student.password = generate_password_hash(new_pw)

        db.session.commit()
        session['student_name'] = student.name
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('student_profile'))

    return render_template('student/profile_edit.html', student=student)

# ══════════════════════════════════════════════════════════════════════════════
# TEACHER PORTAL
# ══════════════════════════════════════════════════════════════════════════════

@app.route('/teacher/login', methods=['GET', 'POST'])
def teacher_login():
    if request.method == 'POST':
        email    = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        teacher  = Teacher.query.filter_by(email=email, is_active=True).first()
        if teacher and teacher.check_password(password):
            session['teacher_logged_in'] = True
            session['teacher_id']        = teacher.id
            session['teacher_name']      = teacher.name
            return redirect(url_for('teacher_mark_attendance'))
        flash('Invalid email or password.', 'danger')
    return render_template('teacher/login.html')

@app.route('/teacher/logout')
def teacher_logout():
    session.pop('teacher_logged_in', None)
    session.pop('teacher_id', None)
    session.pop('teacher_name', None)
    return redirect(url_for('teacher_login'))

@app.route('/teacher/attendance', methods=['GET', 'POST'])
@teacher_login_required
def teacher_mark_attendance():
    today    = date.today()
    sel_date = request.args.get('date', today.strftime('%Y-%m-%d'))
    students = Student.query.filter_by(is_active=True).order_by(Student.name).all()
    existing = {a.student_id: a for a in Attendance.query.filter_by(date=sel_date).all()}
    if request.method == 'POST':
        att_date = request.form.get('att_date', sel_date)
        for student in students:
            status = request.form.get(f'status_{student.id}', 'absent')
            note   = request.form.get(f'note_{student.id}', '')
            record = Attendance.query.filter_by(student_id=student.id, date=att_date).first()
            if record:
                record.status = status; record.note = note; record.marked_by = session['teacher_name']
            else:
                db.session.add(Attendance(student_id=student.id, date=att_date,
                                          status=status, note=note, marked_by=session['teacher_name']))
        db.session.commit()
        flash(f'Attendance saved for {att_date}!', 'success')
        return redirect(url_for('teacher_mark_attendance', date=att_date))
    return render_template('teacher/mark_attendance.html', students=students,
                           sel_date=sel_date, existing=existing)

# ══════════════════════════════════════════════════════════════════════════════
# ADMIN
# ══════════════════════════════════════════════════════════════════════════════

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if session.get('admin_logged_in'):
        if request.is_json:
            return jsonify({'success': True, 'redirect': url_for('admin_dashboard')})
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        if request.is_json:
            data     = request.get_json(force=True, silent=True) or {}
            username = str(data.get('username', '')).strip()
            password = str(data.get('password', '')).strip()
        else:
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()

        app.logger.info(f"Admin login attempt: username='{username}'")
        admin = Admin.query.filter_by(username=username).first()
        app.logger.info(f"Admin found: {admin is not None}")

        if admin and admin.check_password(password):
            session['admin_logged_in'] = True
            session['admin_username']  = username
            app.logger.info(f"Admin login SUCCESS for '{username}'")
            return jsonify({'success': True, 'redirect': url_for('admin_dashboard')})

        app.logger.warning(f"Admin login FAILED for '{username}'")
        return jsonify({'success': False, 'error': 'Invalid credentials. Please try again.'}), 401

    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    session.clear(); return redirect(url_for('admin_login'))

@app.route('/admin')
@login_required
def admin_dashboard():
    stats = {
        'total_inquiries': Inquiry.query.count(),
        'new_inquiries':   Inquiry.query.filter_by(status='new').count(),
        'total_courses':   Course.query.filter_by(is_active=True).count(),
        'total_faculty':   Faculty.query.filter_by(is_active=True).count(),
        'total_results':   Result.query.filter_by(is_active=True).count(),
        'total_students':  Student.query.filter_by(is_active=True).count(),
        'total_teachers':  Teacher.query.filter_by(is_active=True).count(),
    }
    recent = Inquiry.query.order_by(Inquiry.created_at.desc()).limit(5).all()
    return render_template('admin/dashboard.html', stats=stats, recent=recent)

@app.route('/admin/inquiries')
@login_required
def admin_inquiries():
    status_filter = request.args.get('status', '')
    q = Inquiry.query.order_by(Inquiry.created_at.desc())
    if status_filter: q = q.filter_by(status=status_filter)
    return render_template('admin/inquiries.html', inquiries=q.all(), status_filter=status_filter)

@app.route('/admin/inquiries/<int:inquiry_id>/status', methods=['POST'])
@login_required
def update_inquiry_status(inquiry_id):
    inquiry = Inquiry.query.get_or_404(inquiry_id)
    new_status = request.form.get('status')
    if new_status in ('new', 'contacted', 'enrolled'):
        inquiry.status = new_status; db.session.commit()
        flash(f'Status updated to "{new_status}"', 'success')
    return redirect(url_for('admin_inquiries'))

@app.route('/admin/inquiries/<int:inquiry_id>/delete', methods=['POST'])
@login_required
def delete_inquiry(inquiry_id):
    inquiry = Inquiry.query.get_or_404(inquiry_id)
    db.session.delete(inquiry); db.session.commit()
    flash('Inquiry deleted.', 'info'); return redirect(url_for('admin_inquiries'))

# ── Admin: Students ───────────────────────────────────────────────────────────

@app.route('/admin/students')
@login_required
def admin_students():
    return render_template('admin/students.html', students=Student.query.order_by(Student.name).all())

@app.route('/admin/students/add', methods=['GET', 'POST'])
@login_required
def add_student():
    if request.method == 'POST':
        last       = db.session.execute(db.select(db.func.max(Student.id))).scalar() or 0
        student_id = f"EDU{date.today().year}{last + 1:04d}"
        db.session.add(Student(
            student_id=student_id, name=request.form['name'],
            email=request.form['email'],
            password=generate_password_hash(request.form['password']),
            grade=request.form.get('grade', ''),
            parent_name=request.form.get('parent_name', ''),
            parent_email=request.form.get('parent_email', ''),
            phone=request.form.get('phone', ''),
        ))
        db.session.commit()
        flash(f'Student added! ID: {student_id}', 'success')
        return redirect(url_for('admin_students'))
    return render_template('admin/student_form.html', student=None, action='Add')

@app.route('/admin/students/<int:student_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_student(student_id):
    student = Student.query.get_or_404(student_id)
    if request.method == 'POST':
        student.name         = request.form['name']
        student.email        = request.form['email']
        student.grade        = request.form.get('grade', '')
        student.parent_name  = request.form.get('parent_name', '')
        student.parent_email = request.form.get('parent_email', '')
        student.phone        = request.form.get('phone', '')
        student.is_active    = 'is_active' in request.form
        if request.form.get('password'):
            student.password = generate_password_hash(request.form['password'])
        db.session.commit(); flash('Student updated!', 'success')
        return redirect(url_for('admin_students'))
    return render_template('admin/student_form.html', student=student, action='Edit')

@app.route('/admin/students/<int:student_id>/delete', methods=['POST'])
@login_required
def delete_student(student_id):
    student = Student.query.get_or_404(student_id)
    db.session.delete(student); db.session.commit()
    flash('Student deleted.', 'info'); return redirect(url_for('admin_students'))

@app.route('/admin/students/<int:student_id>/attendance')
@login_required
def admin_student_attendance(student_id):
    student = Student.query.get_or_404(student_id)
    today   = date.today()
    year    = int(request.args.get('year',  today.year))
    month   = int(request.args.get('month', today.month))
    records = Attendance.query.filter(
        Attendance.student_id == student.id,
        extract('year',  Attendance.date) == year,
        extract('month', Attendance.date) == month,
    ).order_by(Attendance.date).all()
    summary           = get_monthly_summary(student.id, year, month)
    records_by_date   = {r.date.strftime('%Y-%m-%d'): r for r in records}
    days_in_month     = monthrange(year, month)[1]
    first_weekday     = (monthrange(year, month)[0] + 1) % 7
    today_day         = today.day if (year == today.year and month == today.month) else -1
    monthly_summaries = []
    for i in range(5, -1, -1):
        m = month - i; y = year
        while m <= 0: m += 12; y -= 1
        monthly_summaries.append(get_monthly_summary(student.id, y, m))
    return render_template('admin/student_attendance.html',
                           student=student, records=records,
                           summary=summary, monthly_summaries=monthly_summaries,
                           selected_year=year, selected_month=month,
                           records_by_date=records_by_date,
                           days_in_month=days_in_month,
                           first_weekday=first_weekday,
                           today_day=today_day)

# ── Admin: Teachers ───────────────────────────────────────────────────────────

@app.route('/admin/teachers')
@login_required
def admin_teachers():
    return render_template('admin/teachers.html', teachers=Teacher.query.order_by(Teacher.name).all())

@app.route('/admin/teachers/add', methods=['GET', 'POST'])
@login_required
def add_teacher():
    if request.method == 'POST':
        db.session.add(Teacher(
            name=request.form['name'], email=request.form['email'],
            password=generate_password_hash(request.form['password']),
            subject=request.form.get('subject', ''),
        ))
        db.session.commit(); flash('Teacher added!', 'success')
        return redirect(url_for('admin_teachers'))
    return render_template('admin/teacher_form.html', teacher=None, action='Add')

@app.route('/admin/teachers/<int:teacher_id>/delete', methods=['POST'])
@login_required
def delete_teacher(teacher_id):
    teacher = Teacher.query.get_or_404(teacher_id)
    db.session.delete(teacher); db.session.commit()
    flash('Teacher deleted.', 'info'); return redirect(url_for('admin_teachers'))

# ── Admin: Mark Attendance ────────────────────────────────────────────────────

@app.route('/admin/attendance', methods=['GET', 'POST'])
@login_required
def admin_mark_attendance():
    today    = date.today()
    sel_date = request.args.get('date', today.strftime('%Y-%m-%d'))
    students = Student.query.filter_by(is_active=True).order_by(Student.name).all()
    existing = {a.student_id: a for a in Attendance.query.filter_by(date=sel_date).all()}
    if request.method == 'POST':
        att_date = request.form.get('att_date', sel_date)
        for student in students:
            status = request.form.get(f'status_{student.id}', 'absent')
            note   = request.form.get(f'note_{student.id}', '')
            record = Attendance.query.filter_by(student_id=student.id, date=att_date).first()
            if record:
                record.status = status; record.note = note; record.marked_by = 'admin'
            else:
                db.session.add(Attendance(student_id=student.id, date=att_date,
                                          status=status, note=note, marked_by='admin'))
        db.session.commit()
        flash(f'Attendance saved for {att_date}!', 'success')
        return redirect(url_for('admin_mark_attendance', date=att_date))
    return render_template('admin/mark_attendance.html', students=students,
                           sel_date=sel_date, existing=existing)

# ── Admin: Courses ────────────────────────────────────────────────────────────

@app.route('/admin/courses')
@login_required
def admin_courses():
    return render_template('admin/courses.html', courses=Course.query.all())

@app.route('/admin/courses/add', methods=['GET', 'POST'])
@login_required
def add_course():
    if request.method == 'POST':
        db.session.add(Course(title=request.form['title'], stream=request.form['stream'],
            description=request.form.get('description', ''), duration=request.form.get('duration', ''),
            target=request.form.get('target', '')))
        db.session.commit(); flash('Course added!', 'success')
        return redirect(url_for('admin_courses'))
    return render_template('admin/course_form.html', course=None, action='Add')

@app.route('/admin/courses/<int:course_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_course(course_id):
    course = Course.query.get_or_404(course_id)
    if request.method == 'POST':
        course.title       = request.form['title']
        course.stream      = request.form['stream']
        course.description = request.form.get('description', '')
        course.duration    = request.form.get('duration', '')
        course.target      = request.form.get('target', '')
        course.is_active   = 'is_active' in request.form
        db.session.commit(); flash('Course updated!', 'success')
        return redirect(url_for('admin_courses'))
    return render_template('admin/course_form.html', course=course, action='Edit')

@app.route('/admin/courses/<int:course_id>/delete', methods=['POST'])
@login_required
def delete_course(course_id):
    course = Course.query.get_or_404(course_id)
    db.session.delete(course); db.session.commit()
    flash('Course deleted.', 'info'); return redirect(url_for('admin_courses'))

@app.route('/admin/faculty')
@login_required
def admin_faculty():
    return render_template('admin/faculty.html', faculty=Faculty.query.all())

@app.route('/admin/faculty/add', methods=['GET', 'POST'])
@login_required
def add_faculty():
    if request.method == 'POST':
        db.session.add(Faculty(name=request.form['name'],
            qualification=request.form.get('qualification', ''),
            experience=request.form.get('experience', ''),
            subject=request.form.get('subject', '')))
        db.session.commit(); flash('Faculty added!', 'success')
        return redirect(url_for('admin_faculty'))
    return render_template('admin/faculty_form.html', member=None, action='Add')

@app.route('/admin/faculty/<int:faculty_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_faculty(faculty_id):
    member = Faculty.query.get_or_404(faculty_id)
    if request.method == 'POST':
        member.name          = request.form['name']
        member.qualification = request.form.get('qualification', '')
        member.experience    = request.form.get('experience', '')
        member.subject       = request.form.get('subject', '')
        member.is_active     = 'is_active' in request.form
        db.session.commit(); flash('Faculty updated!', 'success')
        return redirect(url_for('admin_faculty'))
    return render_template('admin/faculty_form.html', member=member, action='Edit')

@app.route('/admin/faculty/<int:faculty_id>/delete', methods=['POST'])
@login_required
def delete_faculty(faculty_id):
    member = Faculty.query.get_or_404(faculty_id)
    db.session.delete(member); db.session.commit()
    flash('Faculty deleted.', 'info'); return redirect(url_for('admin_faculty'))

@app.route('/admin/results')
@login_required
def admin_results():
    return render_template('admin/results.html', results=Result.query.order_by(Result.year.desc()).all())

@app.route('/admin/results/add', methods=['GET', 'POST'])
@login_required
def add_result():
    if request.method == 'POST':
        db.session.add(Result(student_name=request.form['student_name'],
            exam=request.form.get('exam', ''), score=request.form.get('score', ''),
            rank=request.form.get('rank', ''),
            year=int(request.form.get('year', datetime.utcnow().year))))
        db.session.commit(); flash('Result added!', 'success')
        return redirect(url_for('admin_results'))
    return render_template('admin/result_form.html', result=None, action='Add')

@app.route('/admin/results/<int:result_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_result(result_id):
    result = Result.query.get_or_404(result_id)
    if request.method == 'POST':
        result.student_name = request.form['student_name']
        result.exam         = request.form.get('exam', '')
        result.score        = request.form.get('score', '')
        result.rank         = request.form.get('rank', '')
        result.year         = int(request.form.get('year', result.year))
        result.is_active    = 'is_active' in request.form
        db.session.commit(); flash('Result updated!', 'success')
        return redirect(url_for('admin_results'))
    return render_template('admin/result_form.html', result=result, action='Edit')

@app.route('/admin/results/<int:result_id>/delete', methods=['POST'])
@login_required
def delete_result(result_id):
    result = Result.query.get_or_404(result_id)
    db.session.delete(result); db.session.commit()
    flash('Result deleted.', 'info'); return redirect(url_for('admin_results'))

# ══════════════════════════════════════════════════════════════════════════════
# SEED & INIT
# ══════════════════════════════════════════════════════════════════════════════

def seed_db():
    if Course.query.count() == 0:
        db.session.add_all([
            Course(title='Advanced Mathematics', stream='Science Stream',
                   description='Mastering calculus, algebra, and geometry.', duration='12 Months', target='Class 11-12'),
            Course(title='Integrated Science', stream='Science Stream',
                   description='Physics, Chemistry, and Biology.', duration='12 Months', target='Class 9-10'),
            Course(title='JEE / NEET Prep', stream='Entrance Exam',
                   description="Crack India's toughest exams.", duration='2 Years', target='Aspirants'),
        ])
    if Faculty.query.count() == 0:
        db.session.add_all([
            Faculty(name='Dr. Rajesh Sharma',  qualification='Ph.D. in Physics',  experience='15+ Years', subject='Physics'),
            Faculty(name='Prof. Ananya Gupta', qualification='M.Sc. Mathematics', experience='10+ Years', subject='Mathematics'),
            Faculty(name='Mr. Vikram Verma',   qualification='Organic Chemistry', experience='12+ Years', subject='Chemistry'),
            Faculty(name='Ms. Kavita Iyer',    qualification='Senior Biology',    experience='8+ Years',  subject='Biology'),
        ])
    if Result.query.count() == 0:
        db.session.add_all([
            Result(student_name='Priya Kapoor', exam='JEE Advanced 2023', score='99.8 Percentile', rank='AIR 15',     year=2023),
            Result(student_name='Arjun Mehta',  exam='NEET 2023',         score='710 / 720',        rank='AIR 42',    year=2023),
            Result(student_name='Sanya Gill',   exam='Maths Olympiad',    score='National Winner',  rank='Gold Medal', year=2023),
        ])
    if Admin.query.count() == 0:
        db.session.add(Admin(username='admin', password=generate_password_hash('admin123')))
    if Teacher.query.count() == 0:
        db.session.add(Teacher(name='Demo Teacher', email='teacher@eduprime.com',
                               password=generate_password_hash('teacher123'), subject='Mathematics'))
    if Student.query.filter_by(email='student@eduprime.com').first() is None:
        db.session.add(Student(student_id='EDU20240001', name='Demo Student',
                               email='student@eduprime.com',
                               password=generate_password_hash('student123'),
                               grade='Class 11', parent_name='Demo Parent',
                               parent_email='parent@eduprime.com', phone='9999999999'))
    db.session.commit()



# ── DEBUG: Check database and login ──────────────────────────────────────────
@app.route('/debug-login')
def debug_login():
    try:
        admins = Admin.query.all()
        admin_info = []
        for a in admins:
            admin_info.append(f"ID:{a.id} | username:'{a.username}' | password_hash:{a.password[:30]}...")
        
        # Test the password check directly
        test_admin = Admin.query.filter_by(username='admin').first()
        test_result = test_admin.check_password('admin123') if test_admin else 'No admin found'
        
        students = Student.query.all()
        student_info = []
        for s in students:
            student_info.append(f"ID:{s.id} | email:'{s.email}' | name:'{s.name}'")
        
        admin_rows = '<br>'.join(admin_info) if admin_info else 'EMPTY'
        student_rows = '<br>'.join(student_info) if student_info else 'EMPTY'
        html = (
            '<pre style="font-family:monospace;padding:30px;font-size:14px">'
            '=== ADMIN TABLE ===<br>'
            'Count: ' + str(len(admins)) + '<br>'
            + admin_rows +
            '<br><br>=== PASSWORD CHECK (admin / admin123) ===<br>'
            'Result: ' + str(test_result) +
            '<br><br>=== STUDENT TABLE ===<br>'
            'Count: ' + str(len(students)) + '<br>'
            + student_rows +
            '<br><br>=== SESSION ===<br>'
            + str(dict(session)) +
            '</pre>'
        )
        return html
    except Exception as e:
        return f'<pre style="padding:30px;color:red">ERROR: {str(e)}</pre>'

@app.route('/force-reset')
def force_reset():
    try:
        # Delete and recreate admin
        Admin.query.delete()
        db.session.commit()
        new_admin = Admin(username='admin', password=generate_password_hash('admin123'))
        db.session.add(new_admin)
        
        # Fix student too
        existing = Student.query.filter_by(email='student@eduprime.com').first()
        if existing:
            existing.password = generate_password_hash('student123')
        else:
            db.session.add(Student(
                student_id='EDU20240001', name='Demo Student',
                email='student@eduprime.com',
                password=generate_password_hash('student123'),
                grade='Class 11', parent_name='Demo Parent',
                parent_email='parent@eduprime.com', phone='9999999999'
            ))
        db.session.commit()
        
        # Verify
        a = Admin.query.filter_by(username='admin').first()
        check = a.check_password('admin123') if a else False
        msg = '✅ DONE | Admin recreated | Password check: ' + str(check)
        return '<pre style="padding:30px">' + msg + '<br><br><a href="/">Go to Homepage</a></pre>'
    except Exception as e:
        db.session.rollback()
        return '<pre style="padding:30px;color:red">ERROR: ' + str(e) + '</pre>'

# ══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

with app.app_context():
    db.create_all()
    seed_db()

if __name__ == '__main__':
    app.run(debug=True)