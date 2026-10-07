# JobHub

JobHub is a Django-based job marketplace platform that connects job seekers with employers. Users can create professional profiles, discover and filter job opportunities, submit applications, and manage the application process.

The project was built to demonstrate practical backend development using **Python and Django**, including authentication, database relationships, authorization, validation, CRUD operations, search, filtering, pagination, and application workflow management.

## Features

### Authentication & User Profiles

* User registration and login
* User logout
* User profile creation and management
* Profile editing
* Profile image upload
* GitHub and LinkedIn profile links
* Skills, bio, location, and contact information
* Protected profile ownership and editing

### Job Management

* Create job postings
* Edit own job postings
* Delete own job postings
* View detailed job information
* Application deadlines
* Salary information
* Job type and location
* Job search
* Job filtering
* Pagination
* Employer ownership protection

### Job Applications

* Apply for jobs with a cover letter
* View submitted applications
* Prevent users from applying to their own jobs
* Prevent applications after the application deadline
* Prevent duplicate applications
* Employers can view applications for their own jobs
* Employers can update application statuses

Application statuses include:

* Pending
* Reviewed
* Accepted
* Rejected

### Security & Validation

* Authentication for protected features
* User ownership authorization
* CSRF protection
* Required-field validation
* Protected job editing and deletion
* Protected application management
* Duplicate application prevention
* Application deadline validation
* Environment-based secret key management
* Custom 403, 404, and 500 error pages

## Technologies

* **Python**
* **Django 6.1.1**
* **SQLite**
* **HTML5**
* **CSS3**
* **Bootstrap 5**
* **Bootstrap Icons**
* **Git**
* **GitHub**

## Project Structure

```text
JobHub/
├── accounts/
│   ├── migrations/
│   ├── templates/
│   │   ├── accounts/
│   │   └── base.html
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── manage.py
├── requirements.txt
├── .gitignore
└── README.md
```

> User-uploaded profile images and environment files are excluded from Git using `.gitignore`.

## Local Setup

### 1. Clone the Repository

```bash
git clone https://github.com/progdatatofa/JobHub.git
cd JobHub
```

### 2. Create a Virtual Environment

```bash
python -m venv env
```

Activate it on Windows:

```powershell
env\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key
```

Never commit the `.env` file to GitHub.

### 5. Apply Database Migrations

```bash
python manage.py migrate
```

### 6. Create an Administrator Account

```bash
python manage.py createsuperuser
```

### 7. Start the Development Server

```bash
python manage.py runserver
```

Open the application at:

```text
http://127.0.0.1:8000/
```

## Security

JobHub uses Django's built-in security features together with application-level authorization checks.

Examples include:

* Authentication for protected actions
* Ownership verification before editing or deleting jobs
* Ownership verification before viewing job applications
* Ownership verification before updating application statuses
* CSRF protection on forms
* Duplicate application prevention
* Application deadline validation
* Environment-based secret key management
* Protected user profile management

These controls ensure that users can only perform actions they are authorized to perform.

## Future Improvements

Planned or potential improvements include:

* Email notifications
* Employer dashboard
* Saved jobs
* CV/resume upload
* Advanced job filtering
* Employer messaging
* Application analytics
* Notification system
* Production database integration
* Automated testing

## Author

**Yahaya Mustapha Ismail**

BSc Computer Science
Bayero University Kano

Backend Developer focused on **Python, Django, and web application development**.

GitHub: https://github.com/progdatatofa

## License

This project is currently maintained as a portfolio and learning project.
