// Live, read-only Chrome smoke test for the local dashboard additions.
import {spawn} from 'node:child_process';
import {mkdtemp, readFile, rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join, resolve} from 'node:path';

const profile = await mkdtemp(join(tmpdir(), 'sentinel-dashboard-'));
const port = 9238;
const appPort = process.env.APP_PORT || '8000';
const chrome = spawn('/usr/bin/google-chrome', [
  '--headless=new', '--no-sandbox', '--disable-gpu', '--disable-dev-shm-usage',
  `--remote-debugging-port=${port}`, `--user-data-dir=${profile}`, 'about:blank',
], {stdio:'ignore'});
const pause = ms => new Promise(done => setTimeout(done, ms));
let socket;
try {
  let target;
  for (let attempt = 0; attempt < 50; attempt++) {
    try {
      target = (await (await fetch(`http://127.0.0.1:${port}/json`)).json()).find(item => item.type === 'page');
      if (target) break;
    } catch { /* Chrome is still starting. */ }
    await pause(200);
  }
  if (!target) throw new Error('Chrome did not start');
  socket = new WebSocket(target.webSocketDebuggerUrl);
  await new Promise((done, fail) => {socket.onopen = done; socket.onerror = fail;});
  let id = 0;
  const pending = new Map();
  const exceptions = [];
  socket.onmessage = event => {
    const message = JSON.parse(event.data);
    if (message.method === 'Runtime.exceptionThrown') exceptions.push(message.params.exceptionDetails.text);
    if (message.id && pending.has(message.id)) {
      const {done, fail} = pending.get(message.id);
      pending.delete(message.id);
      message.error ? fail(new Error(message.error.message)) : done(message.result);
    }
  };
  const send = (method, params = {}) => new Promise((done, fail) => {
    const key = ++id;
    pending.set(key, {done, fail});
    socket.send(JSON.stringify({id:key, method, params}));
  });
  const evaluate = async expression => {
    const result = await send('Runtime.evaluate', {expression, returnByValue:true, awaitPromise:true});
    if (result.exceptionDetails) throw new Error(result.exceptionDetails.text);
    return result.result.value;
  };
  const assert = async (expression, message) => {
    if (!await evaluate(expression)) throw new Error(message);
  };
  await send('Runtime.enable');
  await send('Emulation.setDeviceMetricsOverride', {width:1440,height:900,deviceScaleFactor:1,mobile:false});
  await send('Page.navigate', {url:`http://127.0.0.1:${appPort}/`});
  await pause(2000);
  await assert("document.querySelector('#metric-total').textContent !== '—'", 'Overview did not load');
  await assert("document.querySelectorAll('#capability-grid .capability-card').length === 11", 'Capability catalog incomplete');
  await evaluate("document.querySelector('[data-page=queue]').click()");
  await pause(700);
  await assert("document.querySelectorAll('#queue-body tr').length === 20", 'Queue did not show 20 cases');
  await assert("document.querySelector('#queue-summary').textContent.includes('20')", 'Queue summary missing');
  await evaluate("document.querySelector('#queue-capacity').value='5';document.querySelector('#queue-capacity').dispatchEvent(new Event('change'))");
  await pause(500);
  await assert("document.querySelectorAll('#queue-body tr').length === 5", 'Queue capacity did not update');
  await evaluate("document.querySelector('[data-page=operations]').click()");
  await pause(750);
  await assert("document.querySelectorAll('#operations-metrics .metric-card').length === 4", 'Monitoring metrics missing');
  await assert("document.querySelectorAll('#operations-drift .drift-row').length === 2", 'Drift diagnostics missing');
  const keys = JSON.parse(await readFile(resolve('data/local-api-keys.json'), 'utf8'));
  await evaluate(`document.querySelector('#operations-admin-key').value=${JSON.stringify(keys.admin)};document.querySelector('#feedback-refresh').click()`);
  await pause(500);
  await assert("document.querySelectorAll('#feedback-summary .feedback-cell').length === 5", 'Admin feedback summary missing');
  await assert("!document.querySelector('#feedback-summary').textContent.includes('NaN')", 'Feedback field mismatch');
  await assert("document.querySelector('#operations-admin-key').value === ''", 'Admin key stayed in input');
  await evaluate("document.querySelector('[data-page=capabilities]').click()");
  await assert("document.querySelector('#feedback-summary').textContent === ''", 'Feedback persisted after leaving');
  await assert("document.querySelectorAll('#capability-grid .cap-status.local').length === 8", 'Local capability legend mismatch');
  await evaluate("document.querySelector('#language').value='ru';document.querySelector('#language').dispatchEvent(new Event('change'))");
  await assert("document.documentElement.lang==='ru' && document.querySelector('#page-capabilities h1').textContent==='Возможности'", 'Russian translation missing');
  await evaluate("document.querySelector('#language').value='en';document.querySelector('#language').dispatchEvent(new Event('change'))");
  await assert("document.querySelector('#page-capabilities h1').textContent==='Capabilities'", 'English translation missing');
  await send('Emulation.setDeviceMetricsOverride', {width:390,height:844,deviceScaleFactor:1,mobile:true});
  await pause(200);
  await assert("document.documentElement.scrollWidth <= innerWidth + 1", 'Mobile page overflows horizontally');
  await assert("getComputedStyle(document.querySelector('#capability-grid')).gridTemplateColumns.split(' ').length === 1", 'Mobile cards are not stacked');
  if (exceptions.length) throw new Error(`Browser exceptions: ${exceptions.join('; ')}`);
  console.log('Dashboard smoke passed: 3 languages, queue, monitoring, admin feedback, capabilities, mobile layout.');
} finally {
  socket?.close();
  chrome.kill();
  if (chrome.exitCode === null && chrome.signalCode === null) await new Promise(done => chrome.once('exit', done));
  await rm(profile, {recursive:true, force:true, maxRetries:5, retryDelay:100});
}
