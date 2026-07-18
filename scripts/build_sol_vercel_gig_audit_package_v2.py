from __future__ import annotations

import hashlib, json, shutil, subprocess, zipfile, threading, http.server, socketserver, os
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen, Request
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
RUN_ID=datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_UTC')
OUT=ROOT/'runtime'/f'sol_vercel_gig_audit_v2_{RUN_ID}'
RAW=OUT/'raw_evidence'; PUBLIC=RAW/'public_live'; SOURCE=RAW/'source_files'; SCREEN=RAW/'screenshots'; SUMMARY=OUT/'summaries'
BASE='https://gig-factory-navy.vercel.app'
SLUGS=['lead-value-roi-calculator','local-service-quote-calculator','website-audit-scorecard']
ROUTES=[{'slug':'home','url':BASE+'/'},* [{'slug':s,'url':f'{BASE}/gigs/{s}/'} for s in SLUGS]]

SUPPORT=['README.md','.hermes.md','docs/profit-shortlist.md','docs/sales-listings.md','docs/sell-next-steps.md','docs/continuity/latest-handoff.md','templates/landing-page/index.html','templates/landing-page/styles.css','templates/landing-page/script.js','scripts/publish_gigs_to_landing_page.py','scripts/build_sol_vercel_gig_audit_package.py','scripts/build_sol_vercel_gig_audit_package_v2.py']
for s in SLUGS:
    SUPPORT += [f'gigs/{s}/index.html',f'gigs/{s}/styles.css',f'gigs/{s}/script.js',f'gigs/{s}/README.md',f'templates/landing-page/gigs/{s}/index.html',f'templates/landing-page/gigs/{s}/styles.css',f'templates/landing-page/gigs/{s}/script.js',f'templates/landing-page/assets/screenshots/gigs/{s}-desktop-output.png',f'templates/landing-page/assets/screenshots/gigs/{s}-mobile-output.png']


def sha(p):
    h=hashlib.sha256();
    with open(p,'rb') as f:
        for c in iter(lambda:f.read(1048576),b''): h.update(c)
    return h.hexdigest()

def write_json(p,d): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(d,indent=2,ensure_ascii=False),encoding='utf-8')
def run(cmd):
    pr=subprocess.run(cmd,cwd=str(ROOT),text=True,capture_output=True,timeout=240)
    return {'cmd':cmd,'returncode':pr.returncode,'stdout':pr.stdout,'stderr':pr.stderr}

def start_server(directory):
    class H(http.server.SimpleHTTPRequestHandler):
        def log_message(self,*a): pass
    class S(socketserver.TCPServer): allow_reuse_address=True
    srv=S(('127.0.0.1',0),H); port=srv.server_address[1]; old=Path.cwd()
    def worker():
        os.chdir(directory)
        try: srv.serve_forever()
        finally: os.chdir(old)
    threading.Thread(target=worker,daemon=True).start()
    return srv,port

def copy_files():
    out=[]
    for rel in SUPPORT:
        src=ROOT/rel; rec={'relative_path':rel,'exists':src.exists()}
        if src.exists() and src.is_file():
            dest=SOURCE/rel; dest.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,dest)
            rec.update({'copied_to':str(dest.relative_to(OUT)),'bytes':dest.stat().st_size,'sha256':sha(dest)})
        out.append(rec)
    return out

def fetch_public():
    res=[]
    for r in ROUTES:
        url=r['url']+'?v=sol-audit-v2'
        rec={'route':r,'url':url}
        try:
            with urlopen(Request(url,headers={'User-Agent':'Hermes SOL audit v2'}),timeout=30) as resp:
                body=resp.read(); rec.update({'status':resp.status,'bytes':len(body),'headers':dict(resp.headers)})
                (PUBLIC/f"{r['slug']}_http_body.html").write_bytes(body)
        except Exception as e: rec['error']=repr(e)
        res.append(rec)
    return res

