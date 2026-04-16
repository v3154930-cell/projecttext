from scenarios.receipt_simple import ReceiptSimpleScenario

s = ReceiptSimpleScenario()

answers = [
    "",  # start
    "Иванов Иван Иванович",
    "4510",
    "123456",
    "УВД г. Москвы",
    "01.01.2020",
    "",
    "Петров Петр Петрович",
    "100000",
]

for i, ans in enumerate(answers):
    result = s.process_answer(ans)
    print(f"{i+1}. answer='{ans}' -> current_step={s.get_current_step()}, complete={s.is_complete()}, result={str(result)[:50] if result else 'None'}")