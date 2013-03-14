# all the imports
from __future__ import with_statement
from contextlib import closing
from flask import Flask, request, session, g, redirect, url_for, \
	abort, render_template, flash
import os
from random import shuffle
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
app.debug = True
db = SQLAlchemy(app)

###############################################################################





###############################################################################
# DATABASE STUFF
class Participant(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	pID = db.Column(db.String(120))
	age = db.Column(db.String(120))
	gender = db.Column(db.String(120))
	language1 = db.Column(db.String(120))
	language2 = db.Column(db.String(120))
	language3 = db.Column(db.String(120))
	language4 = db.Column(db.String(120))
	yrLanguage1 = db.Column(db.String(120))
	yrLanguage2 = db.Column(db.String(120))
	yrLanguage3 = db.Column(db.String(120))
	yrLanguage4 = db.Column(db.String(120))
	yearsEngCountry = db.Column(db.String(120))
	answers = db.relationship("Answer", order_by="Answer.setNum", \
								backref="Participant")

	def __init__(self,
			pID, age='', gender='', 
			language1='', yrLanguage1='',
			language2='', yrLanguage2='',
			language3='', yrLanguage3='',
			language4='', yrLanguage4='',
			yearsEngCountry=''):
		self.pID = pID
		self.age = age
		self.gender = gender
		self.language1 = language1
		self.yrLanguage1 = yrLanguage1
		self.language2 = language2
		self.yrLanguage2 = yrLanguage2
		self.language3 = language3
		self.yrLanguage3 = yrLanguage3
		self.language4 = language4
		self.yrLanguage4 = yrLanguage4
		self.yearsEngCountry = yearsEngCountry

	def __repr__(self):
		return '<Participant %r>' % self.pID

class Answer(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	pID = db.Column(db.Integer, db.ForeignKey('participant.id'))
	setNum = db.Column(db.Integer)
	ans = db.Column(db.Integer)

	def __init__(self, setNum, ans):
		self.setNum = setNum
		self.ans = ans

	def __repr__(self):
		return '<Answer %r>' % self.setNum

###############################################################################


###############################################################################
# APP CODE
@app.route('/')
def first():
	# if not session.get('logged_in'):
	# 	return redirect(url_for('enter_id'))
	# else:
	# 	# flash('Welcome back, click resume below')
	# 	return redirect(url_for('intro'))

	return redirect(url_for('enter_id'))

@app.route('/intro')
def intro():
	return render_template('intro.html')



@app.route('/enter_id', methods=['GET','POST'])
def enter_id():
	error = None
	# if session['logged_in']:
	# 	return redirect(url_for('collect_ans'))

	if request.method == 'POST':
		pID = request.form['pID']
		participant = Participant.query.filter_by(pID=pID).first()
		if participant is None:
			session['logged_in'] = True
			session['pID'] = pID
			db.session.add(Participant(pID))
			db.session.commit()
			flash('Welcome Participant ' + pID + '.')
			populate_pics()
			return redirect(url_for('intro'))
		else:
			error = participant.pID + \
				' is already taken, contact an administrator.'

	return render_template('enter_id.html', error=error)

def populate_pics():
	session['pictureTups'] = []
	for i in range(1, app.config['NUMPICS']+1):
		session['pictureTups'].append(( str(i) + 'a.jpeg',str(i) + 'b.jpeg', i))
	shuffle(session['pictureTups'])


@app.route('/collect_ans', methods=['GET','POST'])
def collect_ans():
	if request.method == 'POST':
		formAns = int(request.form['btn'])
		setNum = int(session['lastPop'])
		pID=session['pID']
		p = db.session.query(Participant).filter_by(pID=pID).first()
		p.answers.append(Answer(setNum, formAns))
		db.session.commit()

	pictureTups = session['pictureTups']
	if not pictureTups:
		db.session.commit()
		return redirect(url_for('add_participant'))

	pictureTup = pictureTups.pop(0)
	session['lastPop'] = pictureTup[-1]
	imgName1 = 'static/img/' + pictureTup[0]
	imgName2 = 'static/img/' + pictureTup[1]
	session['pictureTups'] = pictureTups

	# if request.method == 'POST':
	return render_template('collect_ans.html', \
		imgName1=imgName1, imgName2=imgName2, pictureTup=str(session['pictureTups']))




@app.route('/add_participant', methods=['GET','POST'])
def add_participant():
	if request.method == 'POST':
		inDict = request.form
		pID=session['pID']
		p = db.session.query(Participant).filter_by(pID=pID).first()
		p.age = inDict['age']
		p.gender = inDict['gender']
		p.language1 = inDict['language1']
		p.yrLanguage1 = inDict['yrLanguage1']
		p.language2 = inDict['language2']
		p.yrLanguage2 = inDict['yrLanguage2']
		p.language3 = inDict['language3']
		p.yrLanguage3 = inDict['yrLanguage3']
		p.language4 = inDict['language4']
		p.yrLanguage4 = inDict['yrLanguage4']
		p.yearsEngCountry =  inDict['yearsEngCountry']
		db.session.commit()

		flash('New participant was successfully posted')
		return redirect(url_for('thanks'))
	else:
		return render_template('add_participants.html')

@app.route('/thanks', methods=['GET','POST'])
def thanks():
	return render_template('thanks.html')


@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
	error = None
	if request.method == 'POST':
		password = request.form['password']
		if password == app.config['PASSWORD']:
			session['admin_logged_in'] = True
			flash('You were logged in')
			return redirect(url_for('show_participants'))
		else:
			error = 'Incorrect Password.'

	return render_template('admin_login.html', error=error)

@app.route('/admin_logout')
def admin_logout():
	session.pop('admin_logged_in', None)
	flash('You were logged out')
	return redirect(url_for('admin_login'))


@app.route('/show', methods=['GET', 'POST'])
def show_participants():
	participants = Participant.query.order_by(Participant.pID).all()
	return render_template('show_participants.html', participants=participants, \
													numPics = app.config['NUMPICS'])

@app.route('/logout')
def logout():
	session.pop('pID', None)
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



