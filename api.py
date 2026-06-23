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
    try:
        # Create a simple testing agent on the fly
        security_agent = Agent(
            role='Data Assistant',
            goal='Provide helpful information based on user request',
            backstory='You are an AI assistant processing incoming requests.',
            verbose=False,
            allow_delegation=False
        )

        # Pass the malicious payload from the scanner to the task
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

        # Execute CrewAI
        result = crew.kickoff()
        
        # Return the response in the format expected by the scanner
        return {"reply": str(result.raw)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# For running on Railway
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
