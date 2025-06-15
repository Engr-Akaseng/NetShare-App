from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField, DecimalField
from wtforms.validators import DataRequired, Length, NumberRange

class UserManagementForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=30)])
    email = StringField('Email', validators=[DataRequired()])
    role = SelectField('Role', choices=[('user', 'User'), ('host', 'Host'), ('admin', 'Admin')], validators=[DataRequired()])
    submit = SubmitField('Update User')

class PricingForm(FlaskForm):
    plan_name = StringField('Plan Name', validators=[DataRequired()])
    price = DecimalField('Price (USD)', validators=[DataRequired(), NumberRange(min=0)])
    speed = StringField('Speed (Mbps)', validators=[DataRequired()])
    submit = SubmitField('Add/Update Pricing')

class PopupMessageForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    message = TextAreaField('Message', validators=[DataRequired(), Length(max=500)])
    submit = SubmitField('Post Message')
