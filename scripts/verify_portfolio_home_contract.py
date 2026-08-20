from __future__ import annotations
import http.server,os,socketserver,threading
from pathlib import Path
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];LANDING=ROOT/'templates'/'landing-page';HTML=LANDING/'index.html';CSS=LANDING/'styles.css';GEN=ROOT/'scripts'/'publish_gigs_to_landing_page.py'
H1='Interactive calculators and scorecards, ready for your brand and approved business rules.'
BRAND='The Watchers Edge — Interactive Tools'
PRODUCTS={
 'Lead Value & ROI Calculator':'https://nanoojr.gumroad.com/l/lfxro',
 'Custom Service Estimate & Intake Calculator':'https://nanoojr.gumroad.com/l/bfqgb',
 'Website Audit Scorecard':'https://nanoojr.gumroad.com/l/sapzeo',
}
def assert_source_contract():
 html=HTML.read_text(encoding='utf-8');css=CSS.read_text(encoding='utf-8');gen=GEN.read_text(encoding='utf-8');soup=BeautifulSoup(html,'html.parser')
 meta=soup.find('meta',attrs={'name':'description'});assert meta and len(meta.get('content',''))>=80
 icon=soup.find('link',rel=lambda value:value and 'icon' in value);assert icon and (LANDING/icon['href']).is_file()
 assert soup.h1 and soup.h1.get_text(' ',strip=True)==H1
 assert soup.select_one('.brand') and soup.select_one('.brand').get_text(' ',strip=True)==BRAND
 tie=soup.select_one('.product-bridge');assert tie and 'three TWE products on Gumroad' in tie.get_text(' ',strip=True)
 cards=soup.select('.gig-card');assert len(cards)==3
 sources=soup.select('.gig-card picture source[type="image/webp"]');assert len(sources)==3
 webp_paths=[LANDING/src['srcset'] for src in sources];assert all(p.is_file() for p in webp_paths);assert sum(p.stat().st_size for p in webp_paths)<=900_000
 for img in soup.select('.gig-card picture img'):
  assert img.get('loading')=='lazy' and img.get('decoding')=='async' and img.get('width') and img.get('height')
 for card,(title,url) in zip(cards,PRODUCTS.items()):
  assert card.select_one('h2').get_text(' ',strip=True)==title
  links=[a for a in card.select('a') if a.get('href')==url and a.get_text(' ',strip=True)=='View product on Gumroad']
  assert len(links)==1,(title,url)
 assert not any(a.get('href')=='https://github.com/NanooSR/gig-factory' for a in soup.select('.hero-actions a'))
 tech=soup.select_one('section.technical-details');assert tech
 github=tech.find('a',href='https://github.com/NanooSR/gig-factory');assert github and github.get_text(' ',strip=True)=='Technical source (GitHub)'
 for token in [H1,BRAND,*PRODUCTS.values(),'product-bridge','technical-details','Technical source (GitHub)']:
  assert token in gen,f'generator missing {token}'
 assert 'h1 { font-size: clamp(2.5rem, 4.5vw, 3.5rem); line-height: 1.05; max-width: 18ch; }' in css
 assert 'h1 { max-width: 14ch; margin-block: 0.6rem 1rem; }' in css
 assert 'aspect-ratio: 16 / 10' in css and 'object-fit: cover' in css and 'object-position: top' in css
 assert '<picture>' in gen and 'type="image/webp"' in gen
 assert '<meta name="description"' in gen and '<link rel="icon"' in gen and '<h2>{gig[\'title\']}</h2>' in gen
def assert_mobile_geometry():
 class Handler(http.server.SimpleHTTPRequestHandler):
  def log_message(self,*args):pass
 class Server(socketserver.TCPServer):allow_reuse_address=True
 old=os.getcwd();os.chdir(LANDING);srv=Server(('127.0.0.1',0),Handler);threading.Thread(target=srv.serve_forever,daemon=True).start()
 try:
  with sync_playwright() as p:
   b=p.chromium.launch(headless=True)
   desktop=b.new_page(viewport={'width':1440,'height':1000});desktop.goto(f'http://127.0.0.1:{srv.server_address[1]}/',wait_until='networkidle');assert desktop.locator('h1').bounding_box()['height']<=360;desktop.close()
   pg=b.new_page(viewport={'width':390,'height':844});pg.goto(f'http://127.0.0.1:{srv.server_address[1]}/',wait_until='networkidle');first=pg.locator('.gig-card').first.bounding_box();assert first and first['y']<=1266,first;assert pg.evaluate('document.documentElement.scrollWidth <= document.documentElement.clientWidth + 2');h1=pg.locator('h1');assert h1.bounding_box()['width']<=320;assert float(h1.evaluate("e=>getComputedStyle(e).maxWidth").removesuffix('px'))<=320;boxes=pg.locator('.screenshot-link picture').evaluate_all('els=>els.map(e=>{const r=e.getBoundingClientRect();return [r.width,r.height]})');assert len(boxes)==3 and all(abs(w/h-1.6)<0.03 for w,h in boxes),boxes;b.close()
 finally:srv.shutdown();srv.server_close();os.chdir(old)
def main():assert_source_contract();assert_mobile_geometry();print('PORTFOLIO_HOME_CONTRACT_OK')
if __name__=='__main__':main()
