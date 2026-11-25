# AE Replace Color Emojis (`AE_Replace_Color_Emojis.jsx`)

**Procedural typography engine that detects monochrome font emojis in Adobe After Effects text layers, measures their exact coordinates, and replaces them with native, full-color vector shape layer emojis.**

[![Live Demo](https://img.shields.io/badge/Live%20Demo-AE%20ScriptUI%20Simulator-2c8cff?style=for-the-badge&logo=javascript)](https://work2survive.github.io/AE_JS_builder/?jsx=AE_Replace_Color_Emojis.jsx&autobuild=true)
[![Adobe After Effects](https://img.shields.io/badge/Adobe%20After%20Effects-CS6%20--%20CC%202026%2B-9999FF?style=for-the-badge&logo=adobeaftereffects)](https://www.adobe.com/products/aftereffects.html)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

> **[🚀 Launch Interactive Live Demo in Browser (`AE_JS_builder`)](https://work2survive.github.io/AE_JS_builder/?jsx=AE_Replace_Color_Emojis.jsx&autobuild=true)**

---

## Why This Tool Exists

Adobe After Effects text layers lack native rendering for color emoji font tables (`COLR/CPAL`, `SBIX`, `CBDT/CBLC`). When emojis are typed or pasted into After Effects text layers, they typically render as monochrome outlines, flat black glyphs, or missing-glyph fallback boxes (`□`).

**AE Replace Color Emojis** bridges the procedural text layout engine of **[AE-Text-Highlight](https://github.com/work2survive/AE-Text-Highlight)** with the vector emoji database of **[AE_Get_Emojis](https://github.com/work2survive/AE_Get_Emojis)**:
1. It analyzes the typography metrics (`fontSize`, `leading`, `tracking`, `boxTextPos`, `sourceRectAtTime`) and calculates sub-pixel emoji positions using delimiter-anchored advance measurement.
2. It substitutes monochrome glyphs with native vector After Effects Shape Layers (`ADBE Vector Group` + cubic Bézier `Shape` paths + `Fill` + `Stroke`), sourced from OpenMoji and Twemoji.

---

## What's New in v2.0.1

- 🌟 **+30% Optical Sizing (130% Default Multiplier)**: Emojis are automatically rendered 30% larger than font size by default to visually balance with font ascenders and capital heights.
- ⚡ **Silent & Fast Workflow**: Removed blocking modal alert dialogs upon successful replacement, enabling smooth keyboard shortcuts and uninterrupted production work.
- 🎛️ **Reorganized Visual UI Hierarchy**: Clean layout placing the primary **`✨ Replace Font Emojis with Color Emojis`** action button prominently at the base of the panel, with **`↺ Restore Text Layer`** and **`🧪 Create Demo Test`** neatly positioned side-by-side underneath.
- 📦 **Box-Text Word Wrapping & Right-Alignment Support**: Advanced paragraph text measurement handles multi-line word wrapping and right-aligned box text with zero glyph drift.
- 🧹 **Zero External Dependencies**: Self-contained ES3 JSX bundle with zero runtime disk reads or external JSON dependencies required.

---

### Key Features

### 1. Dual Replacement Engines

| Feature | 📐 Calculation Method (Recommended) | ✂️ Split Method (Decomposition) |
| :--- | :--- | :--- |
| **Original Text Layer** | **100% Intact and Active** (`enabled=true, guideLayer=false`) | Preserved as hidden guideline (`guideLayer=true, enabled=false`) |
| **Monochrome Glyph Hiding** | Native `ADBE Text Animator` ("Hide Monochrome Emojis") with Opacity = 0% on emoji character ranges | Emoji segments are removed from text layers entirely |
| **Text Spacing & Kerning** | Perfectly preserved; zero word-wrap or line-break shift | Segment text layers positioned using prefix advance measurement |
| **Layer Structure** | Single master Shape Layer or separate layers parented to text | Decomposed text boxes and shape layers parented to original |
| **Best Used For** | Static text, subtitles, kinetic text, keeping layer stacks tidy | Custom per-word animations, word transitions, granular control |

---

### 2. Unicode Emoji & Emoticon Detection

- **Unicode Emojis (Surrogate Pairs & BMP)**:
  - Smileys & People: `😃`, `🙂`, `😂`, `🥰`, `😎`, `🤔`, `😭`, `😡`, etc.
  - Symbols & Nature: `❤️`, `💔`, `🔥`, `🚀`, `✨`, `⭐`, `🎉`, `👍`, `👎`, `💯`, `⚠️`, `✅`, `☕`, etc.
  - Full support for Variation Selector-16 (`\uFE0F`).
- **Text Emoticons & Shortcodes**:
  - Automatically identifies text emoticons (e.g. `:D`, `:)`, `;-)`, `:P`, `<3`, `</3`, `XD`, `¯\_(ツ)_/¯`, `uwu`) and shortcodes (e.g. `:fire:`, `:thumbsup:`, `:100:`, `:rocket:`) using the Wikipedia Emoticons catalog.

---

### 3. Multi-Style Vector Support

Choose from 4 vector styles:
1. **OpenMoji Color** — Handcrafted full-color fills with clean black outline strokes.
2. **Twemoji Flat Color** — Clean modern flat design without black outline strokes.
3. **OpenMoji Flat** — Color fills with outlines removed.
4. **OpenMoji Black** — Line-art wireframe vectors.

---

### 4. Timeline Organization: Master vs. Separate Layers

- **📦 Single Master Shape Layer (Recommended)**: Groups all detected emojis into a single child Shape Layer parented to the text layer, keeping the composition timeline neat and uncluttered.
- **📑 Separate Shape Layer per Emoji**: Creates an independent Shape Layer for each detected emoji, allowing individual animation, parenting, or keyframing.

---

### 5. Procedural Effect Controls on Shape Layers

Each generated Shape Layer includes live effect controls:
- **`Emoji Size (px)`**: Master size in pixels (calibrated to text font size).
- **`Emoji Size Multiplier %`**: Interactive scaling relative to font size (default **130%** for optical balance).
- **`Outline Width %`**: Interactive stroke width adjustment for OpenMoji line art.
- **`Show Outlines`**: Checkbox to toggle line-art outlines on or off.
- **`Offset X` & `Offset Y`**: Fine-tune horizontal and vertical alignment.

---

### 6. Zero-Shift Anchor Alignment & Precomposition

- **Mandatory First-Action Anchor Alignment**: Aligns text layer anchor point based on justification with **0.00px visual shift** (powered by `AE-Align-AnchorPoint`).
- **Precomposition Option**: Optional zero-shift precomposition bundling the text layer and generated emoji layers into a clean precomp.
- **Full Undo / Restore System**: One-click restore button cleans up all created shape and text layers, restores the original text layer, and removes animators.

---

## Installation & Usage

1. Clone or download this repository:
   ```text
   AE-replace-color-emojis/
   ├── AE_Replace_Color_Emojis.jsx
   ├── emojis/
   │   ├── emoji_index.json
   │   ├── wikipedia_emoticons.json
   │   ├── openmoji_color.json
   │   ├── twemoji_color.json
   │   ├── openmoji_black.json
   │   └── emoji_schema.json
   ├── scripts/
   │   └── build_jsx.py
   └── tests/
       └── test_ae_replace_color_emojis.js
   ```
2. In Adobe After Effects, select **File → Scripts → Run Script File...** and choose `AE_Replace_Color_Emojis.jsx` (or place it in your `Scripts/ScriptUI Panels/` directory).
3. Select any Text Layer containing emojis in your active composition, configure your preferences in the panel, and click **`✨ Replace Font Emojis with Color Emojis`**.

---

## Testing

Run the automated integration test suite:
```bash
npm test
```

To re-build `AE_Replace_Color_Emojis.jsx` from the JSON databases:
```bash
npm run build
```

---

## Credits & Related Repositories

- **[AE-Text-Highlight](https://github.com/work2survive/AE-Text-Highlight)**: Text measurement, delimiter advance calculations, and dual-engine architecture.
- **[AE_Get_Emojis](https://github.com/work2survive/AE_Get_Emojis)**: Vector emoji indexing and shape layer construction.
- **[AE-Align-AnchorPoint](https://github.com/work2survive/AE-Align-AnchorPoint)**: Zero-shift anchor point alignment algorithm.
- **[AE_JS_builder](https://github.com/work2survive/AE_JS_builder)**: Browser-based ScriptUI and timeline simulator.
- **OpenMoji**: Vector graphics licensed under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).
- **Twemoji**: Vector graphics licensed under [CC BY 4.0](https://creativecommons.org/licenses/by-4.0/).
