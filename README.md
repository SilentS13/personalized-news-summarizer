# 📰 Personalized News Summarizer

A powerful web application that uses AI to generate customized news article summaries based on your interests and reading preferences.

## 🌟 Project Overview

The Personalized News Summarizer is designed to help you save time and focus on content that matters to you. This application provides smart, AI-powered summaries of news articles, academic papers, and other online content, tailored to your personal preferences.

### What Can You Do?

- 📝 Generate concise summaries from URLs or pasted text
- 🎯 Customize summary length and reading complexity
- 🏷️ Define personal interests for targeted content focus
- 💾 Save and organize your summarized articles
- 🔍 View key topics and themes extracted from content
- 📊 Track your reading history

## ✨ Key Features

- **🔐 User Authentication**: Secure account system with personal reading preferences
- **🌐 Smart Content Extraction**: Automatically identify and extract relevant content from any URL
- **🧠 AI-Powered Summarization**: Utilizes OpenAI GPT-4o for high-quality, contextually aware summaries
- **⚙️ Customization Options**: Adjust summary length and reading level to match your needs
- **🔆 Interest Highlighting**: Automatically highlight content relevant to your specified interests
- **🛡️ Robust Reliability**: Includes fallback mechanisms to ensure summarization works even when AI is unavailable

## 🛠️ Technology Stack

- **Backend**: Python with Flask web framework
- **Database**: SQLAlchemy ORM with PostgreSQL support
- **Content Extraction**: Trafilatura library for clean content parsing
- **AI Summarization**: OpenAI GPT-4o integration
- **Frontend**: Responsive design with Bootstrap 5
- **Authentication**: Secure session-based auth with Werkzeug

## 🚀 Installation

### Prerequisites
- Python 3.9+
- PostgreSQL (recommended) or SQLite
- OpenAI API key

### Step 1: Clone the Repository
```bash
git clone https://github.com/yourusername/personalized-news-summarizer.git
cd personalized-news-summarizer
```

### Step 2: Set Up Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install flask flask-sqlalchemy gunicorn openai psycopg2-binary python-dotenv sqlalchemy trafilatura werkzeug email_validator flask-login flask-wtf
```

### Step 4: Configure Environment Variables
Create a `.env` file in the project root with:
```
DATABASE_URL=postgresql://username:password@localhost/news_summarizer
# Or for SQLite: DATABASE_URL=sqlite:///news_summarizer.db
OPENAI_API_KEY=your_openai_api_key
SESSION_SECRET=your_secret_key
```

### Step 5: Initialize the Database
```bash
# The database tables will be automatically created when the app runs for the first time
python main.py
```

## 💻 Running the Application

Start the development server:
```bash
python main.py
```

Visit `http://localhost:5000` in your web browser to access the application.

## 🌐 Deployment Options

The application is designed for easy deployment on various platforms:

- **Render**: Use the Procfile and set the start command to `gunicorn main:app`
- **PythonAnywhere**: Use `main:app` as the WSGI entry point
- **Railway**: Connect your GitHub repository for automatic deployment
- **Heroku**: Use the provided `Procfile` for easy deployment

Remember to set the required environment variables in your deployment platform's settings.

## 📱 Using the Application

1. **Create an Account**: Register to access personalized features
2. **Set Your Preferences**: Configure your reading level, summary length, and topic interests
3. **Generate Summaries**: Enter a URL or paste text to create a customized summary
4. **Review & Save**: View your summary with highlighted key points and save for later reference
5. **Manage Your Library**: Access your history of summarized content

## 📋 Project Structure

```
personalized-news-summarizer/
├── main.py                # Main application file
├── summarizer.py          # AI summarization engine
├── utils.py               # Utility functions
├── static/                # Static assets
│   ├── css/               # Stylesheets
│   └── js/                # JavaScript files
├── templates/             # HTML templates
├── instance/              # Database instance (when using SQLite)
├── .env                   # Environment variables (create this)
├── .gitignore             # Git ignore file
├── Procfile               # For deployment
└── README.md              # This file
```

## 📄 License

MIT License - See the LICENSE file for details

## 👏 Acknowledgements

- OpenAI for their powerful language models that drive the summarization
- Trafilatura developers for the excellent content extraction library
- Flask and its ecosystem for the robust web framework
- The open source community for various libraries that made this project possible

## 📬 Contact

For questions, feedback, or support, please create an issue in this repository or contact the repository owner.

---

Developed with ❤️ for efficiently consuming digital content
