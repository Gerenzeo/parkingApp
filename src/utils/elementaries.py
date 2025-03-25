from dateutil.relativedelta import relativedelta

from fastapi import Request, Depends, status, HTTPException
from fastapi.responses import RedirectResponse

from src.db.models import User
from src.services.authorization import auth_service

async def get_current_user_or_redirect(
    request: Request,
    current_user: User = Depends(auth_service.get_current_user)
):
    if not current_user:
        request.session['link_from'] = str(request.url)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Please login")
    return current_user


def calculate_period_months(place):
    start_date = place.start_date
    end_date = place.end_date
    period = relativedelta(end_date, start_date)
    
    return period.years * 12 + period.months
