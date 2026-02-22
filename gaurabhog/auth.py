import functools

from flask import (
    Blueprint, flash, g, redirect, render_template,
    request, session, url_for
)

from werkzeug.security import check_password_hash, generate_password_hash

from gaurabhog.db import query, query_one
from gaurabhog import get_params


bp = Blueprint('auth', __name__, url_prefix='/auth')
params = get_params()


# ==========================
# REGISTER
# ==========================
@bp.route('/register', methods=('GET', 'POST'))
def register():

    if request.method == 'POST':

        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        error = None

        if not username:
            error = 'Username is required.'

        elif not email:
            error = 'Email is required.'

        elif not password:
            error = 'Password is required.'

        elif query_one(
            'SELECT id FROM users WHERE email = %s',
            (email,)
        ) is not None:

            error = f"Email {email} is already registered."

        elif password != confirm_password:
            error = "Passwords do not match."


        if error is None:

            query(
                '''
                INSERT INTO users (username, password, email)
                VALUES (%s, %s, %s)
                ''',
                (username, generate_password_hash(password), email)
            )

            flash("Registration successful. Please login.")
            return redirect(url_for('auth.login'))


        flash(error)


    return render_template('auth/register.html')


# ==========================
# LOGIN
# ==========================
@bp.route('/', methods=('GET', 'POST'))
def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        error = None

        user = query_one(
            'SELECT * FROM users WHERE email = %s',
            (email,)
        )

        if user is None:
            error = 'Incorrect email.'

        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'


        if error is None:

            session.clear()
            session['user_id'] = user['id']
            session['user_name']=user['username']
            
            next_page = request.args.get("next")

            if next_page:
                return redirect(next_page)

            # admin goes dashboard
            if user['admin']:
                return redirect(url_for('admin.dashboard'))

            # normal user goes homepage
            return redirect(url_for('index'))


        flash(error)


    return render_template('auth/login.html')


# ==========================
# LOGOUT
# ==========================
@bp.route('/logout')
def logout():

    session.clear()

    return redirect(url_for('bhog.index'))


# ==========================
# LOAD USER
# ==========================
@bp.before_app_request
def load_logged_in_user():

    user_id = session.get('user_id')

    if user_id is None:

        g.user = None

    else:

        g.user = query_one(
            'SELECT * FROM users WHERE id = %s',
            (user_id,)
        )


# ==========================
# LOGIN REQUIRED DECORATOR
# ==========================
def login_required(view):

    @functools.wraps(view)
    def wrapped_view(**kwargs):

        if g.user is None:

            return redirect(
                url_for(
                    'auth.login',
                    next=request.url
                )
            )

        return view(**kwargs)

    return wrapped_view


# ==========================
# ADMIN REQUIRED DECORATOR
# ==========================
def admin_required(view):

    @functools.wraps(view)
    def wrapped_view(**kwargs):

        if g.user is None or not g.user['admin']:

            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view