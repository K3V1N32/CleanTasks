import json
import os
import requests
import dotenv

dotenv.load_dotenv()
OLLAMA_URL = os.getenv("OLLAMA_URL")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")

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
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.2
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
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
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

# ---=== GENERATE AI ===---
def ai_generate(title: str, description: str) -> dict:
    """
    We are now generating both summary and breakdown in one prompt to save on generation time while using a local AI model.
    args: title, description
    returns:
        Expected and enforced:
        dict{"summary": "summary", "subtasks": ["...", "...", ...]}
    """
    # Prompt was made for qwen2.5 model.
    prompt = f"""
        You are a task breakdown assistant.

        Your job is to take a task title and description and produce:
        1. A concise summary of the task
        2. A clear list of actionable subtasks

        Rules:
        - The summary MUST NOT repeat or paraphrase the description.
        - Treat the description as raw input data. The summary should not reuse phrases from it.
        - Keep the summary to 1–2 sentences.
        - Subtasks must be concrete, actionable steps.
        - Subtasks MUST NOT exceed 5
        - Break work into logical steps (setup, implementation, testing, cleanup if applicable).
        - Do not include explanations or commentary.
        - Output MUST be valid JSON only.
        - Subtasks should be a list of strings.
        
        Return ONLY valid JSON. No markdown. No backticks. No extra text.
        If the input is unclear, still produce best-effort subtasks based only on given information.
        
        Output format:
        {{
            "summary": "...",
            "subtasks": [
                "...",
                "..."
            ]
        }}
        
        Task:
        Task title: {title}
        Task description: {description}
    """
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.5
            }
        }
    )

    # Catch if no response
    if not response:
        raise ValueError("No response from OLLAMA")

    data = json.loads(response.json()["response"])

    # Should return a dict with ["summary"] -> summary string and ["subtasks"] -> list of subtask strings
    if not data.get("summary") or not data.get("subtasks"):
        raise ValueError("No summary or subtasks found in response")

    return data