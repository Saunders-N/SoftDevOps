from flask import (Blueprint, flash, g, redirect, render_template, request, url_for)
from werkzeug.exceptions import abort

from .auth import login_required
from .db import get_db

bp = Blueprint('ticket', __name__)

def get_ticket(id, check_author=True):
    ticket = get_db().execute(
        'SELECT t.id, title, body, created, author_id, username'
        ' FROM ticket t JOIN user u ON t.author_id = u.id'
        ' WHERE t.id = ?',
        (id,)
    ).fetchone()

    if ticket is None:
        abort(404, f"Ticket id {id} doesn't exist.")

    if check_author and ticket['author_id'] != g.user['id']:
        abort(403)

    return ticket

@bp.route('/')
@login_required
def index():
    db = get_db()
    ticket = db.execute(
        'SELECT t.id, title, body, created, author_id, username, resolved'
        ' FROM ticket t JOIN user u ON t.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('ticket/index.html', ticket=ticket)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO ticket (title, body, author_id)'
                ' VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('ticket.index'))



    return render_template('ticket/create.html')

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    ticket = get_ticket(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE ticket SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('ticket.index'))

    return render_template('ticket/update.html', ticket=ticket)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_ticket(id)
    db = get_db()
    db.execute('DELETE FROM ticket WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('ticket.index'))