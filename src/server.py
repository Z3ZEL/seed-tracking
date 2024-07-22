from flask import Flask, session, abort,request

from server_lib.device import Device, DeviceStatus
import server_lib.device_exception

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
    return {"status": device.status(uuid).name}


@app.route('/init')
def init():
    session_id = device.start_session()
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
    device.start_record(uuid, 5)
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
    return device.get_records_csv(uuid)



    



    


