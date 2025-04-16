from flask import Flask, render_template, session, request, redirect, flash, url_for
import os
import logging
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.sql import func

# Create the base class
class Base(DeclarativeBase):
    pass

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///news_summarizer.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Create DB connection
db = SQLAlchemy(model_class=Base)
db.init_app(app)

# Define models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    reading_level = db.Column(db.String(20), default="medium")
    summary_length = db.Column(db.String(20), default="medium")
    interests = db.Column(db.Text, default="general")
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_interests_list(self):
        return [interest.strip() for interest in self.interests.split(',')]

class Summary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    original_text = db.Column(db.Text, nullable=False)
    summarized_text = db.Column(db.Text, nullable=False)
    source_url = db.Column(db.String(500))
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    summary_length = db.Column(db.String(20), default="medium")
    reading_level = db.Column(db.String(20), default="medium")
    key_topics = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Create tables
with app.app_context():
    db.create_all()

# Utility Functions
def is_valid_email(email):
    """Check if the email is valid."""
    return '@' in email and '.' in email.split('@')[1]

def is_valid_url(url):
    """Check if the input is a valid URL."""
    return url.startswith('http://') or url.startswith('https://')

def generate_summary(text, length="medium", reading_level="medium", interests=None):
    """Generate summary using the advanced summarizer module."""
    # Import here to avoid circular imports
    from summarizer import generate_summary as generate_summary_ai
    
    # Use the AI-powered summarizer from summarizer.py
    result = generate_summary_ai(text, length, reading_level, interests)
    
    return result

def extract_article_from_url(url):
    """Extract article content from a URL using trafilatura."""
    try:
        # Using trafilatura to extract content from URL
        import trafilatura
        downloaded = trafilatura.fetch_url(url)
        
        if not downloaded:
            return None, "Failed to download content from URL"
        
        # Extract main text content
        text = trafilatura.extract(downloaded)
        
        if not text:
            return None, "No content extracted from URL"
        
        # Get a title from the URL (remove protocol and domain)
        import re
        title = url
        # Remove protocol
        title = re.sub(r'^https?://', '', title)
        # Remove domain
        title = re.sub(r'^[^/]+/', '', title)
        # Replace dashes with spaces and capitalize
        title = ' '.join(word.capitalize() for word in title.replace('-', ' ').split())
        
        return {
            'title': title[:100],  # Limit title length
            'text': text,
            'url': url
        }, None
    except Exception as e:
        return None, f"Error processing URL: {str(e)}"

def get_reading_level_options():
    """Return reading level options for the UI."""
    return [
        {'value': 'basic', 'label': 'Basic - Simplified language'},
        {'value': 'medium', 'label': 'Medium - Balanced complexity'},
        {'value': 'advanced', 'label': 'Advanced - Technical terminology'}
    ]

def get_summary_length_options():
    """Return summary length options for the UI."""
    return [
        {'value': 'brief', 'label': 'Brief - Quick overview'},
        {'value': 'medium', 'label': 'Medium - Balanced detail'},
        {'value': 'detailed', 'label': 'Detailed - Comprehensive summary'}
    ]

def get_interest_categories():
    """Return common interest categories for the UI."""
    return [
        'Technology', 'Science', 'Politics', 'Business',
        'Health', 'Sports', 'Entertainment', 'Environment',
        'Education', 'Art', 'Travel', 'Food', 'Fashion'
    ]

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Username and password are required', 'danger')
            return redirect(url_for('login'))
        
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.check_password(password):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))
        
        session['user_id'] = user.id
        flash('Login successful!', 'success')
        return redirect(url_for('index'))
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not username or not email or not password:
            flash('All fields are required', 'danger')
            return redirect(url_for('register'))
        
        if not is_valid_email(email):
            flash('Invalid email address', 'danger')
            return redirect(url_for('register'))
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('register'))
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('register'))
        
        user = User(username=username, email=email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    # Check if user is logged in
    user_id = session.get('user_id')
    if not user_id:
        flash('Please log in to view your profile', 'warning')
        return redirect(url_for('login'))
    
    user = User.query.get(user_id)
    if not user:
        flash('User not found', 'danger')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        # Update user preferences
        reading_level = request.form.get('reading_level', 'medium')
        summary_length = request.form.get('summary_length', 'medium')
        interests = request.form.getlist('interests')
        
        # Validate input
        if reading_level not in ['basic', 'medium', 'advanced']:
            reading_level = 'medium'
            
        if summary_length not in ['brief', 'medium', 'detailed']:
            summary_length = 'medium'
        
        # Update user preferences
        user.reading_level = reading_level
        user.summary_length = summary_length
        user.interests = ','.join(interests) if interests else 'general'
        
        # Save changes
        db.session.commit()
        
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))
    
    # Get user's summaries
    summaries = Summary.query.filter_by(user_id=user.id).order_by(Summary.date_created.desc()).limit(5).all()
    
    return render_template(
        'profile.html',
        user=user,
        summaries=summaries,
        reading_level_options=get_reading_level_options(),
        summary_length_options=get_summary_length_options(),
        interest_categories=get_interest_categories(),
        selected_interests=user.get_interests_list()
    )

