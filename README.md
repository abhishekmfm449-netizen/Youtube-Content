# Youtube-Content

Source assets and the edit that turns them into a finished Short.

## Vayu UTtaM

A 1080×1920 / 30 fps YouTube Short about the Indian Air Force's Vayu UTtaM
unmanned traffic management system, cut to the supplied voiceover.

**Watch:** [`project/out/Vayu_UTtaM_YouTube_Short.mp4`](project/out/Vayu_UTtaM_YouTube_Short.mp4) — 82.6 s

**How it was made, what was used, what was deliberately left out:**
[`project/README.md`](project/README.md)

## Layout

| Folder | What's in it |
|---|---|
| `Script/` | The narration script |
| `Voiceover/` | The recorded read — the master timeline for the edit |
| `Image/` | Supplied stills |
| `Video/` | Supplied clips |
| `project/` | The edit: source, assets it generates, and the deliverables in `project/out/` |

To rebuild the video from these assets: `cd project && ./build.sh`
