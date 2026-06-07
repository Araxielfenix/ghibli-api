# Ghibli API

Este proyecto consiste en el desarrollo de una **API REST de usuarios** para consumir recursos de la API oficial de Studio Ghibli, mapeados según el rol y los privilegios del usuario autenticado. 

---

## 🛠️ Stack Tecnológico

- **Backend:** Python 3.11+ con **FastAPI** (Estructura de alto rendimiento asíncrona).
- **ORM / Base de Datos:** **SQLAlchemy** conectado a **PostgreSQL (Neon.tech)** en la nube para persistencia en producción (con soporte *fallback* local a SQLite).
- **Cliente HTTP:** **HTTPX** (Consumo asíncrono y eficiente de APIs externas mediante un pool de conexiones optimizado).
- **Frontend:** HTML5 puro, JavaScript moderno y **Tailwind CSS**.

---

## 📐 Arquitectura del Proyecto

El backend actúa estrictamente como un API REST puro que distribuye datos en formato JSON, mientras que el frontend interactúa de forma asíncrona mediante peticiones `fetch`.

### Flujo de Seguridad y Consumo de la API
1. El cliente envía sus credenciales al Backend.
2. El Backend valida la identidad del operador directamente en la base de datos PostgreSQL.
3. El Backend determina el recurso permitido según su rol y realiza la petición hacia Ghibli.

---

## 🛠️ Guía de despliegue local

Si deseas clonar y ejecutar este proyecto en tu entorno local, sigue los pasos detallados a continuación:

### 1. Clonar el Repositorio
En tu terminal escribe el siguiente comando
```
git clone https://github.com/Araxielfenix/ghibli-api.git
cd tu-repositorio
```

### 2. Configurar el Archivo de Entorno (.env)
Crea un archivo llamado .env en la raíz del proyecto (al mismo nivel que main.py).

Debe llevar la siguiente estructura exacta:
```
# URL de conexión a tu base de datos de Neon.tech (PostgreSQL)
DATABASE_URL=postgresql://neondb_owner:...

# URL oficial de la API de Studio Ghibli
GHIBLI_API_URL="https://ghibliapi.vercel.app"
```

### 3. Instalación de Dependencias
Para instalar todas las librerías necesarias que requiere el backend para ejecutarse de manera correcta, ejecuta el siguiente comando en tu terminal:
```
pip install fastapi uvicorn sqlalchemy psycopg2-binary httpx python-dotenv bcrypt pydantic
```

Librerías instaladas:
- fastapi y uvicorn: Framework web y servidor de producción ASGI.
- sqlalchemy y psycopg2-binary: Para la conexión con la BD.
- httpx: Cliente HTTP asíncrono para el Gateway Proxy de Studio Ghibli.
- python-dotenv: Lector y mapeador del archivo .env.
- bcrypt: Encriptación segura de contraseñas (Hashing).
- pydantic: Validación de esquemas de datos.

### 4. Comando de Ejecución
Una vez que las dependencias estén instaladas y el archivo .env configurado, inicia el servidor de FastAPI con el siguiente comando:
```
uvicorn main:app --reload
```
El sistema estará disponible inmediatamente en tu navegador web a través de la dirección local: ```http://localhost:8000```
