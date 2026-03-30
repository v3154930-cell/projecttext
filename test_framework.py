"""Smoke-тесты для framework и сценариев ProjectText."""
import sys

MAX_STEPS = 60


def drive_scenario(scenario, answers, label="scenario"):
    """Провести сценарий по шагам, вернуть (success, steps_taken, final_data)."""
    scenario.process_answer("")  # start
    step_count = 0
    last_step = None
    repeats = 0

    while not scenario.is_complete() and step_count < MAX_STEPS:
        current_step = scenario.get_current_step()
        field_type = scenario.get_current_field_type()

        # Guard: бесконечный цикл на одном шаге
        if current_step == last_step:
            repeats += 1
            if repeats > 5:
                print(f"FAIL [{label}]: stuck on step '{current_step}' after {repeats} repeats")
                return False, step_count, scenario.data
        else:
            repeats = 0
        last_step = current_step

        # Определяем ответ: preview/edit/post_edit_choice берём из answers по field_type
        if field_type == "preview":
            answer = answers.get("preview", "1")
        elif field_type == "edit_select":
            answer = answers.get("edit_select", "2")  # default: back to preview
        elif field_type == "post_edit_choice":
            answer = answers.get("post_edit_choice", "2")  # default: return to preview
        elif current_step == "done":
            # Safety: shouldn't happen if is_complete is False
            break
        else:
            answer = answers.get(current_step, "пропустить")

        result = scenario.process_answer(answer)
        if result:
            print(f"  [{label}] step={current_step} ft={field_type} -> {result[:80]}")
        step_count += 1

    return scenario.is_complete(), step_count, scenario.data


# ── receipt_simple ──────────────────────────────────────────────

def test_receipt_simple_happy_path():
    from scenarios.receipt_simple import ReceiptSimpleScenario
    s = ReceiptSimpleScenario()

    answers = {
        "ask_receiver_fio": "Иванов Иван Иванович",
        "ask_passport_series": "4510",
        "ask_passport_number": "123456",
        "ask_passport_issued_by": "УВД г. Москвы",
        "ask_passport_date": "01.01.2020",
        "ask_passport_code": "770001",
        "ask_sender_fio": "Петров Петр Петрович",
        "ask_amount": "100000",
        "ask_date": "30.03.2026",
        "ask_return_date": "30.09.2026",
        "ask_city": "Москва",
        "preview": "1",
    }
    ok, steps, data = drive_scenario(s, answers, "receipt_simple")
    assert ok, f"Сценарий не завершился за {MAX_STEPS} шагов. Last: {s.get_current_step()}"
    assert data.get("fio_receiver") == "Иванов Иван Иванович"
    assert data.get("fio_sender") == "Петров Петр Петрович"
    assert data.get("city") == "Москва"
    assert data.get("passport_series") == "4510"
    assert data.get("passport_number") == "123456"
    assert "passport" in data
    assert s.generate_document()
    print(f"OK   [receipt_simple_happy_path]: {steps} steps")


def test_receipt_simple_passport_optional_skip():
    """Паспортный код подразделения — optional, можно пропустить."""
    from scenarios.receipt_simple import ReceiptSimpleScenario
    s = ReceiptSimpleScenario()

    answers = {
        "ask_receiver_fio": "Сидоров Алексей Петрович",
        "ask_passport_series": "4511",
        "ask_passport_number": "654321",
        "ask_passport_issued_by": "ОВД г. Сочи",
        "ask_passport_date": "15.03.2019",
        "ask_passport_code": "",
        "ask_sender_fio": "Козлов Дмитрий Сергеевич",
        "ask_amount": "50000",
        "ask_date": "01.01.2026",
        "ask_return_date": "01.07.2026",
        "ask_city": "Сочи",
        "preview": "1",
    }
    ok, steps, data = drive_scenario(s, answers, "receipt_simple_skip_code")
    assert ok, f"Сценарий не завершился. Last: {s.get_current_step()}"
    assert "passport_code" not in data or data.get("passport_code") == ""
    print(f"OK   [receipt_simple_skip_code]: {steps} steps")


# ── receipt_advanced ────────────────────────────────────────────

def test_receipt_advanced_happy_path():
    from scenarios.receipt_advanced import ReceiptAdvancedScenario
    s = ReceiptAdvancedScenario()

    answers = {
        "ask_receiver_fio": "Иванов Иван Иванович",
        "ask_passport_series": "4510",
        "ask_passport_number": "123456",
        "ask_passport_issued_by": "УВД г. Москвы",
        "ask_passport_date": "01.01.2020",
        "ask_passport_code": "770001",
        "ask_sender_fio": "Петров Петр Петрович",
        "ask_amount": "100000",
        "ask_date": "30.03.2026",
        "ask_return_date": "30.09.2026",
        "ask_city": "Москва",
        "ask_interest_rate": "10%",
        "ask_payment_option": "1",
        "ask_penalty": "",
        "ask_repayment_order": "",
        "preview": "1",
    }
    ok, steps, data = drive_scenario(s, answers, "receipt_advanced")
    assert ok, f"Сценарий не завершился. Last: {s.get_current_step()}"
    assert data.get("interest_rate") == "10%"
    assert data.get("payment_option") == "1"
    assert "passport" in data
    doc = s.generate_document()
    assert "10%" in doc
    print(f"OK   [receipt_advanced_happy_path]: {steps} steps")


