#Import sqlalchemy for database, flask for structure
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask import Flask,session,flash,url_for,request,redirect,render_template
from flask_login import login_user,logout_user,login_required,current_user,LoginManager
from werkzeug.security import generate_password_hash,check_password_hash
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
import os


#Flask boilerplate
app = Flask(__name__)

#Database initialization
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cafee.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "My_Secret_key"
app.config["UPLOAD_DIRECTORY"] = os.path.join("static", "uploads")

app.config["MAX_CONTENT_LENGTH"] = 16*1024*1024 #16MB   
app.config["ALLOWED_EXTENSIONS"] = [".jpg",".png",".jfif",".jpeg",".gif",".webp"]

db = SQLAlchemy(app)


#Creating users db model
class Users(db.Model,UserMixin):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(100),nullable=False)
    email = db.Column(db.String, nullable=False,unique=True)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(100),nullable=False)
    profile_image = db.Column(db.String(200), nullable=True)

  
#Creating Menu db model
class Menu(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String,nullable=False)
    description = db.Column(db.String(1000),nullable=False)
    price = db.Column(db.Float,nullable=False)
    image_filename = db.Column(db.String(200),nullable=False)
 
#Creating a staff db model
class Staff(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    profile_picture = db.Column(db.String(200), nullable=False)
    full_name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.Integer,nullable=False)
    
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def loader(user_id):
    return Users.query.get(int(user_id))   


#Setting up add_staff route
@app.route("/add_staff",methods=["GET","POST"])
def add_staff():
    members = Staff.query.all()
    
    return render_template("add_staff.html",members=members)

#Setting up staff upload photo
@app.route("/upload_profile",methods=["GET","POST"])
@login_required
def upload_profile():
    file = request.files.get("profile_picture")
    try:
        if not file or file.filename == "":
            flash("file not selected", category="danger")
            
            return redirect(url_for("add_staff"))
        
        extension =  os.path.splitext(file.filename)[1].lower()
        if extension not in app.config["ALLOWED_EXTENSIONS"]:
            flash("Invalid image format",category="danger")
            
            return redirect(url_for("add_staff"))
        
        filename = secure_filename(f"user_{current_user.id}_{file.filename}")
        file_path = os.path.join(app.config["UPLOAD_DIRECTORY"],filename)
        file.save(file_path)
        
        current_user.profile_picture = filename        
        db.session.commit()
        
        flash("profile picture uploaded",category="success")
        
        return redirect(url_for("add_staff"))
    
    except RequestEntityTooLarge:
        flash("File exceeds 16MB", category="danger")
        
        return redirect(url_for("add_staff"))
    
    
#Setting up add staff route
@app.route("/add_emplo",methods=["GET","POST"])
@login_required
def add_emplo():
    if request.method=="POST":
        profile_picture = request.files.get("profile_picture")
        full_name = request.form.get("full_name")
        email = request.form.get("email")
        contact = request.form.get("contact")
        role = request.form.get("role")
        
        if not profile_picture or not full_name or not email or not contact or not role:
            flash("All fields must be filled",category="danger")
            
            return redirect(url_for("add_staff"))
        
        if not profile_picture or profile_picture.filename =="":
            flash("file not selected", category="danger")
            
            return redirect(url_for("add_staff"))
        
        extension = os.path.splitext(profile_picture.filename)[1].lower()
        if extension not in app.config["ALLOWED_EXTENSIONS"]:
            flash("Invalid image format",category="danger")
            
            return redirect(url_for("add_staff"))
        
        filename = secure_filename(f"user_{current_user.id}_{profile_picture.filename}")
        file_path = os.path.join(app.config["UPLOAD_DIRECTORY"],filename)
        profile_picture.save(file_path)
        
        
        staff = Staff(profile_picture=filename,full_name=full_name,email=email,contact=contact,role=role)
        db.session.add(staff)
        db.session.commit()
        
        flash("Added successfully",category="success")
        
        return redirect(url_for("add_staff"))
    
    return render_template("add_staff.html")


