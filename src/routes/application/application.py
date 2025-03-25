from typing import List
import uuid

from fastapi import APIRouter, Request, Form, Depends, status, HTTPException, Query
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import User
from src.services.authorization import auth_service
from src.repositories.rp_services import oServices
from src.repositories.rp_roles import oRoles
from src.schemas.users.users_schema import UserModel
from src.schemas.services.services_schema import ServiceModel
from src.schemas.roles.roles_schema import RoleModel
from src.schemas.application.application_schema import ApplicationModel
from src.repositories.rp_app import oApp
from src.db.models import engine, Base
from src.repositories.rp_users import oUsers

current_dir_many = "applications"
current_dir_one = "application"

router = APIRouter(prefix=f"/{current_dir_one}")
templates = Jinja2Templates(directory="templates")
router.mount('/static', StaticFiles(directory="static"), name='static')


# STEP 1
@router.get("/step-1")
async def data_root(
    request: Request,
):
    tmp_project_name = request.session.get("tmp_project_name", "")
    project_name_message = request.session.pop("project_name_message", "")

    return templates.TemplateResponse(
        f"pages/{current_dir_one}/step_1.html",
        context={
            "request": request,
            "current_page": f"Step",
            "title": "title",
            "tmp_project_name": tmp_project_name,
            "project_name_message": project_name_message,
        }
    )

# STEP 1 POST
@router.post("/step-1/success")
async def data_root(
    request: Request,
    project_name: str = Form(None),
):
    request.session['tmp_project_name'] = project_name

    if not project_name:
        request.session['project_name_message'] = "Please enter project name!"
        return RedirectResponse(url=f"/{current_dir_one}/step-1", status_code=status.HTTP_302_FOUND)
    
    request.session['init_project_name'] = project_name.strip()
    return RedirectResponse(url=f"/{current_dir_one}/step-2", status_code=status.HTTP_302_FOUND)



# STEP 2
@router.get("/step-2")
async def data_root(
    request: Request
):
    tmp_full_name = request.session.get("tmp_full_name", "")
    full_name_message = request.session.pop("full_name_message", "")

    tmp_email = request.session.get("tmp_email", "")
    email_message = request.session.pop("email_message", "")


    password_message = request.session.pop("password_message", "")
    

    return templates.TemplateResponse(
        f"pages/{current_dir_one}/step_2.html",
        context={
            "request": request,
            "current_page": f"Step",
            "title": "title",
            
            "tmp_full_name": tmp_full_name,
            "full_name_message": full_name_message,
            "tmp_email": tmp_email,
            "email_message": email_message,
            "password_message": password_message,
        }
    )

# STEP 2 POST
@router.post("/step-2/success")
async def data_root(
    request: Request,
    full_name: str = Form(None),
    email: str = Form(None),
    password: str = Form(None),
    confirm_password: str = Form(None),
):
    request.session['tmp_full_name'] = full_name
    request.session['tmp_email'] = email

    if not full_name:
        request.session['full_name_message'] = "Please enter Full Name!"
        return RedirectResponse(url=f"/{current_dir_one}/step-2", status_code=status.HTTP_302_FOUND)

    if not email:
        request.session['email_message'] = "Please enter Email!"
        return RedirectResponse(url=f"/{current_dir_one}/step-2", status_code=status.HTTP_302_FOUND)
    
    if not password or not confirm_password:
        request.session['password_message'] = "Please enter passwords!"
        return RedirectResponse(url=f"/{current_dir_one}/step-2", status_code=status.HTTP_302_FOUND)
    
    if not password == confirm_password:
        request.session['password_message'] = "Passwords are dismatch!"
        return RedirectResponse(url=f"/{current_dir_one}/step-2", status_code=status.HTTP_302_FOUND)
    

    project_name = request.session.get("tmp_project_name")
    full_name = full_name.strip()
    email = email.strip()
    password = password.strip()

    
    # CREATE ALL TABLES
     # **Создание таблиц**
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


    new_app = ApplicationModel(
        is_active=True
    )
    await oApp.create(new_app)

    roles = []
    super_user_role = RoleModel(
        role_name="superuser",
        role_name_code="superuser",
    )
    user_role = RoleModel(
        role_name="user",
        role_name_code="user",
    )
    roles.append(super_user_role)
    roles.append(user_role)

    await oRoles.bulk_create(roles)

    password = auth_service.get_password_hash(password)
    unique_code = uuid.uuid4().hex

    new_user = UserModel(
        unique_code=unique_code,
        full_name=full_name,
        email=email,
        phone=None,
        country=None,
        city=None,
        password=password,
        role_id=1,
        activity=True,
    )
    await oUsers.create(new_user)
    return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

    
    

    # return RedirectResponse(url=f"/{current_dir_one}/step-2", status_code=status.HTTP_302_FOUND)





