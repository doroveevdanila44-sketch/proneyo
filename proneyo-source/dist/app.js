'use strict';
const menuButton=document.querySelector('.menu-toggle');
const mobileNav=document.getElementById('mobile-nav');
const headerBrand=document.querySelector('.site-header .brand');
function syncBrandPlate(){if(!headerBrand)return;const r=headerBrand.getBoundingClientRect();headerBrand.dataset.brandSide=(r.left+r.width/2<document.documentElement.clientWidth/2)?'left':'right';}
syncBrandPlate();window.addEventListener('resize',syncBrandPlate,{passive:true});
function closeMenu(){menuButton.setAttribute('aria-expanded','false');menuButton.setAttribute('aria-label','Открыть меню');document.body.classList.remove('menu-open');mobileNav.inert=true;}
menuButton.addEventListener('click',()=>{const opened=menuButton.getAttribute('aria-expanded')==='true';menuButton.setAttribute('aria-expanded',String(!opened));menuButton.setAttribute('aria-label',opened?'Открыть меню':'Закрыть меню');document.body.classList.toggle('menu-open',!opened);mobileNav.inert=opened;});
mobileNav.querySelectorAll('a').forEach(a=>a.addEventListener('click',closeMenu));
document.addEventListener('keydown',e=>{if(e.key==='Escape')closeMenu();});
window.matchMedia('(min-width:1025px)').addEventListener('change',e=>{if(e.matches)closeMenu();});
document.querySelectorAll('[data-close]').forEach(button=>button.addEventListener('click',()=>button.closest('dialog').close()));
document.querySelectorAll('dialog').forEach(dialog=>dialog.addEventListener('click',e=>{if(e.target===dialog){const r=dialog.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)dialog.close();}}));
const services={"face":{"title":"Косметология","description":"Чистки, пилинги и уходовые процедуры для лица в студии «Про НЕЁ» на Пейзажной улице. В каталоге есть уходы по типу кожи, гиалуронопластика, ревитализация и фракционная мезотерапия.","anchor":"cosmetology","url":"/services/kosmetologiya/","items":[{"name":"Ультразвуковая чистка","price":2100,"duration":"50 мин"},{"name":"Комбинированная чистка","price":2500,"duration":"60 мин"},{"name":"Пилинг Молочный","price":2000,"duration":"25 мин"},{"name":"Антивозрастной уход","price":5000,"duration":"45 мин"},{"name":"Экспресс-уход \"Вспышка красоты\" (G-Derm)","price":2100,"duration":"35 мин"},{"name":"Фракционная мезотерапия","price":2300,"duration":"40 мин"}]},"massage":{"title":"Массаж","description":"Массаж лица и тела в Санкт-Петербурге, на Пейзажной улице. Можно выбрать общий оздоровительный массаж или отдельную зону: спину, голову, ноги, лицо, шею и декольте. В каталоге также есть роликовый массаж лица и программа «Перезагрузка. Тело + Энергия».","anchor":"massage","url":"/services/massazh/","items":[{"name":"Общий оздоровительный массаж тела + голова + лицо","price":2500,"duration":"60 мин"},{"name":"Массаж спины","price":1350,"duration":"30 мин"},{"name":"Массаж лица + шейно-воротниковая зона + голова","price":1400,"duration":"40 мин"},{"name":"Массаж лица шеи и зоны декольте","price":1700,"duration":"30 мин"},{"name":"Массаж ног","price":1350,"duration":"30 мин"},{"name":"Перезагрузка. Тело + Энергия","price":3500,"duration":"120 мин"},{"name":"Биоэнергетический массаж (бесконтактный) · акция","price":1500,"duration":"60 мин"},{"name":"Роликовый массаж лица","price":1500,"duration":"30 мин"}]},"spa":{"title":"SPA-уход","description":"SPA-уход для лица с LED-маской и гидролатом розы в студии «Про НЕЁ». Это отдельная процедура в актуальном каталоге DIKIDI: 30 минут, стоимость 1 200 ₽.","anchor":"spa","url":"/services/spa-uhod/","items":[{"name":"SPA-уход с LED-маской и гидролатом розы","price":1200,"duration":"30 мин"}]},"body":{"title":"Коррекция фигуры","description":"Уход за телом и аппаратные процедуры в студии «Про НЕЁ» на Пейзажной улице: роликовый массаж, RF-лифтинг тела, кавитация, лазерный липолиз и криолиполиз. В прайсе отдельно показаны разовые процедуры и варианты курсов.","anchor":"body","url":"/services/korrekciya-figury/","items":[{"name":"Роликовый массаж · 1 процедура","price":2200,"duration":"60 мин"},{"name":"RF-лифтинг тела · 1 зона, 1 сеанс","price":1600,"duration":"30 мин"},{"name":"Кавитация · 1 зона, 1 сеанс","price":1400,"duration":"30 мин"},{"name":"Лазерный липолиз · 1 процедура","price":1200,"duration":"40 мин"},{"name":"Криолиполиз 1 насадка за один сеанс","price":3000,"duration":"40 мин"}]},"children":{"title":"Детский массаж","description":"Детский массаж в студии «Про НЕЁ» в Санкт-Петербурге, на Пейзажной улице. В каталоге есть два варианта: детский массаж на 30 минут и массаж шейно-воротниковой зоны на 20 минут.","anchor":"children","url":"/services/detskiy-massazh/","items":[{"name":"Детский массаж","price":1200,"duration":"30 мин"},{"name":"Детский массаж шейно-воротниковой зоны","price":1200,"duration":"20 мин"}]},"details":{"title":"Депиляция и пирсинг","description":"Восковая депиляция лица и пирсинг ушей в студии «Про НЕЁ». В записи доступны депиляция носа и верхней губы, пирсинг мочки и хряща уха. Ниже — отдельные цены и длительность каждого варианта.","anchor":"depilation","url":"/services/depilyaciya-i-pirsing/","items":[{"name":"Восковая депиляция носа","price":300,"duration":"15 мин"},{"name":"Восковая депиляция верхней губы","price":300,"duration":"15 мин"},{"name":"Пирсинг мочки уха","price":1500,"duration":"25 мин"},{"name":"Пирсинг хряща уха","price":1500,"duration":"30 мин"}]}};
const serviceDialog=document.getElementById('service-dialog');
document.querySelectorAll('[data-service]').forEach(button=>button.addEventListener('click',event=>{
 if(event.metaKey||event.ctrlKey||event.shiftKey||event.altKey||event.button!==0)return;
 event.preventDefault();
 const service=services[button.dataset.service];
 document.getElementById('service-page-link').href=service.url;
 document.getElementById('service-title').textContent=service.title;
 document.getElementById('service-description').textContent=service.description;
 document.getElementById('service-price-link').href='/prices/#'+service.anchor;
 document.getElementById('service-details').replaceChildren(...service.items.map(item=>{
  const li=document.createElement('li');
  const name=document.createElement('span');name.textContent=item.name;
  const meta=document.createElement('span');meta.className='service-detail-meta';
  const price=document.createElement('strong');price.textContent=new Intl.NumberFormat('ru-RU').format(item.price)+' ₽';
  const duration=document.createElement('small');duration.textContent=item.duration;
  meta.append(price,duration);li.append(name,meta);return li;
 }));
 serviceDialog.showModal();
}));
const priceGroups=[...document.querySelectorAll('details.price-group')];
function openPriceGroup(group){
 priceGroups.forEach(other=>{if(other!==group)other.open=false;});
 group.open=true;
}
priceGroups.forEach(group=>group.addEventListener('toggle',()=>{
 if(group.open)priceGroups.forEach(other=>{if(other!==group)other.open=false;});
}));
function revealPriceGroup(){
 const id=decodeURIComponent(location.hash.slice(1));
 const section=id&&document.getElementById(id);
 if(section){const group=section.matches('details.price-group')?section:section.closest('details.price-group');if(group)openPriceGroup(group);}
}
revealPriceGroup();window.addEventListener('hashchange',revealPriceGroup);
window.addEventListener('pageshow',()=>{
 priceGroups.forEach(group=>{group.open=false;});
 revealPriceGroup();
});
document.querySelectorAll('.price-tabs a').forEach(link=>link.addEventListener('click',()=>{
 const group=document.getElementById(decodeURIComponent(link.hash.slice(1)));
 if(group)openPriceGroup(group);
}));
document.querySelectorAll('[data-collapse-price]').forEach(button=>button.addEventListener('click',()=>{
 const group=button.closest('details');group.open=false;
 group.querySelector('summary').focus({preventScroll:true});
 group.scrollIntoView({block:'start',behavior:'instant'});
}));
const articleSoon=document.getElementById('article-soon-dialog');
document.querySelectorAll('[data-article]').forEach(button=>button.addEventListener('click',()=>{document.querySelectorAll('dialog[open]').forEach(dialog=>dialog.close());document.getElementById('article-soon-subject').textContent=button.dataset.article;articleSoon.showModal();}));
const downloadDialog=document.getElementById('download-dialog');
document.querySelectorAll('[data-download]').forEach(link=>link.addEventListener('click',e=>{if(e.metaKey||e.ctrlKey||e.shiftKey||e.altKey||e.button!==0)return;e.preventDefault();document.querySelectorAll('dialog[open]').forEach(dialog=>dialog.close());downloadDialog.showModal();}));
if('serviceWorker'in navigator){window.addEventListener('load',()=>{navigator.serviceWorker.register('/sw.js').catch(()=>{});});}