#Setting up edit staff route
@app.route("/edit_staff/<int:id>",methods=["GET","POST"])
@login_required
def edit_staff(id):
    member = Staff.query.get_or_404(id)
    
    if request.method == "POST":
        member.full_name = request.form.get("full_name")
        member.email = request.form.get("email")
        member.contact = request.form.get("contact")
        member.role = request.form.get("role")
        
        profile_picture = request.files.get("profile_picture")
        
        if profile_picture and profile_picture.filename:
            filename = secure_filename(profile_picture.filename)
            file_path = os.path.join("static/uploads",filename)
            profile_picture.save(file_path)
            member.profile_picture = filename
            
        db.session.commit()
        
        flash("member successfully updated",category="success")
        
        return redirect(url_for("add_staff"))
    
    return render_template("add_staff.html",member=member)

#Setting up delete staff route
@app.route("/delete_staff/<int:id>",methods=["GET","POST"])
@login_required
def delete_staff(id):
    member = Staff.query.get_or_404(id)
    
    db.session.delete(member)
    db.session.commit()
    
    flash("Successfully deleted",category="success")
    
    return redirect(url_for("add_staff"))
        
            


#Setting up home route
@app.route("/")
def home():
    return render_template("login.html")

#Setting up a admin menu route
@app.route("/admin_menu",methods=["GET","POST"])
@login_required
def admin_menu():
    items = Menu.query.all()
    
    return render_template("admin_menu.html",items=items)

#Setting up upload image file route
@app.route("/upload_image", methods=["POST"])
@login_required
def upload_image():
    try:
        file = request.files.get("profile_picture")
        if not file or file.filename == "":
            flash("No file selected", category="danger")
            return redirect(url_for("dashboard"))

        extension = os.path.splitext(file.filename)[1].lower()
        if extension not in app.config["ALLOWED_EXTENSIONS"]:
            flash("Invalid image format", category="danger")
            return redirect(url_for("dashboard"))

        filename = secure_filename(f"user_{current_user.id}_{file.filename}")
        file_path = os.path.join(app.config["UPLOAD_DIRECTORY"], filename)
        file.save(file_path)

        current_user.profile_image = filename
        db.session.commit()

        flash("Profile picture updated!", category="success")
        return redirect(url_for("dashboard"))

    except RequestEntityTooLarge:
        flash("File exceeds 16MB!", category="danger")
        return redirect(url_for("dashboard"))

#Setting up upload photo route
@app.route("/upload_photo",methods=["GET","POST"])  
@login_required
def upload_photo():
    try:
        image_file = request.files.get("image_file")
        extra_image = request.files.get("extra_image")
        if not image_file and extra_image or image_file.filename and extra_image.filename == "":
            flash("File not selected",category="danger")
            
            return redirect(url_for("admin_menu"))
        
        extension = os.path.splitext(image_file.filename,extra_image.filename)[1].lower()
        if extension not in app.config["ALLOWED_EXTENSIONS"]:
            flash("Invalid image format",category="danger")
            
            return redirect(url_for("admin_menu"))
        
        filename = secure_filename(f"user_{current_user.id}_{image_file.filename,extra_image.filename}")
        file_path = os.path.join(app.config["UPLOAD_DIRECTORY"],filename)
        image_file.save(file_path)
        extra_image.save(file_path)
        current_user.image_filename = filename
        db.session.commit()
        
        flash("image added successfully",category="success")
        
        return redirect(url_for("admin_menu"))
    
    except RequestEntityTooLarge:
        flash("File exceeds 16MB",category="danger")
        
        return render_template("admin_menu.html")

