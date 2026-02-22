import os
import uuid

from flask import (
    Blueprint, flash, redirect, render_template,
    request, url_for, g
)

from gaurabhog.auth import login_required
from gaurabhog.db import query, query_one, query_all
from gaurabhog import get_params

import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException


bp = Blueprint('order', __name__, url_prefix='/order')
params = get_params()


# ==========================
# PLACE ORDER
# ==========================
@bp.route('/place/<string:bhog_id>', methods=('GET', 'POST'))
@login_required
def order(bhog_id):

    bhog = query_one(
        "SELECT * FROM bhog WHERE bhog_id = %s",
        (bhog_id,)
    )

    if bhog is None:
        flash("Bhog not found.")
        return redirect(url_for('bhog.index'))

    if request.method == 'POST':

        quantity = int(request.form['quantity'])
        address = request.form['address']
        phone = request.form['phone']

        total_price = int(bhog['price']) * quantity

        confirmation_token = str(uuid.uuid4())

        # Save order
        query(
            """
            INSERT INTO orders
            (user_id, bhog_id, quantity, total_price,
             address, phone, status, is_confirmed, confirmation_token)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                g.user['id'],
                bhog_id,
                quantity,
                total_price,
                address,
                phone,
                "PENDING",
                False,
                confirmation_token
            )
        )

        # Send confirmation email
        send_confirmation_email(
            g.user['email'],
            confirmation_token,
            bhog['bhog_title']
        )

        flash("Order placed! Please confirm from your email.", "success")

        return redirect(url_for('bhog.index'))

    return render_template(
        "order/order.html",
        bhog=bhog,
        params=params
    )


# ==========================
# CONFIRM ORDER
# ==========================
@bp.route('/confirm/<token>')
def confirm_order(token):

    order = query_one(
        "SELECT * FROM orders WHERE confirmation_token = %s",
        (token,)
    )

    if order is None:
        flash("Invalid confirmation link.", "danger")
        return redirect(url_for('bhog.index'))

    query(
        """
        UPDATE orders
        SET is_confirmed = TRUE,
            status = 'CONFIRMED'
        WHERE confirmation_token = %s
        """,
        (token,)
    )

    flash("Order confirmed successfully!", "success")

    return redirect(url_for('bhog.index'))


# ==========================
# USER ORDER HISTORY
# ==========================
@bp.route('/my_orders')
@login_required
def my_orders():

    orders = query_all(
        """
        SELECT o.*, b.bhog_title, b.bhog_image
        FROM orders o
        JOIN bhog b ON o.bhog_id = b.bhog_id
        WHERE o.user_id = %s
        ORDER BY o.id DESC
        """,
        (g.user['id'],)
    )

    return render_template(
        "order/order.html",
        orders=orders,
        params=params
    )


# ==========================
# SEND EMAIL FUNCTION
# ==========================
def send_confirmation_email(user_email, token, bhog_title):

    api_key = os.environ.get("brevo_api_key")
    sender_email = os.environ.get("verified_sender")

    if not api_key or not sender_email:
        print("Brevo environment variables missing")
        return

    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = api_key

    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
        sib_api_v3_sdk.ApiClient(configuration)
    )

    confirm_link = f"https://gaurabhog.onrender.com/order/confirm/{token}"

    html_content = f"""
    <h2>Confirm your order</h2>

    <p>You ordered: <b>{bhog_title}</b></p>

    <p>Click below to confirm:</p>

    <a href="{confirm_link}"
       style="
       background:#28a745;
       color:white;
       padding:10px 20px;
       text-decoration:none;
       border-radius:5px;">
       Confirm Order
    </a>

    <p>If you did not place this order, ignore this email.</p>
    """

    email = sib_api_v3_sdk.SendSmtpEmail(
        sender={"email": sender_email, "name": "GauraBhog"},
        to=[{"email": user_email}],
        subject="Confirm your GauraBhog order",
        html_content=html_content
    )

    try:
        api_instance.send_transac_email(email)
        print("Confirmation email sent")

    except ApiException as e:
        print("Email error:", e)