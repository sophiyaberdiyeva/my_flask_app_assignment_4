from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')  # submit button to submit to our route


class VariableSelectForm(FlaskForm):
    variable = SelectField('Select Variable', choices=[
        ('GreenVote19', 'Green Vote 2019'),
        ('Turnout19', 'Turnout 2019'),
        ('ConVote19', 'Conservative Vote 2019'),
        ('LabVote19', 'Labour Vote 2019'),
        ('LDVote19', 'Lib Dem Vote 2019'),
        ('SNPVote19', 'SNP Vote 2019'),
        ('PCVote19', 'PC Vote 2019'),
        ('UKIPVote19', 'UKIP Vote 2019'),
        ('BrexitVote19', 'Brexit Vote 2019'),
        ('TotalVote19', 'Total Vote 2019'),
        ('c11PopulationDensity', 'Population Density (2011)'),
        ('c11Female', 'Female % (2011)'),
        ('c11FulltimeStudent', 'Full-time Students % (2011)'),
        ('c11Retired', 'Retired % (2011)'),
        ('c11HouseOwned', 'House Owned % (2011)'),
        ('c11HouseholdMarried', 'Married Household % (2011)')
    ])
    submit = SubmitField('Update')

