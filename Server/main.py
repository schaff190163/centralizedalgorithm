from flask import Flask, request, jsonify
from celery import Celery
from coordinator import Coordinator

app = Flask(__name__)
coord = Coordinator()

# Konfiguration für Celery
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

# Beispiel für eine registrierte Aufgabe
@coord.register_task("my_hook")
def my_task(context):
    print(context["message"])
    return f"Received message: {context['message']}"

# Celery-Task für die Ausführung von Aufgaben
@celery.task
def execute_task(task_name, task_payload):
    return coord.fire_hook(task_name, task_payload)

# Endpoint für Clients zum Senden von Anfragen
@app.route('/send_request', methods=['POST'])
def send_request():
    data = request.get_json()
    task_name = data.get('task_name')
    task_payload = data.get('task_payload')

    if task_name and task_payload:
        # Hier wird der Celery-Task zur Verarbeitung der Anfrage gestartet
        result = execute_task.apply_async(args=[task_name, task_payload])
        return jsonify({'task_id': result.id}), 202
    else:
        return jsonify({'error': 'Invalid request'}), 400

if __name__ == '__main__':
    app.run(debug=True)
