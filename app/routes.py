from flask import Blueprint, render_template, request, redirect, url_for, session
from flask_login import login_user, logout_user, login_required, current_user
from app.models import db, Job, Skill, User
from app.ai_service import extract_skills
from flask import current_app

bp = Blueprint('routes', __name__)

# ============== AUTHENTICATION ROUTES ==============

@bp.route('/login')
def login():
    """Show login page or redirect to Google OAuth"""
    if current_user.is_authenticated:
        return redirect(url_for('routes.index'))
    
    from app import oauth
    redirect_uri = url_for('routes.authorize', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@bp.route('/login/callback')
def authorize():
    """Handle the callback from Google after user authorizes"""
    try:
        from app import oauth
        token = oauth.google.authorize_access_token()
        user_info = token.get('userinfo')
        
        if user_info:
            # Check if user already exists in database
            user = User.query.filter_by(google_id=user_info['sub']).first()
            
            if not user:
                # Create new user
                user = User(
                    google_id=user_info['sub'],
                    email=user_info['email'],
                    name=user_info.get('name'),
                    picture=user_info.get('picture')
                )
                db.session.add(user)
                db.session.commit()
            
            # Log the user in
            login_user(user)
            return redirect(url_for('routes.index'))
        
    except Exception as e:
        print(f"Login error: {e}")
        return redirect(url_for('routes.login_page'))
    
    return redirect(url_for('routes.login_page'))

@bp.route('/login-page')
def login_page():
    """Show the actual login page with Google button"""
    if current_user.is_authenticated:
        return redirect(url_for('routes.index'))
    return render_template('login.html')

@bp.route('/logout')
@login_required
def logout():
    """Log out the current user"""
    logout_user()
    return redirect(url_for('routes.login_page'))

# ============== APPLICATION ROUTES ==============

@bp.route('/')
@login_required  # User must be logged in to access
def index():
    # Get only jobs belonging to the current user
    jobs = Job.query.filter_by(user_id=current_user.id).order_by(Job.applied_date.desc()).all()

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
@login_required  # User must be logged in to add jobs
def add_job():
    if request.method == 'POST':
        description = request.form.get('description', '')
        
        # Create job and assign it to current user
        job = Job(
            company=request.form['company'],
            position=request.form['position'],
            location=request.form.get('location', ''),
            salary=request.form.get('salary', ''),
            url=request.form.get('url', ''),
            description=request.form.get('description', ''),
            status='applied',
            user_id=current_user.id
        )

        # Extract skills using AI if description provided
        if description:
            print(f"Extracting skills from description...")
            skill_names = extract_skills(description)
            print(f"Extracted skills: {skill_names}")
            
            for skill_name in skill_names:
                skill = Skill.query.filter_by(name=skill_name).first()
                
                if not skill:
                    skill = Skill(name=skill_name, count=1)
                    db.session.add(skill)
                else:
                    skill.count += 1
                
                job.skills.append(skill)

        db.session.add(job)
        db.session.commit()

        return redirect(url_for('routes.index'))
    
    return render_template('add_job.html')

@bp.route('/skills')
@login_required  # User must be logged in
def skills_dashboard():
    # Get only jobs for current user
    user_jobs = Job.query.filter_by(user_id=current_user.id).all()
    total_jobs = len(user_jobs)
    
    # Count skills only from this user's jobs
    skill_counts = {}
    for job in user_jobs:
        for skill in job.skills:
            if skill.name in skill_counts:
                skill_counts[skill.name] += 1
            else:
                skill_counts[skill.name] = 1
    
    # Create skills data sorted by count
    skills_data = []
    for skill_name, count in sorted(skill_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total_jobs * 100) if total_jobs > 0 else 0
        skills_data.append({
            'name': skill_name,
            'count': count,
            'percentage': round(percentage, 1)
        })

    return render_template('skills.html',
                          skills=skills_data,
                          total_jobs=total_jobs)

@bp.route('/update_status/<int:job_id>', methods=['POST'])
@login_required  # User must be logged in
def update_status(job_id):
    # Get job and verify it belongs to current user
    job = Job.query.filter_by(id=job_id, user_id=current_user.id).first_or_404()
    
    new_status = request.form.get('status')
    
    if new_status in ['applied', 'interview', 'offer', 'rejected']:
        job.status = new_status
        db.session.commit()
        print(f"Updated {job.company} - {job.position} to {new_status}")
    
    return redirect(url_for('routes.index'))