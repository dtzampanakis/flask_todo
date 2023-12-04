import json


def get_todos_from_redis(cache):
    todos_json = cache.get('todos')
    print(f"DEBUG: Retrieved JSON from cache: {todos_json}")
    if todos_json:
        try:
            return json.loads(todos_json)
        except json.JSONDecodeError as e:
            print(f"ERROR: JSON decoding error: {e}")
    return []


def save_todos_to_redis(cache, todos):
    try:
        cache.set('todos', json.dumps(todos))
        print(f"DEBUG: Saved JSON to cache: {json.dumps(todos)}")
    except Exception as e:
        print(f"ERROR: Failed to save to Redis: {e}")
        return str(e)
