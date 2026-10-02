# Public product research and genuine UI sources

Read and captured on **2 October 2026, approximately 20:26–20:30 UTC**.
The browser was the installed Chromium (Playwright browser revision 1208), driven by the installed Playwright package. No browser or package was installed for this step. Captures are unmodified browser pixels at device scale 2, after a 10–12 second hydration wait and font loading. The built-in web reader could not access the domain; the direct HTTPS site and real Chromium browser did.

Sources:

- <https://pepe2pepe.fun/> — current fixed-odds homepage and open-market cards.
- <https://pepe2pepe.fun/guide> — current public product blueprint, including expanded real FAQ summaries about creation, Oracle timing and settlement review.
- <https://pepe2pepe.fun/robinhood/market/12> — actual open Quotrons market, YES 40% / NO 60%; 63 IMD volume at capture.
- <https://pepe2pepe.fun/robinhood/market/10> — actual open IMD-price market, YES 50% / NO 50%; 320 USDG volume at capture.
- <https://pepe2pepe.fun/market/3> — captured for research only; currently trading closed, so it should not be presented as an open market.

## Product facts checked

Anyone can create a question and fund a side at fixed odds. Other people can back the same side or take the opposite side; earlier backing matches first. An accepted return does not change when later people bet. The contract holds funds, on Ethereum or Robinhood. No NFT is required. The IMD Oracle supplies outcome research, and operator review remains the current default before settlement. Ask Oracle is the earliest request time, not a payout deadline. The film should make no promise of profit, immediate settlement or autonomous resolution.

## Capture choices

`captures/home-crypto-900.webp` is the real homepage with the actual **Crypto** topic filter selected in the browser. Its natural responsive 900 CSS pixel viewport displays two genuine open cards side by side. No CSS, market data, titles, balances or outcomes were changed. The camera can move within this one raster to preserve the spatial relationship between header and cards.

Suggested physical-image crop for a 1320 × 651 film region: x=24, width=1752, height=864. Drift y from 1740 to 1920, then hold. Both real questions and YES/NO odds are visible through this move. The first position includes the real open-market section heading; the second includes both complete cards. The original screenshot measured 1800 × 3648. To fit the source upload budget, the delivered lossless WebP retains original rows 1700–2819, all 1800 columns (1800 × 1120). The compositor places these rows at their original y=1700 position on an in-memory canvas, preserving the original camera coordinates and subpixel arithmetic; every sampled pixel is retained, with extra margin for resampling. Padding is outside every rendered viewport and is never visible. Decoded RGB pixels were compared byte for byte against the original PNG crop.

`captures/market10.webp` shows the site's current, simplified real market UI, including a blank zero stake input, Bet NO 50% and Bet YES 50%. No wallet was connected and no stake was entered. Native screenshot: 2880 × 2010. Suggested overview crop: (500, 290) to (2816, 1310). The actual question is large at top; actual controls are at the right. Because V1's old UI has changed, use this fresh capture rather than reconstructing its older controls.

`captures/guide-oracle.txt` is the expanded current FAQ research evidence, not a recommended film composition. The Oracle film scene can use a clearly editorial illustration, without suggesting an actual transaction or completed result.

Capture times and image dimensions are in `captures/metadata.json`. `capture.py` preserves the optional acquisition recipe. Offline rendering uses the delivered lossless WebP inputs and does not need network access or Playwright. The market #10 source is a full-frame lossless conversion, with decoded RGB equality checked. Unused research screenshots were removed to meet the 8 MiB source limit; all raw research text, URLs, acquisition times and DOM evidence remain. Optional recapture writes full-page screenshots to `test/scratch/v2-recapture/`.
