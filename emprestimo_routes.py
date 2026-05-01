from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_
from dependencies import pegar_sessao, verificar_admin, verificar_token
from models import Usuarios, Emprestimos, Livros
from datetime import datetime, timedelta

emprestimo_router = APIRouter(prefix='/emprestimos', tags=['emprestimo'])

def formatar_emprestimo(e: Emprestimos):
    return {
        "id": e.id,
        "livro_id": e.id_livro,
        "livro": e.livro.titulo,
        "usuario": e.usuario.nome,
        "usuario_id": e.id_usuario,
        "status": e.status,
        "data_emprestimo": e.data_emprestimo.strftime("%d/%m/%Y %H:%M"),
        "data_devolucao_prevista": e.data_devolucao_prevista.strftime("%d/%m/%Y %H:%M") if e.data_devolucao_prevista else None,
        "data_devolucao_real": e.data_devolucao_real.strftime("%d/%m/%Y %H:%M") if e.data_devolucao_real else None
    }

def formatar_emprestimo_atrasado(e: Emprestimos):
    dias_atrasados = (datetime.utcnow() - e.data_devolucao_prevista).days 
    return {
        "id": e.id,
        "livro_id": e.id_livro,
        "usuario_id": e.id_usuario,
        "livro": e.livro.titulo,
        "usuario": e.usuario.nome,
        "status": e.status,
        "data_emprestimo": e.data_emprestimo.strftime("%d/%m/%Y %H:%M"),
        "data_devolucao_prevista": e.data_devolucao_prevista.strftime("%d/%m/%Y %H:%M") if e.data_devolucao_prevista else None,
        'dias_atrasado': dias_atrasados,
        'multa': float(dias_atrasados)
    }


@emprestimo_router.get('/listar_emprestimos_usuario_logado')
async def listar_usuario_logado(usuario: Usuarios = Depends(verificar_token), session: Session = Depends(pegar_sessao)):
    '''
    Rota da API usada para listar todos os emprestimos do usuario que está logado
    '''
    emprestimos = session.query(Emprestimos).filter(Emprestimos.id_usuario==usuario.id).all()
    if not emprestimos:
        return {'message': 'Você não possui emprestimos ainda'}
    return {
        'message': 'Sucesso ao listar os seus emprestimos',
        'emprestimos': [formatar_emprestimo(e) for e in emprestimos]
    }

@emprestimo_router.get('/ativos_logado')
async def listar_usuario_logado(usuario: Usuarios = Depends(verificar_token), session: Session = Depends(pegar_sessao)):
    '''
    Rota da API usada para listar todos os emprestimos do usuario que está logado
    '''
    emprestimos = session.query(Emprestimos).filter(and_(Emprestimos.id_usuario==usuario.id, Emprestimos.status=='ativo')).all()
    if not emprestimos:
        return {'message': 'Você não possui emprestimos ainda'}
    return {
        'message': 'Sucesso ao listar os seus emprestimos',
        'emprestimos': [formatar_emprestimo(e) for e in emprestimos]
    }

@emprestimo_router.get('/listar_todos_emprestimos')
async def listar_todos_emprestimos(usuario: Usuarios = Depends(verificar_admin), session: Session = Depends(pegar_sessao)):
    '''
    Rota da API usada para listar todos os emprestimos de todos os usuarios
    '''
    emprestimos = session.query(Emprestimos).all()
    return {
        'message': 'Sucesso ao listar emprestimos',
        'emprestimos': [formatar_emprestimo(e) for e in emprestimos]
    }

@emprestimo_router.get('/listar_emprestimos_ativos')
async def listar_emprestimos_ativos(usuario: Usuarios = Depends(verificar_admin), session: Session = Depends(pegar_sessao)):
    '''
    Rota da API usada para listar todos os emprestimos ativos(somente admins)
    '''
    emprestimos = session.query(Emprestimos).filter(Emprestimos.status=='ativo').all()
    if not emprestimos:
        return {"message": "não existe nenhum emprestimo ativo agora"}
    return {
        'message': 'Sucesso ao proucurar emprestimos ativos',
        'emprestimos_ativos': [formatar_emprestimo(e) for e in emprestimos]
    }

