"""Тесты сценария receipt_advanced с проверками assert."""
import sys

MAX_STEPS = 60


def drive(scenario, answers, label=""):
    """Провести сценарий до completion, вернуть (ok, steps, data)."""
    scenario.process_answer("")
    step = 0
    last_step = None
    repeats = 0

    while not scenario.is_complete() and step < MAX_STEPS:
        cur = scenario.get_current_step()
        ft = scenario.get_current_field_type()

        # Защита от зацикливания
        if cur == last_step:
            repeats += 1
            if repeats > 5:
                print(f"FAIL [{label}]: stuck at '{cur}' after {repeats} repeats")
                return False, step, scenario.data
        else:
            repeats = 0
        last_step = cur

        if ft == "preview":
            ans = answers.get("preview", "1")
        elif ft == "edit_select":
            ans = answers.get("edit_select", "2")
        elif ft == "post_edit_choice":
            ans = answers.get("post_edit_choice", "2")
        elif cur == "done":
            break
        else:
            ans = answers.get(cur, "пропустить")

        err = scenario.process_answer(ans)
        if err:
            print(f"  [{label}] {cur} ft={ft} -> {err[:80]}")
        step += 1

    return scenario.is_complete(), step, scenario.data


def test_adv_full_happy_path():
    """Полный happy path: ФИО + паспорт + сумма + даты + город + проценты."""
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
    ok, steps, data = drive(s, answers, "adv_full")
    assert ok, f"Не завершился. Last: {s.get_current_step()}"
    assert data.get("fio_receiver") == "Иванов Иван Иванович"
    assert data.get("fio_sender") == "Петров Петр Петрович"
    assert data.get("interest_rate") == "10%"
    assert data.get("payment_option") == "1"
    assert "passport" in data
    doc = s.generate_document()
    assert "РАСШИРЕННАЯ РАСПИСКА" in doc
    assert "10%" in doc
    print(f"OK   [adv_full_happy_path]: {steps} steps")


def test_adv_with_interest_and_penalty():
    """Проценты + штраф + порядок возврата."""
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
        "ask_interest_rate": "15% годовых",
        "ask_payment_option": "2",
        "ask_penalty": "0,1% от суммы за каждый день",
        "ask_repayment_order": "наличными",
        "preview": "1",
    }
    ok, steps, data = drive(s, answers, "adv_interest_penalty")
    assert ok, f"Не завершился. Last: {s.get_current_step()}"
    assert data.get("interest_rate") == "15% годовых"
    assert data.get("payment_option") == "2"
    doc = s.generate_document()
    assert "15%" in doc
    assert "наличными" in doc
    print(f"OK   [adv_interest_penalty]: {steps} steps")


def test_adv_no_interest():
    """Без процентов — depends_on пропускает payment_option."""
    from scenarios.receipt_advanced import ReceiptAdvancedScenario
    s = ReceiptAdvancedScenario()

    answers = {
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
        "ask_interest_rate": "",
        "ask_penalty": "",
        "ask_repayment_order": "",
        "preview": "1",
    }
    ok, steps, data = drive(s, answers, "adv_no_interest")
    assert ok, f"Не завершился. Last: {s.get_current_step()}"
    assert "interest_rate" not in data or data.get("interest_rate") == ""
    assert "payment_option" not in data
    print(f"OK   [adv_no_interest]: {steps} steps")


def test_adv_edit_flow():
    """Заполнение -> preview -> edit -> back to preview -> confirm."""
    from scenarios.receipt_advanced import ReceiptAdvancedScenario
    s = ReceiptAdvancedScenario()

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
        "ask_interest_rate": "",
        "ask_penalty": "",
        "ask_repayment_order": "",
    }

    s.process_answer("")
    step = 0
    for name, ans in fill.items():
        while s.get_current_step() != name and not s.is_complete() and step < MAX_STEPS:
            s.process_answer("пропустить")
            step += 1
        if s.get_current_step() == name:
            s.process_answer(ans)
            step += 1

    assert s.get_current_field_type() == "preview", f"Expected preview, got {s.get_current_field_type()}"

    # Edit -> select field -> re-enter value -> post_edit_choice -> back to preview -> confirm
    s.process_answer("2")  # Редактировать
    assert s.get_current_field_type() == "edit_select"
    s.process_answer("1")  # Выбрать первое поле

    # Re-enter value for the field being edited
    field_step = s._steps[s._current_index]
    current_val = s.data.get(field_step.data_key, "test")
    s.process_answer(str(current_val))

    assert s.get_current_field_type() == "post_edit_choice"
    s.process_answer("2")  # Вернуться к просмотру
    assert s.get_current_field_type() == "preview"
    s.process_answer("1")  # Подтвердить
    assert s.is_complete()
    doc = s.generate_document()
    assert "РАСШИРЕННАЯ РАСПИСКА" in doc
    print(f"OK   [adv_edit_flow]: {step} steps, edit cycle works")


if __name__ == "__main__":
    tests = [
        test_adv_full_happy_path,
        test_adv_with_interest_and_penalty,
        test_adv_no_interest,
        test_adv_edit_flow,
    ]
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
