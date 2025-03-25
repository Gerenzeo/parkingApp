import uuid

from fastapi import APIRouter, Request, Form, Depends, status, HTTPException, Query
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from src.db.models import User
from src.services.authorization import auth_service
from src.repositories.rp_services import oServices
from src.repositories.rp_plans import oPlans
from src.repositories.rp_users import oUsers
from src.schemas.places.places_schema import PlaceModel
from src.repositories.rp_places import oPlaces
from src.repositories.rp_place_service import oPlaceServices
from src.utils.elementaries import get_current_user_or_redirect

current_dir_many = "orders"
current_dir_one = "order"

router = APIRouter(prefix=f"/{current_dir_many}")
templates = Jinja2Templates(directory="templates")
router.mount('/static', StaticFiles(directory="static"), name='static')



# ORDER PLAN GET
@router.get("")
async def orders_root(
    request: Request,
    current_user: User = Depends(get_current_user_or_redirect)
    ):

    if not current_user:
        request.session['link_from'] = str(request.url)
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)

    success_message = request.session.pop("success-message", "")

    return templates.TemplateResponse(
        f"pages/{current_dir_many}/orders.html",
        context={
            "request": request,
            "current_page": current_dir_many,
            "current_user": current_user,
            "title": current_dir_many.title(),
            "success_message": success_message,
        }
    ) 

# ORDER PLAN GET
@router.get("/order-plan")
async def order_plan_root(
    request: Request,
    name: str = Query(None),
    current_user: User = Depends(auth_service.get_current_user)
    ):

    if not current_user:
        request.session['link_from'] = str(request.url)
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)

    success_message = request.session.pop("success-message", "")
    count_place_message = request.session.pop('count_place_message', '')

    plans = await oPlans.get_data_order_by("position")
    
    if not name:
        selected_plan = None 

    selected_plan = await oPlans.get_data_by("code", name)
    
    return templates.TemplateResponse(
        f"pages/{current_dir_many}/order-plan.html",
        context={
            "request": request,
            "current_page": current_dir_many,
            "current_user": current_user,
            "title": current_dir_many.title(),
            "success_message": success_message,
            "plans": plans,
            "selected_plan": selected_plan,
            "count_place_message": count_place_message,
        }
    )


# # ORDER PLAN POST
@router.post("/order-plan-{plan_code}")
async def order_plan_post(
    request: Request,
    plan_code: str,
    count_place: int = Form(None),
    current_user: User = Depends(auth_service.get_current_user)
    ):

    if not current_user:
        request.session['link_from'] = str(request.url)
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)
    
    plan = await oPlans.get_data_by("code", plan_code)

    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page not found")

    if not count_place:
        request.session['count_place_message'] = f'Please write count of places!'
        return RedirectResponse(url=f"/orders/order-plan?name={plan_code}", status_code=status.HTTP_302_FOUND)
    
    if count_place < 5 or count_place > 100:
        request.session['count_place_message'] = f'Available from 5 to 100'
        return RedirectResponse(url=f"/orders/order-plan?name={plan_code}", status_code=status.HTTP_302_FOUND)

    if current_user.plan_id == plan.id:
        request.session['success-message'] = f'You can\'t buy selected plan! Please choose another plan!'
        return RedirectResponse(url=f"/orders/order-plan?name={plan_code}", status_code=status.HTTP_302_FOUND)
    
    if current_user.balance <= 0:
        request.session['count_place_message'] = f'Not enough funds on your balance!'
        return RedirectResponse(url=f"/orders/order-plan?name={plan_code}", status_code=status.HTTP_302_FOUND)

    if current_user.plan:
        if not plan.id == current_user.plan.id:
            await oPlaces.delete_all_data("user_id", current_user.id)

    total_price = sum(s.price for s in plan.services)

    user_update = {
        "balance": current_user.balance - total_price,
        "plan_id": plan.id,
        "count_place": count_place
    }
    await oUsers.update_data_by_fields(current_user.id, user_update)

    PLACES = [PlaceModel(
            unique_key=uuid.uuid4().hex,
            index=i,
            available=True,
            is_charger=False,
            next_to_exit=False,
            start_date=None,
            end_date=None,
            user_id=current_user.id,
        ) for i in range(1, count_place+1)]
    
    await oPlaces.bulk_create(PLACES)

    request.session.clear()
    request.session['success-message'] = f'Purchase successfully confirmed! Enjoy your parking!'
    return RedirectResponse(url=f"/", status_code=status.HTTP_302_FOUND)


    
    