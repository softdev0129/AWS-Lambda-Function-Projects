import fs from 'fs';
import path from 'path';
import nodemailer from 'nodemailer';
import {ImapFlow} from 'imapflow';
import crypto from 'crypto'
import CryptoJS from 'crypto-js'
import dotenv from 'dotenv';
dotenv.config();

// Path to static files
const htmlFilePath = path.join(path.resolve(), 'form.html');
const jsFilePath = path.join(path.resolve(), 'script.js'); // Path to your JS file
const cssFilePath = path.join(path.resolve(), 'styles.css'); // Path to your CSS file
const jsonFilePath = path.join(path.resolve(), '/.well-known/microsoft-identity-association.json');

const generateSecretKey = (secret = process.env.SECRET_KEY) => {
    // Get the current time and round to the nearest minute (in milliseconds)
    const currentMinute = Math.floor(Date.now() / 360000);

    // Concatenate the secret and the current minute to generate a consistent key
    const data = secret + currentMinute;

    // Generate an HMAC (or hash) from the data
    return crypto.createHmac('sha256', secret).update(data).digest('hex');
}

const decryptPassword = (encryptedPassword) => {
    try {
        let secretKey = generateSecretKey();
        const decryptedBytes = CryptoJS.AES.decrypt(encryptedPassword, secretKey);
        return decryptedBytes.toString(CryptoJS.enc.Utf8);
    } catch (error) {
        return '';
    }
}

const saveEmail = async (smtpCredentials, mailOptions, path) => {
    const client = new ImapFlow(smtpCredentials);
    try {
        await client.connect();
        await client.mailboxOpen(path);
        let toAddressString = '';
        for (const toAddress of mailOptions.to) {
            toAddressString += `<${toAddress}>,`;
        }
        let emailContent = `From: <${mailOptions.from}>\nTo: ${toAddressString}`;
        if (mailOptions.cc) {
            let ccAddressString = '';
            for (const ccAddress of mailOptions.cc) {
                ccAddressString += `<${ccAddress}>,`;
            }
            emailContent += `\ncc: ${ccAddressString}`;
        }
        emailContent += `\nSubject: ${mailOptions.subject}\nDate: ${new Date().toUTCString()}`;
        if (mailOptions.attachments) {
            emailContent += `\nMIME-Version: 1.0\nContent-Type: multipart/mixed; boundary="boundary123"\n\n--boundary123\nContent-Type: text/plain; charset="utf-8"\nContent-Transfer-Encoding: 7bit\n\n${mailOptions.text}`
            for (const attachment of mailOptions.attachments) {
                emailContent += `\n\n--boundary123\nContent-Disposition: attachment; filename="${attachment.filename}"\nContent-Transfer-Encoding: base64\n\n${attachment.content}`;
            }
            emailContent += `\n\n--boundary123--`;
        } else {
            emailContent += `\n\n${mailOptions.text}`;
        }
        await client.append(path, emailContent, ['\\Seen']);
    } catch (error) {
        return {status: false, message: error};
    } finally {
        await client.logout();
    }

    return {status: true, message: "Success!"};
}


