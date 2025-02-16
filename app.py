from flask import Flask
from flask import render_template, redirect, url_for
from flask import request, session, jsonify
import json
# from farmer import Farmer
import os
from auction import Auction
from datetime import datetime, timedelta
from flask import send_from_directory

app = Flask(__name__)
app.secret_key = "thisissecretkey"

UPLOAD_FOLDER = 'uploads'  # Directory where files will be stored
ALLOWED_EXTENSIONS = {'pdf'} #, 'png', 'jpg', 'jpeg'}  # Allowed file extensions
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    """Check if the file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def add_15_minutes(time_str):
    time_obj = datetime.strptime(time_str, "%H:%M")  # Convert string to datetime object
    new_time = time_obj + timedelta(minutes=15)  # Add 15 minutes
    return new_time.strftime("%H:%M")  # Convert back to string

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
    l = session["userid"]
    data[utype][l] = ndata
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)
    return data

def isApproved(utype):
    filename = "users.json"
    with open(filename, "r") as f:
        data = json.load(f)
    l = str(session["userid"])
    try:
        if data[utype][l]["approved"] == "0":
            return False
        elif data[utype][l]["approved"] == "1":
            return True
    except:
        return True

@app.route("/")
def index():
    if "user" not in session:
        session["user"] = False
    return render_template('newindex.html', userpresent=session["user"])

# @app.route('/signup', methods=["GET", "POST"])
# def signup():
#     if "user" not in session or "usertype" not in session or "registration" not in session:
#         session["user"] = False
#         session["usertype"] = ""
#         session["registration"] = False
#     if session["user"] != True:
#         if request.method == "GET":
#             return render_template('signup.html')
#         elif request.method == "POST":
#             name = request.form.get('name')
#             email = request.form.get('email')
#             password = request.form.get('password')
#             usertype = request.form.get('usertype')
#             session["user"] = True
#             session["usertype"] = usertype
#             session["registration"] = False
#             session["userid"] = len(read_users()[usertype]) + 1
#             add_users(usertype, {"name": name, "email": email, "password": password, "registration": "0"})
#             if usertype == "farmer":
#                 return redirect(url_for("farmer_dashboard"))
#             if usertype == "merchant":
#                 return redirect(url_for("merchant_dashboard"))
#     else:
#         return redirect(url_for('index'))

@app.route("/login", methods=["GET", "POST"])
def login():
    if "user" not in session or "usertype" not in session or "registration" not in session:
        session["user"] = False
        session["usertype"] = ""
        session["registration"] = False
    if session["user"] != True:
        if request.method == "GET":
            return render_template('login.html', message="")
        elif request.method == "POST":
            email = request.form.get('email')
            password = request.form.get('password')
            usertype = request.form.get('usertype')
            users = read_users()[usertype]
            if email in [users[i]['email'] for i in users]:
                for user in users:
                    if users[user]['email'] == email and users[user]['password'] == password:
                        session["user"] = True
                        session["usertype"] = usertype
                        session["userid"] = user
                        if usertype == "farmer":
                            return redirect(url_for("farmer_dashboard"))
                        if usertype == "merchant":
                            return redirect(url_for("merchant_dashboard"))
                        if usertype == "agent":
                            return redirect(url_for("agent_dashboard"))
                else:
                    return render_template('login.html', message="Password is incorrect. Please retry!")
            else:
                # return render_template('login.html', message="Email not present in the database")
                email = request.form.get('email')
                password = request.form.get('password')
                usertype = request.form.get('usertype')
                session["user"] = True
                session["usertype"] = usertype
                session["registration"] = False
                session["userid"] = len(read_users()[usertype]) + 1
                # if usertype.lower() == "farmer" or usertype.lower() == "agent":
                add_users(usertype, {"email": email, "password": password, "registration": "0", "approved": "0"})
                # else:
                    # add_users(usertype, {"email": email, "password": password, "registration": "0"})
                if usertype == "farmer":
                    return redirect(url_for("farmer_dashboard"))
                if usertype == "merchant":
                    return redirect(url_for("merchant_dashboard"))
                if usertype == "agent":
                    return redirect(url_for("agent_dashboard"))
                # print(users[user]["email"])
                # if users[user]["email"] == email:
                #     if users[user]["password"] == password:
                #         session["user"] = True
                #         session["usertype"] = usertype
                #         session["userid"] = user
                #         if usertype == "farmer":
                #             return redirect(url_for("farmer_dashboard"))
                #         if usertype == "merchant":
                #             return redirect(url_for("merchant_dashboard"))
                #     else:
                #         return render_template('login.html', message="Password is incorrect")
                # else:
                #     return render_template('login.html', message="Email not in database")
            # else:
            #     return redirect(url_for("signup"))
    else:
        return redirect(url_for('index'))

@app.route("/logout")
def logout():
    session["user"] = False
    session["usertype"] = ""
    session["registration"] = False
    session["userid"] = ""
    return redirect(url_for("index"))

@app.route("/uploads/<filename>")
@app.route("/uploads/")
def farmer_uploads(filename=""):
    if filename == "":
        return "File is not present in the system!"
    if session["usertype"] == "farmer":
        try:
            if filename.split("_")[0] == session["userid"]:
                upload_folder = "uploads/"
                return send_from_directory(upload_folder, filename, as_attachment=False)
            return "You aren't allowed to access other's file."
        except:
            return "File is not present in the system"
    if session["usertype"] == "merchant":
        upload_folder = "uploads/"
        return send_from_directory(upload_folder, filename, as_attachment=False)

# Custom 404 Error Handler
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404  # Renders a custom 404 page

############
## FARMER ##
############

@app.route("/farmer/registration", methods=["GET", "POST"])
def farmer_registration():
    if "user" in session:
        if session["user"] != False:
            if request.method == "GET":
                if session["user"] == True and session["usertype"] == "farmer" and session["registration"] == False:
                    return render_template("farmer_registration.html")
                else:
                    return "this should return to dashboard/something"
            elif request.method == "POST":
                if session["user"] == True and session["usertype"] == "farmer" and session["registration"] == False:
                    # get data from the form
                    name = request.form.get('name')
                    password = request.form.get('password')
                    email = request.form.get('email')
                    contact = request.form.get('contact')
                    address = request.form.get('address')
                    farm_address = request.form.get('farm_address')
                    
                    usertype = "farmer"
                    add_users(usertype, {"name": name, "email": email, "password": password, "registration": "1", "approved":"0"})
                    
                    aadhar_card = request.files.get('aadhar_card')
                    seven_doc = request.files.get('seven')
                    
                    user_id = session["userid"]

                    # Save Aadhar card with custom name
                    if aadhar_card and allowed_file(aadhar_card.filename):
                        aadhar_filename = f"{user_id}_aadhar.{aadhar_card.filename.split(".")[-1]}"
                        aadhar_path = os.path.join(app.config['UPLOAD_FOLDER'], aadhar_filename)
                        aadhar_card.save(aadhar_path)

                    # Save 7/12 document with custom name
                    if seven_doc and allowed_file(seven_doc.filename):
                        seven_filename = f"{user_id}_seven.{seven_doc.filename.split(".")[-1]}"
                        seven_path = os.path.join(app.config['UPLOAD_FOLDER'], seven_filename)
                        seven_doc.save(seven_path)
                    
                    # save the data
                    # Save data to users.json
                    try:
                        with open("users.json", "r") as f:
                            users = json.load(f)
                        
                        # Update farmer data
                        farmers = users["farmer"]
                        farmers[str(user_id)]["registration_data"] = {
                            "name": name,
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
                    # return redirect(url_for("add_crop"))
                    if usertype == "farmer":
                        return redirect(url_for("farmer_dashboard"))
                    if usertype == "merchant":
                        return redirect(url_for("merchant_dashboard"))
        else:
            return redirect(url_for("login"))
    else:
        return redirect(url_for('login'))

# @app.route('/farmer/addcrop', methods=["GET","POST"])
# def add_crop():
#     if request.method == "GET":
#         if "user" in session:
#             if session["user"] != False:
#                 return render_template('add_crop.html')
#         return redirect(url_for("login"))
#     else:
#         # Get data from the form
#         crops = request.form.getlist('crops')  # Assuming crops are passed as a list
#         bid = request.form.get('bid')
#         info = request.form.get('info')
        
#         user_id = session["userid"]
#         try:
#             with open("users.json", "r") as f:
#                 users = json.load(f)
            
#             # Update farmer data
#             farmers = users["farmer"]
#             farmers[str(user_id)]["crop_data"] = {
#                 "crops": crops,
#                 "bid": bid,
#                 "info": info
#             }
#             farmers[str(user_id)]["registration"] = "1"
#             with open("users.json", "w") as f:
#                 json.dump(users, f, indent=4)
#             session["registration"] = True
#         except Exception as e:
#             return f"Error saving data: {e}", 500
#         return redirect(url_for("farmer_dashboard"))

@app.route('/farmer/profile')
def farmer_profile():
    try:
        if session["registration"] == False and read_users()["farmer"][str(session["userid"])]["registration"] == "0":
            return redirect(url_for("farmer_registration"))
        session["registration"] = True
        return render_template('farmer_profile.html', data=read_users()["farmer"][str(session["userid"])], approval=isApproved("farmer"))
    except:
        return redirect(url_for("index"))

@app.route('/farmer/dashboard')
def farmer_dashboard():
    try:
        if session["registration"] == False and read_users()["farmer"][str(session["userid"])]["registration"] == "0":
            print("True")
            return redirect(url_for("farmer_registration"))
        session["registration"] = True
        data=read_users()["farmer"][str(session["userid"])]
        try:
            ta = len(data["auction"])
        except:
            ta=0
        pr = 0
        st = 0
        ys = 0
        tf = 0
        auction_data = Auction()
        try:
            for auction_id in data["auction"]:
                ad = auction_data.get_auction_data(auction_id=auction_id)
                tf += int(ad["highest_bid"])
                if data["auction"][auction_id]["verification"] == "0":
                    pr += 1
                else:
                    if data["auction"][auction_id]["verification_data"]["started"] == "1":
                        st += 1
                    else:
                        ys += 1
        except:
            pass
        return render_template('farmer_dashboard.html', data=data, approval=isApproved("farmer"), ta=ta, pr=pr, st=st, ys=ys, tf=tf)
    except:
        return redirect(url_for("index"))

@app.route('/farmer/dashboard/requests')
def farmer_dashboard_requests():
    users = read_users()
    farmer = users["farmer"][str(session["userid"])]
    return render_template('farmer_dashboard_requests.html', approval=isApproved("farmer"), farmer=farmer)

@app.route('/farmer/dashboard/requests/<aid>')
def farmer_dashboard_requests_view(aid):
    users = read_users()
    farmer = users["farmer"][str(session["userid"])]["auction"][aid]
    auction = Auction()
    auct_data = auction.get_auction_data()

    with open("users.json", "r") as f:
        users = json.load(f)['farmer']
    highest_bid = 0
    highest_bidder = 0
    auction_data = {}
    for user in users:
        if "auction" in users[user]:
            if aid in users[user]["auction"]:
                auction_data[user] = users[user]["auction"]
                for i in auct_data[aid]["bidding_details"]:
                    try:
                        highest_bid = auct_data[aid]["bidding_details"][i]["bid"]
                        highest_bidder = auct_data[aid]["bidding_details"][i]["merchant_id"].split("d")[-1]
                    except:
                        highest_bid = i[0]
                        highest_bidder = i
    try:
        auction_table = auct_data[aid]["bidding_details"]
    except:
        auction_table = ""
    with open("users.json", "r") as f:
        users = json.load(f)
    try:
        highest_bidder_id = highest_bidder
        highest_bidder = users["merchant"][highest_bidder]["name"]
    except:
        highest_bidder_id = highest_bidder
        highest_bidder = users["merchant"][highest_bidder]["registration_data"]["name"]
    return render_template('farmer_dashboard_requests_view.html', aid=aid, auction_table=auction_table, approval=isApproved("farmer"), highest_bidder=highest_bidder, highest_bid=highest_bid, highest_bidder_id=highest_bidder_id)
    return farmer
    # return render_template('farmer_dashboard_requests.html', approval=isApproved("farmer"), farmer=farmer)


@app.route('/farmer/dashboard/auction', methods=["GET", "POST"])
@app.route('/farmer/dashboard/auction/<msg>')
def farmer_dashboard_inventory(msg=""):
    if request.method == "GET":
        if session["user"] == True and session["usertype"] == "farmer" and session["registration"] != False:
            return render_template('farmer_dashboard_auction.html', approval=isApproved("farmer"), msg=msg)
        else:
            return redirect(url_for("index"))
    elif request.method == "POST":
        data = {
            "crop": request.form.get("selected_crop"),
            "bid": request.form.get("bid"),
            "info": request.form.get("info"),
            "start_time": str(datetime.now()),
            "stop_time": str(datetime.now() + timedelta(minutes=15)),
            "verification": "0"
        }
        auction = Auction()
        auction_id = auction.create_auction()

        with open("users.json", "r") as f:
            users = json.load(f)
        
        user_id = session["userid"]
        # Update farmer data
        farmers = users["farmer"]
        if "auction" not in farmers[str(user_id)]:
            farmers[str(user_id)]["auction"] = {}
        farmers[str(user_id)]["auction"][auction_id] = data

        with open("users.json", "w") as f:
            json.dump(users, f, indent=4)

        return redirect("/farmer/dashboard/auction/Bid Added Successfully")



##############
## MERCHANT ##
##############

@app.route("/merchant/registration", methods=["GET", "POST"])
def merchant_registration():
    if "user" in session:
        if session["user"] != False:
            if request.method == "GET":
                user_id = session["userid"]
                print(user_id)
                return render_template("merchant_registration.html")
            elif request.method == "POST":
                aadhar_card = request.files.get('aadhar_card')
                license = request.files.get('license')
                
                user_id = session["userid"]

                # Save Aadhar card with custom name
                if aadhar_card and allowed_file(aadhar_card.filename):
                    aadhar_filename = f"merchant_{user_id}_aadhar.{aadhar_card.filename.split(".")[-1]}"
                    aadhar_path = os.path.join(app.config['UPLOAD_FOLDER'], aadhar_filename)
                    aadhar_card.save(aadhar_path)

                # Save 7/12 document with custom name
                if license and allowed_file(license.filename):
                    license_filename = f"merchant_{user_id}_license.{license.filename.split(".")[-1]}"
                    license_path = os.path.join(app.config['UPLOAD_FOLDER'], license_filename)
                    license.save(license_path)

                data = {
                    "name": f"{request.form.get('fname')} {request.form.get('lname')}",
                    "email": request.form.get("email"),
                    "contact": request.form.get("contact"),
                    "address": request.form.get("address"),
                    "aadhar": aadhar_filename,
                    "license": license_filename
                }

                with open("users.json", "r") as f:
                    users = json.load(f)
                
                user_id = session["userid"]
                merchant = users["merchant"]
                merchant[str(user_id)]["registration"] = "1"
                merchant[str(user_id)]["registration_data"] = data
                session["registration"] = True

                with open("users.json", "w") as f:
                    json.dump(users, f, indent=4)

                return redirect(url_for('merchant_dashboard'))
        else:
            return redirect(url_for("login"))
    else:
        return redirect(url_for("login"))

@app.route("/merchant/dashboard/listing")
def merchant_listings(msg=""):
    try:
        if session["registration"] == False and read_users()["merchant"][str(session["userid"])]["registration"] == "0":
            return redirect(url_for("merchant_registration"))
        session["registration"] = True
        # auction = Auction()
        # auction_data = auction.get_auction_data()
        # print(auction_data)
        with open("users.json", "r") as f:
            users = json.load(f)['farmer']
        auction_data = {}
        for user in users:
            if "auction" in users[user]:
                auction_data[user] = users[user]["auction"]
                for auction in users[user]["auction"]:
                    if "verification_data" in users[user]["auction"][auction]:
                        try:
                            auction_data[user][auction]["verification_data"]["end_time"] = str(add_15_minutes(auction_data[user][auction]["verification_data"]["start_time"]))
                        except:
                            auction_data[user][auction]["verification_data"]["end_time"] = "0"
        print(auction_data)
        current_time = datetime.now().strftime("%H:%M")
        current_date = datetime.now().strftime("%Y-%m-%d")
        print(current_time, current_date)  # Example Output: "14:05"
        return render_template('merchant_listings.html', data=auction_data, msg=msg, current_time=str(current_time), current_date=current_date, approved=isApproved("merchant"))
    except:
        return redirect(url_for("index"))

@app.route("/merchant/dashboard/listing/<aid>/result")
def merchant_listing_result(aid):
    users = read_users()
    
    auction = Auction()
    auct_data = auction.get_auction_data()

    with open("users.json", "r") as f:
        users = json.load(f)['farmer']

    highest_bid = 0
    highest_bidder = 0
    auction_data = {}
    
    if aid in auct_data:
        auction_data[aid] = auct_data[aid]
        for i in auct_data[aid]["bidding_details"]:
            try:
                highest_bid = auct_data[aid]["bidding_details"][i]["bid"]
                highest_bidder = auct_data[aid]["bidding_details"][i]["merchant_id"].split("d")[-1]
            except:
                highest_bid = i[0]
                highest_bidder = i
    # return auction_data
    try:
        auction_table = auct_data[aid]["bidding_details"]
    except:
        auction_table = ""
    with open("users.json", "r") as f:
        users = json.load(f)
    try:
        highest_bidder_id = highest_bidder
        highest_bidder = users["merchant"][highest_bidder]["name"]
    except:
        try:
            highest_bidder_id = highest_bidder
            highest_bidder = users["merchant"][highest_bidder]["registration_data"]["name"]
        except:
            highest_bidder_id = 0
            highest_bidder = ""
    return render_template('merchant_results.html', aid=aid, auction_table=auction_table, highest_bidder=highest_bidder, highest_bid=highest_bid, highest_bidder_id=highest_bidder_id, approved=isApproved("merchant"))
    

@app.route("/rate_farmer/<fid>", methods=["POST"])
def rate_farmer(fid):
    if request.method == "POST":
        with open("users.json", "r") as f:
            users = json.load(f)
        users["farmer"][fid]["rating"] = {
            session["userid"]:{
                "stars": request.form.get("rating"),
                "feedback": request.form.get("feedback")
            }
        }
        with open("users.json", "w") as f:
            json.dump(users, f, indent=4)
        return "Thanks for rating the farmer"

@app.route("/merchant/dashboard/listing/apply/<aid>", methods=["GET", "POST"])
@app.route("/merchant/dashboard/listing/apply/<aid>/<msg>", methods=["GET", "POST"])
def merchant_listings_apply(aid, msg=""):
    if request.method == "GET":
        try:
            if session["registration"] == False and read_users()["merchant"][str(session["userid"])]["registration"] == "0":
                return redirect(url_for("merchant_registration"))
            session["registration"] = True
            auction = Auction()
            auct_data = auction.get_auction_data()

            with open("users.json", "r") as f:
                users = json.load(f)['farmer']
            auction_data = {}
            for user in users:
                if "auction" in users[user]:
                    if aid in users[user]["auction"]:
                        auction_data[user] = users[user]["auction"]
            try:
                auction_table = auct_data[aid]["bidding_details"]
            except:
                auction_table = ""
            return render_template('merchant_listing_apply.html', data=auction_data, aid=aid, auction_table=auction_table, msg=msg, farmers=users, approved=isApproved("merchant"))
        except:
            return redirect(url_for("index"))
    elif request.method == "POST":
        auction = Auction(auction_id=aid)
        try:
            if str(session["userid"]) not in auction.get_auction_data()["bidder_details"]:
                auction.add_bidder(merchant_id=str(session["userid"]))
        except:
            auction.add_bidder(merchant_id=str(session["userid"]))
        bidup = auction.bid_up(merchant_id=str(session["userid"]), amount=request.form.get("bid_amount"))
        if bidup[0] == True:
            return redirect(url_for("merchant_listings_apply", aid = aid))
        else:
            return redirect(url_for("merchant_listings_apply", aid = aid, msg=bidup[1]))

# /merchant/dashboard/listing/apply/{{i}}/notify
@app.route("/merchant/dashboard/listing/apply/<aid>/notify")
def merchant_listings_apply_notify(aid):
    if "notify_bid" not in session:
        session["notify_bid"] = []
    if aid not in session["notify_bid"]:
        session["notify_bid"].append(aid)
    return merchant_listings(msg="Bid Starred, You will be notified once bid starts")

@app.route("/merchant/dashboard/listings/getnotify")
def merchant_listings_get_notify():
    if "notify_bid" not in session:
        session["notify_bid"] = []
    return jsonify(userid=session.get("notify_bid"))  # Returns session data as JSON

@app.route("/merchant/dashboard")
def merchant_dashboard():
    try:
        if session["registration"] == False and read_users()["merchant"][str(session["userid"])]["registration"] == "0":
            return redirect(url_for("merchant_registration"))
        session["registration"] = True
        
        return render_template('merchant_dashboard.html', approved=isApproved("merchant"))
    except:
        return redirect(url_for("index"))
    
@app.route('/merchant/profile')
def merchant_profile():
    # try:
    if session["registration"] == False and read_users()["merchant"][str(session["userid"])]["registration"] == "0":
        return redirect(url_for("merchant_registration"))
    session["registration"] = True
    return render_template('merchant_profile.html', data=read_users()["merchant"][str(session["userid"])], approved=isApproved("merchant"))

###########
## AGENT ##
###########

@app.route("/agent/registration", methods=["GET", "POST"])
def agent_registration():
    if "user" in session:
        if session["user"] != False:
            if request.method == "GET":
                if session["user"] == True and session["usertype"] == "agent" and session["registration"] == False:
                    return render_template("agent_registration.html")
                else:
                    return redirect(url_for("agent_dashboard"))
            elif request.method == "POST":
                if session["user"] == True and session["usertype"] == "agent" and session["registration"] == False:
                    # get data from the form
                    name = request.form.get('name')
                    password = request.form.get('password')
                    email = request.form.get('email')
                    contact = request.form.get('contact')
                    address = request.form.get('address')
                    
                    usertype = "agent"
                    add_users(usertype, {"name": name, "email": email, "password": password, "registration": "1", "approved": "0"})
                    
                    aadhar_card = request.files.get('aadhar_card')
                    
                    user_id = session["userid"]

                    # Save Aadhar card with custom name
                    if aadhar_card and allowed_file(aadhar_card.filename):
                        aadhar_filename = f"agent_{user_id}_aadhar.{aadhar_card.filename.split(".")[-1]}"
                        aadhar_path = os.path.join(app.config['UPLOAD_FOLDER'], aadhar_filename)
                        aadhar_card.save(aadhar_path)

                    
                    # save the data
                    # Save data to users.json
                    try:
                        with open("users.json", "r") as f:
                            users = json.load(f)
                        
                        # Update farmer data
                        agent = users["agent"]
                        agent[str(user_id)]["registration"] = "1"
                        agent[str(user_id)]["registration_data"] = {
                            "name": name,
                            "email": email,
                            "contact": contact,
                            "address": address,
                            "aadhar_card": aadhar_filename,
                        }

                        with open("users.json", "w") as f:
                            json.dump(users, f, indent=4)
                    except Exception as e:
                        return f"Error saving data: {e}", 500

                    # change session["registration"] = True
                    # return to the dashboard/something
                    # return redirect(url_for("add_crop"))
                    if usertype == "farmer":
                        return redirect(url_for("farmer_dashboard"))
                    if usertype == "merchant":
                        return redirect(url_for("merchant_dashboard"))
                    if usertype == "agent":
                        return redirect(url_for("agent_dashboard"))
        else:
            return redirect(url_for("login"))
    else:
        return redirect(url_for('login'))

@app.route("/agent/dashboard")
def agent_dashboard():
    # try:
    if session["registration"] == False and read_users()["agent"][str(session["userid"])]["registration"] == "0":
        return redirect(url_for("agent_registration"))
    users=read_users()["farmer"]
    tf = len(users)
    ta = 0
    tv = 0
    for user in users:
        try:
            ta += len(users[user]["auction"])
            for i in users[user]["auction"]:
                if users[user]["auction"][i]["verification"] == "0":
                    tv += 1
        except:
            continue
    return render_template("agent_dashboard.html", tf=tf, ta=ta, tv=tv, approved=isApproved("agent"))
    # except:
    #     return redirect(url_for("index"))

@app.route("/agent/farmers/verify")
def agent_dashboard_farmer():
    # try:
    if session["registration"] == False and read_users()["agent"][str(session["userid"])]["registration"] == "0":
        return redirect(url_for("agent_registration"))
    users=read_users()
    current_date = datetime.now().strftime("%Y-%m-%d")
    return render_template("agent_farmer.html", farmers=users["farmer"], current_date=current_date, approved=isApproved("agent"))
    # except:
    #     return redirect(url_for("index"))

@app.route("/agent/farmers/verify/<fid>/<aid>", methods=["GET", "POST"])
def agent_dashboard_farmer_view(fid, aid):
    # try:
    if request.method == "GET":
        if session["registration"] == False and read_users()["agent"][str(session["userid"])]["registration"] == "0":
            return redirect(url_for("agent_registration"))
        users=read_users()
        # return users['farmer'][fid]
        return render_template("agent_farmer_view.html", farmer_data=users["farmer"][fid], fid=fid, aid=aid, approved=isApproved("agent"))
    elif request.method == "POST":
        product_image = request.files.get('product_image')

        # Save Aadhar card with custom name
        if product_image:
            product_filename = f"{aid}_image.{product_image.filename.split(".")[-1]}"
            product_path = os.path.join(app.config['UPLOAD_FOLDER'], product_filename)
            product_image.save(product_path)

        data = {
            "quality": request.form.get("quality"),
            "start": request.form.get("starttime"),
            "end": request.form.get("endtime"),
            "image": product_filename,
            "started": "0",
            "start_time": "0"
        }

        users = read_users()
        users["farmer"][fid]["auction"][aid]["verification"] = "1"
        users["farmer"][fid]["auction"][aid]["verification_data"] = data
        with open("users.json", "w") as f:
            json.dump(users, f, indent=4)
        return redirect("/agent/farmers/verify")
    # except:
    #     return redirect(url_for("index"))

@app.route("/agent/produce/verify")
def agent_produce_verify():
    try:
        if session["registration"] == False and read_users()["agent"][str(session["userid"])]["registration"] == "0":
            return redirect(url_for("agent_registration"))
        return render_template("agent_quality_verify.html", approved=isApproved("agent"))
    except:
        return redirect(url_for("index"))

###########
## ADMIN ##
###########
    
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "GET":
        return render_template("admin_login.html")
    elif request.method == "POST":
        name = request.form.get("name")
        password = request.form.get("password")
        if name == "admin" and password == "admin":
            session["admin"] = True
            return redirect(url_for("admin"))
        else:
            return render_template("admin_login.html")

@app.route("/admin")
def admin():
    if "admin" not in session:
        session["admin"] = False
    if session["admin"] == True:
        users = read_users()
        total_farmer = len(users["farmer"])
        total_merchant = len(users["merchant"])
        total_agents = len(users["agent"])
        return render_template("admin_dashboard.html", tf=total_farmer, tm=total_merchant, ta=total_agents)
    else:
        return redirect(url_for("admin_login"))
    
@app.route("/admin/users")
def admin_users():
    if session["admin"] == True:
        return render_template("admin_users.html")
    else:
        return redirect(url_for("admin_login"))

@app.route("/admin/users/farmers")
def admin_users_farmers():
    if session["admin"] == True:
        users = read_users()["farmer"]
        return render_template("admin_users_farmers.html", users=users)
    else:
        return redirect(url_for("admin_login"))

@app.route("/admin/users/farmers/<fid>")
def admin_users_farmers_approve(fid):
    if session["admin"] == True:
        users = read_users()
        if users["farmer"][fid]["approved"] == "0": 
            users["farmer"][fid]["approved"] = "1"
        else:
            users["farmer"][fid]["approved"] = "0"
        with open("users.json", "w") as f:
            json.dump(users, f, indent=4)
        return redirect(url_for("admin_users_farmers"))
    else:
        return redirect(url_for("admin_login"))

@app.route("/admin/users/merchants")
def admin_users_merchants():
    if session["admin"] == True:
        users = read_users()["merchant"]
        return render_template("admin_users_merchants.html", users=users)
    else:
        return redirect(url_for("admin_login"))

@app.route("/admin/users/merchant/<fid>")
def admin_users_merchant_approve(fid):
    if session["admin"] == True:
        users = read_users()
        if users["merchant"][fid]["approved"] == "0": 
            users["merchant"][fid]["approved"] = "1"
        else:
            users["merchant"][fid]["approved"] = "0"
        with open("users.json", "w") as f:
            json.dump(users, f, indent=4)
        return redirect(url_for("admin_users_merchants"))
    else:
        return redirect(url_for("admin_login"))

@app.route("/admin/users/agents")
def admin_users_agents():
    if session["admin"] == True:
        users = read_users()["agent"]
        return render_template("admin_users_agents.html", users=users)
    else:
        return redirect(url_for("admin_login"))

@app.route("/admin/users/agent/<aid>")
def admin_users_agent_approve(aid):
    if session["admin"] == True:
        users = read_users()
        if users["agent"][aid]["approved"] == "0": 
            users["agent"][aid]["approved"] = "1"
        else:
            users["agent"][aid]["approved"] = "0"
        with open("users.json", "w") as f:
            json.dump(users, f, indent=4)
        return redirect(url_for("admin_users_agents"))
    else:
        return redirect(url_for("admin_login"))

@app.route("/admin/uploads/<filename>")
def admin_upload_file(filename):
    # Ensure your file path points to the directory where uploads are stored
    upload_folder = "uploads/"
    return send_from_directory(upload_folder, filename, as_attachment=False) 

@app.route("/admin/auctions")
def admin_auction():
    if session["admin"] == True:
        users = read_users()
        farmer = users["farmer"]
        current_date = datetime.now().strftime("%Y-%m-%d")
        farmer_data = {}
        for i in farmer:
            if "auction" in farmer[i]:
                for j in farmer[i]["auction"]:
                    if "verification_data" in farmer[i]["auction"][j]:
                        try:
                            farmer[i]["auction"][j]["verification_data"]["stop_time"] = add_15_minutes(farmer[i]["auction"][j]["verification_data"]["start_time"])
                        except:
                            pass
            farmer_data[i] = farmer[i]
        return render_template("admin_auction.html", farmer=farmer_data, current_date=current_date)
    else:
        return redirect(url_for("admin_login"))

@app.route("/admin/auctions/<aid>/start", methods=["POST"])
def admin_auction_start(aid):
    if session["admin"] == True:
        users = read_users()
        start_time = request.form.get("time")
        farmers = users["farmer"]
        for farmer in farmers:
            if "auction" in farmers[farmer]:
                if aid in farmers[farmer]["auction"]:
                    if users["farmer"][farmer]["auction"][aid]["verification_data"]["started"] == "0": 
                        users["farmer"][farmer]["auction"][aid]["verification_data"]["started"] = "1"
                        users["farmer"][farmer]["auction"][aid]["verification_data"]["start_time"] = start_time
                    else:
                        users["farmer"][farmer]["auction"][aid]["verification_data"]["started"] = "0"
                        users["farmer"][farmer]["auction"][aid]["verification_data"]["start_time"] = ""
        with open("users.json", "w") as f:
            json.dump(users, f, indent=4)
        return redirect(url_for("admin_auction"))
        # return render_template("admin_auction.html", farmer=farmer)
    else:
        return redirect(url_for("admin_login"))

@app.route("/admin/logout")
def admin_logout():
    session["admin"] = False
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
