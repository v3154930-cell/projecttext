"""Тесты для сценария Простой расписки через TestClient."""
import pytest
from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def client():
    return TestClient(app)


class TestReceiptSimple:
    """Тесты для сценария receipt_simple."""

    def test_receipt_simple_happy_path(self, client):
        """Пройти все обязательные шаги и получить документ."""
        session_id = "test_receipt_simple_001"
        
        # Шаг 1: start -> первый вопрос
        response = client.post(
            "/api/scenario/receipt_simple",
            json={"session_id": session_id, "answer": ""}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["question"] is not None
        session_id = data.get("session_id", session_id)
        
        # Заполняем все поля
        answers = [
            "Иванов Иван Иванович",  # ask_receiver_fio
            "4510",                  # ask_passport_series
            "123456",                # ask_passport_number
            "УВД г. Москвы",         # ask_passport_issued_by
            "01.01.2020",            # ask_passport_date
            "",                      # ask_passport_code (skip)
            "Петров Петр Петрович",  # ask_sender_fio
            "100000",                # ask_amount
            "30.03.2026",            # ask_date
            "30.09.2026",            # ask_return_date
            "Москва",                # ask_city
            "1",                     # preview confirm
        ]
        
        for answer in answers:
            response = client.post(
                "/api/scenario/receipt_simple",
                json={"session_id": session_id, "answer": answer}
            )
            assert response.status_code == 200
            data = response.json()
        
        # Проверяем результат
        assert data["is_complete"] is True
        assert data["document"] is not None
        
        doc = data["document"]
        
        # Проверяем ключевые маркеры в документе (формат суммы может отличаться)
        assert "РАСПИСКА" in doc
        assert "Иванов Иван Иванович" in doc
        assert "Петров Петр Петрович" in doc
        assert "100 000" in doc or "100000" in doc
        assert "Москва" in doc
        assert "30.03.2026" in doc
        assert "30.09.2026" in doc
        
        print(f"✅ test_receipt_simple_happy_path passed")

    def test_receipt_simple_collects_data(self, client):
        """Проверить, что данные собираются в collected_data."""
        session_id = "test_receipt_simple_002"
        
        # Start
        response = client.post(
            "/api/scenario/receipt_simple",
            json={"session_id": session_id, "answer": ""}
        )
        session_id = response.json().get("session_id", session_id)
        
        # Заполняем все обязательные поля
        answers = [
            "Иванов Иван Иванович",
            "4510",
            "123456",
            "УВД г. Москвы",
            "01.01.2020",
            "",  # passport_code skip
            "Петров Петр Петрович",
            "50000",
            "01.04.2026",
            "01.10.2026",
            "Сочи",
            "1",  # preview confirm
        ]
        
        for answer in answers:
            response = client.post(
                "/api/scenario/receipt_simple",
                json={"session_id": session_id, "answer": answer}
            )
            assert response.status_code == 200
        
        # Проверяем collected_data
        data = response.json()
        assert data["is_complete"] is True
        collected = data.get("collected_data", {})
        
        assert collected.get("fio_receiver") == "Иванов Иван Иванович"
        assert collected.get("fio_sender") == "Петров Петр Петрович"
        assert "50 000" in collected.get("amount", "") or "50000" in collected.get("amount", "")
        assert collected.get("city") == "Сочи"
        
        print(f"✅ test_receipt_simple_collects_data passed")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])