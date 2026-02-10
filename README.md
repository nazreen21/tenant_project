Tenant_project


Installation
Prerequisites

- Python 3.12+
- PostgreSQL 12+
- pip

Setup Steps

1. Clone the repository
   
   git clone <repository-url>
   cd tenant_project
   

2. Create and activate virtual environment
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

3. Install dependencies

   pip install -r requirements.txt
   

4. Configure environment variables
   
   Create a `.env` file in the project root:
   
   DB_NAME=your_db_name
   DB_USER=your_user_name
   DB_PASSWORD=your_password
   DB_HOST=localhost
   DB_PORT=5432

5. Create PostgreSQL database
   In psql prompt:-
   CREATE DATABASE your_db_name;
   CREATE USER your_user_namer WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE your_db_name TO your_user_name;
   ```

6. Run migrations
   python manage.py migrate

7. Create superuser (Platform Superadmin)
   python manage.py createsuperuser

8. Run development server
   python manage.py runserver

The API will be available at `http://127.0.0.1:8000/`

Authentication

The API uses JWT (JSON Web Tokens) for authentication. Include the access token in the Authorization header:
Authorization: Bearer <access_token>
