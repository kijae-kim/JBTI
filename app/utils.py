from datetime import datetime


def json_serial(obj):    
    if isinstance(obj, (datetime)):
        if obj != obj or obj == float('inf') or obj == -float('inf'):
            return str(obj)
    raise TypeError("Type not serializable")

def clean_data(data):    
    if isinstance(data, dict):
        return {k: clean_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [clean_data(i) for i in data]
    elif isinstance(data, float):
        if data != data or data == float('inf') or data == -float('inf'):
            return str(data)
        else:
            return data
    else:
        return data