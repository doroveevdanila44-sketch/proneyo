#!/usr/bin/env python3
"""Build portable, data-backed SEO pages and metadata. Python 3 standard library only."""
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import urlsplit
import argparse, hashlib, html, json, re
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
H=html.escape
ARROW='<svg class="icon" aria-hidden="true"><use href="#arrow-up"/></svg>'

def read_json(p):return json.loads(p.read_text())
def dump_json(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def money(x):return f'{x:,}'.replace(',','\u202f')+' ₽'
def replace_main(t,main):return re.sub(r'<main\b.*?</main>',main,t,count=1,flags=re.S)
def text(t):return ' '.join(html.unescape(re.sub('<[^>]+>',' ',t)).split())
def safe_script(x):return json.dumps(x,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')

CATEGORIES=[
 {'key':'face','slug':'kosmetologiya','name':'Косметология','groups':['cosmetology'],'image':'/assets/service-face-square-v2.webp','note':'Чистки, пилинги и уходы','intro':'Чистки, пилинги и уходовые процедуры для лица в студии «Про НЕЁ» на Пейзажной улице. В каталоге есть уходы по типу кожи, гиалуронопластика, ревитализация и фракционная мезотерапия.','ids':['6779049','6780899','6780943','6781001','6781033','6780905'],'faq':[('Есть ли уходы по типу кожи?','В прайсе указаны уходы для сухой и нормальной, комбинированной и жирной, чувствительной кожи, а также уход «Купероз / Розацеа». Конкретный вариант можно обсудить со специалистом при записи.'),('Какие чистки есть в каталоге?','Ультразвуковая, атравматическая, механическая, комбинированная, кислородная, чистка носа и сочетание чистки с пилингом. Все цены и длительность приведены ниже.')]},
 {'key':'massage','slug':'massazh','name':'Массаж','groups':['massage'],'image':'/assets/service-massage-square-v1.webp','note':'Лицо, спина и всё тело','intro':'Массаж лица и тела в Санкт-Петербурге, на Пейзажной улице. Можно выбрать общий оздоровительный массаж или отдельную зону: спину, голову, ноги, лицо, шею и декольте. В каталоге также есть роликовый массаж лица и программа «Перезагрузка. Тело + Энергия».','ids':['22993821','22993786','22993830','6780931','23134721','23206488','22989545','22054082'],'faq':[('Можно ли записаться только на одну зону?','Да. В каталоге есть отдельные варианты для спины, головы и ног, а также массаж лица, шеи и декольте. Длительность конкретного сеанса указана в прайсе.'),('Есть ли абонементы на массаж?','В каталоге есть курсы массажа спины, лица с шейно-воротниковой зоной и головой, антицеллюлитного и роликового массажа лица. Для курсов отдельно указаны стоимость сеанса и полная стоимость курса.')]},
 {'key':'spa','slug':'spa-uhod','name':'SPA-уход','groups':['spa'],'image':'/assets/service-spa-square-v1.webp','note':'LED-маска и гидролат розы','intro':'SPA-уход для лица с LED-маской и гидролатом розы в студии «Про НЕЁ». Это отдельная процедура в актуальном каталоге DIKIDI: 30 минут, стоимость 1 200 ₽.','ids':['22394769'],'faq':[('Какой SPA-уход доступен?','В актуальном каталоге указана одна отдельная SPA-процедура: уход с LED-маской и гидролатом розы.'),('Сколько длится процедура и сколько стоит?','В каталоге студии указаны 30 минут и 1 200 ₽. Доступное время записи открывается в DIKIDI.')]},
 {'key':'body','slug':'korrekciya-figury','name':'Коррекция фигуры','groups':['body'],'image':'/assets/service-body-square-v1.webp','note':'Массаж и аппаратные процедуры','intro':'Уход за телом и аппаратные процедуры в студии «Про НЕЁ» на Пейзажной улице: роликовый массаж, RF-лифтинг тела, кавитация, лазерный липолиз и криолиполиз. В прайсе отдельно показаны разовые процедуры и варианты курсов.','ids':['22050755','22054234','22054272','22054203','22054158'],'faq':[('Можно ли выбрать разовый сеанс?','Да. Для роликового массажа, RF-лифтинга, кавитации и лазерного липолиза есть разовые варианты. Для криолиполиза в каталоге указаны варианты по количеству насадок.'),('Как читать цены на курсы?','У курса полная стоимость указана в названии, а в колонке цены — стоимость одного сеанса в курсе. Эта цена не означает стоимость всего курса.')]},
 {'key':'children','slug':'detskiy-massazh','name':'Детский массаж','groups':['children'],'image':'/assets/service-children-square-v1.webp','note':'Общий массаж и шейно-воротниковая зона','intro':'Детский массаж в студии «Про НЕЁ» в Санкт-Петербурге, на Пейзажной улице. В каталоге есть два варианта: детский массаж на 30 минут и массаж шейно-воротниковой зоны на 20 минут.','ids':['22993900','23723992'],'faq':[('Какие варианты детского массажа доступны?','В записи есть детский массаж длительностью 30 минут и детский массаж шейно-воротниковой зоны длительностью 20 минут.'),('Сколько стоит сеанс?','Оба варианта стоят по 1 200 ₽ согласно актуальному каталогу DIKIDI. Вопросы о возрасте ребёнка и выборе процедуры уточните у специалиста до записи.')]},
 {'key':'details','slug':'depilyaciya-i-pirsing','name':'Депиляция и пирсинг','groups':['depilation','piercing'],'image':'/assets/service-details-square-v1.webp','note':'Депиляция лица и пирсинг ушей','intro':'Восковая депиляция лица и пирсинг ушей в студии «Про НЕЁ». В записи доступны депиляция носа и верхней губы, пирсинг мочки и хряща уха. Ниже — отдельные цены и длительность каждого варианта.','ids':['6792439','6792447','6792061','6792077'],'faq':[('Какие зоны депиляции есть в прайсе?','В текущем каталоге указаны нос и верхняя губа. Стоимость каждой процедуры — 300 ₽, длительность — 15 минут.'),('Какие варианты пирсинга доступны?','Пирсинг мочки уха — 1 500 ₽ и 25 минут; пирсинг хряща уха — 1 500 ₽ и 30 минут. Условия процедуры обсудите со специалистом при записи.')]}]
PRICE_GROUPS=[('cosmetology','Косметология','Чистки, пилинги и уход за кожей'),('massage','Массаж','Для лица и тела · разовые сеансы и курсы'),('children','Детский массаж','Общий массаж и шейно-воротниковая зона'),('spa','SPA','Уход с LED-маской и гидролатом розы'),('body','Коррекция фигуры','Роликовый массаж и аппаратные процедуры'),('depilation','Депиляция','Восковая депиляция лица'),('piercing','Пирсинг','Мочка и хрящ уха'),('other','Консультация и другие услуги','Консультация, тейпирование и варианты записи')]
FACE_CATS=['Чистки','Пилинги','Уходовые процедуры','Гиалуронопластика','Ревитализация','Био/мезо','Фракционная мезотерапия']

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--base-url');ap.add_argument('--root',type=Path,default=ROOT);args=ap.parse_args()
 root=args.root.resolve();d=root/'dist';cfg=read_json(root/'seo.config.json')
 if args.base_url:
  u=urlsplit(args.base_url)
  if u.scheme!='https' or not u.netloc or u.username or u.password or u.query or u.fragment or u.path not in ('','/'):
   raise SystemExit('--base-url must be an HTTPS origin without credentials, path, query or fragment')
  cfg['site_url']=args.base_url.rstrip('/');dump_json(root/'seo.config.json',cfg)
 base=cfg['site_url'].rstrip('/');absurl=lambda p:base+p if p.startswith('/') else p
 catalog=read_json(d/'content/prices.json');items=catalog['items'];byid={x['id']:x for x in items}
 verified=datetime.fromisoformat(catalog['verified_at']).strftime('%d.%m.%Y')
 articles=read_json(d/'content/articles.json');published=[]
 for a in articles:
  if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',a['slug']):raise ValueError('Invalid article slug')
  if a['status']=='published':
   if not a.get('editorial_approved') or not a.get('author',{}).get('name') or not a.get('sections') or not a.get('published_at') or not a.get('updated_at'):
    raise ValueError('Published articles need reviewed content, real author and explicit dates')
   if not any(p.strip() for s in a['sections'] for p in s.get('paragraphs',[])):raise ValueError('Empty published article')
   for key in ['published_at','updated_at']:
    dt=datetime.fromisoformat(a[key].replace('Z','+00:00'))
    if not dt.tzinfo:raise ValueError('Article dates need timezone')
   if datetime.fromisoformat(a['updated_at'].replace('Z','+00:00'))<datetime.fromisoformat(a['published_at'].replace('Z','+00:00')):raise ValueError('Article modified date precedes publication')
   if a.get('image') and (not a.get('image_width') or not a.get('image_height')):raise ValueError('Published article image needs actual width and height')
   published.append(a)
  elif a['status']!='coming_soon':raise ValueError('Unknown article status')
 ptemplate=(d/'prices/index.html').read_text()
 bodyheader=re.search(r'<body[^>]*>(.*?)<main',ptemplate,re.S).group(1)
 footer=re.search(r'<footer class="site-footer container">.*?</footer>',(d/'index.html').read_text(),re.S).group(0)
 def shell(main):return '<!doctype html>\n<html lang="ru"><head></head><body class="inner-page">'+bodyheader+main+footer+'</body></html>\n'
 def book(label='Записаться онлайн'):
  return f'<a class="button" href="{cfg["booking_url"]}" target="_blank" rel="noopener noreferrer">{label} {ARROW}</a>'
 def breadcrumbs(parts):
  return '<nav class="breadcrumbs" aria-label="Хлебные крошки">'+''.join(('<span aria-hidden="true">/</span>' if i else '')+(f'<a href="{p}">{H(n)}</a>' if p else f'<span aria-current="page">{H(n)}</span>') for i,(n,p) in enumerate(parts))+'</nav>'
 def contact(compact=False):
  return f'''<section class="service-location" aria-labelledby="location-title"><h2 id="location-title">Студия на Пейзажной</h2><div class="location-card" itemscope itemtype="https://schema.org/BeautySalon" itemid="{base}/#studio"><h3 itemprop="name">Про НЕЁ</h3><a itemprop="url" class="text-link" href="/">Современная beauty студия</a><div itemprop="address" itemscope itemtype="https://schema.org/PostalAddress"><span itemprop="addressLocality">{cfg['city']}</span>, <span itemprop="streetAddress">{cfg['street']}</span></div><p>{cfg['location_note']}</p><p>Принимаем по предварительной записи.</p><a class="contact-phone" itemprop="telephone" href="tel:{cfg['telephone']}">{cfg['telephone_display']}</a><div class="location-actions">{book()}<a class="text-link" href="{cfg['map_url']}" target="_blank" rel="noopener noreferrer">Студия на Яндекс Картах {ARROW}</a><a class="text-link" href="{cfg['profile_url']}" target="_blank" rel="noopener noreferrer">Студия в DIKIDI {ARROW}</a></div></div></section>'''
 def row(s,anchor=False):
  idattr=f' id="procedure-{s["id"]}"' if anchor else ''
  basis='<small>за сеанс в курсе</small>' if s['price_basis']=='за сеанс в курсе' else ''
  return f'<li class="price-row" data-service-id="{s["id"]}"{idattr}><span class="price-service">{H(s["display_name"])}<small>{s["duration_minutes"]} мин</small></span><span class="price-amount">{money(s["price_rub"])}{basis}</span></li>'
 def studio_schema():
  return {'@type':'BeautySalon','@id':base+'/#studio','name':cfg['name'],'url':base+'/','logo':absurl(cfg['logo']),'image':absurl(cfg['default_image']),'telephone':cfg['telephone'],'description':'Современная бьюти-студия в Санкт-Петербурге. Косметология, массаж для взрослых и детей, SPA-уход, коррекция фигуры, депиляция лица и пирсинг ушей.','address':{'@type':'PostalAddress','streetAddress':cfg['street'],'addressLocality':cfg['city'],'addressCountry':cfg['country']},'hasMap':cfg['map_url'],'sameAs':[cfg['map_url'],cfg['profile_url']]+cfg['social_urls'],'hasOfferCatalog':{'@type':'OfferCatalog','name':'Направления услуг студии','itemListElement':[{'@type':'OfferCatalog','name':c['name'],'url':base+'/services/'+c['slug']+'/'} for c in CATEGORIES]}}
 def offer(s):
  return {'@type':'Offer','@id':base+'/prices/#offer-'+s['id'],'name':s['display_name'],'price':s['price_rub'],'priceCurrency':'RUB','url':cfg['booking_url'],'description':f'{s["duration_minutes"]} мин. '+('Стоимость одного сеанса в курсе; полная стоимость курса указана в названии.' if s['price_basis']=='за сеанс в курсе' else 'Стоимость процедуры.'),'itemOffered':{'@type':'Service','@id':base+'/prices/#procedure-'+s['id'],'name':s['display_name'],'serviceType':s['category'],'provider':{'@id':base+'/#studio'},'areaServed':{'@type':'City','name':cfg['city']}}}
 def category_items(c):return [s for s in items if s['site_group'] in c['groups']]
 def cards(tag='h3',modal=True):
  return '<div class="service-grid">'+''.join(f'''<a class="service-card service-tile" href="/services/{c['slug']}/"{(' data-service="'+c['key']+'" aria-haspopup="dialog" aria-controls="service-dialog"') if modal else ''}><span class="service-image"><img src="{c['image']}" width="1254" height="1254" alt="{H(c['name'])}: иллюстрация направления студии" loading="lazy" decoding="async"></span><div class="service-tile-copy"><{tag} class="service-caption">{c['name']}</{tag}><p class="service-note">{c['note']}</p></div><span class="service-open" aria-hidden="true">{ARROW}</span></a>''' for c in CATEGORIES)+'</div>'
 def article_cards():
  out='<div class="articles-grid">'
  for a in articles:
   ready=a['status']=='published';href='/articles/'+a['slug']+'/'
   title=f'<a href="{href}">{H(a["title"])}</a>' if ready else f'<button type="button" class="article-title-button" data-article="{H(a["title"],quote=True)}" aria-haspopup="dialog" aria-controls="article-soon-dialog">{H(a["title"])}</button>'
   action=f'<a class="text-link" href="{href}">Читать материал →</a>' if ready else f'<button type="button" class="text-link article-soon-button" data-article="{H(a["title"],quote=True)}" aria-haspopup="dialog" aria-controls="article-soon-dialog">Скоро дополним →</button>'
   out+=f'<article class="article-card"><span class="article-category">{"МАТЕРИАЛ СТУДИИ" if ready else "ГОТОВИМ МАТЕРИАЛ"}</span><h3>{title}</h3><p>{H(a["summary"])}</p>{action}</article>'
  return out+'</div>'
 pages={}
 def save_page(path,t,title,desc,crumbs,image=None,index=True,extra=None,business=False,ptype='WebPage'):
  graph=[{'@type':'WebSite','@id':base+'/#website','name':cfg['name'],'url':base+'/','inLanguage':'ru-RU','publisher':{'@id':base+'/#studio'}}, {'@type':ptype,'@id':absurl(path)+'#webpage','url':absurl(path),'name':title,'description':desc,'inLanguage':'ru-RU','isPartOf':{'@id':base+'/#website'},'about':{'@id':base+'/#studio'}}]
  if business:graph.append(studio_schema())
  if len(crumbs)>1:graph.append({'@type':'BreadcrumbList','@id':absurl(path)+'#breadcrumbs','itemListElement':[{'@type':'ListItem','position':i+1,'name':n,'item':absurl(p or path)} for i,(n,p) in enumerate(crumbs)]})
  if extra:graph+=extra
  image=image or cfg.get('social_image',cfg['default_image'])
  social=image==cfg.get('social_image')
  dims=(cfg['social_image_width'],cfg['social_image_height']) if social else (1672,941) if image==cfg['default_image'] else (1254,1254) if image in [c['image'] for c in CATEGORIES] else None
  image_alt=cfg['social_image_alt'] if social else title
  image_type={'.png':'image/png','.jpg':'image/jpeg','.jpeg':'image/jpeg','.webp':'image/webp'}.get(Path(image).suffix.lower())
  dimensions=(f'<meta property="og:image:width" content="{dims[0]}"><meta property="og:image:height" content="{dims[1]}">' if dims else '')
  dimensions+=f'<meta property="og:image:secure_url" content="{absurl(image)}">'
  if image_type:dimensions+=f'<meta property="og:image:type" content="{image_type}">'
  robots='index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1' if index else 'noindex,follow'
  head=f'''<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover"><meta name="theme-color" content="{cfg['theme_color']}"><meta name="color-scheme" content="light"><title>{H(title)}</title><meta name="description" content="{H(desc,quote=True)}"><meta name="robots" content="{robots}"><link rel="canonical" href="{absurl(path)}"><meta property="og:locale" content="ru_RU"><meta property="og:site_name" content="{cfg['name']}"><meta property="og:type" content="{'article' if any(x.get('@type') in ('Article','BlogPosting') for x in (extra or [])) else 'website'}"><meta property="og:title" content="{H(title,quote=True)}"><meta property="og:description" content="{H(desc,quote=True)}"><meta property="og:url" content="{absurl(path)}"><meta property="og:image" content="{absurl(image)}"><meta property="og:image:alt" content="{H(image_alt,quote=True)}">{dimensions}<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{H(title,quote=True)}"><meta name="twitter:description" content="{H(desc,quote=True)}"><meta name="twitter:image" content="{absurl(image)}"><meta name="twitter:image:alt" content="{H(image_alt,quote=True)}"><link rel="icon" type="image/svg+xml" href="/assets/favicon.svg"><link rel="apple-touch-icon" href="/assets/app-icon-192.png"><link rel="manifest" href="/manifest.webmanifest"><link rel="stylesheet" href="/style.css"><script src="/app.js" defer></script><script type="application/ld+json">{safe_script({'@context':'https://schema.org','@graph':graph})}</script>'''
  if path=='/':
   preloads=''.join(f'<link rel="preload" as="image" href="{asset}" fetchpriority="high">' for asset in ['/assets/app-visual.webp','/assets/app-store-light-clean.webp'])
   head=head.replace('<meta charset="UTF-8">','<meta charset="UTF-8">'+preloads,1)
  t=re.sub(r'<head>.*?</head>',lambda m:'<head>\n'+head+'\n</head>',t,count=1,flags=re.S)
  # Current canonical origin is rewritten in visible microdata as well.
  t=re.sub(r'itemid="https://[^\"]+/#studio"',f'itemid="{base}/#studio"',t)
  out=d/('index.html' if path=='/' else path.lstrip('/')+'index.html') if path.endswith('/') else d/path.lstrip('/')
  out.parent.mkdir(parents=True,exist_ok=True);out.write_text(t)
  pages[path]={'file':str(out.relative_to(d)),'title':title,'description':desc,'indexable':index,'image':image,'schema_types':sorted({x['@type'] for x in graph})}
 # Home: keep the established layout, use explicit section semantics and crawlable links.
 t=(d/'index.html').read_text()
 t=t.replace('<body>','<body class="home-page">',1)
 t=re.sub(r'<span class="(?:service-number|review-slot|studio-photo-index)"[^>]*>.*?</span>','',t)
 t=t.replace('<div class="experience-value">17 <small>лет</small></div>','<div class="experience-value">17<span>+</span> <small>лет</small></div>')
 t=re.sub(r'(<h1 id="hero-title">Косметология<br>)\s*',r'\1\n',t)
 t=t.replace('<p class="eyebrow">ЛИЦО · ТЕЛО · ВАШЕ СОСТОЯНИЕ</p><h2 id="services-title">Забота начинается здесь.</h2>','<h2 class="eyebrow service-section-label" id="services-title">Услуги студии</h2><p class="services-display-title">Забота начинается здесь.</p>')
 start=t.index('<div class="service-grid">');end=t.index('<p class="services-additional">',start);t=t[:start]+cards()+t[end:]
 t=re.sub(r'<div class="articles-grid">.*?</div></section>',lambda m:article_cards()+'</section>',t,count=1,flags=re.S)
 # Add a native detail link inside the existing modal while preserving its price and booking actions.
 if 'id="service-page-link"' not in t:t=t.replace('<div class="dialog-actions">','<a class="text-link service-page-link" id="service-page-link" href="/services/">Подробнее о направлении →</a><div class="dialog-actions">',1)
 # Visible contacts carry a second, microdata representation for local search compatibility.
 t=t.replace('<div class="contact-details">','<div class="contact-details" itemscope itemtype="https://schema.org/BeautySalon" itemid="'+base+'/#studio"><p class="contact-studio-name" itemprop="name">Про НЕЁ</p>',1) if 'class="contact-details" itemscope' not in t else t
 t=t.replace('<span class="contact-label">САНКТ-ПЕТЕРБУРГ</span><p>Пейзажная улица, 4, корпус 3</p>','<div itemprop="address" itemscope itemtype="https://schema.org/PostalAddress"><span class="contact-label" itemprop="addressLocality">Санкт-Петербург</span><p itemprop="streetAddress">Пейзажная улица, 4, корпус 3</p></div>')
 t=t.replace('class="contact-phone" href="tel:', 'class="contact-phone" itemprop="telephone" href="tel:')
 # The main services action goes straight to the full price list.
 t=t.replace('href="/services/">Все направления и цены','href="/prices/">Полный прайс-лист',1)
 t=re.sub(r'(id="service-price-link"[^>]*>)[^<]+',r'\1Все услуги и цены ',t)
 save_page('/',t,'Косметология и массаж в Санкт-Петербурге — Про НЕЁ','Косметология, массаж для взрослых и детей, SPA и уход за телом в студии Про НЕЁ. Санкт-Петербург, Пейзажная улица, 4, корпус 3. Цены и запись в DIKIDI.',[('Главная','/')],business=True)
 # Full price list; all 73 provider entries remain visible in static HTML.
 sections=[]
 for gid,name,note in PRICE_GROUPS:
  selected=[s for s in items if s['site_group']==gid]
  if gid=='cosmetology':content=''.join(f'<h3 class="price-subcategory">{cat}</h3><ul>'+''.join(row(s,True) for s in selected if s['category']==cat)+'</ul>' for cat in FACE_CATS)
  else:content='<ul>'+''.join(row(s,True) for s in selected)+'</ul>'
  sections.append(f'<details class="price-group" name="studio-prices" id="{gid}"><summary><h2 class="price-group-heading"><span><span class="price-group-title">{name}</span><small>{note}</small></span><span class="price-group-count"><span class="price-group-toggle" aria-hidden="true">+</span></span></h2></summary><div class="price-group-content">{content}<div class="price-group-end"><span>Конец раздела «{name}»</span><button type="button" class="price-collapse" data-collapse-price>Свернуть {ARROW}</button></div></div></details>')
 main=f'<main class="subpage container" id="services">{breadcrumbs([("Главная","/"),("Услуги","/services/"),("Цены",None)])}<div class="subpage-heading"><p class="eyebrow">УСЛУГИ СТУДИИ</p><h1>Услуги и цены.</h1><p>Косметология, массаж для взрослых и детей, SPA и уход за телом в Санкт-Петербурге.</p></div><nav class="price-tabs" aria-label="Категории услуг">'+''.join(f'<a href="#{i}">{n}</a>' for i,n,_ in PRICE_GROUPS)+'</nav><div class="price-list">'+''.join(sections)+f'</div><div class="price-bottom"><p>Цены и длительность из <a href="{catalog["source"]}" target="_blank" rel="noopener noreferrer">каталога студии в DIKIDI</a>.<br>Сверено {verified}. Для курсов показана цена одного сеанса, полная стоимость — в названии. Итоговую стоимость и условия акции уточняйте при записи.</p>{book("Выбрать время")}</div>{contact()}</main>'
 save_page('/prices/',shell(main),'Цены на косметологию и массаж в Санкт-Петербурге — Про НЕЁ','Прайс студии Про НЕЁ на Пейзажной: косметология, взрослый и детский массаж, SPA, коррекция фигуры, депиляция и пирсинг. Стоимость, длительность и запись.',[('Главная','/'),('Услуги','/services/'),('Цены',None)],business=True,ptype='CollectionPage',extra=[{'@type':'OfferCatalog','@id':base+'/prices/#catalog','name':'Услуги и цены студии Про НЕЁ','itemListElement':[offer(s) for s in items]}])
 # Service index plus six substantial pages with exact offerings, local contacts and visible questions.
 main=f'<main class="subpage container" id="services">{breadcrumbs([("Главная","/"),("Услуги",None)])}<div class="subpage-heading"><p class="eyebrow">ПРО НЕЁ · САНКТ-ПЕТЕРБУРГ</p><h1>Услуги студии.</h1><p>Косметология, массаж, SPA и уход за телом на Пейзажной улице. Выберите направление — внутри полный список процедур, цены и длительность.</p></div>{cards("h2",False)}<p class="services-additional">Консультация, тейпирование и другие варианты записи — в <a class="text-link" href="/prices/#other">полном прайсе</a>.</p>{contact()}</main>'
 save_page('/services/',shell(main),'Услуги косметологии и массажа в Санкт-Петербурге — Про НЕЁ','Шесть направлений студии Про НЕЁ: косметология, массаж, SPA, коррекция фигуры, детский массаж, депиляция и пирсинг. Пейзажная улица, 4, корпус 3.',[('Главная','/'),('Услуги',None)],business=True,ptype='CollectionPage',extra=[{'@type':'ItemList','name':'Направления услуг','itemListElement':[{'@type':'ListItem','position':i+1,'name':c['name'],'url':base+'/services/'+c['slug']+'/'} for i,c in enumerate(CATEGORIES)]}])
 for c in CATEGORIES:
  selected=category_items(c);standalone=[s for s in selected if s['price_basis']!='за сеанс в курсе'];startprice=min(s['price_rub'] for s in standalone)
  path='/services/'+c['slug']+'/'
  group_sections=''
  if c['key']=='face':
   group_sections=''.join(f'<h3 class="price-subcategory">{cat}</h3><ul>'+''.join(row(s) for s in selected if s['category']==cat)+'</ul>' for cat in FACE_CATS)
  else:group_sections='<ul>'+''.join(row(s) for s in selected)+'</ul>'
  faq='<section class="service-questions"><h2>Перед записью</h2>'+''.join(f'<details class="service-question"><summary><h3>{H(q)}</h3></summary><p>{H(a)}</p></details>' for q,a in c['faq'])+'</section>'
  related='<nav class="related-services" aria-label="Другие направления"><h2>Также в студии</h2>'+''.join(f'<a class="text-link" href="/services/{x["slug"]}/">{x["name"]} →</a>' for x in CATEGORIES if x['key']!=c['key'])+'</nav>'
  main=f'''<main class="subpage container service-page" id="services">{breadcrumbs([('Главная','/'),('Услуги','/services/'),(c['name'],None)])}<header class="service-page-hero"><div><p class="eyebrow">ПРО НЕЁ · ПЕЙЗАЖНАЯ УЛИЦА</p><h1>{c['name']}<br><span>в Санкт-Петербурге</span></h1><p class="service-page-lead">{c['intro']}</p><p class="service-start-price">Разовые процедуры от {money(startprice)}</p>{book()}</div><img src="{c['image']}" width="1254" height="1254" alt="{c['name']}: иллюстрация направления студии" fetchpriority="high"></header><section class="service-price-section"><h2>Процедуры и цены</h2><p class="service-price-note">Цены и длительность из актуального каталога DIKIDI, сверены {verified}. Для курсов показана цена одного сеанса, полная стоимость курса — в названии. Условия и доступное время уточняйте при записи.</p><div class="service-price-list">{group_sections}</div><a class="text-link" href="/prices/">Полный прайс студии →</a></section>{faq}{contact()}{related}</main>'''
  service={'@type':'Service','@id':absurl(path)+'#service','name':c['name'],'serviceType':c['name'],'description':c['intro'],'url':absurl(path),'image':absurl(c['image']),'provider':{'@id':base+'/#studio'},'areaServed':{'@type':'City','name':cfg['city']},'hasOfferCatalog':{'@type':'OfferCatalog','name':'Процедуры: '+c['name'],'itemListElement':[offer(s) for s in selected]}}
  save_page(path,shell(main),f'{c["name"]} в Санкт-Петербурге, цены — Про НЕЁ',f'{c["name"]} в студии Про НЕЁ на Пейзажной улице, 4, корпус 3. Разовые процедуры от {money(startprice)}. Полный список, длительность и онлайн-запись в DIKIDI.',[('Главная','/'),('Услуги','/services/'),(c['name'],None)],image=c['image'],business=True,extra=[service])
 # Drafts never become Article markup or sitemap entries; actual publication is explicit and validated.
 dialog='<dialog id="article-soon-dialog" class="dialog" aria-labelledby="article-soon-title"><button class="dialog-close" data-close aria-label="Закрыть">×</button><p class="eyebrow">СТАТЬИ ПРО НЕЁ</p><h2 id="article-soon-title">Статья скоро дополнится.</h2><p class="dialog-description" id="article-soon-subject"></p></dialog>'
 main=f'<main class="subpage container" id="services">{breadcrumbs([("Главная","/"),("Статьи",None)])}<div class="subpage-heading"><p class="eyebrow">НАШИ ЗНАНИЯ — ДЛЯ ВАС</p><h1>Об уходе простыми словами</h1><p class="articles-intro">Делимся знаниями об уходе и процедурах, чтобы вам было проще разобраться и задать свои вопросы.</p></div><section class="article-list"><h2 class="article-list-label">{"Материалы студии" if published else "Готовим материалы"}</h2>{article_cards()}</section></main>'
 save_page('/articles/',shell(main).replace('</body>',dialog+'</body>'),'Об уходе простыми словами — статьи Про НЕЁ','Материалы студии Про НЕЁ об уходе за лицом и телом, косметологии и массаже. Вопросы перед процедурами и понятные объяснения.',[('Главная','/'),('Статьи',None)],index=bool(published),ptype='CollectionPage')
 for a in articles:
  path='/articles/'+a['slug']+'/';ready=a['status']=='published';extra=[]
  content='<div class="article-pending"><h2>Статья скоро дополнится.</h2><p>Мы готовим материал. Загляните сюда чуть позже.</p></div>'
  if ready:
   author=a['author'];content=f'<p class="article-byline">Автор: <a href="{H(author.get("url","/#specialists"),quote=True)}">{H(author["name"])}</a> · <time datetime="{a["published_at"]}">{a["published_at"][:10]}</time></p>'
   content+='<div class="article-content">'+''.join('<section><h2>'+H(s['heading'])+'</h2>'+''.join('<p>'+H(p)+'</p>' for p in s.get('paragraphs',[]))+('<ul>'+''.join('<li>'+H(b)+'</li>' for b in s['bullets'])+'</ul>' if s.get('bullets') else '')+'</section>' for s in a['sections'])+'</div>'
   if a.get('image'):content=f'<img class="article-hero-image" src="{H(a["image"],quote=True)}" width="{int(a["image_width"])}" height="{int(a["image_height"])}" alt="{H(a.get("image_alt",a["title"]),quote=True)}">'+content
   if a.get('sources'):content+='<section class="article-sources"><h2>Источники</h2><ul>'+''.join(f'<li><a href="{H(s["url"],quote=True)}" target="_blank" rel="noopener noreferrer">{H(s["title"])}</a></li>' for s in a['sources'])+'</ul></section>'
   extra=[{'@type':'BlogPosting','@id':absurl(path)+'#article','headline':a['title'],'description':a['summary'],'mainEntityOfPage':{'@id':absurl(path)+'#webpage'},'author':{'@type':'Person','name':author['name'],'url':absurl(author.get('url','/#specialists'))},'publisher':{'@id':base+'/#studio'},'datePublished':a['published_at'],'dateModified':a['updated_at'],'inLanguage':'ru-RU'}]
   if a.get('image'):extra[0]['image']=absurl(a['image'])
  main=f'<main class="subpage container article-page" id="article">{breadcrumbs([("Главная","/"),("Статьи","/articles/"),(a["title"],None)])}<article><div class="subpage-heading"><p class="eyebrow">ПОЛЕЗНО ЗНАТЬ</p><h1>{H(a["title"])}</h1></div>{content}</article></main>'
  save_page(path,shell(main),a['title']+' — Про НЕЁ',a['summary'] if ready else a['title']+'. Статья готовится.',[('Главная','/'),('Статьи','/articles/'),(a['title'],None)],image=a.get('image') or None,index=ready,extra=extra)
 main='<main class="subpage container"><div class="subpage-heading"><p class="eyebrow">ПРО НЕЁ</p><h1>Страница не найдена.</h1><p>Перейдите на главную или выберите нужную услугу.</p></div><div class="location-actions"><a class="button" href="/">На главную</a><a class="text-link" href="/services/">Услуги студии →</a></div></main>'
 save_page('/404.html',shell(main),'Страница не найдена — Про НЕЁ','Страница не найдена. Услуги и запись в студию Про НЕЁ.',[],index=False)
 # Regenerate modal prices from the same catalog, not a second hand-maintained list.
 js=(d/'app.js').read_text();payload={c['key']:{'title':c['name'],'description':c['intro'],'anchor':c['groups'][0],'url':'/services/'+c['slug']+'/','items':[{'name':byid[i]['display_name'],'price':byid[i]['price_rub'],'duration':str(byid[i]['duration_minutes'])+' мин'} for i in c['ids']]} for c in CATEGORIES}
 js=re.sub(r'const services=.*?;\nconst serviceDialog=',lambda m:'const services='+safe_script(payload)+';\nconst serviceDialog=',js,count=1,flags=re.S)
 js=js.replace("document.querySelectorAll('[data-service]').forEach(button=>button.addEventListener('click',()=>{","document.querySelectorAll('[data-service]').forEach(button=>button.addEventListener('click',event=>{\n if(event.metaKey||event.ctrlKey||event.shiftKey||event.altKey||event.button!==0)return;\n event.preventDefault();")
 if "getElementById('service-page-link').href" not in js:js=js.replace("const service=services[button.dataset.service];","const service=services[button.dataset.service];\n document.getElementById('service-page-link').href=service.url;")
 js=js.replace("if(section&&section.matches('details.price-group'))section.open=true;","if(section){const group=section.matches('details.price-group')?section:section.closest('details.price-group');if(group)group.open=true;}")
 (d/'app.js').write_text(js)
 # Stable, content-based modification dates; unchanged rebuilds do not pretend freshness.
 statefile=root/'seo-state.json';state=read_json(statefile) if statefile.exists() else {};today=datetime.now(timezone.utc).date().isoformat();newstate={}
 for path,p in pages.items():
  data=(d/p['file']).read_bytes();fingerprint=hashlib.sha256(data).hexdigest();old=state.get(path,{})
  p['lastmod']=old.get('lastmod',today) if old.get('fingerprint')==fingerprint else today
  newstate[path]={'fingerprint':fingerprint,'lastmod':p['lastmod']}
 dump_json(statefile,newstate)
 ns='http://www.sitemaps.org/schemas/sitemap/0.9';ET.register_namespace('',ns);smap=ET.Element('{'+ns+'}urlset')
 for path,p in pages.items():
  if p['indexable']:
   e=ET.SubElement(smap,'{'+ns+'}url');ET.SubElement(e,'{'+ns+'}loc').text=absurl(path);ET.SubElement(e,'{'+ns+'}lastmod').text=p['lastmod']
 ET.ElementTree(smap).write(d/'sitemap.xml',encoding='UTF-8',xml_declaration=True)
 robots='User-agent: *\nAllow: /\n\nUser-agent: OAI-SearchBot\nAllow: /\n\nSitemap: '+base+'/sitemap.xml\n'
 (d/'robots.txt').write_text(robots)
 dump_json(d/'content/site.json',{'name':cfg['name'],'url':base+'/','city':cfg['city'],'address':cfg['street'],'telephone':cfg['telephone'],'booking_url':cfg['booking_url'],'directions':[{'name':c['name'],'url':base+'/services/'+c['slug']+'/','procedures':len(category_items(c))} for c in CATEGORIES],'prices_source':catalog['source'],'prices_verified_at':catalog['verified_at']})
 # Offline shell is content-versioned automatically; draft article routes are excluded.
 routes=[p for p,v in pages.items() if v['indexable']];assets=sorted(set(re.findall(r'(?:src|href)="(/assets/[^\"#]+)"',''.join((d/v['file']).read_text() for v in pages.values()))))
 shellpaths=routes+['/style.css','/app.js','/manifest.webmanifest']+assets
 cachehash=hashlib.sha256(b''.join((d/(p.strip('/')+'/index.html' if p.endswith('/') and p!='/' else 'index.html' if p=='/' else p.lstrip('/'))).read_bytes() for p in shellpaths)).hexdigest()[:12]
 sw="const CACHE='pro-neyo-"+cachehash+"';\nconst SHELL="+json.dumps(shellpaths,separators=(',',':'))+";\n"+"self.addEventListener('install',e=>{e.waitUntil(caches.open(CACHE).then(c=>c.addAll(SHELL)));self.skipWaiting();});\nself.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim()));});\nself.addEventListener('fetch',e=>{if(e.request.method!=='GET'||new URL(e.request.url).origin!==self.location.origin)return;e.respondWith(fetch(e.request).then(r=>{if(r.ok){const copy=r.clone();caches.open(CACHE).then(c=>c.put(e.request,copy));}return r;}).catch(()=>caches.match(e.request)));});\n"
 (d/'sw.js').write_text(sw)
 dump_json(root/'seo-pages.json',{'site_url':base,'generated_pages':pages,'sitemap_entries':sum(p['indexable'] for p in pages.values()),'published_articles':len(published),'procedure_records':len(items),'cache':cachehash})
 print(json.dumps({'pages':len(pages),'indexable_pages':sum(p['indexable'] for p in pages.values()),'service_pages':len(CATEGORIES),'procedures':len(items),'published_articles':len(published),'cache':cachehash},ensure_ascii=False))

if __name__=='__main__':main()
