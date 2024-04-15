from flask import Flask, render_template, request, redirect, url_for, session, abort
import pymysql

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dsfgj56547jgfkh90gh4ogot'

#ToDo захешировать пароли


connection = pymysql.connect(
        host='mysql-db',
        port=3306,
        user='root',
        password='hytgbn',
        database='todolist',
        cursorclass=pymysql.cursors.DictCursor
    )

print("successfully connected...")
print("#" * 20)


def check_user(username, password):
    with connection.cursor() as cursor:
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        cursor.execute(query)
        result = cursor.fetchone()
        return result is not None


@app.route('/main_page', methods=['GET', 'POST'])
def main_page():
    if not 'username' in session:
        return redirect(url_for('login'))
    with connection.cursor() as cursor:
        user_query = f"SELECT * FROM users WHERE username = '{session['username']}'"
        cursor.execute(user_query)
        user = cursor.fetchone()
        if request.method == 'GET':
            notes_query = f"SELECT * FROM notes WHERE user_id = {user['id']}"
            cursor.execute(notes_query)
            notes = cursor.fetchall()
            return render_template('index.html', notes=notes)
        # post
        note = request.form.get('note')
        if note:
            insert_note = f"INSERT INTO notes (user_id, note) VALUES ({user['id']}, '{note}')"
            cursor.execute(insert_note)
            connection.commit()
            return redirect(url_for('main_page'))


@app.route('/delete-note/<int:note_id>/')
def delete_note(note_id):
    if 'username' in session:
        with connection.cursor() as cursor:
            get_query = f"SELECT * FROM notes WHERE id = {note_id}"
            cursor.execute(get_query)
            result = cursor.fetchone()
            user_query = f"SELECT * FROM users WHERE username = '{session['username']}'"
            cursor.execute(user_query)
            user = cursor.fetchone()
            if user['id'] != result['user_id']:
                abort(403)
            if result is not None:
                delete_query = f"DELETE FROM notes WHERE id = {note_id}"
                cursor.execute(delete_query)
                connection.commit()
            return redirect(url_for('main_page'))


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if check_user(username, password):
            session['username'] = username
            return redirect(url_for('main_page'))
        return render_template('login.html', error_message='Invalid username or password')
    return render_template('login.html')


@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    if request.method != 'POST':
        return render_template('sign_up.html')
    username = request.form['username']
    password = request.form['password']
    with connection.cursor() as cursor:
        user_query = f"SELECT * FROM users WHERE username = '{username}'"
        cursor.execute(user_query)
        isFound = cursor.fetchone()
        if isFound is not None:
            return render_template('sign_up.html', error_message='This username already exists')
        add_user = f"INSERT INTO users (username, password) VALUES ('{username}', '{password}')"
        cursor.execute(add_user)
        connection.commit()
        session['username'] = username
        return redirect(url_for('main_page'))


@app.route('/logout')
# @login_required
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/delete_account', methods=['GET', 'POST'])
def delete_account():
    if 'username' not in session:
        abort(403)
    else:
        if request.method == 'POST':
            password = request.form['password']
            if check_user(session['username'], password):
                with connection.cursor() as cursor:
                    user_query = f"SELECT * FROM users WHERE username = '{session['username']}' AND password = '{password}'"
                    cursor.execute(user_query)
                    user = cursor.fetchone()
                    delete_query = f"DELETE FROM users WHERE id = '{user['id']}'"
                    cursor.execute(delete_query)
                session.pop('username', None)
                return redirect(url_for('login'))
            return render_template('delete_account.html', error_message='Invalid password')
        return render_template('delete_account.html')


@app.errorhandler(404)
def page_not_found(e):
    return "Page not found", 404


if __name__ == '__main__':
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.run(debug=True, host='0.0.0.0')
