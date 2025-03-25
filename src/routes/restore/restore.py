import pathlib
import json
import os

from fastapi import APIRouter, Request, Form, Depends, status, HTTPException, UploadFile, File
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from src.db.models import User
from src.services.authorization import auth_service
from src.repositories.rp_services import oServices
from src.repositories.rp_places import oPlaces
from src.schemas.services.services_schema import ServiceModel
from src.repositories.rp_clients import oClients


current_dir_many = "restore"
current_dir_one = "restore"

router = APIRouter(prefix=f"/{current_dir_many}")
templates = Jinja2Templates(directory="templates")
router.mount('/static', StaticFiles(directory="static"), name='static')


# RESTORE
@router.get("")
async def restore_route(
    request: Request,
    current_user: User = Depends(auth_service.get_current_user)
    ):

    if not current_user:
        request.session['link_from'] = str(request.url)
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)
    
    success_message = request.session.pop("success-message", "")
    
    json_error_message = request.session.pop("json-error-message", '')
    csv_error_message = request.session.pop("csv-error-message", '')

    return templates.TemplateResponse(
        f"pages/{current_dir_many}/{current_dir_many}.html",
        context={
            "request": request,
            "current_page": current_dir_many,
            "current_user": current_user,
            "title": current_dir_many.title(),
            "success_message": success_message,

            "json_error_message": json_error_message,
            "csv_error_message": csv_error_message,
        }
    )


# RESTORE FROM JSON
@router.post("/restore-from-json")
async def restore_from_json_route(
    request: Request,
    file: UploadFile = File(None),
    current_user: User = Depends(auth_service.get_current_user)
    ):

    if not current_user:
        request.session['link_from'] = str(request.url)
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)
    
    filename = file.filename
    file_content = await file.read() 

    if len(file_content) == 0:
        request.session['json-error-message'] = "No file selected! Or the file is empty! Please select a valid file."
        return RedirectResponse(url="/restore", status_code=status.HTTP_302_FOUND)
    
    file_extension = os.path.splitext(filename)[1].lower()

    if file_extension != ".json":
        request.session['json-error-message'] = "Invalid file type! Only .json files are allowed."
        return RedirectResponse(url="/restore", status_code=status.HTTP_302_FOUND)
    
    # Дальше можно обработать файл
    return {"filename": filename, "message": "File processed successfully"}


# DOWNLOAD TO JSON
@router.get("/download-json")
async def download_to_json_route(
    request: Request,
    current_user: User = Depends(auth_service.get_current_user)
    ):

    if not current_user:
        request.session['link_from'] = str(request.url)
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)
    

    clients = await oClients.get_json_data_by("user_id", current_user.id)
    places = await oPlaces.get_json_data_by("user_id", current_user.id)

    return {"clients": clients, "places": places}
    


    