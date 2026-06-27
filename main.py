from flask import Flask,render_template,request,redirect,session,flash,url_for
from flask_sqlalchemy import SQLAlchemy
import datetime
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = "Maurice_secret_key"
app.config["SQLALCHEMY_DATABASE_URI"]= "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


db = SQLAlchemy(app)

# Database using sqlalchemy
#A database class
# Creating a database Model
class Users(db.Model):
    #class variables
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(100), nullable=False)
    
    def set_password(self,password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self,password):
        return check_password_hash(self.password_hash,password)


#Home route
@app.route("/")
def home():
    if "username" in session:
        return redirect(url_for("dashboard"))
    return render_template("index.html")


#Login route
@app.route("/login",methods=["POST"])
def login():
    #Collecting info from the forms
    username = request.form["username"]
    password = request.form["password"]
    #check if info is in the database

    user = Users.query.filter_by(username=username).first()
    if user and user.check_password(password):
        session["username"]= username
        
        return render_template("dashboard.html",username=username)
    else:
        return render_template("index.html")   

#Register route
@app.route("/register",methods=["POST"])
def register():
    # collecting info from user's database
    username = request.form["username"]
    password = request.form["password"]
    
    # check info is already in database
    user = Users.query.filter_by(username=username).first()
    if user:
        return render_template("index.html", error="User already registered!")
    else:
        new_user = Users(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        session["username"]=username
        return redirect(url_for("home"))
    

#Dashboard route
@app.route("/dashboard")
def dashboard():
    if "username" in session:
        return render_template("dashboard.html",username=session["username"])
    
    else:
        return redirect(url_for("index"))

#logout route
@app.route("/logout")
def logout():
    session.pop("username",None)
    return render_template("index.html")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)