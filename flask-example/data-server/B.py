import json
from flask import Flask, render_template, redirect, Response, jsonify,request
from flask_cors import CORS
from Kerberos import Server,ServerError
app = Flask(__name__, static_folder='./static', static_url_path='/')
cors = CORS(app)

#! This server uses single route for all requests,
#! and the actual action to be taken is decided by the data sent in req param in HTTP Post request

#? We make our Kerberos server (not HTTP Server) from the ticket generated by TGS ,
#? copied from there and saved in Tickets folder here.
server = Server.make_server_from_db('B',check_rand=True)

#* The mock databse
book_data = ['General Theory of Relativity','Quantum Electrodynamics']

@app.route('/',methods=['POST'])
def get_data():
    data = request.get_json()
    req = data['req']
    ticket = data['ticket']
    try:
         #? we first try to decode req param in HTTP request recieved
        dec_req = server.decrypt_req(req,ticket)
        req = json.loads(dec_req)

        #? Then we verify that the random number used by user is used for the first time
        server.verify_rand(req['user'],request.remote_addr,req.get('rand',None))

        #? As the req is successfully decrypted, the user is authenticated
        #? And as all possible operations will always succeed in this, we first set res (data, not HTTP) as success True
        res = {'success':True}
        
        #* If request (body param in HTTP POST request) contains 'req' param as data, we send the data
        if req['req'] == 'data':
            res['res'] = book_data
        #* If request (body param in HTTP POST request) contains 'req' param as add, we add the data in out mock db
        if req['req'] == 'add':
            book_data.append(req['book'])

        #? we encrypt the respnse(data, not HTTP) that is to be sent
        enc_res = server.encrypt_res(req['user'],request.remote_addr,ticket,res)
        
        #? we return HTTP response
        return Response(enc_res, status=200)
    except ServerError as e:
        #? If some error occured send the error as reponse, can be encrypted, but not done here
        return Response(str(e),400)
app.run(host='0.0.0.0', port='5002', debug=True)