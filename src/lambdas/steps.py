# src/lambdas/steps.py
from fastapi import FastAPI, Request
from mangum import Mangum
from ..database import get_db_connection
from ..utils import format_response, handle_error

app = FastAPI()

@app.post("/updateStepCount")
async def update_step_count(request: Request):
    data = await request.json()
    email = data.get('userEmail')
    step_count = data.get('stepCount')
    date = data.get('date')

    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """INSERT INTO stepcount (user_id, stepcount, date) 
                SELECT u.user_id, %s, %s FROM users u WHERE u.email_id = %s""",
                (step_count, date, email)
            )
            connection.commit()
            return {"message": "Step count updated successfully!"}

@app.post("/buttonAverage")
async def get_average_steps(request: Request):
    data = await request.json()
    email = data.get('userEmail')

    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT AVG(s.stepcount) AS average_stepcount 
                FROM users u 
                JOIN stepcount s ON u.user_id = s.user_id 
                WHERE u.email_id = %s
                GROUP BY u.user_id
            """, (email,))
            result = cursor.fetchone()
            return {"average_stepcount": result['average_stepcount'] if result else 0}

@app.post("/buttonTotal")
async def get_total_steps(request: Request):
    data = await request.json()
    email = data.get('userEmail')

    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT SUM(s.stepcount) AS total_stepcount 
                FROM users u 
                JOIN stepcount s ON u.user_id = s.user_id 
                WHERE u.email_id = %s
                GROUP BY u.user_id
            """, (email,))
            result = cursor.fetchone()
            return {"total_stepcount": result['total_stepcount'] if result else 0}

handler = Mangum(app)