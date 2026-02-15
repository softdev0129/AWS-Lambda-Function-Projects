// Save SMTP Credentials
document.getElementById('smtpForm').addEventListener('submit', function (e) {
    e.preventDefault();

    const smtpCredentials = {
        host: document.getElementById('smtpHost').value,
        port: parseInt(document.getElementById('smtpPort').value),
        secure: document.getElementById('smtpSecure').checked,
        auth: {
            user: document.getElementById('smtpUser').value,
            pass: document.getElementById('smtpPass').value,
        },
    };

    // Store the SMTP credentials in local storage
    localStorage.setItem('smtpCredentials', JSON.stringify(smtpCredentials));
    document.getElementById('message').textContent = 'SMTP Configuration Saved!';
});

// Send Email
document.getElementById('emailForm').addEventListener('submit', async function (e) {
    e.preventDefault();

    let smtpCredentials = JSON.parse(localStorage.getItem('smtpCredentials'));

    const mailOptions = {
        from: document.getElementById('from').value,
        to: document.getElementById('to').value,
        subject: document.getElementById('subject').value,
        text: document.getElementById('text').value,
        html: document.getElementById('html').value,
    };
    const res = await fetch('/v1/secretkey', {
        method: 'GET'
    });
    let data = await res.json();
    const secretKey = data.key;
    smtpCredentials.auth.pass = CryptoJS.AES.encrypt(smtpCredentials.auth.pass, secretKey).toString();
    // Send email via the Lambda endpoint
    const response = await fetch('/v1/send-email', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({smtpCredentials, mailOptions}),
    });

    data = await response.json();
    document.getElementById('message').textContent = data.message || data.error;
});

async function saveToDraft() {
    console.log('saveToDraft');
    let smtpCredentials = JSON.parse(localStorage.getItem('smtpCredentials'));

    const mailOptions = {
        from: document.getElementById('from').value,
        to: [document.getElementById('to').value],
        subject: document.getElementById('subject').value,
        text: document.getElementById('text').value,
        html: document.getElementById('html').value,
    };
    const res = await fetch('/v1/secretkey', {
        method: 'GET'
    });
    let data = await res.json();
    const secretKey = data.key;
    smtpCredentials.auth.pass = CryptoJS.AES.encrypt(smtpCredentials.auth.pass, secretKey).toString();
    // Send email via the Lambda endpoint
    const response = await fetch('/v1/save-to-draft', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({smtpCredentials, mailOptions}),
    });

    data = await response.json();
    document.getElementById('message').textContent = data.message || data.error;
}

// Retrieve Emails
document.getElementById('retrieveForm').addEventListener('submit', async function (e) {
    e.preventDefault();
    const smtpCredentials = JSON.parse(localStorage.getItem('smtpCredentials'));

    const res = await fetch('/v1/secretkey', {
        method: 'GET'
    });

    let data = await res.json();
    const secretKey = data.key;
    smtpCredentials.auth.pass = CryptoJS.AES.encrypt(smtpCredentials.auth.pass, secretKey).toString();
    const uri = document.getElementById('uri').value;
    const path = document.getElementById('mail_path').value;
    // Retrieve emails via the Lambda endpoint
    const response = await fetch("/v1/" + uri, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({smtpCredentials, path, page: 1, pageSize: 10}),
    });

    data = await response.json();
    document.getElementById('emailList').innerHTML = ''; // Clear the list

    if (data.emails) {
        data.emails.forEach(email => {
            const li = document.createElement('li');
            li.innerHTML = `<strong>From:</strong> ${email?.from[0]?.name} (${email?.from[0]?.address}) <br />
                            <strong>Subject:</strong> ${email.subject} <br />
                            <strong>Date:</strong> ${new Date(email.date).toLocaleString()} <br />
                            <strong>UID:</strong> ${email.uid} <br />
                            `;
            document.getElementById('emailList').appendChild(li);
        });
        document.getElementById('message').textContent = data.message;
    } else {
        document.getElementById('message').textContent = data.error;
    }
});

document.getElementById('moveForm').addEventListener('submit', async function (e) {
    e.preventDefault();
    const smtpCredentials = JSON.parse(localStorage.getItem('smtpCredentials'));

    const res = await fetch('/v1/secretkey', {
        method: 'GET'
    });

    let data = await res.json();
    const secretKey = data.key;
    smtpCredentials.auth.pass = CryptoJS.AES.encrypt(smtpCredentials.auth.pass, secretKey).toString();
    const uid = document.getElementById('uid').value;
    const path = document.getElementById('path').value;
    const response = await fetch('/v1/move-to-trash', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({smtpCredentials, uid, path}),
    });

    data = await response.json();
    document.getElementById('message').textContent = data.message;
});

