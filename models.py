from sqlalchemy import create_engine, Column, String, Integer, Boolean
from sqlalchemy.orm import DeclarativeBase

engine = create_engine('sqlite:///banco.db')

class Base(DeclarativeBase):
    pass

class Usuarios(Base):
    __tablename__ = 'usuario'

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    nome = Column('nome', String)
    email = Column('email', String)
    senha = Column('senha', String)
    admin = Column('admin', Boolean)

    def __init__(self, nome, email, senha, admin):
        self.nome = nome
        self.email = email
        self.senha = senha
        self.admin = admin
        

class Livros(Base):
    __tablename__ = 'livros'

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    titulo = Column('titulo', String)
    autor = Column('autor', String)
    descricao = Column('descricao', String)
    isbn = Column('isbn', String)
    quantidade_disponivel = Column('quantidade_disponivel', Integer)
    categoria = Column('categoria', String)

    def __init__(self, titulo, autor, descricao, isbn, quantidade_disponivel, categoria):
        self.titulo = titulo
        self.autor = autor
        self.descricao = descricao
        self.isbn = isbn
        self.quantidade_disponivel = quantidade_disponivel
        self.categoria = categoria


