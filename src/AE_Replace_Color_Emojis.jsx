/**
 * ============================================================================
 * AE Replace Color Emojis v2.0.1 — Ground-Up Rewrite
 * ============================================================================
 *
 * Replaces monochrome font emojis in Adobe After Effects text layers with
 * full-color native vector cubic Bézier shape layers (OpenMoji & Twemoji).
 *
 * Repository: https://github.com/work2survive/AE-replace-color-emojis
 * Live Demo:  https://work2survive.github.io/AE_JS_builder/?jsx=AE_Replace_Color_Emojis.jsx&autobuild=true
 */

(function (thisObj) {
    "use strict";

    var SCRIPT_TITLE   = "AE Replace Color Emojis";
    var SCRIPT_VERSION = "v2.0.1";

    // -------------------------------------------------------------------------
    // 1. Safe Environment & Polyfills
    // -------------------------------------------------------------------------
    var globalObj = (typeof $ !== "undefined" && typeof $.global !== "undefined")
        ? $.global
        : (typeof globalThis !== "undefined" ? globalThis : (typeof window !== "undefined" ? window : this));

    var ShapeClass = (typeof Shape !== "undefined")
        ? Shape
        : (globalObj.Shape || ((typeof window !== "undefined") ? window.Shape : null) || function () {
            this.vertices = []; this.inTangents = []; this.outTangents = []; this.closed = false;
        });

    var JSONSafe = (typeof JSON !== "undefined" && JSON && typeof JSON.parse === "function") ? JSON : {
        parse: function (s) { return eval("(" + s + ")"); },
        stringify: function (o) { return "" + o; }
    };

    // -------------------------------------------------------------------------
    // 2. Embedded Standalone Fallback Datasets (Injected by build_jsx.py)
    // -------------------------------------------------------------------------
    var FALLBACK_INDEX    = /* @@EMBEDDED_INDEX@@ */ {};
    var FALLBACK_OPENMOJI = /* @@EMBEDDED_OPENMOJI@@ */ {};
    var FALLBACK_TWEMOJI  = /* @@EMBEDDED_TWEMOJI@@ */ {};

    // -------------------------------------------------------------------------
    // 3. Database Loader (Disk / Network / Memory Fallback)
    // -------------------------------------------------------------------------
    var shapeDatabases = {
        openmoji_color: FALLBACK_OPENMOJI,
        twemoji_color:  FALLBACK_TWEMOJI
    };

    function loadJSONFile(filename) {
        // Browser / AE_JS_builder simulator
        if (typeof XMLHttpRequest !== "undefined") {
            var urls = [
                "jsx/emojis/" + filename,
                "emojis/" + filename,
                "https://raw.githubusercontent.com/work2survive/AE-replace-color-emojis/main/emojis/" + filename,
                "https://raw.githubusercontent.com/work2survive/AE_Get_Emojis/main/emojis/" + filename
            ];
            for (var u = 0; u < urls.length; u++) {
                try {
                    var xhr = new XMLHttpRequest();
                    xhr.open("GET", urls[u], false);
                    xhr.send(null);
                    if (xhr.status >= 200 && xhr.status < 300 && xhr.responseText) {
                        return JSONSafe.parse(xhr.responseText);
                    }
                } catch (eX) {}
            }
        }
        // AE Desktop ExtendScript
        if (typeof File !== "undefined") {
            try {
                var folderPath = "";
                if (typeof $.fileName !== "undefined" && $.fileName) {
                    folderPath = new File($.fileName).parent.fsName + "/emojis/";
                }
                var f = new File(folderPath + filename);
                if (!f.exists) f = new File("/home/antigravity/work2survive/AE-replace-color-emojis/emojis/" + filename);
                if (f.exists && f.open("r")) {
                    var content = f.read();
                    f.close();
                    if (content) return JSONSafe.parse(content);
                }
            } catch (eF) {}
        }
        return null;
    }

    function initDatabases() {
        var om = loadJSONFile("openmoji_color.json");
        if (om) shapeDatabases.openmoji_color = om;
        var tw = loadJSONFile("twemoji_color.json");
        if (tw) shapeDatabases.twemoji_color = tw;
    }
    initDatabases();

    function getShapesForEmoji(hexcode, styleId) {
        var hc = String(hexcode || "").toUpperCase();
        var db = shapeDatabases[styleId] || shapeDatabases.openmoji_color;
        var shapes = (db && db[hc]) ? db[hc] : null;

        if (!shapes) {
            if (styleId === "twemoji_color" && FALLBACK_TWEMOJI[hc]) {
                shapes = FALLBACK_TWEMOJI[hc];
            } else if (FALLBACK_OPENMOJI[hc]) {
                shapes = FALLBACK_OPENMOJI[hc];
            }
        }
        return shapes || [];
    }

    // -------------------------------------------------------------------------
    // 4. Emoji Detection in Text Strings
    // -------------------------------------------------------------------------
    var EMOTICON_MAP = {
        ":D": "1F603", ":-D": "1F603", "8-D": "1F603",
        ":)": "1F642", ":-)": "1F642", "=)": "1F642",
        ";)": "1F609", ";-)": "1F609",
        "<3": "2764",  ":heart:": "2764",
        ":fire:": "1F525", ":rocket:": "1F680", ":sparkles:": "2728"
    };

    function findEmojisInString(str) {
        var matches = [];
        if (!str || str.length === 0) return matches;

        var i = 0;
        while (i < str.length) {
            var code = str.charCodeAt(i);

            // 1. Surrogate Pairs (U+10000 - U+10FFFF, e.g. 🎪 1F3AA, 🍿 1F37F, 😃 1F603)
            if (code >= 0xD800 && code <= 0xDBFF && i + 1 < str.length) {
                var next = str.charCodeAt(i + 1);
                if (next >= 0xDC00 && next <= 0xDFFF) {
                    var cp = ((code - 0xD800) * 0x400) + (next - 0xDC00) + 0x10000;
                    var hex = cp.toString(16).toUpperCase();
                    var len = 2;
                    // Optional Variation Selector-16 (U+FE0F)
                    if (i + 2 < str.length && str.charCodeAt(i + 2) === 0xFE0F) len = 3;

                    matches.push({
                        start: i,
                        length: len,
                        char: str.substr(i, len),
                        hexcode: hex
                    });
                    i += len;
                    continue;
                }
            }

            // 2. BMP Emojis (U+2600 - U+27BF, U+2B50, e.g. ❤️ 2764, ✨ 2728, ⭐ 2B50)
            if ((code >= 0x2600 && code <= 0x27BF) || code === 0x2B50) {
                var len2 = 1;
                if (i + 1 < str.length && str.charCodeAt(i + 1) === 0xFE0F) len2 = 2;
                matches.push({
                    start: i,
                    length: len2,
                    char: str.substr(i, len2),
                    hexcode: code.toString(16).toUpperCase()
                });
                i += len2;
                continue;
            }

            // 3. Text Emoticons & Shortcodes
            var matchedEmo = null;
            for (var em in EMOTICON_MAP) {
                if (str.substr(i, em.length) === em) {
                    if (!matchedEmo || em.length > matchedEmo.char.length) {
                        matchedEmo = { char: em, hexcode: EMOTICON_MAP[em] };
                    }
                }
            }
            if (matchedEmo) {
                matches.push({
                    start: i,
                    length: matchedEmo.char.length,
                    char: matchedEmo.char,
                    hexcode: matchedEmo.hexcode
                });
                i += matchedEmo.char.length;
                continue;
            }

            i++;
        }
        return matches;
    }

    // -------------------------------------------------------------------------
    // 5. Typography Metrics & Sub-Pixel Advance Measurement
    // -------------------------------------------------------------------------
    function getTextDocument(layer) {
        if (!layer) return null;
        try {
            var st = layer.property("Source Text") || layer.property("ADBE Text Properties").property("ADBE Text Document");
            if (st && st.value) return st.value;
        } catch (e1) {}
        try {
            if (layer.text && layer.text.sourceText && layer.text.sourceText.value) return layer.text.sourceText.value;
        } catch (e2) {}
        return null;
    }

    function getTextBoxProperties(layer) {
        if (!layer) return null;
        var textDoc = getTextDocument(layer);
        if (!textDoc) return null;

        var isBox = false;
        var boxWidth = 0;
        var boxPos = [0, 0];
        try {
            if ((textDoc.boxText || layer.boxText) && (textDoc.boxTextSize || layer.boxTextSize)) {
                isBox = true;
                var bSize = textDoc.boxTextSize || layer.boxTextSize;
                boxWidth = bSize[0];
                if (textDoc.boxTextPos) boxPos = textDoc.boxTextPos;
                else if (layer.boxTextPos) boxPos = layer.boxTextPos;
            }
        } catch (eB) {}

        var fullText = String(textDoc.text || "");

        var just = "left";
        try {
            var j = (textDoc && textDoc.justification !== undefined) ? textDoc.justification : layer.justification;
            if (typeof ParagraphJustification !== "undefined") {
                if (j === ParagraphJustification.CENTER_JUSTIFY ||
                    j === ParagraphJustification.JUSTIFY_LAST_CENTER ||
                    (typeof ParagraphJustification.FULL_JUSTIFY_LASTCENTER !== "undefined" && j === ParagraphJustification.FULL_JUSTIFY_LASTCENTER)) {
                    just = "center";
                } else if (j === ParagraphJustification.RIGHT_JUSTIFY ||
                           j === ParagraphJustification.JUSTIFY_LAST_RIGHT ||
                           (typeof ParagraphJustification.FULL_JUSTIFY_LASTRIGHT !== "undefined" && j === ParagraphJustification.FULL_JUSTIFY_LASTRIGHT)) {
                    just = "right";
                }
            }
            if (j == 7414 || j == 7417 || j == 2 || j === "center" || j === "CENTER_JUSTIFY") {
                just = "center";
            } else if (j == 7413 || j == 7416 || j == 1 || j === "right" || j === "RIGHT_JUSTIFY") {
                just = "right";
            } else if (typeof j === "string") {
                var lj = j.toLowerCase();
                if (lj.indexOf("center") !== -1) just = "center";
                else if (lj.indexOf("right") !== -1) just = "right";
            }
        } catch (eJ) {}

        return {
            textDoc: textDoc,
            fullText: fullText,
            fontSize: textDoc.fontSize || 36,
            font: textDoc.font || "Arial",
            leading: textDoc.leading || ((textDoc.fontSize || 36) * 1.2),
            tracking: textDoc.tracking || 0,
            justification: just,
            isBox: isBox,
            boxWidth: boxWidth,
            boxPos: boxPos
        };
    }

    function createMeasureHelper(comp, props) {
        var mLayer = null;
        var mProp = null;
        var pipeRight = 0;
        var calib = (typeof AETextCalibration !== "undefined") ? AETextCalibration : (globalObj.AETextCalibration || null);

        if (comp && comp.layers && typeof comp.layers.addText === "function") {
            try {
                mLayer = comp.layers.addText("");
                mLayer.enabled = true;
                mLayer.transform.position.setValue([-9999, -9999, 0]);

                mProp = mLayer.property("Source Text") || mLayer.property("ADBE Text Properties").property("ADBE Text Document");
                if (mProp) {
                    var doc = mProp.value;
                    if (doc) {
                        doc.fontSize = props.fontSize;
                        if (props.font) {
                            doc.font = props.font;
                            try { doc.fontFamily = props.font; } catch (eFF) {}
                        }
                        doc.tracking = props.tracking;
                        try { doc.boxText = false; } catch (eB) {}
                        mProp.setValue(doc);
                    }
                    // Measure delimiter anchor "|"
                    try {
                        var dP = mProp.value;
                        if (dP) { dP.text = "|"; mProp.setValue(dP); }
                        else { mProp.setValue("|"); }
                        var rP = mLayer.sourceRectAtTime(0, false);
                        if (rP && typeof rP.width === "number") pipeRight = rP.left + rP.width;
                    } catch (eP) {}
                }
            } catch (eH) {
                mLayer = null;
            }
        }

        function measureRect(str) {
            if (!str) return { left: 0, top: 0, width: 0, height: 0 };
            if (mLayer && mProp) {
                try {
                    var d = mProp.value;
                    if (d) { d.text = str; mProp.setValue(d); }
                    else { mProp.setValue(str); }
                    var r = mLayer.sourceRectAtTime(0, false);
                    if (r && typeof r.width === "number") return r;
                } catch (eR) {}
            }
            return { left: 0, top: -(props.fontSize * 0.78), width: str.length * props.fontSize * 0.55, height: props.fontSize };
        }

        function measurePrefixAdvance(prefix) {
            if (!prefix) return 0;
            if (calib && typeof calib.measureLineWidth === "function") {
                try {
                    return calib.measureLineWidth(prefix, props.fontSize, props.font, props.tracking);
                } catch (eCal) {}
            }
            if (mLayer && mProp && pipeRight > 0) {
                try {
                    var rPipe = measureRect(prefix + "|");
                    return Math.max(0, (rPipe.left + rPipe.width) - pipeRight);
                } catch (eAdv) {}
            }
            return prefix.length * props.fontSize * 0.55;
        }

        function cleanup() {
            if (mLayer) {
                try { mLayer.remove(); } catch (eC) {}
                mLayer = null;
            }
        }

        return {
            measureRect: measureRect,
            measurePrefixAdvance: measurePrefixAdvance,
            cleanup: cleanup
        };
    }

    function computeVisualLines(props, measurer) {
        var fullText = props.fullText;
        if (!props.isBox || props.boxWidth <= 0) {
            return fullText.split(/\r\n|\r|\n/);
        }

        // 1. Check simulator / global AETextCalibration engine
        var calib = (typeof AETextCalibration !== "undefined") ? AETextCalibration : (globalObj.AETextCalibration || null);
        if (calib && typeof calib.wrapParagraph === "function") {
            try {
                var wrapped = calib.wrapParagraph(fullText, props.boxWidth, props.fontSize, props.font, {}, props.tracking);
                if (wrapped && wrapped.length > 0) {
                    var wLines = [];
                    for (var wi = 0; wi < wrapped.length; wi++) {
                        wLines.push(wrapped[wi].text);
                    }
                    return wLines;
                }
            } catch (eCW) {}
        }

        // 2. Fallback word-wrap using measurer
        var rawParas = fullText.split(/\r\n|\r|\n/);
        var resultLines = [];
        for (var pi = 0; pi < rawParas.length; pi++) {
            var para = rawParas[pi];
            var words = para.match(/\S+|\s+/g) || [];
            if (words.length === 0) {
                resultLines.push("");
                continue;
            }
            var curLine = "";
            for (var wi = 0; wi < words.length; wi++) {
                var token = words[wi];
                var testLine = curLine + token;
                var testW = measurer ? measurer.measurePrefixAdvance(testLine.replace(/\s+$/, "")) : 0;
                if (testW > props.boxWidth && curLine.replace(/\s+$/, "").length > 0) {
                    resultLines.push(curLine.replace(/\s+$/, ""));
                    curLine = token.replace(/^\s+/, "");
                } else {
                    curLine = testLine;
                }
            }
            if (curLine.length > 0) {
                resultLines.push(curLine.replace(/\s+$/, ""));
            }
        }
        return resultLines.length > 0 ? resultLines : rawParas;
    }

    // -------------------------------------------------------------------------
    // 6. Vector Shape Layer Builder
    // -------------------------------------------------------------------------
    function ensureSlider(fxGroup, name, val) {
        var sl = fxGroup.property(name) || fxGroup.addProperty("ADBE Slider Control");
        sl.name = name;
        if (sl.property(1) && sl.property(1).setValue) sl.property(1).setValue(val);
        return sl;
    }

    function addEmojiVectorGroup(masterContents, shapes, posX, posY, fontSize, sizeMultiplier) {
        var mult = (typeof sizeMultiplier === "number" ? sizeMultiplier : 130) / 100.0;
        var emoGrp = masterContents.addProperty("ADBE Vector Group");
        var emoContents = emoGrp.property("ADBE Vectors Group") || emoGrp.property("Contents") || emoGrp;

        var tr = emoGrp.property("ADBE Vector Transform Group") || emoGrp.property("Transform");
        if (tr) {
            var pAnchor = tr.property("ADBE Vector Anchor Point") || tr.property("Anchor Point");
            if (pAnchor && pAnchor.setValue) pAnchor.setValue([0, 0]);

            var pPos = tr.property("ADBE Vector Position") || tr.property("Position");
            if (pPos && pPos.setValue) {
                pPos.setValue([posX, posY]);
                try {
                    pPos.expression = [
                        'var ox = 0, oy = 0;',
                        'try { ox = thisLayer.effect("Offset X")(1).value; } catch(e1) {}',
                        'try { oy = thisLayer.effect("Offset Y")(1).value; } catch(e2) {}',
                        '[' + posX.toFixed(2) + ' + ox, ' + posY.toFixed(2) + ' + oy];'
                    ].join('\n');
                } catch (eP) {}
            }

            var pScale = tr.property("ADBE Vector Scale") || tr.property("Scale");
            if (pScale && pScale.setValue) {
                var scalePct = ((fontSize * mult / 72.0) * 100);
                pScale.setValue([scalePct, scalePct]);
                try {
                    pScale.expression = [
                        'try {',
                        '  var sz = thisLayer.effect("Emoji Size (px)")(1).value;',
                        '  var mult = thisLayer.effect("Emoji Size Multiplier %")(1).value / 100.0;',
                        '  var s = ((sz * mult) / 72.0) * 100.0;',
                        '  [s, s];',
                        '} catch(e) { value; }'
                    ].join('\n');
                } catch (eS) {}
            }
        }

        // Render subpaths and fills
        var inBrowser = (typeof window !== "undefined" && typeof document !== "undefined");
        var startIdx = inBrowser ? 0 : (shapes.length - 1);
        var endIdx   = inBrowser ? shapes.length : -1;
        var step     = inBrowser ? 1 : -1;

        for (var idx = startIdx; idx !== endIdx; idx += step) {
            var item = shapes[idx];
            var partGrp = emoContents.addProperty("ADBE Vector Group");
            partGrp.name = (item.l ? "Outline_" : "Color_") + (idx + 1);
            var partVecs = partGrp.property("ADBE Vectors Group") || partGrp.property("Contents") || partGrp;

            var subpaths = item.p ? item.p : [item];
            for (var spIdx = 0; spIdx < subpaths.length; spIdx++) {
                var sp = subpaths[spIdx];
                if (!sp.v || sp.v.length < 2) continue;

                var pathGrp = partVecs.addProperty("ADBE Vector Shape - Group");
                pathGrp.name = "Path_" + (spIdx + 1);
                var myShape = new ShapeClass();
                myShape.vertices   = sp.v;
                myShape.inTangents = sp.i || [];
                myShape.outTangents= sp.o || [];
                myShape.closed     = Boolean(sp.c);

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
                var swProp = strokeProp.property("ADBE Vector Stroke Width") || strokeProp.property("Stroke Width");
                if (swProp && swProp.setValue) swProp.setValue(item.sw);
            }
        }
        return emoGrp;
    }

    // -------------------------------------------------------------------------
    // 7. Core Replacement & Restoration Routines
    // -------------------------------------------------------------------------
    function replaceEmojisInLayer(comp, origLayer, options) {
        if (!comp || !origLayer) return null;
        var props = getTextBoxProperties(origLayer);
        if (!props) return null;

        var measurer = createMeasureHelper(comp, props);
        var lines = computeVisualLines(props, measurer);
        if (!lines || lines.length === 0) {
            measurer.cleanup();
            return null;
        }

        var firstBaselineY = 0;
        if (props.isBox) {
            var rFirst = measurer.measureRect(lines[0] || "A");
            var ascender = Math.abs(rFirst.top) || (props.fontSize * 0.78);
            firstBaselineY = props.boxPos[1] + ascender;
        }

        var lineStep = props.leading || (props.fontSize * 1.2);
        var origAP = (origLayer.transform && origLayer.transform.anchorPoint) ? origLayer.transform.anchorPoint.value : [0, 0, 0];

        var matchedEmojis = [];
        for (var vl = 0; vl < lines.length; vl++) {
            var lineStr = lines[vl];
            if (!lineStr || lineStr.length === 0) continue;

            var lineBaselineY = firstBaselineY + (vl * lineStep);
            var lineW = measurer.measurePrefixAdvance(lineStr);

            var lineLeftX = 0;
            if (props.isBox && props.boxWidth > 0) {
                if (props.justification === "center") {
                    lineLeftX = props.boxPos[0] + (props.boxWidth - lineW) / 2;
                } else if (props.justification === "right") {
                    lineLeftX = props.boxPos[0] + props.boxWidth - lineW;
                } else {
                    lineLeftX = props.boxPos[0];
                }
            } else {
                if (props.justification === "center") {
                    lineLeftX = -lineW / 2;
                } else if (props.justification === "right") {
                    lineLeftX = -lineW;
                } else {
                    lineLeftX = 0;
                }
            }

            var lineMatches = findEmojisInString(lineStr);
            for (var lm = 0; lm < lineMatches.length; lm++) {
                var m = lineMatches[lm];
                var prefix = lineStr.substring(0, m.start);
                var prefixAdv = measurer.measurePrefixAdvance(prefix);
                var segX = lineLeftX + prefixAdv;
                var charAdv = measurer.measurePrefixAdvance(prefix + m.char) - prefixAdv;
                if (charAdv <= 0) charAdv = props.fontSize * 0.7;

                var emojiCenterX = segX + (charAdv / 2);
                var emojiCenterY = lineBaselineY - (props.fontSize * 0.35);

                matchedEmojis.push({
                    char: m.char,
                    hexcode: m.hexcode,
                    posX: emojiCenterX,
                    posY: emojiCenterY
                });
            }
        }
        measurer.cleanup();

        if (matchedEmojis.length === 0) return { emojiCount: 0, shapeLayer: null };

        // 1. Hide Monochrome Font Emojis on Text Layer via native Text Animator
        try {
            var textPropGroup = origLayer.property("ADBE Text Properties");
            var animators = textPropGroup ? (textPropGroup.property("ADBE Text Animators") || textPropGroup.addProperty("ADBE Text Animators")) : null;
            if (animators) {
                var existingAnim = animators.property("Replace Color Emojis - Hide Font Emojis");
                if (existingAnim) try { existingAnim.remove(); } catch (eR) {}

                var anim = animators.addProperty("ADBE Text Animator");
                if (anim) {
                    anim.name = "Replace Color Emojis - Hide Font Emojis";
                    var animProps = anim.property("ADBE Text Animator Properties");
                    var opProp = animProps ? animProps.addProperty("ADBE Text Opacity") : null;
                    if (opProp && opProp.setValue) opProp.setValue(0);

                    var selectors = anim.property("ADBE Text Selectors") || anim.property("Selectors");
                    var fullMatches = findEmojisInString(props.fullText);
                    var totalChars = Math.max(1, props.fullText.length);

                    for (var fi = 0; fi < fullMatches.length; fi++) {
                        var fm = fullMatches[fi];
                        var sel = (fi === 0 && selectors.numProperties > 0) ? selectors.property(1) : selectors.addProperty("ADBE Text Selector");
                        if (sel) {
                            try {
                                if (sel.property("ADBE Text Range Units")) sel.property("ADBE Text Range Units").setValue(2); // Index units
                                sel.property("ADBE Text Index Start").setValue(fm.start);
                                sel.property("ADBE Text Index End").setValue(fm.start + fm.length);
                            } catch (eSel) {
                                // Fallback to percentage units
                                try {
                                    sel.property("ADBE Text Percent Start").setValue((fm.start / totalChars) * 100);
                                    sel.property("ADBE Text Percent End").setValue(((fm.start + fm.length) / totalChars) * 100);
                                } catch (eP2) {}
                            }
                        }
                    }
                }
            }
        } catch (eAnim) {}

        // 2. Create Master Shape Layer
        var shapeLayer = comp.layers.addShape();
        shapeLayer.name = origLayer.name + " - Color Emojis";
        shapeLayer.comment = "AE_COLOR_EMOJI_CHILD";
        shapeLayer.parent = origLayer;
        shapeLayer.transform.anchorPoint.setValue([0, 0, 0]);
        shapeLayer.transform.position.setValue([-origAP[0], -origAP[1], 0]);
        shapeLayer.transform.scale.setValue([100, 100, 100]);

        var effMultiplier = (typeof options.sizeMultiplier === "number" ? options.sizeMultiplier : 130);

        // Attach effect sliders
        var fx = shapeLayer.property("ADBE Effect Parade") || shapeLayer.property("Effects");
        if (fx) {
            ensureSlider(fx, "Emoji Source (1=OM,2=TW,3=Flat,4=Blk)", (options.sourceId === "twemoji_color" ? 2 : 1));
            ensureSlider(fx, "Emoji Size (px)", props.fontSize);
            ensureSlider(fx, "Emoji Size Multiplier %", effMultiplier);
            ensureSlider(fx, "Outline Width %", 100);
            var chk = fx.addProperty("ADBE Checkbox Control");
            chk.name = "Show Outlines";
            if (chk.property(1)) chk.property(1).setValue(1);
            ensureSlider(fx, "Offset X", (typeof options.offsetX === "number" ? options.offsetX : 0));
            ensureSlider(fx, "Offset Y", (typeof options.offsetY === "number" ? options.offsetY : 0));
        }

        var masterContents = shapeLayer.property("ADBE Root Vectors Group") || shapeLayer.property("Contents") || shapeLayer;

        for (var mi = 0; mi < matchedEmojis.length; mi++) {
            var item = matchedEmojis[mi];
            var shapes = getShapesForEmoji(item.hexcode, options.sourceId);
            var grp = addEmojiVectorGroup(masterContents, shapes, item.posX, item.posY, props.fontSize, effMultiplier);
            grp.name = "Emoji " + item.char + " [U+" + item.hexcode + "]";
        }

        return { emojiCount: matchedEmojis.length, shapeLayer: shapeLayer };
    }

    function removeEmojisAndRestore(comp) {
        if (!comp || !comp.layers) return 0;
        var count = 0;
        var len = comp.layers.length || (comp.layers._layers ? comp.layers._layers.length : 0);

        for (var i = len; i >= 1; i--) {
            var l = comp.layer ? comp.layer(i) : (comp.layers._layers ? comp.layers._layers[i - 1] : null);
            if (!l) continue;
            if (l.comment === "AE_COLOR_EMOJI_CHILD" || (l.name && (l.name.indexOf("- Color Emojis") !== -1 || l.name.indexOf("[Emoji]") !== -1 || l.name.indexOf("[Text]") !== -1))) {
                try { l.remove(); count++; } catch (eR) {}
            } else if (l.enabled === false && l.guideLayer === true) {
                l.enabled = true;
                l.guideLayer = false;
            }
        }

        for (var j = 1; j <= (comp.layers.length || 0); j++) {
            var tl = comp.layer ? comp.layer(j) : (comp.layers._layers ? comp.layers._layers[j - 1] : null);
            if (!tl) continue;
            try {
                var anims = tl.property("ADBE Text Properties").property("ADBE Text Animators");
                if (anims) {
                    var aCount = anims.numProperties || (anims._list ? anims._list.length : 0);
                    for (var a = aCount; a >= 1; a--) {
                        var anim = anims.property ? anims.property(a) : anims._list[a - 1];
                        if (anim && anim.name && anim.name.indexOf("Hide Font Emojis") !== -1) {
                            try { anim.remove(); } catch (eAR) {}
                        }
                    }
                }
            } catch (eA) {}
        }
        return count;
    }

    // -------------------------------------------------------------------------
    // 8. ScriptUI User Interface
    // -------------------------------------------------------------------------
    function buildUI(thisObj) {
        var isDockable = (typeof Panel !== "undefined" && thisObj instanceof Panel);
        var WinClass = (typeof Window !== "undefined") ? Window : (globalObj.Window || null);
        var win = isDockable ? thisObj : (WinClass ? new WinClass("palette", SCRIPT_TITLE + " " + SCRIPT_VERSION, undefined, { resizeable: true }) : null);
        if (!win) return null;

        win.orientation = "column";
        win.alignChildren = ["fill", "top"];
        win.spacing = 8;
        win.margins = 10;

        // Header Panel
        var pnlHeader = win.add("panel", undefined, SCRIPT_TITLE + " " + SCRIPT_VERSION);
        pnlHeader.orientation = "column";
        pnlHeader.alignChildren = ["fill", "top"];
        pnlHeader.spacing = 3;
        pnlHeader.margins = [8, 6, 8, 6];

        var lblSub = pnlHeader.add("statictext", undefined, "Replaces monochrome font emojis with native color vector shapes");
        try { lblSub.graphics.foregroundColor = win.graphics.newPen(win.graphics.PenType.SOLID_COLOR, [0.35, 0.75, 1.0, 1.0], 1); } catch (eG) {}

        // Style Selector
        var grpStyle = win.add("group");
        grpStyle.orientation = "row";
        grpStyle.alignChildren = ["left", "center"];
        grpStyle.spacing = 8;
        grpStyle.add("statictext", undefined, "Vector Style:");
        var ddStyle = grpStyle.add("dropdownlist", undefined, [
            "1. OpenMoji Color (Outlined Vectors)",
            "2. Twemoji Flat Color (Modern Flat Shapes)"
        ]);
        ddStyle.selection = 0;
        ddStyle.alignment = ["fill", "center"];

        // Utility Actions (Restore + Demo Text)
        var grpSubBtns = win.add("group");
        grpSubBtns.orientation = "row";
        grpSubBtns.alignChildren = ["fill", "center"];
        grpSubBtns.spacing = 6;
        var btnRestore = grpSubBtns.add("button", undefined, "↺ Restore Original Text");
        var btnDemo    = grpSubBtns.add("button", undefined, "📝 Demo Text");
        btnRestore.preferredSize = [-1, 26];
        btnDemo.preferredSize    = [-1, 26];

        // Primary Action (Prominent big button at bottom)
        var btnExecute = win.add("button", undefined, "✨ Replace Font Emojis with Color Emojis");
        btnExecute.alignment = ["fill", "center"];
        btnExecute.preferredSize = [-1, 36];

        function getActiveComp() {
            var activeApp = (typeof app !== "undefined") ? app : globalObj.app;
            if (activeApp && activeApp.project && activeApp.project.activeItem) {
                var itm = activeApp.project.activeItem;
                if (typeof CompItem !== "undefined" && itm instanceof CompItem) return itm;
                if (itm.typeName === "Composition" || itm.layers) return itm;
            }
            return null;
        }

        function getSelectedTextLayer(comp) {
            if (!comp) return null;
            var sel = comp.selectedLayers;
            if (sel && sel.length > 0) {
                for (var i = 0; i < sel.length; i++) {
                    var l = sel[i];
                    if (l && (l.matchName === "ADBE Text Layer" || l.property("Source Text"))) return l;
                    if (l && l.parent && (l.parent.matchName === "ADBE Text Layer" || l.parent.property("Source Text"))) return l.parent;
                }
            }
            return null;
        }

        btnDemo.onClick = function () {
            var comp = getActiveComp();
            if (!comp) { alert("Please open a composition first."); return; }
            var demoStr = "Hello After Effects! 😃 We now have color emojis! 🚀🔥 With red heart ❤️ and smile :D ✨";
            var demoLayer = comp.layers.addText(demoStr);
            demoLayer.name = "Demo Text with Emojis";
            if (demoLayer.transform) {
                demoLayer.transform.position.setValue([Math.round(comp.width / 2), Math.round(comp.height / 2), 0]);
            }
            try {
                var doc = getTextDocument(demoLayer);
                if (doc) {
                    doc.fontSize = 54;
                    doc.fillColor = [1, 1, 1];
                    if (typeof ParagraphJustification !== "undefined") doc.justification = ParagraphJustification.CENTER_JUSTIFY;
                    demoLayer.property("Source Text").setValue(doc);
                }
            } catch (eD) {}
            demoLayer.selected = true;
        };

        btnRestore.onClick = function () {
            var comp = getActiveComp();
            if (!comp) { alert("No active composition found."); return; }
            var removed = removeEmojisAndRestore(comp);
            alert("Restore complete! Cleaned up " + removed + " emoji / helper layer(s) and restored original text layer(s).");
        };

        btnExecute.onClick = function () {
            var comp = getActiveComp();
            if (!comp) { alert("Please open a composition first."); return; }
            var textLayer = getSelectedTextLayer(comp);
            if (!textLayer) {
                btnDemo.onClick();
                textLayer = getSelectedTextLayer(comp);
            }
            if (!textLayer) { alert("Please select a text layer containing emojis."); return; }

            var styleId = (ddStyle.selection && ddStyle.selection.index === 1) ? "twemoji_color" : "openmoji_color";
            var res = replaceEmojisInLayer(comp, textLayer, { sourceId: styleId, sizeMultiplier: 130, offsetX: 0, offsetY: 0 });

            if (!res || res.emojiCount === 0) {
                alert("No emojis detected in text layer '" + textLayer.name + "'.");
                return;
            }
        };

        if (win && !isDockable && typeof win.show === "function") {
            try { win.center(); } catch (eC) {}
            try { win.show(); } catch (eS) {}
        } else if (win && win.layout) {
            try { win.layout.layout(true); } catch (eL) {}
        }

        win._btnExecute = btnExecute;
        win._btnRestore = btnRestore;
        win._btnDemo    = btnDemo;
        try { globalObj._aeReplaceColorEmojisWin = win; } catch (eGWin) {}

        return win;
    }

    buildUI(thisObj);

})(this);
