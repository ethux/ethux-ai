from database.database import Database
from fastapi import APIRouter

router = APIRouter()

@router.get("/execution-results")
async def get_execution_results():
    db = Database()
    logs = db.get_logs()
    db.close()
    return {"logs": logs}