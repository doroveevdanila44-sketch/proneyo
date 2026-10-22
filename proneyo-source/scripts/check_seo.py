#!/usr/bin/env python3
"""Validate generated HTML, links, schemas, indexing rules and provider prices."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import argparse,json,re,xml.etree.ElementTree as ET
from check_static_content import validate_static
class Page(HTMLParser):
 def __init__(self,t):
  super().__init__();self.tags=[];self.titles=[];self.in_title=False;self.title='';self.schemas=[];self.in_ld=False;self.ld='';self.h1=[];self.in_h1=False;self.h='';self.feed(t)
 def handle_starttag(self,t,a):
  a=dict(a);self.tags.append((t,a))
  if t=='title':self.in_title=True;self.title=''
  if t=='h1':self.in_h1=True;self.h=''
  if t=='script' and a.get('type')=='application/ld+json':self.in_ld=True;self.ld=''
 def handle_data(self,t):
  if self.in_title:self.title+=t
  if self.in_h1:self.h+=t
  if self.in_ld:self.ld+=t
 def handle_endtag(self,t):
  if t=='title' and self.in_title:self.titles.append(self.title.strip());self.in_title=False
  if t=='h1' and self.in_h1:self.h1.append(self.h.strip());self.in_h1=False
  if t=='script' and self.in_ld:self.schemas.append(json.loads(self.ld));self.in_ld=False

def validate(root):
 d=root/'dist';manifest=json.loads((root/'seo-pages.json').read_text());base=manifest['site_url'];errors=[];titles=set();descs=set();booking=0;offers=0
 def expect(ok,msg):
  if not ok:errors.append(msg)
 for route,meta in manifest['generated_pages'].items():
  p=d/meta['file'];t=p.read_text();s=Page(t)
  expect(len(s.h1)==1 and bool(s.h1[0]),route+': H1')
  expect(len(s.titles)==1 and bool(s.titles[0]),route+': title')
  expect(s.titles[0] not in titles,route+': duplicate title');titles.add(s.titles[0])
  desc=[a.get('content') for tag,a in s.tags if tag=='meta' and a.get('name')=='description'];expect(len(desc)==1 and desc[0] not in descs,route+': description');descs.update(desc)
  canon=[a.get('href') for tag,a in s.tags if tag=='link' and a.get('rel')=='canonical'];expect(canon==[base+route],route+': canonical')
  robots=[a.get('content','') for tag,a in s.tags if tag=='meta' and a.get('name')=='robots'];expect(len(robots)==1 and ('noindex' not in robots[0])==meta['indexable'],route+': robots')
  expect(any(tag=='meta' and a.get('property')=='og:url' and a.get('content')==base+route for tag,a in s.tags),route+': og:url')
  expect(any(tag=='meta' and a.get('name')=='theme-color' and a.get('content')=='#fbf7f1' for tag,a in s.tags),route+': theme')
  expect(len(s.schemas)==1,route+': schema graph')
  for sc in s.schemas:
   expect(sc.get('@context')=='https://schema.org',route+': context')
   raw=json.dumps(sc,ensure_ascii=False)
   expect('AggregateRating' not in raw and 'FAQPage' not in raw,route+': inappropriate ratings/FAQ schema')
   if route.startswith('/articles/') and not meta['indexable']:expect('BlogPosting' not in raw and '"@type": "Article"' not in raw,route+': draft Article markup')
   for node in sc.get('@graph',[]):
    if node.get('@type')=='OfferCatalog':offers+=len(node.get('itemListElement',[])) if route=='/prices/' else 0
  for tag,a in s.tags:
   if tag=='img':expect('alt' in a and bool(a.get('width')) and bool(a.get('height')),route+': image attributes')
   if tag=='a' and a.get('href','').startswith('https://dikidi.net/ru/record/'):booking+=1
   for key in ['href','src']:
    url=a.get(key,'');u=urlsplit(url)
    if url.startswith('/') and not url.startswith('//'):
     target=d/unquote(u.path).lstrip('/');target=target/'index.html' if not target.suffix else target
     expect(target.exists(),route+': missing '+url)
     if u.fragment and target.exists() and target.suffix=='.html':expect(re.search(r'id=[\"\']'+re.escape(u.fragment)+r'[\"\']',target.read_text()) is not None,route+': bad fragment '+url)
    elif url.startswith('#'):expect(re.search(r'id=[\"\']'+re.escape(url[1:])+r'[\"\']',t) is not None,route+': missing fragment '+url)
   if tag=='a' and a.get('data-service'):expect(a.get('href','').startswith('/services/'),route+': non-crawlable service')
  expect(not re.search(r'class="(?:service-number|review-slot|studio-photo-index)"',t),route+': decorative numbering')
 smap=ET.parse(d/'sitemap.xml');urls=[x.text for x in smap.findall('.//{*}loc')];expected=[base+r for r,p in manifest['generated_pages'].items() if p['indexable']]
 expect(set(urls)==set(expected) and len(urls)==len(set(urls)),'sitemap coverage')
 expect('Sitemap: '+base+'/sitemap.xml' in (d/'robots.txt').read_text(),'robots sitemap')
 expect('User-agent: OAI-SearchBot\nAllow: /' in (d/'robots.txt').read_text(),'search crawler rule')
 raw=json.loads((d/'content/prices.json').read_text());t=(d/'prices/index.html').read_text();ids=re.findall(r'data-service-id="(\d+)"',t)
 expect(len(ids)==len(set(ids))==73 and set(ids)=={i['id'] for i in raw['items']},'73 price rows')
 data=Page(t).schemas[0];catalog=next(n for n in data['@graph'] if n['@type']=='OfferCatalog');mapped={o['@id'].rsplit('-',1)[1]:o for o in catalog['itemListElement']}
 for i in raw['items']:expect(mapped[i['id']]['price']==i['price_rub'] and mapped[i['id']]['priceCurrency']=='RUB','price mismatch '+i['id'])
 main=(d/'index.html').read_text();expect('17<span>+</span> <small>лет</small>' in main,'17+ years');expect(main.count('class="service-card service-tile"')==6,'six service cards')
 static=validate_static(root);errors.extend(static['errors'])
 result={'passed':not errors,'pages_checked':len(manifest['generated_pages']),'indexable_pages':len(urls),'procedure_rows':len(ids),'price_offers':len(mapped),'service_pages':6,'booking_links':booking,'published_articles':manifest['published_articles'],'static_html':static,'errors':errors}
 return result
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);ap.add_argument('--json-output',type=Path);args=ap.parse_args();result=validate(args.root)
 if args.json_output:args.json_output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(result,ensure_ascii=False));raise SystemExit(0 if result['passed'] else 1)
