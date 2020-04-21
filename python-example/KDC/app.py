import json
from Crypto.Hash import SHA256
from flask import Flask, render_template, redirect, Response, jsonify,request
from Kerberos import Kerberos_KDC,ServerError
app = Flask(__name__, static_folder='./static', static_url_path='/')

kdc = Kerberos_KDC(check_rand=True)
#kdc.add_server('A')
#kdc.add_server('B')

users = {'u1':'pass1','u2':'pass2'}

@app.route('/')
def homepage():
    return render_template('home.html')

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    if 'username' not in data or data['username'].strip() == '' or 'rand' not in data:
        return Response(json.dumps({'success': False, 'err': 'Incomplete Fields'}), mimetype="application/json", status=400)

    password = users.get(data['username'],None)

    if password == None:
        return Response(json.dumps({'success': False, 'err': 'No User Found'}), mimetype="application/json", status=400)
    h = SHA256.new()
    h.update(password.encode('ascii'))
    hash_key = h.hexdigest()[0:32]
    try:
        auth,tgt = kdc.gen_auth_tickets(data['rand'],data['username'],request.remote_addr,hash_key)
        return Response(json.dumps({'success': True, 'auth':auth.decode('ascii'),'tgt':tgt.decode('ascii')}), mimetype="application/json", status=200)
    except ServerError as e:
       return Response(json.dumps({'success': False,'err':str(e)}), mimetype="application/json", status=400)

@app.route('/tickets',methods=['POST'])
def tickets():
    data = request.get_json()
    if 'req' not in data:
        return Response(json.dumps({'success': False,'err':'No req found'}), mimetype="application/json", status=400)
    if 'tgt' not in data:
        return Response(json.dumps({'success': False,'err':'No tgt found'}), mimetype="application/json", status=400)
    try:
        res,ticket = kdc.get_res_and_ticket('u1',request.remote_addr,data['tgt'],data['req'])
        return Response(json.dumps({'success': True,'res':res.decode('ascii'),'ticket':ticket.decode('ascii')}), mimetype="application/json", status=200)
    except ServerError as e:
        return Response(json.dumps({'success': False,'err':str(e)}), mimetype="application/json", status=400)
    

app.run(host='0.0.0.0', port='5000', debug=True)
