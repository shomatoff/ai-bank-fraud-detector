// Capture real pages from a running local server via Chrome DevTools Protocol.
import { spawn } from 'node:child_process';
import { mkdtemp, mkdir, readFile, writeFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';

const profile = await mkdtemp(join(tmpdir(), 'sentinel-chrome-'));
const port = 9227;
const appPort = process.env.APP_PORT || "8000";
const chrome = spawn('/usr/bin/google-chrome', [
  '--headless=new', '--no-sandbox', '--disable-gpu', '--disable-dev-shm-usage',
  `--remote-debugging-port=${port}`, `--user-data-dir=${profile}`, 'about:blank',
], {stdio:'ignore'});
const pause = ms => new Promise(resolve => setTimeout(resolve, ms));
let ws;
try {
  let target;
  for (let i=0; i<50; i++) {
    try { target = (await (await fetch(`http://127.0.0.1:${port}/json`)).json()).find(x => x.type === 'page'); if (target) break; } catch {}
    await pause(200);
  }
  if (!target) throw new Error('Chrome did not start');
  ws = new WebSocket(target.webSocketDebuggerUrl);
  await new Promise((resolve, reject) => {ws.onopen=resolve;ws.onerror=reject;});
  let id=0; const pending=new Map();
  ws.onmessage = event => {const message=JSON.parse(event.data);if (message.id && pending.has(message.id)) {const {resolve,reject}=pending.get(message.id);pending.delete(message.id);message.error?reject(new Error(message.error.message)):resolve(message.result);}};
  const send = (method, params={}) => new Promise((resolve,reject) => {const key=++id;pending.set(key,{resolve,reject});ws.send(JSON.stringify({id:key,method,params}));});
  await send('Emulation.setDeviceMetricsOverride',{width:1440,height:1000,deviceScaleFactor:1,mobile:false});
  await send('Page.navigate',{url:`http://127.0.0.1:${appPort}/`});
  await pause(2200);
  await mkdir(resolve('screenshots'),{recursive:true});
  const capture = async name => {const {data}=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});await writeFile(resolve('screenshots',name),Buffer.from(data,'base64'));};
  const evalJs = expression => send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});
  const assertJs = async (expression, message) => {const result=await evalJs(expression);if(result.exceptionDetails || !result.result.value) throw new Error(message);};
  await assertJs("document.querySelector('#metric-total').textContent !== '—'", 'Overview data did not load');
  await capture('01-overview-uz.png');
  await evalJs("document.querySelector('[data-page=\"analyzer\"]').click()");
  await pause(350);
  await evalJs("document.querySelector('input[name=amount]').value='2400';document.querySelector('select[name=is_new_device]').value='true';document.querySelector('input[name=velocity_1h]').value='6';document.querySelector('input[name=prior_declines_24h]').value='2';document.querySelector('#score-form').requestSubmit()");
  await pause(750);
  await assertJs("!document.querySelector('#result').hidden && document.querySelector('#risk-number').textContent.includes('%')", 'Risk scoring did not render');
  await assertJs("document.querySelector('#ux-reasons').textContent.length > 15", 'Model-based reasons did not render');
  await capture('02-risk-analyzer-uz.png');
  await evalJs("document.querySelector('#ux-reasons').scrollIntoView()");
  await capture('08-model-reasons-uz.png');
  const analystKey = process.env.SENTINELAI_ANALYST_KEY || JSON.parse(await readFile(resolve('data/local-api-keys.json'), 'utf8')).analyst;
  await evalJs(`document.querySelector('#ux-api-key').value=${JSON.stringify(analystKey)};document.querySelector('#ux-api-key').dispatchEvent(new Event('input'))`);
  await assertJs("document.querySelector('#ux-api-key').type==='password' && window.localApiKey().length>20", 'Local analyst key input failed');
  await evalJs("document.querySelector('#save-report').click()");
  await pause(450);
  await assertJs("document.querySelector('#save-message').textContent.length > 0", 'Report save status is missing');
  await evalJs("document.querySelector('[data-page=\"reports\"]').click()");
  await pause(450);
  await assertJs("document.querySelector('#reports-body a.report-link') !== null", 'Report export link is missing');
  await assertJs("fetch(document.querySelector('#reports-body a.report-link').href).then(r=>r.json()).then(x=>x.data_source==='synthetic')", 'Report export did not return synthetic JSON');
  await capture('05-reports-uz.png');
  await evalJs("document.querySelector('#ux-report-id').value=Number(document.querySelector('#reports-body a.report-link').href.match(/\\d+(?=\\/export$)/)[0]);document.querySelector('#ux-report-id').dispatchEvent(new Event('change'))");
  await pause(350);
  await evalJs("document.querySelector('#ux-status').value='in_review';document.querySelector('#ux-note').value='Synthetic analyst review';document.querySelector('#ux-save').click()");
  await pause(450);
  await assertJs("document.querySelectorAll('#ux-audit p').length >= 2 && document.querySelector('#ux-review-message').textContent.length > 0", 'Status review was not saved');
  await evalJs("document.querySelector('#ux-note').value='Updated synthetic note';document.querySelector('#ux-save').click()");
  await pause(450);
  await assertJs("document.querySelectorAll('#ux-audit p').length >= 3", 'Note-only audit entry was not saved');
  await capture('07-analyst-workflow-uz.png');
  await capture('09-v5-keyed-workflow-uz.png');
  await evalJs("document.querySelector('#language').value='ru';document.querySelector('#language').dispatchEvent(new Event('change'));document.querySelector('[data-page=\"model\"]').click()");
  await pause(350);
  await assertJs("document.documentElement.lang==='ru' && document.querySelector('#model-metrics').children.length > 0", 'Russian model page did not render');
  await capture('03-model-ru.png');
  await assertJs("document.querySelectorAll('#ux-curves svg').length === 3 && document.querySelector('#ux-monitor table')", 'Diagnostic curves or slice table missing');
  await evalJs("document.querySelector('#ux-curves').scrollIntoView()");
  await capture('06-model-diagnostics-ru.png');
  await evalJs("document.querySelector('#language').value='en';document.querySelector('#language').dispatchEvent(new Event('change'));document.querySelector('[data-page=\"transactions\"]').click()");
  await pause(350);
  await assertJs("document.documentElement.lang==='en' && document.querySelector('#transactions-body').children.length > 0", 'English transaction page did not render');
  await capture('04-transactions-en.png');
  console.log('Verified live pages, explanations, keyed status/note audit and captured 9 screenshots');
} finally {
  ws?.close(); chrome.kill(); if (chrome.exitCode === null && chrome.signalCode === null) await new Promise(resolve => chrome.once("exit", resolve)); await rm(profile,{recursive:true,force:true,maxRetries:5,retryDelay:100});
}
