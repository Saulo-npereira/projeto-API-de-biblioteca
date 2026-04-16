from fastapi import APIRouter, Depends, HTTPException
from schemas import LivroSchema
from sqlalchemy.orm import Session
from dependencies import pegar_sessao, verificar_admin
from models import Livros, Usuarios

biblioteca_router = APIRouter(prefix='/bibliotecas', tags=['biblioteca'])


@biblioteca_router.post('/adicionar_livro')
async def adicionar_livro(livro_schema: LivroSchema, session: Session = Depends(pegar_sessao), usuario: Usuarios = Depends(verificar_admin)):
    livro = session.query(Livros).filter(Livros.titulo==livro_schema.titulo).first()
    if livro:
        raise HTTPException(status_code=400, detail='Já existe esse livro')
    livro = Livros(titulo=livro_schema.titulo, autor=livro_schema.autor, descricao=livro_schema.descricao,
                    isbn=livro_schema.isbn, quantidade_disponivel=livro_schema.quantidade_disponivel, categoria=livro_schema.categoria)
    session.add(livro)
    session.commit()
    livro = session.query(Livros).filter(Livros.titulo==livro_schema.titulo).first()
    return {
        'message': f'Livro adicionado com sucesso pelo usuario {usuario.nome}',
        'livro': livro
    }

@biblioteca_router.get('/listar_livros')
async def listar_livros(session: Session = Depends(pegar_sessao)):
    livros = session.query(Livros).all()
    return {
        'livros': livros
    }

@biblioteca_router.delete('/deletar_livro/{id_livro}')
async def deletar_livro(id_livro: int, session: Session = Depends(pegar_sessao), usuario: Usuarios = Depends(verificar_admin)):
    livro = session.query(Livros).filter(Livros.id==id_livro).first()
    session.delete(livro)
    session.commit()
    return {
        'message': 'livro deletado com sucesso',
        'livro': livro
    }

@biblioteca_router.get('/buscar_livro_id')
async def buscar_livro_por_id(id_livro: int, session: Session = Depends(pegar_sessao)):
    livro = session.query(Livros).filter(Livros.id==id_livro).first()
    if not livro:
        raise HTTPException(status_code=404, detail='livro não encontrado')
    return {
        'message': 'livro encontrado com sucesso',
        'livro': livro
    }

@biblioteca_router.get('/buscar_livro_isbn')
async def buscar_livro_por_isbn(isbn_livro: str, session: Session = Depends(pegar_sessao)):
    livro = session.query(Livros).filter(Livros.isbn==isbn_livro).first()
    if not livro:
        raise HTTPException(status_code=404, detail='livro não encontrado')
    return {
        'message': 'livro encontrado com sucesso',
        'livro': livro
    }

@biblioteca_router.get('/buscar_livro_titulo')
async def buscar_livro_por_titulo(titulo_livro: str, session: Session = Depends(pegar_sessao)):
    livro = session.query(Livros).filter(Livros.titulo==titulo_livro).first()
    if not livro:
        raise HTTPException(status_code=404, detail='livro não encontrado')
    return {
        'message': 'livro encontrado com sucesso',
        'livro': livro
    }