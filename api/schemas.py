from pydantic import BaseModel, Field
from typing import List, Optional

class Metadata(BaseModel):
    codigo: str = Field(..., description="Unique code for the question, e.g. FUVEST_2026_V1_Q11")
    edital: str = Field(..., description="Exam publisher or category, e.g. ENEM, FUVEST, PISM")
    numero: int = Field(..., description="Question number in the exam booklet")
    tipo_ou_cor: str = Field(..., description="Exams version, color, or booklet type, e.g. V1, AZUL")
    ano: int = Field(..., description="Year of the exam")

class Content(BaseModel):
    enunciado: str = Field(..., description="The main text body/question description")
    descricao: Optional[str] = Field(None, description="Optional extra description or contextual notes")
    dica: Optional[str] = Field(None, description="Optional tip or hint for solving the question")
    url_img: Optional[str] = Field(None, description="Optional URL or local path to associated main image")

class Specification(BaseModel):
    materia: str = Field(..., description="Subject category, e.g. Matemática, Português")
    tags: List[str] = Field(default_factory=list, description="Associated content tags, e.g. Algebra, Sintaxe")

class Alternative(BaseModel):
    texto: str = Field(..., description="The text of the alternative")
    imagem: Optional[str] = Field(None, description="Optional image URL or path for this alternative")
    correta: bool = Field(..., description="Whether this is the correct alternative")

class Question(BaseModel):
    metadados: Metadata
    conteudo: Content
    especificacao: Specification
    alternativas: List[Alternative]

class ComplementaryMetadata(BaseModel):
    codigos_questoes: List[str] = Field(..., description="List of question codes that share this complementary text")

class ComplementaryContent(BaseModel):
    enunciado: str = Field(..., description="The shared complementary text body")
    img_url: Optional[str] = Field(None, description="Optional image URL or path associated with this text")

class ComplementaryText(BaseModel):
    metadados: ComplementaryMetadata
    conteudo: ComplementaryContent
