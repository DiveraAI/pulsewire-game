#!/usr/bin/env python3
"""PULSEWIRE web demo builder.

Reads the BUILT game (pulsewire/www/index.html — AD-KIT already stripped by
`npm run build`) and applies the demo deltas below, then copies the minimal
asset subset. The shipping game is never modified.

Re-sync after a game update:
    cd pulsewire && npm run build
    python3 pulsewire-site/play/make_demo.py

Every delta is anchored to an exact source string and FAILS LOUD if the anchor
is missing or ambiguous — a game update that moves an anchor stops the build
instead of silently shipping a half-patched demo.
"""
import pathlib, shutil, sys

HERE = pathlib.Path(__file__).resolve().parent            # pulsewire-site/play
GAME = HERE.parent.parent / 'pulsewire'                   # sibling repo
SRC  = GAME / 'www' / 'index.html'
OUT  = HERE / 'index.html'

DEMO_LEVELS = 5
APPSTORE_URL = 'https://apps.apple.com/us/app/pulsewire/id6778034497?ct=webdemo&mt=8'
# TODO(user): append &pt=<provider-token> (App Store Connect → Analytics → campaign
# links) so ct=webdemo shows up as a named campaign source. Referrer attribution
# (pulsewire-game.com) works even without it.

html = SRC.read_text(encoding='utf-8')
if 'AD-KIT-STRIP-START' in html:
    sys.exit('FATAL: source still contains the AD-KIT — run `npm run build` in pulsewire first.')

def patch(anchor, replacement, count=1):
    global html
    n = html.count(anchor)
    if n != count:
        sys.exit(f'FATAL: anchor not unique/found ({n}x, want {count}):\n  {anchor[:100]}')
    html = html.replace(anchor, replacement)

# ── 1. Page identity — this IS the product being promoted: a free browser game ─
patch('<title>PULSEWIRE</title>',
      '<title>PULSEWIRE — Free Browser Game · A Cyberpunk Arcade Thriller</title>\n'
      '<meta name="description" content="Free browser game — no install, no signup, no ads. '
      'Draw one unbroken line, ground the spark, skim death for points. '
      'A cyberpunk arcade thriller, playable right here.">\n'
      '<link rel="canonical" href="https://www.pulsewire-game.com/play/">\n'
      '<meta property="og:site_name" content="PULSEWIRE">\n'
      '<meta property="og:title" content="PULSEWIRE — Free Browser Game">\n'
      '<meta property="og:description" content="A cyberpunk arcade thriller in your browser. '
      'No install, no signup, no ads. Trace the current.">\n'
      '<meta property="og:type" content="website">\n'
      '<meta property="og:url" content="https://www.pulsewire-game.com/play/">\n'
      '<meta property="og:image" content="https://www.pulsewire-game.com/assets/pulsewire-poster.jpg">\n'
      '<meta name="twitter:card" content="summary_large_image">\n'
      '<meta name="twitter:title" content="PULSEWIRE — Free Browser Game">\n'
      '<meta name="twitter:description" content="A cyberpunk arcade thriller in your browser. '
      'No install, no signup, no ads.">\n'
      '<meta name="twitter:image" content="https://www.pulsewire-game.com/assets/pulsewire-poster.jpg">\n'
      '<link rel="icon" href="../assets/favicon.png">')

# ── 2. Campaign capped at the first 5 levels ────────────────────────────────
patch('let levels = getLevels();',
      f'let levels = getLevels().slice(0, {DEMO_LEVELS});   // DEMO: training segment only')

