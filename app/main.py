from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse

from app.config import get_settings
from app.session import get_current_user_id, get_optional_user_id
from app.routes import auth
from app.storage.user_storage import get_user_storage

settings = get_settings()

# Initialize CSV storage
get_user_storage()
auth_router = auth.router

app = FastAPI(title="Web3 Community Binding")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.include_router(auth_router)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request, user_id: int = Depends(get_optional_user_id)):
    if user_id:
        return RedirectResponse("/dashboard", status_code=303)
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, user_id: int = Depends(get_current_user_id)):
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/health")
async def health():
    return {"status": "healthy"}
