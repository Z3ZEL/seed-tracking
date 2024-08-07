from flask import Flask, session, abort,request, send_from_directory, send_file, Response
import os, time
from werkzeug.exceptions import BadRequestKeyError
from server_lib.device import Device, DeviceStatus
import server_lib.device_exception
from args import get_args_dict
from resource_manager import CONFIG
import logging
from uuid import UUID
import time

true_str = ['true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh']
false_str = ['false', '0', 'f', 'n', 'no', 'nope', 'nah', 'not really', 'no way']
## INIT DEVICE




## INIT FLASK

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

app.logger.setLevel(logging.INFO)

## CLEANING

def on_startup():
    ##Cleaning log file
    import sys
    args = sys.argv
    error_logfile = None
    access_logfile = None
    #get index of '--error-logfile' in args
    try:
        index = args.index('--error-logfile')
        #remove the next argument
        error_logfile = args.pop(index+1)
        print(f"Removing {error_logfile}")
        #remove the argument itself
        with open(error_logfile, 'w') as f:
            f.write("")
    except Exception:
        pass

    try:
        index = args.index('--access-logfile')
        access_logfile = args.pop(index+1)
        print(f"Removing {access_logfile}")
        args.pop(index)
        with open(access_logfile, 'w') as f:
            f.write("")
    except Exception:
        pass

if CONFIG["production"]:
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
    on_startup()


device = Device(app.logger)


## Error handling
def logError(error):
    app.logger.error(f"{time.strftime('%H:%M:%S')} - {str(error)}")

@app.errorhandler(server_lib.device_exception.DeviceNoSessionException)
def handle_no_session(error):
    logError(error)
    return {"error": "No session found"}, 404

@app.errorhandler(server_lib.device_exception.DeviceBusyException)
def handle_device_busy(error):
    logError(error)
    return {"error": "Device is busy, please try again later"}, 403

@app.errorhandler(server_lib.device_exception.DeviceStateNotAllowed)
def handle_device_state_not_allowed(error): 
    logError(error)
    return {"error": "Device is not in right state"}, 405

@app.errorhandler(server_lib.device_exception.NoRecordFound)
def handle_no_record(error):
    logError(error)
    return {"error": "No record found"}, 404

# Disabling cors if dev
from flask_cors import CORS
CORS(app, origins="*", allow_headers="*")
if get_args_dict()["dev"]:


    @app.route("/trigger_error")
    def trigger_error():
        device.raise_error(server_lib.device_exception.DeviceException("A test error"))
        return "ok", 200

def get_uuid():
    return UUID(request.args.get("uuid")) if "uuid" in request.args else session.get("uuid")


@app.route('/status')
def status():
    uuid = get_uuid()
    ## Keep the session alive and return the status whenever the status is changing
    def gen():
        while True:
            yield f"data: {device.status(uuid).name}\n\n"
            ## Sleep for 1 second
            time.sleep(1)
    return Response(gen(), mimetype='text/event-stream')



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
    print("Session ID " , uuid)
    delay = request.args.get("delay")
    try:
        delay = int(delay) if delay != None else 2
    except ValueError:
        delay = 2
    seed_id = request.args.get("seed_id")
    device.start_record(uuid, 6, delay = delay, seed_id = seed_id)
    return device.status(uuid).name

@app.route('/abort')
def abort():
    uuid = get_uuid()
    return device.stop_job(uuid)


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

    
app.logger.info("Server started")


