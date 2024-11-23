from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os


app = Flask(__name__)

# Add `enumerate` as a global function
#app.jinja_env.globals.update(enumerate=enumerate)

# Route for the homepage to display all registration
@app.route('/')
def index():
    conn = sqlite3.connect('registration.db')
    c = conn.cursor()
    c.execute("SELECT * FROM registration")
    registration = c.fetchall()
    
    c.execute("select sum(registration_fees) FROM registration")
    sums = c.fetchone()[0]

    c.execute("select count(*) FROM registration")
    enrolcount = c.fetchone()[0]

    c.execute("select count(*) FROM registration where class=10")
    class10 = c.fetchone()[0]

    c.execute("select count(*) FROM registration where class=11")
    class11 = c.fetchone()[0]
    
    c.execute("select count(*) FROM registration where class=12")
    class12 = c.fetchone()[0]

    conn.close()
   
    return render_template("index.html", registration=registration, sums=sums, enrolcount=enrolcount, class10=class10, class11=class11, class12=class12)


# Route for the homepage to display all registration
@app.route('/feestructure')
def fee_structure():
   
    return render_template("fee_structure.html")


# Route for creating a new register
@app.route('/new', methods=['GET', 'POST'])
def new_register():
    if request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        subject = request.form['subject']
        classs = request.form['class']
        title = request.form['title']
        Regfee = request.form['Regfee']
        comment = request.form['comment']
        
        conn = sqlite3.connect('registration.db')
        c = conn.cursor()
        c.execute("INSERT INTO registration (F_Name, L_Name, Subject, Class, Title, Registration_fees, comment) VALUES (?, ?, ?, ?, ?, ?, ?)", (fname, lname, subject, classs, title, Regfee, comment))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('new_register.html')

# Route for editing an existing register
@app.route('/edit/<int:register_id>', methods=['GET', 'POST'])
def edit_register(register_id):
    conn = sqlite3.connect('registration.db')
    c = conn.cursor()
    c.execute("SELECT * FROM registration WHERE id = ?", (register_id,))
    reg = c.fetchone()

    conn.close()

    if request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        subject = request.form['subject']
        classs = request.form['class']
        title = request.form['title']
        regfee = request.form['regfee']
        comment = request.form['comment']
        conn = sqlite3.connect('registration.db')
      
        c = conn.cursor()
        c.execute("UPDATE registration SET F_Name = ?, L_name = ?, Subject = ?, Class=?,Title=?,Registration_fees=?,comment=? WHERE id = ?", (fname, lname, subject, classs, title, regfee, comment, register_id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('edit_register.html', reg=reg)

# Route for deleting a register
@app.route('/delete/<int:register_id>')
def delete_register(register_id):
    conn = sqlite3.connect('registration.db')
    c = conn.cursor()
    c.execute("DELETE FROM registration WHERE id = ?", (register_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))



if __name__ == "__main__":
      app.run(debug=False, host='0.0.0.0', port=int(os.environ.get("PORT", 3000)))