def fill_state(page, slug, state):
    if slug=='lead-value-roi-calculator':
        vals={
          'default':{},
          'changed':{'#monthly-leads':'240','#qualification-rate':'35','#close-rate':'14','#revenue-per-client':'2200','#gross-margin':'62','#ad-spend':'1000','#ltv-uplift':'10'},
          'zero':{'#monthly-leads':'0','#qualification-rate':'0','#close-rate':'0','#revenue-per-client':'0','#gross-margin':'0','#ad-spend':'0','#ltv-uplift':'0'},
          'high':{'#monthly-leads':'5000','#qualification-rate':'80','#close-rate':'35','#revenue-per-client':'15000','#gross-margin':'85','#ad-spend':'50000','#ltv-uplift':'50'},
          'invalid_blank':{'#monthly-leads':'','#qualification-rate':'','#close-rate':'','#revenue-per-client':'','#gross-margin':'','#ad-spend':'','#ltv-uplift':''},
        }[state]
        page.fill('#brand-name','TWE Growth Studio'); page.fill('#brand-email','hello@example.com')
        for k,v in vals.items(): page.fill(k,v)
        page.click('#calculate')
    elif slug=='local-service-quote-calculator':
        page.fill('#brand-name','TWE Local Services'); page.fill('#brand-email','hello@example.com')
        if state=='changed': page.select_option('#service-type', index=2); page.fill('#hours','12'); page.fill('#hourly-rate','125'); page.select_option('#team-size','1.35'); page.select_option('#urgency','1.22'); page.fill('#materials','650')
        elif state=='zero': page.fill('#hours','0'); page.fill('#hourly-rate','0'); page.fill('#materials','0')
        elif state=='high': page.fill('#hours','80'); page.fill('#hourly-rate','300'); page.select_option('#team-size','1.35'); page.select_option('#urgency','1.22'); page.fill('#materials','20000')
        elif state=='invalid_blank': page.fill('#hours',''); page.fill('#hourly-rate',''); page.fill('#materials','')
        page.click('#calculate')
    elif slug=='website-audit-scorecard':
        page.fill('#brand-name','TWE Web Review'); page.fill('#brand-email','hello@example.com')
        values={'default':None,'changed':'4','zero':'0','high':'5','invalid_blank':'0'}[state]
        if values is not None:
            for sl in page.locator('input[type=range]').all(): sl.evaluate('(el,v)=>{el.value=v; el.dispatchEvent(new Event("input",{bubbles:true}))}', values)
        page.locator('#score-btn').click()
    page.wait_for_timeout(350)

def capture_all():
    captures=[]; behavior=[]; SCREEN.mkdir(parents=True,exist_ok=True); PUBLIC.mkdir(parents=True,exist_ok=True)
    srv,port=start_server(ROOT/'templates'/'landing-page'); base=f'http://127.0.0.1:{port}'
    try:
      with sync_playwright() as p:
        b=p.chromium.launch(headless=True)
        for r in ROUTES:
          for vp_name,vp in [('desktop',{'width':1440,'height':1200}),('mobile',{'width':430,'height':1100})]:
            pg=b.new_page(viewport=vp); rec={'route':r,'viewport':vp_name,'url':r['url']+'?v=sol-audit-v2'}
            resp=pg.goto(rec['url'],wait_until='networkidle',timeout=45000); pg.wait_for_timeout(400)
            png=SCREEN/f"{r['slug']}_{vp_name}.png"; html=PUBLIC/f"{r['slug']}_{vp_name}.rendered.html"; text=PUBLIC/f"{r['slug']}_{vp_name}.visible_text.txt"
            pg.screenshot(path=str(png),full_page=True); html.write_text(pg.content(),encoding='utf-8'); text.write_text(pg.locator('body').inner_text(),encoding='utf-8')
            rec.update({'status':resp.status if resp else None,'screenshot':str(png.relative_to(OUT)),'rendered_html':str(html.relative_to(OUT)),'visible_text':str(text.relative_to(OUT)),'links':pg.eval_on_selector_all('a','els=>els.map(a=>({text:a.innerText.trim(),href:a.href}))'),'images':pg.eval_on_selector_all('img','els=>els.map(i=>({alt:i.alt,src:i.src,width:i.naturalWidth,height:i.naturalHeight}))')})
            captures.append(rec); pg.close()
        for slug in SLUGS:
          for state in ['default','changed','zero','high','invalid_blank']:
            pg=b.new_page(viewport={'width':1280,'height':1000}); rec={'slug':slug,'state':state,'local_url':f'{base}/gigs/{slug}/'}
            try:
              pg.goto(rec['local_url'],wait_until='networkidle',timeout=45000); fill_state(pg,slug,state)
              png=SCREEN/f"behavior_{slug}_{state}.png"; pg.screenshot(path=str(png),full_page=True)
              rec.update({'screenshot':str(png.relative_to(OUT)),'visible_text':pg.locator('body').inner_text(),'links':pg.eval_on_selector_all('a','els=>els.map(a=>({text:a.innerText.trim(),href:a.href}))'),'result_html':pg.locator('body').inner_html()[:20000]})
            except Exception as e: rec['error']=repr(e)
            behavior.append(rec); pg.close()
        b.close()
    finally:
      srv.shutdown(); srv.server_close()
    return captures,behavior

