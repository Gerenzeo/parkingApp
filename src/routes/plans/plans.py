from typing import List

from fastapi import APIRouter, Request, Form, Depends, status, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from src.db.models import User
from src.services.authorization import auth_service
from src.repositories.rp_services import oServices
from src.repositories.rp_plans import oPlans
from src.repositories.rp_users import oUsers
from src.repositories.rp_places import oPlaces
from src.schemas.plans.plans_schema import PlanModel
from src.schemas.services.services_schema import ServiceModel

current_dir_many = "plans"
current_dir_one = "plan"

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

    success_message = request.session.pop("success-message", "")

    plans = await oPlans.get_data()

    return templates.TemplateResponse(
        "pages/plans/plans.html",
        context={
            "request": request,
            "current_page": current_dir_many,
            "current_user": current_user,
            "title": current_dir_many.title(),
            "plans": plans,
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

    tmp_position = request.session.get("tmp_position")
    position_message = request.session.pop("position_message", '')

    return templates.TemplateResponse(
        "pages/plans/create.html",
        context={
            "request": request,
            "current_page": current_dir_many,
            "current_user": current_user,
            "title": current_dir_many.title(),
            
            # Messages
            "name_message": name_message,
            "position_message": position_message,

            # Tmp data
            "tmp_name": tmp_name,
            "tmp_position": tmp_position,
        }
    )



# CREATE POST
@router.post("/new")
async def data_create_post(
    request: Request,
    name: str = Form(None),
    position: str = Form(None),
    # services: List[int] = Form([]),
    current_user: User = Depends(auth_service.get_current_user)
    ):

    request.session["tmp_name"] = name
    request.session["tmp_position"] = position

    if name is None:
        request.session["tmp_name"] = ""
        request.session["name_message"] = f'Please enter name of {current_dir_one}!'
        return RedirectResponse(url=f'/{current_dir_many}/new', status_code=status.HTTP_302_FOUND)

    existing_plan = await oPlans.get_data_by("name", name.strip())
    if existing_plan:
        request.session["name_message"] = f'This {current_dir_one} already exist!'
        return RedirectResponse(url=f'/{current_dir_many}/new', status_code=status.HTTP_302_FOUND)

    if position is None:
        request.session["tmp_position"] = ""
        request.session["position_message"] = f'Please enter position for plan!'
        return RedirectResponse(url=f'/{current_dir_many}/new', status_code=status.HTTP_302_FOUND)
    


    if not current_user:
        request.session['link_from'] = str(request.url)
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)

    code = name.strip().replace(" ", '_').lower()

    new_plan = PlanModel(
        name=name.strip(),
        code=code,
        position=int(position.strip()),
    )
    plan = await oPlans.create(new_plan)

    request.session.clear()
    request.session['success-message'] = f'{current_dir_one.title()} was successfully created!'
    return RedirectResponse(url=f"/{current_dir_many}", status_code=status.HTTP_302_FOUND)


# UPDATE GET
@router.get("/update/{data_code}")
async def data_update_page(
    request: Request,
    data_code: str,
    current_user: User = Depends(auth_service.get_current_user)
    ):
    if not current_user:
        request.session['link_from'] = str(request.url)
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)
    
    data = await oPlans.get_data_by("code", data_code)

    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page not found")

    name_message = request.session.pop("name_message", '')
    position_message = request.session.pop("position_message", '')

    return templates.TemplateResponse(
        f"pages/{current_dir_many}/update.html",
        context={
            "request": request,
            "current_page": current_dir_many,
            "current_user": current_user,
            "title": current_dir_many.title(),
            "plan": data,
            
            # Messages
            "name_message": name_message,
            "position_message": position_message,
        }
    )



# UPDATE POST
@router.post("/update/{data_code}")
async def data_update_post(
    request: Request,
    data_code: str,
    name: str = Form(None),
    count_place: str = Form(None),
    position: str = Form(None),
    # services: List[int] = Form([]),
    current_user: User = Depends(auth_service.get_current_user)
    ):
    

    if name is None:
        request.session["name_message"] = f'Please enter name of {current_dir_one}!'
        return RedirectResponse(url=f'/{current_dir_many}/update/{data_code}', status_code=status.HTTP_302_FOUND)
    
    existing_plan = await oPlans.get_data_by("code", data_code)
    if existing_plan and existing_plan.code != data_code:
        request.session["name_message"] = f'This {current_dir_one} already exist!'
        return RedirectResponse(url=f'/{current_dir_many}/update/{data_code}', status_code=status.HTTP_302_FOUND)

    if position is None:
        request.session["tmp_position"] = ""
        request.session["position_message"] = f'Please enter position for plan!'
        return RedirectResponse(url=f'/{current_dir_many}/update/{data_code}', status_code=status.HTTP_302_FOUND)

    if not current_user:
        request.session['link_from'] = str(request.url)
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)
    
    code = name.strip().replace(" ", '_').lower()
    new_plan = PlanModel(
        name=name.strip(),
        code=code,
        position=int(position.strip()),
    )

    plan = await oPlans.update_data(existing_plan.id, new_plan)

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
    
    await oPlans.delete_by("id", data_id)
    request.session['success-message'] = f'{current_dir_one.title()} was successfully deleted!'
    return RedirectResponse(url=f"/{current_dir_many}", status_code=status.HTTP_302_FOUND)




