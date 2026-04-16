"""Тесты для сценария Договор займа через TestClient."""
import pytest
from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def client():
    return TestClient(app)


class TestLoan:
    """Тесты для сценария loan."""

    def test_loan_happy_path(self, client):
        """Пройти все обязательные шаги и получить документ."""
        session_id = "test_loan_001"
        
        r = client.post("/api/scenario/loan", json={"session_id": session_id, "answer": ""})
        session_id = r.json().get("session_id", session_id)
        
        answers = [
            "Иванов Иван Иванович",
            "4510",
            "111111",
            "УВД г. Москвы",
            "01.01.2020",
            "",
            "Петров Петр Петрович",
            "4511",
            "222222",
            "ОВД г. Сочи",
            "15.06.2021",
            "",
            "200000",
            "30.03.2026",
            "30.03.2027",
            "12%",
            "1",
            "Москва",
            "",
            "",
            "",
            "1",
        ]
        
        for answer in answers:
            r = client.post("/api/scenario/loan", json={"session_id": session_id, "answer": answer})
            assert r.status_code == 200
        
        data = r.json()
        assert data["is_complete"] is True
        doc = data["document"]
        
        assert "ДОГОВОР" in doc.upper() or "ЗАЕМ" in doc.upper()
        assert "Иванов Иван Иванович" in doc
        assert "Петров Петр Петрович" in doc
        assert "12%" in doc
        
        print(f"✅ test_loan_happy_path passed")

    def test_loan_skip_optional(self, client):
        """Тест с пропуском всех optional полей."""
        session_id = "test_loan_002"
        
        r = client.post("/api/scenario/loan", json={"session_id": session_id, "answer": ""})
        session_id = r.json().get("session_id", session_id)
        
        answers = [
            "Иванов Иван Иванович",
            "4510",
            "111111",
            "УВД г. Москвы",
            "01.01.2020",
            "",
            "Петров Петр Петрович",
            "4511",
            "222222",
            "ОВД г. Сочи",
            "15.06.2021",
            "",
            "100000",
            "01.01.2026",
            "01.01.2027",
            "",  # skip interest_rate
            "Москва",
            "",  # skip purpose
            "",  # skip penalty
            "",  # skip collateral
            "1",
        ]
        
        for answer in answers:
            r = client.post("/api/scenario/loan", json={"session_id": session_id, "answer": answer})
            assert r.status_code == 200
        
        data = r.json()
        assert data["is_complete"] is True
        doc = data["document"]
        
        assert "ДОГОВОР" in doc.upper() or "ЗАЕМ" in doc.upper()
        
        print(f"✅ test_loan_skip_optional passed")

    def test_loan_collects_passport_data(self, client):
        """Проверить, что паспортные данные собираются."""
        session_id = "test_loan_003"
        
        r = client.post("/api/scenario/loan", json={"session_id": session_id, "answer": ""})
        session_id = r.json().get("session_id", session_id)
        
        answers = [
            "Иванов Иван Иванович",
            "4510",
            "111111",
            "УВД г. Москвы",
            "01.01.2020",
            "",  # lender_passport_code skip
            "Петров Петр Петрович",
            "4511",
            "222222",
            "ОВД г. Сочи",
            "15.06.2021",
            "",  # borrower_passport_code skip
            "50000",
            "01.01.2026",
            "01.01.2027",
            "",  # interest_rate skip
            "",  # payment_option skip
            "Москва",
            "",  # purpose skip
            "",  # penalty skip
            "",  # collateral skip
            "1",
        ]
        
        for answer in answers:
            r = client.post("/api/scenario/loan", json={"session_id": session_id, "answer": answer})
            assert r.status_code == 200
        
        data = r.json()
        assert data["is_complete"] is True
        collected = data.get("collected_data", {})
        
        assert "lender_passport" in collected
        assert "borrower_passport" in collected
        
        print(f"✅ test_loan_collects_passport_data passed")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])