from fastapi import APIRouter, Request, Form, Depends, status, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from src.db.models import User
from src.services.authorization import auth_service
from src.repositories.rp_users import oUsers
from src.schemas.services.services_schema import ServiceModel

current_dir_many = "users"
current_dir_one = "user"

router = APIRouter(prefix=f"/{current_dir_many}")
templates = Jinja2Templates(directory="templates")
router.mount('/static', StaticFiles(directory="static"), name='static')




# ALL DATA
@router.get("")
async def data_root(
    request: Request,
    current_user: User = Depends(auth_service.get_current_user)
    ):
    if not current_user:
        request.session['link_from'] = str(request.url)
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)
    
    users = await oUsers.get_data()

    return templates.TemplateResponse(
        f"pages/{current_dir_many}/{current_dir_many}.html",
        context={
            "request": request,
            "current_page": current_dir_many,
            "current_user": current_user,
            "title": current_dir_many.title(),
            "users": users,            
        }
    )

