# JobHub

JobHub is a Django-based job platform that connects job seekers with employers. Users can create professional profiles, post jobs, search and filter available jobs, submit applications, and manage application statuses.

## Features

### Authentication & Profiles

* User registration and login
* User logout
* User profiles
* Profile editing
* Profile image upload
* GitHub and LinkedIn profile links
* Skills, bio, location, and contact information

### Job Management

* Create job postings
* Edit own job postings
* Delete own job postings
* View job details
* Application deadlines
* Salary information
* Job type and location
* Job search and filtering
* Pagination

### Job Applications

* Apply for jobs with a cover letter
* View submitted applications
* Prevent users from applying to their own jobs
* Prevent applications after the deadline
* Prevent duplicate applications
* Employers can view applications for their own jobs
* Employers can update application status
* Application statuses:

  * Pending
  * Reviewed
  * Accepted
  * Rejected

### Security & Validation

* Login-required access for protected features
* User ownership checks
* CSRF protection
* Form validation
* Protected job editing and deletion
* Protected application management
* Custom 403, 404, and 500 error pages
* Secret key stored using environment variables

## Technologies

* Python
* Django
* SQLite
* HTML5
* CSS3
* Bootstrap 5
* Bootstrap Icons
* Git & GitHub

## Project Structure

```text
JobHub/
├── accounts/
│   ├── migrations/
│   ├── templates/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── admin.py
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── profile/
├── manage.py
├── requirements.txt
├── .gitignore
├── README.md
└── .env
```

> `.env` contains sensitive environment variables and is excluded from Git using `.gitignore`.

## Local Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd JobHub
```

### 2. Create a virtual environment

```bash
python -m venv env
```

Activate it on Windows:

```bash
env\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key
```

Never commit the `.env` file to GitHub.

### 5. Apply migrations

```bash
python manage.py migrate
```

### 6. Create an admin account

```bash
python manage.py createsuperuser
```

### 7. Start the development server

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
* Deadline validation
* Environment-based secret management

## Future Improvements

Possible future features include:

* Email notifications
* Employer dashboard
* Saved jobs
* CV upload
* Advanced job filtering
* Employer messaging
* Application analytics
* Notification system

## Author

**Yahaya Mustapha Ismail**

BSc Computer Science
Bayero University Kano

Interested in backend development with Python and Django.

## License

This project is currently intended as a portfolio and learning project.
