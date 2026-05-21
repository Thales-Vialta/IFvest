from pydantic import BaseModel, Field
from typing import List, Optional

class Metadata(BaseModel):
    codigo: str = Field(..., description="Código do vestibular, ex: FUVEST_2026_V1_Q11")
    edital: str = Field(..., description=",Banca ex: ENEM, FUVEST, PISM")
    numero: int = Field(..., description="Número da questão")
    tipo_ou_cor: str = Field(..., description="tipo do caderno que foi escaneado, ex: V1, AZUL")
    ano: int = Field(..., description="Ano da aplicação do vestibular")

class Content(BaseModel):
    enunciado: str = Field(..., description="enunciado")
    descricao: Optional[str] = Field(None, description="Anotações opcionais")
    dica: Optional[str] = Field(None, description="dica para o aluno enquanto faz a questão, atribuido como opcional")
    url_img: Optional[str] = Field(None, description="url para a imagem salva para algumas questões")

class Specification(BaseModel):
    materia: str = Field(..., description="Matéria da questão, ex: Matemática, História")
    tags: List[str] = Field(default_factory=list, description="Conteúdo atrelado a matéria aplicada. Ex: Reino Monera, Idade Média(476-1453)")

class Alternative(BaseModel):
    texto: str = Field(..., description="Texto da alternativa")
    imagem: Optional[str] = Field(None, description="URL da imagem para provas com gráficos")
    correta: bool = Field(..., description="Valor da alternativa")

class Question(BaseModel):
    metadados: Metadata
    conteudo: Content
    especificacao: Specification
    alternativas: List[Alternative]

class ComplementaryMetadata(BaseModel):
    codigos_questoes: List[str] = Field(..., description="List of question codes that share this complementary text")

class ComplementaryContent(BaseModel):
    enunciado: str = Field(..., description="Texto compartilhado para mais de uma questão")
    img_url: Optional[str] = Field(None, description="Imagem ou figura atrelada ao texto")

class ComplementaryText(BaseModel):
    metadados: ComplementaryMetadata
    conteudo: ComplementaryContent
