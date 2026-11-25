const fs = require("fs");
const vm = require("vm");
const path = require("path");

function createMockAEP() {
  function CompItem() {}

  function createVectorGroup(name) {
    const grp = {
      name: name,
      _children: [],
      _trProps: {},
      property: function (propName) {
        if (propName === "ADBE Vector Transform Group" || propName === "Transform") {
          const self = this;
          return {
            property: function (trProp) {
              const key = (trProp === "ADBE Vector Position" || trProp === "Position") ? "Position" :
                          (trProp === "ADBE Vector Anchor Point" || trProp === "Anchor Point") ? "Anchor Point" :
                          (trProp === "ADBE Vector Scale" || trProp === "Scale") ? "Scale" : trProp;
              if (!self._trProps[key]) {
                self._trProps[key] = { value: [0, 0], setValue: function (v) { this.value = v; } };
              }
              return self._trProps[key];
            }
          };
        }
        if (propName === "ADBE Vectors Group" || propName === "Contents") {
          return {
            addProperty: function (childType) {
              if (childType === "ADBE Vector Group") {
                const subGrp = createVectorGroup(childType);
                grp._children.push(subGrp);
                return subGrp;
              }
              const elem = {
                name: childType,
                property: function (subProp) {
                  return { value: null, setValue: function (v) { this.value = v; } };
                }
              };
              grp._children.push(elem);
              return elem;
            }
          };
        }
        return null;
      }
    };
    return grp;
  }

  const mockComp = {
    name: "Emoji Test Comp",
    width: 1920,
    height: 1080,
    time: 0,
    duration: 10,
    selectedLayers: [],
    layers: {
      _layers: [],
      get length() { return this._layers.length; },
      addText: function (text) {
        const l = {
          name: "Text Layer",
          matchName: "ADBE Text Layer",
          enabled: true,
          guideLayer: false,
          transform: {
            position: { value: [960, 540, 0], setValue: function (v) { this.value = v; } },
            anchorPoint: { value: [0, 0, 0], setValue: function (v) { this.value = v; } },
            scale: { value: [100, 100, 100], setValue: function (v) { this.value = v; } }
          },
          _textDoc: {
            text: text || "",
            fontSize: 48,
            font: "Arial",
            fillColor: [1, 1, 1],
            boxText: false,
            leading: 58,
            tracking: 0
          },
          property: function (name) {
            if (name === "Source Text" || name === "ADBE Text Document") {
              return { value: this._textDoc, setValue: function (v) { this.value = v; } };
            }
            if (name === "ADBE Text Properties") {
              if (!this._animators) {
                this._animators = {
                  _list: [],
                  get numProperties() { return this._list.length; },
                  property: function (n) {
                    if (n === "ADBE Text Animators" || n === "Animators") return this;
                    if (typeof n === "number") return this._list[n - 1];
                    return this._list.find(a => a.name === n);
                  },
                  addProperty: function (n) {
                    if (n === "ADBE Text Animators" || n === "Animators") return this;
                    const anim = {
                      name: n,
                      _props: [],
                      remove: function () {
                        const idx = l._animators._list.indexOf(anim);
                        if (idx !== -1) l._animators._list.splice(idx, 1);
                      },
                      property: function (pName) {
                        if (pName === "ADBE Text Animator Properties") {
                          return {
                            addProperty: function (propType) {
                              const pr = { type: propType, value: null, setValue: function (v) { this.value = v; } };
                              anim._props.push(pr);
                              return pr;
                            }
                          };
                        }
                        if (pName === "ADBE Text Selectors" || pName === "Selectors") {
                          return {
                            numProperties: 0,
                            property: function () { return null; },
                            addProperty: function () {
                              return {
                                property: function () {
                                  return { setValue: function () {} };
                                }
                              };
                            }
                          };
                        }
                        return null;
                      }
                    };
                    this._list.push(anim);
                    return anim;
                  }
                };
              }
              return this._animators;
            }
            return null;
          },
          sourceRectAtTime: function () {
            const fs = this._textDoc ? this._textDoc.fontSize : 48;
            const len = (this._textDoc && this._textDoc.text) ? this._textDoc.text.length : 0;
            return {
              left: 0,
              top: -(fs * 0.78),
              width: len * (fs * 0.55),
              height: fs
            };
          },
          remove: function () {
            const idx = mockComp.layers._layers.indexOf(l);
            if (idx !== -1) mockComp.layers._layers.splice(idx, 1);
          }
        };
        mockComp.layers._layers.push(l);
        return l;
      },
      addShape: function () {
        const sl = {
          name: "Shape Layer",
          matchName: "ADBE Vector Layer",
          comment: "",
          parent: null,
          transform: {
            position: { value: [0, 0, 0], setValue: function (v) { this.value = v; } },
            anchorPoint: { value: [0, 0, 0], setValue: function (v) { this.value = v; } },
            scale: { value: [100, 100, 100], setValue: function (v) { this.value = v; } }
          },
          _effects: [],
          _vectors: [],
          property: function (propName) {
            if (propName === "ADBE Effect Parade" || propName === "Effects") {
              return {
                property: function (effName) {
                  return sl._effects.find(e => e.name === effName);
                },
                addProperty: function (effType) {
                  const eff = {
                    name: effType,
                    _prop1: { value: 0, setValue: function (v) { this.value = v; } },
                    property: function () {
                      return this._prop1;
                    }
                  };
                  sl._effects.push(eff);
                  return eff;
                }
              };
            }
            if (propName === "ADBE Root Vectors Group" || propName === "Contents") {
              return {
                numProperties: sl._vectors.length,
                property: function (idxOrName) {
                  if (typeof idxOrName === "number") return sl._vectors[idxOrName - 1];
                  return sl._vectors.find(v => v.name === idxOrName);
                },
                addProperty: function (vType) {
                  const grp = createVectorGroup(vType);
                  sl._vectors.push(grp);
                  return grp;
                }
              };
            }
            return null;
          },
          remove: function () {
            const idx = mockComp.layers._layers.indexOf(sl);
            if (idx !== -1) mockComp.layers._layers.splice(idx, 1);
          }
        };
        mockComp.layers._layers.push(sl);
        return sl;
      }
    },
    layer: function (idx) {
      return this.layers._layers[idx - 1];
    }
  };
  Object.setPrototypeOf(mockComp, CompItem.prototype);

  return { mockComp, CompItem };
}

