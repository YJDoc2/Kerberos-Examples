//* We need client and user as global variable so we can access it from all functions
let client = null;
let user = '';
//? It may be possible that by the time our request sent to a server using Kerberos reches it,
//? the ticket that we sent is gets expired , in edge cases.
//? So we use a error delta here so than in refresh ticket function below if the remaining time for ticket's expiry is
//? less than this we first take a fresh ticket and then make the request.
const errDelta = 5000;

//* Helper function to show errors in  error div
function showError(e) {
  console.log(e);
  const err = document.querySelector('#error');
  const errStr = e.response ? e.response.data.err : e;
  err.innerHTML = errStr;
}

//* Helper function to clear the error div
function clearError() {
  document.querySelector('#error').innerHTML = '';
}

//* A helper function to check if we have the required ticket,
//* and if it is expired/close to expiry , take a new one
//? name is the name of server we want the ticket for
//? the ricket is saved in client by the 'name' and
//? the response that is sent along with the ticket is decrypted and seved by name 'dec{name}'
//? so for a server A, the ticket will be saved with name 'A' and decrypted response saved with name 'decA'
async function refreshTicket(name) {
  //* First check if ticket and decrypted response is present, returns undefined if it is not present
  const ticket = client.getTicket(name);
  const decTicket = client.getTicket(`dec${name}`);
  //? Either is the ticket is not present or it is close to expiry, get a new ticket
  if (
    !ticket ||
    decTicket.timestamp + decTicket.lifetime < Date.now() + errDelta
  ) {
    const auth = client.getTicket('decAuth');
    let req = {};
    req.user = user;
    req.uid1 = auth.uid1;
    req.uid2 = auth.uid2;
    req.rand = Math.floor(Math.random() * 1000);
    req.target = name;

    //* Encrypt the request(data, not http) to be sent
    const encReq = client.encryptReq(auth.key, req);

    const response = (
      await axios.post('/tickets', {
        req: encReq,
        tgt: client.getTicket('tgt'),
      })
    ).data;
    //* Decrypt the response(data not http) sent with ticket
    const res = client.decryptRes(auth.key, response.res);
    //* save decrypted response and ticket
    client.saveTicket(name, response.ticket);
    client.saveTicket(`dec${name}`, res);
  }
  //* Either the ticket was already present or it is now brought from TGS
  return;
}

//* Initial Login Function
async function login() {
  //* Get data from the html elements
  let username = document.querySelector('#username').value;
  user = username;
  let pass = document.querySelector('#password').value;
  //* clear the error div
  clearError();

  try {
    //? Make a new random number to send along with request.
    const rand = Math.floor(Math.random() * 1000);
    const res = (
      await axios.post('/api/login', { username: username, rand: rand })
    ).data;
    //* Here we make SHA 256 digest of password, exactly as it is done on server , and is used to encrypt the response
    const enc = new TextEncoder();
    const passEnc = enc.encode(pass);
    const hashBuffer = await crypto.subtle.digest('SHA-256', passEnc); // hash the message
    const hashArray = Array.from(new Uint8Array(hashBuffer)); // convert buffer to byte array
    const hashHex = hashArray
      .map((b) => b.toString(16).padStart(2, '0'))
      .join(''); // convert bytes to hex string
    const key = hashHex.substr(0, 32);
    //* Create the Client instance with the key
    client = new Kerberos.Client();
    //* Try to decrypt response(data, not http) sent by server
    //* Throws a error if incorrecr key, that is incorrect password
    const auth = client.decryptRes(key, res.auth);
    //* If correct password save decrypted response as decAuth, encrypted response and Ticket Granting Ticket
    client.saveTicket('decAuth', auth);
    client.saveTicket('Auth', res.auth);
    client.saveTicket('tgt', res.tgt);
  } catch (e) {
    if (e instanceof ReferenceError) {
      showError('Incorrect Password');
    } else {
      throw e;
    }
  }
}

