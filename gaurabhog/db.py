import psycopg2, psycopg2.extras
from datetime import datetime

import click
from flask import current_app, g


def get_db():
    if 'db' not in g:
        g.db = psycopg2.connect(
            current_app.config['DATABASE_URL'],
            sslmode='require',
            cursor_factory=psycopg2.extras.RealDictCursor
        )

    return g.db


def query_one(sql, params=None):
    db = get_db()
    cur = db.cursor()
    cur.execute(sql, params)
    result = cur.fetchone()
    cur.close()
    return result


def query_all(sql, params=None):
    db = get_db()
    cur = db.cursor()
    cur.execute(sql, params)
    result = cur.fetchall()
    cur.close()
    return result


def query(sql, params=None):
    db = get_db()
    cur = db.cursor()
    cur.execute(sql, params)
    db.commit()
    cur.close()


# Close database connection
def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


@click.command('init-db')
def init_db_command():
    """Test database connection."""
    try:
        db = psycopg2.connect(current_app.config['DATABASE_URL'], sslmode="require")
        db.close()
        click.echo('Database connection successful ✅')
    except Exception as e:
        click.echo(f'Database connection failed ❌: {e}')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)