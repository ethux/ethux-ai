from database.database import Database

async def log_code_execution(code, result, response_status_code, stderr):
    """
    Logs the execution of a code snippet along with its result.
    """
    db = Database()
    log_entry = db.log_execution(code, result, response_status_code, stderr)
    db.close()
    return {"message": "Code execution logged successfully", "log_entry": log_entry}