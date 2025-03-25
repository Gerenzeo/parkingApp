import uuid
from datetime import datetime
from typing import List

from fastapi import APIRouter, Request, Form, Depends, status, HTTPException, Query
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from src.db.models import User
from src.services.authorization import auth_service
from src.repositories.rp_services import oServices
from src.repositories.rp_place_service import oPlaceServices
from src.repositories.rp_plans import oPlans
from src.repositories.rp_places import oPlaces
from src.repositories.rp_clients import oClients
from src.schemas.plans.plans_schema import PlanModel
from src.schemas.services.services_schema import ServiceModel
from src.schemas.places.places_schema import PlaceServiceModel
from src.schemas.clients.clients_schema import ClientModel


current_dir_many = "parking"
current_dir_one = "parking"

router = APIRouter(prefix=f"/{current_dir_many}")
templates = Jinja2Templates(directory="templates")
router.mount('/static', StaticFiles(directory="static"), name='static')


# ALL DATA
@router.get("")
async def data_root(
    request: Request,
    place: str = Query(None),
    event: str = Query(None),
    type: str = Query(None),
    current_user: User = Depends(auth_service.get_current_user)
    ):
    if not current_user:
        request.session['link_from'] = str(request.url)
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)
    
    success_message = request.session.pop("success-message", "")
    selected_place = await oPlaces.get_data_by("unique_key", place)

    services_for_selected_place = []
    place_services = []

    if selected_place:

        services_for_selected_place = await oServices.get_list_data_by_with_order("plan_id", selected_place.user.plan_id, "created_at")
        place_services = await oPlaceServices.get_list_data_by_with_order("place_id", selected_place.id, "created_at")
    
    clients = await oClients.get_data()
    places = await oPlaces.get_list_data_by_with_order("user_id", current_user.id, "index")
    client = None

    if event == "show-client":
        client = await oClients.get_data_by("id", selected_place.client_id)

    tmp_first_name = request.session.get('tmp_first_name', '')
    first_name_message = request.session.pop('first_name_message', '')
    tmp_last_name = request.session.get('tmp_last_name', '')
    last_name_message = request.session.pop('last_name_message', '')
    tmp_phone = request.session.get('tmp_phone', '')
    phone_message = request.session.pop('phone_message', '')

    return templates.TemplateResponse(
        "pages/parking/parking.html",
        context={
            "request": request,
            "current_page": current_dir_many,
            "current_user": current_user,
            "title": current_dir_many.title(),
            "success_message": success_message,
            "place": place,
            "event": event,
            "type": type,
            "selected_place": selected_place,
            "services_for_selected_place": services_for_selected_place,
            "place_services": place_services,
            "clients": clients,
            "places": places,
            "client": client,

            "tmp_first_name": tmp_first_name,
            "first_name_message": first_name_message,
            "tmp_last_name": tmp_last_name,
            "last_name_message": last_name_message,
            "tmp_phone": tmp_phone,
            "phone_message": phone_message

        }
    )