# SERVICES #########################################################################################################


# CREATE SERVICES
@router.get("/{data_code}/add-service")
async def data_create(
    request: Request,
    data_code: str,
    current_user: User = Depends(auth_service.get_current_user)
    ):
    if not current_user:
        request.session['link_from'] = str(request.url)
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)

    plan = await oPlans.get_data_by("code", data_code)

    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page not found")

    tmp_service_name = request.session.get("tmp_service_name")
    service_name_message = request.session.pop("service_name_message", '')

    tmp_price = request.session.get("tmp_price")
    price_message = request.session.pop("price_message", '')

    tmp_icon_svg = request.session.get("tmp_icon_svg")
    icon_svg_message = request.session.pop("icon_svg_message", '')

    tmp_custom = request.session.get("tmp_custom")
    custom_message = request.session.pop("custom_message", '')

    return templates.TemplateResponse(
        "pages/plans/create-service.html",
        context={
            "request": request,
            "current_page": current_dir_many,
            "current_user": current_user,
            "title": f"{data_code} - Add service",
            "plan": plan,
            
            # Messages
            "service_name_message": service_name_message,
            "price_message": price_message,
            "icon_svg_message": icon_svg_message,
            "custom_message": custom_message,

            # Tmp data
            "tmp_service_name": tmp_service_name,
            "tmp_price": tmp_price,
            "tmp_svg_icon": tmp_icon_svg,
            "tmp_custom": tmp_custom,
        }
    )


# CREATE SERVICE POST
@router.post("/{data_code}/add-service")
async def data_create_post(
    request: Request,
    data_code: str,
    name: str = Form(None),
    price: str = Form(None),
    icon_svg: str = Form(None),
    custom: bool = Form(None),
    current_user: User = Depends(auth_service.get_current_user)
    ):

    plan = await oPlans.get_data_by("code", data_code)
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page not found")

    request.session["tmp_service_name"] = name
    request.session["tmp_price"] = price
    request.session["tmp_icon_svg"] = icon_svg
    request.session["tmp_custom"] = custom


    if name is None:
        request.session["tmp_service_name"] = ""
        request.session["service_name_message"] = f'Please enter name of service!'
        return RedirectResponse(url=f'/{current_dir_many}/{data_code}/add-service', status_code=status.HTTP_302_FOUND)
    
    if price is None:
        request.session["tmp_price"] = ""
        request.session["price_message"] = f'Please enter price for service!'
        return RedirectResponse(url=f'/{current_dir_many}/{data_code}/add-service', status_code=status.HTTP_302_FOUND)
    
    if icon_svg is None:
        request.session["tmp_icon_svg"] = ""
        request.session["icon_svg_message"] = f'Please enter svg icon code for service!'
        return RedirectResponse(url=f'/{current_dir_many}/{data_code}/add-service', status_code=status.HTTP_302_FOUND)
    
    if not current_user:
        request.session['link_from'] = str(request.url)
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)

    new_service = ServiceModel(
        name=name.lower().strip(),
        price=int(price.strip()),
        icon_svg=icon_svg,
        custom=custom,
        plan_id=plan.id,
    )
    service = await oServices.create(new_service)

    request.session.clear()
    request.session['success-message'] = f'Service {service.name.title()} successfully created!'
    return RedirectResponse(url=f"/{current_dir_many}", status_code=status.HTTP_302_FOUND)



