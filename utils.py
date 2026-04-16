from passlib.context import CryptContext
from sqlalchemy.orm import Session
from models import Usuarios
from datetime import timedelta, datetime
from jose import jwt, JWTError
from security import SECRET_KEY, ALGORITHM

pwd_context = CryptContext(schemes=['argon2'], deprecated='auto')

def gerar_hash(senha: str):
    return pwd_context.hash(senha)

def autenticar_usuario(email: str, senha: str, session: Session):
    usuario = session.query(Usuarios).filter(Usuarios.email==email).first()
    if not usuario:
        return False
    if not pwd_context.verify(senha, usuario.senha):
        return False
    return usuario

def gerar_token(dados: dict, duracao: timedelta = timedelta(minutes=30)):
    dados_copia = dados.copy()
    expire = datetime.utcnow() + duracao
    dados_copia.update({'exp': expire})
    return jwt.encode(dados_copia, SECRET_KEY, algorithm=ALGORITHM)

def verificar_token(dados, session: Session):
    try:
        dados = jwt.decode(dados, SECRET_KEY, algorithms=[ALGORITHM])
        usuario = session.query(Usuarios).filter(Usuarios.email==dados.get('sub')).first()
    except JWTError:
        return False
    return usuario