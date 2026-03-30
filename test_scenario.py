"""Smoke-тест: инициализация сценариев и проверка первого шага."""
import sys


def test_receipt_simple_init():
    from scenarios.receipt_simple import ReceiptSimpleScenario
    s = ReceiptSimpleScenario()
    assert s.get_current_step() == "start"
    s.process_answer("")
    assert s.get_current_step() == "ask_receiver_fio"
    q = s.get_next_question()
    assert "ФИО" in q or "получателя" in q
    print("OK   [receipt_simple_init]")


def test_receipt_advanced_init():
    from scenarios.receipt_advanced import ReceiptAdvancedScenario
    s = ReceiptAdvancedScenario()
    assert s.get_current_step() == "start"
    s.process_answer("")
    assert s.get_current_step() == "ask_receiver_fio"
    print("OK   [receipt_advanced_init]")


def test_loan_init():
    from scenarios.loan import LoanScenario
    s = LoanScenario()
    assert s.get_current_step() == "start"
    s.process_answer("")
    assert s.get_current_step() == "ask_lender"
    assert s.data.get("days") == "3"
    assert s.data.get("notice_days") == "30"
    print("OK   [loan_init]")


def test_step_names():
    """Проверка что все сценарии генерируют ожидаемые имена шагов."""
    from scenarios.receipt_simple import ReceiptSimpleScenario
    from scenarios.loan import LoanScenario

    # receipt_simple: start -> fio -> 5 passport steps -> fio2 -> amount -> date -> return_date -> city
    rs = ReceiptSimpleScenario()
    rs.process_answer("")
    passport_fill = {
        "ask_receiver_fio": "Иванов Иван Иванович",
        "ask_passport_series": "4510",
        "ask_passport_number": "123456",
        "ask_passport_issued_by": "УВД г. Москвы",
        "ask_passport_date": "01.01.2020",
        "ask_passport_code": "",
        "ask_sender_fio": "Петров Петр Петрович",
        "ask_amount": "50000",
        "ask_date": "01.01.2026",
        "ask_return_date": "01.06.2026",
        "ask_city": "Москва",
    }
    for exp, ans in passport_fill.items():
        assert rs.get_current_step() == exp, f"Expected {exp}, got {rs.get_current_step()}"
        rs.process_answer(ans)
    print("OK   [step_names_receipt_simple]")

    # loan
    lo = LoanScenario()
    lo.process_answer("")
    loan_fill = {
        "ask_lender": "Иванов Иван Иванович",
        "ask_lender_passport_series": "4510",
        "ask_lender_passport_number": "111111",
        "ask_lender_passport_issued_by": "УВД г. Москвы",
        "ask_lender_passport_date": "01.01.2020",
        "ask_lender_passport_code": "",
        "ask_borrower": "Петров Петр Петрович",
        "ask_borrower_passport_series": "4511",
        "ask_borrower_passport_number": "222222",
        "ask_borrower_passport_issued_by": "ОВД г. Сочи",
        "ask_borrower_passport_date": "15.06.2021",
        "ask_borrower_passport_code": "",
    }
    for exp, ans in loan_fill.items():
        assert lo.get_current_step() == exp, f"Expected {exp}, got {lo.get_current_step()}"
        lo.process_answer(ans)
    print("OK   [step_names_loan]")


if __name__ == "__main__":
    tests = [test_receipt_simple_init, test_receipt_advanced_init,
             test_loan_init, test_step_names]
    passed = failed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except Exception as e:
            print(f"FAIL [{t.__name__}]: {e}")
            failed += 1
    print(f"\nResults: {passed} passed, {failed} failed out of {len(tests)}")
    sys.exit(1 if failed else 0)
