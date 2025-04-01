from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf.csrf import CSRFProtect
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, ValidationError, EqualTo
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os


app = Flask(__name__) 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
csrf = CSRFProtect(app)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    tasks = db.relationship('Task', backref='user', lazy=True)
    lists = db.relationship('TaskList', backref='user', lazy=True)

class TaskList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    tasks = db.relationship('Task', backref='task_list', lazy=True)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    important = db.Column(db.Boolean, default=False)
    due_date = db.Column(db.DateTime)
    reminder = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    list_id = db.Column(db.Integer, db.ForeignKey('task_list.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', 
                                   validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
@login_required
def index():
    default_list = TaskList.query.filter_by(user_id=current_user.id).first()
    if default_list:
        return redirect(url_for('view_list', list_id=default_list.id))
    return render_template('index.html')

@app.route('/list/<int:list_id>')
@login_required
def view_list(list_id):
    task_list = TaskList.query.get_or_404(list_id)
    if task_list.user_id != current_user.id:
        return redirect(url_for('index'))
    
    tasks = Task.query.filter_by(list_id=list_id, user_id=current_user.id).order_by(Task.important.desc(), Task.due_date).all()
    lists = TaskList.query.filter_by(user_id=current_user.id).all()
    
    
    from forms import TaskForm 
    form = TaskForm()
    
    return render_template('index.html', 
                         tasks=tasks, 
                         current_list=task_list, 
                         lists=lists,
                         form=form)  

@app.route('/add_task', methods=['POST'])
@login_required
def add_task():
    list_id = request.form.get('list_id')
    title = request.form.get('title')
    due_date = request.form.get('due_date')
    reminder = request.form.get('reminder')
    notes = request.form.get('notes')
    important = request.form.get('important') == 'on'
    
    if not title:
        flash('Task title is required', 'error')
        return redirect(request.referrer)
    
    try:
        due_date = datetime.strptime(due_date, '%Y-%m-%d') if due_date else None
        reminder = datetime.strptime(reminder, '%Y-%m-%dT%H:%M') if reminder else None
    except ValueError:
        flash('Invalid date format', 'error')
        return redirect(request.referrer)
    
    new_task = Task(
        title=title,
        list_id=list_id,
        user_id=current_user.id,
        due_date=due_date,
        reminder=reminder,
        notes=notes,
        important=important
    )
    
    db.session.add(new_task)
    db.session.commit()
    flash('Task added successfully', 'success')
    return redirect(request.referrer)

@app.route('/toggle_task/<int:task_id>', methods=['POST'])
@login_required
def toggle_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        return jsonify({'success': False})
    
    task.completed = not task.completed
    db.session.commit()
    
    return jsonify({'success': True, 'completed': task.completed})

@app.route('/toggle_important/<int:task_id>', methods=['POST'])
@login_required
def toggle_important(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        return jsonify({'success': False})
    
    task.important = not task.important
    db.session.commit()
    
    return jsonify({'success': True, 'important': task.important})

@app.route('/add_list', methods=['POST'])
@login_required
def add_list():
    name = request.form.get('name')
    
    if not name:
        flash('List name is required', 'error')
        return redirect(request.referrer)
    
    new_list = TaskList(
        name=name,
        user_id=current_user.id
    )
    
    db.session.add(new_list)
    db.session.commit()
    flash('List created successfully', 'success')
    return redirect(url_for('view_list', list_id=new_list.id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Login unsuccessful. Please check username and password', 'danger')
    return render_template('auth/login.html', form=form)  

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(username=form.username.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        
        default_list = TaskList(name="My Tasks", user_id=user.id)
        db.session.add(default_list)
        db.session.commit()
        
        flash('Your account has been created! You can now log in', 'success')
        return redirect(url_for('login'))
    return render_template('auth/register.html', form=form)  

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)