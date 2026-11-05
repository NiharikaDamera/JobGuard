# JobGuard — Fake Job & Internship Detector

**JobGuard** is a full-stack web application designed to help job seekers identify potentially fraudulent job and internship opportunities.

It analyzes job descriptions using a rule-based risk detection engine and Natural Language Processing (NLP) to highlight suspicious patterns and provide a risk score.

The goal is to help job seekers make safer and more informed career decisions.

## Features

- **User Authentication:** Secure registration and login.
- **Job Risk Analysis:** Analyzes job descriptions and calculates a risk score out of 100.
- **Risk Classification:** Categorizes job postings as Low, Medium, High, or Critical Risk.
- **NLP Insights:** Extracts possible organizations, important nouns, and action words.
- **Company Verification Checks:** Identifies basic company information and suspicious recruitment practices.
- **Analysis History:** Saves previous analyses and allows users to view results.
- **Responsive Design:** User-friendly interface for desktop and mobile devices.

- ## Tech Stack

### Frontend
- HTML5
- CSS3
- JavaScript

### Backend
- Python
- Django
- Django REST Framework

### Database
- MySQL

### NLP
- spaCy

### Tools
- Git
- GitHub
- MySQL Workbench
- Visual Studio Code

- ## How It Works

1. Create an account or log in to JobGuard.
2. Open the Job Analysis page.
3. Enter the job title, company name, and job description.
4. Submit the job details for analysis.
5. The rule-based risk engine checks for suspicious patterns.
6. NLP extracts relevant words, actions, and possible organization names.
7. JobGuard displays a risk score, risk level, and analysis insights.
8. The analysis is saved in the user's dashboard history.

## Important Disclaimer

JobGuard is an awareness tool designed to identify potentially suspicious job postings. 
Its risk scores and company checks are indicators, not guarantees.
Users should independently verify employers and recruitment opportunities before sharing personal information or making payments.

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/NiharikaDamera/JobGuard.git
cd JobGuard
```

### 2. Set Up the Backend

```bash
cd Backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy `.env.example` and rename the copy to `.env`.

Update the database credentials and secret key in `.env`.

### 4. Set Up the MySQL Database

Create a MySQL database named:

```sql
CREATE DATABASE jobguard_db;
```

### 5. Apply Migrations

```bash
python manage.py migrate
```

### 6. Start the Django Development Server

```bash
python manage.py runserver
```

The backend will be available at:

`http://127.0.0.1:8000/`

### 7. Run the Frontend

Open `Frontend/index.html` in your web browser.
