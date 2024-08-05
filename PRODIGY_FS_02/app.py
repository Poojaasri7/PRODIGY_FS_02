from flask import Flask, redirect, render_template, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SECRET_KEY'] = "Helloworld"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Admin_details.db'
app.config['SQLALCHEMY_BINDS'] = {
    'employees': 'sqlite:///Employee_details.db'
}
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'Home'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'poojaasribalakumar@gmail.com'
app.config['MAIL_PASSWORD'] = 'balamanjupoojaajaya'
app.config['MAIL_DEFAULT_SENDER'] = 'poojaasribalakumar@gmail.com'

# Creating the admin database model
class Admin(UserMixin, db.Model):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, default=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    user_type = db.Column(db.String(10), default='admin')

# Creating the employee database model
class Employee(UserMixin, db.Model):
    __bind_key__ = 'employees'
    __tablename__ = 'employees'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    age = db.Column(db.Integer, nullable=False)
    salary = db.Column(db.Integer, nullable=False)
    role = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    user_type = db.Column(db.String(10), default='employee')

@login_manager.user_loader
def load_user(user_id):
    user = Employee.query.get(int(user_id))
    if user:
        user.user_type = 'employee'
        return user
    user = Admin.query.get(int(user_id))
    if user:
        user.user_type = 'admin'
        return user
    return None

@app.route("/")
@app.route("/Home", methods=["POST", "GET"])
def Home():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        admin = Admin.query.filter_by(username=username).first()

        if admin and bcrypt.check_password_hash(admin.password, password):
            admin.user_type = 'admin'
            login_user(admin)
            return redirect(url_for("emp_dashboard"))
        else:
            flash("Login Unsuccessful. Please check your username and password.", "danger")
    return render_template("Home.html")

@app.route("/employee_login", methods=["POST", "GET"])
def employee_login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = Employee.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            user.user_type = 'employee'
            login_user(user)
            return redirect(url_for("employee_dashboard"))
        else:
            flash("Login Unsuccessful. Please check your email and password.", "danger")
    return render_template("employee_login.html")

@app.route("/AddEmp", methods=["POST", "GET"])
@login_required
def AddEmp():
    """if not current_user.is_admin:
        flash('You do not have access to this page.', 'danger')
        return redirect(url_for('Home'))"""
    
    if request.method == "POST":
        employee_id = request.form["Empid"]
        name = request.form["name"]
        age = request.form["age"]
        salary = request.form["salary"]
        role = request.form["Role"]
        email = request.form["email"]
        password = request.form["password"]
        
        user = Employee.query.filter_by(email=email).first()
        if user:
            flash('Email is already registered. Please use a different email.', 'danger')
            return redirect(url_for('AddEmp'))
        
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        new_emp = Employee(id=employee_id, username=name, age=age, salary=salary, role=role, email=email, password=hashed_password)
        db.session.add(new_emp)
        db.session.commit()
        flash('Employee added successfully!', 'success')
        return redirect(url_for('AddEmp'))
    return render_template("AddEmp.html")

@app.route("/emp_dashboard")
@login_required
def emp_dashboard():
    employees = Employee.query.all()
    return render_template('emp_dashboard.html', employees=employees, user=current_user)

@app.route("/employee_dashboard")
@login_required
def employee_dashboard():
    return render_template('employee_dashboard.html', user=current_user)

@app.route("/update_employee/<int:id>", methods=["POST"])
@login_required
def update_employee(id):
    """if not current_user.is_admin:
        flash('You do not have access to this page.', 'danger')
        return redirect(url_for('Home'))"""
        
    employee = Employee.query.get_or_404(id)
    employee.username = request.form["username"]
    employee.age = request.form["age"]
    employee.salary = request.form["salary"]
    employee.role = request.form["role"]
    employee.email = request.form["email"]
    db.session.commit()
    flash('Employee updated successfully!', 'success')
    return redirect(url_for('emp_dashboard'))


@app.route("/update_user_profile", methods=["POST"])
@login_required
def update_user_profile():
    user = current_user
    user.username = request.form["username"]
    user.age = request.form["age"]
    user.salary = request.form["salary"]
    user.role = request.form["role"]
    user.email = request.form["email"]
    db.session.commit()
    flash('Profile updated successfully!', 'success')
    return redirect(url_for('employee_dashboard'))

@app.route("/delete_employee/<int:id>", methods=["POST", "GET"])
@login_required
def delete_employee(id):
    """if not current_user.is_admin:
        flash('You do not have access to this page.', 'danger')
        return redirect(url_for('Home'))"""
        
    employee = Employee.query.get_or_404(id)
    db.session.delete(employee)
    db.session.commit()
    flash('Employee deleted successfully!', 'success')
    return redirect(url_for('emp_dashboard'))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('Home'))

@app.route("/UserSignup", methods=["GET", "POST"])
def UserSignup():
    if request.method == "POST":
        employee_id = request.form["Empid"]
        name = request.form["name"]
        age = request.form["age"]
        salary = request.form["salary"]
        role = request.form["Role"]
        email = request.form["email"]
        password = request.form["password"]
        
        user = Employee.query.filter_by(email=email).first()
        if user:
            flash('Email is already registered. Please use a different email.', 'danger')
            return redirect(url_for('UserSignup'))
        
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        new_emp = Employee(id=employee_id, username=name, age=age, salary=salary, role=role, email=email, password=hashed_password)
        db.session.add(new_emp)
        db.session.commit()
        flash('Signup successful! You can now log in.', 'success')
        return redirect(url_for('Home'))
    return render_template("UserSignup.html")

@app.route("/AboutUs")
def AboutUs():
    return render_template("AboutUs.html")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
