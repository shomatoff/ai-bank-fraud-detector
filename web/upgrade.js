// Synthetic analyst tools; no real bank actions.
const uxWords = {
  en: {reasons:'Model-based linear reasons',reasonNote:'Exact calibrated log-odds contributions; not causal. Separate from descriptive rules.',rules:'Descriptive rules, not model attribution',threshold:'Validation threshold sandbox',thresholdNote:'Validation-only estimates. The slider does not change the deployed threshold or test results.',fp:'False-positive cost',fn:'Missed-fraud cost',budget:'Review cap',optimize:'Choose lowest-cost threshold',alerts:'Alerts',precision:'Precision',recall:'Recall',cost:'Estimated cost',curves:'Synthetic test PR, ROC and reliability',curveNote:'Descriptive held-out plots; never tune on this test.',monitor:'Synthetic PSI and slices',monitorNote:'A drift simulation, not production monitoring or a fairness audit.',batch:'Batch synthetic CSV scoring',batchNote:'Exact ten-column header, UTF-8, at most 1 MB and 1,000 rows. No identifiers.',scoreCsv:'Score and download CSV',workflow:'Analyst case workflow',workflowNote:'Local synthetic reports; each status change and note is logged.',reportId:'Report ID',status:'Status',note:'Analyst note',save:'Save review',audit:'Local audit history',allCsv:'All reports CSV',updated:'Review saved',loadError:'Report could not be loaded',new:'New',in_review:'In review',confirmed_fraud:'Confirmed fraud',false_positive:'False positive',rows:'Rows',prevalence:'Fraud prevalence',fpr:'False-positive rate'},
  uz: {reasons:'Modelga asoslangan chiziqli sabablar',reasonNote:'Kalibrlangan log-oddsga aniq hissa; sababiy xulosa emas. Tavsifiy qoidalardan alohida.',rules:'Tavsifiy qoidalar, model atributsiyasi emas',threshold:'Validatsiya chegarasi sinovi',thresholdNote:'Faqat validatsiya bahosi. Slayder amaldagi chegara yoki test natijasini o‘zgartirmaydi.',fp:'Yolg‘on ogohlantirish xarajati',fn:'O‘tkazib yuborish xarajati',budget:'Ko‘rib chiqish limiti',optimize:'Eng arzon chegarani tanlash',alerts:'Ogohlantirishlar',precision:'Aniqlik',recall:'Qamrov',cost:'Taxminiy xarajat',curves:'Sintetik testning PR, ROC va ishonchlilik grafiklari',curveNote:'Ajratilgan testni faqat tasvirlaydi; unda sozlash mumkin emas.',monitor:'Sintetik PSI va guruhlar',monitorNote:'Drift simulyatsiyasi; production monitoring yoki fairness auditi emas.',batch:'Sintetik CSV ni ommaviy baholash',batchNote:'Aniq o‘nta ustun, UTF-8, eng ko‘pi 1 MB va 1 000 satr. Identifikator yo‘q.',scoreCsv:'Baholab CSV yuklash',workflow:'Analitik ish oqimi',workflowNote:'Lokal sintetik hisobot; har bir holat va izoh o‘zgarishi qayd etiladi.',reportId:'Hisobot ID',status:'Holat',note:'Analitik izohi',save:'Tekshiruvni saqlash',audit:'Lokal audit tarixi',allCsv:'Barcha hisobotlar CSV',updated:'Tekshiruv saqlandi',loadError:'Hisobot yuklanmadi',new:'Yangi',in_review:'Tekshiruvda',confirmed_fraud:'Firibgarlik tasdiqlandi',false_positive:'Yolg‘on ogohlantirish',rows:'Satrlar',prevalence:'Firibgarlik ulushi',fpr:'Yolg‘on ijobiy ulushi'},
  ru: {reasons:'Линейные причины по модели',reasonNote:'Точный вклад в калиброванные логарифмические шансы; не причинность. Отдельно от правил.',rules:'Описательные правила, не вклад модели',threshold:'Порог на валидации',thresholdNote:'Только валидационные оценки. Ползунок не меняет рабочий порог или тест.',fp:'Цена ложного срабатывания',fn:'Цена пропуска',budget:'Лимит проверки',optimize:'Выбрать порог минимальных затрат',alerts:'Предупреждения',precision:'Точность',recall:'Полнота',cost:'Оценка затрат',curves:'PR, ROC и надёжность синтетического теста',curveNote:'Описательные графики; на тесте нельзя настраивать модель.',monitor:'Синтетический PSI и сегменты',monitorNote:'Симуляция дрейфа, не production-мониторинг и не аудит справедливости.',batch:'Пакетная оценка синтетического CSV',batchNote:'Точно десять столбцов, UTF-8, максимум 1 МБ и 1 000 строк. Без идентификаторов.',scoreCsv:'Оценить и скачать CSV',workflow:'Работа аналитика',workflowNote:'Локальные синтетические отчёты; все изменения статуса и заметок записываются.',reportId:'ID отчёта',status:'Статус',note:'Примечание аналитика',save:'Сохранить проверку',audit:'Локальный журнал аудита',allCsv:'Все отчёты CSV',updated:'Проверка сохранена',loadError:'Не удалось загрузить отчёт',new:'Новый',in_review:'На проверке',confirmed_fraud:'Мошенничество подтверждено',false_positive:'Ложное срабатывание',rows:'Строки',prevalence:'Доля мошенничества',fpr:'Доля ложноположительных'},
};
uxWords.en.reasonNote='Exact selected-model log-odds contributions; calibration may be disabled. Not causal; separate from rules.';
uxWords.uz.reasonNote='Tanlangan model log-oddsiga aniq hissa; kalibrlash o‘chirilgan bo‘lishi mumkin. Sababiy emas; qoidalardan alohida.';
uxWords.ru.reasonNote='Точный вклад в логарифмические шансы выбранной модели; калибровка может быть отключена. Не причинность; отдельно от правил.';
const uxExtra = {
  en: {thresholdLabel:'Threshold',exportLabel:'Export',slice:'Slice',chooseCsv:'Choose CSV',maxMb:'1 MB max',psi:'PSI validation→test',shift:'1.5× amount simulation',reliability:'Reliability',accountAge:'Account age',under90:'Under 90 days',older90:'90 days or more',night:'Night hour',youngAccount:'Young account',logAmount:'Log amount',apiKey:'Local analyst/admin API key',notEvaluable:'Not evaluable (<30 positives)'},
  uz: {thresholdLabel:'Chegara',exportLabel:'Eksport',slice:'Guruh',chooseCsv:'CSV tanlang',maxMb:'Eng ko‘pi 1 MB',psi:'PSI validatsiya→test',shift:'Summani 1.5× oshirish simulyatsiyasi',reliability:'Ishonchlilik',accountAge:'Hisob yoshi',under90:'90 kundan kam',older90:'90 kun yoki ko‘p',night:'Tungi soat',youngAccount:'Yangi hisob',logAmount:'Summaning log qiymati',apiKey:'Lokal analitik/admin API kaliti',notEvaluable:'Baholab bo‘lmaydi (<30 ijobiy)'},
  ru: {thresholdLabel:'Порог',exportLabel:'Экспорт',slice:'Сегмент',chooseCsv:'Выберите CSV',maxMb:'Не более 1 МБ',psi:'PSI валидация→тест',shift:'Симуляция суммы ×1.5',reliability:'Надёжность',accountAge:'Возраст счёта',under90:'Менее 90 дней',older90:'90 дней и более',night:'Ночной час',youngAccount:'Новый счёт',logAmount:'Логарифм суммы',apiKey:'Локальный API-ключ аналитика/администратора',notEvaluable:'Нельзя оценить (<30 положительных)'},
};
const ux = key => {const lang=document.querySelector('#language').value;return (uxWords[lang]||uxWords.uz)[key]||(uxExtra[lang]||uxExtra.uz)[key]||key;};
const uxid = id => document.getElementById(id);
const pct = value => (100 * Number(value || 0)).toFixed(1) + '%';
let uxMetrics, uxToken, uxReason, uxPreview, uxReport, uxAudit = [];