def test_receipt_advanced_with_interest():
    """Процентная ставка + аннуитетный вариант."""
    from scenarios.receipt_advanced import ReceiptAdvancedScenario
    s = ReceiptAdvancedScenario()

    answers = {
        "ask_receiver_fio": "Сидоров Алексей Петрович",
        "ask_passport_series": "4511",
        "ask_passport_number": "654321",
        "ask_passport_issued_by": "ОВД г. Сочи",
        "ask_passport_date": "15.03.2019",
        "ask_passport_code": "",
        "ask_sender_fio": "Козлов Дмитрий Сергеевич",
        "ask_amount": "50000",
        "ask_date": "01.01.2026",
        "ask_return_date": "01.01.2027",
        "ask_city": "Сочи",
        "ask_interest_rate": "15%",
        "ask_payment_option": "2",
        "ask_penalty": "0.1%",
        "ask_repayment_order": "наличными",
        "preview": "1",
    }
    ok, steps, data = drive_scenario(s, answers, "receipt_advanced_interest")
    assert ok, f"Сценарий не завершился. Last: {s.get_current_step()}"
    assert data.get("interest_rate") == "15%"
    assert data.get("payment_option") == "2"
    doc = s.generate_document()
    assert "15%" in doc
    print(f"OK   [receipt_advanced_interest]: {steps} steps")


def test_receipt_advanced_skip_interest():
    """Пропуск процентной ставки — payment_option тоже пропускается (depends_on)."""
    from scenarios.receipt_advanced import ReceiptAdvancedScenario
    s = ReceiptAdvancedScenario()

    answers = {
        "ask_receiver_fio": "Иванов Иван Иванович",
        "ask_passport_series": "4510",
        "ask_passport_number": "123456",
        "ask_passport_issued_by": "УВД г. Москвы",
        "ask_passport_date": "01.01.2020",
        "ask_passport_code": "770001",
        "ask_sender_fio": "Петров Петр Петрович",
        "ask_amount": "100000",
        "ask_date": "30.03.2026",
        "ask_return_date": "30.09.2026",
        "ask_city": "Москва",
        "ask_interest_rate": "",
        "ask_penalty": "",
        "ask_repayment_order": "",
        "preview": "1",
    }
    ok, steps, data = drive_scenario(s, answers, "receipt_advanced_skip_interest")
    assert ok, f"Сценарий не завершился. Last: {s.get_current_step()}"
    assert "interest_rate" not in data or data.get("interest_rate") == ""
    assert "payment_option" not in data
    print(f"OK   [receipt_advanced_skip_interest]: {steps} steps")


# ── loan ────────────────────────────────────────────────────────

def test_loan_happy_path():
    from scenarios.loan import LoanScenario
    s = LoanScenario()

    answers = {
        "ask_lender": "Иванов Иван Иванович",
        "ask_lender_passport_series": "4510",
        "ask_lender_passport_number": "111111",
        "ask_lender_passport_issued_by": "УВД г. Москвы",
        "ask_lender_passport_date": "01.01.2020",
        "ask_lender_passport_code": "770001",
        "ask_borrower": "Петров Петр Петрович",
        "ask_borrower_passport_series": "4511",
        "ask_borrower_passport_number": "222222",
        "ask_borrower_passport_issued_by": "ОВД г. Сочи",
        "ask_borrower_passport_date": "15.06.2021",
        "ask_borrower_passport_code": "",
        "ask_amount": "200000",
        "ask_date": "30.03.2026",
        "ask_term": "30.03.2027",
        "ask_interest_rate": "12%",
        "ask_payment_option": "1",
        "ask_city": "Москва",
        "ask_purpose": "",
        "ask_penalty": "",
        "ask_collateral": "",
        "preview": "1",
    }
    ok, steps, data = drive_scenario(s, answers, "loan")
    assert ok, f"Сценарий не завершился. Last: {s.get_current_step()}"
    assert data.get("lender") == "Иванов Иван Иванович"
    assert data.get("borrower") == "Петров Петр Петрович"
    assert data.get("interest_rate") == "12%"
    assert "lender_passport" in data
    assert "borrower_passport" in data
    assert data.get("days") == "3"
    assert data.get("notice_days") == "30"
    doc = s.generate_document()
    assert "12%" in doc
    print(f"OK   [loan_happy_path]: {steps} steps")


def test_loan_skip_optional():
    """Loan с пропуском всех optional полей."""
    from scenarios.loan import LoanScenario
    s = LoanScenario()

    answers = {
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
        "ask_amount": "100000",
        "ask_date": "01.01.2026",
        "ask_term": "01.01.2027",
        "ask_interest_rate": "",
        "ask_city": "Москва",
        "ask_purpose": "",
        "ask_penalty": "",
        "ask_collateral": "",
        "preview": "1",
    }
    ok, steps, data = drive_scenario(s, answers, "loan_skip_optional")
    assert ok, f"Сценарий не завершился. Last: {s.get_current_step()}"
    assert "interest_rate" not in data or data.get("interest_rate") == ""
    print(f"OK   [loan_skip_optional]: {steps} steps")


