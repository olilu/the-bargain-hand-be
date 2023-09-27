# Backend for the Bargain Hand web application

## Prerequisites
- Python
- PostgreSQL Server

## Get Started
To start the backed locally you can clone this repository and add a dev.env file at the root folder.
The dev.env file needs to include at least the following variables (the values are examples):

```text
POSTGRES_USER=pgadmin
POSTGRES_PASSWORD=password
POSTGRES_PORT=5432
POSTGRES_DB=mydb
POSTGRES_SERVER=localhost
SMTP_SERVER=smtp.example.com
SMTP_PORT=465
SMTP_SENDER_EMAIL=test@example.com
SMTP_SENDER_PASSWORD='password'
```
It is advised to create a python virtual environment for the dependencies: https://docs.python.org/3/library/venv.html

To start up the FastAPI application use the following commands:

```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8080 # add --reload for development
```
Access the Swagger API Docs at http://localhost:8080/docs


