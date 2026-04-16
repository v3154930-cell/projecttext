"""Тесты для сценария Претензия маркетплейс через TestClient."""
import pytest
from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def client():
    return TestClient(app)


class TestClaimMarketplace:
    """Тесты для сценария claim_marketplace_buyer."""

    def _run_claim_scenario(self, client, session_id, answers):
        """Вспомогательный метод для запуска сценария претензии."""
        # Start
        r = client.post("/api/scenario/claim_marketplace_buyer", json={"session_id": session_id, "answer": ""})
        session_id = r.json().get("session_id", session_id)
        
        for answer in answers:
            r = client.post("/api/scenario/claim_marketplace_buyer", json={"session_id": session_id, "answer": answer})
            assert r.status_code == 200
        
        return r.json()

    def test_claim_not_suitable(self, client):
        """Тест: товар не подошёл (без неустойки)."""
        session_id = "test_claim_not_suitable_001"
        
        answers = [
            "1",   # recipient_type = marketplace
            "1",   # platform = Ozon
            "123456789",
            "Смартфон Xiaomi",
            "25000",
            "Иванов Иван Иванович",
            "4510",
            "123456",
            "УВД г. Москвы",
            "01.01.2020",
            "",
            "16.04.2026",
            "",
            "",
            "1",   # claim_reason = not_suitable
            "1",   # preview confirm
        ]
        
        data = self._run_claim_scenario(client, session_id, answers)
        
        assert data["is_complete"] is True
        doc = data["document"]
        
        assert "ПРЕТЕНЗИЯ" in doc
        assert "Иванов Иван Иванович" in doc
        assert "123456789" in doc
        assert "Смартфон Xiaomi" in doc
        
        # Проверяем причину в collected_data
        collected = data.get("collected_data", {})
        assert collected.get("claim_reason") == "not_suitable"
        
        print(f"✅ test_claim_not_suitable passed")

    def test_claim_defect(self, client):
        """Тест: товар с браком."""
        session_id = "test_claim_defect_001"
        
        answers = [
            "1",  # recipient_type = marketplace
            "2",  # platform = Wildberries
            "987654321",
            "Ноутбук Acer",
            "45000",
            "Петров Петр Петрович",
            "4511",
            "654321",
            "ОВД г. Сочи",
            "15.03.2019",
            "",
            "16.04.2026",
            "10.04.2026",  # receipt_date
            "1",  # condition: упаковка не вскрыта
            "2",  # claim_reason = defect
            "1",
        ]
        
        data = self._run_claim_scenario(client, session_id, answers)
        
        assert data["is_complete"] is True
        doc = data["document"]
        
        assert "ПРЕТЕНЗИЯ" in doc
        assert "Петров Петр Петрович" in doc
        assert "Wildberries" in doc
        
        collected = data.get("collected_data", {})
        assert collected.get("claim_reason") == "defect"
        
        print(f"✅ test_claim_defect passed")

    def test_claim_delivery_with_penalty(self, client):
        """Тест: нарушение сроки доставки с расчётом неустойки."""
        session_id = "test_claim_delivery_001"
        
        answers = [
            "1",  # recipient_type = marketplace
            "3",  # platform = Yandex.Market
            "111222333",
            "Планшет Samsung",
            "30000",
            "Сидоров Алексей Петрович",
            "4512",
            "789012",
            "УВД г. Казани",
            "20.02.2024",
            "",
            "16.04.2026",
            "",  # receipt_date skip
            "",  # condition skip
            "3",  # claim_reason = delivery
            "01.03.2026",  # prepayment_date
            "30000",  # prepayment_amount
            "",  # refund_date skip
            "1",
        ]
        
        data = self._run_claim_scenario(client, session_id, answers)
        
        assert data["is_complete"] is True
        doc = data["document"]
        
        assert "ПРЕТЕНЗИЯ" in doc
        assert "Сидоров Алексей Петрович" in doc
        assert "Yandex.Market" in doc
        
        # Проверяем, что есть расчёт неустойки
        assert "НЕУСТОЙК" in doc.upper() or "неустойк" in doc.lower()
        
        collected = data.get("collected_data", {})
        assert collected.get("claim_reason") == "delivery"
        
        print(f"✅ test_claim_delivery_with_penalty passed")

    def test_claim_cancelled_with_penalty(self, client):
        """Тест: отмена заказа с расчётом неустойки."""
        session_id = "test_claim_cancelled_001"
        
        answers = [
            "1",  # Ozon
            "1",
            "555666777",
            "Наушники Sony",
            "15000",
            "Козлов Дмитрий Сергеевич",
            "4513",
            "456789",
            "ОВД г. Екатеринбурга",
            "10.05.2023",
            "",
            "16.04.2026",
            "",
            "",
            "4",  # claim_reason = cancelled
            "15.02.2026",
            "15000",
            "",
            "1",
        ]
        
        data = self._run_claim_scenario(client, session_id, answers)
        
        assert data["is_complete"] is True
        doc = data["document"]
        
        assert "ПРЕТЕНЗИЯ" in doc
        assert "Козлов Дмитрий Сергеевич" in doc
        
        # Неустойка
        assert "НЕУСТОЙК" in doc.upper() or "неустойк" in doc.lower()
        
        print(f"✅ test_claim_cancelled_with_penalty passed")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])