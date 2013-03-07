# all the imports
from __future__ import with_statement
import sqlite3
from contextlib import closing
from flask import Flask, request, session, g, redirect, url_for, \
	abort, render_template, flash
import os

###############################################################################
# GLOBAL Config

# create our little application :)
app = Flask(__name__)
# pulls all capitalized variables from this file as config
app.config.from_object(__name__)
# allows for specification of a config file other than default
app.config.from_envvar('GT_SETTINGS', silent=True)
###############################################################################


###############################################################################
# DATABASE FUNCTIONS

def connect_db():
	return sqlite3.connect(app.config['DATABASE'])

def init_db():
	with closing(connect_db()) as db:
		with app.open_resource('schema.sql') as f:
			db.cursor().executescript(f.read())
		db.commit()

@app.before_request
def before_request():
	g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
	g.db.close()

def query_db(query, args=(), one=False):
	cur = g.db.execute(query, args)
	rv = [dict((cur.description[idx][0], value)
			for idx, value in enumerate(row))
			 for row in cur.fetchall()]

	return (rv[0] if rv else None) if one else rv
###############################################################################


###############################################################################
# APP CODE
@app.route('/')
def show_participants():
	cur = g.db.execute('select \
			user_id, \
			age, \
			gender, \
			nat_lang, \
			oth_lang, \
			years_eng, \
			years_eng_cnt \
			from participants order by r_id desc')
	participants = [dict( \
			user_id=row[0], \
			age=row[1], \
			gender=row[2], \
			nat_lang=row[3], \
			oth_lang=row[4], \
			years_eng=row[5], \
			years_eng_cnt=row[6]) \
			for row in cur.fetchall()]
	return render_template('show_participants.html', participants=participants)


@app.route('/add_participant', methods=['POST'])
def add_participant():
	if not session.get('logged_in'):
		abort(401)
	g.db.execute('insert into participants \
			(user_id, age, gender, nat_lang, oth_lang, years_eng, years_eng_cnt) \
			values (?, ?, ?, ?, ?, ?, ?)', \
			[session['user_id'], \
			request.form['age'], \
			request.form['gender'], \
			request.form['nat_lang'], \
			request.form['oth_lang'], \
			request.form['years_eng'], \
			request.form['years_eng_cnt']])
	g.db.commit()

	flash('New participant was successfully posted')
	return redirect(url_for('show_participants'))



@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	if request.method == 'POST':
		user_id = request.form['user_id']
		user = query_db('select * from participants where user_id=?',
                [user_id], one=True)
		if user is None:
			session['logged_in'] = True
			session['user_id'] = user_id
			flash('You were logged in')
			return redirect(url_for('show_participants'))
		else:
		    error = str(user['user_id']) + \
		    ' is already taken, contact an administrator.'

	return render_template('login.html', error=error)

@app.route('/logout')
def logout():
	session.pop('logged_in', None)
	flash('You were logged out')
	return redirect(url_for('show_participants'))

###############################################################################









###############################################################################
## RUN THE PROGRAM
if __name__ == '__main__':
	# must get the port number from heroku
	# environment variable and look for all open
	# connections
	port = int(os.environ.get('PORT', 5000))
	app.run(host='0.0.0.0', port=port)