@emprestimo_router.get('/emprestimos_usuario/{usuario_id}')
async def listar_emprestimos_de_alguem(usuario_id: int, usuario: Usuarios = Depends(verificar_admin), session: Session = Depends(pegar_sessao)):
    '''
    Rota da API usada para listar emprestimos de alguem em especifico(somente admins)
    '''
    usuario_emprestimo = session.query(Usuarios).filter(Usuarios.id==usuario_id).first()
    if not usuario_emprestimo:
        raise HTTPException(status_code=404, detail='Usuário não existente')
    emprestimos = session.query(Emprestimos).filter(Emprestimos.id_usuario==usuario_id).all()
    if not emprestimos:
        return {'detail': f'O usuário {usuario_emprestimo.nome} não possui emprestimos'}
    return {
        'message': f'Sucesso ao buscar emprestimos de {usuario_emprestimo.nome}',
        'emprestimos': [formatar_emprestimo(e) for e in emprestimos]
    }

@emprestimo_router.get('/emprestimos_livro/{livro_titulo}')
async def listar_emprestimos_de_livro(livro_titulo: str, usuario: Usuarios = Depends(verificar_admin), session: Session = Depends(pegar_sessao)):
    '''
    Rota da API usada para listar emprestimos de algum livro em especifico(somente admins)
    '''
    livro_emprestado = session.query(Livros).filter(Livros.titulo.ilike(f'{livro_titulo}%')).first()
    if not livro_emprestado:
        raise HTTPException(status_code=404, detail='Livro não existente')
    emprestimos = session.query(Emprestimos).filter(Emprestimos.id_livro==livro_emprestado.id).all()
    if not emprestimos:
        return {'detail': f'O livro {livro_emprestado.titulo} não possui emprestimos'}
    return {
        'emprestimos': [formatar_emprestimo(e) for e in emprestimos]
    }

@emprestimo_router.get('/listar_atrasados')
async def listar_atrasados(session: Session = Depends(pegar_sessao), usuario: Usuarios = Depends(verificar_admin)):
    '''
    Rota da API usada para listar todos os emprestimos que estão atrasados
    '''
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
        'emprestimos_atrasados': [formatar_emprestimo_atrasado(e) for e in emprestimos]
    }

@emprestimo_router.post('/seus_emprestimo')
async def seus_emprestimos(session: Session = Depends(pegar_sessao), usuario: Usuarios = Depends(verificar_token)):
    '''
    Rota da API usada para listar todos os emprestimos
    '''
    emprestimos = session.query(Emprestimos).filter(Emprestimos.id_usuario==usuario.id).all()
    if not emprestimos:
        return {'message': 'você não possui nenhum emprestimo'}
    return {
        'emprestimos': [formatar_emprestimo(e) for e in emprestimos]
    }
    

@emprestimo_router.post('/renovar_emprestimo/{emprestimo_id}')
async def renovar_emprestimo(emprestimo_id: int, session: Session = Depends(pegar_sessao), usuario: Usuarios = Depends(verificar_token)):
    '''
    Rota da API usada para renovar emprestimos
    '''
    emprestimo = session.query(Emprestimos).filter(and_(Emprestimos.id==emprestimo_id, Emprestimos.id_usuario==usuario.id)).first()
    if not emprestimo:
        raise HTTPException(status_code=404, detail='emprestimo inexistente')
    if emprestimo.status == 'devolvido':
        raise HTTPException(status_code=400, detail='emprestimo já devolvido')
    if emprestimo.vezes_renovado >= 3:
        raise HTTPException(status_code=400, detail='Você excedeu o número de vezes que se pode renovar o emprestimo')
        
    nova_vezes_renovado = emprestimo.vezes_renovado + 1
    emprestimo.vezes_renovado = nova_vezes_renovado
    nova_data = datetime.utcnow() + timedelta(days=10)
    emprestimo.data_devolucao_prevista = nova_data
    if emprestimo.status == 'atrasado':
        emprestimo.status = 'ativo'
    session.commit()
    emprestimo = session.query(Emprestimos).filter(and_(Emprestimos.id==emprestimo_id, Emprestimos.id_usuario==usuario.id)).first()
    return {
        'detail': f'Sucesso ao renovar o emprestimo, nova data de devolução: {nova_data.strftime("%d/%m/%Y")}',
        'message': f'Sucesso ao renovar o emprestimo, nova data de devolução: {nova_data.strftime("%d/%m/%Y")}',
        'vezes_renovado': nova_vezes_renovado
    }



    