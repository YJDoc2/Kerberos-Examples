import json
from flask import Flask, render_template, redirect, Response, jsonify,request
from flask_cors import CORS
from Kerberos import Server,Server_Error
app = Flask(__name__, static_folder='./static', static_url_path='/')
cors = CORS(app)

#! This server uses distinct routes for different type of requests

#? We make our Kerberos server (not HTTP Server) from the ticket generated by TGS ,
#? copied from there and saved in Tickets folder here.
server = Server.make_server_from_db('A',check_rand=True)


#* The mock databse
book_data = ['Gravitation','Clean Code']

@app.route('/data',methods=['POST'])
def get_data():
    data = request.get_json()
    req = data['req']
    ticket = data['ticket']
    try:
        #? we first try to decode req param in HTTP request recieved
        dec_req = server.decrypt_req(req,ticket)
        req = json.loads(dec_req)

        #? Then we verify that the random number used by user is used for the first time
        server.verify_rand(req.get('rand',None),req['user'],request.remote_addr)

        #? we encrypt the respnse(data, not HTTP) that is to be sent
        enc_res = server.encrypt_res(req['user'],request.remote_addr,{'success': True,'res':book_data},ticket)

        #? we return HTTP response
        return Response(enc_res, status=200)
    except Server_Error as e:
        #? If some error occured send the error as reponse, can be encrypted, but not done here
        return Response(str(e),400)

@app.route('/add',methods=['POST'])
def add_data():
    data = request.get_json()
    req = data['req']
    ticket = data['ticket']
    try:
        #? we first try to decode req param in HTTP request recieved
        dec_req = server.decrypt_req(req,ticket)
        req = json.loads(dec_req)

        #? Then we verify that the random number used by user is used for the first time
        server.verify_rand(req.get('rand',None),req['user'],request.remote_addr)

        #* we add the data that is send, in real application we would operate with actual database here
        book_data.append(req['book'])

        #? we encrypt the respnse(data, not HTTP) that is to be sent
        enc_res = server.encrypt_res(req['user'],request.remote_addr,{'success':'true'},ticket)

         #? we return HTTP response
        return Response(enc_res, status=200)
    except Server_Error as e:
        #? If some error occured send the error as reponse, can be encrypted, but not done here
        return Response(str(e),400)

app.run(host='0.0.0.0', port='5001', debug=True)