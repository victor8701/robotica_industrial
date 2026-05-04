


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

fpComponentsLoadCSS("fp-components/fp-components-digital-a.css");

var FPComponents = FPComponents || {};

(function(o) {
    if (!o.hasOwnProperty("Digital_A")) {
        o.Digital_A = class {
            constructor() {
                this._anchor = null;
                this._root = null;
                this._onclick = null;
                this._active = false;
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
            get active() {
                return this._active;
            }
            set active(a) {
                this._active = a == true;
                if (this._root !== null) {
                    this._root.textContent = this._active ? "1" : "0";
                }
                this._updateClassNames();
            }
            get desc() {
                return this._desc;
            }
            set desc(d) {
                this._desc = d;
                if (this._container == null) {
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
                let descDiv = document.createElement("div");
                descDiv.className = "fp-components-digital-a-desc";
                descDiv.textContent = this._desc;
                this._container.appendChild(descDiv);
                this._descDiv = descDiv;
            }
            _updateClassNames() {
                if (this._root !== null) {
                    this._root.className = "fp-components-digital-a";
                    if (this._active) {
                        this._root.className += " fp-components-digital-a-active";
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
                let divIndicator = document.createElement("div");
                divContainer.className = "fp-components-digital-a-container";
                divIndicator.textContent = this._active ? "1" : "0";
                divContainer.onclick = () => {
                    if (this._onclick !== null) {
                        this._onclick();
                    }
                };
                divContainer.appendChild(divIndicator);
                this._container = divContainer;
                this._root = divIndicator;
                if (this._desc !== null) {
                    this._createDesc();
                }
                this._updateClassNames();
                this._anchor.appendChild(divContainer);
            }
        };
        o.Digital_A.VERSION = "1.6.0";
    }
})(FPComponents);