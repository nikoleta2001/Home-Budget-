from fastapi import FastAPI, HTTPException
from .config import settings
from .db import init_db, engine
from .seed import seed_categories
from sqlalchemy import inspect
from .auth.routes import router as auth_router
from .routers.categories import router as categories_router
from .routers.expenses import router as expenses_router
from .routers.analytics import router as analytics_router
from .routers.incomes import router as incomes_router
from contextlib import asynccontextmanager

tags_metadata = [
    {"name": "auth", "description": "Registracija i prijava korisnika. Vraća JWT (Bearer)."},
    {"name": "categories", "description": "CRUD nad kategorijama troškova."},
    {"name": "expenses", "description": "CRUD nad troškovima + filteri."},
    {"name": "analytics", "description": "Sažeci potrošnje po periodu i kategoriji."},
    {"name": "incomes", "description": "CRUD nad prihodima (+ utječe na balance)."},
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    seed_categories()
    yield
    

app = FastAPI(
    title="Home Budget API",
    version="0.1.0",
    description="Jednostavan API za kućni budžet: auth, kategorije, troškovi, analitika.",
    openapi_tags=tags_metadata,
    contact={"name": "Home Budget", "email": "support@example.com"},
    license_info={"name": "MIT"},
    lifespan=lifespan,
)


@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/")
def root():
    return {
        "message": "Home Budget API – up and running",
        "docs": "/docs",
        "env_loaded": bool(settings.SECRET_KEY),
    }

@app.get("/db-check")
def db_check():
    try:
        with engine.connect() as conn:
            version = conn.exec_driver_sql("SELECT version();").scalar()
        return {"db": "ok", "version": version}
    except Exception:
        raise HTTPException(status_code=500, detail="DB connection failed")

@app.get("/debug/tables")
def list_tables():
    insp = inspect(engine)
    return {"tables": insp.get_table_names()}

app.include_router(auth_router)
app.include_router(categories_router)
app.include_router(expenses_router)
app.include_router(analytics_router)
app.include_router(incomes_router)