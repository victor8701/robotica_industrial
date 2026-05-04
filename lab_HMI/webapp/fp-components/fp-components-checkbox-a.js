


// OmniCore App SDK 1.6.0



// Copyright (c) 2020-2026 ABB

// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software (the "Software"), to deal in the Software without
// restriction, including without limitation the rights to use, copy, modify,
// merge, publish, distribute, sublicense, and/or sell copies of the Software,
// and to permit persons to whom the Software is furnished to do so, subject to
// the following conditions:

// The above copyright notice and this permission notice shall be included in
// all copies or substantial portions of the Software.

// The manuals related to the Software and the information therein are not
// included in these permissions and must not be reproduced, distributed,
// copied, or disclosed to third parties without ABB's written permission.
// ABB reserves all rights regarding Intellectual Property Rights in such
// manuals and information therein. 

// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
// FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
// DEALINGS IN THE SOFTWARE.





"use strict";

fpComponentsLoadCSS("fp-components/fp-components-checkbox-a.css");

var FPComponents = FPComponents || {};

(function(o) {
    if (!o.hasOwnProperty("Checkbox_A")) {
        o.Checkbox_A = class {
            constructor() {
                this._anchor = null;
                this._root = null;
                this._button = null;
                this._scale = 1;
                this._enabled = true;
                this._onclick = null;
                this._checked = false;
                this._desc = null;
                this._descDiv = null;
            }
            get parent() {
                return this._anchor;
            }
            get onclick() {
                return this._onclick;
            }
            set onclick(f) {
                this._onclick = f;
            }
            get enabled() {
                return this._enabled;
            }
            set enabled(e) {
                this._enabled = e ? true : false;
                this._updateClassNames();
            }
            get checked() {
                return this._checked;
            }
            set checked(c) {
                this._checked = c ? true : false;
                this._updateClassNames();
            }
            get desc() {
                return this._desc;
            }
            set desc(d) {
                this._desc = d;
                if (this._root == null) {
                    return;
                }
                if (!d) {
                    if (this._descDiv !== null) {
                        this._root.removeChild(this._descDiv);
                    }
                    this._descDiv = null;
                    return;
                }
                if (this._descDiv == null) {
                    this._createDesc(this._root);
                    return;
                }
                this._descDiv.textContent = d;
            }
            _createDesc(parent) {
                let divdesc = document.createElement("div");
                divdesc.className = "fp-components-checkbox-desc";
                divdesc.textContent = this._desc;
                parent.appendChild(divdesc);
                this._descDiv = divdesc;
            }
            _updateClassNames() {
                if (this._button !== null) {
                    if (this._checked == true) {
                        this._button.className = this._enabled === true ? "fp-components-checkbox-checked" : "fp-components-checkbox-checked fp-components-checkbox-disabled";
                    } else {
                        this._button.className = this._enabled === true ? "fp-components-checkbox" : "fp-components-checkbox fp-components-checkbox-disabled";
                    }
                }
            }
            attachToId(nodeId) {
                let element = document.getElementById(nodeId);
                if (element === null) {
                    console.log("Could not find element with id: " + nodeId);
                    return false;
                }
                return this.attachToElement(element);
            }
            attachToElement(element) {
                this._anchor = element;
                return this.rebuild();
            }
            _paintCanvas(canvas, color) {
                let s = this._scale;
                canvas.height = s * 20;
                canvas.width = s * 20;
                let ctx = canvas.getContext("2d");
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                ctx.beginPath();
                ctx.translate(s * 10, s * 10);
                ctx.translate(-s * .5, -s * 2.5);
                ctx.rotate(45 * (Math.PI / 180));
                ctx.translate(-3 * s, -6 * s);
                ctx.moveTo(0, s * 13);
                ctx.lineTo(s * 7, s * 13);
                ctx.lineTo(s * 7, 0);
                ctx.strokeStyle = color;
                ctx.lineCap = "butt";
                ctx.lineWidth = s * 2.5;
                ctx.stroke();
            }
            rebuild() {
                let checkBoxDiv = document.createElement("div");
                checkBoxDiv.className = "fp-components-checkbox-root";
                let divButton = document.createElement("div");
                let canvas1 = document.createElement("canvas");
                let canvas2 = document.createElement("canvas");
                this._paintCanvas(canvas1, "white");
                this._paintCanvas(canvas2, "white");
                divButton.appendChild(canvas1);
                divButton.appendChild(canvas2);
                checkBoxDiv.onclick = () => {
                    if (this._enabled == true) {
                        this._checked = this._checked == true ? false : true;
                        this._updateClassNames();
                        if (this._onclick !== null) {
                            this._onclick(this._checked);
                        }
                    }
                };
                this._button = divButton;
                checkBoxDiv.appendChild(divButton);
                if (this._desc !== null) {
                    this._createDesc(checkBoxDiv);
                }
                this._root = checkBoxDiv;
                this._updateClassNames();
                if (this._scale !== 1) {
                    this.scale = this._scale;
                }
                this._anchor.appendChild(checkBoxDiv);
            }
            set scale(s) {
                this._scale = s;
                if (this._button !== null) {
                    this._button.style.borderWidth = (2 * s).toString() + "px";
                    this._button.style.borderRadius = (3 * s).toString() + "px";
                    this._button.style.width = (20 * s).toString() + "px";
                    this._button.style.height = (20 * s).toString() + "px";
                    let canvases = this._button.getElementsByTagName("canvas");
                    this._paintCanvas(canvases[0], "white");
                    this._paintCanvas(canvases[1], "white");
                }
            }
            get scale() {
                return this._scale;
            }
        };
        o.Checkbox_A.VERSION = "1.6.0";
    }
})(FPComponents);