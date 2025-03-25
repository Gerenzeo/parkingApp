import uuid

from fastapi import APIRouter, Request, Form, Depends, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from src.data.countries import COUNTRIES
from src.config.config import settings
from src.repositories.rp_users import oUsers
from src.repositories.rp_roles import oRoles
from src.services.authorization import auth_service
from src.schemas.users.users_schema import UserModel


router = APIRouter(prefix="/auth")
templates = Jinja2Templates(directory="templates")
router.mount('/static', StaticFiles(directory="static"), name='static')


# LOGIN GET PAGE
@router.get("/login")
async def auth_login(request: Request):

    registration_message = request.session.pop("success-registration", "")
    error_message = request.session.pop("error-message", "")

    tmp_email = request.session.get("tmp_email")
    email_message = request.session.pop("email_message", '')
    password_message = request.session.pop("password_message", '')

    return templates.TemplateResponse(
        "pages/auth/login.html",
        context={
            "request": request,
            "current_page": "login",
            "title": "Login",
            "registration_message": registration_message,
            "error_message": error_message,

            # Messages
            "email_message": email_message,
            "password_message": password_message,

            # Tmp data
            "tmp_email": tmp_email,
        }
    )

# SIGNUP GET PAGE
@router.get("/signup")
async def auth_signup(
    request: Request):
    
    tmp_first_name = request.session.get("tmp_first_name")
    first_name_message = request.session.pop("first_name_message", '')
    
    tmp_last_name = request.session.get("tmp_last_name")
    last_name_message = request.session.pop("last_name_message", '')

    tmp_email = request.session.get("tmp_email")
    email_message = request.session.pop("email_message", '')
    
    tmp_phone = request.session.get("tmp_phone")
    phone_message = request.session.pop("phone_message", '')

    tmp_country = request.session.get("tmp_country")
    country_message = request.session.pop("country_message", '')

    tmp_city = request.session.get("tmp_city")
    city_message = request.session.pop("city_message", '')
    

    password_message = request.session.pop("password_message", '')
    
    
    return templates.TemplateResponse(
        "pages/auth/signup.html",
        context={
            "request": request,
            "current_page": "signup",
            "title": "SignUp",
            "countries": COUNTRIES,

            # Messages
            "first_name_message": first_name_message,
            "last_name_message": last_name_message,
            "email_message": email_message,
            "phone_message": phone_message,
            "password_message": password_message,
            "country_message": country_message,
            "city_message": city_message,

            # Tmp data
            "tmp_first_name": tmp_first_name,
            "tmp_last_name": tmp_last_name,
            "tmp_email": tmp_email,
            "tmp_phone": tmp_phone,
            "tmp_country": tmp_country,
            "tmp_city": tmp_city,
        }
    )



# SIGNUP POST
@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def auth_signup_post(
    request: Request,
    first_name: str= Form(None),
    last_name: str= Form(None),
    email: str = Form(None),
    phone: str = Form(None),
    country: str = Form(None),
    city: str = Form(None),
    password: str = Form(None),
    confirm_password: str = Form(None)):

    request.session['tmp_first_name'] = first_name
    request.session['tmp_last_name'] = last_name
    request.session['tmp_email'] = email
    request.session['tmp_phone'] = phone
    request.session['tmp_country'] = country
    request.session['tmp_city'] = city

    if first_name is None:
        request.session["tmp_first_name"] = ""
        request.session["first_name_message"] = f'Please enter first name!'
        return RedirectResponse(url='/auth/signup', status_code=status.HTTP_302_FOUND)
    
    if last_name is None:
        request.session["tmp_last_name"] = ""
        request.session["last_name_message"] = f'Please enter last name!'
        return RedirectResponse(url='/auth/signup', status_code=status.HTTP_302_FOUND)
    
    if email is None:
        request.session["tmp_email"] = ""
        request.session["email_message"] = f'Please enter email!'
        return RedirectResponse(url='/auth/signup', status_code=status.HTTP_302_FOUND)
    
    if phone is None:
        request.session["tmp_phone"] = ""
        request.session["phone_message"] = f'Please enter phone!'
        return RedirectResponse(url='/auth/signup', status_code=status.HTTP_302_FOUND)
    
    if phone is None:
        request.session["tmp_phone"] = ""
        request.session["phone_message"] = f'Please enter phone!'
        return RedirectResponse(url='/auth/signup', status_code=status.HTTP_302_FOUND)
    
    existing_user = await oUsers.get_data_by("email", email.lower().strip())
    if existing_user:
        request.session["email_message"] = f'User with this email already exist!'
        return RedirectResponse(url='/auth/signup', status_code=status.HTTP_302_FOUND)

    if password is None or confirm_password is None:
        request.session["password_message"] = f'Enter password and confirm password!'
        return RedirectResponse(url='/auth/signup', status_code=status.HTTP_302_FOUND)

    if password and confirm_password and (not password == confirm_password):
        request.session['password_message'] = f'Passwords are dismatch!'
        return RedirectResponse(url='/auth/signup', status_code=status.HTTP_302_FOUND)
    
    

    password = auth_service.get_password_hash(password)
    unique_code = uuid.uuid4().hex
    existing_user_by_code = await oUsers.get_data_by("unique_code", unique_code)
    if existing_user_by_code:
        request.session['email_message'] = f'Please try this operation again! [Unqiue_key already exist!]'
        return RedirectResponse(url='/auth/signup', status_code=status.HTTP_302_FOUND)
    
    count_users = await oUsers.get_total_count()
    if count_users < 1:
        role = await oRoles.get_data_by("role_name", "superuser")
    else:
        role = await oRoles.get_data_by("role_name", "user")
    

    new_user = UserModel(
        unique_code=unique_code,
        full_name=f"{first_name.capitalize()} {last_name.capitalize()}",
        email=email.strip().lower(),
        phone=phone,
        country=country,
        city=city,
        password=password,
        role_id=role.id,
    )
    await oUsers.create(new_user)

    request.session.clear()
    request.session['success-registration'] = 'Registration complete! You can login!'
    return RedirectResponse(url='/auth/login', status_code=status.HTTP_302_FOUND)



@router.post('/login')
async def login_post(
    request: Request,
    email: str = Form(None),
    password: str = Form(None)
):
    if email is None:
        request.session["tmp_email"] = ""
        request.session["email_message"] = f'Please enter email!'
        return RedirectResponse(url='/auth/login', status_code=status.HTTP_302_FOUND)
    
    request.session['tmp_email'] = email.strip()
    
    if password is None:
        request.session["password_message"] = f'Please enter password and confirm password!'
        return RedirectResponse(url='/auth/login', status_code=status.HTTP_302_FOUND)

    user = await oUsers.get_data_by("email", email.strip().lower())
    if user and auth_service.verify_password(password, user.password):
        refresh_token = await auth_service.create_token(data={"sub": user.email}, scope="refresh_token", exp_delta=int(settings.refresh_token_time))
        await oUsers.update_data_by_fields(user.id, {"refresh_token": refresh_token})

        redirect_url = request.session.pop('link_from', "/")
        response = RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)
        response.set_cookie(settings.jwt_token, value=refresh_token, httponly=True)
        return response

    else:
        request.session['error-message'] = 'Not correct Email or Password!'
        return RedirectResponse(url='/auth/login', status_code=status.HTTP_302_FOUND)