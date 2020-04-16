import json
from flask import Flask, render_template, redirect, Response, jsonify,request
from flask_cors import CORS
from Kerberos import Server
app = Flask(__name__, static_folder='./static', static_url_path='/')
cors = CORS(app)

server = Server.make_server_from_db('A')

# initial data
book_data = ['Gravitation','Clean Code']

@app.route('/data',methods=['POST'])
def get_data():
    data = request.form.to_dict()
    req = data['req']
    ticket = data['ticket']
    req = server.decrypt_req('u1',request.remote_addr,ticket,req)
    enc_res = server.encrypt_res('u1',request.remote_addr,ticket,{'success': True,'res':book_data})
    return Response(enc_res, status=200)

@app.route('/add',methods=['POST'])
def add_data():
    data = request.form.to_dict()
    req = data['req']
    ticket = data['ticket']
    req = server.decrypt_req('u1',request.remote_addr,ticket,req)
    book_data.append(req['book'])
    enc_res = server.encrypt_res('u1',request.remote_addr,ticket,{'success':'true'})
    return Response(enc_res, status=200)

app.run(host='0.0.0.0', port='5001', debug=True)