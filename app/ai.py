import requests

# ---=== SUMMARIZE ===---
def summarize_task(title: str, description: str) -> str:
    prompt = f"""
    You are a productivity assistant engine.
    
    ONLY output sentences with NO line breaks.
    
    Rewrite this task to be:
    - Clear
    - Actionable
    - Specific
    
    NO Prefixes. NO Suffixes.
    DO NOT include line breaks.
    
    Task:
    Title: {title}
    Description: {description}
    
    Return only the improved version, and keep it to 1 sentence.
    Example:
    Input: Clean the house
    Output: Dedicate 2-3 hours to work on cleaning the house each day to improve health
    """
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3",
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.2,
                "stop": ["\n"]
            }
        }
    )
    return response.json()["response"]

# ---=== SUBTASK BREAKDOWN ===---
def task_breakdown(title: str, description: str) -> dict:
    prompt =f"""
        You are a formatting engine.
        Output ONLY a comma-separated list.
        Do NOT include:
        -bullet points
        -numbering
        -explanations
        -extra text
        -No underscores
        
        No prefixes. No suffixes.
        
        Your task is to Break the following down into 3-4 subtasks:
        
        Task:
        Title: {title}
        Description: {description}
        
        Example:
        Input: Clean the house
        Output: gather supplies, vacuum floors, wipe surfaces, take out trash
        """
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3",
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.2,
                "stop": ["\n"]
            }
        }
    )
    subtasks = {"subtasks" : []}
    for subtask in response.json()["response"].split(","):
        subtask = subtask.strip().capitalize()
        subtasks["subtasks"].append(subtask)
    return subtasks