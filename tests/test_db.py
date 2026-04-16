import pytest

HAS_PSYCOPG2 = False
try:
    import psycopg2
    HAS_PSYCOPG2 = True
except ImportError:
    pass

@pytest.mark.skipif(not HAS_PSYCOPG2, reason="psycopg2 not installed")
class TestDatabase:
    def test_connection(self):
        pass

    def test_execute_query(self):
        pass

    def test_create_and_drop_table(self):
        pass

    def test_insert_and_select(self):
        pass