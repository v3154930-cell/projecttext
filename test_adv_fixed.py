from scenarios.receipt_advanced import ReceiptAdvancedScenario

# Тест нового сценария receipt_advanced
s = ReceiptAdvancedScenario()

print(f"Начальный шаг: {s.get_current_step()}")
print(f"Первый вопрос: {s.get_next_question()}")
print()

# Симулируем прохождение всех шагов
answers = {
    "start": "Иванов Иван Иванович",  # ФИО получателя
    "ask_receiver_fio": "1234 567890",  # Паспорт
    "ask_passport": "Петров Петр Петрович",  # ФИО передающего
    "ask_sender_fio": "50000",  # Сумма
    "ask_amount": "31.12.2026",  # Срок возврата
    "ask_return_date": "26.03.2026",  # Дата составления
    "ask_date": "Москва",  # Город
    "ask_city": "10% годовых",  # Процентная ставка
    "ask_interest_rate": "пропустить",  # Период процентов
    "ask_interest_period": "пропустить",  # Штраф
    "ask_penalty": "наличными"  # Порядок возврата
}

current_step = s.get_current_step()
step_count = 1

while current_step != "done":
    question = s.get_next_question()
    expected_answer = answers.get(current_step, "пропустить")
    
    print(f"Шаг {step_count} ({current_step}):")
    print(f"  Вопрос: {question}")
    print(f"  Ответ: {expected_answer}")
    
    result = s.process_answer(expected_answer)
    if result:
        print(f"  Ошибка/уточнение: {result}")
    
    current_step = s.get_current_step()
    print(f"  Новый шаг: {current_step}")
    print()
    step_count += 1

print("=== ТЕСТ ПРОЙДЕН ===")
print(f"Шагов пройдено: {step_count}")
print(f"Документ готов: {s.is_complete()}")
print()
print("Данные:")
for k, v in s.data.items():
    print(f"  {k}: {v}")
