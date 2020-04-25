const express = require('express');
const crypto = require('crypto');
const bodyParser = require('body-parser');
const cors = require('cors');

const Kerberos = require('./Kerberos-JS');

const app = express();
const EXPRESS_PORT = process.env.PORT || 5002;
app.use(bodyParser.urlencoded({ extended: false }));
app.use(bodyParser.json());

app.use(cors());

//* Create the TGS class instance
const serverdb = new Kerberos.LocalDB();
const aescryptor = new Kerberos.AESCryptor();
const TGS = new Kerberos.KerberosTGS(aescryptor, serverdb, true);

//? This part would idaelly be exposed via an admin only route, that would allow additino of servers to the network
//? But here, We just add them with following code. Every time these are run a new ticket will be generated for Servers A and B
//? Which must be copied EXACTLY same on the respective server's DB
//? In case one wants to try that out, uncomment following two lines, run this script only,
//? copy those generated tickets in Tickets folder in data-server folder,
//? and them comment these line again and run the whole thing from start.

//TGS.addServer('Books');

app.post('/', (request, response) => {
  const { req, tgt, user } = request.body;

  //* Sanity Checks
  if (!req || !user) {
    return response
      .status(400)
      .send({ success: false, err: 'Incomplete Fields' });
  }
  if (!tgt) {
    return response.status(400).send({ success: false, err: 'tgt not found' });
  }

  try {
    //* decrypt the request (data not http) using the key of this server
    const decReq = TGS.decryptReq(req, user, request.ips[0] || request.ip, tgt);

    //? then we verify that the random number sent in the req is used for the first time by the user to
    //? prevent replay attacks. This is kept a distinct step from decoding the request,
    //? as it is not necessary that the request be an json as encoded string
    //? thus we can retrieve random number from it as it is stored and then verify it in this step.
    TGS.verifyRand(user, request.ips[0] || request.ip, decReq.rand);

    //? here we get response for the client and ticket that the client requested.
    //? NOTE that the response is not a http response, but an encrypted response which only the client can open with
    //? the key sent in the auth ticket originally, and contains key to encrypt the requests
    //? that are to be sent to the requested server.
    let { res, ticket } = TGS.getResponseAndTicket(
      user,
      request.ips[0] || request.ip,
      tgt,
      decReq.target,
      decReq.rand
    );

    //* Send the actual http response
    return response
      .status(200)
      .send({ success: true, res: res, ticket: ticket });
  } catch (e) {
    //* If error is of type ServerError, it means ther is some error in decoding the request(data not http)
    if (e instanceof Kerberos.ServerError) {
      //? send the error as reponse, can be encrypted, but not done here
      return response.status(400).send({ success: false, err: e.message });
    } else {
      //* Some other error occurred
      throw e;
    }
  }
});

app.listen(EXPRESS_PORT, () => {
  console.log(`Express TGS listening on Port ${EXPRESS_PORT}...`);
});
