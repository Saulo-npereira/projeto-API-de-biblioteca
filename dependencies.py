from models import engine, Usuarios
from sqlalchemy.orm import sessionmaker, Session
from fastapi import Depends, HTTPException
from security import oauth2_scheme, SECRET_KEY, ALGORITHM
from jose import jwt, JWTError


def pegar_sessao():
    try:
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
    finally:
        session.close()

def verificar_token(token: str = Depends(oauth2_scheme), session: Session = Depends(pegar_sessao)):
    try:
        dic_info = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = dic_info.get('sub')
    except JWTError:
        raise HTTPException(status_code=401, detail='você não possui permição')

    usuario = session.query(Usuarios).filter(Usuarios.email==email).first()
    if not usuario:
        raise HTTPException(status_code=401, detail='você não possui uma conta')
    return usuario

def verificar_admin(usuario: Usuarios = Depends(verificar_token), session: Session = Depends(pegar_sessao)):
    if not usuario.admin:
        raise HTTPException(status_code=401, detail='voce não é um admin')
    return usuario



