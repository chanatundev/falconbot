from utils import jsondata

def get(key: str, **kwargs):
    localization_data = jsondata.read_json(path="localizations/en.json")
    keys = key.split(".")
    value = localization_data
    try:
        for k in keys:
            value = value[k]
        if kwargs:
            value = value.format(**kwargs)
        return value
    except KeyError:
        print(f"Localization key '{key}' not found.")
        return key
    except Exception as e:
        print(f"Error retrieving localization key '{key}': {e}")
        return key