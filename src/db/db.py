import sqlite3
from sqlite3 import Connection, connect

from src.internal.log.log import logger

db = ...


class Database:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance

    def __init__(self, path: str) -> None:
        logger.info("Initializing database")

        if getattr(self, "initialized", False):
            return

        self.initialized = True

        self.connection: Connection = connect(path)

        self.cursor = self.connection.cursor()

        self.create_tables_and_fill_data()

    def create_tables_and_fill_data(self) -> None:
        """
        Create the tables in the database if they don't exist already.
        """
        logger.info("Initializing database tables")

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
        self.cursor.executemany(
            "INSERT INTO risk_factors (id, name) VALUES (?, ?)", risk_factors
        )

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
        self.cursor.executemany(
            "INSERT INTO risk_types (id, name) VALUES (?, ?)", risk_types
        )

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

    def fetch_account_by_email(self, email: str) -> tuple | None:
        logger.info(f"Fetching account by email: {email}")
        self.cursor.execute(
            "SELECT id, email, name, password, projectName, projectId, description FROM accounts WHERE email = ?",
            (email,),
        )
        return self.cursor.fetchone()

    def fetch_email_by_id(self, auth_account_id: int) -> tuple | None:
        logger.info(f"Fetching email by id: {auth_account_id}")
        self.cursor.execute(
            "SELECT email FROM accounts WHERE id = ?",
            (str(auth_account_id),),
        )
        return self.cursor.fetchone()

    def fetch_account_by_id(self, account_id: int) -> tuple | None:
        logger.info(f"Fetching account by ID: {account_id}")
        self.cursor.execute(
            "SELECT id, email, name, password, projectName, projectId, description FROM accounts WHERE id = ?",
            (account_id,),
        )
        return self.cursor.fetchone()

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
            logger.info(f"Creating account: {email}")
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
            logger.error(f"Error creating account: {e}")
            self.connection.rollback()
            raise RuntimeError(f"Error creating account: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error creating account: {e}")
            self.connection.rollback()
            raise RuntimeError(
                f"Unexpected error creating account: {e}"
            ) from e

    def update_account(
        self,
        account_id: int,
        email: str | None = None,
        name: str | None = None,
        projectName: str | None = None,
        projectId: int | None = None,
        description: str | None = None,
    ) -> None:
        logger.info(f"Updating account: {account_id}")
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
        sql += ", ".join(
            [
                f"{key} = ?"
                for key, value in updates.items()
                if value is not None
            ]
        )
        sql += " WHERE id = ?"

        values = [value for value in updates.values() if value is not None]
        values.append(account_id)

        self.cursor.execute(sql, values)
        self.connection.commit()

    def update_account_password(self, account_id: int, password: str) -> None:
        logger.info(f"Updating password for account: {account_id}")
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
        logger.info(f"Updating password for account: {account_id}")
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
            logger.error(
                "Database connection has already been closed or never existed."
            )
            raise RuntimeError(
                "Database connection has already been closed or never existed."
            )

        try:
            logger.info("Closing database connection")
            self.connection.close()
        except Exception as e:
            logger.error(f"Unexpected error closing database connection: {e}")
            raise RuntimeError(
                f"Unexpected error closing database connection: {e}"
            ) from e


def init_db(path: str) -> Database:
    return Database(path=path)
