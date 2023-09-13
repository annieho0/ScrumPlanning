# FIT2101 Project

This is a web app for a software project management.
By: CL_Thursday6pm_Team2

## Installation Guide for Django Application
### Prerequisites:
- Python (3.6+ recommended)
- pip
- Git
- Virtualenv (optional but recommended)

#### Note:
- If using python does not work try python3 or method to run python scrip. Same with pip and pip3.

### Steps:
#### 1. Clone the Repository:

```bash
git clone <repository_url> <optional_directory_name>
cd <directory_name> # Use the directory name if you specified one during cloning.
```

#### 2. Set Up a Virtual Environment (optional but recommended):
##### Install Virtual Environment
```bash
virtualenv venv
```
##### Activate the environment:

- macOS and Linux: 
```bash
source venv/bin/activate
```
- Windows: 
```bash
.\venv\Scripts\activate
```

#### 3. Install Required Packages:
Install all dependecies required to run the application locally.
```bash
pip install -r requirements.txt
```

#### 4. Database Setup:
Ensure the database is set up and update the DATABASES setting in settings.py.
```bash
python manage.py makemigrations
python manage.py migrate
```

#### 5. Run the Development Server:
You need to hose the server locally for local testing and development.
```bash
python manage.py runserver
```

#### 6. Access the Webapp
Access the application at http://127.0.0.1:8000/ using your preferred browser.
