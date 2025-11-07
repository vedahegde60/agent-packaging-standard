# registry/src/aps_registry/store.py
from __future__ import annotations
import os, json, sqlite3, tarfile
from typing import Dict, List

class Store:
    """
    Simple filesystem + SQLite-backed store.
    Layout:
      <root>/
        index.db
        packages/<id>/<ver>/agent.aps.tar.gz
    """
    def __init__(self, root: str):
        self.root = root
        os.makedirs(self.packages_dir, exist_ok=True)
        self._init_db()

    @property
    def db_path(self) -> str:
        return os.path.join(self.root, "index.db")

    @property
    def packages_dir(self) -> str:
        return os.path.join(self.root, "packages")

    # ------------ DB helpers (fresh connection per call)

    def _conn(self):
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def _init_db(self):
        with self._conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS agents (
                    id TEXT NOT NULL,
                    version TEXT NOT NULL,
                    name TEXT,
                    summary TEXT,
                    manifest TEXT NOT NULL,
                    PRIMARY KEY (id, version)
                )
            """)

    # ------------ Publish path

    def save_upload(self, filename: str, data: bytes) -> str:
        tmp = os.path.join(self.root, "_upload.tmp.tar.gz")
        with open(tmp, "wb") as f:
            f.write(data)
        return tmp

    def index_package(self, tmp_pkg_path: str) -> Dict:
        # Read manifest from tar to know id/version
        import yaml
        with tarfile.open(tmp_pkg_path, "r:gz") as tf:
            try:
                member = tf.getmember("aps/agent.yaml")
            except KeyError:
                raise FileNotFoundError("package missing aps/agent.yaml")
            manifest_yaml = tf.extractfile(member).read().decode("utf-8")
        manifest = yaml.safe_load(manifest_yaml)

        agent_id = manifest["id"]
        version  = manifest["version"]
        name     = manifest.get("name","")
        summary  = manifest.get("summary","")

        dest_dir = os.path.join(self.packages_dir, agent_id, version)
        os.makedirs(dest_dir, exist_ok=True)
        dest_pkg = os.path.join(dest_dir, "agent.aps.tar.gz")

        # Move uploaded file into packages/...
        if os.path.exists(dest_pkg):
            # Overwrite on re-publish of same version (or choose to reject)
            os.remove(dest_pkg)
        os.replace(tmp_pkg_path, dest_pkg)

        # Upsert manifest row
        with self._conn() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO agents (id, version, name, summary, manifest) VALUES (?,?,?,?,?)",
                (agent_id, version, name, summary, json.dumps(manifest)),
            )

        return {"id": agent_id, "version": version, "name": name, "summary": summary}

    # ------------ Query path

    def search(self, q: str) -> List[Dict]:
        sql = """
            SELECT id, version, name, summary
            FROM agents
            {where}
            ORDER BY id ASC, version DESC
        """
        params = ()
        if q:
            like = f"%{q}%"
            where = "WHERE id LIKE ? OR name LIKE ? OR summary LIKE ?"
            params = (like, like, like)
        else:
            where = ""
        sql = sql.format(where=where)
        with self._conn() as conn:
            cur = conn.execute(sql, params)
            rows = cur.fetchall()
        return [{"id": r[0], "version": r[1], "name": r[2] or "", "summary": r[3] or ""} for r in rows]

    def get_agent(self, agent_id: str) -> Dict:
        with self._conn() as conn:
            cur = conn.execute(
                "SELECT manifest FROM agents WHERE id = ? ORDER BY version DESC LIMIT 1",
                (agent_id,),
            )
            row = cur.fetchone()
        if not row:
            return {"error":"not_found","id":agent_id}
        return json.loads(row[0])

    def latest_version(self, agent_id: str) -> str | None:
        with self._conn() as conn:
            cur = conn.execute(
                "SELECT version FROM agents WHERE id = ? ORDER BY version DESC LIMIT 1",
                (agent_id,)
            )
            row = cur.fetchone()
        return row[0] if row else None

    def package_path(self, agent_id: str, version: str) -> str:
        return os.path.join(self.packages_dir, agent_id, version, "agent.aps.tar.gz")
