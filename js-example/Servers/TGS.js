const express = require('express');
const crypto = require('crypto');
const bodyParser = require('body-parser');
const cors = require('cors');

const Kerberos = require('./Kerberos');

const app = express();
const EXPRESS_PORT = process.env.PORT || 5002;
app.use(bodyParser.urlencoded({ extended: false }));
app.use(bodyParser.json());

app.use(cors());

const serverdb = new Kerberos.LocalDB();
const aescryptor = new Kerberos.AESCryptor();
const TGS = new Kerberos.KerberosTGS(aescryptor, serverdb, true);

//TGS.addServer('Books');

app.post('/', (request, response) => {
  const { req, tgt, user } = request.body;

  if (!req || !user) {
    return response
      .status(400)
      .send({ success: false, err: 'Incomplete Fields' });
  }
  if (!tgt) {
    return response.status(400).send({ success: false, err: 'tgt not found' });
  }

  try {
    let { res, ticket } = TGS.getResponseAndTicket(
      user,
      request.ips[0] || request.ip,
      tgt,
      req
    );

    return response
      .status(200)
      .send({ success: true, res: res, ticket: ticket });
  } catch (e) {
    if (e instanceof Kerberos.ServerError) {
      return response.status(400).send({ success: false, err: e.message });
    }
  }
});

app.listen(EXPRESS_PORT, () => {
  console.log(`Express TGS listening on Port ${EXPRESS_PORT}...`);
});
