from flask import Flask, render_template, request, redirect, url_for
from flask.ext.bootstrap import Bootstrap
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager, UserMixin, login_user, logout_user, login_required
from wtforms import StringField, SubmitField
from wtforms.validators import Length, Required
from flask.ext.wtf import Form
import datetime

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///db-test.sqlite'
app.config['SECRET_KEY']='very top secret'
db=SQLAlchemy(app)
bootstrap=Bootstrap(app)
db.create_all()
date=datetime.datetime.now()

class NameForm(Form):
    name = StringField('Whats your name?', validators=[Length(1,16), Required()]) 
    submit = SubmitField('submit')

class User(db.Model):
    __tablename__='user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15),index=True,unique=True)
    
    @staticmethod
    def register_user(name):
        u=User(username=name)
        db.session.add(u)
        db.session.commit()
        return u

    def __repr__(self):
        return self.username
    
@app.route('/', methods=['GET', 'POST'])
def index():
    users=User.query.all()
    form = NameForm()
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
        return redirect(url_for('user', user=name))
    return render_template('index.html', users=users, form=form, date=date)

@app.route('/user/<user>')
def user(user):
    date=datetime.datetime.now()
    return render_template('user.html', user=user, date=date)

if __name__ == '__main__':
    app.run(debug=True)
