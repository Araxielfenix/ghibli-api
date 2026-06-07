import logging
import os
import bcrypt
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from contextlib import asynccontextmanager
import httpx
from fastapi import Depends, FastAPI, HTTPException, Header, Form, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import Base, engine, get_db
from models import User

class UserBulkDeleteRequest(BaseModel):
    ids: List[int]

class UserUpdateRequest(BaseModel):
    nombre: Optional[str] = None
    email: Optional[EmailStr] = None
    rol: Optional[str] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    limits = httpx.Limits(max_connections=100, max_keepalive_connections=20)
    timeout = httpx.Timeout(timeout=5.0)
    
    app.state.http_client = httpx.AsyncClient(limits=limits, timeout=timeout)
    
    yield
    await app.state.http_client.aclose()

app = FastAPI(title="Ghibli API Challenge", lifespan=lifespan)
app.title = "Ghibli API Challenge"

Base.metadata.create_all(bind=engine)
templates = Jinja2Templates(directory="pages")
GHIBLI_API_URL = os.getenv("GHIBLI_API_URL")

@app.get("/", tags=["Vistas"], response_class=HTMLResponse)
def home():
    with open("pages/index.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, status_code=200)

@app.get("/admin", tags=["Vistas"], response_class=HTMLResponse)
def admin():
    with open("pages/admin.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, status_code=200)

@app.get("/dashboard", tags=["Vistas"], response_class=HTMLResponse)
def dashboard():
    with open("pages/dashboard.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, status_code=200)

@app.post("/User/signUp", tags=["Autenticación"])
def signUp(
    nombre: str = Form(...), 
    email: str = Form(...), 
    password: str = Form(...), 
    rol: str = Form(...), 
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == email).first()
    if user:
        raise HTTPException(status_code=400, detail="El correo electrónico ya está registrado.")
    
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    nuevo_usuario = User(nombre=nombre, email=email, password=password_hash, rol=rol)
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return {"status": "success", "message": "Usuario registrado correctamente"}

@app.post("/User/login", tags=["Autenticación"])
def login(
    email: str = Form(...), 
    password: str = Form(...), 
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos.")
    if not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos.")
    return {
        "status": "success",
        "id": user.id,
        "rol": user.rol,
        "nombre": user.nombre
    }

def get_http_client(request: Request) -> httpx.AsyncClient:
    return request.app.state.http_client

@app.get("/api/ghibli", tags=["Ghibli API"])
async def get_ghibli_data(
    resource: str = Query("films", description="Recurso a consultar de Ghibli"),
    x_user_id: int = Header(..., description="ID del usuario que consulta"),
    db: Session = Depends(get_db),
    client: httpx.AsyncClient = Depends(get_http_client)
):
    usuario = db.query(User).filter(User.id == x_user_id).first()
    if not usuario:
        raise HTTPException(status_code=401, detail="Usuario no válido.")
    
    endpoint_final = resource if usuario.rol == "admin" else usuario.rol
    
    try:
        response = await client.get(f"{GHIBLI_API_URL}/{endpoint_final}")
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=502, 
                detail="La API externa de Studio Ghibli no respondió correctamente."
            )
        
    except httpx.HTTPError as e:
        logging.error(f"Error al conectar con la API de Ghibli: {e}")
        raise HTTPException(status_code=504, detail="Error de comunicación o timeout con el proveedor externo.")
    
    datos_api = response.json()
    resultados = []
    for item in datos_api:
        titulo = item.get("title") or item.get("name") or "Sin nombre"
        descripcion = item.get("description") or f"Recurso de tipo {endpoint_final} sin descripción."
        extra = item.get("original_title") or item.get("climate") or item.get("gender") or "N/A"
        url_imagen = item.get("image") or None
        
        resultados.append({
            "title_or_name": titulo,
            "description": descripcion,
            "extra_detail": f"{extra}",
            "resource_type": endpoint_final,
            "cover_image": url_imagen
        })
        
    return {"status": "success", "resultados": resultados}

def verificar_admin(x_user_id: int = Header(...), db: Session = Depends(get_db)):
    usuario_operador = db.query(User).filter(User.id == x_user_id).first()
    if not usuario_operador or usuario_operador.rol != "admin":
        raise HTTPException(status_code=403, detail="Acceso denegado: Se requieren permisos de administrador.")
    return usuario_operador

@app.get("/users", tags=["Usuarios"])
def get_users(db: Session = Depends(get_db), current_admin: User = Depends(verificar_admin)):
    users = db.query(User).all()
    return [{"id": u.id, "nombre": u.nombre, "email": u.email, "rol": u.rol} for u in users]

@app.get("/user/{id}", tags=["Usuarios"])
def get_user(id: int, db: Session = Depends(get_db), current_admin: User = Depends(verificar_admin)):
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {"id": user.id, "nombre": user.nombre, "email": user.email, "rol": user.rol}

@app.patch("/user/update/{id}", tags=["Usuarios"])
def update_user(
    id: int,
    payload: UserUpdateRequest,
    db: Session = Depends(get_db),
    current_admin: User = Depends(verificar_admin)
):
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    update_data = payload.dict(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(user, key, value)
    
    db.commit()
    db.refresh(user)
    
    return {
        "status": "success", 
        "message": "Usuario actualizado correctamente",
        "user": {"id": user.id, "nombre": user.nombre, "email": user.email, "rol": user.rol}
    }

@app.delete("/user/delete/{id}", tags=["Usuarios"])
def delete_user(id: int, db: Session = Depends(get_db), current_admin: User = Depends(verificar_admin)):
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    db.delete(user)
    db.commit()
    return {"status": "success", "message": "Usuario eliminado correctamente"}

@app.post("/users/bulk-delete", tags=["Usuarios"])
def delete_multiple_users(
    payload: UserBulkDeleteRequest, 
    db: Session = Depends(get_db), 
    current_admin: User = Depends(verificar_admin)
):
    try:
        users_to_delete = db.query(User).filter(User.id.in_(payload.ids)).all()
        
        if len(users_to_delete) != len(payload.ids):
            found_ids = {u.id for u in users_to_delete}
            missing_ids = list(set(payload.ids) - found_ids)
            raise HTTPException(
                status_code=404, 
                detail=f"Operación cancelada. No se encontraron los IDs: {missing_ids}"
            )
        
        for user in users_to_delete:
            db.delete(user)
            
        db.commit()
        return {"status": "success", "message": f"{len(users_to_delete)} usuarios eliminados correctamente"}
        
    except HTTPException:
        db.rollback() 
        raise
    except Exception as e:
        db.rollback()
        logging.error(f"Error crítico en bulk-delete: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno al procesar el borrado masivo.")