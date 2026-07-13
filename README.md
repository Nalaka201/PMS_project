# CCMS - Citizen Complaint Management System

A modern web-based complaint management system designed for Sri Lankan local government authorities (Grama Niladhari divisions and Pradeshiya Sabhas). Citizens can submit and track public service complaints (road damage, waste management, drainage, street lighting, etc.) with real-time status updates and officer remarks.

## Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Running the Application](#running-the-application)
- [Features](#features)
- [Project Structure](#project-structure)
- [Key Models & Workflow](#key-models--workflow)
- [Contributing](#contributing)
- [License](#license)

## Overview

This system bridges citizens and government by enabling:
- **Public Interface**: Citizens submit complaints and track progress using reference numbers (e.g., `CCMS-2026-XXXXX`)
- **Officer Dashboard**: Local government officers review, update, and resolve complaints within their jurisdiction
- **Admin Panel**: Administrators manage officers, locations (districts, Pradeshiya Sabhas, Wasamas), and view system-wide analytics
- **Hierarchical Permissions**: Officers are assigned to administrative boundaries (district/sabha/wasama level) and only see complaints in their jurisdiction

## Tech Stack

- **Backend**: Django 5.0+ (Python)
- **Frontend**: HTML5, CSS3, Bootstrap 5
- **Database**: SQLite (development) / PostgreSQL (production-ready)
- **JavaScript**: AJAX for cascading location dropdowns
- **Charts**: Chart.js for admin analytics

## Getting Started

### Prerequisites

Ensure you have installed:
- **Python** 3.10+
- **pip** (Python package manager)
- **Git**

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Nalaka201/PMS_project.git
   cd PMS_project
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create a superuser** (admin account)
   ```bash
   python manage.py createsuperuser
   ```
   Follow the prompts to set username, email, and password.

### Running the Application

**Development Server**
```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`

- **Public homepage**: `http://localhost:8000/`
- **Complaint submission**: `http://localhost:8000/lodge/`
- **Admin panel**: `http://localhost:8000/admin/` (use superuser credentials)

## Features

### Public Interface
- **Home Page** (`index.html`): Quick search for complaint tracking
- **Lodge Complaint** (`lodge_complaint.html`): 
  - Multi-step form with cascading dropdowns (District → Pradeshiya Sabha → Wasama)
  - Category selection (Road Damage, Waste Management, Drainage, Street Lighting, Environmental, Public Services, Other)
  - File upload for evidence
  - Auto-generated unique reference number (e.g., `CCMS-2026-XXXXX`)
  - Multilingual labels (English + Sinhala)

- **Track Complaint** (`track.html`):
  - Search by reference number
  - View current status, officer remarks, and status history
  - Real-time progress tracking

### Officer Dashboard
- View complaints in their assigned jurisdiction (Wasama/Sabha/District/Global)
- Filter by category, status, or search by reference number/title/citizen name
- Update complaint status (Pending → In Progress → Resolved/Rejected)
- Add remarks with automated status history tracking
- Permission-based access: officers cannot update complaints outside their jurisdiction

### Admin Dashboard
- **Overview**: Total complaints, pending, in progress, resolved counts
- **Analytics**: Charts showing complaint distribution by category and district
- **Officer Management**: Create new officers and assign administrative boundaries
- **Location Management**: Manage Districts, Pradeshiya Sabhas, and Wasama divisions
- **System-wide View**: Access all complaints and generate insights

## Project Structure

```
PMS_project/
├── complaints/                 # Main app
│   ├── models.py              # Data models (District, PradeshiyaSabha, Wasama, OfficerProfile, Complaint, ComplaintRemark)
│   ├── views.py               # Request handlers (public, officer, admin views)
│   ├── forms.py               # Django forms for complaint submission and remarks
│   ├── urls.py                # URL routing
│   ├── admin.py               # Django admin configuration
│   ├── apps.py                # App configuration
│   └── templates/             # HTML templates
│       ├── base.html          # Base template with navbar, footer, styling
│       ├── index.html         # Public homepage with complaint tracking search
│       ├── lodge_complaint.html # Complaint submission form
│       ├── lodge_success.html # Success confirmation page
│       ├── track.html         # Complaint tracking page
│       ├── dashboard_officer.html  # Officer dashboard with complaint list and filters
│       ├── dashboard_admin.html    # Admin dashboard with analytics and management
│       └── ...
├── complaints_project/         # Project settings
│   ├── settings.py            # Django configuration
│   ├── urls.py                # Project URL routing
│   ├── wsgi.py                # WSGI application
│   └── asgi.py                # ASGI application
├── manage.py                  # Django management script
├── requirements.txt           # Python dependencies
├── db.sqlite3                 # SQLite database (auto-created)
└── media/                     # User-uploaded complaint evidence files

```

## Key Models & Workflow

### Data Models

**District**: Administrative district (e.g., Colombo, Kandy)

**PradeshiyaSabha**: Local government authority within a district

**Wasama** (Grama Niladhari Division): Smallest administrative unit; contains divisions like "GN 600"

**OfficerProfile**: Extends Django User; tracks role (OFFICER/ADMIN) and assigned jurisdiction

**Complaint**: Core model
- Auto-generated reference number (CCMS-YYYY-XXXXX)
- Status progression: Pending → In Progress → Resolved or Rejected
- Tracks submitter, location (District/Sabha/Wasama), category, and attachments
- Timestamps for creation and updates

**ComplaintRemark**: Audit trail
- Records each status change with officer notes
- Preserves status_from and status_to for history

### Workflow

1. **Citizen Submits**: Chooses district → sabha → wasama, fills form, submits
2. **Reference Generated**: Automatic CCMS-2026-XXXXX format
3. **Officer Views**: Dashboard shows complaints matching their jurisdiction
4. **Officer Updates**: Changes status from Pending → In Progress → Resolved; adds remarks
5. **History Tracked**: Each update recorded in ComplaintRemark
6. **Citizen Tracks**: Searches by reference number; sees current status and remarks

## Admin Setup (First Time)

After creating a superuser, log in to `/admin/` to:

1. **Create Districts**: Add administrative districts
2. **Create Pradeshiya Sabhas**: Assign to districts
3. **Create Wasamas**: Assign to sabhas; include GN division codes
4. **Create Officers**: Assign users to specific jurisdictions (or leave blank for global access)

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/YourFeature`)
3. Make your changes and test thoroughly
4. Commit with clear messages (`git commit -m 'Add YourFeature'`)
5. Push to your branch (`git push origin feature/YourFeature`)
6. Open a Pull Request with a description of changes

## License

This project is licensed under the GNU General Public License v3.0 — see the [LICENSE](LICENSE) file for details.

---

**Developed for**: Sri Lankan local government complaint management  
**Last Updated**: July 13, 2026
