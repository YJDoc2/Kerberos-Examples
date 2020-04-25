const express = require('express');
const crypto = require('crypto');
const bodyParser = require('body-parser');
const cors = require('cors');

const Kerberos = require('./Kerberos-JS');

const app = express();
const EXPRESS_PORT = process.env.PORT || 5001;
app.use(bodyParser.urlencoded({ extended: false }));
app.use(bodyParser.json());

app.use(cors());

//* This is our mock DB. In actual application this will be a connection to MongoDB or MySQLDb or some other DB
//* but for this we just usea dictionary mapping username to plain passwords
//! Note that the passwords should never be stored in plain text format in real application.
const users = new Map();
users.set('u1', 'pass1');
users.set('u2', 'pass2');

//* Make a new LocalDB instance and AESEncrypter instance for TGS, which is required for AS, then make AS
const serverdb = new Kerberos.LocalDB();
const aescryptor = new Kerberos.AESCryptor();
const TGS = new Kerberos.KerberosTGS(aescryptor, serverdb, true);
const AS = new Kerberos.KerberosAS(aescryptor, TGS, true);

app.post('/', (req, res) => {
  const { username, rand } = req.body;

  //* Sanity check
  if (!username || !rand) {
    return res.status(400).send({ success: false, err: 'Incomplete Fields' });
  }

  //* Here we retrive the password from our 'DB'
  //* in real application here one would contact a DB and query for username
  const password = users.get(username);
  //* User does not exists
  if (!password) {
    return res.status(400).send({ success: false, err: 'No user Found' });
  }

  //? Following is a possible way to convert a password to a secrete key.
  //? Note that this process must be exactly repeated on client side, so that an exact same secrete key is
  //? generated on both sides, and response can be correctly decrypted.
  //! Final generated hash key must be of length 512 bits, i.e. 32 bytes total
  //! NOTE Encoding or decoding from encodings like utf-8 or base 64 , 32 characters may not be total 256 bits
  let hash = crypto.createHash('SHA256');
  hash.update(password);
  hashKey = hash.digest('hex').substr(0, 32);

  try {
    //* Get auth ticket and Ticket Granting Ticket
    let { auth, tgt } = AS.makeAuthTickets(
      rand,
      username,
      req.ips[0] || req.ip,
      hashKey
    );
    //* Send the response
    return res.status(200).send({ success: true, auth: auth, tgt: tgt });
  } catch (e) {
    //* If error is of type ServerError, it means ther is some error in creating the tickets
    if (e instanceof Kerberos.ServerError) {
      //? send the error as reponse, can be encrypted, but not done here
      return res.status(400).send({ success: false, err: e.message });
    } else {
      //* Some other error occurred
      throw e;
    }
  }
});

app.listen(EXPRESS_PORT, () => {
  console.log(`Express AS listening on Port ${EXPRESS_PORT}...`);
});
