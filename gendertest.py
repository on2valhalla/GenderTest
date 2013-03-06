# all the imports
from __future__ import with_statement
import sqlite3
from contextlib import closing
from flask import Flask, request, session, g, redirect, url_for, \
	abort, render_template, flash

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
###############################################################################


###############################################################################
# APP CODE


if __name__ == '__main__':
	app.run()