function featureName(feature) {
  const raw = feature.replace(/^category__|^numeric__/, '');
  if (raw.startsWith('merchant_category_')) return t('merchant') + ': ' + t(raw.slice(18));
  if (raw.startsWith('channel_')) return t('channel') + ': ' + t(raw.slice(8));
  const keys = {amount:'amount',hour:'hour',country_risk:'countryRisk',is_new_device:'newDevice',velocity_1h:'velocity',distance_km:'distance',account_age_days:'accountAge',prior_declines_24h:'declines'};
  const derived = {night:'night',young_account:'youngAccount',log_amount:'logAmount'};
  return keys[raw] ? t(keys[raw]) : derived[raw] ? ux(derived[raw]) : raw.replaceAll('_', ' ');
}

function sliceName(dimension, value) {
  const label = {channel:t('channel'),country_risk:t('countryRisk'),account_age:ux('accountAge')}[dimension] || dimension;
  const item = value === 'under_90_days' ? ux('under90') : value === '90_days_or_more' ? ux('older90') : dimension === 'channel' ? t(value) : value;
  return label + ': ' + item;
}

function panel(title, note, content) {
  const node = document.createElement('article');
  node.className = 'panel upgrade-panel';
  node.innerHTML = '<div class="panel-head"><div><h2 data-ux="' + title + '"></h2><p data-ux="' + note + '"></p></div></div>' + content;
  return node;
}
const reasonBox = panel('reasons','reasonNote','<div id="ux-reasons"></div>');
uxid('result').append(reasonBox);
const ruleCaption = document.createElement('p');
ruleCaption.className = 'upgrade-help';
ruleCaption.dataset.ux = 'rules';
uxid('signals').before(ruleCaption);
window.renderModelReasons = result => {uxReason = result.model_explanation; renderReasons();};
uxid('page-analyzer').append(panel('batch','batchNote','<div class="upgrade-controls"><input id="ux-batch-file" type="file" accept=".csv,text/csv" aria-label="CSV"><button id="ux-batch-go" class="secondary" data-ux="scoreCsv"></button></div><p id="ux-batch-message" class="upgrade-help" role="status"></p>'));
uxid('page-model').append(panel('threshold','thresholdNote','<div class="upgrade-controls"><label><span data-ux="thresholdLabel"></span> <output id="ux-threshold-value"></output><input id="ux-threshold" type="range" min="0" max="1" step=".005"></label><label><span data-ux="fp"></span><input id="ux-fp" type="number" min="0" max="100000" value="1"></label><label><span data-ux="fn"></span><input id="ux-fn" type="number" min="0" max="100000" value="10"></label><label><span data-ux="budget"></span><select id="ux-budget"><option value=".05">5%</option><option value=".1" selected>10%</option><option value=".2">20%</option></select></label><button id="ux-optimize" class="secondary" data-ux="optimize"></button></div><div id="ux-preview" class="upgrade-stats" aria-live="polite"></div>'));
uxid('page-model').append(panel('curves','curveNote','<div id="ux-curves" class="upgrade-curves"></div>'));
uxid('page-model').append(panel('monitor','monitorNote','<div id="ux-monitor"></div>'));
uxid('page-reports').append(panel('workflow','workflowNote','<div class="upgrade-controls"><label><span data-ux="reportId"></span><input id="ux-report-id" type="number" min="1"></label><label><span data-ux="status"></span><select id="ux-status"></select></label><label><span data-ux="note"></span><input id="ux-note" maxlength="300"></label><button id="ux-save" class="secondary" data-ux="save"></button></div><p id="ux-review-message" class="upgrade-help" role="status"></p><p class="upgrade-help"><span data-ux="exportLabel"></span>: <a id="ux-json" href="#">JSON</a> · <a id="ux-html" href="#">HTML</a> · <a id="ux-pdf" href="#">PDF</a> · <a href="/api/reports/export.csv" data-ux="allCsv"></a></p><h3 data-ux="audit"></h3><div id="ux-audit" class="upgrade-audit"></div>'));
uxid('page-analyzer').append(panel('apiKey','workflowNote','<label><span data-ux="apiKey"></span><input id="ux-api-key" type="password" autocomplete="off"></label>'));
uxid('ux-api-key').value=sessionStorage.getItem('sentinelai-api-key')||'';
uxid('ux-api-key').addEventListener('input',event=>sessionStorage.setItem('sentinelai-api-key',event.target.value));
window.localApiKey=()=>sessionStorage.getItem('sentinelai-api-key')||'';

