# HCIProject

## Purpose
Small FastAPI service that accepts a screenshot and a short `task` string, forwards them to a configured LLM provider (or returns a mock reply), and returns text.

## Quick start
1. Initialize virtual environment: python -m venv .venv
2. Install dependencies: pip install -r requirements.txt
3. Edit .env file
4. Run server: uvicorn app:app --reload --port 8000

```
backend/
├── app.py           # FastAPI app and /api/analyze endpoint
├── llm_client.py    # Provider wrapper 
├── requirements.txt
├── .env.example
├── README.md        
```
