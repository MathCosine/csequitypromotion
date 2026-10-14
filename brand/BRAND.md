# CS Equity AI — brand notes

Two looks:

- **Posters: clean event posters.** DM Sans throughout, flat colour (navy `#1C2B4A` text,
  blue `#2457C5`, pink `#E5487F`, yellow `#FFCF3D`, soft tints of each), warm off-white
  stock with a faint grain, and a clear reading order: headline, one-line pitch, the details,
  then a blue call-to-action panel with a QR code. Code: `scripts/posters.py`.
- **Video and social: cut-paper puppet theater.** Printed illustrations cut out of card
  stock, hung on strings inside a riveted brass frame with red curtains, on a kraft-paper wall.
  Toolkit: `scripts/paper.py`.

## Mark
`logo-mark.svg`: code brackets `< >` (computer science) around an equals sign (equity),
with two gold nodes. `logo-horizontal.svg` adds the wordmark.

## Paper-theater palette

| Token  | Hex       | Use                                     |
|--------|-----------|-----------------------------------------|
| Kraft  | `#5E4634` | Background wall                         |
| Paper  | `#F1E8D4` | Cards, tickets                          |
| Sky    | `#EAE0C8` | Stage backdrop                          |
| Ink    | `#2E2620` | Text, outlines, strings                 |
| Terra  | `#C47A5E` | Accent headlines, tags, the bridge      |
| Teal   | `#8DB9B3` | Water; `#4F8580` for small accent text  |
| Slate  | `#94A9BC` | Buildings                               |
| Ochre  | `#D8B25C` | Highlights; brass `#B48A3C` for frames  |
| Navy   | `#2F3A56` | Logo tile, laptop screens               |

## Paper-theater type
- **Fraunces** (900 for headlines, 700 for small accents): soft vintage serif.
- **Special Elite**: typewriter face for labels and body copy.

Both are embedded in every SVG (from `brand/fonts/`, SIL Open Font License), so the files
render the same anywhere.

## Paper look, in code (`scripts/paper.py`)
- `piece()`: cream paper margin + colour + engraving hatch + thin ink line, with a filter
  that roughens the edge slightly and drops a soft shadow.
- `card()`: a printed ticket with a double ink rule. `tape()`, `pin()`, `strings()` attach things.
- `frame()`: the brass porthole with rivets. `scenery()`: the stage set, with a US
  suspension bridge, Hong Kong and Taipei skyline, and water, for the three places we teach.
- A grain + fibre overlay and a vignette sit over the whole page.

## Voice
Write like a person, not a brochure. The site's own lines are the model:
- "We teach students to build with AI, not just use it. Free."
- "No tuition, no gatekeeping. Just a browser and curiosity."
- "Each level ends with something real."
- "Free, like everything we run."

Rules of thumb:
- Only claim what's on csequityai.org. No invented stats or student counts.
- Short sentences. Concrete nouns (a certificate, a working AI system, a pitch).
- Skip words like "empower", "unlock", "revolutionize", "journey", "cutting-edge".