# ADD NEW CLIENT
@router.post("/{place}/{event}/{type}/add-new-client")
async def data_root(
    request: Request,
    place: str,
    event: str,
    type: str,
    first_name: str = Form(None),
    last_name: str = Form(None),
    phone: str = Form(None),
    current_user: User = Depends(auth_service.get_current_user)
    ):

    request.session['tmp_first_name'] = first_name
    request.session['tmp_last_name'] = last_name
    request.session['tmp_phone'] = phone

    if not current_user:
        request.session['link_from'] = str(request.url)
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)
    
    if not first_name:
        request.session['first_name_message'] = "Please enter first name!"
        return RedirectResponse(url=f"/parking?place={place}&event={event}&type={type}", status_code=status.HTTP_302_FOUND)
    
    if not last_name:
        request.session['last_name_message'] = "Please enter last name!"
        return RedirectResponse(url=f"/parking?place={place}&event={event}&type={type}", status_code=status.HTTP_302_FOUND)

    if not phone:
        request.session['phone_message'] = "Please enter phone!"
        return RedirectResponse(url=f"/parking?place={place}&event={event}&type={type}", status_code=status.HTTP_302_FOUND)


    client = await oClients.get_data_by("phone", phone.strip())
    selected_place = await oPlaces.get_data_by("unique_key", place)
    
    if not place:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page not found")

    if client:
        place_fields = {
            "available": False,
            "client_id": client.id
        }
        await oPlaces.update_data_by_fields(selected_place.id, place_fields)
        
        request.session.clear()
        request.session['success-message'] = f'Client successfully added and set place!'
        return RedirectResponse(url=f"/parking", status_code=status.HTTP_302_FOUND)
    else:
        unique_code = uuid.uuid4().hex
        new_client = ClientModel(
            unique_code=unique_code,
            first_name=first_name,
            last_name=last_name,
            email=None,
            phone=phone,
            car_brand=None,
            car_model=None,
            car_year=None,
            plate=None,
            color="black",
            user_id=current_user.id,
        )

        created_client = await oClients.create(new_client)
        
        place_fields = {
            "available": False,
            "client_id": created_client.id
        }
        await oPlaces.update_data_by_fields(selected_place.id, place_fields)

        request.session.clear()
        request.session['success-message'] = f'Client successfully added and set place!'
        return RedirectResponse(url=f"/parking", status_code=status.HTTP_302_FOUND)



# ADD EXISTING CLIENT
@router.post("/{place}/{event}/{type}/add-existing-client")
async def data_root(
    request: Request,
    place: str,
    event: str,
    type: str,
    phone: str = Form(None),
    current_user: User = Depends(auth_service.get_current_user)
    ):

    request.session['tmp_phone'] = phone

    if not current_user:
        request.session['link_from'] = str(request.url)
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)
    
    if not phone:
        request.session['phone_message'] = "Please enter phone!"
        return RedirectResponse(url=f"/parking?place={place}&event={event}&type={type}", status_code=status.HTTP_302_FOUND)


    client = await oClients.get_data_by("phone", phone.strip())
    selected_place = await oPlaces.get_data_by("unique_key", place)
    
    if not selected_place:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page not found")

    if not client:
        request.session['phone_message'] = "Client with this phone is not found!"
        return RedirectResponse(url=f"/parking?place={place}&event={event}&type={type}", status_code=status.HTTP_302_FOUND)

    place_fields = {
        "available": False,
        "client_id": client.id
    }
    await oPlaces.update_data_by_fields(selected_place.id, place_fields)
    
    request.session.clear()
    request.session['success-message'] = f'Client successfully added and set place!'
    return RedirectResponse(url=f"/parking", status_code=status.HTTP_302_FOUND)



# CREATE PLACE SERVICE
@router.get("/{event}/{place_code}/{service_id}/turn-on")
async def data_root(
    request: Request,
    event: str,
    place_code: str,
    service_id: int,
    current_user: User = Depends(auth_service.get_current_user)
    ):
    if not current_user:
        request.session['link_from'] = str(request.url)
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)

    place = await oPlaces.get_data_by("unique_key", place_code)
    service = await oServices.get_data_by("id", service_id)

    if not place or not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page not found")
    
    place_service = PlaceServiceModel(
        place_id=place.id,
        service_id=service.id,
        service_active=True
    )
    new_place_service = await oPlaceServices.create(place_service)
    return RedirectResponse(url=f"/parking?place={place.unique_key}&event={event}", status_code=status.HTTP_302_FOUND) 


# TURN OFF PLACE SERVICE
@router.get("/{event}/{place_code}/{place_service_id}/turn-off")
async def data_root(
    request: Request,
    event: str,
    place_code: str,
    place_service_id: int,
    current_user: User = Depends(auth_service.get_current_user)
    ):
    if not current_user:
        request.session['link_from'] = str(request.url)
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)

    place = await oPlaces.get_data_by("unique_key", place_code)
    place_service = await oPlaceServices.get_data_by("id", place_service_id)

    if not place or not place_service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page not found")

    fields = {
        "service_active": False
    }
    
    await oPlaceServices.update_data_by_fields(place_service.id, fields)

    return RedirectResponse(url=f"/parking?place={place.unique_key}&event={event}", status_code=status.HTTP_302_FOUND) 



