from flask import Flask, jsonify, request
from flask_caching import Cache
from apothiki import save_todos_to_redis, get_todos_from_redis

app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'redis', 'CACHE_REDIS_URL': 'redis://redis:6379/0'})

# Routes


@app.route('/todos', methods=['GET'])
def get_todos():
    todos = get_todos_from_redis(cache)
    return jsonify({'todos': todos})


@app.route('/todos/<int:todo_id>', methods=['GET'])
def get_todo(todo_id):
    todos = get_todos_from_redis(cache)
    todo = next((item for item in todos if item['id'] == todo_id), None)
    if todo is None:
        return jsonify({'error': 'Todo not found'}), 404
    return jsonify({'todo': todo})


@app.route('/todos/', methods=['POST'])
def create_todo():
    if not request.json or 'title' not in request.json:
        return jsonify({'error': 'Title is required'}), 400  # Use 400 Bad Request

    todos = get_todos_from_redis(cache)
    todo = {
        'id': len(todos) + 1,
        'title': request.json['title'],
        'completed': False
    }
    todos.append(todo)

    # Save to Redis and check for errors
    save_result = save_todos_to_redis(cache, todos)
    if isinstance(save_result, str):
        return jsonify({'error': f'Failed to save to Redis: {save_result}'}), 500

    return jsonify({'todo': todo}), 200


@app.route('/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    todos = get_todos_from_redis(cache)
    print(todos)
    todo = next((item for item in todos if item['id'] == todo_id), None)
    if todo is None:
        return jsonify({'error': 'Todo not found'}), 404

    todo['title'] = request.json.get('title', todo['title'])
    todo['completed'] = request.json.get('completed', todo['completed'])

    # Save to Redis and check for errors
    save_result = save_todos_to_redis(cache, todos)
    if isinstance(save_result, str):
        return jsonify({'error': f'Failed to save to Redis: {save_result}'}), 500

    return jsonify({'todo': todo})


@app.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    todos = get_todos_from_redis(cache)
    todos = [item for item in todos if item['id'] != todo_id]

    # Save to Redis and check for errors
    save_result = save_todos_to_redis(cache, todos)
    if isinstance(save_result, str):
        return jsonify({'error': f'Failed to save to Redis: {save_result}'}), 500

    return jsonify({'result': 'Todo deleted'})


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
