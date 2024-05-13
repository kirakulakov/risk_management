import logging
import sqlite3
from sqlite3 import Connection, connect

from src.api.request.risks import RequestRisk, RequestRiskUpdate

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

    def drop_tables_with_dynamic_data(self) -> None:
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
        self.cursor.execute(
            """
            DROP TABLE IF EXISTS history_log_risks; 
            """
        )
        self.connection.commit()

    def create_tables_and_fill_data(self) -> None:
        """
        Create the tables in the database if they don't exist already and fill them with data.
        """
        self.cursor.execute(
            """
            DROP TABLE IF EXISTS probability; 
            """
        )
        self.cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS probability (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            value FLOAT NOT NULL
        )
        """
        )
        probabilities = [
            (
                1,
                "Низкая",
                0.2
            ),
            (
                2,
                "Ниже среднего",
                0.4

            ),
            (
                3,
                "Средняя",
                0.6
            ),
            (
                4,
                "Выше среднего",
                0.8
            ),
            (
                5,
                "Высокая",
                1
            )
        ]
        self.cursor.executemany("INSERT INTO probability (id, name, value) VALUES (?, ?, ?)", probabilities)

        self.cursor.execute(
            """
            DROP TABLE IF EXISTS impact; 
            """
        )
        self.cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS impact (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            value FLOAT NOT NULL
        )
        """
        )
        impacts = [
            (
                1,
                "Незначительное",
                0.2
            ),
            (
                2,
                "Минимальное",
                0.4

            ),
            (
                3,
                "Среднее",
                0.6
            ),
            (
                4,
                "Высокое",
                0.8
            ),
            (
                5,
                "Критичное",
                1
            )
        ]
        self.cursor.executemany("INSERT INTO impact (id, name, value) VALUES (?, ?, ?)", impacts)

        self.cursor.execute(
            """
            DROP TABLE IF EXISTS risk_status; 
            """
        )

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
        CREATE TABLE IF NOT EXISTS risk_status (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
            )
        """
        )
        risk_statuses = [
            (
                1,
                "Открыто",
            ),
            (
                2,
                "Выполняется",
            ),
            (
                3,
                "Закрыто",
            ),
        ]
        self.cursor.executemany("INSERT INTO risk_status (id, name) VALUES (?, ?)", risk_statuses)

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
                risk_status_id INTEGER NOT NULL DEFAULT 1,
                probability_id INTEGER,
                impact_id INTEGER,
                FOREIGN KEY (account_id) REFERENCES accounts(id),
                FOREIGN KEY (risk_factor_id) REFERENCES risk_factors(id),
                FOREIGN KEY (risk_type_id) REFERENCES risk_types(id),
                FOREIGN KEY (risk_management_method_id) REFERENCES risk_management_methods(id),
                FOREIGN KEY (risk_status_id) REFERENCES risk_status(id),
                FOREIGN KEY (probability_id) REFERENCES probability(id),
                FOREIGN KEY (impact_id) REFERENCES impact(id),
                PRIMARY KEY (id, account_id)
            )
        """
        )

        self.cursor.execute(
            """
            CREATE TRIGGER IF NOT EXISTS track_name_changes
            AFTER UPDATE OF name ON risks
            FOR EACH ROW
            BEGIN
                INSERT INTO history_log_risks (risk_id, updated_column_name, old_data, new_data, timestamp, prev_history_id)
                VALUES (OLD.id, 'название', OLD.name, NEW.name, CURRENT_TIMESTAMP, (SELECT id FROM history_log_risks WHERE risk_id = OLD.id ORDER BY id DESC LIMIT 1));
            END;
            """
        )

        self.cursor.execute(
            """
            CREATE TRIGGER IF NOT EXISTS track_description_changes
            AFTER UPDATE OF description ON risks
            FOR EACH ROW
            BEGIN
                INSERT INTO history_log_risks (risk_id, updated_column_name, old_data, new_data, timestamp, prev_history_id)
                VALUES (OLD.id, 'описание', OLD.description, NEW.description, CURRENT_TIMESTAMP, (SELECT id FROM history_log_risks WHERE risk_id = OLD.id ORDER BY id DESC LIMIT 1));
            END;
            """
        )

        self.cursor.execute(
            """
            CREATE TRIGGER IF NOT EXISTS track_comment_changes
            AFTER UPDATE OF comment ON risks
            FOR EACH ROW
            BEGIN
                INSERT INTO history_log_risks (risk_id, updated_column_name, old_data, new_data, timestamp, prev_history_id)
                VALUES (OLD.id, 'комментарий', OLD.comment, NEW.comment, CURRENT_TIMESTAMP, (SELECT id FROM history_log_risks WHERE risk_id = OLD.id ORDER BY id DESC LIMIT 1));
            END;
            """
        )

        self.cursor.execute(
            """
            CREATE TRIGGER IF NOT EXISTS track_risk_factor_id_changes
            AFTER UPDATE OF risk_factor_id ON risks
            FOR EACH ROW
            WHEN OLD.risk_factor_id != NEW.risk_factor_id
            BEGIN
                INSERT INTO history_log_risks (risk_id, updated_column_name, old_data, new_data, timestamp, prev_history_id)
                VALUES (OLD.id, 'фактор', (SELECT name FROM risk_factors WHERE id = OLD.risk_factor_id), (SELECT name FROM risk_factors WHERE id = NEW.risk_factor_id), CURRENT_TIMESTAMP, (SELECT id FROM history_log_risks WHERE risk_id = OLD.id ORDER BY id DESC LIMIT 1));
            END;
            """
        )
        self.cursor.execute(
            """
            CREATE TRIGGER IF NOT EXISTS track_risk_type_id_changes
            AFTER UPDATE OF risk_type_id ON risks
            FOR EACH ROW
            WHEN OLD.risk_type_id != NEW.risk_type_id
            BEGIN
                INSERT INTO history_log_risks (risk_id, updated_column_name, old_data, new_data, timestamp, prev_history_id)
                VALUES (OLD.id, 'вид риска', (SELECT name FROM risk_types WHERE id = OLD.risk_type_id), (SELECT name FROM risk_types WHERE id = NEW.risk_type_id), CURRENT_TIMESTAMP, (SELECT id FROM history_log_risks WHERE risk_id = OLD.id ORDER BY id DESC LIMIT 1));
            END;
            """
        )
        self.cursor.execute(
            """
            CREATE TRIGGER IF NOT EXISTS track_risk_management_method_id_changes
            AFTER UPDATE OF risk_management_method_id ON risks
            FOR EACH ROW
            WHEN OLD.risk_management_method_id != NEW.risk_management_method_id
            BEGIN
                INSERT INTO history_log_risks (risk_id, updated_column_name, old_data, new_data, timestamp, prev_history_id)
                VALUES (OLD.id, 'метод управления', (SELECT name FROM risk_management_methods WHERE id = OLD.risk_management_method_id), (SELECT name FROM risk_management_methods WHERE id = NEW.risk_management_method_id), CURRENT_TIMESTAMP, (SELECT id FROM history_log_risks WHERE risk_id = OLD.id ORDER BY id DESC LIMIT 1));
            END;
            """
        )
        self.cursor.execute(
            """
            CREATE TRIGGER IF NOT EXISTS track_risk_status_id_changes
            AFTER UPDATE OF risk_status_id ON risks
            FOR EACH ROW
            WHEN OLD.risk_status_id != NEW.risk_status_id
            BEGIN
                INSERT INTO history_log_risks (risk_id, updated_column_name, old_data, new_data, timestamp, prev_history_id)
                VALUES (OLD.id, 'статус', (SELECT name FROM risk_status WHERE id = OLD.risk_status_id), (SELECT name FROM risk_status WHERE id = NEW.risk_status_id), CURRENT_TIMESTAMP, (SELECT id FROM history_log_risks WHERE risk_id = OLD.id ORDER BY id DESC LIMIT 1));
            END;
            """
        )
        self.cursor.execute(
            """
            CREATE TRIGGER IF NOT EXISTS track_probability_id_changes
            AFTER UPDATE OF probability_id ON risks
            FOR EACH ROW
            WHEN OLD.probability_id != NEW.probability_id
            BEGIN
                INSERT INTO history_log_risks (risk_id, updated_column_name, old_data, new_data, timestamp, prev_history_id)
                VALUES (OLD.id, 'вероятность', (SELECT name FROM probability WHERE id = OLD.probability_id), (SELECT name FROM probability WHERE id = NEW.probability_id), CURRENT_TIMESTAMP, (SELECT id FROM history_log_risks WHERE risk_id = OLD.id ORDER BY id DESC LIMIT 1));
            END;
            """
        )
        self.cursor.execute(
            """
            CREATE TRIGGER IF NOT EXISTS track_impact_id_changes
            AFTER UPDATE OF impact_id ON risks
            FOR EACH ROW
            WHEN OLD.impact_id != NEW.impact_id
            BEGIN
                INSERT INTO history_log_risks (risk_id, updated_column_name, old_data, new_data, timestamp, prev_history_id)
                VALUES (OLD.id, 'влияние', (SELECT name FROM impact WHERE id = OLD.impact_id), (SELECT name FROM impact WHERE id = NEW.impact_id), CURRENT_TIMESTAMP, (SELECT id FROM history_log_risks WHERE risk_id = OLD.id ORDER BY id DESC LIMIT 1));
            END;

            """
        )

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS history_log_risks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                risk_id string NOT NULL,
                prev_history_id INTEGER,
                updated_column_name TEXT NOT NULL,
                old_data TEXT,
                new_data TEXT NOT NULL,
                timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (risk_id) REFERENCES risks(id),
                FOREIGN KEY (prev_history_id) REFERENCES history_log_risks(id)
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
        self.cursor.execute(
            f"DELETE FROM history_log_risks WHERE risk_id = '{risk_id}'",
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
            "SELECT id, name, description, comment, risk_factor_id, risk_type_id, risk_management_method_id, probability_id, impact_id, risk_status_id FROM risks WHERE account_id = ? ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (auth_account_id, limit, offset),
        ).fetchall()

    def get_risk_by_id(self, auth_account_id: int, risk_id: str) -> tuple:
        return self.cursor.execute(
            "SELECT id, name, description, comment, risk_factor_id, risk_type_id, risk_management_method_id, probability_id, impact_id, risk_status_id FROM risks WHERE account_id = ? AND id = ?",
            (auth_account_id, risk_id),
        ).fetchone()

    def get_risk_created_at_by_id(self, auth_account_id: int, risk_id: str) -> tuple:
        return self.cursor.execute(
            "SELECT created_at FROM risks WHERE account_id = ? AND id = ?",
            (auth_account_id, risk_id),
        ).fetchone()

    def get_risk_history_by_risk_id(self, risk_id: str, limit: int, offset: int) -> list[tuple]:
        return self.cursor.execute(
            "SELECT timestamp, updated_column_name, old_data, new_data FROM history_log_risks WHERE risk_id = ? ORDER BY id DESC LIMIT ? OFFSET ?",
            (risk_id, limit, offset),
        ).fetchall()

    def update_risk_by_request_model(self, auth_account_id: int, request_model: RequestRiskUpdate) -> None:
        attributes = {
            'name': request_model.name,
            'description': request_model.description,
            'comment': request_model.comment,
            'risk_factor_id': request_model.factor_id,
            'risk_type_id': request_model.type_id,
            'risk_management_method_id': request_model.method_id,
            'probability_id': request_model.probability_id,
            'impact_id': request_model.impact_id,
            'risk_status_id': request_model.status_id
        }

        query = "UPDATE risks SET "
        _params = []

        for attr, value in attributes.items():
            if value is not None:
                query += f"{attr} = ?, "
                _params.append(value)

        query = query.rstrip(', ')  # remove trailing comma and space
        query += " WHERE account_id = ? AND id = ?"
        _params += [auth_account_id, request_model.id]

        self.cursor.execute(query, tuple(_params))
        self.connection.commit()

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

    def get_risk_statuses(self) -> list[tuple]:
        return self.cursor.execute("SELECT * FROM risk_status").fetchall()

    def get_risk_probabilities(self) -> list[tuple]:
        return self.cursor.execute("SELECT id, name, value FROM probability").fetchall()

    def get_risk_impacts(self) -> list[tuple]:
        return self.cursor.execute("SELECT id, name, value FROM impact").fetchall()

    def get_risk_status_by_id(self, risk_status_id: int) -> tuple:
        return self.cursor.execute("SELECT * FROM risk_status WHERE id = ?", (risk_status_id,)).fetchone()

    def get_risk_probability_by_id(self, risk_probability_id: int) -> tuple:
        return self.cursor.execute("SELECT id, name, value FROM probability WHERE id = ?",
                                   (risk_probability_id,)).fetchone()

    def get_risk_impact_by_id(self, risk_impact_id: int) -> tuple:
        return self.cursor.execute("SELECT id, name, value FROM impact WHERE id = ?",
                                   (risk_impact_id,)).fetchone()

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
                id, account_id, name, comment, risk_factor_id, risk_type_id, risk_management_method_id, probability_id, impact_id, description
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                request_model.id,
                auth_account_id,
                request_model.name,
                request_model.comment,
                request_model.factor_id,
                request_model.type_id,
                request_model.method_id,
                request_model.probability_id,
                request_model.impact_id,
                request_model.description
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
