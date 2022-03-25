from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, template_folder="templates")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'

db = SQLAlchemy(app)

student_course = db.Table('student_course',
                          db.Column('students_id', db.Integer, db.ForeignKey('students.id')),
                          db.Column('course_id', db.Integer, db.ForeignKey('course.id')))


class Students(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    studentID = db.Column(db.Integer)
    studentName = db.Column(db.Text)
    credits = db.Column(db.Integer)
    classes = db.relationship('Course', secondary=student_course, backref='enrolled')

    def __str__(self):
        return f'{self.id} {self.studentID} {self.studentName} {self.credits}'


class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teacherID = db.Column(db.Integer)
    teacherName = db.Column(db.Text)
    department = db.Column(db.Text)

    def __str__(self):
        return f'{self.id} {self.teacherID} {self.teacherName} {self.department}'


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    courseID = db.Column(db.Integer)
    courseName = db.Column(db.Text)
    teacherID = db.Column(db.Integer)

    def __str__(self):
        return f'{self.id} {self.courseID} {self.courseName} {self.teacherID}'


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('base.html')


@app.route('/student', methods=['GET', 'POST'])
def student():
    request_method = request.method
    students = Students.query.all()
    if request_method == 'POST':
        stu = Students(studentID=request.form['Student ID'],
                       studentName=request.form['Name'],
                       credits=request.form['Credits'])
        db.session.add(stu)
        db.session.commit()
        return redirect('/student')
    return render_template('students.html', request_method=request_method, students=students)


@app.route('/teacher', methods=['GET', 'POST'])
def teacher():
    request_method = request.method
    teachers = Teacher.query.all()
    if request_method == 'POST':
        teach = Teacher(teacherID=request.form['Teacher ID'],
                        teacherName=request.form['Name'],
                        department=request.form['Department'])
        db.session.add(teach)
        db.session.commit()
        return redirect('/teacher')
    return render_template('teacher.html', request_method=request_method, teachers=teachers)


@app.route('/course', methods=['GET', 'POST'])
def course():
    request_method = request.method
    courses = Course.query.all()
    if request_method == 'POST':
        cour = Course(courseID=request.form['Course ID'],
                      courseName=request.form['Name'],
                      teacherID=request.form['Teacher ID'])
        db.session.add(cour)
        db.session.commit()
        return redirect('/course')
    return render_template('course.html', request_method=request_method, courses=courses)


@app.route('/enroll', methods=['GET', 'POST'])
def enroll():
    request_method = request.method
    students = Students.query.all()
    courses = Course.query.all()
    query_student_course = Students.query.join(student_course).join(Course).\
        filter((student_course.c.students_id == Students.id) & (student_course.c.course_id == Course.id)).all()

    if request_method == 'POST':
        stu = Students.query.filter_by(studentID=request.form['Student ID']).first()
        cour = Course.query.filter_by(courseID=request.form['Course ID']).first()
        stu.classes.append(cour)
        db.session.commit()
        return redirect('/enroll')
    return render_template('enroll.html', request_method=request_method, students=students, courses=courses,
                           query_student_course=query_student_course)


@app.route('/update/<int:id>/<string:type>', methods=['GET', 'POST'])
def update(id, type):
    request_method = request.method
    user = ''
    c = type[0]
    if type == 'student':
        user = Students.query.get(id)
    elif type == 'teacher':
        user = Teacher.query.get(id)
    elif type == 'course':
        user = Course.query.get(id)
    if request_method == 'POST':
        if type == 'student':
            user.studentID = request.form['Student ID']
            user.studentName = request.form['Name']
            user.credits = request.form['Credits']
            db.session.commit()
            return redirect('/student')
        elif type == 'teacher':
            user.teacherID = request.form['Teacher ID']
            user.teacherName = request.form['Name']
            user.department = request.form['Department']
            db.session.commit()
            return redirect('/teacher')
        elif type == 'course':
            user.courseID = request.form['Course ID']
            user.courseName = request.form['Name']
            user.teacherID = request.form['Teacher ID']
            db.session.commit()
            return redirect('/course')

    return render_template('update.html', request_method=request_method, user=user, c=c)


@app.route('/drop/<int:id>', methods=['GET', 'POST'])
def drop(id):
    request_method = request.method
    user = Students.query.get(id)
    if request_method == 'POST':
        cour = Course.query.filter_by(courseID=request.form['Course ID']).first()
        user.classes.remove(cour)
        db.session.commit()
        return redirect('/enroll')
    return render_template('drop.html', request_method=request_method, user=user)


@app.route('/delete/<int:id>/<string:type>')
def delete(id, type):
    user = ''
    if type == 'student':
        user = Students.query.get(id)
        db.session.delete(user)
        db.session.commit()
        return redirect('/student')
    elif type == 'teacher':
        user = Teacher.query.get(id)
        db.session.delete(user)
        db.session.commit()
        return redirect('/teacher')
    elif type == 'course':
        user = Course.query.get(id)
        db.session.delete(user)
        db.session.commit()
        return redirect('/course')


if __name__ == '__main__':
    app.run(debug=True)
