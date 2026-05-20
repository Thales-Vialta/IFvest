import os
import json
from parser import extract_questions_from_pdf

# Configured exams mapping
EXAMS_TO_PROCESS = [
    {
        "pdf": "fuvest2026-fase1-prova-V1.pdf",
        "gabarito": "fuvest2026-fase1-gabarito.pdf",
        "type": "FUVEST",
        "year": 2026,
        "booklet": "V1"
    },
    {
        "pdf": "fuvest2025_primeira_fase_prova_V1.pdf",
        "gabarito": "fuvest2025_gabarito_primeira_fase.pdf",
        "type": "FUVEST",
        "year": 2025,
        "booklet": "V1"
    },
    {
        "pdf": "fuvest2024_primeira_fase_prova_V.pdf",
        "gabarito": "fuvest2024_gabarito_primeira_fase_retificado_2023-11-24.pdf",
        "type": "FUVEST",
        "year": 2024,
        "booklet": "V"
    },
    {
        "pdf": "Pism-1-Dia-1.pdf",
        "gabarito": "GABARITO-PISM-2025-OBJETIVA-D1-P1-NF.pdf",
        "type": "PISM",
        "year": 2025,
        "booklet": "D1-P1"
    }
]

def main():
    base_dir = r"c:\Users\thale\Documents\IFvest\api"
    processed_dir = os.path.join(base_dir, "dados_processados")
    questions_dir = os.path.join(processed_dir, "questions")
    complementary_dir = os.path.join(processed_dir, "complementary")
    
    # Create target directories
    os.makedirs(questions_dir, exist_ok=True)
    os.makedirs(complementary_dir, exist_ok=True)
    
    print("==================================================")
    print("      IFVest Question Extraction Pipeline         ")
    print("==================================================")
    
    summary_report = []
    
    for exam in EXAMS_TO_PROCESS:
        pdf_path = os.path.join(base_dir, "provas", exam["pdf"])
        gabarito_path = os.path.join(base_dir, "provas", exam["gabarito"])
        
        if not os.path.exists(pdf_path):
            print(f"[Warning] PDF file {exam['pdf']} not found in 'provas' directory. Skipping.")
            continue
            
        print(f"\nProcessing {exam['type']} {exam['year']} (Booklet: {exam['booklet']})...")
        
        # Run the parsing engine
        questions, comp_texts = extract_questions_from_pdf(
            pdf_path=pdf_path,
            exam_type=exam["type"],
            year=exam["year"],
            booklet=exam["booklet"],
            gabarito_path=gabarito_path
        )
        
        # Save individual questions JSONs
        saved_q_count = 0
        for q in questions:
            # We dump using standard python json serializer from the Pydantic dump_model
            filename = f"{q.metadados.codigo}.json"
            filepath = os.path.join(questions_dir, filename)
            
            # Serialize using Pydantic's model_dump
            q_data = q.model_dump()
            
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(q_data, f, ensure_ascii=False, indent=2)
            saved_q_count += 1
            
        # Save complementary text JSONs
        saved_comp_count = 0
        for idx, ct in enumerate(comp_texts):
            # Generate a consistent hash or sequential code
            comp_code = f"{exam['type']}_{exam['year']}_{exam['booklet']}_COMP_{idx+1}"
            filename = f"{comp_code}.json"
            filepath = os.path.join(complementary_dir, filename)
            
            ct_data = ct.model_dump()
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(ct_data, f, ensure_ascii=False, indent=2)
            saved_comp_count += 1
            
        print(f"  -> Extracted & Validated: {len(questions)} questions.")
        print(f"  -> Saved {saved_q_count} individual question JSONs.")
        print(f"  -> Saved {saved_comp_count} complementary text JSONs.")
        
        summary_report.append({
            "exam": f"{exam['type']} {exam['year']} ({exam['booklet']})",
            "questions": saved_q_count,
            "complementary": saved_comp_count
        })
        
    print("\n==================================================")
    print("               Pipeline Execution Report          ")
    print("==================================================")
    total_q = 0
    total_c = 0
    for r in summary_report:
        print(f" - {r['exam']}: {r['questions']} questions, {r['complementary']} shared texts saved.")
        total_q += r['questions']
        total_c += r['complementary']
    print(f"\nPipeline successfully finished. Total saved: {total_q} questions, {total_c} texts.")
    print(f"Location: {processed_dir}")
    print("==================================================")

if __name__ == "__main__":
    main()