function renderReasons() {
  if (!uxReason) return;
  const target = uxid('ux-reasons');
  target.replaceChildren();
  for (const reason of uxReason.top_reasons) {
    const row = document.createElement('div');
    row.className = 'upgrade-reason';
    const name = document.createElement('span');
    name.textContent = featureName(reason.feature);
    const value = document.createElement('strong');
    value.className = reason.contribution >= 0 ? 'upgrade-up' : 'upgrade-down';
    value.textContent = (reason.contribution >= 0 ? '+' : '') + reason.contribution.toFixed(3) + ' log-odds';
    row.append(name,value);
    target.append(row);
  }
}
function renderPreview() {
  if (!uxPreview) return;
  uxid('ux-threshold-value').textContent = Number(uxid('ux-threshold').value).toFixed(3);
  const values = [[ux('alerts'),uxPreview.alerts + ' / ' + uxPreview.validation_rows + ' (' + pct(uxPreview.alert_rate) + ')'],[ux('precision'),pct(uxPreview.precision)],[ux('recall'),pct(uxPreview.recall)],[ux('cost'),Number(uxPreview.estimated_cost).toFixed(1)]];
  uxid('ux-preview').replaceChildren(...values.map(([key,value])=>{
    const node=document.createElement('div');node.className='upgrade-stat';
    const label=document.createElement('small');label.textContent=key;
    const number=document.createElement('strong');number.textContent=value;
    node.append(label,number);return node;
  }));
}
async function requestPreview(optimize) {
  const payload={threshold:optimize?null:Number(uxid('ux-threshold').value),false_positive_cost:Number(uxid('ux-fp').value),false_negative_cost:Number(uxid('ux-fn').value),review_budget:Number(uxid('ux-budget').value)};
  try {
    const response=await fetch('/api/threshold/preview',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
    if(!response.ok)throw new Error('HTTP '+response.status);
    uxPreview=await response.json();
    if(optimize)uxid('ux-threshold').value=String(uxPreview.threshold);
    renderPreview();
  } catch(error) {uxid('ux-preview').textContent=String(error);}
}
let previewDelay;
uxid('ux-threshold').addEventListener('input',()=>{uxid('ux-threshold-value').textContent=Number(uxid('ux-threshold').value).toFixed(3);clearTimeout(previewDelay);previewDelay=setTimeout(()=>requestPreview(false),120);});
for(const id of ['ux-fp','ux-fn','ux-budget'])uxid(id).addEventListener('change',()=>requestPreview(false));
uxid('ux-optimize').addEventListener('click',()=>requestPreview(true));

function lineChart(title,x,y) {
  const box=document.createElement('div');box.className='upgrade-chart';
  const heading=document.createElement('strong');heading.textContent=title;
  const svg=document.createElementNS('http://www.w3.org/2000/svg','svg');
  svg.setAttribute('viewBox','0 0 310 170');svg.setAttribute('role','img');svg.setAttribute('aria-label',title);
  const axis=document.createElementNS('http://www.w3.org/2000/svg','path');
  axis.setAttribute('d','M24 24V142H284');axis.setAttribute('fill','none');axis.setAttribute('stroke','#52617e');
  const line=document.createElementNS('http://www.w3.org/2000/svg','polyline');
  line.setAttribute('points',x.map((value,i)=>(24+260*Math.max(0,Math.min(1,value)))+','+(142-118*Math.max(0,Math.min(1,y[i])))).join(' '));
  line.setAttribute('fill','none');line.setAttribute('stroke','#aa93ff');line.setAttribute('stroke-width','2');
  svg.append(axis,line);box.append(heading,svg);return box;
}
function renderDiagnostics() {
  if(!uxMetrics)return;
  const curves=uxMetrics.diagnostic_curves;
  uxid('ux-curves').replaceChildren(
    lineChart('Precision–Recall',curves.precision_recall.recall,curves.precision_recall.precision),
    lineChart('ROC',curves.roc.fpr,curves.roc.tpr),
    lineChart(ux('reliability'),curves.reliability.predicted,curves.reliability.observed));
  const monitor=uxid('ux-monitor');monitor.replaceChildren();
  const psi=document.createElement('p');psi.className='upgrade-help';
  psi.textContent=ux('psi')+': '+uxMetrics.monitoring.drift.amount_validation_vs_test_psi.toFixed(3)+' · '+ux('shift')+': '+uxMetrics.monitoring.drift.amount_shifted_1_5x_psi.toFixed(3);
  monitor.append(psi);
  const table=document.createElement('table');table.className='upgrade-slices';
  const header=document.createElement('tr');
  [ux('slice'),ux('rows'),ux('prevalence'),ux('precision'),ux('recall'),ux('fpr')].forEach(value=>{const cell=document.createElement('th');cell.textContent=value;header.append(cell);});
  table.append(header);
  for(const [dimension,entries] of Object.entries(uxMetrics.monitoring.slices))
    for(const [value,item] of Object.entries(entries)){
      const row=document.createElement('tr');
      [sliceName(dimension,value),item.rows,pct(item.fraud_prevalence),pct(item.precision),item.recall===null?ux('notEvaluable'):pct(item.recall),pct(item.fpr)].forEach(v=>{const cell=document.createElement('td');cell.textContent=String(v);row.append(cell);});
      table.append(row);
    }
  monitor.append(table);
}
function renderReport(){
  if(!uxReport)return;
  const transitions={new:['in_review'],in_review:['confirmed_fraud','false_positive'],confirmed_fraud:['in_review'],false_positive:['in_review']};
  uxid('ux-status').replaceChildren(...[uxReport.status,...transitions[uxReport.status]].map(value=>{const option=document.createElement('option');option.value=value;option.textContent=ux(value);return option;}));
  uxid('ux-note').value=uxReport.note||'';
  for(const [name,suffix] of [['json','export'],['html','export.html'],['pdf','export.pdf']])uxid('ux-'+name).href='/api/reports/'+uxReport.id+'/'+suffix;
  uxid('ux-audit').replaceChildren(...uxAudit.map(item=>{
    const node=document.createElement('p');
    node.textContent=new Date(item.created_at).toLocaleString()+' · '+(item.old_status?ux(item.old_status)+' → ':'')+ux(item.new_status)+' · '+item.note;
    return node;
  }));
}
async function loadReport(){
  const id=Number(uxid('ux-report-id').value);
  if(!Number.isInteger(id)||id<1)return;
  try{
    const options={headers:{'X-API-Key':window.localApiKey()}};
    const [report,audit]=await Promise.all([fetch('/api/reports/'+id,options).then(r=>{if(!r.ok)throw new Error();return r.json();}),fetch('/api/reports/'+id+'/audit',options).then(r=>{if(!r.ok)throw new Error();return r.json();})]);
    uxReport=report;uxAudit=audit;renderReport();
  }catch{uxid('ux-review-message').textContent=ux('loadError');}
}
uxid('ux-report-id').addEventListener('change',loadReport);
uxid('ux-save').addEventListener('click',async()=>{
  if(!uxReport)return;
  const response=await fetch('/api/reports/'+uxReport.id,{method:'PATCH',headers:{'Content-Type':'application/json','X-CSRF-Token':uxToken,'X-API-Key':window.localApiKey()},body:JSON.stringify({status:uxid('ux-status').value,note:uxid('ux-note').value})});
  if(!response.ok){uxid('ux-review-message').textContent='HTTP '+response.status;return;}
  uxid('ux-review-message').textContent=ux('updated');await loadReport();
});
uxid('ux-batch-go').addEventListener('click',async()=>{
  const file=uxid('ux-batch-file').files[0];
  if(!file){uxid('ux-batch-message').textContent=ux('chooseCsv');return;}
  if(file.size>1000000){uxid('ux-batch-message').textContent=ux('maxMb');return;}
  try{
    const response=await fetch('/api/score/batch',{method:'POST',headers:{'Content-Type':'text/csv'},body:file});
    if(!response.ok)throw new Error('HTTP '+response.status+': '+await response.text());
    const url=URL.createObjectURL(await response.blob());
    const link=document.createElement('a');link.href=url;link.download='synthetic-batch-scores.csv';link.click();
    setTimeout(()=>URL.revokeObjectURL(url),1000);
    uxid('ux-batch-message').textContent=ux('scoreCsv');
  }catch(error){uxid('ux-batch-message').textContent=String(error);}
});
new MutationObserver(()=>{
  if(uxid('page-reports').classList.contains('active'))fetch('/api/reports',{headers:{'X-API-Key':window.localApiKey()}}).then(r=>{if(!r.ok)throw new Error();return r.json();}).then(rows=>{
    if(rows.length&&!uxid('ux-report-id').value){uxid('ux-report-id').value=rows[0].id;loadReport();}
  }).catch(()=>{});
}).observe(uxid('page-reports'),{attributes:true,attributeFilter:['class']});
function translateUpgrade(){document.querySelectorAll('[data-ux]').forEach(node=>{node.textContent=ux(node.dataset.ux);});renderReasons();renderPreview();renderReport();renderDiagnostics();}
uxid('language').addEventListener('change',translateUpgrade);
Promise.all([fetch('/api/config').then(r=>r.json()),fetch('/api/metrics').then(r=>r.json())]).then(([config,metrics])=>{
  uxToken=config.csrf_token;uxMetrics=metrics;uxid('ux-threshold').value=String(metrics.threshold);
  requestPreview(false);renderDiagnostics();
}).catch(error=>{uxid('ux-preview').textContent=String(error);});
translateUpgrade();