@app.route('/summarize', methods=['GET', 'POST'])
def summarize():
    """Summarize content route."""
    # Check if user is logged in
    user_id = session.get('user_id')
    if not user_id:
        flash('Please log in to use the summarization feature', 'warning')
        return redirect(url_for('login'))
    
    user = User.query.get(user_id)
    if not user:
        flash('User not found', 'danger')
        return redirect(url_for('index'))
    
    summary = None
    
    if request.method == 'POST':
        content_type = request.form.get('content_type')
        reading_level = request.form.get('reading_level', user.reading_level)
        summary_length = request.form.get('summary_length', user.summary_length)
        
        if content_type == 'url':
            url = request.form.get('url_input')
            if not url:
                flash('URL is required', 'danger')
                return redirect(url_for('summarize'))
            
            if not is_valid_url(url):
                flash('Invalid URL format', 'danger')
                return redirect(url_for('summarize'))
            
            article, error = extract_article_from_url(url)
            if error:
                flash(f'Error extracting article: {error}', 'danger')
                return redirect(url_for('summarize'))
            
            title = article['title']
            original_text = article['text']
            source_url = article['url']
            
        else:  # text input
            text_input = request.form.get('text_input')
            if not text_input:
                flash('Text content is required', 'danger')
                return redirect(url_for('summarize'))
            
            title = request.form.get('title', 'Custom Text')
            original_text = text_input
            source_url = None
        
        # Generate summary
        summary_result = generate_summary(
            original_text, 
            length=summary_length,
            reading_level=reading_level,
            interests=user.get_interests_list()
        )
        
        # Create summary object
        summary = Summary(
            title=title,
            original_text=original_text,
            summarized_text=summary_result['summary'],
            source_url=source_url,
            summary_length=summary_length,
            reading_level=reading_level,
            key_topics=','.join(summary_result['key_topics']),
            user_id=user.id
        )
        
        # Save summary to database
        db.session.add(summary)
        db.session.commit()
        
        flash('Summary generated successfully!', 'success')
    
    return render_template(
        'summary.html',
        reading_level_options=get_reading_level_options(),
        summary_length_options=get_summary_length_options(),
        current_summary_length=user.summary_length,
        current_reading_level=user.reading_level,
        summary=summary
    )

@app.route('/summary/<int:summary_id>')
def view_summary(summary_id):
    """View a specific summary."""
    # Check if user is logged in
    user_id = session.get('user_id')
    if not user_id:
        flash('Please log in to view summaries', 'warning')
        return redirect(url_for('login'))
    
    # Get the summary
    summary = Summary.query.get_or_404(summary_id)
    
    # Check if the summary belongs to the current user
    if summary.user_id != user_id:
        flash('You do not have permission to view this summary', 'danger')
        return redirect(url_for('profile'))
    
    return render_template('view_summary.html', summary=summary)

# Make current user available to templates
@app.context_processor
def inject_user():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if user:
            return dict(current_user={'is_authenticated': True, 'username': user.username, 'id': user.id})
    return dict(current_user={'is_authenticated': False, 'username': 'Guest', 'id': None})

@app.errorhandler(404)
def page_not_found(e):
    return render_template('index.html', error="Page not found"), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('index.html', error="Internal server error"), 500

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    app.run(host="0.0.0.0", port=5000, debug=True)