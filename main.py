from flask import Flask,render_template,request,session,redirect,url_for,flash
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import login_user,logout_user,login_manager,LoginManager,UserMixin
from flask_login import login_required,current_user
import json
from flask_mysqldb import MySQL
from collections import namedtuple

local_server= True
app = Flask(__name__)
app.secret_key='kusumachandashwini'

# Enter your database connection details below
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '0519212610Eo'
app.config['MYSQL_DB'] = 'new'

# Intialize MySQL
mysql = MySQL(app)

# this is for getting unique user access
login_manager=LoginManager(app)
login_manager.login_view='login'

# Define User class to represent users
class User(UserMixin):
    def __init__(self, id, username, email, password_hash):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash

# User loader function
@login_manager.user_loader
def load_user(user_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM user WHERE id = %s", (user_id,))
    user_data = cur.fetchone()
    cur.close()
    if user_data:
        return User(user_data[0], user_data[1], user_data[2], user_data[3])
    else:
        return None


@app.route('/')
def index(): 
    return render_template('index.html',current_user=current_user)

@app.route('/studentdetails')
def studentdetails():
    cur = mysql.connection.cursor()
    cur.execute("SELECT student.*, department.branch FROM student JOIN department ON student.branch = department.branch")
    query = cur.fetchall()
    cur.close()
    return render_template('studentdetails.html', query=query)

@app.route('/triggers')
def triggers():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM student")
    query = cur.fetchall()
    cur.close()
    return render_template('triggers.html',query=query)

@app.route('/department', methods=['POST', 'GET'])
def department():
    if request.method == "POST":
        dept = request.form.get('dept')
       

        # Check if department already exists
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM department WHERE branch = %s", (dept,))
        query = cur.fetchone()
        cur.close()
        

        if query:
            flash("Department Already Exist", "warning")
            return redirect('/department')

        # Insert new department
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO department (branch) VALUES (%s)", (dept,))
        mysql.connection.commit()
        

        flash("Department Added", "success")

    return render_template('department.html', current_user=current_user)

@app.route('/addattendance',methods=['POST','GET'])
def addattendance():
    # query=db.engine.execute(f"SELECT * FROM `student`") 
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM student")
    query = cur.fetchall()
    cur.close()
    if request.method=="POST":
        rollno=request.form.get('rollno')
        attend=request.form.get('attend')
        
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO attendence (rollno,attendance) VALUES (%s,%s)", (rollno,attend))
        mysql.connection.commit()
        cur.close()
        flash("Attendance added","warning")

        
    return render_template('attendance.html',query=query)

@app.route('/search',methods=['POST','GET'])
def search():
    if request.method=="POST":
        rollno=request.form.get('roll')
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM student where rollno =%s",(rollno,))
        bio= cur.fetchone()
        cur.execute("SELECT * FROM attendence where rollno =%s",(rollno,))
        attend= cur.fetchone()
        cur.close()
        return render_template('search.html',bio=bio,attend=attend)
        
    return render_template('search.html')

@app.route("/delete/<string:id>",methods=['POST','GET'])
@login_required
def delete(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM student where id = %s",(id,))
    post = cur.fetchone()
# Check if the student record exists
    if post:
        # Delete the student record
        cur.execute("DELETE FROM student WHERE id = %s", (id,))
        mysql.connection.commit()
        cur.close()

        flash("Slot Deleted Successfully", "danger")
    else:
        flash("Student record not found", "danger")

    return redirect('/studentdetails')


@app.route("/edit/<string:id>",methods=['POST','GET'])
@login_required
def edit(id):
# Fetch all departments for populating dropdown menu
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM department")
    dept = cur.fetchall()

    if request.method == "POST":
        rollno = request.form.get('rollno')
        sname = request.form.get('sname')
        sem = request.form.get('sem')
        gender = request.form.get('gender')
        branch = request.form.get('branch')
        email = request.form.get('email')
        num = request.form.get('num')
        address = request.form.get('address')

        # Update the student record
        cur.execute("UPDATE Student SET rollno = %s, sname = %s, sem = %s, gender = %s, branch = %s, email = %s, number = %s, address = %s WHERE id = %s", 
                    (rollno, sname, sem, gender, branch, email, num, address, id))
        mysql.connection.commit()
        cur.close()

        flash("Slot is Updated", "success")
        return redirect('/studentdetails')

    # Fetch the student record to be edited
    cur.execute("SELECT * FROM Student WHERE id = %s", (id,))
    posts = cur.fetchone()

    return render_template('edit.html', posts=posts, dept=dept)


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == "POST":
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if the email already exists in the database
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM user WHERE email = %s", (email,))
        user = cur.fetchone()

        if user:
            flash("Email Already Exists", "warning")
            return render_template('signup.html')

        # Hash the password
        encpassword = generate_password_hash(password)

        # Insert new user into the database
        cur.execute("INSERT INTO User (username, email, password) VALUES (%s, %s, %s)", (username, email, encpassword))
        mysql.connection.commit()
        cur.close()

        flash("Signup Successful. Please Login.", "success")
        return render_template('login.html')

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM user WHERE email = %s", (email,))
        user_data = cur.fetchone()
        cur.close()
        if user_data and check_password_hash(user_data[3], password):
            user = User(user_data[0], user_data[1], user_data[2], user_data[3])
            login_user(user)
            flash('Login successful', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password', 'danger')
    return render_template('login.html')



@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logout SuccessFul","warning")
    return redirect(url_for('login'))



@app.route('/addstudent',methods=['POST','GET'])
@login_required
def addstudent():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM department")
    dept = cur.fetchall()
    cur.close()
    

    if request.method == "POST":
        rollno = request.form.get('rollno')
        sname = request.form.get('sname')
        sem = request.form.get('sem')
        gender = request.form.get('gender')
        branch = request.form.get('branch')
        email = request.form.get('email')
        num = request.form.get('num')
        address = request.form.get('address')
        
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO student (rollno, sname, sem, gender, branch, email, number, address) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (rollno, sname, sem, gender, branch, email, num, address))
        mysql.connection.commit()
        cur.close()

        flash("Student Details Added Successfully", "info")

# Fetch departments for populating branch dropdown
    cur = mysql.connection.cursor()
    cur.execute("SELECT branch FROM department")
    dept = cur.fetchall()
    cur.close()


    return render_template('student.html', dept=dept)

@app.route('/about')
def about():
    return render_template('about.html')
 
if __name__ =='__main__':
	app.run(debug=True) 