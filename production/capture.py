import asyncio,json
from pathlib import Path
from playwright.async_api import async_playwright
async def main():
 async with async_playwright() as p:
  b=await p.chromium.launch(args=['--no-sandbox'])
  page=await b.new_page(viewport={'width':1440,'height':1000},device_scale_factor=1)
  for name,path in [('home','/'),('guide','/guide'),('market10','/robinhood/market/10'),('market12','/robinhood/market/12'),('market3','/market/3')]:
   await page.goto('https://pepe2pepe.fun'+path,wait_until='domcontentloaded',timeout=90000)
   await page.wait_for_timeout(8000)
   await page.screenshot(path=f'production/captures/{name}.png',full_page=True)
   Path(f'production/captures/{name}.txt').write_text(await page.locator('body').inner_text())
   print(name,(await page.locator('body').inner_text())[:16000],flush=True)
  await page.goto('https://explorer.imd.fun/jobs/e154da77-66eb-4c2b-9904-0f82d02be6c1',wait_until='domcontentloaded')
  Path('production/captures/reference.txt').write_text(await page.locator('body').inner_text())
  await b.close()
asyncio.run(main())
