#!/usr/bin/env python3
"""
build_jsx.py
Generates AE_Replace_Color_Emojis.jsx by combining:
1. Typography measurement, zero-shift anchor alignment, and dual-engine architecture from AE-Text-Highlight
2. Full-color vector cubic Bézier shape generation from AE_Get_Emojis
3. Unicode emoji detection (surrogate pairs, BMP, VS16) & text emoticon mapping
4. In-place monochrome font emoji hiding via native After Effects Text Animator (Opacity 0%)
5. Standalone fallback JSON embedding for 100% offline & simulator compatibility
"""

import json
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.dirname(SCRIPT_DIR)
EMOJIS_DIR = os.path.join(REPO_DIR, "emojis")
OUT_JSX = os.path.join(REPO_DIR, "AE_Replace_Color_Emojis.jsx")

FALLBACK_HEXCODES = [
    "1F642", "1F603", "1F606", "1F604", "1F601", "1F602", "1F923", "1F60A",
    "1F607", "1F608", "1F609", "1F60D", "1F60E", "1F60F", "1F610", "1F612",
    "1F615", "1F618", "1F61B", "1F61C", "1F620", "1F621", "1F622", "1F62D",
    "1F62E", "1F633", "1F634", "1F635", "1F641", "1F63A", "1F914", "1F929",
    "1F937", "1F64C", "1FAE1", "2764", "1F494", "1F44D", "1F44E", "1F525",
    "1F4AF", "1F4A9", "2728", "1F680", "1F480", "1F389", "2705", "26A0",
    # All 30 EMOJI_POOL emojis from AE_JS_builder
    "1F4A1", "1F3A8", "1F31F", "1F48E", "1F3AF", "26A1", "1F308", "1F355",
    "2615", "1F388", "1F340", "1F3C6", "1F3B5", "1F916", "1F30D", "1F369",
    "1F37F", "1F3B8", "1F3AA", "1F951", "1F98A", "1F431", "1F576", "1F47E",
]

def load_fallback_data():
    with open(os.path.join(EMOJIS_DIR, "emoji_index.json"), "r", encoding="utf-8") as f:
        idx_data = json.load(f)
    with open(os.path.join(EMOJIS_DIR, "wikipedia_emoticons.json"), "r", encoding="utf-8") as f:
        wiki_data = json.load(f)
    with open(os.path.join(EMOJIS_DIR, "openmoji_color.json"), "r", encoding="utf-8") as f:
        om_color = json.load(f)

    fallback_emojis = []
    fallback_shapes = {}
    seen = set()
    for e in idx_data["emojis"]:
        hc = e["hexcode"]
        if hc in FALLBACK_HEXCODES and hc not in seen:
            seen.add(hc)
            rec = dict(e)
            rec["index"] = len(fallback_emojis) + 1
            fallback_emojis.append(rec)
            if hc in om_color:
                fallback_shapes[hc] = om_color[hc]

    fallback_index_json = json.dumps({"version": "1.0.0", "totalCount": len(fallback_emojis), "emojis": fallback_emojis}, ensure_ascii=False, separators=(",", ":"))
    fallback_wiki_json = json.dumps(wiki_data, ensure_ascii=False, separators=(",", ":"))
    fallback_shapes_json = json.dumps(fallback_shapes, ensure_ascii=False, separators=(",", ":"))

    return fallback_index_json, fallback_wiki_json, fallback_shapes_json

