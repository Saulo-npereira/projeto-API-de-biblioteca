from fastapi import APIRouter, Depends, HTTPException
from schemas import LivroSchema
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from dependencies import pegar_sessao, verificar_admin, verificar_token
from models import Livros, Usuarios, Emprestimos
from datetime import datetime, timedelta

biblioteca_router = APIRouter(prefix='/bibliotecas', tags=['biblioteca'])

def formatar_emprestimo(e):
    return {
        "id": e.id,
        "livro_id": e.id_livro,
        "usuario_id": e.id_usuario,
        "status": e.status,
        "data_emprestimo": e.data_emprestimo.strftime("%d/%m/%Y %H:%M"),
        "data_devolucao_prevista": e.data_devolucao_prevista.strftime("%d/%m/%Y %H:%M") if e.data_devolucao_prevista else None,
        "data_devolucao_real": e.data_devolucao_real.strftime("%d/%m/%Y %H:%M") if e.data_devolucao_real else None
    }

def detectar_atraso(data_prevista, data_agora = datetime.utcnow()):
    if data_prevista < data_agora:
        return True
    return False



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

@biblioteca_router.post('/editar_estoque/{id_livro}/{quantidade}')
async def editar_estoque(id_livro: int, quantidade: int, usuario: Usuarios = Depends(verificar_admin), session: Session = Depends(pegar_sessao)):
    livro = session.query(Livros).filter(Livros.id==id_livro).first()
    novo_estoque = livro.quantidade_disponivel + quantidade
    if novo_estoque < 0:
        raise HTTPException(status_code=400, detail='O estoque não pode ser menor que 0')
    livro.quantidade_disponivel = novo_estoque
    session.commit()
    return {
        'message': f'estoque do livro {livro.titulo} atualizado com sucesso'
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

@biblioteca_router.post('/pegar_emprestado/{id_livro}')
async def pegar_emprestado(id_livro: int, session: Session = Depends(pegar_sessao), usuario: Usuarios = Depends(verificar_token)):
    usuario_emprestimos_ativos = session.query(Emprestimos).filter(and_(Emprestimos.id_usuario==usuario.id, or_(Emprestimos.status=='ativo', Emprestimos.status=='atrasado'))).count()
    if usuario_emprestimos_ativos >= 3:
        raise HTTPException(status_code=400, detail='Você já possui 3 emprestimos não devolvidos')
    emprestimo_existe = session.query(Emprestimos).filter(
        Emprestimos.id_usuario==usuario.id,
        Emprestimos.id_livro==id_livro,
        Emprestimos.status=='ativo'
    ).first()
    if emprestimo_existe:
        raise HTTPException(status_code=401, detail='Você já pegou esse livro emprestado')
    livro = session.query(Livros).filter(Livros.id==id_livro).first()
    if not livro:
        raise HTTPException(status_code=400, detail='Não possuimos esse livro')
    if livro.quantidade_disponivel < 1:
        raise HTTPException(status_code=400, detail='Este livro está fora do estoque')
    livro.quantidade_disponivel -= 1
    data_devolucao = datetime.utcnow() + timedelta(days=10)
    emprestimo = Emprestimos(id_usuario=usuario.id, id_livro=id_livro, data_devolucao_prevista=data_devolucao)
    session.add(emprestimo)
    session.commit()
    return {
        'message': f'livro {livro.titulo} emprestado com sucesso para o usuario {usuario.nome}',
        'data_devolucao': data_devolucao.strftime("%d/%m/%Y %H:%M")
    }

@biblioteca_router.post('/devolver_livro/{id_livro}')
async def devolver_livro(id_livro: int, usuario: Usuarios = Depends(verificar_token), session: Session = Depends(pegar_sessao)):
    livro = session.query(Livros).filter(Livros.id==id_livro).first()
    if not livro:
        raise HTTPException(status_code=400, detail='Não existe esse livro')
    emprestimo = session.query(Emprestimos).filter(
        Emprestimos.id_livro == id_livro,
        Emprestimos.id_usuario == usuario.id,
        or_(Emprestimos.status == 'ativo', Emprestimos.status == 'atrasado')
    ).first()
    if not emprestimo:
        raise HTTPException(status_code=400, detail='Você ainda não pegou esse livro emprestado')

    livro.quantidade_disponivel += 1
    emprestimo.status = 'devolvido'
    emprestimo.data_devolucao_real = datetime.utcnow()
    session.commit()

    return {
        'message': f'usuario {usuario.nome} devolveu o livro {livro.titulo} com sucesso'
    }

@biblioteca_router.get('/listar_emprestimos_usuario_logado')
async def listar_usuario_logado(usuario: Usuarios = Depends(verificar_token), session: Session = Depends(pegar_sessao)):
    emprestimos = session.query(Emprestimos).filter(Emprestimos.id_usuario==usuario.id).all()
    if not emprestimos:
        return {'message': 'Você não possui emprestimos ainda'}
    return {
        'message': 'Sucesso ao listar os seus emprestimos',
        'emprestimos': [formatar_emprestimo(e) for e in emprestimos]
    }

@biblioteca_router.get('/listar_todos_emprestimos')
async def listar_todos_emprestimos(usuario: Usuarios = Depends(verificar_admin), session: Session = Depends(pegar_sessao)):
    emprestimos = session.query(Emprestimos).all()
    return {
        'message': 'Sucesso ao listar emprestimos',
        'emprestimos': [formatar_emprestimo(e) for e in emprestimos]
    }

@biblioteca_router.get('/listar_emprestimos_ativos')
async def listar_emprestimos_ativos(usuario: Usuarios = Depends(verificar_admin), session: Session = Depends(pegar_sessao)):
    emprestimos = session.query(Emprestimos).filter(Emprestimos.status=='ativo').all()
    if not emprestimos:
        return {"message": "não existe nenhum emprestimo ativo agora"}
    return {
        'message': 'Sucesso ao proucurar emprestimos ativos',
        'emprestimos_ativos': [formatar_emprestimo(e) for e in emprestimos]
    }

@biblioteca_router.get('/listar_emprestimos_de_alguem')
async def listar_emprestimos_de_alguem(usuario_id: int, usuario: Usuarios = Depends(verificar_admin), session: Session = Depends(pegar_sessao)):
    usuario_emprestimo = session.query(Usuarios).filter(Usuarios.id==usuario_id).first()
    if not usuario_emprestimo:
        raise HTTPException(status_code=404, detail='Usuário não existente')
    emprestimos = session.query(Emprestimos).filter(Emprestimos.id_usuario==usuario_id).all()
    if not emprestimos:
        return {'message': f'O usuário {usuario_emprestimo.nome} não possui emprestimos'}
    return {
        'message': f'Sucesso ao buscar emprestimos de {usuario_emprestimo.nome}',
        'emprestimos': [formatar_emprestimo(e) for e in emprestimos]
    }

@biblioteca_router.get('/listar_atrasados')
async def listar_atrasados(session: Session = Depends(pegar_sessao), usuario: Usuarios = Depends(verificar_admin)):
    session.query(Emprestimos).filter(
    Emprestimos.status == "ativo",
    Emprestimos.data_devolucao_prevista < datetime.utcnow()
).update(
    {"status": "atrasado"},
    synchronize_session=False
)
    session.commit()
    emprestimos = session.query(Emprestimos).filter(Emprestimos.status=='atrasado').all()
    if not emprestimos:
        return {'message': 'não possui nenhum emprestimo atrasado'}
    return {
        'emprestimos_atrasados': [formatar_emprestimo(e) for e in emprestimos]
    }
    