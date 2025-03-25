from fastapi import APIRouter, Request, Form, Depends, status, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from src.db.models import User
from src.services.authorization import auth_service
from src.repositories.rp_services import oServices
from src.schemas.services.services_schema import ServiceModel


current_dir_many = "services"
current_dir_one = "service"

router = APIRouter(prefix=f"/{current_dir_many}")
templates = Jinja2Templates(directory="templates")
router.mount('/static', StaticFiles(directory="static"), name='static')




# DATA
@router.get("")
async def data_root(
    request: Request,
    current_user: User = Depends(auth_service.get_current_user)
    ):

    if not current_user:
        request.session['link_from'] = str(request.url)
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)
    
    success_message = request.session.pop("success-message", "")
    services = await oServices.get_data()

    return templates.TemplateResponse(
        f"pages/{current_dir_many}/{current_dir_many}.html",
        context={
            "request": request,
            "current_page": current_dir_many,
            "current_user": current_user,
            "title": current_dir_many.title(),
            "services": services,
            "success_message": success_message,
        }
    )

# CREATE GET
@router.get("/new")
async def data_create(
    request: Request,
    current_user: User = Depends(auth_service.get_current_user)
    ):

    if not current_user:
        request.session['link_from'] = str(request.url)
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)
    
    tmp_name = request.session.get("tmp_name")
    name_message = request.session.pop("name_message", '')

    tmp_price = request.session.get("tmp_price")
    price_message = request.session.pop("price_message", '')
    

    return templates.TemplateResponse(
        f"pages/{current_dir_many}/create.html",
        context={
            "request": request,
            "current_page": current_dir_many,
            "current_user": current_user,
            "title": current_dir_many.title(),
            
            # Messages
            "name_message": name_message,
            "price_message": price_message,

            # Tmp data
            "tmp_name": tmp_name,
            "tmp_price": tmp_price,
        }
    )


# CREATE POST
@router.post("/new")
async def data_create_post(
    request: Request,
    name: str = Form(None),
    price: str = Form(None),
    current_user: User = Depends(auth_service.get_current_user)
    ):

    if name is None:
        request.session["tmp_name"] = ""
        request.session["name_message"] = f'Please enter name of {current_dir_one}!'
        return RedirectResponse(url=f'/{current_dir_many}/new', status_code=status.HTTP_302_FOUND)
    
    request.session["tmp_name"] = name

    existing_service = await oServices.get_data_by("name", name.strip())
    if existing_service:
        request.session["name_message"] = f'This {current_dir_one} already exist!'
        return RedirectResponse(url=f'/{current_dir_many}/new', status_code=status.HTTP_302_FOUND)


    if price is None:
        request.session["tmp_price"] = ""
        request.session["price_message"] = f'Please enter price of {current_dir_one}!'
        return RedirectResponse(url=f'/{current_dir_many}/new', status_code=status.HTTP_302_FOUND)

    request.session["tmp_price"] = price
    
    if not current_user:
        request.session['link_from'] = str(request.url)
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)
    
    new_service = ServiceModel(
        name=name.strip(),
        price=int(price),
    )
    await oServices.create(new_service)


    request.session.clear()
    request.session['success-message'] = f'{current_dir_one.title()} was successfully created!'
    return RedirectResponse(url=f"/{current_dir_many}", status_code=status.HTTP_302_FOUND)



# UPDATE GET
@router.get("/update/{service_id}")
async def data_update_page(
    request: Request,
    service_id: int,
    current_user: User = Depends(auth_service.get_current_user)
    ):
    if not current_user:
        request.session['link_from'] = str(request.url)
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)
    
    service = await oServices.get_data_by("id", service_id)

    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    name_message = request.session.pop("name_message", '')
    price_message = request.session.pop("price_message", '')

    return templates.TemplateResponse(
        f"pages/{current_dir_many}/update.html",
        context={
            "request": request,
            "current_page": current_dir_many,
            "current_user": current_user,
            "title": current_dir_many.title(),
            "service": service,
            
            # Messages
            "name_message": name_message,
            "price_message": price_message,
        }
    )

# UPDATE POST
@router.post("/update/{data_id}")
async def data_update_post(
    request: Request,
    data_id: int,
    name: str = Form(None),
    price: str = Form(None),
    current_user: User = Depends(auth_service.get_current_user)
    ):
    if not current_user:
        request.session['link_from'] = str(request.url)
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)
    
    if name is None:
        request.session["name_message"] = f'Please enter name of {current_dir_one}!'
        return RedirectResponse(url=f'/{current_dir_many}/update/{data_id}', status_code=status.HTTP_302_FOUND)
    

    existing_service = await oServices.get_data_by("id", data_id)
    if existing_service and existing_service.id != data_id:
        request.session["name_message"] = f'This {current_dir_one} already exist!'
        return RedirectResponse(url=f'/{current_dir_many}/update/{data_id}', status_code=status.HTTP_302_FOUND)


    if price is None:
        request.session["price_message"] = f'Please enter price of {current_dir_one}!'
        return RedirectResponse(url=f'/{current_dir_many}/update/{service_id}', status_code=status.HTTP_302_FOUND)


    
    new_service = ServiceModel(
        name=name.strip(),
        price=int(price),
    )
    await oServices.update_data(data_id, new_service)

    request.session.clear()
    request.session['success-message'] = f'{current_dir_one.title()} was successfully updated!'
    return RedirectResponse(url=f"/{current_dir_many}", status_code=status.HTTP_302_FOUND)

# DELETE
@router.get("/remove/{data_id}")
async def data_delete(
    request: Request,
    data_id: int,
    current_user: User = Depends(auth_service.get_current_user)
):
    if not current_user:
        request.session['link_from'] = str(request.url)
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)
    
    await oServices.delete_by("id", data_id)
    request.session['success-message'] = f'{current_dir_one.title()} was successfully deleted!'
    return RedirectResponse(url=f"/{current_dir_many}", status_code=status.HTTP_302_FOUND)
