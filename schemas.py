from pydantic import BaseModel

class UsuarioSchema(BaseModel):
    nome: str
    email: str
    senha: str
    admin: bool

    class Config:
        from_attributes = True

class LoginSchema(BaseModel):
    email: str
    senha: str

    class Config:
        from_attributes = True

class LivroSchema(BaseModel):
    titulo: str
    autor: str
    descricao: str
    isbn: str
    categoria: str
    quantidade_disponivel: int

    class Config:
        from_attributes = True