import pytest
from playwright.sync_api import Page


def test_claim_marketplace_delivery(page: Page):
    page.goto("http://localhost:8001")
    
    if page.locator("#consentOverlay").is_visible():
        page.click("#consentBtn")
    
    page.click('div[data-type="claim_marketplace_buyer"]')
    
    page.wait_for_selector("#answerInput:not([disabled])", timeout=10000)
    
    page.fill("#answerInput", "1")
    page.click("#sendBtn")
    
    page.wait_for_selector("#answerInput:not([disabled])", timeout=10000)
    page.fill("#answerInput", "1")
    page.click("#sendBtn")
    
    page.wait_for_selector("#answerInput:not([disabled])", timeout=10000)
    page.fill("#answerInput", "123456789")
    page.click("#sendBtn")
    
    page.wait_for_selector("#answerInput:not([disabled])", timeout=10000)
    page.fill("#answerInput", "Смартфон Xiaomi")
    page.click("#sendBtn")
    
    page.wait_for_selector("#answerInput:not([disabled])", timeout=10000)
    page.fill("#answerInput", "25000")
    page.click("#sendBtn")
    
    page.wait_for_selector("#answerInput:not([disabled])", timeout=10000)
    page.fill("#answerInput", "Иванов Иван Иванович")
    page.click("#sendBtn")
    
    page.wait_for_selector("#answerInput:not([disabled])", timeout=10000)
    page.fill("#answerInput", "4510")
    page.click("#sendBtn")
    
    page.wait_for_selector("#answerInput:not([disabled])", timeout=10000)
    page.fill("#answerInput", "123456")
    page.click("#sendBtn")
    
    page.wait_for_selector("#answerInput:not([disabled])", timeout=10000)
    page.fill("#answerInput", "УВД г. Москвы")
    page.click("#sendBtn")
    
    page.wait_for_selector("#answerInput:not([disabled])", timeout=10000)
    page.fill("#answerInput", "01.01.2020")
    page.click("#sendBtn")
    
    page.wait_for_selector("#answerInput:not([disabled])", timeout=10000)
    page.fill("#answerInput", "")
    page.click("#sendBtn")
    
    page.wait_for_selector("#answerInput:not([disabled])", timeout=10000)
    page.fill("#answerInput", "16.04.2026")
    page.click("#sendBtn")
    
    page.wait_for_selector("#answerInput:not([disabled])", timeout=10000)
    page.fill("#answerInput", "")
    page.click("#sendBtn")
    
    page.wait_for_selector("#answerInput:not([disabled])", timeout=10000)
    page.fill("#answerInput", "")
    page.click("#sendBtn")
    
    page.wait_for_selector("#answerInput:not([disabled])", timeout=10000)
    page.fill("#answerInput", "3")
    page.click("#sendBtn")
    
    page.wait_for_selector("#answerInput:not([disabled])", timeout=10000)
    page.fill("#answerInput", "01.03.2026")
    page.click("#sendBtn")
    
    page.wait_for_selector("#answerInput:not([disabled])", timeout=10000)
    page.fill("#answerInput", "25000")
    page.click("#sendBtn")
    
    page.wait_for_selector("#answerInput:not([disabled])", timeout=10000)
    page.fill("#answerInput", "")
    page.click("#sendBtn")
    
    page.wait_for_selector("#answerInput:not([disabled])", timeout=10000)
    page.fill("#answerInput", "1")
    page.click("#sendBtn")
    
    document_area = page.locator("#documentArea")
    doc_text = document_area.inner_text()
    
    assert "неустойка" in doc_text.lower() or "НЕУСТОЙК" in doc_text