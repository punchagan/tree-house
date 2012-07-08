# -*- coding: utf-8 -*-
from flask import (request, render_template, session,
    flash, redirect, url_for)
from app import app

@app.route('/')
def index():
    # FIXME: Think about what the index page should be like
    return render_template('index.html', title='Tree House')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # FIXME: currently allows login only with one username and password
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You successfully logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You successfully logged out')
    return redirect('/')

@app.route('/show_entries')
def show_entries():
    return render_template('show_entries.html')

@app.route('/roi')
def roi_():
    return render_template('roi.html')
