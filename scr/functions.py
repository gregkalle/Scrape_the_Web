from datetime import date, timedelta
from time import mktime
import threading

def get_float(text:str)->float:
    digits = "".join([letter for letter in text if letter.isdigit() or letter in [".","-"]])
    try:
        return float(digits)
    except ValueError as exc:
        raise ValueError("Not a float.") from exc
    
def get_point_deci(text:str, change_comma:bool = True)->str:
    if change_comma:
        return text.replace(".","").replace(",",".")
    return text

def get_start_end_time(day:date=None)->tuple[int]:
    if day is None:
        day = date.today()
    end = day
    start = end - timedelta(days=1)

    end = int(mktime(end.timetuple())) - 1
    start = int(mktime(start.timetuple()))
    return start,end

#timeouted userinput
def user_input(prompt, timeout):
    def time_up():
        raise TimeoutError

    timer = threading.Timer(timeout, time_up)
    timer.start()

    try:
        user_response = input(prompt)
        timer.cancel()
        return user_response
    except TimeoutError as exc:
        raise TimeoutError() from exc