# ── preview / edit / post_edit_choice ───────────────────────────

def test_receipt_simple_edit_flow():
    """Полный цикл: заполнение -> preview -> edit -> вернуться к preview -> confirm."""
    from scenarios.receipt_simple import ReceiptSimpleScenario
    s = ReceiptSimpleScenario()

    fill = {
        "ask_receiver_fio": "Иванов Иван Иванович",
        "ask_passport_series": "4510",
        "ask_passport_number": "123456",
        "ask_passport_issued_by": "УВД г. Москвы",
        "ask_passport_date": "01.01.2020",
        "ask_passport_code": "",
        "ask_sender_fio": "Петров Петр Петрович",
        "ask_amount": "100000",
        "ask_date": "30.03.2026",
        "ask_return_date": "30.09.2026",
        "ask_city": "Москва",
    }

    s.process_answer("")  # start
    step_count = 0
    for name, ans in fill.items():
        while s.get_current_step() != name and not s.is_complete() and step_count < MAX_STEPS:
            s.process_answer("пропустить")
            step_count += 1
        if s.get_current_step() == name:
            s.process_answer(ans)
            step_count += 1

    # Should be in preview
    assert s.get_current_field_type() == "preview", f"Expected preview, got {s.get_current_field_type()}"

    # Edit: "2" -> edit_select
    s.process_answer("2")
    assert s.get_current_field_type() == "edit_select"

    # Select first editable field
    s.process_answer("1")
    assert s._return_to_preview is True

    # Re-enter current value for the field being edited
    step = s._steps[s._current_index]
    current_val = s.data.get(step.data_key, "test")
    s.process_answer(str(current_val))

    # post_edit_choice
    assert s.get_current_field_type() == "post_edit_choice"

    # Return to preview
    s.process_answer("2")
    assert s.get_current_field_type() == "preview"

    # Confirm
    s.process_answer("1")
    assert s.is_complete()
    doc = s.generate_document()
    assert "РАСПИСКА" in doc
    print(f"OK   [receipt_simple_edit_flow]: edit cycle works")


# ── BaseScenario unit tests ─────────────────────────────────────

def test_base_scenario_step_flow():
    """Проверка базового flow: start -> steps -> done."""
    from framework import BaseScenario, FieldStep, FieldType, required

    steps = [
        FieldStep(name="start", question=""),
        FieldStep(name="ask_name", question="Имя:", data_key="name",
                  validators=[lambda a: required(a, "Имя")]),
        FieldStep(name="ask_age", question="Возраст:", data_key="age",
                  optional=True),
    ]
    sc = BaseScenario(steps=steps, template_path="templates/receipt_simple.txt")

    assert sc.get_current_step() == "start"
    sc.process_answer("")
    assert sc.get_current_step() == "ask_name"

    err = sc.process_answer("")
    assert err is not None

    sc.process_answer("Тест")
    assert sc.get_current_step() == "ask_age"

    sc.process_answer("пропустить")
    assert sc.get_current_step() == "done"
    assert sc.is_complete()
    assert sc.data["name"] == "Тест"
    print("OK   [base_scenario_step_flow]")


def test_depends_on():
    """Шаг с depends_on пропускается, если зависимость не заполнена."""
    from framework import BaseScenario, FieldStep, FieldType

    steps = [
        FieldStep(name="start", question=""),
        FieldStep(name="ask_a", question="A:", data_key="a", optional=True),
        FieldStep(name="ask_b", question="B:", data_key="b", depends_on="a"),
        FieldStep(name="ask_c", question="C:", data_key="c"),
    ]
    sc = BaseScenario(steps=steps, template_path="templates/receipt_simple.txt")
    sc.process_answer("")
    assert sc.get_current_step() == "ask_a"
    sc.process_answer("пропустить")  # skip optional a
    assert sc.get_current_step() == "ask_c", f"Expected ask_c, got {sc.get_current_step()}"
    sc.process_answer("val_c")
    assert sc.is_complete()
    assert "a" not in sc.data
    assert "b" not in sc.data
    print("OK   [depends_on]")


# ── Run all ─────────────────────────────────────────────────────

if __name__ == "__main__":
    tests = [
        test_receipt_simple_happy_path,
        test_receipt_simple_passport_optional_skip,
        test_receipt_advanced_happy_path,
        test_receipt_advanced_with_interest,
        test_receipt_advanced_skip_interest,
        test_loan_happy_path,
        test_loan_skip_optional,
        test_receipt_simple_edit_flow,
        test_base_scenario_step_flow,
        test_depends_on,
    ]
    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except Exception as e:
            print(f"FAIL [{t.__name__}]: {e}")
            failed += 1
    print(f"\n{'='*50}")
    print(f"Results: {passed} passed, {failed} failed out of {len(tests)}")
    sys.exit(1 if failed else 0)
