# src/lambdas/leaderboard.py
from fastapi import FastAPI
from mangum import Mangum
from ..database import get_db_connection
from datetime import datetime, timedelta

app = FastAPI()

@app.get("/leaderboardDaily")
async def leaderboard_daily():
    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT u.name, sc.stepcount 
                FROM users u 
                JOIN stepcount sc ON u.user_id = sc.user_id 
                WHERE DATE(sc.date) = CURDATE() 
                ORDER BY sc.stepcount DESC
            """)
            users = cursor.fetchall()
            return [{"name": user['name'], "stepcount": user['stepcount']} for user in users]

@app.get("/leaderboardWeekly")
async def leaderboard_weekly():
    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT u.name, ROUND(AVG(sc.stepcount), 2) AS avg_steps 
                FROM users u 
                JOIN stepcount sc ON u.user_id = sc.user_id 
                WHERE sc.date >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
                GROUP BY u.user_id, u.name 
                ORDER BY avg_steps DESC
            """)
            users = cursor.fetchall()
            return [{"name": user['name'], "avg_steps": user['avg_steps']} for user in users]

@app.get("/dashboard")
async def dashboard():
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=6)

    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT u.user_id, u.email_id, 
                       SUM(sc.stepcount) as total_steps,
                       AVG(sc.stepcount) as average_steps
                FROM users u 
                JOIN stepcount sc ON u.user_id = sc.user_id 
                WHERE sc.date BETWEEN %s AND %s 
                GROUP BY u.user_id, u.email_id
            """, (start_date, end_date))
            users_data = cursor.fetchall()

            result = []
            for user in users_data:
                cursor.execute("""
                    SELECT date, stepcount as steps
                    FROM stepcount 
                    WHERE user_id = %s AND date BETWEEN %s AND %s
                """, (user['user_id'], start_date, end_date))
                daily_data = cursor.fetchall()
                
                result.append({
                    "user_id": user['user_id'],
                    "email": user['email_id'],
                    "total_steps": user['total_steps'],
                    "average_steps": user['average_steps'],
                    "last_7_days": [
                        {
                            "date": day['date'].strftime("%Y-%m-%d"),
                            "steps": day['steps']
                        } for day in daily_data
                    ]
                })
            return result

handler = Mangum(app)