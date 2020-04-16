let client = null;
function login() {
  let username = document.querySelector('#username');
  let pass = document.querySelector('#password');
  $.ajax({
    type: 'POST',
    url: '/api/login',
    data: { username: username.value, password: pass.value },
    success: async function (response) {
      const enc = new TextEncoder();
      const passEnc = enc.encode(pass.value);
      const hashBuffer = await crypto.subtle.digest('SHA-256', passEnc); // hash the message
      const hashArray = Array.from(new Uint8Array(hashBuffer)); // convert buffer to byte array
      const hashHex = hashArray
        .map((b) => b.toString(16).padStart(2, '0'))
        .join(''); // convert bytes to hex string
      const key = hashHex.substr(0, 32);
      client = new Kerberos.Client(key);
      const auth = client.decryptRes(response.auth, key);
      client.saveTicket('decAuth', auth);
      client.saveTicket('Auth', response.auth);
      client.saveTicket('tgt', response.tgt);
    },
    error: function (err) {
      console.log(err.responseJSON);
    },
  });
}

function serverAGet() {
  if (!client) {
    console.log('Please Log in with valid credentials');
    return;
  }
  if (!client.getTicket('A')) {
    const auth = client.getTicket('decAuth');
    const key = auth.key;
    let req = {};
    req.uid1 = auth.uid1;
    req.uid2 = auth.uid2;
    req.rand = Math.floor(Math.random() * 1000);
    req.target = 'A';
    const encReq = client.encryptReq(req, auth.key);
    $.ajax({
      type: 'POST',
      url: '/tickets',
      data: { req: encReq, tgt: client.getTicket('tgt') },
      success: function (response) {
        const res = client.decryptRes(response.res, auth.key);
        client.saveTicket('A', response.ticket);
        client.saveTicket('decA', res);
        let req = {};
        const serEncReq = client.encryptReq(req, res.key, res.init_val);
        $.ajax({
          type: 'POST',
          url: 'http://localhost:5001/data',
          data: { req: serEncReq, ticket: response.ticket },
          success: function (response) {
            const res1 = client.decryptRes(response, res.key, res.init_val);

            let template = '';
            res1.res.forEach((entry, i) => {
              template += `<h6>Book ${i + 1} : ${entry}</h6>`;
            });
            document.querySelector('#ServerAData').innerHTML = template;
          },
          error: function (e) {
            console.log(e);
          },
        });
      },
      error: function (e) {
        console.log(e);
      },
    });
  } else {
    let req = {};
    const ticket = client.getTicket('A');
    const decA = client.getTicket('decA');
    const serEncReq = client.encryptReq(req, decA.key, decA.init_val);
    $.ajax({
      type: 'POST',
      url: 'http://localhost:5001/data',
      data: { req: serEncReq, ticket: ticket },
      success: function (response) {
        const res = client.decryptRes(response, decA.key, decA.init_val);
        let template = '';
        res.res.forEach((entry, i) => {
          template += `<h6>Book ${i + 1} : ${entry}</h6>`;
        });
        document.querySelector('#ServerAData').innerHTML = template;
      },
      error: function (e) {
        console.log(e);
      },
    });
  }
}

function serverASave() {
  if (!client) {
    console.log('Please Log in with valid credentials');
    return;
  }
  const input = document.querySelector('#dataA').value.trim();
  if (input === '') {
    return;
  }
  if (!client.getTicket('A')) {
    const auth = client.getTicket('decAuth');
    const key = auth.key;
    let req = {};
    req.uid1 = auth.uid1;
    req.uid2 = auth.uid2;
    req.rand = Math.floor(Math.random() * 1000);
    req.target = 'A';
    const encReq = client.encryptReq(req, auth.key);
    $.ajax({
      type: 'POST',
      url: '/tickets',
      data: { req: encReq, tgt: client.getTicket('tgt') },
      success: function (response) {
        const res = client.decryptRes(response.res, auth.key);
        client.saveTicket('A', response.ticket);
        client.saveTicket('decA', res);
        let req = { book: input };
        const serEncReq = client.encryptReq(req, res.key, res.init_val);
        $.ajax({
          type: 'POST',
          url: 'http://localhost:5001/add',
          data: { req: serEncReq, ticket: response.ticket },
          success: function (response) {},
          error: function (e) {
            console.log(e);
          },
        });
      },
      error: function (e) {
        console.log(e);
      },
    });
  } else {
    let req = { book: input };
    const ticket = client.getTicket('A');
    const decA = client.getTicket('decA');
    const serEncReq = client.encryptReq(req, decA.key, decA.init_val);
    $.ajax({
      type: 'POST',
      url: 'http://localhost:5001/add',
      data: { req: serEncReq, ticket: ticket },
      success: function (response) {},
      error: function (e) {
        console.log(e);
      },
    });
  }
}

