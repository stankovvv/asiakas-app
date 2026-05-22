#import stuff
import os 
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
from dotenv import load_dotenv
#lataa db .envistä
load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-key')
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')
mysql = MySQL(app)
# Routes
@app.route('/')
def index():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM ASIAKAS ORDER BY id DESC")
    asiakkaat = cur.fetchall()
    cur.close()
    return render_template('index.html', asiakkaat=asiakkaat)

@app.route('/add', methods=['GET', 'POST'])
def uusi_asiakas():
    if request.method == 'POST':
        etunimi = request.form['etunimi'].strip()
        sukunimi = request.form['sukunimi'].strip()
        email = request.form['sahkoposti'].strip()
        puhelin = request.form['puhelin'].strip()
        katuosoite = request.form['katuosoite'].strip()
        postinumero = request.form['postinumero'].strip()
        postitoimipaikka = request.form['postitoimipaikka'].strip()

        #MySQL CONNECTION
        cur = mysql.connection.cursor()
        cur.execute("""
                    INSERT INTO ASIAKAS 
                    (etunimi, sukunimi, sahkoposti, puhelin, katuosoite, postinumero, postinimipaikka) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (etunimi, sukunimi, email, puhelin, katuosoite, postinumero, postitoimipaikka))
        mysql.connection.commit()
        cur.close()
        flash('Asiakas lisätty onnistuneesti!', 'success')
        return redirect(url_for('index'))
    
    return render_template('form.html', asiakas=None, action='lisää')
@app.route('/muokkaa/<int:id>', methods=['GET', 'POST'])
def muokkaa_asiakas(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM ASIAKAS WHERE id = %s", (id,))
    asiakas = cur.fetchone()
    if not asiakas:
        flash('Asiakasta ei löytynyt.', 'error')
        return redirect(url_for('index'))
    if request.method == 'POST':
        etunimi = request.form['etunimi'].strip()
        sukunimi = request.form['sukunimi'].strip()
        email = request.form['sahkoposti'].strip()
        puhelin = request.form['puhelin'].strip()
        katuosoite = request.form['katuosoite'].strip()
        postinumero = request.form['postinumero'].strip()
        postitoimipaikka = request.form['postitoimipaikka'].strip()

        cur.execute("""
                    UPDATE ASIAKAS 
                    SET etunimi=%s, sukunimi=%s, sahkoposti=%s, puhelin=%s, katuosoite=%s, postinumero=%s, postinimipaikka=%s
                    WHERE id=%s
                """, (etunimi, sukunimi, email, puhelin, katuosoite, postinumero, postitoimipaikka, id))
        mysql.connection.commit()
        cur.close()
        flash('Asiakas päivitetty onnistuneesti!', 'success')
        return redirect(url_for('index'))
    cur.close()
    return render_template('form.html', asiakas=asiakas, action='Tallenna muutokset')
#Varmistus ennen poistoa
@app.route("/delete/<int:id>", methods=['GET', 'POST'])
def poista_asiakas(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM ASIAKAS WHERE id = %s", (id,))
    asiakas = cur.fetchone()
    if not asiakas:
        flash('Asiakasta ei löytynyt.', 'error')
        return redirect(url_for('index'))
    #jos pyyntö on POST, suoritetaan poisto
    if request.method == 'POST':
        cur.execute("DELETE FROM ASIAKAS WHERE id = %s", (id,))
        mysql.connection.commit()
        cur.close()

        flash('Asiakas poistettu onnistuneesti!', 'success')
        return redirect(url_for('index'))


    cur.close()
    return render_template('confirm_delete.html', asiakas=asiakas)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
