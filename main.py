from fastapi import FastAPI
from models import Base, engine

app = FastAPI()



from usuarios_routes import usuarios_router
from biblioteca_routes import biblioteca_router
from emprestimo_routes import emprestimo_router

app.include_router(usuarios_router)
app.include_router(biblioteca_router)
app.include_router(emprestimo_router)