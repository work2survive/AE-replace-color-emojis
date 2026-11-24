const fs = require("fs");
const vm = require("vm");
const path = require("path");

function createMockAEP() {
  function CompItem() {}

  function createVectorGroup(name) {
    const grp = {
      name: name,
      _children: [],
      property: function (propName) {
        if (propName === "ADBE Vector Transform Group") {
          return {
            property: function (trProp) {
              return { value: [0, 0], setValue: function (v) { this.value = v; } };
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
                  property: function (n) { return this._list.find(a => a.name === n); },
                  addProperty: function (n) {
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
                          if (!this._selectors) {
                            this._selectors = {
                              _selList: [],
                              get numProperties() { return this._selList.length; },
                              property: function (i) { return this._selList[i - 1]; },
                              addProperty: function (selType) {
                                const s = {
                                  name: selType,
                                  property: function (propName) {
                                    return { setValue: function (v) { this.value = v; } };
                                  }
                                };
                                this._selList.push(s);
                                return s;
                              }
                            };
                          }
                          return this._selectors;
                        }
                        return null;
                      }
                    };
                    this._list.push(anim);
                    return anim;
                  }
                };
              }
              return {
                property: (sub) => (sub === "ADBE Text Animators" ? this._animators : null)
              };
            }
            return null;
          },
          sourceRectAtTime: function () {
            return { left: 0, top: -38, width: (this._textDoc.text.length * 26), height: 48 };
          },
          remove: function () {
            const idx = mockComp.layers._layers.indexOf(this);
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
          enabled: true,
          guideLayer: false,
          transform: {
            position: { value: [0, 0, 0], setValue: function (v) { this.value = v; } },
            anchorPoint: { value: [0, 0, 0], setValue: function (v) { this.value = v; } },
            scale: { value: [100, 100, 100], setValue: function (v) { this.value = v; } }
          },
          _effects: [],
          _vectors: [],
          property: function (name) {
            if (name === "ADBE Effect Parade" || name === "Effects") {
              return {
                property: (en) => sl._effects.find(e => e.name === en),
                addProperty: (type) => {
                  const eff = { name: type, property: (idx) => ({ value: null, setValue: function (v) { this.value = v; } }) };
                  sl._effects.push(eff);
                  return eff;
                }
              };
            }
            if (name === "ADBE Root Vectors Group" || name === "Contents") {
              return {
                get numProperties() { return sl._vectors.length; },
                property: (idx) => sl._vectors[idx - 1],
                addProperty: function (groupType) {
                  const grp = createVectorGroup(groupType);
                  sl._vectors.push(grp);
                  return grp;
                }
              };
            }
            return null;
          },
          remove: function () {
            const idx = mockComp.layers._layers.indexOf(this);
            if (idx !== -1) mockComp.layers._layers.splice(idx, 1);
          }
        };
        mockComp.layers._layers.push(sl);
        return sl;
      }
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
      selection: { index: 0 },
      add: function (w2, b2, t2) { return makeUIElement(w2, t2); },
      preferredSize: {},
      alignment: [],
      margins: [],
      spacing: 0,
      graphics: { foregroundColor: null, newPen: () => ({}) }
    };
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

  console.log("▶ Loading AE_Replace_Color_Emojis.jsx into VM...");
  vm.createContext(sandbox);
  vm.runInContext(code, sandbox);
  console.log("✔ Script initialized. ScriptUI UI elements count:", uiElements.length);

  // 1. Trigger Demo Text creation
  console.log("\n▶ Test 1: Create Demo Text with Emojis");
  const btnDemo = uiElements.find(e => e.text === "📝 Demo Text");
  if (!btnDemo) throw new Error("btnDemo button not found!");
  btnDemo.onClick();

  const demoLayer = mockComp.layers._layers.find(l => l.name === "Demo Text with Emojis");
  if (!demoLayer) throw new Error("Demo text layer was not created!");
  console.log("✔ Demo text created:", JSON.stringify(demoLayer._textDoc.text));
  mockComp.selectedLayers = [demoLayer];

  // 2. Scan Emojis Preview
  console.log("\n▶ Test 2: Scan Emojis in selected text");
  const btnScan = uiElements.find(e => e.text === "👀 Scan Emojis");
  btnScan.onClick();
  const lastAlert = alerts[alerts.length - 1];
  console.log("✔ Scan alert preview:", lastAlert.replace(/\n+/g, " | "));
  if (lastAlert.indexOf("Found") === -1) throw new Error("Scan did not detect emojis!");

  // 3. Execute Calculation Method (Default)
  console.log("\n▶ Test 3: Execute Calculation Method (Intact Text Layer)");
  const btnExecute = uiElements.find(e => e.text === "✨ Replace Font Emojis with Color Emojis");
  btnExecute.onClick();

  const colorEmojiShape = mockComp.layers._layers.find(l => l.name.indexOf("- Color Emojis") !== -1);
  if (!colorEmojiShape) throw new Error("Master Color Emojis shape layer was not created!");
  console.log("✔ Color Emojis shape layer created:", colorEmojiShape.name);
  console.log("✔ Effect sliders attached:", colorEmojiShape._effects.map(e => e.name));
  console.log("✔ Vector emoji groups populated:", colorEmojiShape._vectors.length);
  if (colorEmojiShape._vectors.length === 0) throw new Error("Vector groups were not populated!");

  // Check Text Animator
  const animators = demoLayer._animators;
  const hideAnim = animators.property("Replace Color Emojis - Hide Font Emojis");
  if (!hideAnim) throw new Error("Hide Font Emojis animator was not attached to original text layer!");
  console.log("✔ Text Animator attached to original layer to hide monochrome font emojis (Opacity = 0%)");

  // 4. Restore original text layer
  console.log("\n▶ Test 4: Restore Original Text Layer");
  const btnRestore = uiElements.find(e => e.text === "↺ Remove Emojis & Restore Original Text");
  btnRestore.onClick();
  if (mockComp.layers._layers.find(l => l.name.indexOf("- Color Emojis") !== -1)) {
    throw new Error("Emoji shape layer was not removed during restore!");
  }
  if (animators._list.find(a => a.name === "Replace Color Emojis - Hide Font Emojis")) {
    throw new Error("Hide animator was not removed during restore!");
  }
  console.log("✔ Original text layer restored cleanly!");

  // 5. Execute Split Method (Decomposition)
  console.log("\n▶ Test 5: Execute Split Method (Decomposition)");
  const methodDD = uiElements.filter(e => e.type === "dropdownlist")[0];
  methodDD.selection = { index: 1 }; // Split Method
  mockComp.selectedLayers = [demoLayer];
  btnExecute.onClick();

  console.log("✔ Split layers created. Total comp layers:", mockComp.layers._layers.length);
  const textSegments = mockComp.layers._layers.filter(l => l.name.indexOf("[Text]") !== -1);
  const emojiSegments = mockComp.layers._layers.filter(l => l.name.indexOf("[Emoji]") !== -1);
  console.log("✔ Created", textSegments.length, "text segment layers and", emojiSegments.length, "emoji shape layers.");
  if (emojiSegments.length === 0) throw new Error("No emoji layers created in Split Method!");
  if (demoLayer.enabled !== false || demoLayer.guideLayer !== true) {
    throw new Error("Original text layer was not marked as hidden guideline!");
  }
  console.log("✔ Original text layer safely hidden as guideline (guideLayer=true, enabled=false)");

  // 6. Restore after Split Method
  console.log("\n▶ Test 6: Restore after Split Method");
  btnRestore.onClick();
  if (demoLayer.enabled !== true || demoLayer.guideLayer !== false) {
    throw new Error("Original text layer was not unhidden after restore!");
  }
  const remainingChildren = mockComp.layers._layers.filter(l => l.comment === "AE_COLOR_EMOJI_CHILD");
  if (remainingChildren.length > 0) {
    throw new Error("Remaining child layers after restore: " + remainingChildren.length);
  }
  console.log("✔ All split layers removed and original text layer completely restored!");

  console.log("\n========================================================");
  console.log("🎉 ALL TESTS PASSED SUCCESSFULLY!");
  console.log("========================================================");
}

runSuite();