# ── 3. Hide Studio / editor / bundle entries (elements stay: JS handlers keep
#       their references; they are simply unreachable) ────────────────────────
patch('</head>',
      '<style id="demoSkin">\n'
      '  #studioEntry, #editorToggle, #bundleBanner { display: none !important; }\n'
      '  #demoWall { display: flex; flex-direction: column; align-items: center; gap: 12px;\n'
      '    margin: 20px auto 4px; max-width: 340px; }\n'
      '  .dw-badge { display: block; width: 100%; box-sizing: border-box; text-align: center;\n'
      '    font-family: inherit; font-size: 15px; font-weight: 700; letter-spacing: .14em;\n'
      '    padding: 15px 20px; border: 1px solid rgba(78,224,255,.7); border-radius: 10px;\n'
      '    color: #eaffff; background: rgba(78,224,255,.09); text-decoration: none;\n'
      '    box-shadow: 0 0 22px rgba(78,224,255,.22), inset 0 0 14px rgba(78,224,255,.06); }\n'
      '  .dw-badge:active { background: rgba(78,224,255,.2); }\n'
      '  .dw-soon { opacity: .4; border-style: dashed; pointer-events: none; box-shadow: none; }\n'
      '  .dw-note { font-size: 12px; letter-spacing: .1em; color: #9ccfde; text-align: center; }\n'
      '  .dw-tag  { font-size: 11px; letter-spacing: .18em; color: #6b8b96; text-align: center; }\n'
      '  #demoMenuStore { display: block; margin: 14px auto 0; max-width: 340px; font-size: 12px;\n'
      '    letter-spacing: .12em; padding: 12px 16px; }\n'
      '</style>\n</head>')

# ── 4. Badge wall markup (hidden until the L5 full-clear) ───────────────────
patch('<button id="restartBtn">Retry level</button>',
      '<div id="demoWall" style="display:none">\n'
      '      <a class="dw-badge" href="' + APPSTORE_URL + '">&#63743; DOWNLOAD ON THE APP STORE</a>\n'
      '      <span class="dw-badge dw-soon">GOOGLE PLAY &mdash; SOON</span>\n'
      '      <div class="dw-note">FEEL THE CURRENT &mdash; full haptic feedback in the app.</div>\n'
      '      <div class="dw-tag">FREE &middot; 21 LEVELS &middot; ZERO ADS &middot; 100% OFFLINE</div>\n'
      '    </div>\n'
      '    <button id="restartBtn">Retry level</button>')

# ── 4b. Returning-player store strip on the menu (hidden until first full clear) ─
patch('<div class="bundle-banner" id="bundleBanner">',
      '<a id="demoMenuStore" class="dw-badge" style="display:none" href="' + APPSTORE_URL + '">'
      '&#63743; GET THE FULL GAME &mdash; FREE ON THE APP STORE</a>\n'
      '    <div class="bundle-banner" id="bundleBanner">')

# ── 4c. Channel attribution + returning-player logic (outside the game IIFE) ──
#   ?src=tt|ig|rd is saved first-touch to localStorage and folded into every store
#   badge's campaign token (ct=webdemo-<src>) so App Analytics splits installs by
#   channel — still zero data collected by us.
patch('</body>',
      '<script>\n'
      '(function () {\n'
      '  try {\n'
      '    var src = new URLSearchParams(location.search).get("src");\n'
      '    if (src) { src = src.replace(/[^a-z0-9_-]/gi, "").slice(0, 12); localStorage.setItem("pw_demo_src", src); }\n'
      '    else { src = localStorage.getItem("pw_demo_src") || ""; }\n'
      '    if (src) {\n'
      '      document.querySelectorAll("a.dw-badge[href]").forEach(function (a) {\n'
      '        a.href = a.href.replace("ct=webdemo", "ct=webdemo-" + src);\n'
      '      });\n'
      '    }\n'
      '    if (localStorage.getItem("pw_demo_cleared") === "1") {\n'
      '      var s = document.getElementById("demoMenuStore");\n'
      '      if (s) s.style.display = "";\n'
      '    }\n'
      '  } catch (e) {}\n'
      '})();\n'
      '</script>\n'
      '</body>')

# ── 5. Result screen: demo wall shown on the L5 full-clear, hidden otherwise ─
patch("document.getElementById('runVerdict').style.display = 'none';",
      "document.getElementById('runVerdict').style.display = 'none';\n"
      "    document.getElementById('demoWall').style.display = 'none';   // DEMO")

patch("document.getElementById('mainframeBypassed').style.display = isFullClear ? '' : 'none';",
      "document.getElementById('mainframeBypassed').style.display = 'none';   // DEMO: no editor pitch\n"
      "      if (isFullClear) {\n"
      "        document.getElementById('demoWall').style.display = '';\n"
      "        try { localStorage.setItem('pw_demo_cleared', '1'); } catch (e) {}\n"
      "        var _dms = document.getElementById('demoMenuStore'); if (_dms) _dms.style.display = '';\n"
      "      }")

