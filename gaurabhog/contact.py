from flask import (
    Blueprint, flash, redirect, render_template, request, url_for, current_app
)

from gaurabhog.db import query
from gaurabhog import get_params

import os
from dotenv import load_dotenv
load_dotenv() 

import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from sib_api_v3_sdk import ApiClient, Configuration

bp = Blueprint('contact', __name__, url_prefix='/contact')

@bp.route('/', methods=('GET', 'POST'))
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        subject = request.form['subject']
        message = request.form['message']

        # Save message to DB
        query(
            'INSERT INTO contact (name, email, subject, message) VALUES (%s, %s, %s, %s)',
            (name, email, subject, message)
        )

        # ---- Brevo API Setup ----
        configuration = Configuration()
        configuration.api_key = {'api-key': os.environ('brevo_api_key')} 

        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(ApiClient(configuration))

        email_to_admin = sib_api_v3_sdk.SendSmtpEmail(
            sender={"name": "GauraBhog(noreply)", "email": os.environ('verified_sender')},
            to=[{"email": os.environ('admin_email'), "name": "Admin"}],
            subject=subject,
            html_content=f"""
                <h3>New Contact Form Message</h3>
                <p><strong>Name:</strong> {name}</p>
                <p><strong>Email:</strong> {email}</p>
                <p><strong>Message:</strong><br>{message}</p>
            """
        )

        try:
            api_instance.send_transac_email(email_to_admin)
        except ApiException as e:
            flash(f"Error sending email: {e}", "error")
            print(1, e)
            return redirect(url_for('contact.contact'))

        flash('Your message has been sent successfully!')
        return redirect(url_for('index'))

    return render_template('contact/contact.html', params=get_params())