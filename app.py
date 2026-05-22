from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
 
import os

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

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
            class_=request.form['class'],
            title=request.form['title'],
            registration_fees=request.form['Regfee'],
            comment=request.form['comment']
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
        reg.f_name = request.form['fname']
        reg.l_name = request.form['lname']
        reg.subject = request.form['subject']
        reg.class_ = request.form['class']
        reg.title = request.form['title']
        reg.registration_fees = request.form['regfee']
        reg.comment = request.form['comment']

        db.session.commit()
        return redirect(url_for('index'))

    return render_template('edit_register.html', reg=reg)


# Route for deleting a register
@app.route('/delete/<int:register_id>', methods=['POST'])
def delete_register(register_id):
    reg = Registration.query.get_or_404(register_id)
    db.session.delete(reg)
    db.session.commit()
    return redirect(url_for('index'))


if __name__ == "__main__":
      app.run(debug=False, host='0.0.0.0', port=int(os.environ.get("PORT", 3000)))