patch("document.getElementById('resLabel').textContent = 'SYSTEM BREACH COMPLETE';",
      "document.getElementById('resLabel').textContent = 'TRAINING SEGMENT DISMANTLED';")

patch("document.getElementById('resHeadline').textContent = 'MAINFRAME BYPASSED';",
      "document.getElementById('resHeadline').textContent = 'THE CURRENT CONTINUES';")

patch("document.getElementById('resSub').textContent = 'All ' + levels.length + ' levels dismantled. Total: ' + totalScore + ' pts.';",
      "document.getElementById('resSub').textContent = 'Five of twenty-one levels grounded. The mainframe remains.';")

patch("document.getElementById('resSub').textContent = 'All ' + levels.length + ' levels dismantled. The ledger is sealed.';",
      "document.getElementById('resSub').textContent = 'Five of twenty-one levels grounded. The ledger is sealed. The mainframe remains.';")

# ── 9. iPhone Safari: the share-cut stage must track the VISUAL viewport ─────
#   In mobile Safari 100vh (large viewport) ≠ innerHeight (visual viewport with the
#   address bar showing) → the replay canvas buffer got stretched onto a taller CSS
#   box (elongated clip) and the endcard's 0.63·OH CTA line slid into the bottom
#   share prompt. Sizing the CSS box in px from the SAME source as the buffer keeps
#   them locked; the resize listener re-syncs when the bar collapses/expands.
#   (No-op in the app's WKWebView, where 100vh == innerHeight — game code untouched.)
patch("stage.style.cssText = 'position:fixed;inset:0;z-index:9000;width:100vw;height:100vh;background:#000;touch-action:none;';",
      "stage.style.cssText = 'position:fixed;inset:0;z-index:9000;background:#000;touch-action:none;';   // DEMO: sized in px by resizeStage (100vh trap)")

patch("function resizeStage() { if (!stage) return; const dpr = Math.min(window.devicePixelRatio || 1, 2); stage.width = Math.round(innerWidth * dpr); stage.height = Math.round(innerHeight * dpr); }",
      "function resizeStage() { if (!stage) return; const dpr = Math.min(window.devicePixelRatio || 1, 2); "
      "stage.style.width = innerWidth + 'px'; stage.style.height = innerHeight + 'px'; "
      "stage.width = Math.round(innerWidth * dpr); stage.height = Math.round(innerHeight * dpr); }")

# ── 10. Lift the endcard text block clear of the bottom share prompt ─────────
#   Even with the viewport fix, the CTA line at 0.63·OH clears the DOM prompt by
#   only ~15–22px on small phones with the Safari bar visible. Raising the whole
#   block gives it real air; encoded clips (no prompt) still read centered.
patch('const cx = OW / 2, titleY = OH * 0.46, subY = OH * 0.55;',
      'const cx = OW / 2, titleY = OH * 0.40, subY = OH * 0.49;   // DEMO: lifted clear of the share prompt')
patch("ctx.fillStyle = 'rgba(130,236,255,0.97)'; ctx.fillText('FREE ON APP STORE & PLAY STORE', cx, OH * 0.63);",
      "ctx.fillStyle = 'rgba(130,236,255,0.97)'; ctx.fillText('FREE ON APP STORE & PLAY STORE', cx, OH * 0.56);   // DEMO: lifted")

OUT.write_text(html, encoding='utf-8')

# ── 6. Asset subset: fonts + splash icon + story strips for L1–L5 (+06 spare) ─
A_SRC, A_OUT = GAME / 'www' / 'assets', HERE / 'assets'
if A_OUT.exists():
    shutil.rmtree(A_OUT)
(A_OUT / 'strips').mkdir(parents=True)
shutil.copytree(A_SRC / 'fonts', A_OUT / 'fonts')
shutil.copy2(A_SRC / 'appicon-1024.png', A_OUT / 'appicon-1024.png')
for n in range(1, 7):
    shutil.copy2(A_SRC / 'strips' / f'level{n:02d}.jpg', A_OUT / 'strips' / f'level{n:02d}.jpg')

print(f'OK: demo written -> {OUT}')
print(f'OK: assets -> {A_OUT} ({sum(1 for _ in A_OUT.rglob("*") if _.is_file())} files)')
