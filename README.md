#  Home Budget API

Simple Home Budget API that manages authentification (register, login), CRUD(categories, expenses, income) and an analytics endpoint.

# Tech Stach 
- **FastAPI** – web framework  
- **PostgreSQL** – baza podataka  
- **SQLAlchemy** – ORM  
- **Pydantic v2** – validacija i serijalizacija  
- **PyJWT / passlib** – autentifikacija  
- **Pytest** – testiranje

## Pokretanje projekta

### Kloniraj repozitorij
bash
git clone https://github.com/nikoleta2001/Home-Budget-.git
cd Home-Budget-/home-budget-api

### Kreiranje virtualnog okreuženja
python -m venv .venv
# Windows
.\.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

### Instaliraj ovisnost
pip install -r requirements.txt

### Postavi konfiguraciju
Kopiraj .env-example u .env i unesi svoje podatke:
Primjer .env:
DATABASE_URL=postgresql+psycopg://postgres:password@localhost:5432/homebudget
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

### Pokreni aplikaciju:
uvicorn app.main:app --reload

Aplikacija će biti dostupna na:
http://127.0.0.1:8000/docs

