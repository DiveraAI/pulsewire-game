# PULSEWIRE — Free Browser Game (`/play/`)

**This page IS the promoted product** (positioning decision 2026-07-17): TikTok/IG/Reddit
traffic lands here directly (`?src=tt|ig|rd`), plays free — no install, no signup — and the
game itself sells the App Store upgrade after 5 levels. A **standalone copy** of the game;
the shipping game (`pulsewire/index.html`) is never modified — this directory is generated
from the *built* game by `make_demo.py`.

## Files

| file | what |
|---|---|
| `make_demo.py` | the generator — anchored patches, fails loud if the game moved |
| `index.html` | GENERATED — do not hand-edit (edits are lost on re-sync) |
| `assets/` | GENERATED — minimal subset: fonts, splash icon, strips 01–06 |
| `README.md` | this file |

## Re-sync after a game update

```bash
cd ~/Desktop/divera_apps/pulsewire && npm run build       # AD-KIT-stripped www/
python3 ~/Desktop/divera_apps/pulsewire-site/play/make_demo.py
```

If any anchor fails (a patched string changed upstream), the build STOPS with the
missing anchor printed — update `make_demo.py`, never ship a half-patched demo.

## The demo deltas (all applied by make_demo.py)

1. **Title/meta** — "PULSEWIRE — Play the Demo" + meta description.
2. **Campaign capped at 5 levels** — `getLevels().slice(0, 5)`; the level picker
   wraps 1–5 automatically; clearing L5 CRUSH fires the game's own full-clear
   victory branch.
3. **Premium entries hidden** — `#studioEntry`, `#editorToggle`, `#bundleBanner`
   via injected CSS (elements stay in the DOM so game JS keeps its references).
4. **Full-clear result re-skinned** — "TRAINING SEGMENT DISMANTLED /
   THE CURRENT CONTINUES / Five of twenty-one levels grounded…", editor pitch
   (`#mainframeBypassed`) suppressed.
5. **Badge wall** (`#demoWall`) — shown only on the full clear:
   App Store badge → `https://apps.apple.com/us/app/pulsewire/id6778034497?ct=webdemo&mt=8`,
   Google Play placeholder (dashed, disabled — flip when the Play listing is live),
   haptics upsell line, `FREE · 21 LEVELS · ZERO ADS · 100% OFFLINE`.

   **TODO:** append `&pt=<provider-token>` (App Store Connect → campaign links) to
   the badge URL so the `ct` tokens appear as named sources in App Analytics.
   Referrer attribution from pulsewire-game.com works without it.
6. **Channel attribution** (`?src=`) — an inline script (outside the game IIFE) saves the
   first-touch `src` to `localStorage.pw_demo_src` and rewrites every `a.dw-badge` href to
   `ct=webdemo-<src>` (e.g. `webdemo-tt`). Channels: `tt` TikTok, `ig` Instagram, `rd` Reddit.
   Zero data collected by us — attribution happens Apple-side.
7. **Returning-player store strip** (`#demoMenuStore`) — hidden until the first full clear
   sets `localStorage.pw_demo_cleared`; then a "GET THE FULL GAME" badge shows on the menu
   permanently, so returners never have to re-clear L5 to find the store link.
8. **Share/social meta** — og/twitter cards + canonical for the `/play/` URL ("Free Browser
   Game") so bio links unfurl properly.

## Verified 2026-07-17 (browser pane, mobile viewport)

- Loads clean, zero console errors, no asset 404s (favicon only).
- Menu: premium entries hidden; picker cycles exactly L1–L5.
- Tutorial (Level 0) fires on first run; skippable.
- Finger-trace verified: draw, checkpoint lift/resume, precision zoom lens,
  spark launch, grazes (+95/+80), patrol-hit fail screen, score gates (NEED 120).
- Share-cut preview appears on clears and its endcard already advertises the stores;
  "Not now" releases the held advance.
- Full-clear victory → badge wall verified (1-level scratch build, same code path):
  correct texts, campaign-tokened App Store link, Play placeholder, PLAY AGAIN works.

## Still owed (device pass — user)

- Real iPhone Safari via the localtunnel workflow: collapsing address bar
  (`100dvh` behaviour), rubber-band scroll, uninterrupted trace.
- Flip the Google Play badge live once the Play listing exists.