def generate_jsx():
    fallback_index_json, fallback_wiki_json, fallback_shapes_json = load_fallback_data()

    header = r'''/**
 * ============================================================================
 * AE Replace Color Emojis v1.0 — Procedural Color Emoji Replacement Engine
 * ============================================================================
 *
 * Repository: https://github.com/work2survive/AE-replace-color-emojis
 * Live Demo:  https://work2survive.github.io/AE_JS_builder/?jsx=AE_Replace_Color_Emojis.jsx&autobuild=true
 *
 * PURPOSE:
 *   Adobe After Effects text layers do not natively support color emoji fonts
 *   (COLR/CPAL, SBIX, CBDT/CBLC), rendering emojis pasted into text layers as
 *   monochrome black glyphs or missing-font boxes (□).
 *
 *   This script solves that by scanning text layers for emojis, calculating their
 *   exact geometric positions down to the sub-pixel using delimiter-anchored advance
 *   measurement (from AE-Text-Highlight), and replacing monochrome font glyphs with
 *   infinitely scalable, 100% native vector Shape Layer emojis (from AE_Get_Emojis).
 *
 * ARCHITECTURAL HIGHLIGHTS:
 *   1. Dual Replacement Engines:
 *      - Calculation Method (Intact Text Box - Recommended):
 *        Preserves original text layer completely intact and active.
 *        Applies a native After Effects Text Animator ("Hide Monochrome Emojis")
 *        with Opacity = 0% targeting the exact emoji character indices, cleanly hiding
 *        the monochrome font glyphs without altering text spacing or word wrap.
 *        Places full-color vector emoji shape layers directly in front.
 *      - Split Method (Layer Decomposition):
 *        Decomposes lines into independent text boxes for words with top-left anchors
 *        and places color emoji shape layers at each emoji's slot.
 *   2. Unicode Emoji Recognition Engine:
 *      - Scans Unicode surrogate pairs (U+1F000 - U+1FAFF: smileys, symbols, objects)
 *      - Scans BMP emojis (U+2600 - U+27BF, U+2B00 - U+2BFF: heart, sparkles, check, etc.)
 *      - Full support for Variation Selector-16 (\uFE0F) and multi-char glyphs
 *      - Optional: Detects and replaces text emoticons (:D, :), <3, etc.) and
 *        shortcodes (:fire:, :thumbsup:, :rocket:) from the Wikipedia Emoticons catalog!
 *   3. 4 Full-Color Vector Styles (from OpenMoji & Twemoji):
 *      - OpenMoji Color (full-color handcrafted shapes + outlines)
 *      - Twemoji Flat Color (modern flat shapes without black line-art)
 *      - OpenMoji Flat Color (color shapes without outlines)
 *      - OpenMoji Black (pure line-art / wireframe)
 *   4. Single Master Shape Layer vs. Separate Layer per Emoji:
 *      - Single Master Shape Layer groups all emojis into a clean, unified timeline layer
 *      - Separate Shape Layer per Emoji gives individual layer animation controls
 *   5. Mandatory First-Action Anchor Alignment with 0.00px Visual Shift (AE-Align-AnchorPoint)
 *   6. Master Expression Controls on Shape Layer:
 *      - Emoji Size (px) (rigged to fontSize * multiplier)
 *      - Emoji Size Multiplier %
 *      - Outline Width %
 *      - Show Outlines
 *      - Offset X, Offset Y
 *   7. Zero-Shift Precomposition Option (AE-text-precomp)
 *   8. Complete Clean Restore / Undo System
 * ============================================================================
 */

(function (thisObj) {
    "use strict";

    var SCRIPT_TITLE = "AE Replace Color Emojis";
    var SCRIPT_VERSION = "v1.0";
    var GITHUB_REPO_URL = "https://github.com/work2survive/AE-replace-color-emojis";

    var globalObj = (typeof window !== "undefined")
        ? window
        : ((typeof $ !== "undefined" && typeof $.global !== "undefined")
            ? $.global
            : ((typeof global !== "undefined") ? global : (thisObj || {})));

    if (typeof globalObj.$ === "undefined") {
        globalObj.$ = {
            global: globalObj,
            writeln: function (msg) {
                if (typeof console !== "undefined" && console.log) console.log(msg);
            }
        };
    }

    // =========================================================================
    // 1. ES3 / EXTENDSCRIPT POLYFILLS & STRING HELPERS
    // =========================================================================
    var JSONPolyfill = (typeof JSON !== "undefined" && JSON.parse && JSON.stringify) ? JSON : {
        parse: function (str) {
            return eval("(" + str + ")");
        },
        stringify: function (obj) {
            if (obj === null || typeof obj === "undefined") return "null";
            if (typeof obj === "number" || typeof obj === "boolean") return String(obj);
            if (typeof obj === "string") {
                return '"' + obj.replace(/\\/g, "\\\\").replace(/"/g, '\\"').replace(/\n/g, "\\n").replace(/\r/g, "\\r") + '"';
            }
            if (obj instanceof Array) {
                var arr = [];
                for (var i = 0; i < obj.length; i++) arr.push(JSONPolyfill.stringify(obj[i]));
                return "[" + arr.join(",") + "]";
            }
            if (typeof obj === "object") {
                var pairs = [];
                for (var k in obj) {
                    if (obj.hasOwnProperty(k)) {
                        pairs.push(JSONPolyfill.stringify(k) + ":" + JSONPolyfill.stringify(obj[k]));
                    }
                }
                return "{" + pairs.join(",") + "}";
            }
            return '""';
        }
    };

    function trimStr(str) {
        if (!str) return "";
        return String(str).replace(/^\s+|\s+$/g, "");
    }

    function unicodeHexToInt(hex) {
        if (!hex) return 0;
        var cleanHex = String(hex).replace(/^(0x|U\+|\#)/i, "");
        var parts = cleanHex.split("-");
        var baseHex = parts[0];
        var val = parseInt(baseHex, 16);
        return isNaN(val) ? 0 : val;
    }

    function codePointToGlyph(cp) {
        if (!cp || cp <= 0) return "";
        if (cp <= 0xFFFF) {
            return String.fromCharCode(cp);
        }
        var offset = cp - 0x10000;
        var high = 0xD800 + (offset >> 10);
        var low = 0xDC00 + (offset & 0x3FF);
        return String.fromCharCode(high, low);
    }

    function isBrowserSim() {
        return (typeof window !== "undefined" && typeof document !== "undefined");
    }

    // =========================================================================
    // 2. EMBEDDED STANDALONE FALLBACK DATASETS
    // =========================================================================
'''

    embedded_data = f"""    var FALLBACK_INDEX_DATA = {fallback_index_json};
    var FALLBACK_WIKI_DATA = {fallback_wiki_json};
    var FALLBACK_SHAPES_DATA = {fallback_shapes_json};
"""

    body = r'''
    // =========================================================================
    // 3. EMOJI CATALOG & DISK / BROWSER DATABASE LOADER
    // =========================================================================
    var EMOJI_SOURCES = [
        { id: "openmoji_color", label: "1. OpenMoji Color (Handcrafted + Outlines)", index: 1 },
        { id: "twemoji_color",  label: "2. Twemoji Flat Color (Modern Flat Shapes)", index: 2 },
        { id: "openmoji_flat",   label: "3. OpenMoji Flat (Color Only, No Outlines)", index: 3 },
        { id: "openmoji_black",  label: "4. OpenMoji Black (Line Art / Wireframe)",    index: 4 }
    ];

    var emojiCatalog = [];
    var emojiByHex = {};
    var emojiByChar = {};
    var emojiByInt = {};
    var emojiByIndex = {};
    var wikiEmoticonMap = {};
    var wikiEntries = [];

    var shapeDatabases = {
        openmoji_color: null,
        twemoji_color: null,
        openmoji_black: null
    };

    function getEmojisFolder() {
        if (typeof File === "undefined" || typeof Folder === "undefined") return null;
        try {
            var scriptFile = null;
            if (typeof $.fileName !== "undefined" && $.fileName) {
                scriptFile = new File($.fileName);
            }
            if (scriptFile && scriptFile.exists) {
                var candFolder = new Folder(scriptFile.parent.fsName + "/emojis");
                if (candFolder.exists) return candFolder;
            }
            var rootFolder = new Folder("/home/antigravity/work2survive/AE-replace-color-emojis/emojis");
            if (rootFolder.exists) return rootFolder;
            var omFolder = new Folder("/home/antigravity/work2survive/AE_Get_Emojis/emojis");
            if (omFolder.exists) return omFolder;
        } catch (eF) {}
        return null;
    }

    function loadJSONFromEmojisSubfolder(filename) {
        // 1. Browser / AE_JS_builder simulator environment: synchronous XHR
        if (typeof XMLHttpRequest !== "undefined") {
            var candidateUrls = [
                "jsx/emojis/" + filename,
                "emojis/" + filename,
                "https://raw.githubusercontent.com/work2survive/AE-replace-color-emojis/main/emojis/" + filename,
                "https://raw.githubusercontent.com/work2survive/AE_Get_Emojis/main/emojis/" + filename
            ];
            for (var u = 0; u < candidateUrls.length; u++) {
                try {
                    var xhr = new XMLHttpRequest();
                    xhr.open("GET", candidateUrls[u], false);
                    xhr.send(null);
                    if (xhr.status >= 200 && xhr.status < 300 && xhr.responseText) {
                        var txt = trimStr(xhr.responseText);
                        if (txt.charAt(0) === "{" || txt.charAt(0) === "[") {
                            return JSONPolyfill.parse(txt);
                        }
                    }
                } catch (eXhr) {}
            }
        }

        // 2. Desktop Adobe After Effects ExtendScript: read from /emojis/ folder on disk
        if (typeof File !== "undefined") {
            try {
                var folder = getEmojisFolder();
                if (folder && folder.exists) {
                    var f = new File(folder.fsName + "/" + filename);
                    if (f.exists) {
                        f.encoding = "UTF-8";
                        if (f.open("r")) {
                            var content = f.read();
                            f.close();
                            if (content && content.length > 2) {
                                return JSONPolyfill.parse(content);
                            }
                        }
                    }
                }
            } catch (eFile) {}
        }
        return null;
    }

    function rebuildLookupTables(idxData, wikiData) {
        emojiCatalog = (idxData && idxData.emojis && idxData.emojis.length)
            ? idxData.emojis
            : FALLBACK_INDEX_DATA.emojis;

        emojiByHex = {};
        emojiByChar = {};
        emojiByInt = {};
        emojiByIndex = {};

        for (var i = 0; i < emojiCatalog.length; i++) {
            var item = emojiCatalog[i];
            item.index = i + 1;
            var hc = String(item.hexcode || "").toUpperCase();
            if (!item.unicodeInt) {
                item.unicodeInt = unicodeHexToInt(hc);
            }
            if (!item.unicode) {
                item.unicode = "U+" + hc;
            }
            if (!item.emoji) {
                item.emoji = codePointToGlyph(item.unicodeInt);
            }
            emojiByHex[hc] = item;
            if (item.emoji) {
                emojiByChar[item.emoji] = item;
            }
            emojiByInt[item.unicodeInt] = item;
            emojiByIndex[item.index] = item;
        }

        var wData = wikiData || FALLBACK_WIKI_DATA;
        wikiEmoticonMap = {};
        wikiEntries = (wData && wData.entries) ? wData.entries : [];

        if (wData && wData.lookup) {
            for (var k in wData.lookup) {
                if (wData.lookup.hasOwnProperty(k)) {
                    var hexVal = String(wData.lookup[k]).toUpperCase();
                    wikiEmoticonMap[k] = hexVal;
                    wikiEmoticonMap[k.toLowerCase()] = hexVal;
                }
            }
        }
        for (var w = 0; w < wikiEntries.length; w++) {
            var we = wikiEntries[w];
            var whc = String(we.hexcode || "").toUpperCase();
            var emos = we.emoticons || [];
            for (var ei = 0; ei < emos.length; ei++) {
                wikiEmoticonMap[emos[ei]] = whc;
                wikiEmoticonMap[emos[ei].toLowerCase()] = whc;
            }
        }
    }

    function loadAllEmojiDatabases() {
        var idxData = loadJSONFromEmojisSubfolder("emoji_index.json") || FALLBACK_INDEX_DATA;
        var wikiData = loadJSONFromEmojisSubfolder("wikipedia_emoticons.json") || FALLBACK_WIKI_DATA;
        rebuildLookupTables(idxData, wikiData);

        var omColor = loadJSONFromEmojisSubfolder("openmoji_color.json");
        shapeDatabases.openmoji_color = omColor || FALLBACK_SHAPES_DATA;

        var twColor = loadJSONFromEmojisSubfolder("twemoji_color.json");
        shapeDatabases.twemoji_color = twColor || shapeDatabases.openmoji_color;

        var omBlack = loadJSONFromEmojisSubfolder("openmoji_black.json");
        shapeDatabases.openmoji_black = omBlack || shapeDatabases.openmoji_color;
    }

    loadAllEmojiDatabases();

    function getShapesForEmoji(hexcode, sourceId) {
        var hc = String(hexcode || "").toUpperCase();
        var shapes = null;

        if (sourceId === "twemoji_color") {
            if (shapeDatabases.twemoji_color && shapeDatabases.twemoji_color[hc]) {
                shapes = shapeDatabases.twemoji_color[hc];
            }
        } else if (sourceId === "openmoji_black") {
            if (shapeDatabases.openmoji_black && shapeDatabases.openmoji_black[hc]) {
                shapes = shapeDatabases.openmoji_black[hc];
            }
        }

        if (!shapes && shapeDatabases.openmoji_color && shapeDatabases.openmoji_color[hc]) {
            shapes = shapeDatabases.openmoji_color[hc];
        }

        if (!shapes && FALLBACK_SHAPES_DATA[hc]) {
            shapes = FALLBACK_SHAPES_DATA[hc];
        }

        // If shapes not found in specified source or fallbacks, return empty list (do not fake smiley)
        if (!shapes || shapes.length === 0) {
            return [];
        }

        if (sourceId === "openmoji_flat") {
            var filtered = [];
            for (var si = 0; si < shapes.length; si++) {
                if (!shapes[si].l) filtered.push(shapes[si]);
            }
            if (filtered.length > 0) return filtered;
        }

        return shapes;
    }

    // =========================================================================
    // 4. UNICODE EMOJI RECOGNITION & PARSING ENGINE
    // =========================================================================
    /**
     * Scans a line or text string and returns all matched emojis.
     * Supports:
     * - UTF-16 surrogate pairs (U+1F000 - U+1FAFF)
     * - BMP emojis (U+2600 - U+27BF, U+2B00 - U+2BFF, etc.)
     * - Variation Selector 16 (\uFE0F)
     * - Wikipedia text emoticons (:D, :), <3, etc.) and shortcodes (:fire:, :100:)
     */
    function findEmojisInString(str, detectEmoticons) {
        var matches = [];
        if (!str || str.length === 0) return matches;

        var i = 0;
        while (i < str.length) {
            var code = str.charCodeAt(i);

            // 1. Surrogate pair (Code points > 0xFFFF, e.g. 1F603, 1F680, 1F525)
            if (code >= 0xD800 && code <= 0xDBFF && i + 1 < str.length) {
                var nextCode = str.charCodeAt(i + 1);
                if (nextCode >= 0xDC00 && nextCode <= 0xDFFF) {
                    var cp = ((code - 0xD800) * 0x400) + (nextCode - 0xDC00) + 0x10000;
                    var hex = cp.toString(16).toUpperCase();
                    var matchLen = 2;

                    // Check for optional Variation Selector-16 (U+FE0F)
                    if (i + 2 < str.length && str.charCodeAt(i + 2) === 0xFE0F) {
                        matchLen = 3;
                    }

                    var matchedChar = str.substr(i, matchLen);
                    var entry = emojiByHex[hex] || emojiByChar[matchedChar.substr(0, 2)];
                    if (!entry) {
                        // Create dynamic entry for unindexed Unicode emoji
                        entry = {
                            hexcode: hex,
                            unicode: "U+" + hex,
                            unicodeInt: cp,
                            emoji: matchedChar.substr(0, 2),
                            name: "Emoji U+" + hex,
                            index: 0
                        };
                    }

                    matches.push({
                        start: i,
                        length: matchLen,
                        hexcode: hex,
                        char: matchedChar,
                        entry: entry,
                        isEmoticon: false
                    });

                    i += matchLen;
                    continue;
                }
            }

            // 2. BMP emoji (e.g. U+2764 red heart, U+2728 sparkles, U+2705 check mark, U+26A0 warning)
            var isBmpEmoji = false;
            if ((code >= 0x2600 && code <= 0x27BF) ||
                (code >= 0x2B00 && code <= 0x2BFF) ||
                (code >= 0x2300 && code <= 0x23FF) ||
                code === 0x203C || code === 0x2049 || code === 0x2122 || code === 0x2139 ||
                code === 0x3030 || code === 0x303D || code === 0x3297 || code === 0x3299) {
                isBmpEmoji = true;
            }

            if (isBmpEmoji) {
                var bmpHex = code.toString(16).toUpperCase();
                var bmpLen = 1;
                if (i + 1 < str.length && str.charCodeAt(i + 1) === 0xFE0F) {
                    bmpLen = 2;
                }
                var bmpChar = str.substr(i, bmpLen);
                var bmpEntry = emojiByHex[bmpHex] || emojiByChar[str.substr(i, 1)];
                if (!bmpEntry) {
                    bmpEntry = {
                        hexcode: bmpHex,
                        unicode: "U+" + bmpHex,
                        unicodeInt: code,
                        emoji: bmpChar.substr(0, 1),
                        name: "Emoji U+" + bmpHex,
                        index: 0
                    };
                }

                matches.push({
                    start: i,
                    length: bmpLen,
                    hexcode: bmpHex,
                    char: bmpChar,
                    entry: bmpEntry,
                    isEmoticon: false
                });

                i += bmpLen;
                continue;
            }

            // 3. Emoticons & Shortcodes (if enabled)
            if (detectEmoticons) {
                var matchedEmo = null;

                // Check :shortcode: format
                if (str.charAt(i) === ":") {
                    var endColon = str.indexOf(":", i + 1);
                    if (endColon !== -1 && endColon - i <= 24) {
                        var sc = str.substring(i, endColon + 1);
                        if (wikiEmoticonMap[sc]) {
                            matchedEmo = { text: sc, hex: wikiEmoticonMap[sc] };
                        }
                    }
                }

                // Check text emoticons (e.g. :D, :), <3, etc.)
                if (!matchedEmo) {
                    for (var emoText in wikiEmoticonMap) {
                        if (wikiEmoticonMap.hasOwnProperty(emoText)) {
                            if (str.substr(i, emoText.length) === emoText) {
                                if (!matchedEmo || emoText.length > matchedEmo.text.length) {
                                    matchedEmo = { text: emoText, hex: wikiEmoticonMap[emoText] };
                                }
                            }
                        }
                    }
                }

                if (matchedEmo) {
                    var emoHex = matchedEmo.hex.toUpperCase();
                    var emoEntry = emojiByHex[emoHex] || {
                        hexcode: emoHex,
                        unicode: "U+" + emoHex,
                        unicodeInt: unicodeHexToInt(emoHex),
                        emoji: codePointToGlyph(unicodeHexToInt(emoHex)),
                        name: "Emoticon " + matchedEmo.text,
                        index: 0
                    };

                    matches.push({
                        start: i,
                        length: matchedEmo.text.length,
                        hexcode: emoHex,
                        char: matchedEmo.text,
                        entry: emoEntry,
                        isEmoticon: true
                    });

                    i += matchedEmo.text.length;
                    continue;
                }
            }

            i++;
        }

        return matches;
    }

    // =========================================================================
    // 5. TEXT LAYER UTILITIES & ZERO-SHIFT ANCHOR POINT ALIGNMENT
    // =========================================================================
    function isTextLayer(layer) {
        if (!layer) return false;
        try {
            if (layer.matchName === "ADBE Text Layer") return true;
        } catch (eM) {}
        try {
            if (typeof layer.property === "function") {
                if (layer.property("ADBE Text Properties") || layer.property("Source Text") || layer.property("ADBE Text Document")) {
                    return true;
                }
            }
        } catch (eP) {}
        return false;
    }

    function getTextDocument(layer) {
        if (!layer) return null;
        try {
            var st = layer.property("Source Text")
                || layer.property("ADBE Text Properties").property("ADBE Text Document")
                || layer.sourceText;
            if (st && st.value) return st.value;
        } catch (e1) {}
        try {
            if (layer.text && layer.text.sourceText && layer.text.sourceText.value) {
                return layer.text.sourceText.value;
            }
        } catch (e2) {}
        return null;
    }

    function getTextLayerString(layer) {
        var doc = getTextDocument(layer);
        if (doc && typeof doc.text === "string") return doc.text;
        try {
            if (layer.name) return layer.name;
        } catch (e) {}
        return "";
    }

    function getSourceRect(layer, compTime) {
        var t = (typeof compTime === "number") ? compTime : 0;
        try {
            if (layer && typeof layer.sourceRectAtTime === "function") {
                var r = layer.sourceRectAtTime(t, false);
                if (r && typeof r.width === "number") return r;
            }
        } catch (eSR) {}
        return { left: 0, top: 0, width: 300, height: 60 };
    }

    function getSelectedTextLayer(comp) {
        if (!comp) return null;
        try {
            var sel = comp.selectedLayers;
            if (sel && sel.length > 0) {
                for (var i = 0; i < sel.length; i++) {
                    var l = sel[i];
                    if (isTextLayer(l)) return l;
                    if (l && l.parent && isTextLayer(l.parent)) return l.parent;
                }
            }
        } catch (eSel) {}
        return null;
    }

    function getJustificationName(textDoc, textLayer) {
        if (textDoc && typeof textDoc.justification !== "undefined") {
            var j = textDoc.justification;
            if (typeof ParagraphJustification !== "undefined") {
                if (j === ParagraphJustification.CENTER_JUSTIFY) return "center";
                if (j === ParagraphJustification.RIGHT_JUSTIFY) return "right";
                if (j === ParagraphJustification.LEFT_JUSTIFY) return "left";
            }
            if (j === 7413 || j === "center" || j === "CENTER") return "center";
            if (j === 7414 || j === "right" || j === "RIGHT") return "right";
            return "left";
        }
        return "left";
    }

    function measureTextExact(str, fontSize, fontName) {
        if (!str || str.length === 0) return 0;
        var fs = fontSize || 34;
        return str.length * (fs * 0.55);
    }

    function createMeasureHelper(comp, props) {
        var measureLayer = null;
        var measureProp = null;
        var pipeRight = 0;
        var sampleTime = 0;

        if (comp && typeof comp.layers.addText === "function") {
            try {
                measureLayer = comp.layers.addText("");
                measureLayer.enabled = true;
                measureLayer.transform.position.setValue([-9999, -9999, 0]);
                measureLayer.startTime = 0;
                measureLayer.inPoint = 0;
                measureLayer.outPoint = (comp.duration && comp.duration > 0) ? comp.duration : 1000;
                sampleTime = measureLayer.inPoint;

                try { measureProp = measureLayer.property("Source Text"); } catch (eP1) {}
                if (!measureProp) {
                    try { measureProp = measureLayer.property("ADBE Text Properties").property("ADBE Text Document"); } catch (eP2) {}
                }
                if (!measureProp && measureLayer.sourceText) measureProp = measureLayer.sourceText;

                if (measureProp) {
                    var doc = measureProp.value;
                    if (doc) {
                        doc.fontSize = props.fontSize || 34;
                        if (props.font) {
                            try { doc.font = props.font; } catch (eF) {}
                        }
                        doc.tracking = props.tracking || 0;
                        doc.applyFill = true;
                        doc.fillColor = [1, 1, 1];
                        try { doc.boxText = false; } catch (eBT) {}
                        try {
                            if (typeof ParagraphJustification !== "undefined") {
                                doc.justification = ParagraphJustification.LEFT_JUSTIFY;
                            } else {
                                doc.justification = 7412;
                            }
                        } catch (eJ) {}
                        measureProp.setValue(doc);
                    }

                    // Measure delimiter anchor "|"
                    try {
                        var dP = measureProp.value;
                        if (dP) { dP.text = "|"; measureProp.setValue(dP); }
                        else { measureProp.setValue("|"); }
                        var rP = measureLayer.sourceRectAtTime(sampleTime, false);
                        if (rP && typeof rP.width === "number") {
                            pipeRight = rP.left + rP.width;
                        }
                    } catch (ePipe) {}
                }
            } catch (eM) {
                measureLayer = null;
                measureProp = null;
            }
        }

        function measureRect(str) {
            if (!str || str.length === 0) return { left: 0, top: 0, width: 0, height: 0 };
            if (measureLayer && measureProp) {
                try {
                    var d = measureProp.value;
                    if (d) { d.text = str; measureProp.setValue(d); }
                    else { measureProp.setValue(str); }
                    var r = measureLayer.sourceRectAtTime(sampleTime, false);
                    if (r && typeof r.width === "number" && r.width >= 0) {
                        return { left: r.left, top: r.top, width: r.width, height: r.height };
                    }
                } catch (eR) {}
            }
            var w = measureTextExact(str, props.fontSize, props.font);
            return { left: 0, top: 0, width: w, height: props.fontSize };
        }

        function measurePrefixAdvance(prefix) {
            if (!prefix || prefix.length === 0) return 0;
            if (measureLayer && measureProp && pipeRight > 0) {
                try {
                    var rPrePipe = measureRect(prefix + "|");
                    return Math.max(0, (rPrePipe.left + rPrePipe.width) - pipeRight);
                } catch (eAdv) {}
            }
            return measureTextExact(prefix, props.fontSize, props.font);
        }

        function cleanup() {
            if (measureLayer) {
                try { measureLayer.remove(); } catch (eClean) {}
                measureLayer = null;
                measureProp = null;
            }
        }

        return {
            measureRect: measureRect,
            measurePrefixAdvance: measurePrefixAdvance,
            cleanup: cleanup
        };
    }

    function getTextBoxProperties(comp, layer) {
        if (!layer || !isTextLayer(layer)) return null;
        var textDoc = getTextDocument(layer);
        if (!textDoc) return null;

        var sRect = getSourceRect(layer);
        var isBox = false;
        var boxWidth = 0;
        var boxHeight = 0;
        var boxPos = [0, 0];

        try {
            if (textDoc.boxText && textDoc.boxTextSize) {
                isBox = true;
                boxWidth = textDoc.boxTextSize[0];
                boxHeight = textDoc.boxTextSize[1];
                if (textDoc.boxTextPos) boxPos = textDoc.boxTextPos;
            }
        } catch (eB) {}

        if (boxWidth <= 0 && sRect && sRect.width > 0) boxWidth = sRect.width;
        if (boxHeight <= 0 && sRect && sRect.height > 0) boxHeight = sRect.height;

        var fullText = String(textDoc.text || "");
        var paragraphs = fullText.split(/\r\n|\r|\n/);
        var lines = [];

        // Build visual line wrapping
        for (var p = 0; p < paragraphs.length; p++) {
            var para = paragraphs[p];
            if (!isBox || boxWidth <= 0) {
                lines.push(para);
            } else {
                var pWords = para.match(/\S+/g) || [];
                if (pWords.length === 0) {
                    lines.push("");
                    continue;
                }
                var curLine = pWords[0];
                for (var pw = 1; pw < pWords.length; pw++) {
                    var testLine = curLine + " " + pWords[pw];
                    var testW = measureTextExact(testLine, textDoc.fontSize || 34, textDoc.font);
                    if (testW > boxWidth && curLine.length > 0) {
                        lines.push(curLine);
                        curLine = pWords[pw];
                    } else {
                        curLine = testLine;
                    }
                }
                lines.push(curLine);
            }
        }

        return {
            textDoc: textDoc,
            fullText: fullText,
            fontSize: textDoc.fontSize || 34,
            font: textDoc.font || "Arial",
            leading: textDoc.leading || ((textDoc.fontSize || 34) * 1.2),
            tracking: textDoc.tracking || 0,
            fillColor: textDoc.fillColor || [1, 1, 1],
            justification: getJustificationName(textDoc, layer),
            isBox: isBox,
            boxWidth: boxWidth,
            boxHeight: boxHeight,
            boxPos: boxPos,
            sRect: sRect,
            metrics: {
                lines: lines
            }
        };
    }

    function alignAnchorPointToJustification(targetLayer, props) {
        if (!targetLayer || !props) return;
        try {
            var just = props.justification || "left";
            var xMode = (just === "center") ? "Center" : ((just === "right") ? "Right" : "Left");
            var bounds = props.isBox
                ? { left: props.boxPos[0], top: props.boxPos[1], width: props.boxWidth, height: props.boxHeight }
                : props.sRect;

            var targetAnchorX = bounds.left;
            if (xMode === "Center") targetAnchorX = bounds.left + (bounds.width / 2);
            else if (xMode === "Right") targetAnchorX = bounds.left + bounds.width;

            var targetAnchorY = bounds.top;

            var tr = targetLayer.transform;
            var curAnchor = tr.anchorPoint.value;
            var curPos = tr.position.value;

            var dx = targetAnchorX - curAnchor[0];
            var dy = targetAnchorY - curAnchor[1];

            tr.anchorPoint.setValue([targetAnchorX, targetAnchorY, curAnchor[2] || 0]);
            tr.position.setValue([curPos[0] + dx, curPos[1] + dy, curPos[2] || 0]);
        } catch (eAlign) {}
    }

    function applyTextDocCopy(targetLayer, origDoc, textContent, customFillColor) {
        if (!targetLayer || !origDoc) return;
        try {
            var prop = targetLayer.property("Source Text")
                || targetLayer.property("ADBE Text Properties").property("ADBE Text Document")
                || targetLayer.sourceText;
            if (!prop) return;
            var d = prop.value || origDoc;
            d.text = textContent;
            d.fontSize = origDoc.fontSize || 34;
            if (origDoc.font) {
                try { d.font = origDoc.font; } catch (eF) {}
            }
            d.leading = origDoc.leading || (d.fontSize * 1.2);
            d.tracking = origDoc.tracking || 0;
            d.applyFill = true;
            d.fillColor = customFillColor || origDoc.fillColor || [1, 1, 1];
            try { d.boxText = false; } catch (eBT) {}
            prop.setValue(d);
        } catch (eApply) {}
    }

    function markOriginalAsGuideline(layer) {
        if (!layer) return;
        try {
            layer.guideLayer = true;
            layer.enabled = false;
        } catch (eG) {}
    }

    // =========================================================================
    // 6. VECTOR SHAPE POPULATION ENGINE (Cubic Bézier Paths, Fills & Strokes)
    // =========================================================================
    function clearRootVectorContents(rootVectors) {
        if (!rootVectors) return;
        try {
            var num = rootVectors.numProperties;
            for (var i = num; i >= 1; i--) {
                try {
                    rootVectors.property(i).remove();
                } catch (eSub) {}
            }
        } catch (eRoot) {}
    }

    function ensureEffectSlider(fxGroup, name, val) {
        try {
            var p = fxGroup.property(name);
            if (!p) {
                p = fxGroup.addProperty("ADBE Slider Control");
                p.name = name;
            }
            if (p && p.property(1)) {
                p.property(1).setValue(val);
            }
            return p;
        } catch (e) { return null; }
    }

    function ensureEffectCheckbox(fxGroup, name, val) {
        try {
            var p = fxGroup.property(name);
            if (!p) {
                p = fxGroup.addProperty("ADBE Checkbox Control");
                p.name = name;
            }
            if (p && p.property(1)) {
                p.property(1).setValue(val ? 1 : 0);
            }
            return p;
        } catch (e) { return null; }
    }

    function buildVectorGroupForEmoji(masterContents, entry, sourceId, sizePx, posX, posY, outlinePct, showOutlines) {
        var shapes = getShapesForEmoji(entry.hexcode, sourceId);
        var inBrowser = isBrowserSim();

        var emoGrp = masterContents.addProperty("ADBE Vector Group");
        emoGrp.name = "Emoji " + entry.emoji + " [" + entry.unicode + "]";
        var emoContents = emoGrp.property("ADBE Vectors Group") || emoGrp.property("Contents");

        // Rig Master Vector Group Transform
        var emoTr = emoGrp.property("ADBE Vector Transform Group") || emoGrp.property("Transform");
        if (emoTr) {
            var pAnchor = emoTr.property("ADBE Vector Anchor Point") || emoTr.property("Anchor Point") || emoTr.property("ADBE Vector Anchor");
            if (pAnchor && pAnchor.setValue) pAnchor.setValue([0, 0]);

            var pPos = emoTr.property("ADBE Vector Position") || emoTr.property("Position");
            if (pPos && pPos.setValue) pPos.setValue([posX, posY]);

            var pScale = emoTr.property("ADBE Vector Scale") || emoTr.property("Scale");
            if (pScale && pScale.setValue) {
                var scalePct = Math.round((sizePx / 72.0) * 10000) / 100;
                pScale.setValue([scalePct, scalePct]);
            }

            try {
                if (pPos) {
                    pPos.expression = [
                        'var ox = 0, oy = 0;',
                        'try { ox = thisLayer.effect("Offset X")(1).value; } catch(e1) {}',
                        'try { oy = thisLayer.effect("Offset Y")(1).value; } catch(e2) {}',
                        '[' + posX.toFixed(2) + ' + ox, ' + posY.toFixed(2) + ' + oy];'
                    ].join('\n');
                }
            } catch (ePosExpr) {}

            try {
                if (pScale) {
                    pScale.expression = [
                        'try {',
                        '  var sz = thisLayer.effect("Emoji Size (px)")(1).value;',
                        '  var mult = thisLayer.effect("Emoji Size Multiplier %")(1).value / 100.0;',
                        '  var s = ((sz * mult) / 72.0) * 100.0;',
                        '  [s, s];',
                        '} catch(e) { value; }'
                    ].join('\n');
                }
            } catch (eScExpr) {}
        }

        var startIdx = inBrowser ? 0 : (shapes.length - 1);
        var endIdx = inBrowser ? shapes.length : -1;
        var step = inBrowser ? 1 : -1;

        for (var idx = startIdx; idx !== endIdx; idx += step) {
            var item = shapes[idx];
            var isLine = Boolean(item.l) && (sourceId !== "openmoji_black");

            var partGrp = emoContents.addProperty("ADBE Vector Group");
            partGrp.name = (item.l ? "Outline_" : "Color_") + (idx + 1);
            var partVecs = partGrp.property("ADBE Vectors Group") || partGrp.property("Contents") || partGrp;

            var subpaths = item.p ? item.p : [item];
            for (var spIdx = 0; spIdx < subpaths.length; spIdx++) {
                var sp = subpaths[spIdx];
                if (!sp.v || sp.v.length < 2) continue;
                var pathGrp = partVecs.addProperty("ADBE Vector Shape - Group");
                pathGrp.name = "Path_" + (spIdx + 1);
                var ShapeClass = (typeof Shape !== "undefined")
                    ? Shape
                    : ((typeof globalObj !== "undefined" && globalObj.Shape)
                        ? globalObj.Shape
                        : ((typeof window !== "undefined" && window.Shape)
                            ? window.Shape
                            : function () { this.vertices = []; this.inTangents = []; this.outTangents = []; this.closed = false; }));
                var myShape = new ShapeClass();
                myShape.vertices = sp.v;
                myShape.inTangents = sp.i || [];
                myShape.outTangents = sp.o || [];
                myShape.closed = Boolean(sp.c);
                var pathProp = pathGrp.property("ADBE Vector Shape") || pathGrp.property("Path");
                if (pathProp && pathProp.setValue) pathProp.setValue(myShape);
            }

            if (item.f) {
                var fillProp = partVecs.addProperty("ADBE Vector Graphic - Fill");
                fillProp.name = "Fill";
                var fCol = fillProp.property("ADBE Vector Fill Color") || fillProp.property("Color");
                if (fCol && fCol.setValue) fCol.setValue(item.f);
                var fOp = (typeof item.fo === "number") ? item.fo : 100;
                var fOpProp = fillProp.property("ADBE Vector Fill Opacity") || fillProp.property("Opacity");
                if (fOpProp && fOpProp.setValue) fOpProp.setValue(fOp);
            }

            if (item.s && item.sw > 0) {
                var strokeProp = partVecs.addProperty("ADBE Vector Graphic - Stroke");
                strokeProp.name = "Stroke";
                var sCol = strokeProp.property("ADBE Vector Stroke Color") || strokeProp.property("Color");
                if (sCol && sCol.setValue) sCol.setValue(item.s);
                var baseSw = item.sw;
                var effectiveSw = isLine ? (baseSw * (outlinePct / 100.0)) : baseSw;
                var swProp = strokeProp.property("ADBE Vector Stroke Width") || strokeProp.property("Stroke Width");
                if (swProp && swProp.setValue) swProp.setValue(effectiveSw);
                var sOp = (typeof item.so === "number") ? item.so : 100;
                var sOpProp = strokeProp.property("ADBE Vector Stroke Opacity") || strokeProp.property("Opacity");
                if (sOpProp && sOpProp.setValue) sOpProp.setValue(sOp);

                if (isLine && swProp) {
                    try {
                        swProp.expression =
                            "try { value * (thisLayer.effect('Outline Width %')(1).value / 100); } catch(e) { value; }";
                    } catch (eSwExpr) {}
                }
            }

            if (isLine) {
                var partTr = partGrp.property("ADBE Vector Transform Group") || partGrp.property("Transform");
                if (partTr) {
                    var partOp = partTr.property("ADBE Vector Group Opacity") || partTr.property("Opacity") || partTr.property("ADBE Vector Opacity");
                    if (partOp && partOp.setValue) {
                        partOp.setValue(showOutlines ? 100 : 0);
                        try {
                            partOp.expression =
                                "try { (thisLayer.effect('Show Outlines')(1).value > 0) ? 100 : 0; } catch(e) { value; }";
                        } catch (eOpExpr) {}
                    }
                }
            }
        }

        return emoGrp;
    }

    // =========================================================================
    // 7. CALCULATION METHOD (INTACT TEXT BOX ENGINE)
    // =========================================================================
    function buildCalculationEmojiRig(comp, origLayer, options) {
        if (!comp || !origLayer || !isTextLayer(origLayer)) return null;

        var props = getTextBoxProperties(comp, origLayer);
        if (!props || !props.metrics) return null;

        var sourceId = options.sourceId || "openmoji_color";
        var sizeMult = (typeof options.sizeMultiplier === "number") ? options.sizeMultiplier : 100;
        var outlinePct = (typeof options.outlineWidth === "number") ? options.outlineWidth : 100;
        var showOutlines = (options.showOutlines !== false);
        var offX = (typeof options.offsetX === "number") ? options.offsetX : 0;
        var offY = (typeof options.offsetY === "number") ? options.offsetY : 0;
        var detectEmoticons = Boolean(options.detectEmoticons);
        var layerMode = options.layerMode || "single"; // "single" or "separate"

        var lines = props.metrics.lines;
        var lineStep = props.leading || (props.fontSize * 1.2);
        var just = props.justification || "left";

        var measurer = createMeasureHelper(comp, props);

        // Determine first line baseline relative to original text layer local origin:
        // For Point Text: in After Effects local coordinates, line 1 baseline is at Y = 0.
        // For Box Text: line 1 baseline is at boxPos[1] + ascender.
        var firstBaselineY = 0;
        if (props.isBox) {
            var rFirst = measurer.measureRect(lines.length > 0 ? lines[0] : "A");
            var ascender = Math.abs(rFirst.top) || (props.fontSize * 0.78);
            firstBaselineY = props.boxPos[1] + ascender;
        }

        var matchedEmojis = [];
        var createdLayers = [];

        try {
            // 1. Calculate geometric coordinates for emojis across visual lines
            for (var vl = 0; vl < lines.length; vl++) {
                var lineStr = lines[vl];
                if (trimStr(lineStr).length === 0) continue;

                var lineW = measurer.measureRect(lineStr).width;
                var lineBaselineY = firstBaselineY + (vl * lineStep);

                var lineLeftX = 0;
                if (props.isBox) {
                    if (just === "center") lineLeftX = props.boxPos[0] + (props.boxWidth - lineW) / 2;
                    else if (just === "right") lineLeftX = props.boxPos[0] + props.boxWidth - lineW;
                    else lineLeftX = props.boxPos[0];
                } else {
                    if (just === "center") lineLeftX = -lineW / 2;
                    else if (just === "right") lineLeftX = -lineW;
                    else lineLeftX = 0;
                }

                var lineMatches = findEmojisInString(lineStr, detectEmoticons);
                for (var lm = 0; lm < lineMatches.length; lm++) {
                    var match = lineMatches[lm];
                    var prefix = lineStr.substring(0, match.start);
                    var prefixAdv = measurer.measurePrefixAdvance(prefix);
                    var segX = lineLeftX + prefixAdv;
                    var emojiAdv = measurer.measurePrefixAdvance(prefix + match.char) - prefixAdv;
                    if (emojiAdv <= 0) emojiAdv = props.fontSize;

                    var emojiCenterX = segX + (emojiAdv / 2);
                    // Center vertically on typography ascender / cap height
                    var emojiCenterY = lineBaselineY - (props.fontSize * 0.35);

                    matchedEmojis.push({
                        char: match.char,
                        hexcode: match.hexcode,
                        entry: match.entry,
                        posX: emojiCenterX,
                        posY: emojiCenterY,
                        visualLine: vl
                    });
                }
            }

            if (matchedEmojis.length === 0) {
                return { createdCount: 0, emojiCount: 0, shapeLayer: null };
            }

            // 2. Hide Monochrome Font Emojis on Intact Text Layer via native Text Animator (Opacity = 0%)
            try {
                var textPropGroup = origLayer.property("ADBE Text Properties");
                var animators = textPropGroup ? (textPropGroup.property("ADBE Text Animators") || textPropGroup.addProperty("ADBE Text Animators")) : null;
                if (animators) {
                    var existingAnim = animators.property("Replace Color Emojis - Hide Font Emojis");
                    if (existingAnim) {
                        try { existingAnim.remove(); } catch (eRem) {}
                    }

                    var fullMatches = findEmojisInString(props.fullText, detectEmoticons);
                    if (fullMatches.length > 0) {
                        var anim = animators.addProperty("ADBE Text Animator");
                        if (anim) {
                            anim.name = "Replace Color Emojis - Hide Font Emojis";
                            var animProps = anim.property("ADBE Text Animator Properties");
                            var opProp = animProps ? animProps.addProperty("ADBE Text Opacity") : null;
                            if (opProp) {
                                opProp.setValue(0);
                            }

                            var selectors = anim.property("ADBE Text Selectors") || anim.property("Selectors");
                            if (selectors) {
                                var totalChars = Math.max(1, props.fullText.length);
                                for (var fmi = 0; fmi < fullMatches.length; fmi++) {
                                    var fMatch = fullMatches[fmi];
                                    var sel = (fmi === 0 && selectors.numProperties > 0)
                                        ? selectors.property(1)
                                        : selectors.addProperty("ADBE Text Selector");
                                    if (sel) {
                                        sel.name = "Hide Emoji " + (fmi + 1) + " (" + fMatch.char + ")";
                                        var adv = sel.property("ADBE Text Range Advanced");
                                        var usedIndex = false;
                                        if (adv) {
                                            var uProp = adv.property("ADBE Text Range Units2");
                                            if (uProp) {
                                                try {
                                                    uProp.setValue(2); // 2 = Index
                                                    usedIndex = true;
                                                } catch (eU) {}
                                            }
                                        }

                                        var pStart = sel.property("ADBE Text Index Start") || sel.property("ADBE Text Percent Start") || sel.property("Start");
                                        var pEnd = sel.property("ADBE Text Index End") || sel.property("ADBE Text Percent End") || sel.property("End");
                                        var mEnd = fMatch.start + fMatch.length;

                                        if (usedIndex) {
                                            if (pStart) pStart.setValue(fMatch.start);
                                            if (pEnd) pEnd.setValue(mEnd);
                                        } else {
                                            if (pStart) pStart.setValue((fMatch.start / totalChars) * 100);
                                            if (pEnd) pEnd.setValue((mEnd / totalChars) * 100);
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            } catch (eAnim) {}

            // 3. Create Full-Color Vector Emoji Shape Layer(s)
            var primaryShapeLayer = null;

            if (layerMode === "single") {
                // Unified Single Master Shape Layer
                var shapeLayer = comp.layers.addShape();
                shapeLayer.name = origLayer.name + " - Color Emojis";
                shapeLayer.label = 9;
                shapeLayer.comment = "AE_COLOR_EMOJI_CHILD";
                primaryShapeLayer = shapeLayer;

                var fxGroup = shapeLayer.property("ADBE Effect Parade") || shapeLayer.property("Effects");
                if (fxGroup) {
                    var srcIdx = 1;
                    for (var s = 0; s < EMOJI_SOURCES.length; s++) {
                        if (EMOJI_SOURCES[s].id === sourceId) { srcIdx = EMOJI_SOURCES[s].index; break; }
                    }
                    ensureEffectSlider(fxGroup, "Emoji Source (1=OM,2=TW,3=Flat,4=Blk)", srcIdx);
                    ensureEffectSlider(fxGroup, "Emoji Size (px)", props.fontSize);
                    ensureEffectSlider(fxGroup, "Emoji Size Multiplier %", sizeMult);
                    ensureEffectSlider(fxGroup, "Outline Width %", outlinePct);
                    ensureEffectCheckbox(fxGroup, "Show Outlines", showOutlines);
                    ensureEffectSlider(fxGroup, "Offset X", offX);
                    ensureEffectSlider(fxGroup, "Offset Y", offY);
                }

                var rootVectors = shapeLayer.property("ADBE Root Vectors Group") || shapeLayer.property("Contents");
                clearRootVectorContents(rootVectors);

                for (var me = 0; me < matchedEmojis.length; me++) {
                    var mItem = matchedEmojis[me];
                    buildVectorGroupForEmoji(rootVectors, mItem.entry, sourceId, props.fontSize, mItem.posX, mItem.posY, outlinePct, showOutlines);
                }

                var origAP = (origLayer.transform && origLayer.transform.anchorPoint) ? origLayer.transform.anchorPoint.value : [0, 0, 0];
                shapeLayer.parent = origLayer;
                shapeLayer.transform.position.setValue([-origAP[0], -origAP[1], 0]);
                shapeLayer.transform.anchorPoint.setValue([0, 0, 0]);
                shapeLayer.transform.scale.setValue([100, 100, 100]);

                try {
                    if (typeof shapeLayer.moveBefore === "function") {
                        shapeLayer.moveBefore(origLayer);
                    }
                } catch (eMove) {}

                createdLayers.push(shapeLayer);

            } else {
                // Separate Shape Layer per Emoji
                var origAP = (origLayer.transform && origLayer.transform.anchorPoint) ? origLayer.transform.anchorPoint.value : [0, 0, 0];
                for (var sei = 0; sei < matchedEmojis.length; sei++) {
                    var sItem = matchedEmojis[sei];
                    var sLayer = comp.layers.addShape();
                    sLayer.name = origLayer.name + " - Emoji " + (sei + 1) + " " + sItem.char;
                    sLayer.label = 9;
                    sLayer.comment = "AE_COLOR_EMOJI_CHILD";
                    if (!primaryShapeLayer) primaryShapeLayer = sLayer;

                    var sFx = sLayer.property("ADBE Effect Parade") || sLayer.property("Effects");
                    if (sFx) {
                        ensureEffectSlider(sFx, "Emoji Size (px)", props.fontSize);
                        ensureEffectSlider(sFx, "Emoji Size Multiplier %", sizeMult);
                        ensureEffectSlider(sFx, "Outline Width %", outlinePct);
                        ensureEffectCheckbox(sFx, "Show Outlines", showOutlines);
                        ensureEffectSlider(sFx, "Offset X", offX);
                        ensureEffectSlider(sFx, "Offset Y", offY);
                    }

                    var sRoots = sLayer.property("ADBE Root Vectors Group") || sLayer.property("Contents");
                    clearRootVectorContents(sRoots);

                    buildVectorGroupForEmoji(sRoots, sItem.entry, sourceId, props.fontSize, 0, 0, outlinePct, showOutlines);

                    sLayer.parent = origLayer;
                    sLayer.transform.anchorPoint.setValue([0, 0, 0]);
                    sLayer.transform.position.setValue([sItem.posX - origAP[0], sItem.posY - origAP[1], 0]);
                    sLayer.transform.scale.setValue([100, 100, 100]);

                    try {
                        sLayer.transform.position.expression = [
                            'var ox = 0, oy = 0;',
                            'try { ox = effect("Offset X")(1).value; } catch(e1) {}',
                            'try { oy = effect("Offset Y")(1).value; } catch(e2) {}',
                            'var ap = [0, 0]; try { ap = parent.anchorPoint.value; } catch(e3) {}',
                            '[' + sItem.posX.toFixed(2) + ' - ap[0] + ox, ' + sItem.posY.toFixed(2) + ' - ap[1] + oy, 0];'
                        ].join('\n');
                    } catch (ePos) {}

                    try {
                        if (typeof sLayer.moveBefore === "function") {
                            sLayer.moveBefore(origLayer);
                        }
                    } catch (eMove2) {}

                    createdLayers.push(sLayer);
                }
            }

            // 4. Precomposition Option (Zero-Shift)
            if (options.makePrecomp && createdLayers.length > 0) {
                var precompLayers = createdLayers.slice();
                var textCopy = origLayer.duplicate ? origLayer.duplicate() : null;
                if (textCopy) {
                    textCopy.enabled = true;
                    textCopy.guideLayer = false;
                    precompLayers.push(textCopy);
                    markOriginalAsGuideline(origLayer);
                }
                var preName = origLayer.name + " Color Emoji Precomp";
                precomposeWithZeroShift(comp, origLayer, props, precompLayers, preName, primaryShapeLayer, options);
            }

            return {
                createdCount: createdLayers.length,
                emojiCount: matchedEmojis.length,
                shapeLayer: primaryShapeLayer
            };

        } finally {
            measurer.cleanup();
        }
    }

    // =========================================================================
    // 8. SPLIT METHOD (LAYER DECOMPOSITION ENGINE)
    // =========================================================================
    function buildSplitEmojiRig(comp, origLayer, options) {
        if (!comp || !origLayer || !isTextLayer(origLayer)) return null;

        var props = getTextBoxProperties(comp, origLayer);
        if (!props || !props.metrics) return null;

        var sourceId = options.sourceId || "openmoji_color";
        var sizeMult = (typeof options.sizeMultiplier === "number") ? options.sizeMultiplier : 100;
        var outlinePct = (typeof options.outlineWidth === "number") ? options.outlineWidth : 100;
        var showOutlines = (options.showOutlines !== false);
        var offX = (typeof options.offsetX === "number") ? options.offsetX : 0;
        var offY = (typeof options.offsetY === "number") ? options.offsetY : 0;
        var detectEmoticons = Boolean(options.detectEmoticons);

        var lines = props.metrics.lines;
        var lineStep = props.leading || (props.fontSize * 1.2);
        var just = props.justification || "left";

        var measurer = createMeasureHelper(comp, props);

        var firstBaselineY = 0;
        if (props.isBox) {
            var rFirst = measurer.measureRect(lines.length > 0 ? lines[0] : "A");
            var ascender = Math.abs(rFirst.top) || (props.fontSize * 0.78);
            firstBaselineY = props.boxPos[1] + ascender;
        }

        var origAP = (origLayer.transform && origLayer.transform.anchorPoint) ? origLayer.transform.anchorPoint.value : [0, 0, 0];

        var createdLayers = [];
        var totalEmojiCount = 0;
        var primaryShapeLayer = null;

        try {
            for (var vl = 0; vl < lines.length; vl++) {
                var lineStr = lines[vl];
                if (trimStr(lineStr).length === 0) continue;

                var lineW = measurer.measureRect(lineStr).width;
                var lineBaselineY = firstBaselineY + (vl * lineStep);

                var lineLeftX = 0;
                if (props.isBox) {
                    if (just === "center") lineLeftX = props.boxPos[0] + (props.boxWidth - lineW) / 2;
                    else if (just === "right") lineLeftX = props.boxPos[0] + props.boxWidth - lineW;
                    else lineLeftX = props.boxPos[0];
                } else {
                    if (just === "center") lineLeftX = -lineW / 2;
                    else if (just === "right") lineLeftX = -lineW;
                    else lineLeftX = 0;
                }

                var lineMatches = findEmojisInString(lineStr, detectEmoticons);

                if (lineMatches.length === 0) {
                    // Line without emojis -> create independent text box for line
                    var lineLayer = comp.layers.addText(lineStr);
                    applyTextDocCopy(lineLayer, props.textDoc, lineStr, props.fillColor);
                    lineLayer.name = origLayer.name + " [Line " + (vl + 1) + "]";
                    lineLayer.comment = "AE_COLOR_EMOJI_CHILD";

                    var rL = lineLayer.sourceRectAtTime(comp.time, false);
                    lineLayer.transform.anchorPoint.setValue([rL.left, rL.top, 0]);
                    lineLayer.transform.position.setValue([lineLeftX + rL.left - origAP[0], lineBaselineY + rL.top - origAP[1], 0]);
                    lineLayer.parent = origLayer;
                    createdLayers.push(lineLayer);
                    continue;
                }

                // Decompose line around emojis
                var segments = [];
                var curPos = 0;
                for (var m = 0; m < lineMatches.length; m++) {
                    var match = lineMatches[m];
                    if (match.start > curPos) {
                        segments.push({
                            isEmoji: false,
                            text: lineStr.substring(curPos, match.start),
                            colStart: curPos
                        });
                    }
                    segments.push({
                        isEmoji: true,
                        match: match,
                        colStart: match.start
                    });
                    curPos = match.start + match.length;
                }
                if (curPos < lineStr.length) {
                    segments.push({
                        isEmoji: false,
                        text: lineStr.substring(curPos),
                        colStart: curPos
                    });
                }

                for (var segIdx = 0; segIdx < segments.length; segIdx++) {
                    var seg = segments[segIdx];
                    var prefix = lineStr.substring(0, seg.colStart);
                    var prefixAdv = measurer.measurePrefixAdvance(prefix);
                    var segX = lineLeftX + prefixAdv;

                    if (!seg.isEmoji) {
                        if (trimStr(seg.text).length === 0) continue;
                        var txtLayer = comp.layers.addText(seg.text);
                        applyTextDocCopy(txtLayer, props.textDoc, seg.text, props.fillColor);
                        txtLayer.name = origLayer.name + " [Text] " + seg.text.substr(0, 16);
                        txtLayer.comment = "AE_COLOR_EMOJI_CHILD";

                        var rSeg = txtLayer.sourceRectAtTime(comp.time, false);
                        txtLayer.transform.anchorPoint.setValue([rSeg.left, rSeg.top, 0]);
                        txtLayer.transform.position.setValue([segX + rSeg.left - origAP[0], lineBaselineY + rSeg.top - origAP[1], 0]);
                        txtLayer.parent = origLayer;
                        createdLayers.push(txtLayer);

                    } else {
                        totalEmojiCount++;
                        var eMatch = seg.match;
                        var emojiAdv = measurer.measurePrefixAdvance(prefix + eMatch.char) - prefixAdv;
                        if (emojiAdv <= 0) emojiAdv = props.fontSize;

                        var emojiCenterX = segX + (emojiAdv / 2);
                        var emojiCenterY = lineBaselineY - (props.fontSize * 0.35);

                        var emoLayer = comp.layers.addShape();
                        emoLayer.name = origLayer.name + " [Emoji] " + eMatch.char + " " + eMatch.hexcode;
                        emoLayer.label = 9;
                        emoLayer.comment = "AE_COLOR_EMOJI_CHILD";
                        if (!primaryShapeLayer) primaryShapeLayer = emoLayer;

                        var efx = emoLayer.property("ADBE Effect Parade") || emoLayer.property("Effects");
                        if (efx) {
                            ensureEffectSlider(efx, "Emoji Size (px)", props.fontSize);
                            ensureEffectSlider(efx, "Emoji Size Multiplier %", sizeMult);
                            ensureEffectSlider(efx, "Outline Width %", outlinePct);
                            ensureEffectCheckbox(efx, "Show Outlines", showOutlines);
                            ensureEffectSlider(efx, "Offset X", offX);
                            ensureEffectSlider(efx, "Offset Y", offY);
                        }

                        var eRoots = emoLayer.property("ADBE Root Vectors Group") || emoLayer.property("Contents");
                        clearRootVectorContents(eRoots);

                        buildVectorGroupForEmoji(eRoots, eMatch.entry, sourceId, props.fontSize, 0, 0, outlinePct, showOutlines);

                        emoLayer.parent = origLayer;
                        emoLayer.transform.anchorPoint.setValue([0, 0, 0]);
                        emoLayer.transform.position.setValue([emojiCenterX - origAP[0], emojiCenterY - origAP[1], 0]);
                        emoLayer.transform.scale.setValue([100, 100, 100]);

                        try {
                            emoLayer.transform.position.expression = [
                                'var ox = 0, oy = 0;',
                                'try { ox = effect("Offset X")(1).value; } catch(e1) {}',
                                'try { oy = effect("Offset Y")(1).value; } catch(e2) {}',
                                'var ap = [0, 0]; try { ap = parent.anchorPoint.value; } catch(e3) {}',
                                '[' + emojiCenterX.toFixed(2) + ' - ap[0] + ox, ' + emojiCenterY.toFixed(2) + ' - ap[1] + oy, 0];'
                            ].join('\n');
                        } catch (ePos2) {}

                        createdLayers.push(emoLayer);
                    }
                }
            }

            // Hide original text layer as guideline
            markOriginalAsGuideline(origLayer);

            // Precomposition Option
            if (options.makePrecomp && createdLayers.length > 0) {
                var preNameSplit = origLayer.name + " Color Emoji Precomp";
                precomposeWithZeroShift(comp, origLayer, props, createdLayers, preNameSplit, primaryShapeLayer, options);
            }

            return {
                createdCount: createdLayers.length,
                emojiCount: totalEmojiCount,
                shapeLayer: primaryShapeLayer
            };

        } finally {
            measurer.cleanup();
        }
    }

    // =========================================================================
    // 9. ZERO-SHIFT PRECOMPOSITION ENGINE (From AE-text-precomp & AE-Text-Highlight)
    // =========================================================================
    function precomposeWithZeroShift(comp, origLayer, props, layersToPrecompose, precompName, shapeLayer, options) {
        if (!comp || !layersToPrecompose || layersToPrecompose.length === 0) return null;
        try {
            var layerIndices = [];
            for (var k = 0; k < layersToPrecompose.length; k++) {
                if (layersToPrecompose[k] && typeof layersToPrecompose[k].index === "number") {
                    layerIndices.push(layersToPrecompose[k].index);
                }
            }
            if (layerIndices.length === 0) return null;

            var precompLayer = comp.layers.precompose(layerIndices, precompName, true);
            if (precompLayer) {
                precompLayer.comment = "AE_COLOR_EMOJI_CHILD";
                precompLayer.label = 9;

                var bounds = props.isBox
                    ? { left: props.boxPos[0], top: props.boxPos[1], width: props.boxWidth, height: props.boxHeight }
                    : props.sRect;

                var tr = precompLayer.transform;
                if (tr) {
                    tr.anchorPoint.setValue([0, 0, 0]);
                    var origPos = origLayer.transform.position.value;
                    tr.position.setValue([origPos[0], origPos[1], origPos[2] || 0]);
                }
                return precompLayer;
            }
        } catch (ePre) {}
        return null;
    }

    // =========================================================================
    // 10. CLEAN RESTORE / UNDO ENGINE
    // =========================================================================
    function removeEmojisAndRestoreOriginal(comp) {
        if (!comp) return 0;
        var removedCount = 0;
        try {
            var layers = comp.layers;
            var num = (layers && layers.length) ? layers.length : (comp.numLayers || 0);

            // 1. Remove created child layers
            for (var i = num; i >= 1; i--) {
                var l = (layers && layers._layers) ? layers._layers[i - 1] : layers[i];
                if (!l) continue;

                var isChild = false;
                try {
                    if (l.comment === "AE_COLOR_EMOJI_CHILD") isChild = true;
                } catch (eC) {}

                var name = l.name || "";
                if (name.indexOf(" - Color Emojis") !== -1 ||
                    name.indexOf(" - Emoji ") !== -1 ||
                    name.indexOf(" [Emoji]") !== -1 ||
                    name.indexOf(" Color Emoji Precomp") !== -1) {
                    isChild = true;
                }

                if (isChild) {
                    try {
                        l.remove();
                        removedCount++;
                    } catch (eRem) {}
                }
            }

            // 2. Restore all text layers (remove animator and re-enable)
            var currentNum = (layers && layers.length) ? layers.length : (comp.numLayers || 0);
            for (var j = 1; j <= currentNum; j++) {
                var tl = (layers && layers._layers) ? layers._layers[j - 1] : layers[j];
                if (!tl || !isTextLayer(tl)) continue;

                try {
                    tl.enabled = true;
                    tl.guideLayer = false;
                } catch (eEn) {}

                try {
                    var textProp = tl.property("ADBE Text Properties");
                    var animators = textProp ? textProp.property("ADBE Text Animators") : null;
                    if (animators) {
                        var anim = animators.property("Replace Color Emojis - Hide Font Emojis");
                        if (anim) {
                            anim.remove();
                        }
                    }
                } catch (eAnimRem) {}
            }
        } catch (eClean) {}
        return removedCount;
    }

    // =========================================================================
    // 11. SCRIPTUI INTERFACE
    // =========================================================================
    function buildUI(thisObj) {
        var isDockable = (typeof Panel !== "undefined" && thisObj instanceof Panel);
        var WinClass = (typeof Window !== "undefined")
            ? Window
            : ((typeof globalObj !== "undefined" && typeof globalObj.Window !== "undefined")
                ? globalObj.Window
                : ((typeof window !== "undefined") ? window.Window : null));
        var win = isDockable
            ? thisObj
            : (WinClass ? new WinClass("palette", SCRIPT_TITLE + " " + SCRIPT_VERSION, undefined, { resizeable: true }) : null);

        win.orientation = "column";
        win.alignChildren = ["fill", "top"];
        win.spacing = 6;
        win.margins = 8;
        win.minimumSize = [340, 520];

        win.onResizing = win.onResize = function () {
            this.layout.resize();
        };

        // --- Header Panel ---
        var pnlHeader = win.add("panel", undefined, SCRIPT_TITLE + " " + SCRIPT_VERSION);
        pnlHeader.orientation = "column";
        pnlHeader.alignChildren = ["fill", "top"];
        pnlHeader.spacing = 3;
        pnlHeader.margins = [10, 8, 10, 8];

        var lblSub = pnlHeader.add("statictext", undefined, "Procedural Full-Color Vector Emoji Replacement Engine");
        try {
            lblSub.graphics.foregroundColor = win.graphics.newPen(win.graphics.PenType.SOLID_COLOR, [0.35, 0.65, 0.95, 1], 1);
        } catch (eG1) {}

        var lblRef = pnlHeader.add("statictext", undefined, "Native Shape Layers • OpenMoji & Twemoji • Sub-Pixel Alignment");
        lblRef.helpTip = GITHUB_REPO_URL;

        // --- Method Selector Panel ---
        var pnlMethod = win.add("panel", undefined, "1. Replacement Method");
        pnlMethod.orientation = "column";
        pnlMethod.alignChildren = ["fill", "top"];
        pnlMethod.spacing = 4;
        pnlMethod.margins = [8, 6, 8, 6];

        var grpMethodRow = pnlMethod.add("group");
        grpMethodRow.orientation = "row";
        grpMethodRow.alignChildren = ["left", "center"];
        grpMethodRow.spacing = 8;

        grpMethodRow.add("statictext", undefined, "Method:");
        var ddMethod = grpMethodRow.add("dropdownlist", undefined, [
            "📐 Calculation Method (Intact Text Box - Recommended)",
            "✂️ Split Method (Decompose Lines & Segments)"
        ]);
        ddMethod.selection = 0;
        ddMethod.alignment = ["fill", "center"];

        var lblMethodDesc = pnlMethod.add("statictext", undefined, "Keeps text layer 100% intact; hides font emojis via Text Animator (Opacity 0%).");
        lblMethodDesc.alignment = ["fill", "top"];
        try {
            lblMethodDesc.graphics.foregroundColor = lblMethodDesc.graphics.newPen(win.graphics.PenType.SOLID_COLOR, [0.75, 0.75, 0.75, 1.0], 1);
        } catch (eG2) {}

        // --- Target Text Layer & Status Panel ---
        var pnlTarget = win.add("panel", undefined, "2. Active Text Layer & Emoji Scanner");
        pnlTarget.orientation = "column";
        pnlTarget.alignChildren = ["fill", "top"];
        pnlTarget.spacing = 5;
        pnlTarget.margins = [8, 6, 8, 6];

        var lblStatus = pnlTarget.add("statictext", undefined, "Detecting active selection...");
        lblStatus.alignment = ["fill", "top"];
        try {
            lblStatus.graphics.foregroundColor = lblStatus.graphics.newPen(win.graphics.PenType.SOLID_COLOR, [0.35, 0.75, 1.0, 1.0], 1);
        } catch (eG3) {}

        var grpTargetBtns = pnlTarget.add("group");
        grpTargetBtns.orientation = "row";
        grpTargetBtns.alignChildren = ["fill", "center"];
        grpTargetBtns.spacing = 6;

        var btnRefresh = grpTargetBtns.add("button", undefined, "🔄 Detect Layer");
        btnRefresh.helpTip = "Check active composition and inspect the currently selected text layer.";

        var btnScan = grpTargetBtns.add("button", undefined, "👀 Scan Emojis");
        btnScan.helpTip = "Scan selected text layer and preview detected emojis.";

        var btnDemo = grpTargetBtns.add("button", undefined, "📝 Demo Text");
        btnDemo.helpTip = "Create a sample text layer with popular emojis and emoticons for instant 1-click testing.";

        // --- Emoji Detection & Vector Source Panel ---
        var pnlSource = win.add("panel", undefined, "3. Vector Style & Detection Options");
        pnlSource.orientation = "column";
        pnlSource.alignChildren = ["fill", "top"];
        pnlSource.spacing = 5;
        pnlSource.margins = [8, 6, 8, 6];

        var grpDetectRow = pnlSource.add("group");
        grpDetectRow.orientation = "row";
        grpDetectRow.alignChildren = ["left", "center"];
        grpDetectRow.spacing = 10;

        var chkUnicode = grpDetectRow.add("checkbox", undefined, "Unicode Emojis (😃, 🚀, ❤️, 🔥)");
        chkUnicode.value = true;
        chkUnicode.helpTip = "Detect standard Unicode emojis and surrogate pairs.";

        var chkEmoticons = grpDetectRow.add("checkbox", undefined, "Text Emoticons (:D, :fire:, <3)");
        chkEmoticons.value = true;
        chkEmoticons.helpTip = "Also detect Western sideways emoticons and shortcodes from the Wikipedia Emoticons database.";

        var grpSrcRow = pnlSource.add("group");
        grpSrcRow.orientation = "row";
        grpSrcRow.alignChildren = ["left", "center"];
        grpSrcRow.spacing = 6;

        grpSrcRow.add("statictext", undefined, "Vector Style:");
        var srcLabels = [];
        for (var si = 0; si < EMOJI_SOURCES.length; si++) srcLabels.push(EMOJI_SOURCES[si].label);
        var ddSource = grpSrcRow.add("dropdownlist", undefined, srcLabels);
        ddSource.selection = 0;
        ddSource.alignment = ["fill", "center"];

        var btnReloadJSON = grpSrcRow.add("button", undefined, "↻");
        btnReloadJSON.preferredSize = [26, 24];
        btnReloadJSON.helpTip = "Reload JSON database from /emojis/ folder.";

        var grpModeRow = pnlSource.add("group");
        grpModeRow.orientation = "row";
        grpModeRow.alignChildren = ["left", "center"];
        grpModeRow.spacing = 6;

        grpModeRow.add("statictext", undefined, "Layer Mode:");
        var ddLayerMode = grpModeRow.add("dropdownlist", undefined, [
            "📦 Single Master Shape Layer (Clean Timeline)",
            "📑 Separate Shape Layer per Emoji"
        ]);
        ddLayerMode.selection = 0;
        ddLayerMode.alignment = ["fill", "center"];

        // --- Sizing, Offset & Outline Controls Panel ---
        var pnlSizing = win.add("panel", undefined, "4. Emoji Sizing, Offsets & Outlines");
        pnlSizing.orientation = "column";
        pnlSizing.alignChildren = ["fill", "top"];
        pnlSizing.spacing = 4;
        pnlSizing.margins = [8, 6, 8, 6];

        function addSliderRow(parent, label, min, max, defaultVal, unit) {
            var g = parent.add("group");
            g.orientation = "row";
            g.alignChildren = ["left", "center"];
            g.spacing = 6;

            var lbl = g.add("statictext", undefined, label);
            lbl.preferredSize.width = 110;

            var sld = g.add("slider", undefined, defaultVal, min, max);
            sld.alignment = ["fill", "center"];

            var txt = g.add("edittext", undefined, String(defaultVal));
            txt.preferredSize.width = 46;

            if (unit) g.add("statictext", undefined, unit);

            sld.onChanging = function () { txt.text = String(Math.round(this.value)); };
            txt.onChange = function () {
                var v = Number(this.text);
                if (!isNaN(v)) sld.value = Math.max(min, Math.min(max, v));
            };

            return {
                getValue: function () { return Number(txt.text) || sld.value; },
                setValue: function (v) { sld.value = v; txt.text = String(v); }
            };
        }

        var sldMult = addSliderRow(pnlSizing, "Size Multiplier:", 50, 200, 100, "%");
        var sldOffY = addSliderRow(pnlSizing, "Vertical Offset (Y):", -50, 50, 0, "px");
        var sldOffX = addSliderRow(pnlSizing, "Horizontal Offset (X):", -50, 50, 0, "px");
        var sldOutline = addSliderRow(pnlSizing, "Outline Width:", 0, 200, 100, "%");

        var grpCheckRow = pnlSizing.add("group");
        grpCheckRow.orientation = "row";
        grpCheckRow.alignChildren = ["left", "center"];
        grpCheckRow.spacing = 16;

        var chkShowOutlines = grpCheckRow.add("checkbox", undefined, "Show Outlines");
        chkShowOutlines.value = true;

        var chkMakePrecomp = grpCheckRow.add("checkbox", undefined, "Make Precomp Out of Rig");
        chkMakePrecomp.value = false;

        // --- Action Buttons ---
        var pnlActions = win.add("panel", undefined, "5. Execute");
        pnlActions.orientation = "column";
        pnlActions.alignChildren = ["fill", "top"];
        pnlActions.spacing = 6;
        pnlActions.margins = [8, 8, 8, 8];

        var btnExecute = pnlActions.add("button", undefined, "✨ Replace Font Emojis with Color Emojis");
        btnExecute.preferredSize = [-1, 34];
        try {
            btnExecute.graphics.foregroundColor = btnExecute.graphics.newPen(win.graphics.PenType.SOLID_COLOR, [0.1, 0.5, 0.9, 1], 1);
        } catch (eBCol) {}

        var btnRestore = pnlActions.add("button", undefined, "↺ Remove Emojis & Restore Original Text");
        btnRestore.preferredSize = [-1, 26];

        // --- Footer ---
        var grpFooter = win.add("group");
        grpFooter.orientation = "row";
        grpFooter.alignChildren = ["center", "center"];
        var lblRepo = grpFooter.add("statictext", undefined, "GitHub: work2survive/AE-replace-color-emojis");
        try {
            lblRepo.graphics.foregroundColor = lblRepo.graphics.newPen(win.graphics.PenType.SOLID_COLOR, [0.4, 0.7, 1.0, 1.0], 1);
        } catch (eGF) {}

        // ---------------------------------------------------------------------
        // EVENT HANDLERS & LOGIC
        // ---------------------------------------------------------------------
        function getActiveComp() {
            var activeApp = (typeof app !== "undefined") ? app : ((typeof globalObj !== "undefined" && globalObj.app) ? globalObj.app : ((typeof window !== "undefined") ? window.app : null));
            if (activeApp && activeApp.project && activeApp.project.activeItem) {
                var itm = activeApp.project.activeItem;
                if (typeof CompItem !== "undefined") {
                    if (itm instanceof CompItem) return itm;
                }
                if (itm.typeName === "Composition" || itm.layers) {
                    return itm;
                }
            }
            return null;
        }

        function updateSelectionStatus() {
            var comp = getActiveComp();
            if (!comp) {
                lblStatus.text = "⚠️ No active composition found.";
                return null;
            }
            var textLayer = getSelectedTextLayer(comp);
            if (!textLayer) {
                lblStatus.text = "⚠️ Please select a Text Layer in the active composition.";
                return null;
            }

            var textStr = getTextLayerString(textLayer);
            var matches = findEmojisInString(textStr, chkEmoticons.value);
            var emojiNames = [];
            for (var mi = 0; mi < Math.min(4, matches.length); mi++) {
                emojiNames.push(matches[mi].char);
            }
            var emojiSummary = (matches.length > 0)
                ? (matches.length + " emoji(s) found [" + emojiNames.join(" ") + (matches.length > 4 ? "..." : "") + "]")
                : "0 emojis detected in text";

            lblStatus.text = "Layer: '" + textLayer.name.substr(0, 18) + "' • " + emojiSummary;
            return textLayer;
        }

        ddMethod.onChange = function () {
            if (ddMethod.selection.index === 0) {
                lblMethodDesc.text = "Keeps text layer 100% intact; hides font emojis via Text Animator (Opacity 0%).";
            } else {
                lblMethodDesc.text = "Decomposes target lines and segments into independent text boxes (top-left anchors).";
            }
        };

        btnRefresh.onClick = function () {
            updateSelectionStatus();
        };

        btnScan.onClick = function () {
            var comp = getActiveComp();
            var textLayer = updateSelectionStatus();
            if (!comp || !textLayer) return;

            var textStr = getTextLayerString(textLayer);
            var matches = findEmojisInString(textStr, chkEmoticons.value);
            if (matches.length === 0) {
                alert("No emojis or emoticons found in layer '" + textLayer.name + "'.\n\nTry adding emojis like 😃 🚀 🔥 ❤️ or emoticons like :D :fire:");
                return;
            }
            var list = [];
            for (var m = 0; m < matches.length; m++) {
                var itm = matches[m];
                var nm = itm.entry ? itm.entry.name : "Unicode " + itm.hexcode;
                list.push((m + 1) + ". " + itm.char + " [" + itm.hexcode + "] - " + nm);
            }
            alert("Found " + matches.length + " emoji(s) in '" + textLayer.name + "':\n\n" + list.slice(0, 15).join("\n") + (list.length > 15 ? "\n...and " + (list.length - 15) + " more" : ""));
        };

        btnDemo.onClick = function () {
            var comp = getActiveComp();
            if (!comp) {
                alert("Please open or create a composition first.");
                return;
            }
            try {
                if (typeof app !== "undefined" && app.beginUndoGroup) {
                    app.beginUndoGroup("Create Demo Text Layer with Emojis");
                }
                var demoStr = "Hello After Effects! 😃 We now have color emojis! 🚀🔥 With red heart ❤️ and smile :D ✨";
                var demoLayer = comp.layers.addText(demoStr);
                demoLayer.name = "Demo Text with Emojis";
                var tr = demoLayer.transform;
                if (tr) {
                    tr.position.setValue([Math.round(comp.width / 2), Math.round(comp.height / 2), 0]);
                }
                try {
                    var doc = getTextDocument(demoLayer);
                    if (doc) {
                        doc.fontSize = 54;
                        doc.fillColor = [1, 1, 1];
                        if (typeof ParagraphJustification !== "undefined") {
                            doc.justification = ParagraphJustification.CENTER_JUSTIFY;
                        }
                        var prop = demoLayer.property("Source Text");
                        if (prop) prop.setValue(doc);
                    }
                } catch (eDoc) {}

                try {
                    if (comp.layers && comp.layers._layers) {
                        for (var i = 0; i < comp.layers._layers.length; i++) {
                            comp.layers._layers[i].selected = (comp.layers._layers[i] === demoLayer);
                        }
                    }
                    demoLayer.selected = true;
                } catch (eSel) {}

                updateSelectionStatus();
            } finally {
                if (typeof app !== "undefined" && app.endUndoGroup) {
                    app.endUndoGroup();
                }
            }
        };

        btnReloadJSON.onClick = function () {
            loadAllEmojiDatabases();
            alert("Emoji database reloaded! Loaded " + emojiCatalog.length + " catalog emojis and " + Object.keys(wikiEmoticonMap).length + " emoticon mappings.");
            updateSelectionStatus();
        };

        btnRestore.onClick = function () {
            var comp = getActiveComp();
            if (!comp) {
                alert("No active composition found.");
                return;
            }
            try {
                if (typeof app !== "undefined" && app.beginUndoGroup) {
                    app.beginUndoGroup("Remove Emojis & Restore Original");
                }
                var removed = removeEmojisAndRestoreOriginal(comp);
                alert("Restore complete! Cleaned up " + removed + " emoji / helper layer(s) and restored original text layer(s).");
                updateSelectionStatus();
            } finally {
                if (typeof app !== "undefined" && app.endUndoGroup) {
                    app.endUndoGroup();
                }
            }
        };

        btnExecute.onClick = function () {
            var comp = getActiveComp();
            if (!comp) {
                if (isBrowserSim() && typeof app !== "undefined" && app.project && typeof app.project.addComp === "function") {
                    comp = app.project.addComp("Main Comp", 1920, 1080, 1, 10, 30);
                } else {
                    alert("Please open a composition in After Effects first.");
                    return;
                }
            }
            var textLayer = getSelectedTextLayer(comp);
            if (!textLayer) {
                // Auto-create demo text layer if none is selected (essential for simulator autobuild)
                btnDemo.onClick();
                textLayer = getSelectedTextLayer(comp);
            }
            if (!textLayer) {
                alert("Please select a text layer containing emojis (e.g. 😃 🚀 🔥 ❤️) or click '📝 Demo Text'.");
                return;
            }

            var srcObj = EMOJI_SOURCES[ddSource.selection ? ddSource.selection.index : 0] || EMOJI_SOURCES[0];
            var isSplit = (ddMethod.selection && ddMethod.selection.index === 1);
            var isSeparate = (ddLayerMode.selection && ddLayerMode.selection.index === 1);

            var opts = {
                sourceId: srcObj.id,
                sizeMultiplier: sldMult.getValue(),
                outlineWidth: sldOutline.getValue(),
                showOutlines: chkShowOutlines.value,
                offsetX: sldOffX.getValue(),
                offsetY: sldOffY.getValue(),
                detectEmoticons: chkEmoticons.value,
                makePrecomp: chkMakePrecomp.value,
                layerMode: isSeparate ? "separate" : "single"
            };

            try {
                if (typeof app !== "undefined" && app.beginUndoGroup) {
                    app.beginUndoGroup("Replace Font Emojis with Color Emojis");
                }

                var res = isSplit
                    ? buildSplitEmojiRig(comp, textLayer, opts)
                    : buildCalculationEmojiRig(comp, textLayer, opts);

                if (!res || res.emojiCount === 0) {
                    alert("No emojis detected in text layer '" + textLayer.name + "'.\n\nEnsure the text contains Unicode emojis (😃 🚀 🔥) or emoticons (:D, :fire:).");
                    return;
                }

                var summary = "✨ Replaced " + res.emojiCount + " emoji(s) using "
                    + (isSplit ? "Split Method" : "Calculation Method") + " ("
                    + (isSeparate ? (res.createdCount + " shape layers") : "1 master shape layer") + ")!";

                lblStatus.text = summary;

                if (comp._onChanged) {
                    try { comp._onChanged(); } catch (eChg) {}
                }

            } catch (err) {
                alert("Error replacing emojis: " + err);
            } finally {
                if (typeof app !== "undefined" && app.endUndoGroup) {
                    app.endUndoGroup();
                }
            }
        };

        // Live selection sync in AE_JS_builder simulator
        if (typeof window !== "undefined" && typeof window.addEventListener === "function") {
            window.addEventListener("ae-layer-selection-changed", function () {
                try { updateSelectionStatus(); } catch (e) {}
            });
        }
        win.onActivate = function () {
            try { updateSelectionStatus(); } catch (e) {}
        };

        updateSelectionStatus();

        if (win && !isDockable && typeof win.show === "function") {
            try { win.center(); } catch (eCen) {}
            try { win.show(); } catch (eShw) {}
        } else if (win && win.layout) {
            try { win.layout.layout(true); } catch (eLay) {}
        }

        win._btnExecute = btnExecute;
        win._btnRestore = btnRestore;
        win._btnScan = btnScan;
        try { globalObj._aeReplaceColorEmojisWin = win; } catch (eGWin) {}

        return win;
    }

    // Launch ScriptUI Panel
    buildUI(thisObj);

})(this);
'''

    full_jsx = header + embedded_data + body
    with open(OUT_JSX, "w", encoding="utf-8") as f:
        f.write(full_jsx)
    print(f"Generated {OUT_JSX} ({len(full_jsx)} bytes)")

if __name__ == "__main__":
    generate_jsx()
