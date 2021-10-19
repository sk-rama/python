import uvicorn
from fastapi import FastAPI, Path
from fastapi.responses import JSONResponse
import calendar
import datetime


def is_weekend(day_number: int) -> bool:
    ''' 
        date.isoweekday() - Return the day of the week as an integer, where Monday is 1 and Sunday is 7.
        For example, date(2002, 12, 4).isoweekday() == 3, a Wednesday
    '''
    year   = datetime.datetime.today().year 
    dt     = datetime.date(year, 1, 1) + datetime.timedelta(day_number - 1)
    number = dt.isoweekday()
    return number == 6 or number == 7


def daynumber_to_date(day_number: int) -> datetime.date:
    '''
        return datetime.date from start of actual year to days arg. 
        example: if actual year is 2021, daynumber_to_date(365) -> datetime.date(2021, 12, 31)
    '''
    year = datetime.datetime.today().year
    dt   = datetime.date(year, 1, 1) + datetime.timedelta(day_number - 1)
    return dt


def get_day_name(number: int) -> str:
    week_days = { 
        1: "Monday",
        2: "Tuesday",
        3: "Wednesday",
        4: "Thursday",
        5: "Friday",
        6: "Saturday",
        7: "Sunday"
    }
    return week_days[number]
   

app = FastAPI()


@app.get("/v1/api/date/{day_number}")
async def get_date(day_number: int = Path(..., gt=0, lt=367, title="Day number of the present year")):
    response = {}
    if (calendar.isleap(datetime.datetime.now().year) is False) and day_number > 365:
        return JSONResponse(
            status_code=422,
            content={"message": "day_number: Invalid day number",
                     "data": None},
        )
    elif (is_weekend(day_number) is True):
        return JSONResponse(
            status_code=422,
            content={"message": "day_number: Current day number is weekend day",
                     "data": None},
        )
    else:
        dt = daynumber_to_date(day_number)
        dn = dt.isoweekday()
        response['data'] = dt
        response['name'] = get_day_name(dn)
        response['message'] = "Successfully Computed!"
        return response


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
