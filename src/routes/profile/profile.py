from datetime import datetime

from fastapi import APIRouter, Request, Form, Depends, status, HTTPException, Query
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from faker import Faker

from src.data.cars import cars
from src.data.domains import domains
from src.data.years import years
from src.data.colors import colors
from src.db.models import User
from src.repositories.rp_app import oApp
from src.repositories.rp_plans import oPlans
from src.services.authorization import auth_service
from src.repositories.rp_clients import oClients
from src.schemas.clients.clients_schema import ClientModel
from src.repositories.rp_users import oUsers




router = APIRouter(prefix=f"")
templates = Jinja2Templates(directory="templates")
router.mount('/static', StaticFiles(directory="static"), name='static')


@router.get("/profile")
async def profile_root(
    request: Request,
    tab: str = Query(None, alias="tab"),
    method: str = Query(None, alias="method"),
    current_user: User = Depends(auth_service.get_current_user)
):
    if not current_user:
        request.session['link_from'] = str(request.url)
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)
    
    if tab is None or tab not in ["general", "payments", "plan", "settings"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page not found")
    
    plan = await oPlans.get_data_by("id", current_user.plan_id)
    success_message = request.session.pop("success-message", "")

    card_number = request.session.get('tmp_card_number', '')
    card_number_message = request.session.pop('card_number_message', '')
 
    card_cvv = request.session.get('tmp_card_cvv', '')
    card_cvv_message = request.session.pop('card_cvv_message', '')

    card_mounth = request.session.get('tmp_card_mounth', '')
    card_mounth_message = request.session.pop('card_mounth_message', '')

    card_year = request.session.get('tmp_card_year', '')
    card_year_message = request.session.pop('card_year_message', '')

    cash_message = request.session.pop("cash_message", '')
    phone_message = request.session.pop("phone-message", '')
    
    return templates.TemplateResponse(
        "pages/users/profile.html",
        context={
            "request": request,
            "current_page": "profile",
            "current_user": current_user,
            "success_message": success_message,
            "title": "Profile",
            "plan": plan,
            "tab": tab,
            "method": method,

            "tmp_card_number": card_number,
            "card_number_message": card_number_message,

            "tmp_card_cvv": card_cvv,
            "card_cvv_message": card_cvv_message,

            "tmp_card_mounth": card_mounth,
            "card_mounth_message": card_mounth_message,

            "tmp_card_year": card_year,
            "card_year_message": card_year_message,

            "cash_message": cash_message,
            "phone_message": phone_message,
        }
    )

@router.post("/add-payment-card")
async def add_card(
    request: Request,
    card_number: str = Form(None),
    card_cvv: str = Form(None),
    card_mounth: str = Form(None),
    card_year: str = Form(None),
    current_user: User = Depends(auth_service.get_current_user)
):
    
    if not current_user:
        request.session['link_from'] = str(request.url)
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)
    
    request.session['tmp_card_number'] = card_number
    request.session['tmp_card_cvv'] = card_cvv
    request.session['tmp_card_mounth'] = card_mounth
    request.session['tmp_card_year'] = card_year


    if not card_number:
        request.session['card_number_message'] = 'Write corrent card number!'
        return RedirectResponse(url=f"/profile?tab=payments&method=transfer", status_code=status.HTTP_302_FOUND)
    
    if not len(card_number) == 19:
        request.session['card_number_message'] = 'Please write correct card number! Length(19)'
        return RedirectResponse(url=f"/profile?tab=payments&method=transfer", status_code=status.HTTP_302_FOUND)
    
    if not card_cvv:
        request.session['card_cvv_message'] = 'CVV is required!'
        return RedirectResponse(url=f"/profile?tab=payments&method=transfer", status_code=status.HTTP_302_FOUND)
    
    if not len(card_cvv) == 3:
        request.session['card_cvv_message'] = 'CVV should be 3 numeric!'
        return RedirectResponse(url=f"/profile?tab=payments&method=transfer", status_code=status.HTTP_302_FOUND)
    
    if not card_mounth:
        request.session['card_mounth_message'] = 'Please select mounth!'
        return RedirectResponse(url=f"/profile?tab=payments&method=transfer", status_code=status.HTTP_302_FOUND)
    
    if not card_year:
        request.session['card_year_message'] = 'Please select year!'
        return RedirectResponse(url=f"/profile?tab=payments&method=transfer", status_code=status.HTTP_302_FOUND)

    update_data = {
        "card_number": card_number,
        "card_expired_date": f"{card_mounth}/{card_year}",
        "card_cvv": int(card_cvv)
    }

    await oUsers.update_data_by_fields(current_user.id, update_data)
    request.session.clear()
    request.session['success-message'] = f'Card data was accepted!'
    return RedirectResponse(url=f"/profile?tab=payments&method=transfer", status_code=status.HTTP_302_FOUND)


