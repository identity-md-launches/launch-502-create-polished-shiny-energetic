import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
async def main():
 async with async_playwright() as p:
  b=await p.chromium.launch(args=['--no-sandbox']); page=await b.new_page(viewport={'width':1440,'height':1000})
  await page.goto('https://pepe2pepe.fun/guide',wait_until='domcontentloaded'); await page.wait_for_timeout(10000)
  for s in ['Who can create a market?','When does the Oracle answer?','Who can finalize or correct a result?']:
   await page.get_by_text(s,exact=False).first.click()
  await page.screenshot(path='production/captures/oracle.png',full_page=True)
  Path('production/captures/oracle.txt').write_text(await page.locator('body').inner_text())
  await b.close()
asyncio.run(main())
