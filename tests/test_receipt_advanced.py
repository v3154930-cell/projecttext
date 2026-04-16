"""Тесты для сценария Расширенная расписка через TestClient."""
import pytest
from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def client():
    return TestClient(app)


class TestReceiptAdvanced:
    """Тесты для сценария receipt_advanced."""

    def test_receipt_advanced_happy_path(self, client):
        """Пройти все обязательные шаги с процентами и получить документ."""
        session_id = "test_receipt_advanced_001"
        
        # Start
        r = client.post("/api/scenario/receipt_advanced", json={"session_id": session_id, "answer": ""})
        session_id = r.json().get("session_id", session_id)
        
        answers = [
            "Иванов Иван Иванович",
            "4510",
            "123456",
            "УВД г. Москвы",
            "01.01.2020",
            "",
            "Петров Петр Петрович",
            "100000",
            "30.03.2026",
            "30.09.2026",
            "Москва",
            "10%",
            "1",
            "",
            "",
            "1",
        ]
        
        for answer in answers:
            r = client.post("/api/scenario/receipt_advanced", json={"session_id": session_id, "answer": answer})
            assert r.status_code == 200
        
        # Проверяем документ
        data = r.json()
        assert data["is_complete"] is True
        doc = data["document"]
        
        # Ключевые маркеры
        assert "РАСПИСКА" in doc
        assert "Иванов Иван Иванович" in doc
        assert "Петров Петр Петрович" in doc
        assert "10%" in doc
        
        print(f"✅ test_receipt_advanced_happy_path passed")

    def test_receipt_advanced_with_penalty(self, client):
        """Тест с процентами, штрафом и дифференцированными платежами."""
        session_id = "test_receipt_advanced_002"
        
        r = client.post("/api/scenario/receipt_advanced", json={"session_id": session_id, "answer": ""})
        session_id = r.json().get("session_id", session_id)
        
        answers = [
            "Сидоров Алексей Петрович",
            "4511",
            "654321",
            "ОВД г. Сочи",
            "15.03.2019",
            "",
            "Козлов Дмитрий Сергеевич",
            "50000",
            "01.01.2026",
            "01.01.2027",
            "Сочи",
            "15%",
            "2",
            "0.1%",
            "наличными в кассу",
            "1",
        ]
        
        for answer in answers:
            r = client.post("/api/scenario/receipt_advanced", json={"session_id": session_id, "answer": answer})
            assert r.status_code == 200
        
        data = r.json()
        assert data["is_complete"] is True
        doc = data["document"]
        
        assert "15%" in doc
        assert "0.1%" in doc
        
        print(f"✅ test_receipt_advanced_with_penalty passed")

    def test_receipt_advanced_skip_interest(self, client):
        """Тест с пропуском процентной ставки."""
        session_id = "test_receipt_advanced_003"
        
        r = client.post("/api/scenario/receipt_advanced", json={"session_id": session_id, "answer": ""})
        session_id = r.json().get("session_id", session_id)
        
        answers = [
            "Иванов Иван Иванович",
            "4510",
            "123456",
            "УВД г. Москвы",
            "01.01.2020",
            "",
            "Петров Петр Петрович",
            "100000",
            "30.03.2026",
            "30.09.2026",
            "Москва",
            "",  # skip interest_rate
            "",  # skip payment_option
            "",  # skip penalty
            "",  # skip repayment_order
            "1",
        ]
        
        for answer in answers:
            r = client.post("/api/scenario/receipt_advanced", json={"session_id": session_id, "answer": answer})
            assert r.status_code == 200
        
        data = r.json()
        assert data["is_complete"] is True
        doc = data["document"]
        
        assert "РАСПИСКА" in doc
        
        print(f"✅ test_receipt_advanced_skip_interest passed")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])