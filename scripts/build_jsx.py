#!/usr/bin/env python3
"""
Simple Build Script for AE Replace Color Emojis
Injects embedded fallback OpenMoji and Twemoji vector shapes into the JSX bundle.
"""

import json
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
EMOJIS_DIR = os.path.join(ROOT_DIR, "emojis")
SRC_JSX = os.path.join(ROOT_DIR, "src", "AE_Replace_Color_Emojis.jsx")
OUT_JSX = os.path.join(ROOT_DIR, "AE_Replace_Color_Emojis.jsx")

FALLBACK_HEXCODES = [
    # Top 30 Emojis from AE_JS_builder EMOJI_POOL
    "1F603", "1F680", "1F525", "2764", "1F389", "2728", "1F44D", "1F917",
    "1F60E", "1F308", "1F338", "1F31F", "1F4A5", "1F4AC", "1F3A8", "1F955",
    "1F41F", "1F422", "1F34E", "1F451", "1F355", "1F381", "1F37F", "1F3B8",
    "1F3AA", "1F951", "1F98A", "1F431", "1F576", "1F47E", "1F642", "1F609"
]

def build():
    with open(os.path.join(EMOJIS_DIR, "emoji_index.json"), "r", encoding="utf-8") as f:
        idx_data = json.load(f)
    with open(os.path.join(EMOJIS_DIR, "openmoji_color.json"), "r", encoding="utf-8") as f:
        om_color = json.load(f)
    with open(os.path.join(EMOJIS_DIR, "twemoji_color.json"), "r", encoding="utf-8") as f:
        tw_color = json.load(f)

    fallback_index = {}
    fallback_om = {}
    fallback_tw = {}

    for e in idx_data.get("emojis", []):
        hc = e.get("hexcode")
        if hc in FALLBACK_HEXCODES:
            fallback_index[hc] = e
            if hc in om_color:
                fallback_om[hc] = om_color[hc]
            if hc in tw_color:
                fallback_tw[hc] = tw_color[hc]

    with open(SRC_JSX, "r", encoding="utf-8") as f:
        jsx_code = f.read()

    idx_json = json.dumps(fallback_index, separators=(",", ":"), ensure_ascii=False)
    om_json = json.dumps(fallback_om, separators=(",", ":"), ensure_ascii=False)
    tw_json = json.dumps(fallback_tw, separators=(",", ":"), ensure_ascii=False)

    jsx_code = jsx_code.replace("/* @@EMBEDDED_INDEX@@ */ {}", idx_json)
    jsx_code = jsx_code.replace("/* @@EMBEDDED_OPENMOJI@@ */ {}", om_json)
    jsx_code = jsx_code.replace("/* @@EMBEDDED_TWEMOJI@@ */ {}", tw_json)

    with open(OUT_JSX, "w", encoding="utf-8") as f:
        f.write(jsx_code)

    print(f"✔ Generated {OUT_JSX} ({len(jsx_code)} bytes, {len(fallback_om)} OpenMoji, {len(fallback_tw)} Twemoji emojis embedded)")

if __name__ == "__main__":
    build()
