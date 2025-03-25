import random
import string
import uuid
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
from src.services.authorization import auth_service
from src.repositories.rp_clients import oClients
from src.schemas.clients.clients_schema import ClientModel
from src.repositories.rp_places import oPlaces



current_dir_many = "clients"
current_dir_one = "client"

router = APIRouter(prefix=f"/{current_dir_many}")
templates = Jinja2Templates(directory="templates")
router.mount('/static', StaticFiles(directory="static"), name='static')

faker = Faker("en_US")


# DATA
@router.get("")
async def data_root(
    request: Request,
    page: int = Query(1, alias="page"),
    page_size: int = Query(8, alias="page_size"),
    current_user: User = Depends(auth_service.get_current_user)
    ):

    if not current_user:
        request.session['link_from'] = str(request.url)
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)
    
    success_message = request.session.pop("success-message", "")
    
    # Пагинация
    skip = (page - 1) * page_size
    clients = await oClients.get_data_with_pagination_by(by={"user_id": current_user.id},skip=skip, limit=page_size)

    # Получаем общее количество записей для расчета количества страниц
    total_clients = await oClients.get_total_count()  # Предположим, что такой метод существует
    total_pages = (total_clients + page_size - 1) // page_size

    return templates.TemplateResponse(
        f"pages/{current_dir_many}/{current_dir_many}.html",
        context={
            "request": request,
            "current_page": current_dir_many,
            "current_dir_many": current_dir_many,
            "current_user": current_user,
            "title": current_dir_many.title(),
            "success_message": success_message,
            "clients": clients,
            
            # PAGINATION
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }
    )

# DATA CREATE GET
@router.get("/new")
async def data_create_get(
    request: Request,
    current_user: User = Depends(auth_service.get_current_user)
    ):

    if not current_user:
        request.session['link_from'] = str(request.url)
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)
    
    success_message = request.session.pop("success-message", "")
    date = datetime.now()


    first_name = request.session.get('tmp_first_name', '')
    first_name_message = request.session.pop('first_name_message', '')

    last_name = request.session.get("tmp_last_name", "")
    last_name_message = request.session.pop('last_name_message', '')

    email = request.session.get("tmp_email", "")
    email_message = request.session.pop('email_message', '')

    phone = request.session.get("tmp_phone", "")
    phone_message = request.session.pop('phone_message', '')

    car_brand = request.session.get("tmp_car_brand", "")
    car_brand_message = request.session.pop('car_brand_message', '')

    car_model = request.session.get("tmp_car_model", "")
    car_model_message = request.session.pop('car_model_message', '')

    year = request.session.get("tmp_year", "")
    year_message = request.session.pop('year_message', '')

    plate = request.session.get("tmp_plate", "")
    plate_message = request.session.pop('plate_message', '')

    color = request.session.get("tmp_color", "")
    color_message = request.session.pop('color_message', '')
    


    return templates.TemplateResponse(
        f"pages/{current_dir_many}/create.html",
        context={
            "request": request,
            "current_page": current_dir_many,
            "current_user": current_user,
            "title": "Adding new client",
            "success_message": success_message,
            "current_dir_one": current_dir_one,
            "current_dir_many": current_dir_many,
            "date": date,


            "first_name": first_name,
            "first_name_message": first_name_message,

            "last_name": last_name,
            "last_name_message": last_name_message,

            "email": email,

            "phone": phone,
            "phone_message": phone_message,

            "car_brand": car_brand,
            "car_brand_message": car_brand_message,

            "car_model": car_model,
            "car_model_message": car_model_message,

            "year": year,
            "year_message": year_message,

            "plate": plate,
            "plate_message": plate_message,

            "color": color,
            "color_message": color_message,
        }
    )



# DATA CREATE POST
@router.post("/new")
async def data_create_post(
    request: Request,
    first_name: str = Form(None),
    last_name: str = Form(None),
    email: str = Form(None),
    phone: str = Form(None),
    car_brand: str = Form(None),
    car_model: str = Form(None),
    year: str = Form(None),
    plate: str = Form(None),
    color: str = Form(None),
    current_user: User = Depends(auth_service.get_current_user)
    ):

    if not current_user:
        request.session['link_from'] = str(request.url)
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)
    
    request.session['tmp_first_name'] = first_name
    request.session['tmp_last_name'] = last_name
    request.session['tmp_email'] = email
    request.session['tmp_phone'] = phone
    request.session['tmp_car_brand'] = car_brand
    request.session['tmp_car_model'] = car_model
    request.session['tmp_year'] = year
    request.session['tmp_plate'] = plate
    request.session['tmp_color'] = color
    

    if not first_name:
        request.session['first_name_message'] = 'First name is required!'
        return RedirectResponse(url=f"/{current_dir_many}/new", status_code=status.HTTP_302_FOUND)

    if year == 'no-selected':
        request.session['year_message'] = 'Please choose year!'
        return RedirectResponse(url=f"/{current_dir_many}/new", status_code=status.HTTP_302_FOUND)

    if not color:
        request.session['color_message'] = 'Please choose color!'
        return RedirectResponse(url=f"/{current_dir_many}/new", status_code=status.HTTP_302_FOUND)

    unique_code = uuid.uuid4().hex

    exist_client_by_unique_code = await oClients.get_data_by("unique_code", unique_code)
    exist_client_by_email = await oClients.get_data_by("email", email.lower().strip())

    if exist_client_by_unique_code or exist_client_by_email:
        request.session['email'] = 'Client with this email already exist!'
        return RedirectResponse(url=f"/{current_dir_many}/new", status_code=status.HTTP_302_FOUND)

    new_client = ClientModel(
        unique_code=unique_code,
        first_name=first_name.strip().title(),
        last_name=last_name.strip().title(),
        email=email.strip().lower(),
        phone=phone.strip(),
        car_brand=car_brand.strip().lower(),
        car_model=car_model.strip().lower(),
        car_year=year,
        plate=plate.strip().upper(),
        color=color
    )

    await oClients.create(new_client)

    request.session.clear()
    request.session['success-message'] = f'Client successfully added!'
    return RedirectResponse(url=f"/clients", status_code=status.HTTP_302_FOUND)


