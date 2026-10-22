#!/usr/bin/env python3
"""Exercise portability and article publication in disposable copies."""
import hashlib,json,re,shutil,subprocess,tempfile,unittest
from pathlib import Path
from check_static_content import validate_static
ROOT=Path(__file__).resolve().parents[1]
def build(root,*args):
 return subprocess.run(['python',str(ROOT/'scripts/prepare_seo.py'),'--root',str(root),*args],capture_output=True,text=True)
def hashes(root):
 return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (root/'dist').rglob('*') if p.is_file()}
class Pipeline(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
  shutil.copytree(ROOT/'dist',self.root/'dist')
  for name in ['seo.config.json','seo-state.json']:shutil.copy2(ROOT/name,self.root/name)
 def tearDown(self):self.tmp.cleanup()
 def test_unchanged_rebuild_is_stable(self):
  self.assertEqual(build(self.root).returncode,0);before=hashes(self.root)
  state=(self.root/'seo-state.json').read_bytes()
  self.assertEqual(build(self.root).returncode,0)
  self.assertEqual(hashes(self.root),before);self.assertEqual((self.root/'seo-state.json').read_bytes(),state)
 def test_domain_rebase(self):
  old=json.loads((self.root/'seo.config.json').read_text())['site_url']
  r=build(self.root,'--base-url','https://example.test');self.assertEqual(r.returncode,0,r.stderr)
  for p in (self.root/'dist').rglob('*'):
   if p.suffix in ['.html','.xml','.txt','.json']:self.assertNotIn(old,p.read_text(),str(p))
  self.assertIn('https://example.test/sitemap.xml',(self.root/'dist/robots.txt').read_text())
 def test_static_prices_cannot_move_into_template(self):
  self.assertEqual(build(self.root).returncode,0)
  p=self.root/'dist/prices/index.html';t=p.read_text()
  t=re.sub(r'(<li class="price-row"[^>]*>.*?</li>)',r'<template>\1</template>',t,count=1)
  p.write_text(t)
  result=validate_static(self.root)
  self.assertFalse(result['passed']);self.assertTrue(any('incomplete static price rows' in e for e in result['errors']))
 def test_json_ld_does_not_replace_visible_price_names(self):
  self.assertEqual(build(self.root).returncode,0)
  p=self.root/'dist/prices/index.html';t=p.read_text()
  t=re.sub(r'(<li class="price-row"[^>]*><span class="price-service">).*?(<small>)',r'\1<script type="application/json">"Уход"</script>\2',t,count=1)
  p.write_text(t)
  self.assertFalse(validate_static(self.root)['passed'])
 def test_unreviewed_article_rejected(self):
  p=self.root/'dist/content/articles.json';a=json.loads(p.read_text());a[0]['status']='published';p.write_text(json.dumps(a))
  r=build(self.root);self.assertNotEqual(r.returncode,0);self.assertIn('reviewed content',r.stderr)
 def test_reviewed_article_publishes_visible_text_schema_and_links(self):
  p=self.root/'dist/content/articles.json';a=json.loads(p.read_text());a[0].update(status='published',editorial_approved=True,author={'name':'Тестовый автор','url':'/#specialists'},published_at='2026-10-22T12:00:00+03:00',updated_at='2026-10-22T12:00:00+03:00',sections=[{'heading':'Тест раздела','paragraphs':['Проверка текста <важно> и кавычек «да».']}]);p.write_text(json.dumps(a,ensure_ascii=False))
  r=build(self.root);self.assertEqual(r.returncode,0,r.stderr)
  page=(self.root/'dist/articles'/a[0]['slug']/'index.html').read_text()
  self.assertIn('Проверка текста &lt;важно&gt;',page);self.assertIn('BlogPosting',page);self.assertNotIn('Статья скоро дополнится.',page)
  self.assertIn('/articles/'+a[0]['slug']+'/',(self.root/'dist/sitemap.xml').read_text())
  self.assertIn('Читать материал',(self.root/'dist/articles/index.html').read_text())
  self.assertEqual(json.loads((self.root/'seo-pages.json').read_text())['sitemap_entries'],11)
  self.assertTrue(validate_static(self.root)['passed'])
 def test_reversed_dates_rejected_across_timezones(self):
  p=self.root/'dist/content/articles.json';a=json.loads(p.read_text());a[0].update(status='published',editorial_approved=True,author={'name':'Тест'},published_at='2026-10-22T12:00:00+03:00',updated_at='2026-10-22T12:30:00+05:00',sections=[{'heading':'Тест','paragraphs':['Текст']}]);p.write_text(json.dumps(a))
  r=build(self.root);self.assertNotEqual(r.returncode,0);self.assertIn('precedes publication',r.stderr)
if __name__=='__main__':unittest.main(verbosity=2)
