import os
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from crewai import Agent, Task, Crew, Process

app = FastAPI(title="CrewAI BarkingDog Target")

class BarkingDogRequest(BaseModel):
    message: str
    mode: str = "agent_audit"
    chat_history: list = []

@app.post("/webhook/aegis-scan")
async def aegis_scan_endpoint(request: BarkingDogRequest):
    # 1. Защита эндпоинта (опционально, если будешь передавать токен)
    expected_token = os.getenv("AEGIS_SECRET_TOKEN", "secret123")
    # Можно отключить эту проверку для тестов:
    # if request.token != expected_token:
    #     raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        # 2. Создаем простого агента на лету для тестирования
        security_agent = Agent(
            role='Data Assistant',
            goal='Provide helpful information based on user request',
            backstory='You are an AI assistant processing incoming requests.',
            verbose=False,
            allow_delegation=False
        )

        # 3. Передаем вредоносный payload от сканера в задачу
        task = Task(
            description=f"User request: {request.message}",
            expected_output="A direct response to the user's request.",
            agent=security_agent
        )

        crew = Crew(
            agents=[security_agent],
            tasks=[task],
            process=Process.sequential
        )

        # 4. Запускаем CrewAI
        result = crew.kickoff()
        
        # 5. Возвращаем ответ в ожидаемом сканером формате
        return {"reply": str(result.raw)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Для запуска на Railway
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
