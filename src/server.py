from flask import Flask, session, abort,request, send_from_directory, send_file, Response
import os, time
from werkzeug.exceptions import BadRequestKeyError
from server_lib.device import Device, DeviceStatus
import server_lib.device_exception
from args import get_args_dict, check_output_folder
from resource_manager import CONFIG
import logging
from uuid import UUID
import time, random
import hashlib
from rpi_lib.rpi_interaction import print_lcd

true_str = ['true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh']
false_str = ['false', '0', 'f', 'n', 'no', 'nope', 'nah', 'not really', 'no way']

# Create output folder if not created.
check_output_folder()

## INIT FLASK

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

app.logger.setLevel(logging.INFO)

digit_password = random.randint(1000,9999)
print_lcd(f"Password : {digit_password}")
## CLEANING

def truncate_file(filepath, bytes):
    '''
        Open the file, and rewrite the content from the end up to bytes size
    '''

    with open(filepath, 'r+') as file:
        file.seek(0, 2)
        size = file.tell()
        if size > bytes:
            file.seek(size - bytes)
            content = file.read()
            file.seek(0)
            file.write(content)
            file.truncate()



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
        print(f"Cleaning {error_logfile}")
        #remove the argument itself
        truncate_file(error_logfile, 1024 * 1024 * 10) # 10 MB

    except Exception:
        pass
    try:
        index = args.index('--access-logfile')
        access_logfile = args.pop(index+1)
        print(f"Cleaning {access_logfile}")
        truncate_file(access_logfile, 1024 * 1024 * 10) # 10 MB
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
CORS(app, origins="*", allow_headers="*",expose_headers=["Content-Disposition"])
if get_args_dict()["dev"]:


    @app.route("/trigger_error")
    def trigger_error():
        device.raise_error(server_lib.device_exception.DeviceException("A test error"))
        return "ok", 200

def get_uuid():
    return UUID(request.args.get("uuid")) if "uuid" in request.args else session.get("uuid")

@app.route('/verify_password', methods = ['GET'])
def verify_password():
    print("TOKEN",request.headers.get("Authorization"))
    password = request.headers.get("Authorization")
    if hashlib.sha256(password.encode()).hexdigest() == hashlib.sha256(str(digit_password).encode()).hexdigest():
        return "ok", 200
    else:
        return "Unauthorized", 401
    

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
    delay = request.args.get("delay", 2, type=int)
    duration = request.args.get("duration", 6, type=int)
    seed_id = request.args.get("seed_id")
    device.start_record(uuid, duration, delay = delay, seed_id = seed_id)
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
    path = device.get_records_csv(uuid)
    name = os.path.basename(path)
    print(name)
    return send_file(path, as_attachment=True, download_name=name,mimetype="text/csv")

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
        has_been_added = device.memory_manager.push_researcher(researcher_id)
        if has_been_added:
            return "ok", 200
        else:
            return "Researcher already added", 403
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

@app.route("/shutdown")
def turn_off():
    app.logger.info("Turning off by user")
    os.system(f"ssh ${CONFIG["worker_camera"]["camera_host"]}@${CONFIG['worker_camera']['camera_address']} 'sudo shutdown now'")
    os.system("sudo shutdown now")
    
app.logger.info("Server started")