# TURN IN PLACE SERVICE
@router.get("/{event}/{place_code}/{place_service_id}/turnon")
async def data_root(
    request: Request,
    event: str,
    place_code: str,
    place_service_id: int,
    current_user: User = Depends(auth_service.get_current_user)
    ):
    if not current_user:
        request.session['link_from'] = str(request.url)
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)

    place = await oPlaces.get_data_by("unique_key", place_code)
    place_service = await oPlaceServices.get_data_by("id", place_service_id)

    if not place or not place_service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page not found")

    fields = {
        "service_active": True
    }
    
    await oPlaceServices.update_data_by_fields(place_service.id, fields)

    return RedirectResponse(url=f"/parking?place={place.unique_key}&event={event}", status_code=status.HTTP_302_FOUND) 






# DELETE CLIENT FORM PLACE
@router.get("/{event}/{place_code}/delete-client/clean")
async def data_root(
    request: Request,
    event: str,
    place_code: str,
    current_user: User = Depends(auth_service.get_current_user)
    ):
    if not current_user:
        request.session['link_from'] = str(request.url)
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)

    place = await oPlaces.get_data_by("unique_key", place_code)

    if not place:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page not found")
    

    await oPlaces.update_data_by_fields(place.id, {"available": True, "client_id": None, "start_date": None, "end_date": None, "price": None})

    return RedirectResponse(url=f"/parking?place={place.unique_key}&event=add-client&type=new-client", status_code=status.HTTP_302_FOUND) 



# SET DATE
@router.get("/{event}/{place_code}/date/set-date")
async def set_date(
    request: Request,
    event: str,
    place_code: str,
    current_user: User = Depends(auth_service.get_current_user)
    ):
    if not current_user:
        request.session['link_from'] = str(request.url)
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)

    place = await oPlaces.get_data_by("unique_key", place_code)

    if not place:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page not found")
    
    tmp_start_date = request.session.get("tmp_start_date", "")
    start_date_message = request.session.pop("start_date_message", "")
    
    tmp_end_date = request.session.get("tmp_end_date", "")
    end_date_message = request.session.pop("end_date_message", "")

    return templates.TemplateResponse(
        "pages/parking/set-date.html",
        context={
            "request": request,
            "current_page": current_dir_many,
            "current_user": current_user,
            "title": current_dir_many.title() + " - Set date",
            "place": place,
            "event": event,
            "tmp_start_date": tmp_start_date,
            "start_date_message": start_date_message,
            "tmp_end_date": tmp_end_date,
            "end_date_message": end_date_message,
        }
    )

# SET DATE POST
@router.post("/{event}/{place_code}/date/set-date/success")
async def set_date_success(
    request: Request,
    event: str,
    place_code: str,
    start_date: str = Form(None),
    end_date: str = Form(None),
    current_user: User = Depends(auth_service.get_current_user)
    ):
    if not current_user:
        request.session['link_from'] = str(request.url)
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)

    place = await oPlaces.get_data_by("unique_key", place_code)

    if not place:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page not found")
    
    if place.available:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="You need add client to this place first!")
    
    if not start_date:
        request.session["start_date_message"] = "Please select Start Date!"
        return RedirectResponse(url=f"/parking/{event}/{place_code}/date/set-date", status_code=status.HTTP_302_FOUND)
    
    if not end_date:
        request.session["end_date_message"] = "Please select End Date!"
        return RedirectResponse(url=f"/parking/{event}/{place_code}/date/set-date", status_code=status.HTTP_302_FOUND) 

    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    if start_date > end_date:
        request.session["start_date_message"] = "Please select Start Date less then End Date!"
        request.session["end_date_message"] = "Please select End Date more the Start Date!"
        return RedirectResponse(url=f"/parking/{event}/{place_code}/date/set-date", status_code=status.HTTP_302_FOUND) 
    
    update_fields = {
        "start_date": start_date,
        "end_date": end_date
    }

    await oPlaces.update_data_by_fields(place.id, update_fields)
    return RedirectResponse(url=f"/parking?place={place.unique_key}&event=show-client", status_code=status.HTTP_302_FOUND) 