export const lambdaHandler = async (event) => {
    const httpMethod = event.httpMethod;
    const path = event.path;

    // Serve static files for .js and .css
    if (httpMethod === 'GET') {

        if (path === '/secretkey')
            return {
                statusCode: 200,
                body: JSON.stringify({
                    key: generateSecretKey(),
                }),
            };

        if (path.endsWith('.js')) {
            const jsContent = fs.readFileSync(jsFilePath, 'utf8');
            return {
                statusCode: 200,
                headers: {
                    'Content-Type': 'application/javascript',
                    'Access-Control-Allow-Origin': '*',
                },
                body: jsContent,
            };
        }

        if (path.endsWith('.json')) {
            const jsonContent = fs.readFileSync(jsonFilePath, 'utf8');
            return {
                statusCode: 200,
                headers: {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                },
                body: jsonContent,
            };
        }

        if (path.endsWith('.css')) {
            const cssContent = fs.readFileSync(cssFilePath, 'utf8');
            return {
                statusCode: 200,
                headers: {
                    'Content-Type': 'text/css',
                    'Access-Control-Allow-Origin': '*',
                },
                body: cssContent,
            };
        }

        if (path === '/' || path.endsWith('form.html')) {
            const htmlContent = fs.readFileSync(htmlFilePath, 'utf8');
            return {
                statusCode: 200,
                headers: {
                    'Content-Type': 'text/html',
                    'Access-Control-Allow-Origin': '*',
                },
                body: htmlContent,
            };
        }
    }

    if (httpMethod !== 'POST') {
        return {
            statusCode: 405,
            body: JSON.stringify({error: "Method Not Allowed"}),
        };
    }

    // Handle email sending
    if (path === '/send-email') {
        let {smtpCredentials, mailOptions} = JSON.parse(event.body);
        try {
            if ("pass" in smtpCredentials.auth) {
                const decryptedPassword = decryptPassword(smtpCredentials.auth.pass);
                if (decryptedPassword === '')
                    return {
                        statusCode: 500,
                        body: JSON.stringify({
                            message: 'The secret key is invalid.'
                        }),
                    };
                smtpCredentials.auth.pass = decryptedPassword;
            }

            const transporter = nodemailer.createTransport(smtpCredentials);
            const result = await transporter.sendMail(mailOptions);
            smtpCredentials.port = 993;
            smtpCredentials.secure = true;
            let sentBoxName = "Sent";
            if (smtpCredentials.host === "smtp.gmail.com") {
                sentBoxName = '[Gmail]/Sent Mail';
            }
            if (smtpCredentials.host === "smtp.office365.com") {
                sentBoxName = 'Sent Items';
            }
            await saveEmail(smtpCredentials, mailOptions, sentBoxName);
            return {
                statusCode: 200,
                body: JSON.stringify({
                    message: 'Email sent successfully!',
                    result: result
                }),
            };
        } catch (error) {
            return {
                statusCode: 500,
                body: JSON.stringify({
                    message: 'Failed to send email',
                    error
                }),
            };
        }
    }

    if (path === '/retrieve-emails') {
        let {smtpCredentials, path, page, pageSize} = JSON.parse(event.body);

        if ("pass" in smtpCredentials.auth) {
            const decryptedPassword = decryptPassword(smtpCredentials.auth.pass);
            if (decryptedPassword === '')
                return {
                    statusCode: 500,
                    body: JSON.stringify({
                        message: 'The secret key is invalid.'
                    }),
                };
            smtpCredentials.auth.pass = decryptedPassword;
        }

        const client = new ImapFlow(smtpCredentials);

        try {
            await client.connect();
            let mailbox;

            try {
                mailbox = await client.mailboxOpen(path);
            } catch (err) {
                if (err.responseStatus === "NO") {
                    mailbox = await client.mailboxCreate(path);
                } else {
                    throw err; // Rethrow unexpected errors
                }
            }

            const totalMessages = mailbox.exists;
            if (totalMessages === 0) {
                return {
                    statusCode: 200,
                    body: JSON.stringify({
                        message: `The emails in the ${path} have been successfully retrieved!`,
                        emails: [],
                        totalMessages
                    }),
                };
            }

            const start = totalMessages - ((page - 1) * pageSize);
            const end = Math.max(1, start - pageSize + 1);
            const messageRange = start > 0 ? `${start}:${end}` : `1:${Math.min(pageSize, totalMessages)}`;

            const messages = await client.fetch(messageRange, {envelope: true, uid: true, source: true, bodyStructure: true});
            const emails = [];

            for await (let message of messages) {
                const {envelope, bodyStructure} = message;
                envelope.uid = message.uid;

                // Extract attachments if they exist
                envelope.attachments = bodyStructure?.childNodes
                    ?.filter(part => part.disposition === 'attachment')
                    .map(part => part.dispositionParameters.filename) || [];

                emails.push(envelope);
            }

            return {
                statusCode: 200,
                body: JSON.stringify({
                    message: `The emails in the ${path} have been successfully retrieved!`,
                    totalMessages,
                    emails
                }),
            };
        } catch (error) {
            return {
                statusCode: 500,
                body: JSON.stringify({
                    message: `Failed to retrieve emails in the ${path}.`,
                    error
                })
            };
        } finally {
            await client.logout();
        }
    }

    if (path === '/move-to-trash') {
        const {smtpCredentials, path, uid} = JSON.parse(event.body);
        if ("pass" in smtpCredentials.auth) {
            const decryptedPassword = decryptPassword(smtpCredentials.auth.pass);
            if (decryptedPassword === '')
                return {
                    statusCode: 500,
                    body: JSON.stringify({
                        message: 'The secret key is invalid.'
                    }),
                };
            smtpCredentials.auth.pass = decryptedPassword;
        }

        const client = new ImapFlow(smtpCredentials);
        try {
            await client.connect();
            const mailbox = await client.mailboxOpen(path);
            const totalMessages = mailbox.exists;
            if (totalMessages === 0)
                return {
                    statusCode: 200,
                    body: JSON.stringify({
                        message: `There is no email in ${path}`,
                    })
                }
            let trashBoxName;
            if (smtpCredentials.host === 'imap.gmail.com')
                trashBoxName = "[Gmail]/Trash";
            else if (smtpCredentials.host === 'outlook.office365.com')
                trashBoxName = "Deleted Items";
            else
                trashBoxName = "Trash";
            await client.messageMove(uid, trashBoxName, {uid: true});
            return {
                statusCode: 200,
                body: JSON.stringify({
                    message: "The email has been moved to the trash."
                })
            }
        } catch (error) {
            return {
                statusCode: 500,
                body: JSON.stringify({
                    error,
                    message: "Failed to move the email to the trash."
                })
            }
        } finally {
            await client.logout();
        }
    }

    if (path === '/empty-trash') {
        const {smtpCredentials, uid} = JSON.parse(event.body);
        if ("pass" in smtpCredentials.auth) {
            const decryptedPassword = decryptPassword(smtpCredentials.auth.pass);
            if (decryptedPassword === '')
                return {
                    statusCode: 500,
                    body: JSON.stringify({
                        message: 'The secret key is invalid.'
                    }),
                };
            smtpCredentials.auth.pass = decryptedPassword;
        }

        const client = new ImapFlow(smtpCredentials);
        try {
            await client.connect();

            let trashBoxName;
            if (smtpCredentials.host === 'imap.gmail.com')
                trashBoxName = "[Gmail]/Trash";
            else if (smtpCredentials.host === 'outlook.office365.com')
                trashBoxName = "Deleted Items";
            else
                trashBoxName = "Trash";

            const mailbox = await client.mailboxOpen(trashBoxName);
            const totalMessages = mailbox.exists;
            if (totalMessages === 0)
                return {
                    statusCode: 200,
                    body: JSON.stringify({
                        message: `There is no email in the trash.`,
                    })
                }
            await client.messageDelete(uid, {uid: true});
            return {
                statusCode: 200,
                body: JSON.stringify({
                    message: `The email in the trash has been deleted successfully.`,
                })
            }
        } catch (error) {
            return {
                statusCode: 500,
                body: JSON.stringify({
                    message: `Failed to delete the email in the trash.`,
                    error
                }),
            };
        } finally {
            await client.logout();
        }
    }

    if (path === '/save-to-draft') {
        let {smtpCredentials, mailOptions} = JSON.parse(event.body);
        try {
            if ("pass" in smtpCredentials.auth) {
                const decryptedPassword = decryptPassword(smtpCredentials.auth.pass);
                if (decryptedPassword === '')
                    return {
                        statusCode: 500,
                        body: JSON.stringify({
                            message: 'The secret key is invalid.'
                        }),
                    };
                smtpCredentials.auth.pass = decryptedPassword;
            }

            let trashBoxName = smtpCredentials.host === 'imap.gmail.com' ? "[Gmail]/Drafts" : 'Drafts';

            const {status, message} = await saveEmail(smtpCredentials, mailOptions, trashBoxName);
            if (status)
                return {
                    statusCode: 200,
                    body: JSON.stringify({
                        message: 'The email has been saved as a draft!',
                    }),
                };
            else
                return {
                    statusCode: 500,
                    body: JSON.stringify({
                        message: `Failed to save the email as a drafts.`,
                        error: message
                    }),
                };
        } catch (error) {
            return {
                statusCode: 500,
                body: JSON.stringify({
                    message: `Failed to save the email as a drafts.`,
                    error
                }),
            };
        }
    }
};
