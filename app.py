from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
 
import os
import requests

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Registration(db.Model):
    __tablename__ = 'registration'

    id = db.Column(db.Integer, primary_key=True)
    f_name = db.Column('F_Name', db.String(30), nullable=False)
    l_name = db.Column('L_Name', db.String(30), nullable=False)
    subject = db.Column('Subject', db.String(30))
    class_ = db.Column('Class', db.Integer, nullable=False)
    title = db.Column('Title', db.String(50))
    registration_fees = db.Column('Registration_fees', db.Float)
    comment = db.Column('comment', db.String(50))
    status = db.Column('status', db.String(10), default=' ')   
    mobile = db.Column('mobile', db.String(10), nullable=True)    

# ✅ Create tables if they don't exist
with app.app_context():
    db.create_all()

# Add `enumerate` as a global function
#app.jinja_env.globals.update(enumerate=enumerate)

# Route for the homepage to display all registration

@app.route('/')
def index():
    # Fetch all registrations
    registration = Registration.query.all()

    # Sum of registration fees
    sums = db.session.query(db.func.sum(Registration.registration_fees)).scalar() or 0

    # Total enrollment count
    enrolcount = Registration.query.count()

    # Count by class
    class10 = Registration.query.filter_by(class_=10).count()
    class11 = Registration.query.filter_by(class_=11).count()
    class12 = Registration.query.filter_by(class_=12).count()

    return render_template("index.html", registration=registration, sums=sums, enrolcount=enrolcount, class10=class10, class11=class11, class12=class12)

# Route for the homepage to display all registration
@app.route('/feestructure')
def fee_structure():
   
    return render_template("fee_structure.html")


@app.route('/new', methods=['GET', 'POST'])
def new_register():
    if request.method == 'POST':
        new_student = Registration(
            f_name=request.form['fname'],
            l_name=request.form['lname'],
            subject=request.form['subject'],
            class_=int(request.form['class']),
            title=request.form['title'],
            registration_fees=float(request.form['Regfee']),
            comment=request.form['comment'],
            status=request.form['status'],
            mobile=request.form['mobile']
        )
        db.session.add(new_student)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('new_register.html')


# Route for editing an existing register
@app.route('/edit/<int:register_id>', methods=['GET', 'POST'])
def edit_register(register_id):
    reg = Registration.query.get_or_404(register_id)

    if request.method == 'POST':
        old_status = reg.status                    # save old status
        reg.f_name = request.form['fname']
        reg.l_name = request.form['lname']
        reg.subject = request.form['subject']
        reg.class_ = int(request.form['class'])
        reg.title = request.form['title']
        reg.registration_fees = float(request.form['regfee'])
        reg.comment = request.form['comment']
        reg.mobile = request.form['mobile']
        reg.status = request.form['status'] 

        db.session.commit()
          # ✅ Trigger SMS only when status changes to 'completed'
        if old_status != 'completed' and reg.status == 'completed':
            send_sms(reg.mobile, f"{reg.f_name} {reg.l_name}")
        return redirect(url_for('index'))

    return render_template('edit_register.html', reg=reg)


# Route for deleting a register
@app.route('/delete/<int:register_id>', methods=['POST'])
def delete_register(register_id):
    reg = Registration.query.get_or_404(register_id)
    db.session.delete(reg)
    db.session.commit()
    return redirect(url_for('index'))


 
# Route for SMS API  
def send_sms(mobile, fname):
    api_key = os.environ.get('FAST2SMS_API_KEY')  # store in env variable
    
    message = f"Dear {fname}, your registration is now completed. Welcome!"
    
    url = "https://www.fast2sms.com/dev/bulkV2"
    payload = {
        "route": "q",                    # transactional route
        "message": message,
        "language": "english",
        "flash": 0,
        "numbers": mobile       # 10 digit mobile number
    }
    headers = {
        "authorization": api_key,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    response = requests.post(url, data=payload, headers=headers)
    return response.json()

if __name__ == "__main__":
      app.run(debug=True, host='0.0.0.0', port=int(os.environ.get("PORT", 3000)))


