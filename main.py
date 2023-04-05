import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session
from jinja2.nodes import Test
from sqlalchemy import Column, Integer, String, Numeric, create_engine, text, Table, MetaData, select, engine, and_
from flask_mysqldb import MySQL
import MySQLdb.cursors
from sqlalchemy.engine import cursor
app = Flask(__name__)
app.debug = True
app.secret_key = 'Budders23!'

# connection string is in the format mysql://Root:Budders23!@server/boatdb
connection = "mysql://root:Budders23!@localhost/final106"
engine = create_engine(connection, echo=True)
conn = engine.connect()


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/studentlogin', methods=['POST', 'GET'])
def studentlogin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        query = text("SELECT * FROM accounts160 WHERE email = :email AND password = :password")
        params = {"email": email, "password": password}
        result = conn.execute(query, params)
        user = result.fetchone()
        if user is None:
            return render_template('index.html')
        else:
            session['id'] = user[0]
            session['type'] = user[1]
            session['email'] = user[2]
            session['first_name'] = user[3]
            session['last_name'] = user[4]
            if user[0] in [0, 1, 2]:
                return redirect(url_for('teacher'))
            else:
                tests = conn.execute(text("SELECT test_id FROM tests160"))
                return render_template('studentpage.html', tests=tests)
    else:
        return render_template('index.html')



@app.route('/test/<int:test_id>')
def display_test(test_id):
    query = text("SELECT * FROM tests160 WHERE id = :test_id")
    params = {"test_id": test_id}
    result = conn.execute(query, params)
    test = result.fetchone()
    if test:
        test_id, _, q1, q2, q3, q4, q5 = test
        questions = [q1, q2, q3, q4, q5]
        return render_template('tests.html', test_id=test_id, questions=questions[:5])
    else:
        return render_template('404.html'), 404


@app.route('/submit-answers/<int:test_id>', methods=['POST', 'GET'])
def submit_answers(test_id):
    if request.method == 'POST':
        answers = [request.form.get('q1'), request.form.get('q2'), request.form.get('q3'), request.form.get('q4'),
                   request.form.get('q5')]
        query = text("INSERT INTO answers (test_id, id, q1_answer, q2_answer, q3_answer, q4_answer, q5_answer) "
                     "VALUES (:test_id, :student_id, :q1_answer, :q2_answer, :q3_answer, :q4_answer, :q5_answer)")
        params = {"test_id": test_id, "student_id": session['id'], "q1_answer": answers[0], "q2_answer": answers[1], "q3_answer": answers[2], "q4_answer": answers[3], "q5_answer": answers[4]}
        conn.execute(query, params)
        tests = conn.execute(text("SELECT test_id FROM tests160"))
        return render_template('studentpage.html', tests=tests)
    else:
        tests = conn.execute(text("SELECT test_id FROM tests160"))
        return render_template('studentpage.html', tests=tests)


@app.route('/add-student', methods=['POST'])
def add_student():
    id = request.form['id']
    type = 'Student'
    email = request.form['email']
    password = request.form['password']
    first_name = request.form['first_name']
    last_name = request.form['last_name']

    query = text("INSERT INTO accounts160 (id, type, email, password, first_name, last_name) "
                 "VALUES (:id, :type, :email, :password, :first_name, :last_name)")
    params = {"id": id, "type": type, "email": email, "password": password, "first_name": first_name, "last_name": last_name}
    with engine.connect() as conn:
        conn.execute(query, params)
        conn.commit()
    return redirect(url_for('teacher'))


@app.route('/teacher', methods=['GET', 'POST'])
def teacher():
    accounts = conn.execute(text("select * from accounts160")).all()
    tests = conn.execute(text("SELECT test_id FROM tests160"))
    print(accounts)
    return render_template('teacher.html', accounts=accounts, tests=tests)


@app.route('/delete-account/<int:id>', methods=['GET', 'POST'])
def delete_account(id):
    query = text("DELETE FROM accounts160 WHERE id = :id")
    params = {"id": id}
    conn.execute(query, params)
    conn.commit()
    return redirect(url_for('teacher'))


@app.route('/create_test', methods=['GET', 'POST'])
def create_test():
    if request.method == 'POST':
        test_id = request.form['test_id']
        id = session['id']
        q1 = request.form['q1']
        q2 = request.form['q2']
        q3 = request.form['q3']
        q4 = request.form['q4']
        q5 = request.form['q5']
        with engine.connect() as con:
            sql = text(
                'INSERT INTO tests160 (test_id, id, q1, q2, q3, q4, q5) VALUES (:test_id, :id, :q1, :q2, :q3, :q4, :q5)')
            params = {"test_id": test_id, "id": session['id'], "q1": q1, "q2": q2, "q3": q3, "q4": q4, "q5": q5}
            con.execute(sql, params)
            con.commit()
        return 'Test created successfully!'
    return redirect(url_for('teacher'))


@app.route('/delete-test/<int:test_id>', methods=['GET', 'POST'])
def delete_test(test_id):
    query = text("DELETE FROM tests160 WHERE test_id = :test_id")
    params = {"test_id": test_id}
    conn.execute(query, params)
    conn.commit()
    return redirect(url_for('teacher'))


# @app.route('/boats/<int:id>/delete', methods=['POST'])
# def delete_boat(id):
#     con.execute(text("DELETE FROM boats WHERE id=:id"), {"id": id})
#     return redirect(url_for('boat'))


if __name__ == '__main__':
    app.run(debug=True)
