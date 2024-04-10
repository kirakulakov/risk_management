import logging
import sqlite3
from sqlite3 import Connection, connect

from src.api.request.risks import RequestRisk

db = None


class Database:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance

    def __init__(self, path: str, logger: logging.Logger) -> None:
        self.path = path
        self.logger = logger

        if getattr(self, "initialized", False):
            return

        self.initialized = True

        self.connection: Connection = connect(path, check_same_thread=False)

        self.cursor = self.connection.cursor()

        self.create_tables_and_fill_data()
        self.logger.info("Database initialized")

    def get_path(self):
        return self.path

    def drop_all_tables(self) -> None:
        self.cursor.execute(
            """
            DROP TABLE IF EXISTS accounts; 
            """
        )
        self.cursor.execute(
            """
            DROP TABLE IF EXISTS risks; 
            """
        )
        self.connection.commit()

    def create_tables_and_fill_data(self) -> None:
        """
        Create the tables in the database if they don't exist already and fill them with data.
        """

        self.cursor.execute(
            """
            DROP TABLE IF EXISTS risk_factors; 
            """
        )
        self.cursor.execute(
            """
            DROP TABLE IF EXISTS risk_types; 
            """
        )
        self.cursor.execute(
            """
            DROP TABLE IF EXISTS risk_management_methods; 
            """
        )

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                name TEXT NOT NULL,
                projectName TEXT NOT NULL,
                projectId TEXT NOT NULL,
                description TEXT
            )
        """
        )
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS risks (
                id string NOT NULL,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                name TEXT NOT NULL,
                account_id INTEGER NOT NULL,
                description TEXT,
                comment TEXT,
                risk_factor_id INTEGER NOT NULL,
                risk_type_id INTEGER NOT NULL,
                risk_management_method_id INTEGER NOT NULL,
                probability SMALLINT NOT NULL,
                impact SMALLINT NOT NULL,
                FOREIGN KEY (account_id) REFERENCES accounts(id),
                FOREIGN KEY (risk_factor_id) REFERENCES risk_factors(id),
                FOREIGN KEY (risk_type_id) REFERENCES risk_types(id),
                FOREIGN KEY (risk_management_method_id) REFERENCES risk_management_methods(id)
                PRIMARY KEY (id, account_id)
            )
        """
        )

        self.cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS risk_factors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
        """
        )

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS risk_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )
            """
        )

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS risk_management_methods (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )
            """
        )

        risk_factors = [
            (
                1,
                "Внешний",
            ),
            (
                2,
                "Внутренний",
            ),
        ]
        self.cursor.executemany("INSERT INTO risk_factors (id, name) VALUES (?, ?)", risk_factors)

        risk_types = [
            (
                1,
                "Технический",
            ),
            (
                2,
                "Финансовый",
            ),
            (
                3,
                "Страховой",
            ),
            (
                4,
                "Организационный",
            ),
            (
                5,
                "Рыночный",
            ),
            (
                6,
                "Юридический",
            ),
            (
                7,
                "Социальный",
            ),
        ]
        self.cursor.executemany("INSERT INTO risk_types (id, name) VALUES (?, ?)", risk_types)

        risk_management_methods = [
            (
                1,
                "Уклонение",
            ),
            (
                2,
                "Принятие",
            ),
            (
                3,
                "Ограничение",
            ),
            (
                4,
                "Обеспечение",
            ),
            (
                5,
                "Передача",
            ),
        ]
        self.cursor.executemany(
            "INSERT INTO risk_management_methods (id, name) VALUES (?, ?)",
            risk_management_methods,
        )

        self.connection.commit()

    def delete_risk(self, risk_id: str, auth_account_id: int) -> None:
        self.cursor.execute(
            "DELETE FROM risks WHERE id = ? AND account_id = ?",
            (risk_id, auth_account_id),
        )
        self.connection.commit()

    def get_project_id_by_account_id(self, auth_account_id: int) -> str:
        return self.cursor.execute("SELECT projectId FROM accounts WHERE id = ?", (auth_account_id,)).fetchone()[0]

    def get_last_risk_id(self, auth_account_id: int) -> int:
        id_ = self.cursor.execute(
            "SELECT MAX(id) FROM risks WHERE account_id = ?",
            (auth_account_id,),
        ).fetchone()[0]
        if id_ is None:
            return 0
        return id_

    def get_risks(self, auth_account_id: int, limit: int, offset: int) -> list[tuple]:
        return self.cursor.execute(
            "SELECT id, name, description, comment, risk_factor_id, risk_type_id, risk_management_method_id, probability, impact FROM risks WHERE account_id = ? ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (auth_account_id, limit, offset),
        ).fetchall()

    def get_risk_types(self) -> list[tuple]:
        return self.cursor.execute("SELECT * FROM risk_types").fetchall()

    def get_risk_type_by_id(self, risk_type_id: int) -> tuple:
        return self.cursor.execute("SELECT * FROM risk_types WHERE id = ?", (risk_type_id,)).fetchone()

    def get_risk_factors(self) -> list[tuple]:
        return self.cursor.execute("SELECT * FROM risk_factors").fetchall()

    def get_risk_factor_by_id(self, risk_factor_id: int) -> tuple:
        return self.cursor.execute("SELECT * FROM risk_factors WHERE id = ?", (risk_factor_id,)).fetchone()

    def get_risk_management_methods(self) -> list[tuple]:
        return self.cursor.execute("SELECT * FROM risk_management_methods").fetchall()

    def get_risk_management_method_by_id(self, risk_management_method_id: int) -> tuple:
        return self.cursor.execute(
            "SELECT * FROM risk_management_methods WHERE id = ?",
            (risk_management_method_id,),
        ).fetchone()

    def fetch_account_by_email(self, email: str) -> tuple | None:
        self.cursor.execute(
            "SELECT id, email, name, password, projectName, projectId, description FROM accounts WHERE email = ?",
            (email,),
        )
        return self.cursor.fetchone()

    def fetch_email_by_id(self, auth_account_id: int) -> tuple | None:
        self.cursor.execute(
            "SELECT email FROM accounts WHERE id = ?",
            (str(auth_account_id),),
        )
        return self.cursor.fetchone()

    def fetch_account_by_id(self, account_id: int) -> tuple | None:
        self.cursor.execute(
            "SELECT id, email, name, password, projectName, projectId, description FROM accounts WHERE id = ?",
            (account_id,),
        )
        return self.cursor.fetchone()

    def risk_id_exists(self, risk_id: str, auth_account_id: int) -> bool:
        self.cursor.execute(
            "SELECT id FROM risks WHERE id = ? AND account_id = ?",
            (risk_id, auth_account_id),
        )
        return self.cursor.fetchone() is not None

    def create_risk(self, request_model: RequestRisk, auth_account_id: int) -> tuple:
        self.cursor.execute(
            """
            INSERT INTO risks (
                id, account_id, name, comment, risk_factor_id, risk_type_id, risk_management_method_id, probability, impact
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                request_model.id,
                auth_account_id,
                request_model.name,
                request_model.comment,
                request_model.factor_id,
                request_model.type_id,
                request_model.method_id,
                request_model.probability,
                request_model.impact,
            ),
        )
        self.connection.commit()
        return self.cursor.lastrowid

    def create_account(
            self,
            email: str,
            password: str,
            name: str,
            project_name: str,
            project_id: int,
            description: str | None = None,
    ) -> int:
        """
        Create a new account in the database.

        Returns the ID of the created account.
        """
        if self.connection is None:
            raise RuntimeError("Database is not connected")
        if email is None or email == "":
            raise ValueError("Email cannot be None or empty")
        if password is None or password == "":
            raise ValueError("Password cannot be None or empty")
        if name is None or name == "":
            raise ValueError("Name cannot be None or empty")
        if project_name is None or project_name == "":
            raise ValueError("Project name cannot be None or empty")

        try:
            self.cursor.execute(
                """
                INSERT INTO accounts (email, password, name, projectName, projectId, description)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (email, password, name, project_name, project_id, description),
            )
            self.connection.commit()
            return self.cursor.lastrowid

        except sqlite3.Error as e:
            self.logger.error(f"Error creating account: {e}")
            self.connection.rollback()
            raise RuntimeError(f"Error creating account: {e}") from e
        except Exception as e:
            self.logger.error(f"Unexpected error creating account: {e}")
            self.connection.rollback()
            raise RuntimeError(f"Unexpected error creating account: {e}") from e

    def update_account(
            self,
            account_id: int,
            email: str | None = None,
            name: str | None = None,
            projectName: str | None = None,
            projectId: int | None = None,
            description: str | None = None,
    ) -> None:
        updates = {
            "email": email,
            "name": name,
            "projectName": projectName,
            "projectId": projectId,
            "description": description,
        }

        if not any(updates.values()):
            return

        sql = "UPDATE accounts SET "
        sql += ", ".join([f"{key} = ?" for key, value in updates.items() if value is not None])
        sql += " WHERE id = ?"

        values = [value for value in updates.values() if value is not None]
        values.append(account_id)

        self.cursor.execute(sql, values)
        self.connection.commit()

    def update_account_password(self, account_id: int, password: str) -> None:
        self.cursor.execute(
            """
            UPDATE accounts
            SET password = ?
            WHERE id = ?
        """,
            (password, account_id),
        )
        self.connection.commit()

    def update_password(self, account_id: int, new_password: str) -> None:
        self.cursor.execute(
            """
            UPDATE accounts
            SET password = ?
            WHERE id = ?
        """,
            (new_password, account_id),
        )
        self.connection.commit()

    def close_connection(self) -> None:
        if self.connection is None:
            self.logger.error("Database connection has already been closed or never existed.")
            raise RuntimeError("Database connection has already been closed or never existed.")

        try:
            self.connection.close()
        except Exception as e:
            self.logger.error(f"Unexpected error closing database connection: {e}")
            raise RuntimeError(f"Unexpected error closing database connection: {e}") from e
