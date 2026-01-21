from flask import Blueprint, render_template, request, redirect, url_for
from app.models import db, Job

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    # Get all jobs from database
    jobs = Job.query.order_by(Job.applied_date.desc()).all()

    total_jobs = len(jobs)
    applied = len([j for j in jobs if j.status == 'applied'])
    interviews = len([j for j in jobs if j.status == 'interview'])
    offers = len([j for j in jobs if j.status == 'offer'])
    rejected = len([j for j in jobs if j.status == 'rejected'])

    return render_template('index.html',
                           jobs=jobs,
                           total=total_jobs,
                           applied=applied,
                           interviews=interviews,
                           offers=offers,
                           rejected=rejected)

@bp.route('/add', methods=['GET', 'POST'])
def add_job():
    if request.method == 'POST':
        # Get data from the form
        job = Job(
            company = request.form['company'],
            position = request.form['position'],
            location = request.form.get('location', ''),
            salary = request.form.get('salary', ''),
            url = request.form.get('url', ''),
            description = request.form.get('description', ''),
            status = 'applied'
        )


        # Save to database
        db.session.add(job)
        db.session.commit()

        #Redirect back to dashboard
        return redirect(url_for('main.index'))
    
    # if GET request, show the form
    return render_template('add_job.html')