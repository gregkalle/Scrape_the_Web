from datetime import date, timedelta
from time import mktime

def get_float(text:str)->float:
    """Converts a string to a float, extracting digits and handling errors.

    Args:
        text (str): The string to convert.

    Raises:
        ValueError: Not a float.

    Returns:
        float: The extracted float value.
    """
    digits = "".join([letter for letter in text if letter.isdigit() or letter in [".","-"]])
    try:
        return float(digits)
    except ValueError as exc:
        raise ValueError("Not a float.") from exc
    
def get_point_deci(text:str, change_comma:bool = True)->str:
    """Converts commas to decimal points in a string if specified.

    Args:
        text (str): The string to modify.
        change_comma (bool, optional): Whether to change commas to decimal points. Defaults to True.

    Returns:
        str: The modified string.
    """
    if change_comma:
        return text.replace(".","").replace(",",".")
    return text

def get_start_end_time(day:date=None)->tuple[int]:
    """Gets the start and end timestamps for a given day.

    Args:
        day (date, optional): The day to get the timestamps for. Defaults is today.

    Returns:
        tuple[int]: The start and end timestamps.
    """
    if day is None:
        day = date.today()
    end = day
    start = end - timedelta(days=1)

    end = int(mktime(end.timetuple())) - 1
    start = int(mktime(start.timetuple()))
    return start,end
