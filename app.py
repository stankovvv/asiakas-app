import os
import re
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
from dotenv import load_dotenv

# Lataa ympäristömuuttujat .env-tiedostosta
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-key')

app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')

mysql = MySQL(app)


# Validointifunktio
def validate(form):
    errors = []

    if not form.get('etunimi', '').strip():
        errors.append('Etunimi ei saa olla tyhjä.')

    if not form.get('sukunimi', '').strip():
        errors.append('Sukunimi ei saa olla tyhjä.')

    email = form.get('sahkoposti', '').strip()
    if email and not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        errors.append('Sähköpostiosoite ei kelpaa.')

    return errors


# Muuntaa tietokantarivin sanakirjaksi
def row_to_asiakas(row):
    if not row:
        return None

    return {
        "id": row[0],
        "etunimi": row[1],
        "sukunimi": row[2],
        "sahkoposti": row[3],
        "puhelin": row[4],
        "katuosoite": row[5],
        "postinumero": row[6],
        "postitoimipaikka": row[7],
    }


# Etusivu: listaa asiakkaat
@app.route('/')
def index():
    cur = mysql.connection.cursor()
    try:
        cur.execute("""
            SELECT id, etunimi, sukunimi, sahkoposti, puhelin, katuosoite, postinumero, postitoimipaikka
            FROM ASIAKAS
            ORDER BY id DESC
        """)
        rows = cur.fetchall()
    finally:
        cur.close()

    asiakkaat = [row_to_asiakas(row) for row in rows]

    return render_template('index.html', asiakkaat=asiakkaat)


# Lisää uusi asiakas
@app.route('/add', methods=['GET', 'POST'])
def uusi_asiakas():
    if request.method == 'POST':
        etunimi = request.form.get('etunimi', '').strip()
        sukunimi = request.form.get('sukunimi', '').strip()
        email = request.form.get('sahkoposti', '').strip()
        puhelin = request.form.get('puhelin', '').strip()
        katuosoite = request.form.get('katuosoite', '').strip()
        postinumero = request.form.get('postinumero', '').strip()
        postitoimipaikka = request.form.get('postitoimipaikka', '').strip()

        errors = validate(request.form)
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('form.html', asiakas=request.form, action='lisää')

        cur = mysql.connection.cursor()
        try:
            cur.execute("""
                INSERT INTO ASIAKAS
                (etunimi, sukunimi, sahkoposti, puhelin, katuosoite, postinumero, postitoimipaikka)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (etunimi, sukunimi, email, puhelin, katuosoite, postinumero, postitoimipaikka))
            mysql.connection.commit()
            flash('Asiakas lisätty onnistuneesti!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Tietokantavirhe: {e}', 'error')
        finally:
            cur.close()

    return render_template('form.html', asiakas=None, action='lisää')


# Muokkaa asiakasta
@app.route('/muokkaa/<int:id>', methods=['GET', 'POST'])
def muokkaa_asiakas(id):
    cur = mysql.connection.cursor()
    try:
        cur.execute("""
            SELECT id, etunimi, sukunimi, sahkoposti, puhelin, katuosoite, postinumero, postitoimipaikka
            FROM ASIAKAS
            WHERE id = %s
        """, (id,))
        row = cur.fetchone()
        asiakas = row_to_asiakas(row)

        if not asiakas:
            flash('Asiakasta ei löytynyt.', 'error')
            return redirect(url_for('index'))

        if request.method == 'POST':
            errors = validate(request.form)
            if errors:
                for error in errors:
                    flash(error, 'error')

                # Säilytetään käyttäjän syöttämät arvot lomakkeella
                asiakas_form = {
                    "id": id,
                    "etunimi": request.form.get('etunimi', '').strip(),
                    "sukunimi": request.form.get('sukunimi', '').strip(),
                    "sahkoposti": request.form.get('sahkoposti', '').strip(),
                    "puhelin": request.form.get('puhelin', '').strip(),
                    "katuosoite": request.form.get('katuosoite', '').strip(),
                    "postinumero": request.form.get('postinumero', '').strip(),
                    "postitoimipaikka": request.form.get('postitoimipaikka', '').strip(),
                }
                return render_template('form.html', asiakas=asiakas_form, action='Tallenna muutokset')

            etunimi = request.form.get('etunimi', '').strip()
            sukunimi = request.form.get('sukunimi', '').strip()
            email = request.form.get('sahkoposti', '').strip()
            puhelin = request.form.get('puhelin', '').strip()
            katuosoite = request.form.get('katuosoite', '').strip()
            postinumero = request.form.get('postinumero', '').strip()
            postitoimipaikka = request.form.get('postitoimipaikka', '').strip()

            cur.execute("""
                UPDATE ASIAKAS
                SET etunimi = %s,
                    sukunimi = %s,
                    sahkoposti = %s,
                    puhelin = %s,
                    katuosoite = %s,
                    postinumero = %s,
                    postitoimipaikka = %s
                WHERE id = %s
            """, (etunimi, sukunimi, email, puhelin, katuosoite, postinumero, postitoimipaikka, id))

            mysql.connection.commit()
            flash('Asiakas päivitetty onnistuneesti!', 'success')
            return redirect(url_for('index'))

    except Exception as e:
        mysql.connection.rollback()
        flash(f'Tietokantavirhe: {e}', 'error')
        return redirect(url_for('index'))
    finally:
        cur.close()

    return render_template('form.html', asiakas=asiakas, action='Tallenna muutokset')


# Varmistus ennen poistoa
@app.route('/delete/<int:id>', methods=['GET', 'POST'])
def poista_asiakas(id):
    cur = mysql.connection.cursor()
    try:
        cur.execute("""
            SELECT id, etunimi, sukunimi, sahkoposti, puhelin, katuosoite, postinumero, postitoimipaikka
            FROM ASIAKAS
            WHERE id = %s
        """, (id,))
        row = cur.fetchone()
        asiakas = row_to_asiakas(row)

        if not asiakas:
            flash('Asiakasta ei löytynyt.', 'error')
            return redirect(url_for('index'))

        if request.method == 'POST':
            cur.execute("DELETE FROM ASIAKAS WHERE id = %s", (id,))
            mysql.connection.commit()
            flash('Asiakas poistettu onnistuneesti!', 'success')
            return redirect(url_for('index'))

    except Exception as e:
        mysql.connection.rollback()
        flash(f'Tietokantavirhe: {e}', 'error')
        return redirect(url_for('index'))
    finally:
        cur.close()

    return render_template('confirm_delete.html', asiakas=asiakas)


# Terveystarkistus endpoint
@app.route('/health', methods=['GET'])
def health_check():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT 1")
        cur.fetchone()
        cur.close()
        return {"status": "ok", "database": "ok"}, 200
    except Exception:
        return {"status": "error", "database": "down"}, 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)