import sqlite3
from datetime import datetime
import uuid

class Database:
    # Init the database
    def __init__(self, db_name='execution_log.db'):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)
        self.create_table()

    def create_table(self):
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS execution_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    log_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    code TEXT NOT NULL,
                    result TEXT NOT NULL,
                    response_status_code INTEGER,
                    stderr TEXT
                )
            ''')

    # Log the execution of a code snippet
    def log_execution(self, code, result, response_status_code=None, stderr=None):
        timestamp = datetime.now().isoformat()
        log_id = str(uuid.uuid4())
        with self.conn:
            cursor = self.conn.execute('''
                INSERT INTO execution_log (log_id, timestamp, code, result, response_status_code, stderr)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (log_id, timestamp, code, result, response_status_code, stderr))
            id = cursor.lastrowid
        return {
            "id": id,
            "log_id": log_id,
            "timestamp": timestamp,
            "code": code,
            "result": result,
            "response_status_code": response_status_code,
            "stderr": stderr
        }

    # Return all the logs from the db in a structured format
    def get_logs(self):
        cursor = self.conn.execute('SELECT * FROM execution_log')
        logs = cursor.fetchall()
        structured_logs = []
        for log in logs:
            structured_logs.append({
                "id": log[0],
                "log_id": log[1],
                "timestamp": log[2],
                "code": log[3],
                "result": log[4],
                "response_status_code": log[5],
                "stderr": log[6]
            })
        return structured_logs

    def close(self):
        self.conn.close()