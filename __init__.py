from flask import Flask, session, redirect, url_for, request, render_template, flash
from flask_restful import Api
import sys
from passlib.hash import sha256_crypt
from werkzeug.utils import secure_filename
import os
from functools import wraps
import mysql
import mysql.connector

from views import table_test, TableAnimalUpdate, TableAnimalAdd, \
    TableInventoryPasture, TableInventoryFormulary, TableHealthList, TableHerd, TableInventoryPastureHistory,\
    TableHerdUniqueName, TableExperiment, TableHealthAdd, TableReproduction,Expt,TableInspection

app = Flask(__name__)

app.config['SECRET_KEY'] = "The Secret String"
app.config['UPLOAD_FOLDER']='/static/pdf_files/'
ALLOWED_EXTENSIONS=set(['txt','pdf','png','jpg'])

cnx = mysql.connector.connect(host="livebarn.mysql.pythonanywhere-services.com", user="livebarn", passwd="barnyard123$", db="livebarn$barnyard")
# bcrypt = Bcrypt(app)


# API configurations
#These will send and recieve data according to the functions they are assigned to in the Views page.
api = Api(app)

# Testing for the new MYSQL db connection
api.add_resource(table_test, '/api/test/', endpoint="18")
api.add_resource(table_test, '/api/test/')

# APIs for the new UI Design
api.add_resource(TableAnimalUpdate, '/api/animal/update/<Animal_ID>')
api.add_resource(TableAnimalUpdate, '/api/animal/update/', endpoint="20")

api.add_resource(TableAnimalAdd, '/api/animal/add/<Animal_ID>')
api.add_resource(TableAnimalAdd, '/api/animal/add/', endpoint="19")

api.add_resource(TableHerd, '/api/herd/create/')
api.add_resource(TableHerd, '/api/herd/create/', endpoint="21")

api.add_resource(TableInventoryPasture, '/api/inventory/pasture/')
api.add_resource(TableInventoryPasture, '/api/inventory/pasture/', endpoint="22")

api.add_resource(TableInventoryPastureHistory, '/api/inventory/pasturehistory/<pasture_ID>/<event_date>')
api.add_resource(TableInventoryPastureHistory, '/api/inventory/pasturehistory/', endpoint="23")

api.add_resource(TableHerdUniqueName, '/api/herd/name/<name>')
api.add_resource(TableHerdUniqueName, '/api/herd/name/', endpoint="24")

api.add_resource(TableInventoryFormulary, '/api/inventory/formulary/<Medicine_ID>')
api.add_resource(TableInventoryFormulary, '/api/inventory/formulary/', endpoint="25")

api.add_resource(TableExperiment, '/api/experiment/herd/<Animal_ID>')
api.add_resource(TableExperiment, '/api/experiment/herd/', endpoint="26")

api.add_resource(TableHealthAdd, '/api/health/add/<animalname>')
api.add_resource(TableHealthAdd, '/api/health/add/', endpoint="27")

api.add_resource(TableHealthList, '/api/health/record/<Record_ID>')
api.add_resource(TableHealthList, '/api/health/record/', endpoint="28")

api.add_resource(TableReproduction, '/api/reproduction/record/')
api.add_resource(TableReproduction, '/api/reproduction/record/', endpoint="29")

api.add_resource(Expt, '/api/experiment/list/')
api.add_resource(Expt, '/api/experiment/list/', endpoint="30")

api.add_resource(TableInspection, '/api/inspection/report/')
api.add_resource(TableInspection, '/api/inspection/report/', endpoint="31")

#App Routes
#These will reroute all the data through the webpage to its destinations

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("You need to login first")
            return redirect(url_for('login'))

    return wrap

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == 'GET':
        return render_template("signup.html")
    else:
        print >> sys.stderr, 'Registering...'
        name = request.form['name']
        email = request.form['email']
        password = sha256_crypt.encrypt((str(request.form['password'])))
        cur = cnx.cursor(dictionary=True)
        cur.execute("INSERT INTO login (first_name, email_id, password) VALUES (%s,%s,%s)",(name,email,password,))
        print("here after execute")
        cnx.commit()
        session['name'] = request.form['name']
        session['email'] = request.form['email']
        session['logged_in'] = True
        print >> sys.stderr, 'Returning...'
        return redirect(url_for('home'))

