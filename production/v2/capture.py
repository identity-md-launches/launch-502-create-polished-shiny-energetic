#!/usr/bin/env python3
"""Capture unmodified, hydrated public product UI through an installed Playwright.

No npm/pip install is required for delivery. Lossless captured WebP files and text
are supplied for the offline film render. Optional recapture needs Playwright + Chromium, supplied
by the caller through environment variables; the original capture environment had
both already installed. No UI values or page styles are rewritten.
"""
import os, subprocess
from pathlib import Path

SCRIPT = r'''
const {chromium}=require(process.env.PLAYWRIGHT_MODULE || '/opt/identitymd/browser-mcp/node_modules/playwright');
const fs=require('fs');
const out='production/v2/captures';
const research='test/scratch/v2-recapture';
fs.mkdirSync(research,{recursive:true});
(async()=>{
 const b=await chromium.launch({executablePath:process.env.CHROMIUM_EXECUTABLE || '/home/imd-worker/.cache/ms-playwright/chromium-1208/chrome-linux64/chrome',headless:true,args:['--no-sandbox']});
 const page=await b.newPage({viewport:{width:1440,height:1000},deviceScaleFactor:2});
 const metadata={captured_at_utc:new Date().toISOString(),device_scale_factor:2,pages:[]};
 async function save(name,url){
  await page.goto(url,{waitUntil:'domcontentloaded',timeout:90000});
  await page.waitForTimeout(12000);
  await page.evaluate(()=>document.fonts.ready);
  await page.screenshot({path:`${research}/${name}.png`,fullPage:true});
  fs.writeFileSync(`${out}/${name}.txt`,await page.locator('body').innerText());
  metadata.pages.push({name,url,viewport:page.viewportSize(),document:await page.evaluate(()=>({width:document.documentElement.scrollWidth,height:document.documentElement.scrollHeight})),captured_at_utc:new Date().toISOString()});
  console.log('captured',name);
 }
 await save('home','https://pepe2pepe.fun/');
 await page.setViewportSize({width:900,height:1000});
 await page.getByRole('button',{name:'Crypto',exact:true}).click();
 await page.waitForTimeout(2000);
 await page.screenshot({path:`${research}/home-crypto-900.png`,fullPage:true});
 fs.writeFileSync(`${out}/home-crypto-900.txt`,await page.locator('body').innerText());
 fs.writeFileSync(`${out}/home-crypto-900-dom.json`,JSON.stringify(await page.locator('a[href*="/market/"]').evaluateAll(es=>es.map(e=>({text:e.innerText,url:e.getAttribute('href'),rect:{x:e.getBoundingClientRect().x,y:e.getBoundingClientRect().y,width:e.getBoundingClientRect().width,height:e.getBoundingClientRect().height}}))),null,2));
 metadata.pages.push({name:'home-crypto-900',url:page.url(),interaction:'Clicked real Crypto topic filter',viewport:page.viewportSize(),captured_at_utc:new Date().toISOString()});
 await page.setViewportSize({width:1440,height:1000});
 await save('market10','https://pepe2pepe.fun/robinhood/market/10');
 await save('market12','https://pepe2pepe.fun/robinhood/market/12');
 await save('market3','https://pepe2pepe.fun/market/3');
 await save('guide','https://pepe2pepe.fun/guide');
 for(const label of ['Who can create a market?','When does the Oracle answer?','Who can finalize or correct a result?']){
  await page.getByText(label,{exact:true}).click();
 }
 await page.screenshot({path:`${research}/guide-oracle.png`,fullPage:true});
 fs.writeFileSync(`${out}/guide-oracle.txt`,await page.locator('body').innerText());
 metadata.source_packaging={home:{file:'home-crypto-900.webp',original_crop_xywh:[0,1700,1800,1120],lossless:true},market10:{file:'market10.webp',lossless:true},research_png_directory:research};
 fs.writeFileSync(`${out}/metadata.json`,JSON.stringify(metadata,null,2));
 await b.close();
})();
'''

if __name__ == '__main__':
    Path('production/v2/captures').mkdir(parents=True,exist_ok=True)
    subprocess.run(['node','-e',SCRIPT],check=True)
    # Keep only film inputs in the source bundle. Research text stays alongside
    # them; full-page research PNGs remain available in disposable scratch.
    for name,filters in [('home-crypto-900',['-vf','crop=1800:1120:0:1700']),('market10',[])]:
        subprocess.run(['ffmpeg','-y','-v','error','-i',
            f'test/scratch/v2-recapture/{name}.png',*filters,
            '-c:v','libwebp','-lossless','1','-compression_level','6',
            '-pix_fmt','bgra',f'production/v2/captures/{name}.webp'],check=True)
    print('Saved lossless render inputs. Check crop coordinates if the live layout changed.')
