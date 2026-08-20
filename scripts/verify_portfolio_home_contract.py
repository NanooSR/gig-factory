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
 assert soup.h1 and soup.h1.get_text(' ',strip=True)==H1
 assert soup.select_one('.brand') and soup.select_one('.brand').get_text(' ',strip=True)==BRAND
 tie=soup.select_one('.product-bridge');assert tie and 'three TWE products on Gumroad' in tie.get_text(' ',strip=True)
 cards=soup.select('.gig-card');assert len(cards)==3
 for card,(title,url) in zip(cards,PRODUCTS.items()):
  assert card.select_one('h3').get_text(' ',strip=True)==title
  links=[a for a in card.select('a') if a.get('href')==url and a.get_text(' ',strip=True)=='View product on Gumroad']
  assert len(links)==1,(title,url)
 assert not any(a.get('href')=='https://github.com/NanooSR/gig-factory' for a in soup.select('.hero-actions a'))
 tech=soup.select_one('section.technical-details');assert tech
 github=tech.find('a',href='https://github.com/NanooSR/gig-factory');assert github and github.get_text(' ',strip=True)=='Technical source (GitHub)'
 for token in [H1,BRAND,*PRODUCTS.values(),'product-bridge','technical-details','Technical source (GitHub)']:
  assert token in gen,f'generator missing {token}'
 assert 'h1 { font-size: clamp(2.5rem, 4.5vw, 3.5rem); line-height: 1.05; max-width: 18ch; }' in css
 assert 'h1 { max-width: 14ch; margin-block: 0.6rem 1rem; }' in css
def assert_mobile_geometry():
 class Handler(http.server.SimpleHTTPRequestHandler):
  def log_message(self,*args):pass
 class Server(socketserver.TCPServer):allow_reuse_address=True
 old=os.getcwd();os.chdir(LANDING);srv=Server(('127.0.0.1',0),Handler);threading.Thread(target=srv.serve_forever,daemon=True).start()
 try:
  with sync_playwright() as p:
   b=p.chromium.launch(headless=True)
   desktop=b.new_page(viewport={'width':1440,'height':1000});desktop.goto(f'http://127.0.0.1:{srv.server_address[1]}/',wait_until='networkidle');assert desktop.locator('h1').bounding_box()['height']<=360;desktop.close()
   pg=b.new_page(viewport={'width':390,'height':844});pg.goto(f'http://127.0.0.1:{srv.server_address[1]}/',wait_until='networkidle');first=pg.locator('.gig-card').first.bounding_box();assert first and first['y']<=1266,first;assert pg.evaluate('document.documentElement.scrollWidth <= document.documentElement.clientWidth + 2');h1=pg.locator('h1');assert h1.bounding_box()['width']<=320;assert float(h1.evaluate("e=>getComputedStyle(e).maxWidth").removesuffix('px'))<=320;b.close()
 finally:srv.shutdown();srv.server_close();os.chdir(old)
def main():assert_source_contract();assert_mobile_geometry();print('PORTFOLIO_HOME_CONTRACT_OK')
if __name__=='__main__':main()
