import json
import os

def read_file(path: str, lines=False):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return f.read().splitlines() if lines else f.read()
    
def read_json(path: str):
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def write_json(path: str, data: dict):
    contents = read_json(path)
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(contents, f, indent=4)
        print(f"Error writing to {path}: {e}")

# merges default with existing json, useful for config files
def read_json_with_default(path: str, default: str = "templates/blank.json"):
    if not os.path.exists(path):
        return read_json(default)
    # 1 is the default, 2 is the new data to place onto the default
    def deep_merge(default: dict, data: dict) -> dict:
        result = default.copy()
        for key, value in data.items():
            if (key in result and isinstance(result[key], dict) and isinstance(value, dict)):
                result[key] = deep_merge(result[key], value)
            else:
                result[key] = value
        return result
    merged = deep_merge(read_json(default), read_json(path))
    write_json(path, merged)
    return merged

def text_to_json(text: str):
    if text.startswith("```json") and text.endswith("```"):
        text = "\n".join(text.split("\n")[1:-1])
    return json.loads(text)

def extension(filename: str, extension: str) -> str:
    if not filename.endswith(f".{extension}"):
        return filename + f".{extension}"
    return filename