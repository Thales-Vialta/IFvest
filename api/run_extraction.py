import os
import json
from parser import extract_questions_from_pdf
import re 

def detectar_prova(prova_dir):
    pdfs = [f for f in os.listdir(provas_dir) if f.lower().endswith(".pdf")]
    prova = []
    listaP = [p for p in pdfs if "gabarito" not in p.lower()]
    gabarito = [g for g in pdfs if "gabarito" in p.lower()]
    for provas in provas: 
        nome = provas.lower()
        if "fuvest" in nome: 
            exam_type = "FUVEST"
        elif "pism" in nome: 
            exam_type = "PISM"
        else:
            print(f"[SKIP] Tipo não encontrado da: {prova}")
            continue
            year_match = re.search(r"(20\d{2})", nome)
        if not year_match:
            print(f"[SKIP] Ano não encontrado: {prova}")
            continue

        year = int(year_match.group(1))
        booklet_match = re.search(r"(v\d+|v|d\d-p\d)", nome)
        booklet = booklet_match.group(1).upper() if booklet_match else "Banca desconhecida"
        matched_gabarito = None

        for gab in gabaritos:
            gab_lower = gab.lower()
            if (exam_type.lower() in gab_lower and str(year) in gab_lower and booklet.lower() in gab_lower):
                matched_gabarito = gab
                break
        exams.append({
            "pdf": prova,
            "gabarito": matched_gabarito,
            "type": exam_type,
            "year": year,
            "booklet": booklet
        })
    return exams
def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    processed_dir = os.path.join(base_dir, "dados_processados")
    provas_dir=os.path.join(base_dir, "provas")
    questions_dir = os.path.join(processed_dir, "questions")
    complementary_dir = os.path.join(processed_dir, "complementary")
    os.makedirs(questions_dir, exist_ok=True)
    os.makedirs(complementary_dir, exist_ok=True)
    
    summary_report=[]
    
    EXAMS_TO_PROCESS = detect_exams(provas_dir)

    print(f"\n[INFO] {len(EXAMS_TO_PROCESS)} provas detectadas automaticamente.\n")

    for exam in EXAMS_TO_PROCESS:
        pdf_path = os.path.join(base_dir, "provas", exam["pdf"])
        gabarito_path = os.path.join(base_dir, "provas", exam["gabarito"])
        
        if not os.path.exists(pdf_path):
            print(f"[Warning] PDF {exam['pdf']} não encontrado in 'provas' directory. Skipping.")
            continue
            
        print(f"\nProcessing {exam['type']} {exam['year']} (Booklet: {exam['booklet']})...")

        questions, comp_texts = extract_questions_from_pdf(
            pdf_path=pdf_path,
            exam_type=exam["type"],
            year=exam["year"],
            booklet=exam["booklet"],
            gabarito_path=gabarito_path
        )

        saved_q_count = 0
        for q in questions:
            filename = f"{q.metadados.codigo}.json"
            filepath = os.path.join(questions_dir, filename)
            
            q_data = q.model_dump()
            
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(q_data, f, ensure_ascii=False, indent=2)
            saved_q_count += 1
            
        saved_comp_count = 0
        for idx, ct in enumerate(comp_texts):
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
        
    print("Retorno da Extração")
    total_q = 0
    total_c = 0
    for r in summary_report:
        print(f" - {r['exam']}: {r['questions']} questions, {r['complementary']} shared texts saved.")
        total_q += r['questions']
        total_c += r['complementary']
    print(f"\nArquivo totalmente extraído. Total saved: {total_q} Questões, {total_c} textos.")
    print(f"Salvo em: {processed_dir}")

if __name__ == "__main__":
    main()
