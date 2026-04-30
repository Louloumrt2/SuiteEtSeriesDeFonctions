def is_float(val):
    if val in ("", ".", "-", "-."):
        return True  # états intermédiaires acceptables
    try:
        float(val)
        return True
    except ValueError:
        return False

def to_float(val, default = 0) :
    if val in ("", ".", "-", "-.") :
        return default
    else :
        return float(val)