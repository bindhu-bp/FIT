# src/lambdas/auth.py
from fastapi import FastAPI, Request
from mangum import Mangum
from ..database import get_db_connection
from ..utils import format_response, handle_error

app = FastAPI()

@app.post("/login")
async def login(request: Request):
    data = await request.json()
    email = data.get('loginEmail')
    password = data.get('loginPassword')

    if not email or not password:
        return {"message": "invalid"}

    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE email_id = %s", (email,))
            user = cursor.fetchone()

            if user and user['password'] == password:
                return {"message": "valid"}
            return {"message": "invalid"}

@app.post("/signup")
async def signup(request: Request):
    data = await request.json()
    name = data.get('signUpName')
    email = data.get('signUpEmail')
    designation = data.get('signUpDesignation')
    phone = data.get('signUpPhone')
    password = data.get('signUpPassword')

    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE email_id = %s", (email,))
            if cursor.fetchone():
                return {"message": "User Account already exists, Click login."}
            
            try:
                cursor.execute(
                    "INSERT INTO users (name, email_id, phone_no, role, password) VALUES (%s, %s, %s, %s, %s)",
                    (name, email, phone, designation, password)
                )
                connection.commit()
                return {"message": "valid"}
            except:
                return {"message": "invalid"}

handler = Mangum(app)