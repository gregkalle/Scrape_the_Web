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
