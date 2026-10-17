const i18n = {
  en: {
    brandSub:'Fraud intelligence',workspace:'WORKSPACE',overview:'Overview',transactions:'Transactions',riskAnalyzer:'Risk analyzer',reports:'Reports',modelInsights:'Model insights',demoMode:'Synthetic demo mode',noRealData:'No real customer data',systemLive:'System live',commandCenter:'COMMAND CENTER',overviewTitle:'Fraud overview',overviewDesc:'Monitor synthetic activity and spot emerging risk patterns.',aiPowered:'AI-POWERED DETECTION',heroTitle:'Know the risk.<br>Act with confidence.',heroDesc:'Explore transaction signals and inspect every model decision in one clear workspace.',analyzeNow:'Analyze transaction',keyMetrics:'Key metrics',sampleSize:'1,000 synthetic transactions',totalTransactions:'Total transactions',syntheticSample:'Synthetic sample',flaggedFraud:'Flagged fraud',ofTransactions:'of transactions',totalVolume:'Transaction volume',syntheticCurrency:'Synthetic currency units',modelAuc:'Model ROC AUC',heldOutTest:'Held-out test set',hourlyActivity:'Hourly activity',hourlyDesc:'Transactions and fraud by hour',categoryBreakdown:'Category breakdown',categoryDesc:'Fraud share by merchant category',recentTransactions:'Recent transactions',recentDesc:'A preview of the synthetic dataset',viewAll:'View all',id:'ID',merchant:'Category',channel:'Channel',amount:'Amount',time:'Time',status:'Status',dataExplorer:'DATA EXPLORER',transactionsDesc:'Browse generated records without personal information.',searchPlaceholder:'Search ID or category',allStatuses:'All statuses',fraud:'Fraud',normal:'Normal',device:'Device',decisionSupport:'DECISION SUPPORT',analyzerDesc:'Enter synthetic features to estimate fraud probability.',transactionDetails:'Transaction details',noIdentifiers:'Do not enter customer identifiers.',hour:'Hour (0–23)',countryRisk:'Country risk',low:'Low',medium:'Medium',high:'High',newDevice:'New device',no:'No',yes:'Yes',velocity:'Transactions in 1 hour',distance:'Distance (km)',accountAge:'Account age (days)',declines:'Prior declines (24h)',calculateRisk:'Calculate risk',readyToAnalyze:'Ready to analyze',resultHint:'Fill in the transaction details and calculate a risk score.',riskAssessment:'RISK ASSESSMENT',fraudProbability:'Fraud probability',observedSignals:'Observed signals',modelDisclaimer:'Synthetic demo score. A human must review any decision.',reportNote:'Report note (optional)',notePlaceholder:'Add a short note',saveReport:'Save local report',localRecords:'LOCAL RECORDS',reportsDesc:'Saved assessments stay on this computer.',savedAssessments:'Saved assessments',reportsPrivacy:'Only synthetic features, score, and your note are stored.',date:'Date',riskScore:'Risk score',riskLevel:'Risk level',note:'Note',transparentEvaluation:'TRANSPARENT EVALUATION',modelDesc:'Genuine held-out metrics on generated data.',modelName:'Gradient boosting classifier',modelBannerDesc:'Trained and evaluated on separate synthetic rows. These results do not represent real-world bank performance.',confusionMatrix:'Confusion matrix',atThreshold:'At the declared 0.20 threshold',methodology:'Methodology',method1:'Generate transactions and stochastic labels with a fixed seed.',method2:'Stratify a 75/25 train/test split before fitting preprocessing or model.',method3:'Fit only on training rows; evaluate once on untouched test rows.',method4:'Report ROC AUC, PR AUC, precision, recall, F1, and Brier score.',footer:'SentinelAI · Synthetic demonstration · No real financial actions',groceries:'Groceries',electronics:'Electronics',travel:'Travel',fuel:'Fuel',dining:'Dining',other:'Other',card_present:'Card present',online:'Online',transfer:'Transfer',new_device:'New device',high_velocity:'High velocity',country_risk:'Country risk',prior_declines:'Prior declines',large_amount:'Large amount',none:'No prominent rule signals',saved:'Report saved locally',empty:'No records to show',error:'Request failed. Please retry.',tp:'True positive',tn:'True negative',fp:'False positive',fn:'False negative',precision:'Precision',recall:'Recall',prAuc:'PR AUC',f1:'F1 score',brier:'Brier score',rows:'Test rows'
  },
  uz: {
    brandSub:'Firibgarlik tahlili',workspace:'ISH MAYDONI',overview:'Umumiy ko‘rinish',transactions:'Tranzaksiyalar',riskAnalyzer:'Risk tahlili',reports:'Hisobotlar',modelInsights:'Model natijalari',demoMode:'Sintetik demo rejimi',noRealData:'Haqiqiy mijoz ma’lumoti yo‘q',systemLive:'Tizim ishlayapti',commandCenter:'BOSHQARUV MARKAZI',overviewTitle:'Firibgarlik kuzatuvi',overviewDesc:'Sintetik faoliyat va risk tendensiyalarini kuzating.',aiPowered:'AI YORDAMIDA ANIQLASH',heroTitle:'Riskni biling.<br>Ishonch bilan qaror qiling.',heroDesc:'Tranzaksiya signallari va model baholarini bir joyda ko‘ring.',analyzeNow:'Tranzaksiyani tahlil qilish',keyMetrics:'Asosiy ko‘rsatkichlar',sampleSize:'1 000 ta sintetik tranzaksiya',totalTransactions:'Jami tranzaksiyalar',syntheticSample:'Sintetik namuna',flaggedFraud:'Firibgarlik holatlari',ofTransactions:'tranzaksiyadan',totalVolume:'Tranzaksiya hajmi',syntheticCurrency:'Shartli pul birligi',modelAuc:'Model ROC AUC',heldOutTest:'Ajratilgan test to‘plami',hourlyActivity:'Soatlik faollik',hourlyDesc:'Soat bo‘yicha tranzaksiyalar va firibgarlik',categoryBreakdown:'Toifalar bo‘yicha',categoryDesc:'Savdo toifalaridagi firibgarlik ulushi',recentTransactions:'So‘nggi tranzaksiyalar',recentDesc:'Sintetik ma’lumotlardan namuna',viewAll:'Barchasini ko‘rish',id:'ID',merchant:'Toifa',channel:'Kanal',amount:'Summa',time:'Vaqt',status:'Holat',dataExplorer:'MA’LUMOTLAR',transactionsDesc:'Shaxsiy ma’lumotlarsiz yaratilgan yozuvlarni ko‘ring.',searchPlaceholder:'ID yoki toifani qidirish',allStatuses:'Barcha holatlar',fraud:'Firibgarlik',normal:'Oddiy',device:'Qurilma',decisionSupport:'QAROR YORDAMCHISI',analyzerDesc:'Firibgarlik ehtimolini baholash uchun sintetik belgilarni kiriting.',transactionDetails:'Tranzaksiya tafsilotlari',noIdentifiers:'Mijozni aniqlovchi ma’lumotlarni kiritmang.',hour:'Soat (0–23)',countryRisk:'Mamlakat riski',low:'Past',medium:'O‘rta',high:'Yuqori',newDevice:'Yangi qurilma',no:'Yo‘q',yes:'Ha',velocity:'1 soatdagi tranzaksiyalar',distance:'Masofa (km)',accountAge:'Hisob yoshi (kun)',declines:'Rad etilganlar (24 soat)',calculateRisk:'Riskni hisoblash',readyToAnalyze:'Tahlilga tayyor',resultHint:'Tranzaksiya ma’lumotlarini kiriting va riskni hisoblang.',riskAssessment:'RISK BAHOSI',fraudProbability:'Firibgarlik ehtimoli',observedSignals:'Kuzatilgan signallar',modelDisclaimer:'Sintetik demo bahosi. Har bir qarorni inson tekshirishi kerak.',reportNote:'Hisobot izohi (ixtiyoriy)',notePlaceholder:'Qisqa izoh qo‘shing',saveReport:'Lokal hisobotni saqlash',localRecords:'LOKAL YOZUVLAR',reportsDesc:'Saqlangan baholar shu kompyuterda qoladi.',savedAssessments:'Saqlangan baholar',reportsPrivacy:'Faqat sintetik belgilar, baho va izoh saqlanadi.',date:'Sana',riskScore:'Risk bahosi',riskLevel:'Risk darajasi',note:'Izoh',transparentEvaluation:'OSHKORA BAHOLASH',modelDesc:'Yaratilgan ma’lumotlarda haqiqiy ajratilgan test natijalari.',modelName:'Gradient boosting klassifikatori',modelBannerDesc:'Alohida sintetik satrlarda o‘qitilgan va baholangan. Natijalar haqiqiy bankdagi samaradorlikni bildirmaydi.',confusionMatrix:'Xatolik matritsasi',atThreshold:'Belgilangan 0.20 chegarada',methodology:'Metodologiya',method1:'Tranzaksiyalar va ehtimoliy yorliqlar belgilangan seed bilan yaratiladi.',method2:'Qayta ishlashdan oldin 75/25 stratifikatsiyalangan bo‘linish qilinadi.',method3:'Faqat train satrlarda o‘qitilib, test satrlarda bir marta baholanadi.',method4:'ROC AUC, PR AUC, precision, recall, F1 va Brier ko‘rsatiladi.',footer:'SentinelAI · Sintetik namoyish · Haqiqiy moliyaviy amal yo‘q',groceries:'Oziq-ovqat',electronics:'Elektronika',travel:'Sayohat',fuel:'Yoqilg‘i',dining:'Ovqatlanish',other:'Boshqa',card_present:'Karta bilan',online:'Onlayn',transfer:'O‘tkazma',new_device:'Yangi qurilma',high_velocity:'Yuqori faollik',country_risk:'Mamlakat riski',prior_declines:'Oldingi radlar',large_amount:'Katta summa',none:'Muhim qoida signali yo‘q',saved:'Hisobot lokal saqlandi',empty:'Ko‘rsatish uchun yozuv yo‘q',error:'So‘rov bajarilmadi. Qayta urinib ko‘ring.',tp:'To‘g‘ri ijobiy',tn:'To‘g‘ri salbiy',fp:'Xato ijobiy',fn:'Xato salbiy',precision:'Aniqlik',recall:'Qamrov',prAuc:'PR AUC',f1:'F1 baho',brier:'Brier baho',rows:'Test satrlari'
  },
  ru: {
    brandSub:'Аналитика мошенничества',workspace:'РАБОЧАЯ ОБЛАСТЬ',overview:'Обзор',transactions:'Транзакции',riskAnalyzer:'Анализ риска',reports:'Отчёты',modelInsights:'О модели',demoMode:'Синтетический деморежим',noRealData:'Нет данных реальных клиентов',systemLive:'Система работает',commandCenter:'ЦЕНТР УПРАВЛЕНИЯ',overviewTitle:'Обзор мошенничества',overviewDesc:'Следите за синтетической активностью и динамикой риска.',aiPowered:'ОБНАРУЖЕНИЕ С ПОМОЩЬЮ ИИ',heroTitle:'Оцените риск.<br>Принимайте решения уверенно.',heroDesc:'Сигналы транзакций и оценки модели в одном месте.',analyzeNow:'Анализировать транзакцию',keyMetrics:'Ключевые показатели',sampleSize:'1 000 синтетических транзакций',totalTransactions:'Всего транзакций',syntheticSample:'Синтетическая выборка',flaggedFraud:'Случаи мошенничества',ofTransactions:'от всех транзакций',totalVolume:'Объём транзакций',syntheticCurrency:'Условные денежные единицы',modelAuc:'ROC AUC модели',heldOutTest:'Отложенная тестовая выборка',hourlyActivity:'Активность по часам',hourlyDesc:'Транзакции и мошенничество по часам',categoryBreakdown:'По категориям',categoryDesc:'Доля мошенничества в категориях',recentTransactions:'Последние транзакции',recentDesc:'Пример синтетических данных',viewAll:'Смотреть все',id:'ID',merchant:'Категория',channel:'Канал',amount:'Сумма',time:'Время',status:'Статус',dataExplorer:'ДАННЫЕ',transactionsDesc:'Изучайте созданные записи без персональных данных.',searchPlaceholder:'Поиск по ID или категории',allStatuses:'Все статусы',fraud:'Мошенничество',normal:'Обычная',device:'Устройство',decisionSupport:'ПОДДЕРЖКА РЕШЕНИЙ',analyzerDesc:'Введите синтетические признаки для оценки вероятности мошенничества.',transactionDetails:'Данные транзакции',noIdentifiers:'Не вводите идентификаторы клиентов.',hour:'Час (0–23)',countryRisk:'Риск страны',low:'Низкий',medium:'Средний',high:'Высокий',newDevice:'Новое устройство',no:'Нет',yes:'Да',velocity:'Транзакций за час',distance:'Расстояние (км)',accountAge:'Возраст счёта (дни)',declines:'Отказы за 24 часа',calculateRisk:'Рассчитать риск',readyToAnalyze:'Готово к анализу',resultHint:'Заполните данные транзакции и рассчитайте риск.',riskAssessment:'ОЦЕНКА РИСКА',fraudProbability:'Вероятность мошенничества',observedSignals:'Наблюдаемые сигналы',modelDisclaimer:'Оценка на синтетических данных. Решение должен проверять человек.',reportNote:'Примечание (необязательно)',notePlaceholder:'Добавьте короткое примечание',saveReport:'Сохранить локальный отчёт',localRecords:'ЛОКАЛЬНЫЕ ЗАПИСИ',reportsDesc:'Сохранённые оценки остаются на этом компьютере.',savedAssessments:'Сохранённые оценки',reportsPrivacy:'Хранятся только синтетические признаки, оценка и примечание.',date:'Дата',riskScore:'Оценка риска',riskLevel:'Уровень риска',note:'Примечание',transparentEvaluation:'ПРОЗРАЧНАЯ ОЦЕНКА',modelDesc:'Реальные метрики на отложенных синтетических данных.',modelName:'Классификатор градиентного бустинга',modelBannerDesc:'Обучение и оценка на разных синтетических строках. Результаты не отражают работу в реальном банке.',confusionMatrix:'Матрица ошибок',atThreshold:'При заданном пороге 0.20',methodology:'Методология',method1:'Транзакции и вероятностные метки генерируются с фиксированным seed.',method2:'До обучения выполняется стратифицированное разделение 75/25.',method3:'Обучение только на train; однократная оценка на test.',method4:'Показаны ROC AUC, PR AUC, precision, recall, F1 и Brier.',footer:'SentinelAI · Синтетическое демо · Без реальных финансовых операций',groceries:'Продукты',electronics:'Электроника',travel:'Путешествия',fuel:'Топливо',dining:'Кафе',other:'Другое',card_present:'Карта',online:'Онлайн',transfer:'Перевод',new_device:'Новое устройство',high_velocity:'Высокая частота',country_risk:'Риск страны',prior_declines:'Прошлые отказы',large_amount:'Крупная сумма',none:'Нет значимых сигналов',saved:'Отчёт сохранён локально',empty:'Нет записей',error:'Ошибка запроса. Повторите попытку.',tp:'Истинно положительный',tn:'Истинно отрицательный',fp:'Ложноположительный',fn:'Ложноотрицательный',precision:'Точность',recall:'Полнота',prAuc:'PR AUC',f1:'F1',brier:'Оценка Brier',rows:'Тестовые строки'
  }
};
Object.assign(i18n.en, {
  modelAuc:'10-seed mean PR-AUC',heldOutTest:'Synthetic tests · 95% CI in model view',
  modelBannerDesc:'Primary figures are ten-seed means with 95% seed-bootstrap intervals on synthetic data. The confusion matrix is one labelled seed-42 example, not bank performance.',
  atThreshold:'Seed 42 example · validation-selected threshold',
  modelName:'Logistic regression classifier',
  fraudProbability:'Synthetic model score',
  reportsPrivacy:'Synthetic features, score, status, note and audit history are stored locally.',
  logisticName:'Logistic regression classifier',
  atThreshold:'Validation-selected alert threshold',
  method2:'Split development chronologically: 60% fit, 20% calibration, 20% validation; use a later test seed.',
  method3:'Select the model and review threshold on validation; evaluate the selected pipeline on the later test.',
  export:'Export JSON', reviewYes:'Analyst review recommended', reviewNo:'Below review threshold',
});
Object.assign(i18n.uz, {
  modelAuc:'10 seed o‘rtacha PR-AUC',heldOutTest:'Sintetik testlar · 95% interval model sahifasida',
  modelBannerDesc:'Asosiy raqamlar 10 seed o‘rtachasi va 95% seed-bootstrap intervali. Xatolik matritsasi faqat seed 42 namunasi; bank samaradorligi emas.',
  atThreshold:'Seed 42 namunasi · validatsiyada tanlangan chegara',
  modelName:'Logistik regressiya klassifikatori',
  fraudProbability:'Sintetik model bahosi',
  reportsPrivacy:'Sintetik belgilar, baho, holat, izoh va audit tarixi lokal saqlanadi.',
  logisticName:'Logistik regressiya klassifikatori',
  atThreshold:'Validatsiyada tanlangan ogohlantirish chegarasi',
  method2:'Development vaqt bo‘yicha 60% o‘qitish, 20% kalibrlash va 20% validatsiyaga bo‘linadi; keyingi test boshqa seed bilan yaratiladi.',
  method3:'Model va chegara validatsiyada tanlanadi; tanlangan pipeline keyingi testda baholanadi.',
  export:'JSON yuklab olish', reviewYes:'Analitik tekshiruvi tavsiya etiladi', reviewNo:'Tekshiruv chegarasidan past',
});
Object.assign(i18n.ru, {
  modelAuc:'Средняя PR-AUC по 10 seed',heldOutTest:'Синтетические тесты · 95% интервал в разделе модели',
  modelBannerDesc:'Основные цифры — среднее по 10 seed и 95% seed-bootstrap интервал. Матрица ошибок — только пример seed 42, не эффективность в банке.',
  atThreshold:'Пример seed 42 · порог выбран на валидации',
  modelName:'Классификатор логистической регрессии',
  fraudProbability:'Оценка синтетической модели',
  reportsPrivacy:'Синтетические признаки, оценка, статус, заметка и аудит хранятся локально.',
  logisticName:'Классификатор логистической регрессии',
  atThreshold:'Порог оповещения, выбранный на валидации',
  method2:'Данные по времени делятся: 60% обучение, 20% калибровка, 20% валидация; поздний тест создаётся с другим seed.',
  method3:'Модель и порог выбираются на валидации; выбранный конвейер оценивается на позднем тесте.',
  export:'Скачать JSON', reviewYes:'Рекомендуется проверка аналитиком', reviewNo:'Ниже порога проверки',
});
let language = localStorage.getItem('language') || 'uz';
if (!i18n[language]) language = 'uz';
let overview, metrics, transactions = [], reports = [], csrfToken = '', lastTransaction = null;
const t = key => i18n[language][key] || i18n.en[key] || key;
const el = id => document.getElementById(id);
const format = value => new Intl.NumberFormat(language === 'uz' ? 'uz-UZ' : language === 'ru' ? 'ru-RU' : 'en-US', {maximumFractionDigits:0}).format(value);
const escapeHtml = value => String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
async function api(path, options) { const response = await fetch(path, options); if (!response.ok) throw new Error(`${response.status}`); return response.json(); }
function translate() {
  document.documentElement.lang = language;
  document.querySelectorAll('[data-i18n]').forEach(node => { const value = t(node.dataset.i18n); if (node.dataset.i18n === 'heroTitle') node.innerHTML = value; else node.textContent = value; });
  document.querySelectorAll('[data-placeholder]').forEach(node => node.placeholder = t(node.dataset.placeholder));
  el('language').value = language;
  el('current-page').textContent = t(document.querySelector('.nav-item.active').dataset.page === 'analyzer' ? 'riskAnalyzer' : document.querySelector('.nav-item.active').dataset.page === 'model' ? 'modelInsights' : document.querySelector('.nav-item.active').dataset.page);
  el('today').textContent = new Intl.DateTimeFormat(language === 'uz' ? 'uz-UZ' : language === 'ru' ? 'ru-RU' : 'en-US', {day:'numeric',month:'long',year:'numeric'}).format(new Date());
  populateSelects(); render();
}
function populateSelects() {
  const category = el('category-select'), channel = el('channel-select');
  const oldCategory = category.value || 'groceries', oldChannel = channel.value || 'card_present';
  category.innerHTML = ['groceries','electronics','travel','fuel','dining','other'].map(value => `<option value="${value}">${t(value)}</option>`).join('');
  channel.innerHTML = ['card_present','online','transfer'].map(value => `<option value="${value}">${t(value)}</option>`).join('');
  category.value = oldCategory; channel.value = oldChannel;
}
function showPage(page) {
  document.querySelectorAll('.page').forEach(node => node.classList.toggle('active', node.id === `page-${page}`));
  document.querySelectorAll('.nav-item').forEach(node => node.classList.toggle('active', node.dataset.page === page));
  el('current-page').textContent = t(page === 'analyzer' ? 'riskAnalyzer' : page === 'model' ? 'modelInsights' : page);
  window.scrollTo({top:0,behavior:'smooth'});
  if (page === 'reports') loadReports();
}
function statusBadge(row) { return `<span class="status ${row.is_fraud ? 'fraud' : 'normal'}">${t(row.is_fraud ? 'fraud' : 'normal')}</span>`; }
function rowHtml(row, full=false) { return `<tr><td>${escapeHtml(row.id)}</td><td>${t(row.merchant_category)}</td><td>${t(row.channel)}</td><td class="amount">${format(row.amount)}</td><td>${String(row.hour).padStart(2,'0')}:00</td>${full ? `<td>${t(row.is_new_device ? 'yes' : 'no')}</td>` : ''}<td>${statusBadge(row)}</td></tr>`; }
function render() {
  if (overview) {
    el('metric-total').textContent = format(overview.transactions); el('metric-fraud').textContent = format(overview.flagged); el('metric-rate').textContent = `${(overview.fraud_rate*100).toFixed(1)}%`; el('metric-volume').textContent = format(overview.total_amount); el('metric-auc').textContent = metrics.multi_seed_summary.pr_auc.mean.toFixed(4);
    const max = Math.max(...overview.hourly.map(item => item.transactions));
    el('hourly-chart').innerHTML = overview.hourly.map(item => `<div class="chart-bar" style="height:${Math.max(4,item.transactions/max*100)}%" data-tip="${String(item.hour).padStart(2,'0')}:00 · ${item.transactions} / ${item.fraud}"></div>`).join('');
    el('category-chart').innerHTML = overview.categories.map(item => {const pct = item.fraud/item.transactions*100; return `<div class="category-row"><span>${t(item.category)}</span><div class="progress"><span style="width:${pct}%"></span></div><strong>${pct.toFixed(1)}%</strong></div>`;}).join('');
  }
  el('recent-body').innerHTML = transactions.slice(0,5).map(row => rowHtml(row)).join('');
  const query = el('search').value.toLowerCase(), filter = el('filter').value;
  const visible = transactions.filter(row => (row.id.toLowerCase().includes(query) || t(row.merchant_category).toLowerCase().includes(query)) && (filter === 'all' || (filter === 'fraud') === Boolean(row.is_fraud)));
  el('transactions-body').innerHTML = visible.length ? visible.map(row => rowHtml(row,true)).join('') : `<tr><td colspan="7">${t('empty')}</td></tr>`;
  el('reports-body').innerHTML = reports.length ? reports.map(row => `<tr><td>#${row.id}</td><td>${escapeHtml(new Date(row.created_at).toLocaleString(language))}</td><td>${(row.probability*100).toFixed(1)}%</td><td><span class="risk-level ${row.level}">${t(row.level)}</span></td><td>${escapeHtml(row.note)}</td><td><a class="report-link" href="/api/reports/${row.id}/export">${t('export')}</a></td></tr>`).join('') : `<tr><td colspan="6">${t('empty')}</td></tr>`;
  if (metrics) {
    document.querySelector('[data-i18n="modelName"]').textContent = t(metrics.selected_model.startsWith('logistic') ? 'logisticName' : 'modelName');
    document.querySelector('[data-i18n="atThreshold"]').textContent = `${t('atThreshold')}: ${metrics.threshold.toFixed(4)} · ${Math.round(metrics.review_budget*100)}%`;
    const summary=metrics.multi_seed_summary;
    el('model-metrics').innerHTML = [['prAuc',summary.pr_auc],['precision',summary.exact_5pct.precision],['recall',summary.exact_5pct.recall],['f1',summary.exact_5pct.f1]].map(([key,value]) => `<article class="metric-card"><div class="metric-label">${t(key)} · ${key==='prAuc'?'10 seed':'top 5% · 10 seed'}</div><div class="metric-value">${value.mean.toFixed(3)}</div><div class="metric-foot">95% CI ${value.ci95_percentile[0].toFixed(3)}–${value.ci95_percentile[1].toFixed(3)}</div></article>`).join('');
    el('confusion').innerHTML = ['tn','fp','fn','tp'].map(key => `<div class="confusion-cell"><strong>${format(metrics.confusion_matrix[key])}</strong><span>${t(key)}</span></div>`).join('');
  }
}
async function loadReports() { try {reports = await api('/api/reports',{headers:{'X-API-Key':window.localApiKey?.()||''}}); render();} catch {el('reports-body').innerHTML = `<tr><td colspan="6">${t('error')}</td></tr>`;} }
document.addEventListener('click',async event=>{
  const anchor=event.target.closest('a[href^="/api/reports/"]');
  if(!anchor)return;
  event.preventDefault();
  try{
    const response=await fetch(anchor.getAttribute('href'),{headers:{'X-API-Key':window.localApiKey?.()||''}});
    if(!response.ok)throw new Error(`HTTP ${response.status}`);
    const name=/filename="([^"]+)"/.exec(response.headers.get('content-disposition')||'')?.[1]||'synthetic-report';
    const url=URL.createObjectURL(await response.blob());
    const link=document.createElement('a');link.href=url;link.download=name;link.click();
    setTimeout(()=>URL.revokeObjectURL(url),1000);
  }catch{el('save-message').textContent=t('error');}
});
async function scoreTransaction(event) {
  event.preventDefault();
  const values = Object.fromEntries(new FormData(event.currentTarget));
  for (const field of ['amount','hour','country_risk','velocity_1h','distance_km','account_age_days','prior_declines_24h']) values[field] = Number(values[field]);
  values.is_new_device = values.is_new_device === 'true';
  try {
    const result = await api('/api/score',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(values)});
    lastTransaction = values; el('result-empty').hidden = true; el('result').hidden = false;
    el('risk-number').textContent = `${(result.probability*100).toFixed(1)}%`;
    el('risk-level').className = `risk-level ${result.level}`; el('risk-level').textContent = `${t(result.level)} · ${t(result.review_recommended ? 'reviewYes' : 'reviewNo')}`;
    el('signals').innerHTML = result.signals.length ? result.signals.map(signal => `<span class="signal">${t(signal)}</span>`).join('') : `<span class="signal">${t('none')}</span>`;
    if (window.renderModelReasons) window.renderModelReasons(result);
    el('save-message').textContent = '';
  } catch { el('save-message').textContent = t('error'); }
}
async function saveReport() {
  if (!lastTransaction) return;
  try {
    await api('/api/reports',{method:'POST',headers:{'Content-Type':'application/json','X-CSRF-Token':csrfToken,'X-API-Key':window.localApiKey?.()||''},body:JSON.stringify({transaction:lastTransaction,note:el('report-note').value})});
    el('save-message').textContent = t('saved');
  } catch { el('save-message').textContent = t('error'); }
}
document.querySelectorAll('[data-page]').forEach(node => node.addEventListener('click',() => showPage(node.dataset.page)));
document.querySelectorAll('[data-go]').forEach(node => node.addEventListener('click',() => showPage(node.dataset.go)));
el('language').addEventListener('change',event => {language=event.target.value;localStorage.setItem('language',language);translate();});
el('search').addEventListener('input',render); el('filter').addEventListener('change',render);
el('score-form').addEventListener('submit',scoreTransaction); el('save-report').addEventListener('click',saveReport);
Promise.all([api('/api/config'),api('/api/overview'),api('/api/metrics'),api('/api/transactions?limit=100')]).then(([config,o,m,tx]) => {csrfToken=config.csrf_token;overview=o;metrics=m;transactions=tx;translate();}).catch(() => {el('metric-total').textContent=t('error');});
translate();
