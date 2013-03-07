# all the imports
from __future__ import with_statement
from contextlib import closing
from flask import Flask, request, session, g, redirect, url_for, \
	abort, render_template, flash
import os


from flask_sqlalchemy import SQLAlchemy



###############################################################################
# GLOBAL Config

DATABASE_URL = os.environ['DATABASE_URL']

# create our little application :)
app = Flask(__name__)
# pulls all capitalized variables from this file as config
app.config.from_object(__name__)
# allows for specification of a config file other than default
app.config.from_envvar('GT_SETTINGS', silent=True)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
db = SQLAlchemy(app)
###############################################################################





###############################################################################
# DATABASE STUFF
class Participant(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	age = db.Column(db.Integer)
	gender = db.Column(db.String(120))
	nativeLanguage = db.Column(db.String(120))
	otherLanguages = db.Column(db.String(120))
	yearsEnglish = db.Column(db.Integer)
	yearsEngCountry = db.Column(db.Integer)

	def __init__(self, 
			age, gender, nativeLanguage, otherLanguages,
			yearsEnglish, yearsEngCountry):
		self.age = age
		self.gender = gender
		self.nativeLanguage = nativeLanguage
		self.otherLanguages = otherLanguages
		self.yearsEnglish = yearsEnglish
		self.yearsEngCountry = yearsEngCountry

	def __repr__(self):
		return '<Participant %r>' % self.nativeLanguage

###############################################################################


###############################################################################
# APP CODE
@app.route('/')
def show_participants():
	participants = Participant.query.all()
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