# CLEAR CARD
@router.get("/delete-payment-card")
async def data_delete(
    request: Request,
    current_user: User = Depends(auth_service.get_current_user)
):  
    if not current_user:
        request.session['link_from'] = str(request.url)
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)
    
    update_data = {
        "card_number": None,
        "card_expired_date": None,
        "card_cvv": None,
    }

    await oUsers.update_data_by_fields(current_user.id, update_data)
    request.session.clear()
    request.session['success-message'] = f'Card data was sucessfully cleared!'
    return RedirectResponse(url=f"/profile?tab=payments&method=transfer", status_code=status.HTTP_302_FOUND)


# DEPOSIT CASH TO CARD
@router.post("/profile/{method}/deposit-money")
async def cash_to_card(
    request: Request,
    method: str,
    cash: str = Form(None),
    current_user: User = Depends(auth_service.get_current_user)
):  
    if not current_user:
        request.session['link_from'] = str(request.url)
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)
    
    if not method == 'deposit':
        request.session['success-message'] = f'Something wrong!'
        return RedirectResponse(url=f"/profile?tab=payments&method=deposit", status_code=status.HTTP_302_FOUND)

    if not current_user.card_number:
        request.session['success-message'] = f'Please add card first!'
        return RedirectResponse(url=f"/profile?tab=payments&method=deposit", status_code=status.HTTP_302_FOUND)

    if not cash:
        request.session['cash_message'] = f'Please enter amount for deposit!'
        return RedirectResponse(url=f"/profile?tab=payments&method=deposit", status_code=status.HTTP_302_FOUND)

    update_data = {
        "balance": current_user.balance + int(cash)
    }

    await oUsers.update_data_by_fields(current_user.id, update_data)
    request.session.clear()
    request.session['success-message'] = f'Funds successfully received!'
    return RedirectResponse(url=f"/profile?tab=payments&method=deposit", status_code=status.HTTP_302_FOUND)



# TRANSFER CASH FROM ACCOUNT
@router.post("/profile/{method}/transfer-money")
async def transfer_cash_from_account(
    request: Request,
    method: str,
    cash: str = Form(None),
    current_user: User = Depends(auth_service.get_current_user)
):  
    if not current_user:
        request.session['link_from'] = str(request.url)
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)
    
    if not method == 'transfer':
        request.session['success-message'] = f'Something wrong!'
        return RedirectResponse(url=f"/profile?tab=payments&method=transfer", status_code=status.HTTP_302_FOUND)

    if not cash:
        request.session['cash_message'] = f'Please enter amount for transfer!'
        return RedirectResponse(url=f"/profile?tab=payments&method=transfer", status_code=status.HTTP_302_FOUND)

    if not current_user.card_number:
        request.session['success-message'] = f'Please add card first!'
        return RedirectResponse(url=f"/profile?tab=payments&method=deposit", status_code=status.HTTP_302_FOUND)

    if int(cash) > current_user.balance:
        request.session['cash_message'] = f'There is less money in your account! Your max is {current_user.balance}$'
        return RedirectResponse(url=f"/profile?tab=payments&method=transfer", status_code=status.HTTP_302_FOUND)
    

    update_data = {
        "balance": current_user.balance - int(cash)
    }

    await oUsers.update_data_by_fields(current_user.id, update_data)
    request.session.clear()
    request.session['success-message'] = f'Funds successfully transfered to your card!'
    return RedirectResponse(url=f"/profile?tab=payments&method=transfer", status_code=status.HTTP_302_FOUND)




@router.post("/profile/{tab}/update-phone")
async def update_user_phone(
    request: Request,
    tab: str,
    phone: str = Form(None),
    current_user: User = Depends(auth_service.get_current_user)
):
    
    if not current_user:
        request.session['link_from'] = str(request.url)
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)
    
    if not tab == "general":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page not found")
    
    if not phone:
        request.session['phone-message'] = f'Please enter your phone!'
        return RedirectResponse(url=f"/profile?tab=general", status_code=status.HTTP_302_FOUND)

    await oUsers.update_data_by_fields(current_user.id, {"phone": phone})
    request.session['success-message'] = f'Phone successfully added!'
    return RedirectResponse(url=f"/profile?tab=general", status_code=status.HTTP_302_FOUND)
