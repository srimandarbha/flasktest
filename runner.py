from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, request, redirect, url_for, flash, get_flashed_messages
from flask.ext.bootstrap import Bootstrap
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager, UserMixin, login_user, logout_user, login_required
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import Length, Required
from flask.ext.wtf import Form
import datetime
import pymysql

app=Flask(__name__)
Bootstrap(app)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///db-test.sqlite'
app.config['SECRET_KEY']='very top secret'
db=SQLAlchemy(app)
db.create_all()
date=datetime.datetime.now()
login_manager  =  LoginManager(app)
login_manager.login_view = '/'

class NameForm(Form):
    name = StringField('Whats your name?', validators=[Length(1,16), Required()]) 
    password = PasswordField('password', validators=[Required()])
    submit = SubmitField('submit')

class User(UserMixin,db.Model):
    __tablename__='user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15),index=True,unique=True)
    password = db.Column(db.String(15))
    
    def set_password(self, password):
        self.password = generate_password_hash(password)

    def verify_password(self,password):
        return check_password_hash(self.password, password)

    @staticmethod
    def register_user(name,password):
        db.create_all()
        u=User(username=name)
        u.set_password(password)
        db.session.add(u)
        db.session.commit()
        return u

    def __repr__(self):
        return self.username
    
@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route('/', methods=['GET', 'POST'])
def index():
    users=User.query.all()
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if not user is None:
            login_user(user)
            form.name.data = ''
            if user.verify_password(form.password.data): 
                flash('Successfully logged as {}'.format(user))
                return redirect(request.args.get('next') or url_for('user', user=user))
            else:
                flash('Wrong credentials provided')
        else:
            flash('Please provide credentials again')
    return render_template('index.html', users=users, form=form, date=date)

@app.route('/user/<user>')
@login_required
def user(user):
    date=datetime.datetime.now()
    conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='root123', db='inventory')
    cur = conn.cursor()
    cur.execute("SELECT * from inventory")
    cur.close()
    conn.close()
    return render_template('user.html', user=user, date=date, cur=cur)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Successully logged out')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True,port=8000)
