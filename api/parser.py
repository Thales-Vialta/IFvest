import os
import re
from typing import Dict, List, Tuple, Optional
from pypdf import PdfReader
from schemas import Question, Metadata, Content, Specification, Alternative, ComplementaryText, ComplementaryMetadata, ComplementaryContent
from cleaners import clean_exam_text

# Standard Subject Mappings
FUVEST_SUBJECT_RANGES = [
    (1, 18, "Língua Portuguesa e Literatura"),
    (19, 28, "História"),
    (29, 38, "Geografia"),
    (39, 48, "Inglês"),
    (49, 58, "Física"),
    (59, 68, "Química"),
    (69, 78, "Biologia"),
    (79, 90, "Matemática")
]

PISM_SUBJECT_RANGES = [
    (1, 5, "Língua Portuguesa"),
    (6, 10, "Geografia"),
    (11, 15, "Matemática"),
    (16, 20, "Química")
]

def get_subject_by_number(q_num: int, exam_type: str) -> str:
    """
    Returns the subject category based on the question number and exam type.
    """
    ranges = FUVEST_SUBJECT_RANGES if "FUVEST" in exam_type.upper() else PISM_SUBJECT_RANGES
    for start, end, subject in ranges:
        if start <= q_num <= end:
            return subject
    return "Interdisciplinar"

def parse_gabarito(pdf_path: str, exam_type: str) -> Dict[int, str]:
    """
    Parses a gabarito PDF and returns a dictionary mapping question number -> correct alternative.
    """
    answers = {}
    if not os.path.exists(pdf_path):
        return answers
        
    try:
        reader = PdfReader(pdf_path)
        
        if "FUVEST" in exam_type.upper():
            # For FUVEST, we check Page 2 which contains the correspondence table
            # E.g. "E 1 68 46 28" (Alternative, Q_V1, Q_V2, Q_V3, Q_V4)
            # Or Page 1 which contains direct lists like "1 E  46 C"
            # We'll use Page 2 if available, else fallback to Page 1 matches
            page_text = ""
            if len(reader.pages) > 1:
                page_text = reader.pages[1].extract_text()
                # Extract using findall with relaxed boundaries to match asterisks '*' too
                matches = re.findall(r"(?:^|\s+)([A-E\*])\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)(?:\s+(\d+))?(?:\b|$)", page_text)
                for m in matches:
                    ans = m[0]
                    q_num = int(m[1])
                    answers[q_num] = ans
            
            if not answers: # Fallback to Page 1
                page_text = reader.pages[0].extract_text()
                matches = re.findall(r"\b(\d+)\s+([A-E\*])\b", page_text)
                for num_str, ans in matches:
                    answers[int(num_str)] = ans
                    
        elif "PISM" in exam_type.upper():
            # For PISM, page 1 contains grids:
            # "Língua Portuguesa 01 02 03 04 05"
            # "A D C B A"
            # We will search for all single letters A-E and "ANULADA" following numbers
            page_text = clean_exam_text(reader.pages[0].extract_text(), "PISM")
            
            # Simple grid mapping based on PISM 2025 structure
            # Let's extract lines and match sequence of A-E or ANULADA
            lines = page_text.split("\n")
            current_subject = ""
            for idx, line in enumerate(lines):
                if "Língua Portuguesa" in line or "Geografia" in line or "Matemática" in line or "Química" in line:
                    # The next line contains the answers
                    if idx + 1 < len(lines):
                        ans_line = lines[idx+1].strip()
                        # Find all A-E or ANULADA
                        tokens = re.findall(r"\b([A-E]|ANULADA)\b", ans_line)
                        if tokens:
                            # Assign question numbers based on subject
                            start_num = 1
                            if "Geografia" in line: start_num = 6
                            elif "Matemática" in line: start_num = 11
                            elif "Química" in line: start_num = 16
                            
                            for offset, tok in enumerate(tokens):
                                answers[start_num + offset] = tok
                                
    except Exception as e:
        print(f"Error parsing gabarito {pdf_path}: {e}")
        
    return answers

