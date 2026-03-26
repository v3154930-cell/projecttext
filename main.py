from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uuid
from scenarios.receipt_simple import ReceiptSimpleScenario
from scenarios.receipt_advanced import ReceiptAdvancedScenario
from scenarios.loan import LoanScenario

app = FastAPI()

# Настройка CORS - разрешаем все источники
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Хранилище сессий: ключ = f"{session_id}:{scenario_type}"
sessions = {}

# Словарь шаблонов для каждого типа сценария
template_map = {
    "receipt_simple": "templates/receipt_simple.txt",
    "receipt_advanced": "templates/receipt_advanced.txt",
    "loan": "templates/loan.txt"
}

class AgentResponse(BaseModel):
    is_complete: bool = False
    question: Optional[str] = None
    document: Optional[str] = None
    session_id: str
    current_step: Optional[str] = None

class ScenarioRequest(BaseModel):
    session_id: str
    answer: str = ""

def _make_key(session_id: str, scenario_type: str) -> str:
    """Создаёт составной ключ для хранения сценария."""
    return f"{session_id}:{scenario_type}"

def get_or_create_scenario(session_id: str = None, scenario_type: str = "receipt_simple"):
    """Получает или создаёт сценарий по типу."""
    # Если session_id не передан, создаём новый
    if session_id is None or session_id == "":
        session_id = str(uuid.uuid4())
    
    key = _make_key(session_id, scenario_type)
    
    if key not in sessions:
        if scenario_type == "receipt_advanced":
            sessions[key] = ReceiptAdvancedScenario()
        elif scenario_type == "loan":
            sessions[key] = LoanScenario()
        elif scenario_type == "claim_simple":
            # Заглушка для claim_simple - возвращаем None
            sessions[key] = None
        else:
            sessions[key] = ReceiptSimpleScenario()
    
    return sessions[key], session_id

def is_error_response(text: str) -> bool:
    """Проверяет, является ли текст сообщением об ошибке валидации."""
    if not text:
        return False
    error_prefixes = ("не может быть", "Пожалуйста, введите", "Ошибка")
    return text.startswith(error_prefixes)

@app.post("/api/scenario/{scenario_type}", response_model=AgentResponse)
def handle_scenario(request: ScenarioRequest, scenario_type: str):
    """Универсальный эндпоинт для всех типов сценариев."""
    # Проверяем, поддерживается ли тип
    if scenario_type == "claim_simple":
        return AgentResponse(
            session_id=request.session_id or str(uuid.uuid4()),
            error="Сценарий в разработке",
            current_step="unavailable"
        )
    
    # Получаем или создаём сценарий
    scenario, session_id = get_or_create_scenario(request.session_id, scenario_type)
    
    # Проверяем, реализован ли сценарий
    if scenario is None:
        return AgentResponse(
            session_id=session_id,
            error="Сценарий в разработке",
            current_step="unavailable"
        )
    
    template_path = template_map.get(scenario_type, "templates/receipt_simple.txt")
    
    # Если есть ответ - обрабатываем его
    if request.answer and request.answer != "":
        result = scenario.process_answer(request.answer)
        
        # Если вернулась ошибка валидации - возвращаем её как вопрос
        if result and is_error_response(result):
            return AgentResponse(
                question=result,
                session_id=session_id,
                current_step=scenario.get_current_step()
            )
        
        # Если есть result (следующий вопрос) - возвращаем его
        if result:
            return AgentResponse(
                question=result,
                session_id=session_id,
                current_step=scenario.get_current_step()
            )
        
        # Если result None - проверяем завершён ли сценарий
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
    """Сбрасывает все сценарии для данного session_id."""
    # Удаляем все сессии для данного session_id (все типы)
    keys_to_delete = [key for key in sessions if key.startswith(f"{session_id}:")]
    for key in keys_to_delete:
        del sessions[key]
    
    return {"status": "ok", "session_id": session_id, "deleted": len(keys_to_delete)}

@app.get("/api/session/{session_id}/status")
def session_status(session_id: str):
    """Возвращает статус всех сценариев для данного session_id."""
    result = {"session_id": session_id, "scenarios": {}}
    
    for key, scenario in sessions.items():
        if key.startswith(f"{session_id}:"):
            scenario_type = key.split(":")[1]
            if scenario is not None:
                result["scenarios"][scenario_type] = {
                    "current_step": scenario.get_current_step(),
                    "is_complete": scenario.is_complete(),
                    "data": scenario.data
                }
            else:
                result["scenarios"][scenario_type] = {"error": "not_implemented"}
    
    if not result["scenarios"]:
        return {"status": "not_found", "session_id": session_id}
    
    return result

# Обратная совместимость - старые эндпоинты
@app.post("/api/scenario/receipt_simple", response_model=AgentResponse)
def receipt_simple(request: ScenarioRequest):
    return handle_scenario(request, "receipt_simple")

@app.post("/api/scenario/receipt_advanced", response_model=AgentResponse)
def receipt_advanced(request: ScenarioRequest):
    return handle_scenario(request, "receipt_advanced")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)