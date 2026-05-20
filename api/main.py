import os
import json
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from schemas import Question, ComplementaryText

app = FastAPI(
    title="IFVest – Question Extraction API",
    description="REST API for ENEM, FUVEST and PISM Exam Question extraction, validation, storage, and retrieval.",
    version="1.0.0"
)

BASE_DIR = r"c:\Users\thale\Documents\IFvest\api"
QUESTIONS_DIR = os.path.join(BASE_DIR, "dados_processados", "questions")
COMPLEMENTARY_DIR = os.path.join(BASE_DIR, "dados_processados", "complementary")

def load_all_questions() -> List[dict]:
    questions = []
    if not os.path.exists(QUESTIONS_DIR):
        return questions
    for f in os.listdir(QUESTIONS_DIR):
        if f.endswith(".json"):
            try:
                with open(os.path.join(QUESTIONS_DIR, f), "r", encoding="utf-8") as file:
                    questions.append(json.load(file))
            except Exception:
                pass
    return questions

def load_all_complementary() -> List[dict]:
    texts = []
    if not os.path.exists(COMPLEMENTARY_DIR):
        return texts
    for f in os.listdir(COMPLEMENTARY_DIR):
        if f.endswith(".json"):
            try:
                with open(os.path.join(COMPLEMENTARY_DIR, f), "r", encoding="utf-8") as file:
                    texts.append(json.load(file))
            except Exception:
                pass
    return texts

@app.get("/", response_class=HTMLResponse)
def read_root():
    # Return a premium HTML page to wow the user
    return """
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>IFVest API</title>
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap" rel="stylesheet">
        <style>
            body {
                margin: 0;
                font-family: 'Outfit', sans-serif;
                background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
                color: #f8fafc;
                min-height: 100vh;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
            }
            .card {
                background: rgba(255, 255, 255, 0.05);
                backdrop-filter: blur(16px);
                border: 1px rgba(255, 255, 255, 0.1) solid;
                border-radius: 24px;
                padding: 48px;
                max-width: 650px;
                text-align: center;
                box-shadow: 0 20px 50px rgba(0,0,0,0.3);
            }
            h1 {
                font-size: 2.8rem;
                margin-bottom: 8px;
                background: linear-gradient(90deg, #38bdf8, #818cf8);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            p {
                color: #cbd5e1;
                font-size: 1.15rem;
                line-height: 1.6;
            }
            .badge {
                display: inline-block;
                background: rgba(56, 189, 248, 0.15);
                color: #38bdf8;
                border: 1px solid rgba(56, 189, 248, 0.3);
                padding: 6px 16px;
                border-radius: 50px;
                font-size: 0.9rem;
                font-weight: 600;
                margin-bottom: 24px;
            }
            .btn-group {
                margin-top: 36px;
                display: flex;
                gap: 16px;
                justify-content: center;
            }
            .btn {
                padding: 12px 28px;
                border-radius: 12px;
                font-weight: 600;
                text-decoration: none;
                transition: all 0.2s ease;
            }
            .btn-primary {
                background: #4f46e5;
                color: #ffffff;
                box-shadow: 0 4px 15px rgba(79, 70, 229, 0.4);
            }
            .btn-primary:hover {
                background: #4338ca;
                transform: translateY(-2px);
            }
            .btn-secondary {
                background: rgba(255,255,255,0.08);
                color: #f1f5f9;
                border: 1px solid rgba(255,255,255,0.15);
            }
            .btn-secondary:hover {
                background: rgba(255,255,255,0.15);
                transform: translateY(-2px);
            }
        </style>
    </head>
    <body>
        <div class="card">
            <span class="badge">API Pronta para Uso</span>
            <h1>IFVest Question Extraction</h1>
            <p>REST API desenvolvida em Python com FastAPI e Pydantic para ingestão, limpeza de caracteres, segmentação e busca estruturada de questões de vestibulares (FUVEST, PISM, ENEM).</p>
            <div class="btn-group">
                <a href="/docs" class="btn btn-primary">Ver Documentação (Swagger)</a>
                <a href="/questions" class="btn btn-secondary">Explorar Questões (JSON)</a>
            </div>
        </div>
    </body>
    </html>
    """

@app.get("/questions", response_model=List[Question])
def list_questions(
    edital: Optional[str] = Query(None, description="Filtrar por edital (ex: FUVEST, PISM)"),
    ano: Optional[int] = Query(None, description="Filtrar por ano (ex: 2026, 2025)"),
    materia: Optional[str] = Query(None, description="Filtrar por matéria (ex: Matemática, Química)"),
    busca: Optional[str] = Query(None, description="Procura de palavras-chaves no enunciado")
):
    """
    Returns a list of all parsed questions, with flexible query filtering.
    """
    all_q = load_all_questions()
    filtered = []
    
    for q in all_q:
        # Filter by edital
        if edital and q["metadados"]["edital"].upper() != edital.upper():
            continue
        # Filter by ano
        if ano and q["metadados"]["ano"] != ano:
            continue
        # Filter by materia
        if materia and materia.lower() not in q["especificacao"]["materia"].lower():
            continue
        # Search keyword in enunciado
        if busca and busca.lower() not in q["conteudo"]["enunciado"].lower():
            continue
            
        filtered.append(q)
        
    return filtered

@app.get("/questions/{codigo}", response_model=Question)
def get_question(codigo: str):
    """
    Retrieves a single question by its unique identifier code (e.g. FUVEST_2026_V1_Q11).
    """
    filepath = os.path.join(QUESTIONS_DIR, f"{codigo}.json")
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail=f"Question with code {codigo} not found.")
    with open(filepath, "r", encoding="utf-8") as file:
        return json.load(file)

@app.get("/complementary", response_model=List[ComplementaryText])
def list_complementary():
    """
    Returns all shared/complementary texts found in the exams.
    """
    return load_all_complementary()

@app.get("/stats")
def get_stats():
    """
    Returns high-level statistics about the ingested and processed questions database.
    """
    all_q = load_all_questions()
    total = len(all_q)
    
    # Counts by edital and year
    by_edital = {}
    by_year = {}
    by_subject = {}
    
    for q in all_q:
        ed = q["metadados"]["edital"]
        yr = q["metadados"]["ano"]
        sub = q["especificacao"]["materia"]
        
        by_edital[ed] = by_edital.get(ed, 0) + 1
        by_year[yr] = by_year.get(yr, 0) + 1
        by_subject[sub] = by_subject.get(sub, 0) + 1
        
    return {
        "status": "online",
        "total_questoes_processadas": total,
        "por_edital": by_edital,
        "por_ano": by_year,
        "por_materia": by_subject
    }