# UPDATE SERVICE
@router.get("/{data_code}/update-service-{service_id}")
async def data_update(
    request: Request,
    data_code: str,
    service_id: int,
    current_user: User = Depends(auth_service.get_current_user)
    ):
    if not current_user:
        request.session['link_from'] = str(request.url)
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)

    plan = await oPlans.get_data_by("code", data_code)

    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page not found")
    
    service = await oServices.get_data_by('id', service_id)
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page not found")

    tmp_service_name = request.session.get("tmp_service_name")
    service_name_message = request.session.pop("service_name_message", '')

    tmp_price = request.session.get("tmp_price")
    price_message = request.session.pop("price_message", '')

    tmp_icon_svg = request.session.get("tmp_icon_svg")
    icon_svg_message = request.session.pop("icon_svg_message", '')

    tmp_custom = request.session.get("tmp_custom")
    custom_message = request.session.pop("custom_message", '')

    return templates.TemplateResponse(
        "pages/plans/update-service.html",
        context={
            "request": request,
            "current_page": current_dir_many,
            "current_user": current_user,
            "title": f"{data_code} - Add service",
            "plan": plan,
            "service": service,
            
            # Messages
            "service_name_message": service_name_message,
            "price_message": price_message,
            "icon_svg_message": icon_svg_message,
            "custom_message": custom_message,

            # Tmp data
            "tmp_service_name": tmp_service_name,
            "tmp_price": tmp_price,
            "tmp_svg_icon": tmp_icon_svg,
            "tmp_custom": tmp_custom,
        }
    )

# UPDATE SERVICE POST
@router.post("/{data_code}/update-service-{service_id}")
async def data_update(
    request: Request,
    data_code: str,
    service_id: int,
    name: str = Form(None),
    price: str = Form(None),
    icon_svg: str = Form(None),
    custom: bool = Form(None),
    current_user: User = Depends(auth_service.get_current_user)
    ):

    plan = await oPlans.get_data_by("code", data_code)
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page not found")
    
    service = await oServices.get_data_by('id', service_id)
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page not found")

    request.session["tmp_service_name"] = name
    request.session["tmp_price"] = price
    request.session["tmp_icon_svg"] = icon_svg
    request.session["tmp_custom"] = custom

    if name is None:
        request.session["tmp_service_name"] = ""
        request.session["service_name_message"] = f'Please enter name of service!'
        return RedirectResponse(url=f'/{current_dir_many}/{data_code}/add-service', status_code=status.HTTP_302_FOUND)
    
    if price is None:
        request.session["tmp_price"] = ""
        request.session["price_message"] = f'Please enter price for service!'
        return RedirectResponse(url=f'/{current_dir_many}/{data_code}/add-service', status_code=status.HTTP_302_FOUND)
    
    if icon_svg is None:
        request.session["tmp_icon_svg"] = ""
        request.session["icon_svg_message"] = f'Please enter svg icon code for service!'
        return RedirectResponse(url=f'/{current_dir_many}/{data_code}/add-service', status_code=status.HTTP_302_FOUND)

    if not current_user:
        request.session['link_from'] = str(request.url)
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)

    new_service = ServiceModel(
        name=name.lower().strip(),
        price=int(price.strip()),
        icon_svg=icon_svg,
        custom=custom,
        plan_id=plan.id,
    )
    service = await oServices.update_data(service.id, new_service)

    request.session.clear()
    request.session['success-message'] = f'Service {service.name.title()} successfully created!'
    return RedirectResponse(url=f"/{current_dir_many}", status_code=status.HTTP_302_FOUND)


# DELETE
@router.get("/{data_code}/delete-service-{service_id}")
async def data_delete(
    request: Request,
    service_id: int,
    current_user: User = Depends(auth_service.get_current_user)
):  
    if not current_user:
        request.session['link_from'] = str(request.url)
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)
    
    await oServices.delete_by("id", service_id)
    request.session['success-message'] = f'{current_dir_one.title()} was successfully deleted!'
    return RedirectResponse(url=f"/{current_dir_many}", status_code=status.HTTP_302_FOUND)




# DEACTIVATE
@router.get("/{plan_code}/{user_code}/deactivate")
async def deactivate_plan(
    request: Request,
    plan_code: str,
    user_code: str,
    current_user: User = Depends(auth_service.get_current_user)
    ):
    if not current_user:
        request.session['link_from'] = str(request.url)
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)

    success_message = request.session.pop("success-message", "")

    plan = await oPlans.get_data_by("code", plan_code)
    user = await oUsers.get_data_by("unique_code", user_code)

    if not user or not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page not found")

    await oPlaces.delete_all_data("user_id", user.id)


    # await oPlaces
    user_fields = {
        "plan_id": None,
        "count_place": None,
    }
    await oUsers.update_data_by_fields(user.id, user_fields)

    print("All places deleted")