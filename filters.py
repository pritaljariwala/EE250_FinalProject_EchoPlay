# filters.py

WINDOW_SIZE = 8
filter_buffer = []

def moving_average(new_value: float) -> float:
    """
    Moving average filter to smooth analog readings 
    """
    filter_buffer.append(new_value)
    if len(filter_buffer) > WINDOW_SIZE:
        filter_buffer.pop(0)
    return sum(filter_buffer) / len(filter_buffer)
