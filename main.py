from fastapi import FastAPI, HTTPException
from datetime import datetime, timedelta
import calendar
from pydantic import BaseModel
from typing import List

app = FastAPI()

US_HOLIDAYS = {
    "New Year's Day": "01-01",
    "Martin Luther King Jr. Day": "third_monday_january",
    "Presidents' Day": "third_monday_february",
    "Memorial Day": "last_monday_may",
    "Independence Day": "07-04",
    "Labor Day": "first_monday_september",
    "Columbus Day": "second_monday_october",
    "Veterans Day": "11-11",
    "Thanksgiving Day": "fourth_thursday_november",
    "Christmas Day": "12-25"
}

class PaymentRequest(BaseModel):
    debt: float
    start_date: str  # YYYY-MM-DD format
    weeks: int

class PaymentResponse(BaseModel):
    payments: List[dict]

def get_nth_weekday_of_month(year, month, n, weekday):
    first_day = datetime(year, month, 1)
    first_weekday = first_day.weekday()
    days_to_add = (weekday - first_weekday) % 7 + (n - 1) * 7
    return first_day + timedelta(days=days_to_add)

def get_holiday_dates(year):
    holiday_dates = set()
    for rule in US_HOLIDAYS.values():
        if rule in {"01-01", "07-04", "11-11", "12-25"}:
            holiday_dates.add(datetime.strptime(f"{year}-{rule}", "%Y-%m-%d"))
        else:
            parts = rule.split("_")
            week_order = {"first": 1, "second": 2, "third": 3, "fourth": 4, "last": -1}[parts[0]]
            month = list(calendar.month_name).index(parts[2].capitalize())
            weekday = list(calendar.day_name).index(parts[1].capitalize())
            holiday_dates.add(get_nth_weekday_of_month(year, month, week_order, weekday))
    return holiday_dates

def is_holiday(date):
    return date in get_holiday_dates(date.year)

def get_payment_dates(start_date, weeks):
    payment_dates = []
    current_date = start_date
    for _ in range(weeks):
        while current_date.weekday() >= 5 or is_holiday(current_date):  
            current_date += timedelta(days=1)
        payment_dates.append(current_date)
        
        days_added = 0
        while days_added < 5:
            current_date += timedelta(days=1)
            if current_date.weekday() < 5 and not is_holiday(current_date):
                days_added += 1
    return payment_dates

@app.post("/calculate-payments", response_model=PaymentResponse)
def calculate_payments(request: PaymentRequest):
    if request.debt < 30000:
        raise HTTPException(status_code=400, detail="Debt amount must be at least $30,000")
    
    try:
        start_date = datetime.strptime(request.start_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    payment_dates = get_payment_dates(start_date, request.weeks)
    
    A = request.debt * 0.6  
    C = request.debt * 0.1  
    K = A / request.weeks  
    L = 15000 / 8  
    Z = C / request.weeks  
    
    payments = []
    for i, payment_date in enumerate(payment_dates):
        total_payment = K + Z if i >= 8 else K + L + Z
        payments.append({
            "date": payment_date.strftime('%Y-%m-%d'),
            "day": payment_date.strftime('%A'),
            "amount": round(total_payment, 2)
        })
    
    return {"payments": payments}
