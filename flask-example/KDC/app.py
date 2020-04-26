import json
from Crypto.Hash import SHA256
from flask import Flask, render_template, redirect, Response, jsonify,request
from Kerberos import Kerberos_KDC,ServerError
app = Flask(__name__, static_folder='./static', static_url_path='/')

#* We create a KDC with ability to check and verify random
kdc = Kerberos_KDC(check_rand=True)

#? This part would idaelly be exposed via an admin only route, that would allow additino of servers to the network
#? But here, We just add them with following code. Every time these are run a new ticket will be generated for Servers A and B
#? Which must be copied EXACTLY same on the respective server's DB
#? In case one wants to try that out, uncomment following two lines, run this script only,
#? copy those generated tickets in Tickets folder in data-server folder,
#? and them comment these line again and run the whole thing from start.

#kdc.add_server('A')
#kdc.add_server('B')

#* This is our mock DB. In actual application this will be a connection to MongoDB or MySQLDb or some other DB
#* but for this we just usea dictionary mapping username to plain passwords
#! Note that the passwords should never be stored in plain text format in real application.
users = {'u1':'pass1','u2':'pass2'}

@app.route('/')
def homepage():
    return render_template('home.html')

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()

    #? Sanity checks
    if 'username' not in data or data['username'].strip() == '' or 'rand' not in data:
        return Response(json.dumps({'success': False, 'err': 'Incomplete Fields'}), mimetype="application/json", status=400)

    #* Here we retrive the password from our 'DB'
    #* in real application here one would contact a DB and query for username
    password = users.get(data['username'],None)


    if password == None: #* No user Found
        return Response(json.dumps({'success': False, 'err': 'No User Found'}), mimetype="application/json", status=400)

    #? Following is a possible way to convert a password to a secrete key.
    #? Note that this process must be exactly repeated on client side, so that an exact same secrete key is 
    #? generated on both sides, and response can be correctly decrypted. 
    #! Final generated hash key must be of length 512 bits, i.e. 32 bytes total
    #! NOTE Encoding or decoding from encodings like utf-8 or base 64 , 32 characters may not be total 256 bits 
    h = SHA256.new()
    h.update(password.encode('ascii'))
    hash_key = h.hexdigest()[0:32]

    try:
        #* We get authentication and Ticket Granting Ticket from KDC
        #* the auth ticket is encrypted with user's unique pass hash,
        #* and it contains key to encrypt the request sent to TGS with
        #? Here username and ip address is used as two uids for the function
        auth,tgt = kdc.gen_auth_tickets(data['rand'],data['username'],request.remote_addr,hash_key)
        return Response(json.dumps({'success': True, 'auth':auth.decode('ascii'),'tgt':tgt.decode('ascii')}), mimetype="application/json", status=200)
    except ServerError as e:
        #! In case some error is occures which is Server error that is an error in generating the tickets, we send error response.
        #! In case some other type of error is thrown, it may be due to incorrect configuration
        #! Such as passing empty c_uid1 or c_uid2 fields or the hash_key is of incorrect type
       return Response(json.dumps({'success': False,'err':str(e)}), mimetype="application/json", status=400)

@app.route('/tickets',methods=['POST'])
def tickets():
    data = request.get_json()

    #? Sanity checks
    if 'req' not in data:
        return Response(json.dumps({'success': False,'err':'No req found'}), mimetype="application/json", status=400)
    if 'tgt' not in data:
        return Response(json.dumps({'success': False,'err':'No tgt found'}), mimetype="application/json", status=400)
    try:
        #? We first decode the req field that is sent inside the http request
        dec_req = kdc.decrypt_req(data['req'],data['tgt'])
        try:
            req = json.loads(dec_req)
        except Exception as e:
            return Response(json.dumps({'success': False,'err':'Invalid request'}), mimetype="application/json", status=400)

        #? then we verify that the random number sent in the req is used for the first time by the user to
        #? prevent replay attacks. This is kept a distinct step from decoding the request,
        #? as it is not necessary that the request be an json as encoded string
        #? thus we can retrieve random number from it as it is stored and then verify it in this step.
        kdc.verify_rand(req['user'],request.remote_addr,req['rand'])

        #? here we get response for the client and ticket that the client requested.
        #? NOTE that the response is not a http response, but an encrypted response which only the client can open with 
        #? the key sent in the auth ticket originally, and contains key to encrypt the requests
        #? that are to be sent to the requested server.
        res,ticket = kdc.get_res_and_ticket(req['user'],request.remote_addr,data['tgt'],req['target'],req['rand'])
        return Response(json.dumps({'success': True,'res':res.decode('ascii'),'ticket':ticket.decode('ascii')}), mimetype="application/json", status=200)
    except ServerError as e:
        return Response(json.dumps({'success': False,'err':str(e)}), mimetype="application/json", status=400)
    

app.run(host='0.0.0.0', port='5000', debug=True)
