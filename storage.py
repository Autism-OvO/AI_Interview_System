import json
import logging
import os
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import pymysql
except Exception:  # pragma: no cover
    pymysql = None

logger = logging.getLogger(__name__)
BASE_DIR = Path(__file__).parent


class MySQLStorage:
    """MySQL 持久化实现：专门记录学生面试历次多维度得分等。"""

    def __init__(self):
        cfg = self._load_file_config()
        self.enabled = str(cfg.get("enabled", os.getenv("DB_ENABLED", "1"))).strip() == "1"
        self.host = str(cfg.get("host", os.getenv("DB_HOST", "127.0.0.1"))).strip()
        self.port = int(cfg.get("port", os.getenv("DB_PORT", "3306")))
        self.user = str(cfg.get("user", os.getenv("DB_USER", "ai_user"))).strip()
        self.password = str(cfg.get("password", os.getenv("DB_PASSWORD", "")))
        self.database = str(cfg.get("database", os.getenv("DB_NAME", "ai_interview_scores"))).strip()
        self.charset = str(cfg.get("charset", "utf8mb4")).strip() or "utf8mb4"
        self._ready = False

    def _load_file_config(self) -> Dict[str, Any]:
        """从配置文件读取数据库连接参数。默认读取项目根目录 db_config.json。"""
        config_path = os.getenv("DB_CONFIG_FILE", str(BASE_DIR / "db_config.json"))
        path = Path(config_path)
        if not path.exists():
            return {}

        try:
            with open(path, "r", encoding="utf-8") as f:
                raw = json.load(f)
            if not isinstance(raw, dict):
                return {}
            mysql_cfg = raw.get("mysql", raw)
            if not isinstance(mysql_cfg, dict):
                return {}
            return mysql_cfg
        except Exception:
            return {}

    @property
    def ready(self) -> bool:
        return self.enabled and self._ready

    @contextmanager
    def _conn(self, include_db=True):
        kwargs = {
            "host": self.host,
            "port": self.port,
            "user": self.user,
            "password": self.password,
            "charset": self.charset,
            "autocommit": False,
            "cursorclass": pymysql.cursors.DictCursor,
        }
        if include_db:
            kwargs["database"] = self.database
            
        conn = pymysql.connect(**kwargs)
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def init(self) -> None:
        """初始化数据库连接与表结构。确保库存在并建表。"""
        if not self.enabled:
            logger.info("DB persistence disabled by DB_ENABLED")
            return
        if pymysql is None:
            logger.warning("PyMySQL not installed, DB persistence disabled")
            self.enabled = False
            return
        if not self.password:
            logger.warning("DB_PASSWORD is empty, DB persistence disabled")
            self.enabled = False
            return

        try:
            # 连接到已有的库并创建专门存分数的表
            with self._conn() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        CREATE TABLE IF NOT EXISTS student_scores (
                            id BIGINT PRIMARY KEY AUTO_INCREMENT,
                            session_id VARCHAR(64) NULL,
                            candidate VARCHAR(128) NOT NULL,
                            role VARCHAR(128) NOT NULL,
                            overall_score DECIMAL(5,2) NULL,
                            technical_score DECIMAL(5,2) NULL,
                            logic_score DECIMAL(5,2) NULL,
                            communication_score DECIMAL(5,2) NULL,
                            problem_solving_score DECIMAL(5,2) NULL,
                            report_json JSON NULL,
                            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                        """
                    )
            self._ready = True
            logger.info("DB persistence ready: %s:%s/%s", self.host, self.port, self.database)
        except Exception as e:
            logger.warning("DB init failed, persistence disabled: %s", e)
            self.enabled = False
            self._ready = False

    def save_report_scores(self, session_id: str, candidate: str, role: str, report: Dict[str, Any]) -> None:
        if not self.ready:
            return
        
        overall = report.get('overall')
        by_dim = report.get('by_dimension', {})
        tech = by_dim.get('technical')
        logic = by_dim.get('logic')
        comm = by_dim.get('communication')
        prob = by_dim.get('problem_solving')

        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO student_scores (
                        session_id, candidate, role, 
                        overall_score, technical_score, logic_score, communication_score, problem_solving_score, 
                        report_json
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (session_id, candidate, role, overall, tech, logic, comm, prob, json.dumps(report, ensure_ascii=False))
                )

    def get_growth_curve(self, candidate: str, role: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        """获取候选人的历史成长曲线（按完成时间升序）。"""
        if not self.ready or not candidate:
            return []

        safe_limit = max(1, min(int(limit), 100))
        with self._conn() as conn:
            with conn.cursor() as cur:
                if role:
                    cur.execute(
                        """
                        SELECT * FROM (
                            SELECT
                                session_id,
                                role,
                                overall_score as avg_score,
                                DATE_FORMAT(created_at, '%%Y-%%m-%%d %%H:%%i:%%s') AS completed_at,
                                technical_score, logic_score, communication_score, problem_solving_score
                            FROM student_scores
                            WHERE candidate = %s AND role = %s AND overall_score IS NOT NULL
                            ORDER BY created_at DESC
                            LIMIT %s
                        ) t
                        ORDER BY t.completed_at ASC;
                        """,
                        (candidate, role, safe_limit),
                    )
                else:
                    cur.execute(
                        """
                        SELECT * FROM (
                            SELECT
                                session_id,
                                role,
                                overall_score as avg_score,
                                DATE_FORMAT(created_at, '%%Y-%%m-%%d %%H:%%i:%%s') AS completed_at,
                                technical_score, logic_score, communication_score, problem_solving_score
                            FROM student_scores
                            WHERE candidate = %s AND overall_score IS NOT NULL
                            ORDER BY created_at DESC
                            LIMIT %s
                        ) t
                        ORDER BY t.completed_at ASC;
                        """,
                        (candidate, safe_limit),
                    )
                rows = cur.fetchall() or []

        points: List[Dict[str, Any]] = []
        for i, row in enumerate(rows, start=1):
            points.append({
                "index": i,
                "session_id": row.get("session_id"),
                "role": row.get("role"),
                "score": float(row.get("avg_score")) if row.get("avg_score") is not None else None,
                "technical_score": float(row.get("technical_score")) if row.get("technical_score") is not None else None,
                "logic_score": float(row.get("logic_score")) if row.get("logic_score") is not None else None,
                "communication_score": float(row.get("communication_score")) if row.get("communication_score") is not None else None,
                "problem_solving_score": float(row.get("problem_solving_score")) if row.get("problem_solving_score") is not None else None,
                "completed_at": row.get("completed_at"),
            })
        return points

    def get_candidates(self) -> List[str]:
        """获取所有有成绩记录的候选人姓名列表。"""
        if not self.ready:
            return []
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT DISTINCT candidate FROM student_scores WHERE candidate IS NOT NULL AND candidate != '' ORDER BY candidate;"
                )
                rows = cur.fetchall() or []
                return [row["candidate"] for row in rows]

storage = MySQLStorage()
storage.init()
