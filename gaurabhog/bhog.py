from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app
)
from werkzeug.exceptions import abort

from gaurabhog.auth import login_required
from gaurabhog.db import query_all, query_one, query
from gaurabhog import get_params


bp = Blueprint('bhog', __name__)
params = get_params()

@bp.route('/')
def index():
    bhog = query_all(
        'SELECT bid, bhog_id, bhog_title, bhog_description, bhog_image, price, status'
        ' FROM bhog'
        ' ORDER BY bid DESC'
    )
    return render_template('bhog/index.html', bhog=bhog, params=params)


@bp.route('/bhog')
def bhog():
    bhog = query_all(
        'SELECT bid, bhog_id, bhog_title, bhog_description, bhog_image, status, price FROM bhog'
        ' ORDER BY bid ASC'
    )
    return render_template('bhog/bhog.html', bhog=bhog, params=params)


@bp.route('/bhog/<string:bhog_id>/view')
def view_bhog(bhog_id):
    bhog = query_one('SELECT * FROM bhog WHERE bhog_id = %s', (bhog_id,))
    if bhog is None:
        abort(404, f"bhog id {bhog_id} doesn't exist.")
    return render_template('bhog/view_bhog.html', bhog=bhog, params=params)


