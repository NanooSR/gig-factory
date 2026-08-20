from __future__ import annotations
import http.server,json,socketserver,threading
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];LANDING=ROOT/'templates'/'landing-page';OUT=ROOT/'runtime'/'quote_invalid_state_accessibility.json'
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass

def snapshot(page,state):
 return {'state':state,'active_id':page.evaluate('document.activeElement && document.activeElement.id'),'message':page.locator('#client-message').inner_text(),'message_role':page.locator('#client-message').get_attribute('role'),'message_live':page.locator('#client-message').get_attribute('aria-live'),'breakdown_hidden':page.locator('#breakdown').evaluate('e=>e.classList.contains("hidden")'),'invalid':{x:page.locator('#'+x).get_attribute('aria-invalid') for x in ['hours','hourly-rate','materials']}}
def main():
 handler=lambda *a,**k:Handler(*a,directory=str(LANDING),**k)
 with socketserver.TCPServer(('127.0.0.1',0),handler) as srv:
  threading.Thread(target=srv.serve_forever,daemon=True).start();url=f'http://127.0.0.1:{srv.server_address[1]}/gigs/local-service-quote-calculator/';rows=[]
  with sync_playwright() as p:
   browser=p.chromium.launch(headless=True);page=browser.new_page(viewport={'width':390,'height':900});page.goto(url,wait_until='networkidle')
   page.locator('#hours').fill('0');page.locator('#calculate').click();bad=snapshot(page,'invalid');rows.append(bad)
   assert bad['invalid']['hours']=='true' and bad['active_id']=='hours' and (bad['message_role']=='alert' or bad['message_live']=='assertive') and bad['breakdown_hidden']
   page.locator('#hours').fill('4');page.locator('#calculate').click();fixed=snapshot(page,'corrected');rows.append(fixed)
   assert all(v is None for v in fixed['invalid'].values()) and not fixed['breakdown_hidden'] and fixed['message_role']!='alert'
   page.locator('#hours').fill('0');page.locator('#calculate').click();page.locator('#reset-sample').click();reset=snapshot(page,'reset');rows.append(reset)
   assert all(v is None for v in reset['invalid'].values()) and not reset['breakdown_hidden'] and reset['message_role']!='alert'
   browser.close();srv.shutdown()
 OUT.parent.mkdir(exist_ok=True);OUT.write_text(json.dumps({'ok':True,'rows':rows},indent=2),encoding='utf-8');print(f'QUOTE_INVALID_STATE_ACCESSIBILITY_OK {OUT}')
if __name__=='__main__':main()
