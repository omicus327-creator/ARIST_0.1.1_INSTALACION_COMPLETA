from __future__ import annotations
import sqlite3, hashlib
from pathlib import Path
from datetime import datetime, timezone
from . import config

def now(): return datetime.now(timezone.utc).astimezone().isoformat(timespec='seconds')
def digest_file(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024), b''): h.update(chunk)
    return h.hexdigest()

class Registry:
    def __init__(self, path=config.DB_PATH):
        self.path=path; self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.db() as c:
            c.execute('''CREATE TABLE IF NOT EXISTS print_jobs(
                id INTEGER PRIMARY KEY, sha256 TEXT NOT NULL, filename TEXT NOT NULL,
                local_path TEXT NOT NULL, printer TEXT NOT NULL, remote_path TEXT,
                status TEXT NOT NULL, created_at TEXT NOT NULL, uploaded_at TEXT,
                started_at TEXT, finished_at TEXT, notes TEXT DEFAULT '')''')
            c.execute('CREATE INDEX IF NOT EXISTS idx_print_hash ON print_jobs(sha256)')
    def db(self):
        c=sqlite3.connect(self.path); c.row_factory=sqlite3.Row; return c
    def add(self, path, printer, remote, status='ENVIADO'):
        with self.db() as c:
            c.execute('INSERT INTO print_jobs(sha256,filename,local_path,printer,remote_path,status,created_at,uploaded_at) VALUES(?,?,?,?,?,?,?,?)',
                (digest_file(path),path.name,str(path),printer,remote,status,now(),now()))
    def update(self, job_id, status):
        stamp=now(); started=stamp if status=='IMPRIMIENDO' else None; finished=stamp if status in ('COMPLETADO','CANCELADO','ERROR') else None
        with self.db() as c:
            c.execute('UPDATE print_jobs SET status=?, started_at=COALESCE(?,started_at), finished_at=COALESCE(?,finished_at) WHERE id=?',(status,started,finished,job_id))
    def latest(self, limit=50):
        with self.db() as c: return c.execute('SELECT * FROM print_jobs ORDER BY id DESC LIMIT ?', (limit,)).fetchall()
    def find_hash(self, sha):
        with self.db() as c: return c.execute('SELECT * FROM print_jobs WHERE sha256=? ORDER BY id DESC LIMIT 1',(sha,)).fetchone()
