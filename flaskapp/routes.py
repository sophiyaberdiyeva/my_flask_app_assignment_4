from flask import render_template, flash, redirect, url_for, request
from flaskapp import app, db
from flaskapp.models import BlogPost, IpView, Day, UkData
from flaskapp.forms import PostForm, VariableSelectForm
import datetime

import pandas as pd
import json
import plotly
import plotly.express as px


# Route for the home page, which is where the blog posts will be shown
@app.route("/")
@app.route("/home")
def home():
    # Querying all blog posts from the database
    posts = BlogPost.query.all()
    return render_template('home.html', posts=posts)


# Route for the about page
@app.route("/about")
def about():
    return render_template('about.html', title='About page')


# Route to where users add posts (needs to accept get and post requests)
@app.route("/post/new", methods=['GET', 'POST'])
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = BlogPost(title=form.title.data, content=form.content.data, user_id=1)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New Post', form=form)


# Route to the dashboard page
@app.route('/dashboard')
def dashboard():
    days = Day.query.all()
    df = pd.DataFrame([{'Date': day.id, 'Page views': day.views} for day in days])

    fig = px.bar(df, x='Date', y='Page views')

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('dashboard.html', title='Page views per day', graphJSON=graphJSON)


@app.route('/uk_elections', methods=['GET', 'POST'])
def uk_elections():
    variables = [
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
    ]
    
    form = VariableSelectForm()
    form.variable.choices = variables
    
    variable = form.variable.data or 'GreenVote19'
    
    data = UkData.query.all()
    df = pd.DataFrame([{
        'id': row.id,
        'constituency_name': row.constituency_name,
        'region': row.region,
        variable: getattr(row, variable),
        'Female': row.c11Female,
        'Full-time Students': row.c11FulltimeStudent,
        'Retired': row.c11Retired,
        'House Owned': row.c11HouseOwned
    } for row in data])
    
    with open('flaskapp/static/Westminster_Parliamentary_Constituencies_2019.geojson') as f:
        geojson = json.load(f)
    
    variable_display_name = next((display for code, display in variables if code == variable), variable)
    
    map_fig = px.choropleth_mapbox(
        df,
        geojson=geojson,
        locations='id',
        featureidkey='properties.pcon19cd',
        color=variable,
        hover_name='constituency_name',
        color_continuous_scale='greens',
        mapbox_style='carto-positron',
        zoom=4.8,
        center={"lat": 55.0, "lon": -2.3},
        opacity=0.6,
        labels={variable: variable_display_name}
    )

    map_fig.update_traces(
        hovertemplate=(
            "<b>%{hovertext}</b><br>"
            f"{variable_display_name}: " "%{customdata[4]:.0f}<br>"
            "Female: %{customdata[0]:.2f}%<br>"
            "Full-time Students: %{customdata[1]:.2f}%<br>"
            "Retired: %{customdata[2]:.2f}%<br>"
            "House Owned: %{customdata[3]:.2f}%"
        ),
        hovertext=df['constituency_name'],
        customdata=df[['Female', 'Full-time Students', 'Retired', 'House Owned', variable]].values  # Pass additional data
    )

    map_fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        height=None,
        autosize=True
    )
    map_html = map_fig.to_html(full_html=False)
    
    if variable.endswith("Vote19"):
        agg_df = df.groupby('region')[variable].sum().reset_index()
        title_prefix = 'Total'
    elif variable.startswith("c11") or variable == "Turnout19":
        agg_df = df.groupby('region')[variable].mean().reset_index()
        title_prefix = 'Average'
    else:
        agg_df = df.groupby('region')[variable].mean().reset_index()
        title_prefix = 'Average'
    
    bar_fig = px.bar(
        agg_df,
        x=variable,
        y='region',
        orientation='h',
        title=f"{title_prefix} {variable_display_name} by Region",
        labels={variable: variable_display_name},
        color='region',
        color_discrete_sequence=px.colors.qualitative.Prism,
        hover_data={variable: True, 'region': False}
    )
    bar_fig.update_traces(
        hovertemplate=f"{variable_display_name}: %{{x:.0f}}"
    )
    bar_fig.update_layout(
        margin=dict(l=20, r=20, t=40, b=20),
        height=400,
        showlegend=False,
        yaxis_title=""
    )
    bar_html = bar_fig.to_html(full_html=False, config={"displayModeBar": False})
    
    return render_template('uk_elections.html', form=form, graph_html=map_html, bar_html=bar_html)


@app.before_request
def before_request_func():
    day_id = datetime.date.today()  # get our day_id
    client_ip = request.remote_addr  # get the ip address of where the client request came from

    query = Day.query.filter_by(id=day_id)  # try to get the row associated to the current day
    if query.count() > 0:
        # the current day is already in table, simply increment its views
        current_day = query.first()
        current_day.views += 1
    else:
        # the current day does not exist, it's the first view for the day.
        current_day = Day(id=day_id, views=1)
        db.session.add(current_day)  # insert a new day into the day table

    query = IpView.query.filter_by(ip=client_ip, date_id=day_id)
    if query.count() == 0:  # check if it's the first time a viewer from this ip address is viewing the website
        ip_view = IpView(ip=client_ip, date_id=day_id)
        db.session.add(ip_view)  # insert into the ip_view table

    db.session.commit()  # commit all the changes to the database