def make_contact_sheet(pattern, outname, title):
    imgs=[]
    for slug in SLUGS:
        p=ROOT/'templates'/'landing-page'/'assets'/'screenshots'/'gigs'/f'{slug}-{pattern}.png'
        if p.exists(): imgs.append((slug,p))
    thumbs=[]
    for slug,p in imgs:
        im=Image.open(p).convert('RGB'); im.thumbnail((360,420)); thumbs.append((slug,im.copy()))
    w=420*len(thumbs); h=520
    sheet=Image.new('RGB',(max(1,w),h),(12,18,35)); d=ImageDraw.Draw(sheet)
    d.text((18,16),title,fill=(245,247,255))
    x=20
    for slug,im in thumbs:
        sheet.paste(im,(x,60)); d.text((x,490),slug,fill=(245,247,255)); x+=420
    out=ROOT/'docs'/'assets'/'screenshots'/'gigs'/outname; out.parent.mkdir(parents=True,exist_ok=True); sheet.save(out,quality=92)
    return out

def listing_matrix(captures, behavior):
    rows=[]
    for slug in SLUGS:
        cap=next(c for c in captures if c['route']['slug']==slug and c['viewport']=='desktop')
        text=(OUT/cap['visible_text']).read_text(encoding='utf-8',errors='replace')
        rows.append({'slug':slug,'public_url':f'{BASE}/gigs/{slug}/','current_status':'published and HTTP 200' if cap['status']==200 else 'needs verification','source_files':[f'gigs/{slug}/index.html',f'gigs/{slug}/styles.css',f'gigs/{slug}/script.js',f'templates/landing-page/gigs/{slug}/index.html',f'templates/landing-page/gigs/{slug}/styles.css',f'templates/landing-page/gigs/{slug}/script.js'],'image_assets':[f'templates/landing-page/assets/screenshots/gigs/{slug}-desktop-output.png',f'templates/landing-page/assets/screenshots/gigs/{slug}-mobile-output.png'],'listing_visible_text':text,'links':cap.get('links',[]),'images':cap.get('images',[]),'behavior_states':[b for b in behavior if b['slug']==slug]})
    return rows


def validate_evidence(copied, fetches, captures, behavior):
    blockers=[]
    for rec in copied:
        if not rec.get('exists'):
            blockers.append(f"missing expected source/support file: {rec['relative_path']}")
    for rec in fetches:
        if rec.get('status') != 200:
            blockers.append(f"public fetch failed for {rec['route']['slug']}: {rec.get('status') or rec.get('error')}")
    for rec in captures:
        if rec.get('status') != 200:
            blockers.append(f"browser capture failed for {rec['route']['slug']} {rec['viewport']}: {rec.get('status')}")
        if rec.get('screenshot') and not (OUT/rec['screenshot']).exists():
            blockers.append(f"missing browser screenshot: {rec['screenshot']}")
        if not rec.get('visible_text') or not (OUT/rec['visible_text']).exists():
            blockers.append(f"missing visible text capture for {rec['route']['slug']} {rec['viewport']}")
    expected={(s, st) for s in SLUGS for st in ['default','changed','zero','high','invalid_blank']}
    seen={(rec.get('slug'), rec.get('state')) for rec in behavior}
    for key in sorted(expected-seen):
        blockers.append(f"missing behavior state: {key[0]} / {key[1]}")
    for rec in behavior:
        label=f"{rec.get('slug')} / {rec.get('state')}"
        if rec.get('error'):
            blockers.append(f"behavior state has error: {label}: {rec['error']}")
        if not rec.get('screenshot') or not (OUT/rec['screenshot']).exists():
            blockers.append(f"missing behavior screenshot: {label}")
        if not rec.get('visible_text'):
            blockers.append(f"missing behavior visible text: {label}")
        if not rec.get('result_html'):
            blockers.append(f"missing behavior result html: {label}")
        if 'links' not in rec:
            blockers.append(f"missing behavior links: {label}")
    if blockers:
        write_json(OUT/'EVIDENCE_BLOCKERS.json', {'blockers': blockers})
        raise SystemExit('evidence validation failed before ZIP:\n' + '\n'.join(blockers))
    return []


