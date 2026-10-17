// Localize accessibility labels and document title alongside visible UI text.
const accessibilityLabels = {
  uz: {nav:'Asosiy menyu',reviewNav:'Tekshiruv va nazorat menyusi',language:'Til', chart:'Soatlik tranzaksiyalar grafigi', filter:'Holat bo‘yicha saralash', title:'SentinelAI — firibgarlik tahlili'},
  ru: {nav:'Основное меню',reviewNav:'Меню проверки и контроля',language:'Язык', chart:'График транзакций по часам', filter:'Фильтр по статусу', title:'SentinelAI — анализ мошенничества'},
  en: {nav:'Main navigation',reviewNav:'Review and control navigation',language:'Language', chart:'Hourly transaction chart', filter:'Filter status', title:'SentinelAI — fraud analytics'},
};
function updateAccessibilityLabels() {
  const labels = accessibilityLabels[document.documentElement.lang] || accessibilityLabels.uz;
  const navs = document.querySelectorAll('.sidebar nav');
  navs[0].setAttribute('aria-label', labels.nav);
  navs[1].setAttribute('aria-label', labels.reviewNav);
  document.querySelector('#language').setAttribute('aria-label', labels.language);
  document.querySelector('#hourly-chart').setAttribute('aria-label', labels.chart);
  document.querySelector('#filter').setAttribute('aria-label', labels.filter);
  document.title = labels.title;
}
new MutationObserver(updateAccessibilityLabels).observe(document.documentElement, {attributes:true, attributeFilter:['lang']});
updateAccessibilityLabels();
