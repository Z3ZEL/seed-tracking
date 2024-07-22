from flask import Flask, session, abort,request, send_from_directory, send_file
import os
from werkzeug.exceptions import BadRequestKeyError
from server_lib.device import Device, DeviceStatus
import server_lib.device_exception
from resource_manager import CONFIG

true_str = ['true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh']
false_str = ['false', '0', 'f', 'n', 'no', 'nope', 'nah', 'not really', 'no way']
## INIT DEVICE

device = Device()

## INIT FLASK

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


## Error handling
@app.errorhandler(server_lib.device_exception.DeviceNoSessionException)
def handle_no_session(error):
    return {"error": "No session found"}, 404

@app.errorhandler(server_lib.device_exception.DeviceBusyException)
def handle_device_busy(error):
    return {"error": "Device is busy, please try again later"}, 403

@app.errorhandler(server_lib.device_exception.DeviceStateNotAllowed)
def handle_device_state_not_allowed(error): 
    return {"error": "Device is not in right state"}, 405

@app.errorhandler(server_lib.device_exception.NoRecordFound)
def handle_no_record(error):
    return {"error": "No record found"}, 404



def get_uuid():
    return session.get('uuid')


@app.route('/status')
def status():
    uuid = get_uuid()
    print(uuid)
    return device.status(uuid).name


@app.route('/init')
def init():
    session_id = device.start_session(researcher_id=request.args.get("researcher_id"))
    session['uuid'] = session_id
    return {"uuid": session_id}

@app.route("/stop")
def stop():
    uuid = get_uuid()
    device.stop_session(uuid)
    return device.status(uuid).name
    
@app.route('/start')
def start():
    uuid = get_uuid()
    delay = request.args.get("delay")
    try:
        delay = int(delay) if delay != None else 2
    except ValueError:
        delay = 2
    seed_id = request.args.get("seed_id")
    device.start_record(uuid, 5, delay = delay, seed_id = seed_id)
    return device.status(uuid).name


@app.route('/last_record')
def last_record():
    uuid = get_uuid()
    return device.get_record(uuid)


@app.route('/validate')
def validate():
    uuid = get_uuid()
    try:
        valid : bool = request.args.get('valid').lower() in true_str
    except:
        abort(400)
    print(valid == False)
    device.validate_record(uuid, valid)

    return device.status(uuid).name


@app.route('/export')
def records():
    uuid = get_uuid()
    return send_file(device.get_records_csv(uuid))

@app.route("/error")
def error():
    return device.get_error_and_release(get_uuid())

@app.route("/researchers")
def researchers():
    return device.memory_manager.researchers

@app.route("/researcher", methods = ['GET', 'POST'])
def researcher():
    
    try:
        print(request.form)
        researcher_id = request.form.get('id')
        print(researcher_id)
    except BadRequestKeyError:
        abort(400)

    if request.method == 'POST':
        device.memory_manager.push_researcher(researcher_id)
        return researcher_id
    else:
        return researcher_id in device.memory_manager.researchers



@app.route('/res/<session_id>/<filename>')
def get_image(session_id, filename):
    print(f"Fetching {session_id}/{filename}")

    directory = os.path.join(CONFIG["server"]["temp_directory"],session_id)

    # Check if the file exists in the directory
    if os.path.exists(os.path.join(directory, filename)):
        return send_from_directory(directory, filename)
    else:
        # Return a 404 error if the file is not found
        abort(404)

    



    


