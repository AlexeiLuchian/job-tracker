from flask import Blueprint, render_template
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