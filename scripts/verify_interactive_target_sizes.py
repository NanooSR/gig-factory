from __future__ import annotations
import http.server,json,socketserver,threading
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];LANDING=ROOT/'templates'/'landing-page';OUT=ROOT/'runtime'/'interactive_target_sizes.json'
ROUTES=['/','/gigs/lead-value-roi-calculator/','/gigs/local-service-quote-calculator/','/gigs/website-audit-scorecard/'];WIDTHS=[320,390,1440];ZOOMS=[1,2]
ACTIONABLE='a[href],button,input:not([type="hidden"]),select,textarea,[role="button"],[tabindex]:not([tabindex="-1"])'
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass

def main():
 handler=lambda *a,**k:Handler(*a,directory=str(LANDING),**k)
 with socketserver.TCPServer(('127.0.0.1',0),handler) as srv:
  threading.Thread(target=srv.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{srv.server_address[1]}';rows=[]
  with sync_playwright() as p:
   browser=p.chromium.launch(headless=True)
   for width in WIDTHS:
    page=browser.new_page(viewport={'width':width,'height':1000})
    for route in ROUTES:
     page.goto(base+route,wait_until='networkidle')
     for zoom in ZOOMS:
      page.evaluate('(z)=>document.documentElement.style.zoom=String(z)',zoom)
      failures=page.locator(ACTIONABLE).evaluate_all("""els=>els.filter(e=>{const s=getComputedStyle(e),r=e.getBoundingClientRect();return s.display!=='none'&&s.visibility!=='hidden'&&s.opacity!=='0'&&r.width>0&&r.height>0}).map(e=>{const r=e.getBoundingClientRect();let effective={width:r.width,height:r.height,source:'direct'};if(e.type==='checkbox'||e.type==='radio'){const l=(e.id&&document.querySelector(`label[for="${CSS.escape(e.id)}"]`))||e.closest('label');if(l){const lr=l.getBoundingClientRect();effective={width:lr.width,height:lr.height,source:'associated-label'}}}return {tag:e.tagName.toLowerCase(),id:e.id||'',type:e.type||'',classes:e.className||'',text:(e.innerText||e.value||e.getAttribute('aria-label')||'').trim().slice(0,100),width:+r.width.toFixed(2),height:+r.height.toFixed(2),effective_width:+effective.width.toFixed(2),effective_height:+effective.height.toFixed(2),measurement:effective.source}}).filter(x=>x.effective_width<44||x.effective_height<44)""")
      rows.append({'route':route,'width':width,'zoom':zoom,'failures':failures})
     page.evaluate("document.documentElement.style.zoom='1'")
    page.close()
   browser.close();srv.shutdown()
 OUT.parent.mkdir(exist_ok=True);OUT.write_text(json.dumps({'ok':all(not r['failures'] for r in rows),'rows':rows},indent=2),encoding='utf-8')
 failures=[r for r in rows if r['failures']]
 if failures:raise AssertionError(json.dumps(failures,indent=2))
 print(f'INTERACTIVE_TARGET_SIZES_OK {OUT}')
if __name__=='__main__':main()
