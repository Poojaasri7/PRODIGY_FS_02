from app import db, Admin, bcrypt

def create_admin():
    username = "HR"
    email = "admin12@gmail.com"
    password = "hello@123"
    
    hash_password = bcrypt.generate_password_hash(password).decode('utf-8')
    
    new_user = Admin(username=username, password=hash_password, email=email)
    
    db.session.add(new_user)
    db.session.commit()

if __name__ == "__main__":
    from app import app
    with app.app_context():
        create_admin()
    print("Admin created successfully!")