document.getElementById('deleteForm').addEventListener('submit', async function (e) {
    e.preventDefault();
    const smtpCredentials = JSON.parse(localStorage.getItem('smtpCredentials'));

    const res = await fetch('/v1/secretkey', {
        method: 'GET'
    });

    let data = await res.json();
    const secretKey = data.key;
    smtpCredentials.auth.pass = CryptoJS.AES.encrypt(smtpCredentials.auth.pass, secretKey).toString();
    const uid = document.getElementById('t_uid').value;
    const response = await fetch('/v1/empty-trash', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({smtpCredentials, uid}),
    });

    data = await response.json();
    document.getElementById('message').textContent = data.message;
});

let access_token = '';
let refresh_token = '';
let AUTH_CODE = '';

const OUTLOOK_CLIENT_ID = '9a4e608e-c43f-4995-ae41-571d93250cde';
const OUTLOOK_REDIRECTION_URI = 'https://services-dev.vehya.com/auth.html';
const OUTLOOK_CLIENT_SECRET = 'tpl8Q~SqVS2eIqZZ.0Qj5CYP9wxlc453Xnndmc0a';
const OUTLOOK_SCOPES = 'IMAP.AccessAsUser.All offline_access openid Mail.ReadWrite Mail.Send'; // Corrected scope format
const OUTLOOK_RESPONSE_TYPE = 'code';
const OUTLOOK_TENANT_ID = 'bf39561d-6f27-467a-b0ad-8aab96ca16ba';

document.getElementById("outlookLoginBtn").onclick = async () => {
    const authUrl = `https://login.microsoftonline.com/common/oauth2/v2.0/authorize?client_id=${OUTLOOK_CLIENT_ID}&response_type=${OUTLOOK_RESPONSE_TYPE}&redirect_uri=${encodeURIComponent(OUTLOOK_REDIRECTION_URI)}&scope=${encodeURIComponent(OUTLOOK_SCOPES)}`;
    window.location.href = authUrl;
};


const GOOGLE_CLIENT_ID = '867856588138-a8vp40qobd5ovdcrhp97v8fnmuidjgqs.apps.googleusercontent.com';
const GOOGLE_REDIRECT_URI = 'https://d6aljed0n5.execute-api.eu-west-1.amazonaws.com/v1'; // The URI where you will receive the response
const GOOGLE_CLIENT_SECRET = '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';
const GOOGLE_SCOPES = 'https://mail.google.com/'; // Scope for Gmail access

document.getElementById('googleLoginBtn').onclick = function () {
    window.location.href = `https://accounts.google.com/o/oauth2/v2/auth?` +
        `client_id=${GOOGLE_CLIENT_ID}` +
        `&redirect_uri=${encodeURIComponent(GOOGLE_REDIRECT_URI)}` +
        `&response_type=code` +
        `&scope=${encodeURIComponent(GOOGLE_SCOPES)}` +
        `&access_type=offline` +  // Request refresh token
        `&prompt=consent`; // Redirect to Google's OAuth 2.0 server
};

function getQueryParam(param) {
    const currentUrl = window.location.href;
    const url = new URL(currentUrl);
    const params = new URLSearchParams(url.search);
    return params.get(param);
}

async function sendEmailOAuth(service) {
    const code = getQueryParam('code');
    if (code === '' || code === undefined)
        return;

    const mailOptions = {
        from: document.getElementById('from').value,
        to: document.getElementById('to').value,
        subject: document.getElementById('subject').value,
        text: document.getElementById('text').value,
        html: document.getElementById('html').value,
    };

    // Send email via the Lambda endpoint
    const response = await fetch('/v1/send-email-oauth', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({code: AUTH_CODE, mailOptions, service}),
    });

    let data = await response.json();
    document.getElementById('message').textContent = data.message || data.error;
}

document.addEventListener('DOMContentLoaded', async () => {
    // Get the parameter value
    const code = getQueryParam('code');
    const scope = getQueryParam('scope');
    console.log("code:", code);
    if (code !== '' && code !== null) {
        AUTH_CODE = code;
    }
});
