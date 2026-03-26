from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uuid
from scenarios.receipt_simple import ReceiptSimpleScenario
from scenarios.receipt_advanced import ReceiptAdvancedScenario
from scenarios.loan import LoanScenario

app = FastAPI()

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sessions = {}

class AgentResponse(BaseModel):
    is_complete: bool = False
    question: Optional[str] = None
    document: Optional[str] = None
    session_id: str
    current_step: Optional[str] = None

class ScenarioRequest(BaseModel):
    session_id: str
    answer: str = ""

def get_or_create_scenario(session_id: str = None, scenario_type: str = "receipt_simple"):
    # Если session_id не передан, создаём новый
    if session_id is None or session_id == "":
        session_id = str(uuid.uuid4())
    
    if session_id not in sessions:
        if scenario_type == "receipt_advanced":
            sessions[session_id] = ReceiptAdvancedScenario()
        elif scenario_type == "loan":
            sessions[session_id] = LoanScenario()
        else:
            sessions[session_id] = ReceiptSimpleScenario()
    return sessions[session_id], session_id

@app.post("/api/scenario/{scenario_type}", response_model=AgentResponse)
def handle_scenario(request: ScenarioRequest, scenario_type: str):
    # Получаем или создаём сценарий
    scenario, session_id = get_or_create_scenario(request.session_id, scenario_type)
    
    # Выбираем шаблон в зависимости от типа сценария
    template_map = {
        "receipt_simple": "templates/receipt_simple.txt",
        "receipt_advanced": "templates/receipt_advanced.txt",
        "loan": "templates/loan.txt"
    }
    template_path = template_map.get(scenario_type, "templates/receipt_simple.txt")
    
    # Если есть ответ - обрабатываем его
    if request.answer and request.answer != "":
        result = scenario.process_answer(request.answer)
        
        # Если вернулась ошибка (проверяем по специфичным фразам в начале строки)
        error_prefixes = ("не может быть", "Пожалуйста, введите")
        if result and result.startswith(error_prefixes):
            return AgentResponse(
                question=result,
                session_id=session_id,
                current_step=scenario.get_current_step()
            )
        
        # Если есть result (следующий вопрос) - возвращаем его напрямую
        if result:
            return AgentResponse(
                question=result,
                session_id=session_id,
                current_step=scenario.get_current_step()
            )
        
        # Проверяем завершен ли сценарий
        if scenario.is_complete():
            document = scenario.generate_document(template_path)
            return AgentResponse(
                is_complete=True,
                document=document,
                session_id=session_id,
                current_step="done"
            )
        
        # Fallback - получаем следующий вопрос
        next_question = scenario.get_next_question()
        return AgentResponse(
            question=next_question,
            session_id=session_id,
            current_step=scenario.get_current_step()
        )
    
    # Первый вызов без ответа - инициализируем сценарий
    # Вызываем process_answer("") для перехода из START в первый вопрос
    if scenario.get_current_step() == "start":
        scenario.process_answer("")
    
    # Получаем первый вопрос
    question = scenario.get_next_question()
    
    return AgentResponse(
        question=question,
        session_id=session_id,
        current_step=scenario.get_current_step()
    )

@app.post("/api/session/{session_id}/reset")
def reset_session(session_id: str):
    if session_id in sessions:
        sessions[session_id].reset()
    return {"status": "ok", "session_id": session_id}

# Удаляем старые endpoints (теперь всё работает через универсальный)

@app.get("/api/session/{session_id}/status")
def session_status(session_id: str):
    if session_id not in sessions:
        return {"status": "not_found", "session_id": session_id}
    scenario = sessions[session_id]
    return {
        "session_id": session_id,
        "current_step": scenario.get_current_step(),
        "is_complete": scenario.is_complete(),
        "data": scenario.data
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)