//* Function to get data from server A
async function serverAGet() {
  //* Clear ther error div
  clearError();
  //? Sanity check, dont try if user has not successfully logged in
  if (!client) {
    showError('Please Log in with valid credentials');
    return;
  }

  try {
    //* Make sure we have a working ticket for server A
    await refreshTicket('A');
    let req = {};
    //* Make new random for sending
    req.rand = Math.floor(Math.random() * 1000);
    req.user = user;

    const ticket = client.getTicket('A');
    const decA = client.getTicket('decA');
    //* Encrypt our request (data, not http) using the key given in response with ticket A
    const serEncReq = client.encryptReq(decA.key, req, decA.init_val);
    //* send actual(http) request
    const response = (
      await axios.post('http://localhost:5001/data', {
        req: serEncReq,
        ticket: ticket,
      })
    ).data;
    //* decrypt response by same key
    const res = client.decryptRes(decA.key, response, decA.init_val);
    //* Show data on page
    let template = '';
    res.res.forEach((entry, i) => {
      template += `<h6>Book ${i + 1} : ${entry}</h6>`;
    });
    document.querySelector('#ServerAData').innerHTML = template;
  } catch (e) {
    showError(e);
  }
}

//* Function to save data on server B
async function serverASave() {
  //* ckear the error div
  clearError();
  //? Sanity check, dont try if user has not successfully logged in
  if (!client) {
    showError('Please Log in with valid credentials');
    return;
  }
  //* Get the data that is to be sent to server from html element
  const input = document.querySelector('#dataA').value.trim();

  //? sanity check if input is empty dont do anything
  if (input === '') {
    return;
  }

  try {
    //* Make sure we have a working ticket for server A
    await refreshTicket('A');
    //* make our request object as required by our server (the structure is not part of kerberos)
    let req = { book: input };
    //* Make a random number to send along with request
    req.rand = Math.floor(Math.random() * 1000);
    req.user = user;
    //* get the tickets
    const ticket = client.getTicket('A');
    const decA = client.getTicket('decA');
    //* Encrypt the request with key sent in response along with the ticket
    const serEncReq = client.encryptReq(decA.key, req, decA.init_val);
    //* make actual request
    //? as our server does not send any data in response we don't try to decode it.
    const response = (
      await axios.post('http://localhost:5001/add', {
        req: serEncReq,
        ticket: ticket,
      })
    ).data;

    //* Clear the input
    document.querySelector('#dataA').value = '';
  } catch (e) {
    showError(e);
  }
}

//! Same Login as ServerAGet()
async function serverBGet() {
  clearError();
  if (!client) {
    showError('Please Log in with valid credentials');
    return;
  }

  try {
    await refreshTicket('B');
    let req = { req: 'data' };
    req.rand = Math.floor(Math.random() * 1000);
    req.user = user;
    const ticket = client.getTicket('B');
    const decB = client.getTicket('decB');
    const serEncReq = client.encryptReq(decB.key, req, decB.init_val);
    const response = (
      await axios.post('http://localhost:5002/', {
        req: serEncReq,
        ticket: ticket,
      })
    ).data;
    const res = client.decryptRes(decB.key, response, decB.init_val);
    let template = '';
    res.res.forEach((entry, i) => {
      template += `<h6>${entry}</h6>`;
    });
    document.querySelector('#ServerBData').innerHTML = template;
  } catch (e) {
    showError(e);
  }
}

//! Same Login as ServerASave()
async function serverBSave() {
  clearError();
  if (!client) {
    showError('Please Log in with valid credentials');
    return;
  }
  const input = document.querySelector('#dataB').value.trim();
  if (input === '') {
    return;
  }

  try {
    await refreshTicket('B');
    req = { req: 'add', book: input };
    req.rand = Math.floor(Math.random() * 1000);
    req.user = user;
    const ticket = client.getTicket('B');
    const decB = client.getTicket('decB');
    const serEncReq = client.encryptReq(decB.key, req, decB.init_val);
    const response = (
      await axios.post('http://localhost:5002/', {
        req: serEncReq,
        ticket: ticket,
      })
    ).data;
    //* Clear the input
    document.querySelector('#dataB').value = '';
  } catch (e) {
    showError(e);
  }
}