# DATA GENERATE GET
@router.get("/generate/{count}")
async def data_generate(request: Request, count: int, current_user: User = Depends(auth_service.get_current_user)):


    if not count and not isinstance(count, int):
        request.session['success-message'] = f'Please use correct count for generate clients!'
        return RedirectResponse('/{current_dir_many}')


    GENERATED_CLIENTS = []

    for i in range(1, count):
        unique_code = uuid.uuid4().hex

        first_name = faker.first_name()
        last_name = faker.last_name()
        email = f'{first_name.lower()}_{last_name.lower()}@{random.choice(domains)}'
        phone = "+1" + faker.numerify("###########")
        car_brand = random.choice(list(cars.keys()))
        car_model = random.choice(cars.get(car_brand))
        car_year = random.choice(years)
        plate = ''.join(random.choices(string.ascii_letters + string.digits, k=5))
        color = random.choice(colors)

        exist_client_by_unique_code = await oClients.get_data_by("unique_code", unique_code)
        exist_client_by_email = await oClients.get_data_by("email", email.lower().strip())

        if exist_client_by_unique_code or exist_client_by_email:
            request.session['email'] = 'Client with this email already exist!'
            return RedirectResponse(url=f"/{current_dir_many}/new", status_code=status.HTTP_302_FOUND)
        
        new_client = ClientModel(
            unique_code=unique_code,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            car_brand=car_brand,
            car_model=car_model,
            car_year=str(car_year),
            plate=plate,
            color=color,
            user_id=current_user.id,
        )

        GENERATED_CLIENTS.append(new_client)


    await oClients.bulk_create(GENERATED_CLIENTS)

    

    request.session.clear()
    request.session['success-message'] = f'{count} Clients successfully added!'
    return RedirectResponse(url=f"/{current_dir_many}", status_code=status.HTTP_302_FOUND)




# UPDATE GET
@router.get("/update/{data_key}")
async def data_update_page(
    request: Request,
    data_key: str,
    current_user: User = Depends(auth_service.get_current_user)
    ):
    if not current_user:
        request.session['link_from'] = str(request.url)
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)
    
    date = datetime.now()
    data = await oClients.get_data_by("unique_code", data_key)

    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    name_message = request.session.pop("name_message", '')
    count_place_message = request.session.pop("count_place_message", '')
    price_per_place_message = request.session.pop("price_per_place_message", '')

    return templates.TemplateResponse(
        f"pages/{current_dir_many}/update.html",
        context={
            "request": request,
            "current_page": current_dir_many,
            "current_user": current_user,
            "current_dir_many": current_dir_many,
            "title": current_dir_many.title(),
            "client": data,
            "date": date,
            
            # Messages
            "name_message": name_message,
            "count_place_message": count_place_message,
            "price_per_place_message": price_per_place_message,

        }
    )


# DATA UPDATE POST
@router.post("/update/{data_key}")
async def data_update_post(
    request: Request,
    data_key: str,
    first_name: str = Form(None),
    last_name: str = Form(None),
    email: str = Form(None),
    phone: str = Form(None),
    car_brand: str = Form(None),
    car_model: str = Form(None),
    year: str = Form(None),
    plate: str = Form(None),
    color: str = Form(None),
    current_user: User = Depends(auth_service.get_current_user)
    ):

    if not current_user:
        request.session['link_from'] = str(request.url)
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)
    
    current_data = await oClients.get_data_by("unique_code", data_key)

    if not current_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    if not first_name:
        request.session['first_name_message'] = 'First name is required!'
        return RedirectResponse(url=f"/{current_dir_many}/update/{data_key}", status_code=status.HTTP_302_FOUND)
    
    if year == 'no-selected':
        request.session['year_message'] = 'Please choose year!'
        return RedirectResponse(url=f"/{current_dir_many}/update/{data_key}", status_code=status.HTTP_302_FOUND)

    if not color:
        request.session['color_message'] = 'Please choose color!'
        return RedirectResponse(url=f"/{current_dir_many}/update/{data_key}", status_code=status.HTTP_302_FOUND)
    
    if not phone:
        request.session['phone_message'] = 'Phone is required!'
        return RedirectResponse(url=f"/{current_dir_many}/update/{data_key}", status_code=status.HTTP_302_FOUND)

    update_data = ClientModel(
        unique_code=current_data.unique_code,
        first_name=first_name.strip().title(),
        last_name=last_name.strip().title(),
        email=email,
        phone=phone,
        car_brand=car_brand,
        car_model=car_model,
        car_year=year,
        plate=plate,
        color=color,
        user_id=current_user.id
    )
    await oClients.update_data(current_data.id, update_data)

    request.session.clear()
    request.session['success-message'] = f'Successfully saved!'
    return RedirectResponse(url=f"/{current_dir_many}", status_code=status.HTTP_302_FOUND)



