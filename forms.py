from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField
from wtforms.fields import DateField, DateTimeLocalField
from wtforms.validators import DataRequired

class TaskForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    due_date = DateField('Due Date')
    reminder = DateTimeLocalField('Reminder', format='%Y-%m-%dT%H:%M')
    notes = TextAreaField('Notes')
    important = BooleanField('Important')