from fastapi import FastAPI, Form, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import requests

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

class PromptInput(BaseModel):
    prompt: str

# Helper function to generate prompt based on input
def generate_prompt(city1, city2, city3, duration1, duration2, duration3, con1, con2, con3):
    connections = ', '.join(filter(None, [con1, con2, con3]))
    total_duration = int(duration1) + int(duration2) + int(duration3)
    prompt = (f"You plan to visit 3 Indian cities for {total_duration} days in total. "
            f"You only take direct trains to commute between cities"
            f"You would like to visit {city1} for {duration1} days."
            f"You would like to visit {city2} for {duration2} days, "
            f"You would like to visit {city3} for {duration3} days. "
            f"Here are the cities that have direct trains: {connections}."
            f"Find a trip plan of visiting the cities for {total_duration} days by taking direct trains to commute between them.")
    return prompt

# Endpoint to generate prompt
@app.post("/generate_prompt")
async def generate_prompt_endpoint(city1: str = Form(...), city2: str = Form(...), city3: str = Form(...),
                                   duration1: str = Form(...), duration2: str = Form(...), duration3: str = Form(...),
                                   con1: str = Form(None), con2: str = Form(None), con3: str = Form(None)):
    prompt = generate_prompt(city1, city2, city3, duration1, duration2, duration3, con1, con2, con3)
    return JSONResponse(content={"prompt": prompt})

# Endpoint to call LLM (Ollama) and get the response
@app.post("/plan_trip")
async def plan_trip(request: Request):
    data = await request.json()
    prompt = data['prompt']
    
    # Call the Ollama API to get the LLM output
    url = "http://localhost:11434/api/chat"  # Your local Ollama server URL
    payload = {
        "model": "llama3.1:latest",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "stream": False
    }
    
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        response_data = response.json()
        llm_output = response_data['message']['content']
    else:
        llm_output = f"Error: {response.status_code}"
    
    return JSONResponse(content={"response": llm_output})