#Setting up CRUD-->Create,Read,update and Delete
#Setting up add_items route
@app.route("/add_item",methods=["GET","POST"])
@login_required
def add_item():
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        price = float(request.form.get("price"))
        image_file = request.files.get("image_file")
        
        
        
        if not name or not description or not price or not image_file:
            flash("All fields are required", category="danger")
            
            
            return redirect(url_for("admin_menu"))
        
        
        if price:
            try:
                price = float(price)
            
            except ValueError:
                flash("Invalid format", category="danger")
                
                return redirect(url_for("admin_menu"))
            
        if not image_file or image_file.filename=="":
            flash("file not selected!",category="danger")
            
            return redirect(url_for("admin_menu"))
        
        extension = os.path.splitext(image_file.filename)[1].lower()
        if extension not in app.config["ALLOWED_EXTENSIONS"]:
            flash("Invalid image format",category="danger")
            
            return redirect(url_for("admin_menu"))
        
        filename = secure_filename(f"menu_{name}_{image_file.filename}")
        file_path = os.path.join(app.config["UPLOAD_DIRECTORY"],filename)
        image_file.save(file_path)
        
        menu = Menu(name=name,description=description,price=price,image_filename=filename)
        db.session.add(menu)
        db.session.commit()
        
        flash("All items successfully added.",category="success")
        
        return redirect(url_for("admin_menu"))
    
    return render_template("admin_menu.html")
    
#Setting up Dashboard route
@app.route("/dashboard",methods=["GET","POST"])
@login_required
def dashboard():
    item = Menu.query.all()
    files = os.listdir(app.config["UPLOAD_DIRECTORY"])
    images = []
    
    for file in files:
        extension = os.path.splitext(file)[1].lower()
        if extension in app.config["ALLOWED_EXTENSIONS"]:
            images.append(file)
            
    
    return render_template("dashboard.html",item=item,images=images)

#Setting up edit menu route
@app.route("/edit_menu/<int:id>",methods=["GET","POST"])
@login_required
def edit_menu(id):
    item = Menu.query.get_or_404(id)
    
    if request.method == "POST":
        item.name = request.form.get("name")
        item.description = request.form.get("description")
        item.price = float(request.form.get("price"))

        
        image_file = request.files.get("image_file")
        if image_file and image_file.filename:
            filename = secure_filename(image_file.filename)
            image_path = os.path.join("static/uploads",filename)
            image_file.save(image_path)
            item.image_file = filename
        
        db.session.commit()
        
        flash("Items successfully updated!",category="success")
        
        return redirect(url_for("admin_menu"))
        
    return render_template("admin_menu.html",item=item)

#Setting Up delete items route
@app.route("/delete/<int:id>",methods=["GET","POST"])
@login_required
def delete_item(id):
    item = Menu.query.get_or_404(id)
    
    db.session.delete(item)
    db.session.commit()
    flash("Successfully deleted!",category="success")
    
    return redirect(url_for("admin_menu"))
           
    

#Setting up register route
@app.route("/register",methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        role = request.form.get("role")
        
        existing_email = Users.query.filter_by(email=email).first()
        existing_user = Users.query.filter_by(username=username).first()

        if existing_user and check_password_hash(existing_user.password,password):
            flash("Account already exists", category="danger")
            
        elif existing_email:
            flash("Email already registered. Try logging in or use a different email.", category="danger")
            
        elif len(username)<4:
            flash("username is below 4 characters",category="danger")
            
        elif len(password)<8:
            flash("Password is below 8 characters",category="danger")
            
        elif len(email)<4:
            flash("Email is less than 4 characters ")
            
        else:
            new_user = Users(username=username,
                             email=email,
                             password =generate_password_hash(password),
                             role=role)
            db.session.add(new_user)
            db.session.commit()
            flash(f"New account created under username: {username}", category="success")
            
            return redirect(url_for("login"))
    return render_template("register.html")

#Setting up Login route
@app.route("/login",methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = Users.query.filter_by(username=username).first()
        if user and check_password_hash(user.password,password):
            flash("Login successfully!",category="success")
            login_user(user)
            
            return redirect(url_for("dashboard"))
        
        else:
            flash("Invalid username or password!",category="danger")
            
            return redirect(url_for("login"))
    return render_template("login.html")

#Setting up logout route
@app.route("/logout")
def logout():
    logout_user()    
    session.pop("username",None)
    flash("Logout successful!", category="success")
    
    return render_template("login.html")
        
    
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)