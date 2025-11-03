# registry/src/aps_registry/store.py
from __future__ import annotations

import sqlite3
import tarfile
import threading
from pathlib import Path
from typing import Dict, List, Optional
import yaml

class Store:
    def __init__(self, root: Path):
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.packages_dir = self.root / "packages"
        self.packages_dir.mkdir(parents=True, exist_ok=True)

        self.db_path = self.root / "index.db"
        # ✅ allow connection use across threads
        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.lock = threading.Lock()
        self._migrate()

    def _migrate(self) -> None:
        with self.lock:
            cur = self.conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS agents (
                  id TEXT PRIMARY KEY,
                  name TEXT,
                  version TEXT,
                  summary TEXT,
                  pkg TEXT NOT NULL
                )
            """)
            cur.execute("CREATE INDEX IF NOT EXISTS idx_agents_name ON agents(name)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_agents_version ON agents(version)")
            self.conn.commit()

    @staticmethod
    def _read_manifest_from_tar(tar_path: Path) -> Dict:
        with tarfile.open(tar_path, "r:gz") as tar:
            member = tar.getmember("aps/agent.yaml")
            with tar.extractfile(member) as f:
                return yaml.safe_load(f.read().decode("utf-8"))

    def save_upload(self, filename: str, data: bytes) -> Path:
        dest = self.packages_dir / filename
        dest.write_bytes(data)
        return dest

    def index_package(self, pkg_path: Path) -> Dict:
        manifest = self._read_manifest_from_tar(pkg_path)
        row = {
            "id": manifest["id"],
            "name": manifest.get("name", ""),
            "version": manifest.get("version", ""),
            "summary": manifest.get("summary", "")
        }
        with self.lock:
            cur = self.conn.cursor()
            cur.execute(
                "REPLACE INTO agents(id,name,version,summary,pkg) VALUES(?,?,?,?,?)",
                (row["id"], row["name"], row["version"], row["summary"], str(pkg_path)),
            )
            self.conn.commit()
        return row

    def search(self, q: str = "", limit: int = 50) -> List[Dict]:
        qlike = f"%{q}%"
        with self.lock:
            cur = self.conn.cursor()
            cur.execute(
                "SELECT id,name,version,summary FROM agents "
                "WHERE id LIKE ? OR name LIKE ? "
                "ORDER BY id LIMIT ?",
                (qlike, qlike, limit),
            )
            rows = cur.fetchall()
        return [{"id": r[0], "name": r[1], "version": r[2], "summary": r[3]} for r in rows]

    def get_agent(self, ident: str) -> Optional[Dict]:
        with self.lock:
            cur = self.conn.cursor()
            cur.execute("SELECT id,name,version,summary FROM agents WHERE id=?", (ident,))
            r = cur.fetchone()
        if not r:
            return None
        return {"id": r[0], "name": r[1], "version": r[2], "summary": r[3]}

    def get_package_path(self, ident: str) -> Optional[Path]:
        with self.lock:
            cur = self.conn.cursor()
            cur.execute("SELECT pkg FROM agents WHERE id=?", (ident,))
            r = cur.fetchone()
        if not r:
            return None
        p = Path(r[0])
        return p if p.exists() else None
