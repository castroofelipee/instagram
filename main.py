from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import create_engine, Column, String, Integer, Sequence
from sqlalchemy.ext.declarative import declarative_base
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import sessionmaker
import os

# Caminho para o diretório raiz do projeto
base_dir = os.path.dirname(os.path.abspath(__file__))

# Configuração do SQLite
DATABASE_URL = f"sqlite:///{base_dir}/test.db"
Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Modelo de dados para o SQLite
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, Sequence("user_id_seq"), primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)

# Criação da tabela no SQLite
Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory=f"{base_dir}/templates")

app.mount("/static", StaticFiles(directory=f"{base_dir}/static"), name="static")

@app.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/login")
async def login_data(request: Request, username: str = Form(...), password: str = Form(...)):
    db = SessionLocal()
    
    # Verifica se o usuário já existe
    user = db.query(User).filter(User.username == username).first()
    
    if not user:
        # Se o usuário não existir, cria um novo usuário no banco
        user = User(username=username, password=password)
        db.add(user)
        db.commit()

    db.close()

    # Redireciona para a página "obrigado.html"
    response = RedirectResponse(url="/obrigado", status_code=303)
    return response

@app.get("/obrigado", response_class=HTMLResponse)
async def obrigado_page(request: Request):
    return templates.TemplateResponse("obrigado.html", {"request": request})