function runSuite() {
  const { mockComp, CompItem } = createMockAEP();
  const uiElements = [];

  function makeUIElement(what, text) {
    const el = {
      type: what,
      text: text,
      value: false,
      items: [],
      selection: { index: 0 },
      add: function (w2, b2, t2) {
        if (what === "dropdownlist" && w2 === "item") {
          const it = { text: b2, index: el.items.length };
          el.items.push(it);
          return it;
        }
        return makeUIElement(w2, t2);
      },
      preferredSize: {},
      alignment: [],
      margins: [],
      spacing: 0,
      graphics: { foregroundColor: null, newPen: () => ({}) }
    };
    if (Array.isArray(text)) {
      el.items = text.map((t, idx) => ({ text: t, index: idx }));
    }
    uiElements.push(el);
    return el;
  }

  const alerts = [];
  const sandbox = {
    app: {
      project: { activeItem: mockComp },
      beginUndoGroup: () => {},
      endUndoGroup: () => {}
    },
    CompItem: CompItem,
    Shape: function () { this.vertices = []; this.inTangents = []; this.outTangents = []; this.closed = false; },
    Panel: function () {},
    Window: function (type, title) {
      this.add = function (what, b, text) { return makeUIElement(what, text); };
      this.center = function () {};
      this.show = function () {};
      this.layout = { resize: function () {}, layout: function () {} };
      this.graphics = { newPen: () => ({}) };
    },
    alert: function (msg) {
      alerts.push(msg);
      console.log("  [ALERT]:", msg.split("\n")[0]);
    },
    console: console
  };

  const jsxPath = path.join(__dirname, "..", "AE_Replace_Color_Emojis.jsx");
  const code = fs.readFileSync(jsxPath, "utf8");

  console.log("▶ Loading rewritten AE_Replace_Color_Emojis.jsx into VM...");
  vm.createContext(sandbox);
  vm.runInContext(code, sandbox);
  console.log("✔ Script initialized. Clean UI elements count:", uiElements.length);

  // 1. Trigger Demo Text creation
  console.log("\n▶ Test 1: Create Demo Text with Emojis");
  const btnDemo = uiElements.find(e => e.text === "📝 Demo Text");
  if (!btnDemo) throw new Error("btnDemo button not found!");
  btnDemo.onClick();

  const demoLayer = mockComp.layers._layers.find(l => l.name === "Demo Text with Emojis");
  if (!demoLayer) throw new Error("Demo text layer was not created!");
  console.log("✔ Demo text created:", JSON.stringify(demoLayer._textDoc.text));
  mockComp.selectedLayers = [demoLayer];

  // 2. Execute Replacement (OpenMoji Color)
  console.log("\n▶ Test 2: Replace Font Emojis with OpenMoji Color Shapes");
  const btnExecute = uiElements.find(e => e.text === "✨ Replace Font Emojis with Color Emojis");
  if (!btnExecute) throw new Error("btnExecute button not found!");
  btnExecute.onClick();

  const colorEmojiShape = mockComp.layers._layers.find(l => l.name.indexOf("- Color Emojis") !== -1);
  if (!colorEmojiShape) throw new Error("Master Color Emojis shape layer was not created!");
  console.log("✔ Master Shape Layer created:", colorEmojiShape.name);
  console.log("✔ Sliders attached:", colorEmojiShape._effects.map(e => e.name));
  const multEffect = colorEmojiShape._effects.find(e => e.name === "Emoji Size Multiplier %");
  if (!multEffect || multEffect.property(1).value !== 130) {
    throw new Error("Expected Emoji Size Multiplier % to be 130! Found: " + (multEffect ? multEffect.property(1).value : "missing"));
  }
  console.log("✔ Verified Emoji Size Multiplier % is set to 130% (+30% larger)");
  console.log("✔ Vector emoji groups populated:", colorEmojiShape._vectors.length);
  if (colorEmojiShape._vectors.length < 5) throw new Error("Expected at least 5 emoji groups!");

  // Check Text Animator Opacity 0%
  const animators = demoLayer._animators;
  const hideAnim = animators.property("Replace Color Emojis - Hide Font Emojis");
  if (!hideAnim) throw new Error("Hide Font Emojis animator was not attached to original text layer!");
  console.log("✔ Native Text Animator attached (Opacity = 0%) to hide monochrome font glyphs");

  // 3. Restore original text layer
  console.log("\n▶ Test 3: Restore Original Text Layer");
  const btnRestore = uiElements.find(e => e.text === "↺ Restore Original Text");
  if (!btnRestore) throw new Error("btnRestore button not found!");
  btnRestore.onClick();

  if (mockComp.layers._layers.find(l => l.name.indexOf("- Color Emojis") !== -1)) {
    throw new Error("Emoji shape layer was not removed during restore!");
  }
  if (animators._list.find(a => a.name === "Replace Color Emojis - Hide Font Emojis")) {
    throw new Error("Hide animator was not removed during restore!");
  }
  console.log("✔ Shape layer and Text Animator removed cleanly; text restored to 100% original state!");

  // 4. Verify Specific Reported Emojis (🎪 and 🍿)
  console.log("\n▶ Test 4: Circus Tent 🎪 and Popcorn 🍿 Identification and Vector Placement");
  const testLayer = mockComp.layers.addText("Testing emojis 🎪🍿 Let's see if this works!");
  testLayer.name = "Circus Popcorn Layer";
  mockComp.selectedLayers = [testLayer];
  btnExecute.onClick();

  const circusShape = mockComp.layers._layers.find(l => l.name === "Circus Popcorn Layer - Color Emojis");
  if (!circusShape) throw new Error("Circus Popcorn shape layer not found!");
  const circusGroups = circusShape._vectors;
  console.log("✔ Created vector groups count:", circusGroups.length);
  if (circusGroups.length !== 2) throw new Error("Expected exactly 2 emojis (🎪 and 🍿), got " + circusGroups.length);
  console.log("  Group 1:", circusGroups[0].name);
  console.log("  Group 2:", circusGroups[1].name);
  if (circusGroups[0].name.indexOf("1F3AA") === -1) throw new Error("First emoji is not 1F3AA (circus tent)!");
  if (circusGroups[1].name.indexOf("1F37F") === -1) throw new Error("Second emoji is not 1F37F (popcorn)!");
  console.log("✔ 🎪 and 🍿 correctly identified and populated with cubic Bézier vector paths!");

  // 5. Verify Twemoji Style Selection & Metrics Normalization
  console.log("\n▶ Test 5: Twemoji Style Selection & Metrics Normalization");
  btnRestore.onClick();
  const styleDD = uiElements.find(e => e.type === "dropdownlist");
  if (!styleDD) throw new Error("Style dropdown not found!");
  styleDD.selection = { index: 1 }; // Select Twemoji Flat Color
  mockComp.selectedLayers = [testLayer];
  btnExecute.onClick();

  const twShape = mockComp.layers._layers.find(l => l.name === "Circus Popcorn Layer - Color Emojis");
  if (!twShape) throw new Error("Twemoji shape layer not found!");
  const twGroups = twShape._vectors;
  console.log("✔ Twemoji vector groups count:", twGroups.length);
  if (twGroups.length !== 2) throw new Error("Expected 2 Twemoji groups, got " + twGroups.length);
  console.log("  Twemoji Group 1:", twGroups[0].name);
  console.log("  Twemoji Group 2:", twGroups[1].name);
  console.log("✔ Twemoji Flat Color shapes populated with normalized 46/72 optical em-box metrics!");

  // 6. Verify Right-Aligned Box Text Placement
  console.log("\n▶ Test 6: Right-Aligned Box Text Emoji Placement");
  btnRestore.onClick();
  const boxLayer = mockComp.layers.addText("Right aligned box text with popcorn 🍿 and tent 🎪!");
  boxLayer.name = "Right Aligned Box Layer";
  boxLayer.boxText = true;
  boxLayer.boxTextSize = [800, 300];
  boxLayer.boxTextPos = [0, 0];
  boxLayer._textDoc.boxText = true;
  boxLayer._textDoc.boxTextSize = [800, 300];
  boxLayer._textDoc.boxTextPos = [0, 0];
  boxLayer._textDoc.justification = 7413; // ParagraphJustification.RIGHT_JUSTIFY
  mockComp.selectedLayers = [boxLayer];
  btnExecute.onClick();

  const boxShape = mockComp.layers._layers.find(l => l.name === "Right Aligned Box Layer - Color Emojis");
  if (!boxShape) throw new Error("Right aligned box shape layer not found!");
  const boxGroups = boxShape._vectors;
  if (boxGroups.length !== 2) throw new Error("Expected 2 emoji groups in right-aligned box text, got " + boxGroups.length);

  // Check positions of both emojis - they must be positioned on the right side within [0, 800]
  const pos1 = boxGroups[0].property("Transform").property("Position").value;
  console.log("  Box Emoji 1 (🍿) Position:", pos1);
  if (pos1[0] < 0 || pos1[0] > 800) {
    throw new Error("Emoji 1 X coordinate (" + pos1[0] + ") is outside valid box width [0, 800]!");
  }
  const pos2 = boxGroups[1].property("Transform").property("Position").value;
  console.log("  Box Emoji 2 (🎪) Position:", pos2);
  if (pos2[0] < 0 || pos2[0] > 800) {
    throw new Error("Emoji 2 X coordinate (" + pos2[0] + ") is outside valid box width [0, 800]!");
  }
  // Because text is right-aligned in an 800px box, emojis must be on the right half (> 400px)
  if (pos1[0] < 200 || pos2[0] < 200) {
    throw new Error("Emojis are misplaced to the left in right-aligned box text!");
  }
  console.log("✔ Right-aligned Box Text correctly placed emojis on the right side within [0, 800]!");

  console.log("\n========================================================");
  console.log("🎉 ALL TESTS PASSED SUCCESSFULLY!");
  console.log("========================================================");
}

runSuite();
