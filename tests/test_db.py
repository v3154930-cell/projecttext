"""Тесты для PostgreSQL операций ProjectText.

ВНИМАНИЕ: Для запуска этих тестов требуется настроенная база данных PostgreSQL.
Тесты используют переменные окружения для подключения:
- POSTGRES_HOST
- POSTGRES_PORT
- POSTGRES_DB
- POSTGRES_USER
- POSTGRES_PASSWORD

Если база данных не настроена, тесты будут пропущены (pytest.skip).
"""
import pytest
import os

try:
    import psycopg2
    from psycopg2 import sql
    from psycopg2 import extras
    DB_AVAILABLE = True
except ImportError:
    psycopg2 = None
    sql = None
    extras = None
    DB_AVAILABLE = False


def get_db_connection():
    """Создать подключение к PostgreSQL."""
    if not DB_AVAILABLE or psycopg2 is None:
        raise RuntimeError("psycopg2 not installed")
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        dbname=os.getenv("POSTGRES_DB", "projecttext"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", ""),
    )


def is_db_available():
    """Проверить доступность базы данных."""
    if not DB_AVAILABLE:
        return False
    try:
        conn = get_db_connection()
        conn.close()
        return True
    except Exception:
        return False


def require_db(f):
    """Декоратор для пропуска теста, если БД недоступна."""
    return pytest.mark.skipif(not is_db_available(), "psycopg2 or database not available")(f)


class TestDatabase:
    """Тесты для PostgreSQL операций."""

    @require_db
    def test_connection(self):
        """Проверить подключение к базе данных."""
        conn = get_db_connection()
        assert conn is not None
        conn.close()
        print("✅ test_connection passed")

    @require_db
    def test_execute_query(self):
        """Проверить выполнение простого запроса."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 as result")
        result = cursor.fetchone()
        assert result[0] == 1
        cursor.close()
        conn.close()
        print("✅ test_execute_query passed")

    @require_db
    def test_create_and_drop_table(self):
        """Проверить создание и удаление таблицы."""
        import time
        table_name = "test_table_" + str(int(time.time()) % 10000)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(f"""
            CREATE TABLE {table_name} (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100),
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        conn.commit()
        
        cursor.execute(f"""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = '{table_name}'
            )
        """)
        assert cursor.fetchone()[0] is True
        
        cursor.execute(f"DROP TABLE {table_name}")
        conn.commit()
        
        cursor.execute(f"""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = '{table_name}'
            )
        """)
        assert cursor.fetchone()[0] is False
        
        cursor.close()
        conn.close()
        
        print("✅ test_create_and_drop_table passed")

    @require_db
    def test_insert_and_select(self):
        """Проверить вставку и выборку данных."""
        import time
        table_name = "test_data_" + str(int(time.time()) % 10000)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(f"""
            CREATE TABLE {table_name} (
                id SERIAL PRIMARY KEY,
                scenario_type VARCHAR(50),
                session_id VARCHAR(100),
                data JSONB,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        conn.commit()
        
        test_data = {"amount": "100000", "fio": "Тестов Тест Тестович"}
        cursor.execute(f"""
            INSERT INTO {table_name} (scenario_type, session_id, data)
            VALUES ('receipt_simple', 'test_session_001', '{extras.Json(test_data)}')
            RETURNING id
        """)
        
        record_id = cursor.fetchone()[0]
        
        cursor.execute(f"""
            SELECT scenario_type, session_id, data FROM {table_name} WHERE id = {record_id}
        """)
        
        row = cursor.fetchone()
        assert row[0] == "receipt_simple"
        assert row[1] == "test_session_001"
        assert row[2]["amount"] == "100000"
        assert row[2]["fio"] == "Тестов Тест Тестович"
        
        cursor.execute(f"DROP TABLE {table_name}")
        conn.commit()
        
        cursor.close()
        conn.close()
        
        print("✅ test_insert_and_select passed")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])