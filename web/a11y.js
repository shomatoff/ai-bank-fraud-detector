// Localize accessibility labels and document title alongside visible UI text.
const accessibilityLabels = {
  uz: {nav:'Asosiy menyu', language:'Til', chart:'Soatlik tranzaksiyalar grafigi', filter:'Holat bo‘yicha saralash', title:'SentinelAI — firibgarlik tahlili'},
  ru: {nav:'Основное меню', language:'Язык', chart:'График транзакций по часам', filter:'Фильтр по статусу', title:'SentinelAI — анализ мошенничества'},
  en: {nav:'Main navigation', language:'Language', chart:'Hourly transaction chart', filter:'Filter status', title:'SentinelAI — fraud analytics'},
};
function updateAccessibilityLabels() {
  const labels = accessibilityLabels[document.documentElement.lang] || accessibilityLabels.uz;
  document.querySelector('.sidebar nav').setAttribute('aria-label', labels.nav);
  document.querySelector('#language').setAttribute('aria-label', labels.language);
  document.querySelector('#hourly-chart').setAttribute('aria-label', labels.chart);
  document.querySelector('#filter').setAttribute('aria-label', labels.filter);
  document.title = labels.title;
}
new MutationObserver(updateAccessibilityLabels).observe(document.documentElement, {attributes:true, attributeFilter:['lang']});
updateAccessibilityLabels();
