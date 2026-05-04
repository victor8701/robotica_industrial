


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

fpComponentsLoadCSS("fp-components/fp-components-radio-a.css");

var FPComponents = FPComponents || {};

(function(o) {
    if (!o.hasOwnProperty("Radio_A")) {
        o.Radio_A = class {
            constructor() {
                this._anchor = null;
                this._root = null;
                this._scale = 1;
                this._enabled = true;
                this._onclick = null;
                this._checked = false;
                this._desc = null;
                this._descDiv = null;
                this._container = null;
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
                if (this._container === null) {
                    return;
                }
                if (!d) {
                    if (this._descDiv !== null) {
                        this._container.removeChild(this._descDiv);
                    }
                    this._descDiv = null;
                    return;
                }
                if (this._descDiv === null) {
                    this._createDesc();
                    return;
                }
                this._descDiv.textContent = d;
            }
            _createDesc() {
                let divdesc = document.createElement("span");
                divdesc.className = "fp-components-radio-desc";
                divdesc.textContent = this._desc;
                this._container.appendChild(divdesc);
                this._descDiv = divdesc;
            }
            _updateClassNames() {
                if (this._root !== null) {
                    if (this._checked == true) {
                        this._root.className = this._enabled === true ? "fp-components-radio-checked" : "fp-components-radio-checked fp-components-radio-disabled";
                    } else {
                        this._root.className = this._enabled === true ? "fp-components-radio" : "fp-components-radio fp-components-radio-disabled";
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
            rebuild() {
                let divContainer = document.createElement("div");
                let divButton = document.createElement("div");
                divButton.appendChild(document.createElement("div"));
                divContainer.className = "fp-components-radio-container";
                divContainer.onclick = () => {
                    if (this._enabled == true && this._checked != true) {
                        this._checked = true;
                        this._updateClassNames();
                        if (this._onclick !== null) {
                            this._onclick();
                        }
                    }
                };
                divContainer.appendChild(divButton);
                this._container = divContainer;
                this._root = divButton;
                if (this._desc !== null) {
                    this._createDesc();
                }
                this._updateClassNames();
                if (this._scale !== 1) {
                    this.scale = this._scale;
                }
                this._anchor.appendChild(divContainer);
            }
            set scale(s) {
                this._scale = s;
                if (this._root !== null) {
                    this._root.style.borderWidth = (2 * s).toString() + "px";
                    this._root.style.borderRadius = (12 * s).toString() + "px";
                    this._root.style.width = (24 * s).toString() + "px";
                    this._root.style.height = (24 * s).toString() + "px";
                    let markerDiv = this._root.getElementsByTagName("div")[0];
                    markerDiv.style.width = (8 * s).toString() + "px";
                    markerDiv.style.height = (8 * s).toString() + "px";
                    markerDiv.style.borderRadius = (4 * s).toString() + "px";
                    markerDiv.style.marginLeft = (6 * s).toString() + "px";
                    markerDiv.style.marginTop = (6 * s).toString() + "px";
                }
            }
            get scale() {
                return this._scale;
            }
        };
        o.Radio_A.VERSION = "1.6.0";
    }
})(FPComponents);