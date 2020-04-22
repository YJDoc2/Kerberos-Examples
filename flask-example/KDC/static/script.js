let client = null;
const errDelta = 5000;

function showError(e) {
  console.log(e);
  const err = document.querySelector('#error');
  const errStr = e.response ? e.response.data.err : e;
  err.innerHTML = errStr;
}

function clearError() {
  document.querySelector('#error').innerHTML = '';
}

async function refreshTicket(name) {
  const ticket = client.getTicket(name);
  const decTicket = client.getTicket(`dec${name}`);
  if (
    !ticket ||
    decTicket.timestamp + decTicket.lifetime < Date.now() + errDelta
  ) {
    const auth = client.getTicket('decAuth');
    const key = auth.key;
    let req = {};
    req.uid1 = auth.uid1;
    req.uid2 = auth.uid2;
    req.rand = Math.floor(Math.random() * 1000);
    req.target = name;
    const encReq = client.encryptReq(req, auth.key);

    const response = (
      await axios.post('/tickets', {
        req: encReq,
        tgt: client.getTicket('tgt'),
      })
    ).data;
    const res = client.decryptRes(response.res, auth.key);
    client.saveTicket(name, response.ticket);
    client.saveTicket(`dec${name}`, res);
  }
  return;
}

async function login() {
  let username = document.querySelector('#username').value;
  let pass = document.querySelector('#password').value;
  clearError();

  try {
    const rand = Math.floor(Math.random() * 1000);
    const res = (
      await axios.post('/api/login', { username: username, rand: rand })
    ).data;
    const enc = new TextEncoder();
    const passEnc = enc.encode(pass);
    const hashBuffer = await crypto.subtle.digest('SHA-256', passEnc); // hash the message
    const hashArray = Array.from(new Uint8Array(hashBuffer)); // convert buffer to byte array
    const hashHex = hashArray
      .map((b) => b.toString(16).padStart(2, '0'))
      .join(''); // convert bytes to hex string
    const key = hashHex.substr(0, 32);
    client = new Kerberos.Client(key);
    const auth = client.decryptRes(res.auth, key);
    client.saveTicket('decAuth', auth);
    client.saveTicket('Auth', res.auth);
    client.saveTicket('tgt', res.tgt);
  } catch (e) {
    if (e instanceof ReferenceError) {
      showError('Incorrect Password');
    }
  }
}

async function serverAGet() {
  clearError();
  if (!client) {
    showError('Please Log in with valid credentials');
    return;
  }

  try {
    await refreshTicket('A');
    let req = {};
    req.rand = Math.floor(Math.random() * 1000);

    const ticket = client.getTicket('A');
    const decA = client.getTicket('decA');
    const serEncReq = client.encryptReq(req, decA.key, decA.init_val);
    const response = (
      await axios.post('http://localhost:5001/data', {
        req: serEncReq,
        ticket: ticket,
      })
    ).data;
    const res = client.decryptRes(response, decA.key, decA.init_val);
    let template = '';
    res.res.forEach((entry, i) => {
      template += `<h6>Book ${i + 1} : ${entry}</h6>`;
    });
    document.querySelector('#ServerAData').innerHTML = template;
  } catch (e) {
    showError(e);
  }
}

async function serverASave() {
  clearError();
  if (!client) {
    showError('Please Log in with valid credentials');
    return;
  }
  const input = document.querySelector('#dataA').value.trim();
  if (input === '') {
    return;
  }

  try {
    await refreshTicket('A');
    let req = { book: input };
    req.rand = Math.floor(Math.random() * 1000);
    const ticket = client.getTicket('A');
    const decA = client.getTicket('decA');
    const serEncReq = client.encryptReq(req, decA.key, decA.init_val);
    const response = (
      await axios.post('http://localhost:5001/add', {
        req: serEncReq,
        ticket: ticket,
      })
    ).data;
  } catch (e) {
    showError(e);
  }
}

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
    const ticket = client.getTicket('B');
    const decB = client.getTicket('decB');
    const serEncReq = client.encryptReq(req, decB.key, decB.init_val);
    const response = (
      await axios.post('http://localhost:5002/', {
        req: serEncReq,
        ticket: ticket,
      })
    ).data;
    const res = client.decryptRes(response, decB.key, decB.init_val);
    let template = '';
    res.res.forEach((entry, i) => {
      template += `<h6>${entry}</h6>`;
    });
    document.querySelector('#ServerBData').innerHTML = template;
  } catch (e) {
    showError(e);
  }
}

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
    const ticket = client.getTicket('B');
    const decB = client.getTicket('decB');
    const serEncReq = client.encryptReq(req, decB.key, decB.init_val);
    const response = (
      await axios.post('http://localhost:5002/', {
        req: serEncReq,
        ticket: ticket,
      })
    ).data;
  } catch (e) {
    showError(e);
  }
}