function serverBGet() {
  if (!client) {
    console.log('Please Log in with valid credentials');
    return;
  }
  if (!client.getTicket('B')) {
    const auth = client.getTicket('decAuth');
    const key = auth.key;
    let req = {};
    req.uid1 = auth.uid1;
    req.uid2 = auth.uid2;
    req.rand = Math.floor(Math.random() * 1000);
    req.target = 'B';
    const encReq = client.encryptReq(req, auth.key);
    $.ajax({
      type: 'POST',
      url: '/tickets',
      data: { req: encReq, tgt: client.getTicket('tgt') },
      success: function (response) {
        const res = client.decryptRes(response.res, auth.key);
        client.saveTicket('B', response.ticket);
        client.saveTicket('decB', res);
        let req = { req: 'data' };
        const serEncReq = client.encryptReq(req, res.key, res.init_val);
        $.ajax({
          type: 'POST',
          url: 'http://localhost:5002/',
          data: { req: serEncReq, ticket: response.ticket },
          success: function (response) {
            const res1 = client.decryptRes(response, res.key, res.init_val);

            let template = '';
            res1.res.forEach((entry) => {
              template += `<h6>${entry}</h6>`;
            });
            document.querySelector('#ServerBData').innerHTML = template;
          },
          error: function (e) {
            console.log(e);
          },
        });
      },
      error: function (e) {
        console.log(e);
      },
    });
  } else {
    let req = { req: 'data' };
    const ticket = client.getTicket('B');
    const decB = client.getTicket('decB');
    const serEncReq = client.encryptReq(req, decB.key, decB.init_val);
    $.ajax({
      type: 'POST',
      url: 'http://localhost:5002/',
      data: { req: serEncReq, ticket: ticket },
      success: function (response) {
        const res = client.decryptRes(response, decB.key, decB.init_val);
        let template = '';
        res.res.forEach((entry, i) => {
          template += `<h6>${entry}</h6>`;
        });
        document.querySelector('#ServerBData').innerHTML = template;
      },
      error: function (e) {
        console.log(e);
      },
    });
  }
}

function serverBSave() {
  if (!client) {
    console.log('Please Log in with valid credentials');
    return;
  }
  const input = document.querySelector('#dataB').value.trim();
  if (input === '') {
    return;
  }
  if (!client.getTicket('B')) {
    const auth = client.getTicket('decAuth');
    const key = auth.key;
    let req = {};
    req.uid1 = auth.uid1;
    req.uid2 = auth.uid2;
    req.rand = Math.floor(Math.random() * 1000);
    req.target = 'B';
    const encReq = client.encryptReq(req, auth.key);
    $.ajax({
      type: 'POST',
      url: '/tickets',
      data: { req: encReq, tgt: client.getTicket('tgt') },
      success: function (response) {
        const res = client.decryptRes(response.res, auth.key);
        client.saveTicket('B', response.ticket);
        client.saveTicket('decB', res);
        let req = { req: 'add', book: input };
        const serEncReq = client.encryptReq(req, res.key, res.init_val);
        $.ajax({
          type: 'POST',
          url: 'http://localhost:5002/',
          data: { req: serEncReq, ticket: response.ticket },
          success: function (response) {},
          error: function (e) {
            console.log(e);
          },
        });
      },
      error: function (e) {
        console.log(e);
      },
    });
  } else {
    let req = { req: 'add', book: input };
    const ticket = client.getTicket('B');
    const decA = client.getTicket('decB');
    const serEncReq = client.encryptReq(req, decA.key, decA.init_val);
    $.ajax({
      type: 'POST',
      url: 'http://localhost:5002/',
      data: { req: serEncReq, ticket: ticket },
      success: function (response) {},
      error: function (e) {
        console.log(e);
      },
    });
  }
}
