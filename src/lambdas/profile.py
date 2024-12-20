# src/lambdas/profile.py
from fastapi import FastAPI, Request
from mangum import Mangum
from ..database import get_db_connection
from ..utils import format_response, handle_error

app = FastAPI()

@app.post("/getUserProfile")
async def get_user_profile(request: Request):
    data = await request.json()
    email = data.get('userEmail')

    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT name, phone_no, role, address, profile_photo FROM users WHERE email_id = %s",
                (email,)
            )
            user = cursor.fetchone()
            if user:
                return {
                    'name': user['name'],
                    'phone': user['phone_no'],
                    'role': user['role'],
                    'address': user['address'],
                    'profilePhoto': user['profile_photo']
                }
            return {"error": "User not found"}

@app.post("/updateUserProfile")
async def update_user_profile(request: Request):
    data = await request.json()
    email = data.get('email')
    name = data.get('name')
    phone = data.get('phone')
    role = data.get('role')
    address = data.get('address')
    profile_photo = data.get('profilePicture')

    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE users 
                SET name = %s, phone_no = %s, role = %s, address = %s, profile_photo = %s
                WHERE email_id = %s
            """, (name, phone, role, address, profile_photo, email))
            connection.commit()
            return {"success": "User profile updated successfully"}

handler = Mangum(app)