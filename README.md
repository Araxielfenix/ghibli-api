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
