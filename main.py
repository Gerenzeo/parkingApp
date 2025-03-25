import datetime

from fastapi import FastAPI, Request, Depends, status, Query, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware


from src.config.config import settings
from src.db.models import User
from src.data.countries import COUNTRIES
from src.routes.clients import clients
from src.routes.services import services
from src.routes.users import users
from src.routes.plans import plans
from src.routes.auth import auth
from src.routes.orders import orders
from src.routes.profile import profile
from src.routes.parking import parking
from src.routes.restore import restore
from src.routes.application import application
from src.routes.payments import payments
from src.repositories.rp_plans import oPlans
from src.repositories.rp_app import oApp
from src.repositories.rp_clients import oClients
from src.services.authorization import auth_service
from src.schemas.application.application_schema import ApplicationModel
from src.schemas.roles.roles_schema import RoleModel

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)
templates = Jinja2Templates(directory="templates")


@app.get("/")
async def root(
    request: Request,
    current_user: User = Depends(auth_service.get_current_user)
):  
    try:
        app = await oApp.get_data()
    except Exception:
        return RedirectResponse("/application/step-1", status_code=status.HTTP_302_FOUND)

    plans = await oPlans.get_list_data_ordered_by("position")

    return templates.TemplateResponse(
        "index.html",
        context={
            "app": app,
            "request": request,
            "current_page": "home",
            "current_user": current_user,
            "title": "Home",
            "plans": plans
        }
    )


@app.get("/info")
async def info(
    request: Request,
    current_user: User = Depends(auth_service.get_current_user)
):

    return templates.TemplateResponse(
        "info.html",
        context={
            "request": request,
            "current_page": "info",
            "current_user": current_user,
            "title": "Information about project",

        }
    )




@app.get("/api/get-client")
async def get_client(phone: str = Query(..., min_length=10, max_length=15)):
    return await oClients.get_data_by("phone", phone)

@app.get("/cities/")
async def get_cities(country_name: str = Query(...)):
    """Возвращает список городов для выбранной страны"""
    for country in COUNTRIES:
        if country["name"] == country_name:
            return country["cities"]
    return []



app.include_router(restore.router)
app.include_router(application.router)
app.include_router(auth.router)
app.include_router(clients.router)
app.include_router(services.router)
app.include_router(users.router)
app.include_router(plans.router)
app.include_router(orders.router)
app.include_router(profile.router)
app.include_router(parking.router)
app.include_router(payments.router)