def main():
    for d in [RAW,PUBLIC,SOURCE,SCREEN,SUMMARY]: d.mkdir(parents=True,exist_ok=True)
    cmds={'publish_refresh':run(['python','scripts/publish_gigs_to_landing_page.py']),'git_status':run(['git','status','--short']),'git_head':run(['git','rev-parse','HEAD']),'origin_main':run(['bash','-lc','git ls-remote origin main | cut -f1']),'log':run(['git','log','--oneline','-5'])}
    desktop_sheet=make_contact_sheet('desktop-output','gig-factory-desktop-contact-sheet.jpg','Gig Factory desktop screenshot contact sheet')
    mobile_sheet=make_contact_sheet('mobile-output','gig-factory-mobile-contact-sheet.jpg','Gig Factory mobile screenshot contact sheet')
    SUPPORT.extend([str(desktop_sheet.relative_to(ROOT)),str(mobile_sheet.relative_to(ROOT))])
    copied=copy_files(); fetches=fetch_public(); captures,behavior=capture_all(); matrix=listing_matrix(captures,behavior)
    blockers=validate_evidence(copied, fetches, captures, behavior)
    write_json(SUMMARY/'commands.json',cmds); write_json(SUMMARY/'public_fetches.json',fetches); write_json(SUMMARY/'browser_captures.json',captures); write_json(SUMMARY/'behavior_state_matrix.json',behavior); write_json(SUMMARY/'listing_matrix.json',matrix)
    manifest={'package':'v2','generated_utc':datetime.now(timezone.utc).isoformat(),'base_url':BASE,'routes':ROUTES,'slugs':SLUGS,'git':{'head':cmds['git_head']['stdout'].strip(),'origin_main':cmds['origin_main']['stdout'].strip(),'status_short':cmds['git_status']['stdout']},'copied_files':copied,'required_evidence_blockers_expected':blockers,'notes':'Includes JS source, desktop/mobile contact sheets, public captures, source files, and validated behavior-state screenshots for default/changed/zero/high/invalid inputs. The script exits nonzero before ZIP creation if any promised evidence state is missing or errored.'}
    write_json(SUMMARY/'manifest.json',manifest)

    readme=['# SOL Vercel Gig Audit Evidence Package v2','',f'Generated UTC: {manifest["generated_utc"]}',f'Base URL: {BASE}',f'Git head: {manifest["git"]["head"]}','','## Routes']
    for r in ROUTES: readme.append(f'- {r["slug"]}: {r["url"]}')
    readme += ['','## Key contents','- Full source: HTML/CSS/JS for homepage and three gig pages.','- Full public captures: HTTP bodies, rendered HTML, visible text, desktop/mobile screenshots.','- Behavior states: default, changed, zero, high, invalid_blank screenshots and captured output/link state for every calculator.','- Contact sheets: desktop and mobile.','- summaries/listing_matrix.json and summaries/behavior_state_matrix.json are the main machine-readable audit indexes.']
    (OUT/'EVIDENCE_README.md').write_text('\n'.join(readme)+'\n',encoding='utf-8')
    zip_path=OUT/f'SOL_INPUT_ZIP_vercel_gig_service_listings_v2_{RUN_ID}.zip'
    with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as z:
        for f in sorted(OUT.rglob('*')):
            if f==zip_path or f.is_dir(): continue
            z.write(f,f.relative_to(OUT))
    info={'zip_path':str(zip_path),'zip_name':zip_path.name,'sha256':sha(zip_path),'bytes':zip_path.stat().st_size,'members':len(zipfile.ZipFile(zip_path).namelist())}
    write_json(OUT/'ZIP_INFO.json',info)
    print(json.dumps({'out':str(OUT),'zip':str(zip_path),'sha256':info['sha256'],'members':info['members'],'listings':len(SLUGS)},indent=2))
if __name__=='__main__': main()
