import json
from flask import Flask, render_template, redirect, Response, jsonify,request
from flask_cors import CORS
from Kerberos import Server
app = Flask(__name__, static_folder='./static', static_url_path='/')
cors = CORS(app)
server = Server.make_server_from_db('B')

# initial data
book_data = ['General Theory of Relativity','Quantum Electrodynamics']

@app.route('/',methods=['POST'])
def get_data():
    data = request.form.to_dict()
    req = data['req']
    ticket = data['ticket']
    req = server.decrypt_req('u1',request.remote_addr,ticket,req)

    res = {'success':True}
    if req['req'] == 'data':
        res['res'] = book_data
    if req['req'] == 'add':
        book_data.append(req['book'])

    enc_res = server.encrypt_res('u1',request.remote_addr,ticket,res)
    return Response(enc_res, status=200)

app.run(host='0.0.0.0', port='5002', debug=True)