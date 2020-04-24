const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');

const Kerberos = require('./Kerberos-JS');

let data = ['Gravitation', 'Spacetime And Geomatry'];

const app = express();
const EXPRESS_PORT = process.env.PORT || 5003;
app.use(bodyParser.urlencoded({ extended: false }));
app.use(bodyParser.json());

const server = Kerberos.Server.MakeServerFromDB('Books', null, null, true);

app.post('/data', (req, res) => {
  const inReq = req.body.req;
  const { ticket, user } = req.body;

  if (!inReq || !ticket || !user) {
    return res.status(400).send({ success: false, err: 'Incomplete Fields' });
  }

  try {
    let uid2 = req.ips[0] || req.ip;
    let decReq = server.decryptReq(user, uid2, ticket, inReq);
    server.verifyRand(user, uid2, decReq.rand);
    const encRes = server.encryptRes(user, uid2, ticket, data);
    return res.status(200).send({ success: true, res: encRes });
  } catch (e) {
    if (e instanceof Kerberos.ServerError) {
      return res.status(400).send({ success: false, err: e.message });
    }
  }
});

app.post('/add', (req, res) => {
  const inReq = req.body.req;
  const { ticket, user } = req.body;

  if (!inReq || !ticket || !user) {
    return res.status(400).send({ success: false, err: 'Incomplete Fields' });
  }
  try {
    let uid2 = req.ips[0] || req.ip;
    let decReq = server.decryptReq(user, uid2, ticket, inReq);
    server.verifyRand(user, uid2, decReq.rand);
    data.push(decReq.book);
    const encRes = server.encryptRes(user, uid2, ticket, {});
    return res.status(200).send({ success: true, res: encRes });
  } catch (e) {
    if (e instanceof Kerberos.ServerError) {
      return res.status(400).send({ success: false, err: e.message });
    }
  }
});

app.listen(EXPRESS_PORT, () => {
  console.log(`Express Book Server listening on Port ${EXPRESS_PORT}...`);
});