def extract_questions_from_pdf(pdf_path: str, exam_type: str, year: int, booklet: str, gabarito_path: Optional[str] = None) -> Tuple[List[Question], List[ComplementaryText]]:
    """
    Parses an exam PDF and extracts structured questions and complementary texts.
    """
    questions: List[Question] = []
    comp_texts: List[ComplementaryText] = []
    
    # 1. Load Gabarito answers
    answers_key = {}
    if gabarito_path:
        answers_key = parse_gabarito(gabarito_path, exam_type)
        
    if not os.path.exists(pdf_path):
        return questions, comp_texts
        
    reader = PdfReader(pdf_path)
    
    # 2. Extract and clean full exam text
    full_text = ""
    for page in reader.pages:
        text = page.extract_text()
        cleaned = clean_exam_text(text, exam_type)
        
        # Remove headers/footers
        lines = cleaned.split("\n")
        filtered_lines = []
        for line in lines:
            if "Concurso Vestibular FUVEST" in line:
                continue
            if "Pró Reitoria de Graduação" in line or "Coordenação Geral de Processos Seletivos" in line or "Pism" in line:
                continue
            filtered_lines.append(line)
        full_text += "\n" + "\n".join(filtered_lines)
        
    # 3. Detect and Extract Complementary Texts
    # Pattern for complementary text e.g. "Texto para as questões 15 e 16" or "Leia os textos... para resolver"
    comp_pattern = r"(Texto\s+(?:comum\s+)?para\s+as\s+questões\s+(\d+)\s+e\s+(\d+).*?)(?=(?:\{|Questão|\b\d+\b\n|$))"
    comp_matches = re.finditer(comp_pattern, full_text, re.IGNORECASE | re.DOTALL)
    
    for match in comp_matches:
        full_match_text = match.group(1).strip()
        q_start = match.group(2)
        q_end = match.group(3)
        
        # Generate associated question codes
        q_codes = [f"{exam_type.upper()}_{year}_{booklet.upper()}_Q{num}" for num in range(int(q_start), int(q_end) + 1)]
        
        comp_json = ComplementaryText(
            metadados=ComplementaryMetadata(codigos_questoes=q_codes),
            conteudo=ComplementaryContent(enunciado=full_match_text, img_url=None)
        )
        comp_texts.append(comp_json)

    # 4. Split text into question blocks based on booklet type
    if "FUVEST" in exam_type.upper():
        if year in [2025, 2026]:
            split_pattern = r"\{(\d+)\}"
        else: # FUVEST 2024 uses standalone numbers
            split_pattern = r"(?:\n|^)\s*(\d+)\s*(?:\n|$)"
    else: # PISM
        split_pattern = r"(?:\n|^)\s*Questão\s*(\d+)\."

    parts = re.split(split_pattern, full_text)
    if len(parts) <= 1:
        return questions, comp_texts
        
    # 5. Build Pydantic objects from each question block
    for j in range(1, len(parts), 2):
        q_num_str = parts[j].strip()
        try:
            q_num = int(q_num_str)
        except ValueError:
            continue
            
        q_body = parts[j+1] if j+1 < len(parts) else ""
        
        # Heuristics: Skip fake splits (like page numbers or tiny text chunks)
        if len(q_body.strip()) < 50 or "(A)" not in q_body:
            continue
            
        # Separate main text from "Note e adote" (Note and adopt) section if present
        note_adote_match = re.search(r"(Note\s+e\s+adote:.*?)(?=\(([A-E])\)|\Z)", q_body, re.IGNORECASE | re.DOTALL)
        descricao_text = None
        if note_adote_match:
            descricao_text = note_adote_match.group(1).strip()
            # Remove note e adote text from body so it doesn't clutter alternatives
            q_body = q_body.replace(note_adote_match.group(1), "")
            
        # Split body into statement (enunciado) and alternatives using (A), (B), etc.
        alts_parts = re.split(r"\(([A-E])\)", q_body)
        
        enunciado_text = alts_parts[0].strip()
        
        # Parse alternatives list
        alternativas_list: List[Alternative] = []
        correct_letter = answers_key.get(q_num, "")
        
        # Build alternatives array
        for idx in range(1, len(alts_parts), 2):
            label = alts_parts[idx]
            alt_text = alts_parts[idx+1].strip() if idx+1 < len(alts_parts) else ""
            
            # Strip trailing metadata if any (like question borders or hashes)
            alt_text = re.sub(r"#####.*$", "", alt_text, flags=re.DOTALL).strip()
            
            is_correct = (label == correct_letter)
            
            alternativas_list.append(
                Alternative(
                    texto=alt_text,
                    imagem=None,
                    correta=is_correct
                )
            )
            
        # Build final Question schema
        codigo = f"{exam_type.upper()}_{year}_{booklet.upper()}_Q{q_num}"
        subject = get_subject_by_number(q_num, exam_type)
        
        tags = [exam_type, str(year), booklet]
        if correct_letter == "*" or correct_letter == "ANULADA":
            tags.append("ANULADA")
            
        question_obj = Question(
            metadados=Metadata(
                codigo=codigo,
                edital=exam_type,
                numero=q_num,
                tipo_ou_cor=booklet,
                ano=year
            ),
            conteudo=Content(
                enunciado=enunciado_text,
                descricao=descricao_text,
                Resolucao=None,
                url_img=None
            ),
            especificacao=Specification(
                materia=subject,
                tags=tags
            ),
            alternativas=alternativas_list
        )
        questions.append(question_obj)
        
    return questions, comp_texts
