Requirements

Before running the application, install the following Python libraries:

- django

- pandas

- matplotlib

- seaborn

- numpy

- scikit-learn

- joblib

- mysql-connector-python

- consolemenu

The following modules are part of Python’s standard library and require no separate installation:

- datetime

- pathlib

- string

- random


Setup

1. Clone or download this repository and open a terminal in its root folder.

2. (Optional) Create and activate a virtual environment:

bash

/python3 -m venv venv

/source venv/bin/activate     # On Windows use: venv\Scripts\activate

3. Install the required packages:

bash

/pip install django pandas matplotlib seaborn numpy scikit-learn joblib mysql-connector-python consolemenu


Initial Configuration & Database Creation

1. Run the setup script to configure MySQL and create the database:

bash

/python setup.py

2. When prompted, enter your MySQL connection details:

- Host

- User

- Password

- Port

The script updates the configuration file and creates the database if it doesn’t already exist.


Django Migrations & Server Launch

1. Change into the Django project folder (where manage.py resides):

bash

/cd PersonalFinanceTracker

2. Generate and apply database migrations:

bash

/python manage.py makemigrations  # Optional

/python manage.py migrate

3. Start the development server:

bash

/python manage.py runserver

4. Open your browser at http://127.0.0.1:8000/
