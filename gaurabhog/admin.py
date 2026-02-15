import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)

import os

from gaurabhog.db import query, query_one, query_all
from gaurabhog.auth import admin_required
from gaurabhog import get_params
from gaurabhog.supabase_client import upload_bhog_image, delete_bhog_image


bp = Blueprint('admin', __name__, url_prefix='/admin')
params = get_params()



@bp.route('/')
@admin_required
def dashboard():
    return redirect(url_for('admin.manage_bhog')) 
    # return render_template('admin/dashboard.html')



# User management routes
@bp.route('/users')
@admin_required
def manage_users():
    users = query_all('SELECT id, username, email, admin FROM users')
    return render_template('admin/users/manage_users.html', users=users, params=params)


@bp.route('/promote/<int:user_id>')
@admin_required
def promote_user(user_id):
    query('UPDATE users SET admin = TRUE WHERE id = %s', (user_id,))
    flash('User promoted to admin.')
    return redirect(url_for('admin.manage_users'))


@bp.route('/demote/<int:user_id>')
@admin_required
def demote_user(user_id):
    query('UPDATE users SET admin = FALSE WHERE id = %s', (user_id,))
    flash('User demoted from admin.')
    return redirect(url_for('admin.manage_users'))


@bp.route('/delete/<int:user_id>')
@admin_required
def delete_user(user_id):
    query('DELETE FROM users WHERE id = %s', (user_id,))
    flash('User deleted.')
    return redirect(url_for('admin.manage_users'))



# bhog management routes
@bp.route('/bhog')
@admin_required
def manage_bhog():
    bhog = query_all('SELECT bid, bhog_id, bhog_title, bhog_description FROM bhog ORDER BY cid ASC')
    return render_template('admin/bhog/manage_bhog.html', bhog=bhog, params=params)


@bp.route('/delete_bhog/<int:cid>')
@admin_required
def delete_bhog(cid):
    # Get bhog image URL before deleting record
    bhog = query_one(
        'SELECT bhog_image FROM bhog WHERE cid = %s',
        (cid,)
    )

    # ✅ Delete image from Supabase if it exists
    if bhog and bhog['bhog_image']:
        delete_bhog_image(bhog['bhog_image'])

 

    flash('bhog deleted.')
    return redirect(url_for('admin.manage_bhog'))


@bp.route('/add_bhog', methods=('GET', 'POST'))
@admin_required
def add_bhog():
    if request.method == 'POST':
        bhog_id = request.form['bhog_id']
        bhog_title = request.form['bhog_title']
        bhog_description = request.form['bhog_description']
        bhog_image = request.files['bhog_image']

        image_url = upload_bhog_image(bhog_image)

        query(
            'INSERT INTO bhog (bhog_id, bhog_title, bhog_description, bhog_image) VALUES (%s, %s, %s, %s)',
            (bhog_id, bhog_title, bhog_description, image_url)
        )
        flash('bhog added successfully.')
        return redirect(url_for('admin.manage_bhog'))

    return render_template('admin/bhog/add_bhog.html', params=params)


@bp.route('/edit_bhog/<int:cid>', methods=('GET', 'POST'))
@admin_required
def edit_bhog(cid):
    bhog = query_one('SELECT cid, bhog_id, bhog_title, bhog_description, bhog_image FROM bhog WHERE cid = %s', (cid,))
    if request.method == 'POST':
        bhog_id = request.form['bhog_id']
        bhog_title = request.form['bhog_title']
        bhog_description = request.form['bhog_description']
        bhog_image = request.files['bhog_image']

        if bhog_image:
            delete_bhog_image(bhog['bhog_image'])
            new_bhog_image = upload_bhog_image(bhog_image)
        else:
            new_bhog_image = bhog['bhog_image']

        query(
            'UPDATE bhog SET bhog_id = %s, bhog_title = %s, bhog_description = %s, bhog_image = %s WHERE cid = %s',
            (bhog_id, bhog_title, bhog_description, new_bhog_image, cid)
        )
        flash('bhog updated successfully.')
        return redirect(url_for('admin.manage_bhog'))

    return render_template('admin/bhog/edit_bhog.html', bhog=bhog, params=params)


