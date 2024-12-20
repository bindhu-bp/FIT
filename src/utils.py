from fastapi import HTTPException

def handle_error(error_message: str, status_code: int = 400):
    raise HTTPException(status_code=status_code, detail=error_message)

def format_response(data: dict, message: str = "Success"):
    return {
        "status": "success",
        "message": message,
        "data": data
    }