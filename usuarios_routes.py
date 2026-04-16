from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from schemas import UsuarioSchema, LoginSchema
from sqlalchemy.orm import Session
from dependencies import pegar_sessao, verificar_token, verificar_admin
from models import Usuarios
from utils import gerar_hash, autenticar_usuario, gerar_token
from datetime import timedelta
from security import oauth2_scheme
usuarios_router = APIRouter(prefix='/usuarios', tags=['usuario'])

@usuarios_router.post('/criar_usuario')
async def criar_usuario(usuario_schema: UsuarioSchema, session: Session = Depends(pegar_sessao)):
    usuario = session.query(Usuarios).filter(Usuarios.email==usuario_schema.email).first()
    if usuario:
        raise HTTPException(status_code=400, detail='Já existe um usuario com esse email')
    usuario = Usuarios(
        nome=usuario_schema.nome,
        email=usuario_schema.email,
        senha=gerar_hash(usuario_schema.senha),
        admin=usuario_schema.admin
    )
    session.add(usuario)
    session.commit()
    usuario = session.query(Usuarios).filter(Usuarios.email==usuario_schema.email).first()
    return {
        'message': 'usuario criado com sucesso',
        'usuario': usuario
    }

@usuarios_router.post('/login')
async def login(login_schema: LoginSchema, session: Session = Depends(pegar_sessao)):
    usuario = autenticar_usuario(login_schema.email, login_schema.senha, session)
    if not usuario:
        raise HTTPException(status_code=404, detail='Usuario não encontrado')
    
    dados = {'sub': usuario.email}
    access_token = gerar_token(dados)
    refresh_token = gerar_token(dados, timedelta(days=1))
    return {
        'message': 'Login feito com sucesso',
        'access_token': access_token,
        'refresh_token': refresh_token
    }

@usuarios_router.post('/login-form')
async def login_form(login_schema: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(pegar_sessao)):
    usuario = autenticar_usuario(login_schema.username, login_schema.password, session)
    if not usuario:
        raise HTTPException(status_code=404, detail='Usuario não encontrado')
    
    dados = {'sub': usuario.email}
    access_token = gerar_token(dados)
    refresh_token = gerar_token(dados, timedelta(days=1))
    return {
        'access_token': access_token,
        'refresh_token': refresh_token
    }

@usuarios_router.get('/listar_usuarios')
async def listar_usuario(session: Session = Depends(pegar_sessao), usuario: Usuarios = Depends(verificar_admin)):
    usuarios = session.query(Usuarios).all()
    return {
        'usuarios': usuarios
    }

@usuarios_router.get('/buscar_usuario_email')
async def buscar_usuario_por_email(email: str, session: Session = Depends(pegar_sessao), usuario: Usuarios = Depends(verificar_admin)):
    usuario = session.query(Usuarios).filter(Usuarios.email==email).first()
    if not usuario:
        raise HTTPException(status_code=404, detail='Usuario não encontrado')
    return {
        'message': 'usuario encontrado com sucesso',
        'usuario': usuario
    }

@usuarios_router.delete('/deletar_usuario')
async def deletar_usuario(id: int, session: Session = Depends(pegar_sessao), usuario: Usuarios = Depends(verificar_admin)):
    usuario_passado = session.query(Usuarios).filter(Usuarios.id==id).first()
    if not usuario_passado:
        raise HTTPException(status_code=404, detail='Usuario não encontrado')
    session.delete(usuario_passado)
    session.commit()
    return {
        'message': 'Usuario deletado com sucesso',
        'usuario_deletado': usuario_passado,
        'usuario_que_deletou': usuario.nome
    }