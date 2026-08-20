from __future__ import annotations
import hashlib,re
from pathlib import Path
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1]
APPS={
 'lead-value-roi-calculator':{'heading':'Try the interactive tool','preview':'Preview results email','seller':'Request a customized version','buy':'Buy TWE Lead Value & ROI Calculator','url':'https://nanoojr.gumroad.com/l/lfxro'},
 'local-service-quote-calculator':{'heading':'Try the interactive tool','preview':'Preview estimate email','seller':'Request a customized version','buy':'Buy TWE Local Service Quote Calculator','url':'https://nanoojr.gumroad.com/l/bfqgb'},
 'website-audit-scorecard':{'heading':'Try the interactive tool','preview':'Preview scorecard email','seller':'Request a customized version','buy':'Buy TWE Website Audit Scorecard','url':'https://nanoojr.gumroad.com/l/sapzeo'},
}
FILES=['index.html','styles.css','script.js','README.md']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def direct_sections(soup):
 main=soup.find('main')
 if main:return main.find_all('section',recursive=False)
 content=soup.select_one('main.content-grid');return content.find_all('section',recursive=False)
def test_contract():
 publisher=(ROOT/'scripts'/'publish_gigs_to_landing_page.py').read_text(encoding='utf-8');main=publisher.split('def main() -> None:',1)[1].split('if __name__',1)[0];assert 'patch_gig_pages()' not in main
 assert 'assert page.locator(".live-preview-gallery").count() == 0' in publisher
 assert 'assert page.locator("a.purchase-cta").count() == 1' in publisher
 for slug,c in APPS.items():
  source=ROOT/'gigs'/slug;mirror=ROOT/'templates'/'landing-page'/'gigs'/slug
  for name in FILES:assert sha(source/name)==sha(mirror/name),(slug,name)
  html=(source/'index.html').read_text(encoding='utf-8');css=(source/'styles.css').read_text(encoding='utf-8');soup=BeautifulSoup(html,'html.parser')
  assert not soup.select('.live-preview-gallery'),slug
  sections=direct_sections(soup);assert sections
  assert sections[0].find('h2').get_text(' ',strip=True)==c['heading'],slug
  result_i=next(i for i,x in enumerate(sections) if 'result' in x.get('class',[]) or 'result-card' in x.get('class',[]))
  readiness_i=next(i for i,x in enumerate(sections) if 'product-readiness' in x.get('class',[]))
  assert result_i<readiness_i,(slug,result_i,readiness_i)
  assert soup.select_one('#cta').get_text(' ',strip=True)==c['preview']
  assert soup.select_one('.seller-cta').get_text(' ',strip=True)==c['seller']
  buy=[a for a in soup.select('a.purchase-cta') if a.get('href')==c['url'] and a.get_text(' ',strip=True)==c['buy']];assert len(buy)==1,slug
  assert re.search(r'\.product-readiness\s*\{[^}]*color:\s*#f8fafc',css,re.S),slug
  assert re.search(r'\.product-readiness\s*\{[^}]*background:\s*#102a2e',css,re.S),slug
  assert re.search(r'\.scope-note\s*\{[^}]*color:\s*#cbd5e1',css,re.S),slug
  if slug=='local-service-quote-calculator':
   assert '#06b6d4' not in css and '#0ea5e9' not in css and '#0284c7' not in css
   assert 'linear-gradient(135deg, #1e3a8a 0%, #3730a3 52%, #155e75 100%)' in css
   assert re.search(r'\.brand-note\s*\{[^}]*color:\s*#f8fafc',css,re.S)
  if slug=='website-audit-scorecard':
   assert '#0ea5e9' not in css and 'linear-gradient(135deg, #1d4ed8, #0369a1)' in css
 lead=BeautifulSoup((ROOT/'gigs'/'lead-value-roi-calculator'/'index.html').read_text(encoding='utf-8'),'html.parser');assert lead.select_one('#calculate')
 quote=BeautifulSoup((ROOT/'gigs'/'local-service-quote-calculator'/'index.html').read_text(encoding='utf-8'),'html.parser');assert len(quote.select('label > input.addon[type=checkbox]'))==5
 assert quote.select_one('.brand-panel[role="group"][aria-label="Brand and copy settings"]')
 assert quote.select_one('.intake-grid[role="group"][aria-label="Customer and job intake fields"]')
 score=BeautifulSoup((ROOT/'gigs'/'website-audit-scorecard'/'index.html').read_text(encoding='utf-8'),'html.parser');assert len(score.select('input[type=range]'))==10
 assert score.select_one('.context-grid[role="group"][aria-label="Assessment context fields"]')
if __name__=='__main__':test_contract();print('APP_PAGE_CONTRACTS_OK')
