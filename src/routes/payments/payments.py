
import random
import string
import uuid
import time
from datetime import datetime, timedelta


from fastapi import APIRouter, Request, Form, Depends, status, HTTPException, Query, BackgroundTasks
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from faker import Faker

from src.data.cars import cars
from src.data.domains import domains
from src.data.years import years
from src.data.colors import colors
from src.db.models import User
from src.repositories.rp_plans import oPlans
from src.services.authorization import auth_service
from src.repositories.rp_clients import oClients
from src.schemas.clients.clients_schema import ClientModel
from src.repositories.rp_places import oPlaces
from src.repositories.rp_place_service import oPlaceServices
from src.repositories.rp_users import oUsers
from src.services.gmailer.gmailer import MAILER
from src.utils.elementaries import calculate_period_months



current_dir_many = "payments"
current_dir_one = "payment"

router = APIRouter(prefix=f"/{current_dir_many}")
templates = Jinja2Templates(directory="templates")
router.mount('/static', StaticFiles(directory="static"), name='static')

faker = Faker("en_US")



@router.get("/{client_unique_code}/send-email/send-check")
async def send_email_test(
    request: Request,
    background_tasks: BackgroundTasks,
    client_unique_code: str,
    ):
    
    client = await oClients.get_data_by("unique_code", client_unique_code)
    place = await oPlaces.get_data_by("client_id", client.id)
    plan = await oPlans.get_data_by("id", place.user.plan_id)
    period = calculate_period_months(place)

    email_token = await auth_service.create_token(data={"sub": "i.gerenzeo@gmail.com"}, scope="email_token", exp_delta=int(5000))

    place_services = await oPlaceServices.get_list_data_by("place_id", place.id)

    context = {
        "request": request,
        "email_token": email_token,
        "time_token": 5000,
        "plan": plan,
        "place": place,
        "count_month": period,
        "recipient": client,
        "place_services": place_services,
    }
    
    subject = "Parking Space Payment Reminder"
    background_tasks.add_task(MAILER.send_mail, "i.gerenzeo@gmail.com", subject, context=context)

    request.session.clear()
    request.session['success-message'] = f"{subject} was successfully sended!"
    return RedirectResponse(url="/parking", status_code=status.HTTP_302_FOUND)

    # return templates.TemplateResponse(
    #     f"emails_tmp/client-check.html",
    #     context={
    #         "request": request,
    #         "current_page": current_dir_many,
    #         "current_dir_many": current_dir_many,
    #         "title": current_dir_many.title(),
    #         "request": request,
    #         "email_token": email_token,
    #         "time_token": 5000,
    #         "plan": plan,
    #         "place": place,
    #         "count_month": period,
    #         "recipient": client,
    #         "place_services": place_services,
    #     }
    # )


# SEND CHECK
# CHANGET TO TOKEN
@router.get("/check-{client_key}-{place_key}/payment-{token}")
async def payment_page(
    request: Request,
    client_key: str,
    place_key: str,
    token: str,
    ):
    
    client_from_token = await auth_service.get_email_from_token(token=token)
    if not client_from_token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page not found!")

    date = datetime.now()
    place = await oPlaces.get_data_by("unique_key", place_key)
    client = await oClients.get_data_by("unique_code", client_key)
    
    if not place or not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        
    plan = await oPlans.get_data_by("id", place.user.plan_id)
    return templates.TemplateResponse(
        f"pages/{current_dir_many}/check.html",
        context={
            "request": request,
            "current_page": current_dir_many,
            "current_dir_many": current_dir_many,
            "title": current_dir_many.title(),
            "place": place,
            "client": client,
            "date": date,
            "plan": plan,
        }
    )