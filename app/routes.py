from flask import Blueprint, render_template, request, redirect, url_for
from app.models import db, Job, Skill
from app.ai_service import extract_skills

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
        description = request.form.get('description', '')
        
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


        # Extract skills using AI if description provided
        if description:
            print(f"Extracting skills from description...")  # Debug
            skill_names = extract_skills(description)
            print(f"Extracted skills: {skill_names}")  # Debug
            
            # For each skill, create or update it in database
            for skill_name in skill_names:
                # Check if skill already exists
                skill = Skill.query.filter_by(name=skill_name).first()
                
                if not skill:
                    # Create new skill
                    skill = Skill(name=skill_name, count=1)
                    db.session.add(skill)
                else:
                    # Skill exists, increment count
                    skill.count += 1
                
                # Link skill to this job
                job.skills.append(skill)

        # Save to database
        db.session.add(job)
        db.session.commit()

        #Redirect back to dashboard
        return redirect(url_for('main.index'))
    
    # if GET request, show the form
    return render_template('add_job.html')