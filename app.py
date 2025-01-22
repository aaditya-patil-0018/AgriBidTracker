from flask import Flask
from flask import render_template, redirect, url_for
from flask import request, session
import json
from farmer import Farmer
import os

app = Flask(__name__)
app.secret_key = "thisissecretkey"

UPLOAD_FOLDER = 'uploads'  # Directory where files will be stored
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}  # Allowed file extensions
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    """Check if the file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def read_users():
    filename = "users.json"
    with open(filename, "r") as f:
        data = json.load(f)
    return data

def add_users(utype, ndata):
    filename = "users.json"
    with open(filename, "r") as f:
        data = json.load(f)
    print(data)
    l = len(data[utype])
    data[utype][l] = ndata
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)
    return data

@app.route("/")
def index():
    return render_template('index.html')

@app.route('/signup', methods=["GET", "POST"])
def signup():
    if "user" not in session or "usertype" not in session or "registration" not in session:
        session["user"] = False
        session["usertype"] = ""
        session["registration"] = False
    if session["user"] != True:
        if request.method == "GET":
            return render_template('signup.html')
        elif request.method == "POST":
            name = request.form.get('name')
            email = request.form.get('email')
            password = request.form.get('password')
            usertype = request.form.get('usertype')
            session["user"] = True
            session["usertype"] = usertype
            session["registration"] = False
            session["userid"] = len(read_users[usertype])
            add_users(usertype, {"name": name, "email": email, "password": password})
            return {'name':name, 'email': email, 'password': password, 'usertype': usertype}
    else:
        return redirect(url_for('index'))

@app.route("/login", methods=["GET", "POST"])
def login():
    if "user" not in session or "usertype" not in session or "registration" not in session:
        session["user"] = False
        session["usertype"] = ""
        session["registration"] = False
    if session["user"] != True:
        if request.method == "GET":
            return render_template('login.html')
        elif request.method == "POST":
            email = request.form.get('email')
            password = request.form.get('password')
            usertype = request.form.get('usertype')
            users = read_users()[usertype]
            for user in users:
                if users[user]["email"] == email:
                    if users[user]["password"] == password:
                        session["user"] = True
                        session["usertype"] = usertype
                        session["userid"] = user
                        if usertype == "farmer":
                            return redirect(url_for("farmer_dashboard"))
            else:
                return redirect(url_for("signup"))
    else:
        return redirect(url_for('index'))

############
## FARMER ##
############

@app.route("/farmer/registration", methods=["GET", "POST"])
def farmer_registration():
    if "user" in session:
        if request.method == "GET":
            if session["user"] == True and session["usertype"] == "farmer" and session["registration"] == False:
                return render_template("farmer_registration.html")
            else:
                return "this should return to dashboard/something"
        elif request.method == "POST":
            if session["user"] == True and session["usertype"] == "farmer" and session["registration"] == False:
                # get data from the form
                fname = request.form.get('fname')
                lname = request.form.get('lname')
                email = request.form.get('email')
                contact = request.form.get('contact')
                address = request.form.get('address')
                farm_address = request.form.get('farm_address')

                
                aadhar_card = request.files.get('aadhar_card')
                seven_doc = request.files.get('seven')
                
                user_id = session["userid"]

                # Save Aadhar card with custom name
                if aadhar_card and allowed_file(aadhar_card.filename):
                    aadhar_filename = f"{user_id}_aadhar.pdf"
                    aadhar_path = os.path.join(app.config['UPLOAD_FOLDER'], aadhar_filename)
                    aadhar_card.save(aadhar_path)

                # Save 7/12 document with custom name
                if seven_doc and allowed_file(seven_doc.filename):
                    seven_filename = f"{user_id}_seven.pdf"
                    seven_path = os.path.join(app.config['UPLOAD_FOLDER'], seven_filename)
                    seven_doc.save(seven_path)
                
                # save the data
                # Save data to users.json
                try:
                    with open("users.json", "r") as f:
                        users = json.load(f)
                    
                    # Update farmer data
                    farmers = users["farmer"]
                    farmers[user_id]["registration_data"] = {
                        "name": f"{fname} {lname}",
                        "email": email,
                        "contact": contact,
                        "address": address,
                        "farm_address": farm_address,
                        "aadhar_card": aadhar_filename,
                        "seven_doc": seven_filename,
                    }

                    with open("users.json", "w") as f:
                        json.dump(users, f, indent=4)
                except Exception as e:
                    return f"Error saving data: {e}", 500

                # change session["registration"] = True
                # return to the dashboard/something
                return redirect(url_for("add_crop"))
    else:
        return redirect(url_for('login'))

@app.route('/farmer/addcrop', methods=["GET","POST"])
def add_crop():
    if request.method == "GET":
        return render_template('add_crop.html')
    else:
        # Get data from the form
        crops = request.form.getlist('crops')  # Assuming crops are passed as a list
        bid = request.form.get('bid')
        info = request.form.get('info')
        
        user_id = session["userid"]
        try:
            with open("users.json", "r") as f:
                users = json.load(f)
            
            # Update farmer data
            farmers = users["farmer"]
            farmers[user_id]["crop_data"] = {
                "crops": crops,
                "bid": bid,
                "info": info
            }
            with open("users.json", "w") as f:
                json.dump(users, f, indent=4)
            session["registration"] = True
        except Exception as e:
            return f"Error saving data: {e}", 500
        return redirect(url_for("farmer_dashboard"))

@app.route('/farmer/dashboard')
def farmer_dashboard():
    if session["registration"] == False:
        return redirect(url_for("farmer_registration"))
    return render_template('farmer_dashboard.html')

@app.route('/farmer/dashboard/requests')
def farmer_dashboard_requests():
    return render_template('farmer_dashboard_requests.html')

@app.route('/farmer/dashboard/inventory')
def farmer_dashboard_inventory():
    return render_template('farmer_dashboard_inventory.html')

##############
## MERCHANT ##
##############

@app.route("/merchant/registration")
def merchant_registration():
    pass

###########
## AGENT ##
###########

@app.route("/agent/registration")
def agent_registration():
    pass

@app.route("/agent/dashboard")
def agent_dashboard():
    users=read_users()
    return render_template("agent_dashboard.html", total_farmer=len(users["farmer"]), total_merchant=len(users["merchant"]))

@app.route("/agent/dashboard/farmer")
def agent_dashboard_farmer():
    users=read_users()
    return render_template("agent_farmer.html", farmers=users["farmer"])

@app.route("/agent/dashboard/merchant")
def agent_dashboard_merchant():
    pass

###########
## ADMIN ##
###########

@app.route("/admin")
def admin():
    return ""

@app.route("/admin/login")
def admin_login():
    return render_template("admin_login.html")

if __name__ == "__main__":
    app.run(debug=True)
