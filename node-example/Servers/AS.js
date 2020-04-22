const express = require('express');
const crypto = require('crypto');
const bodyParser = require('body-parser');
const cors = require('cors');

const Kerberos = require('./Kerberos');

const app = express();
const EXPRESS_PORT = process.env.PORT || 5001;
app.use(bodyParser.urlencoded({ extended: false }));
app.use(bodyParser.json());

app.use(cors());

const users = new Map();
users.set('u1', 'pass1');
users.set('u2', 'pass2');

const serverdb = new Kerberos.LocalDB();
const aescryptor = new Kerberos.AESCryptor();
const TGS = new Kerberos.KerberosTGS(aescryptor, serverdb, true);
const AS = new Kerberos.KerberosAS(aescryptor, TGS, true);

app.post('/', (req, res) => {
  const { username, rand } = req.body;

  if (!username || !rand) {
    return res.status(400).send({ success: false, err: 'Incomplete Fields' });
  }

  const password = users.get(username);
  if (!password) {
    return res.status(400).send({ success: false, err: 'No user Found' });
  }

  let hash = crypto.createHash('SHA256');
  hash.update(password);
  hashKey = hash.digest('hex').substr(0, 32);

  try {
    let { auth, tgt } = AS.makeAuthTickets(
      rand,
      username,
      req.ips[0] || req.ip,
      hashKey
    );

    return res.status(200).send({ success: true, auth: auth, tgt: tgt });
  } catch (e) {
    if (e instanceof Kerberos.ServerError) {
      return res.status(400).send({ success: false, err: e.message });
    } else {
      console.log(e);
      return res.status(500).send({ success: false, err: 'ServerError' });
    }
  }
});

app.listen(EXPRESS_PORT, () => {
  console.log(`Express AS listening on Port ${EXPRESS_PORT}...`);
});
