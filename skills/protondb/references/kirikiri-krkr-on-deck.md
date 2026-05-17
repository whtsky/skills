# Running Kirikiri / krkr (吉里吉里) VNs on Steam Deck

The Kirikiri / KirikiriZ engine ("krkr", "krkr2", "krkrz") powers a large share of Japanese VNs. It's a Windows engine using DirectShow for video and TJS scripting. Common Proton failure modes are predictable.

ProtonDB coverage for these games is usually **very thin or zero reports** (small Linux user base for niche/R18 VNs), so don't expect a tier — work from the engine-level recipe below.

## Recommended setup (works for most krkr VNs)

1. **Install latest GE-Proton** via ProtonUp-Qt. Stock Valve Proton handles krkr worse than GE — GE bundles DirectShow / video codec fixes.
2. **Force compat tool**: Steam → right-click game → Properties → Compatibility → Force the use of a specific Steam Play compatibility tool → `GE-Proton<latest>`.
3. **Install protontricks bits** (run once per game, replace APPID):
   ```
   protontricks <APPID> -q quartz lavfilters cjkfonts
   ```
   - `quartz` — DirectShow runtime. Critical: without it, krkr OP/ED videos black-screen or game hangs at splash.
   - `lavfilters` — codec pack for WMV/MP4 video the engine loads.
   - `cjkfonts` — Japanese font fallback; prevents tofu boxes in dialogue.
   - (Optional) `wmp11` if `lavfilters` alone doesn't fix video.
4. **Launch options** for Japanese locale (prevents text mojibake):
   ```
   LANG=ja_JP.UTF-8 LC_ALL=ja_JP.UTF-8 %command%
   ```
5. **Controller**: krkr has no native gamepad support. On Deck, use the "Web Browser" or "Gamepad with Mouse Trackpad" Steam Input template — right trackpad as mouse, A = left click.

## Symptoms → fix table

| Symptom | Fix |
|---|---|
| Black screen on OP video | `protontricks <APPID> -q quartz lavfilters` |
| Dialogue boxes show tofu □□□ | `protontricks <APPID> -q cjkfonts` + JP locale launch option |
| Garbled / mojibake menu text | JP locale launch option (`LANG=ja_JP.UTF-8`) |
| Hangs at splash / blank window | Switch to GE-Proton, ensure `quartz` installed |
| No controller input on Deck | Switch Steam Input template to "Mouse + Trackpad", desktop mode often easier than gaming mode |
| Valve marks game "Deck Unsupported" | Usually = no controller support + small text. Game can still run fine in desktop mode. |

## Community alternatives (engine replacement, not Proton)

These bypass Proton entirely by re-implementing the engine. Almost never worth it for play-it scenarios.

- **krkrz official repo** — https://github.com/krkrz/krkrz (★913, last commit 2020)
  - Windows + Android backends only. **No Linux backend.** Don't waste time here.
- **xp3 unpack + re-implement in another engine** (Ren'Py etc.) — modder territory, hundreds of hours, only relevant for translation/preservation work.

**Verdict**: stick with GE-Proton + protontricks. Native engine replacements for Linux don't exist in a usable state.

## Identifying krkr games

Signs a Steam VN is krkr-based (so this guide applies):
- Installed game folder has `tvpwin32.exe` or `tvpwin64.exe` (the krkr runtime)
- `data.xp3`, `patch.xp3`, `scenario.xp3` archives
- A `plugin/` folder full of `.dll` plugins
- Japanese publisher (lass, Pulltop, Lump of Sugar, August, Navel, Yuzusoft, etc.)

If you see Ren'Py (`.rpa` archives, `renpy/` folder) instead, that engine is natively cross-platform and usually runs without Proton tweaks — different story.