@app.route('/login',methods=["GET","POST"])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password'].encode('utf-8')
        cur = cnx.cursor(dictionary=True)
        cur.execute("SELECT * FROM login WHERE email_id=%s",(email,))
        user = cur.fetchone()
        if len(user) > 0:
            if sha256_crypt.verify(password, user["password"]):
                session['name'] = user["first_name"]
                session['email'] = user["email_id"]
                session['logged_in'] = True
                return render_template("home.html")
            else:
                return "Error password and email not match"
        else:
            return "Error user not found"
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    session['logged_in'] = False
    session.clear()
    return redirect(url_for('login'))

@app.route('/tempsearchpage')
@login_required
def home():
    return render_template("tempsearchpage.html")


@app.route('/animal/add', methods=['GET','POST','PATCH'])
@login_required
def animaladd():
        return render_template("animaladd.html")


@app.route('/animal/list')
@login_required
def animallist():
    return render_template("animallist.html")


@app.route('/animal/update', methods=['GET','DELETE'])
@login_required
def animalupdate():
    return render_template("animalupdate.html")


@app.route('/experiment/add', methods=['GET', 'POST'])
@login_required
def experimentadd():
    return render_template("experimentadd.html")


@app.route('/experiment/list', methods=['GET','PATCH','DELETE'])
@login_required
def experiment_list():
    return render_template("experiment_list.html")


@app.route('/experiment/edit', methods=['GET', 'POST','PATCH','DELETE'])
@login_required
def experiment_edit():
    return render_template("experiment_edit.html")


@app.route('/experiment/update', methods=['GET', 'POST', 'PATCH'])
@login_required
def experimentupdate():
    return render_template("experiment_update.html")


@app.route('/report/create')
@login_required
def report_create():
    return render_template("report_create.html")


@app.route('/report/view')
@login_required
def report_view():
    return render_template("report_view.html")


@app.route('/inventory/formulary',methods=['GET', 'POST', 'PATCH', 'DELETE'])
@login_required
def inventory_formulary():
    return render_template("inventory_formulary.html")


@app.route('/inventory/pasture',methods=['GET','POST','PATCH','DELETE'])
@login_required
def inventory_pasture():
    return render_template("inventory_pasture.html")


@app.route('/inventory/procedure')
@login_required
def inventory_procedure():
    return render_template("inventory_procedure.html")


@app.route('/inspection/submit',methods=['GET','POST'])
@login_required
def inspection_submit():
    return render_template("inspection_submit.html")


@app.route('/inspection/view')
@login_required
def inspection_view():
    return render_template("inspection_view.html")


@app.route('/reproduction/calfadd')
@login_required
def reproduction_add_calf():
    return render_template("reproduction_add_calf.html")


@app.route('/reproduction/listview')
@login_required
def reproduction_view_list():
    return render_template("reproduction_view_list.html")


@app.route('/reproduction/calfview')
@login_required
def reproduction_view_calf():
    return render_template("reproduction_view_calf.html")


@app.route('/health/add',methods=['POST','GET',])
@login_required
def healthadd():
    return render_template("health_add.html")


@app.route('/health/list',methods=['POST','GET','PATCH','DELETE'])
@login_required
def healthlist():
    return render_template("health_list.html")


@app.route('/health/update',methods=['PATCH','GET'])
@login_required
def healthupdate():
    return render_template("health_update.html")


@app.route('/herd/create', methods=['GET','POST'])
@login_required
def herd_create():
    return render_template("herd_create.html")


@app.route('/herd/view')
@login_required
def herd_view():
    return render_template("herd_view.html")


@app.route('/herd/grazing')
@login_required
def herd_grazing():
    return render_template("herd_grazing.html")


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/uploadajax', methods=['POST'])
def upload():
    file = request.files['file']

    if file and allowed_file(file.filename):
         filename = secure_filename(file.filename)
         file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
         return filename,200


if __name__ == '__main__':
    app.run(debug=True)
