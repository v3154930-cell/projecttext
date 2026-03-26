from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from scenarios.receipt_simple import ReceiptSimpleScenario
from scenarios.receipt_advanced import ReceiptAdvancedScenario

app = FastAPI()

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

def get_or_create_scenario(session_id: str, scenario_type: str = "receipt_simple"):
    if session_id not in sessions:
        if scenario_type == "receipt_advanced":
            sessions[session_id] = ReceiptAdvancedScenario()
        else:
            sessions[session_id] = ReceiptSimpleScenario()
    return sessions[session_id]

@app.post("/api/scenario/{scenario_type}", response_model=AgentResponse)
def handle_scenario(request: ScenarioRequest, scenario_type: str):
    scenario = get_or_create_scenario(request.session_id, scenario_type)
    
    # Выбираем шаблон в зависимости от типа сценария
    template_map = {
        "receipt_simple": "templates/receipt_simple.txt",
        "receipt_advanced": "templates/receipt_advanced.txt"
    }
    template_path = template_map.get(scenario_type, "templates/receipt_simple.txt")
    
    # Если есть ответ - обрабатываем его
    if request.answer and request.answer != "":
        result = scenario.process_answer(request.answer)
        
        # Если вернулась ошибка
        if result and ("не может быть" in result or "Пожалуйста" in result or "Введите" in result):
            return AgentResponse(
                question=result,
                session_id=request.session_id,
                current_step=scenario.get_current_step()
            )
        
        # Проверяем завершен ли сценарий
        if scenario.is_complete():
            document = scenario.generate_document(template_path)
            return AgentResponse(
                is_complete=True,
                document=document,
                session_id=request.session_id,
                current_step="done"
            )
        
        # Получаем следующий вопрос
        next_question = scenario.get_next_question()
        return AgentResponse(
            question=next_question,
            session_id=request.session_id,
            current_step=scenario.get_current_step()
        )
    
    # Первый вызов без ответа - инициализируем сценарий
    # Вызываем process_answer с пустым ответом чтобы перейти от START к первому вопросу
    if scenario.get_current_step() == "start":
        scenario.process_answer("")
    
    # Получаем первый вопрос
    question = scenario.get_next_question()
    
    return AgentResponse(
        question=question,
        session_id=request.session_id,
        current_step=scenario.get_current_step()
    )

@app.get("/api/scenario/{scenario_type}/reset")
def reset_session(scenario_type: str, session_id: str):
    if session_id in sessions:
        sessions[session_id].reset()
    return {"status": "ok", "session_id": session_id, "scenario_type": scenario_type}

# Обратная совместимость - старые endpoints
@app.post("/api/scenario/receipt_simple", response_model=AgentResponse)
def receipt_simple(request: ScenarioRequest):
    return handle_scenario(request, "receipt_simple")

@app.post("/api/scenario/receipt_advanced", response_model=AgentResponse)
def receipt_advanced(request: ScenarioRequest):
    return handle_scenario(request, "receipt_advanced")

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