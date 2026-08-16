require('dotenv').config();
const express = require('express');
const bodyParser = require('body-parser');
const WebSocket = require('ws');
const nodemailer = require('nodemailer');
const Twilio = require('twilio');

const app = express();
app.use(bodyParser.json());

const PORT = process.env.PORT || 4000;

// Simple WebSocket server
const wss = new WebSocket.Server({ noServer: true });
let sockets = [];
wss.on('connection', function connection(ws) {
  sockets.push(ws);
  ws.on('close', () => { sockets = sockets.filter(s => s !== ws); });
});

// HTTP endpoint to receive alerts
app.post('/alert', async (req, res) => {
  const alert = req.body;
  // broadcast via websocket
  for (const s of sockets) {
    try { s.send(JSON.stringify(alert)); } catch(e){}
  }
  // send email if configured
  if (process.env.SMTP_HOST) {
    try {
      let transporter = nodemailer.createTransport({
        host: process.env.SMTP_HOST,
        port: process.env.SMTP_PORT || 587,
        secure: process.env.SMTP_SECURE === 'true',
        auth: {
          user: process.env.SMTP_USER,
          pass: process.env.SMTP_PASS
        }
      });
      await transporter.sendMail({
        from: process.env.SMTP_FROM || 'alert@example.com',
        to: process.env.ALERT_EMAILS || process.env.SMTP_USER,
        subject: `Alert: ${alert.metric} on ${alert.target}`,
        text: JSON.stringify(alert, null, 2)
      });
    } catch(e){ console.error('email error', e); }
  }
  // send SMS via Twilio if configured
  if (process.env.TWILIO_SID && process.env.TWILIO_TOKEN && process.env.TWILIO_FROM && process.env.ALERT_SMS_TO) {
    try {
      const client = Twilio(process.env.TWILIO_SID, process.env.TWILIO_TOKEN);
      await client.messages.create({ body: `Alert: ${alert.metric} ${alert.value} on ${alert.target}`, from: process.env.TWILIO_FROM, to: process.env.ALERT_SMS_TO });
    } catch(e){ console.error('sms error', e); }
  }
  res.json({status: 'ok'});
});

// Basic health
app.get('/health', (req,res)=>res.json({status:'ok'}));

const server = app.listen(PORT, ()=>console.log('node notifier listening', PORT));
server.on('upgrade', function upgrade(request, socket, head) {
  wss.handleUpgrade(request, socket, head, function done(ws) { wss.emit('connection', ws, request); });
});
