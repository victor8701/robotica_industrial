


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

fpComponentsLoadCSS("fp-components/fp-components-foldin-a.css");

var FPComponents = FPComponents || {};

(function(o) {
    if (!o.hasOwnProperty("Foldin_A")) {
        o.Foldin_A = class {
            constructor() {
                this._anchor = null;
                this._width = "35vw";
                this._contentId = null;
                this._show = false;
                this._foldinOuterDiv = null;
                this._foldinInnerDiv = null;
                this._glassDiv = null;
            }
            get parent() {
                return this._anchor;
            }
            get width() {
                return this._width;
            }
            set width(w) {
                if (typeof w === "string") {
                    this._width = w;
                } else if (typeof w === "number") {
                    this._width = w.toString(10) + "px";
                } else {
                    this._width = w.toString();
                }
                if (this._show === true) {
                    this._foldinOuterDiv.style.width = this._width;
                    this._foldinInnerDiv.style.minWidth = this._width;
                }
            }
            get contentId() {
                return this._contentId;
            }
            set contentId(cId) {
                this._contentId = cId === null ? null : cId.toString();
                if (this._foldinInnerDiv !== null) {
                    if (this._contentId === null) {
                        this._foldinInnerDiv.removeAttribute("id");
                    } else {
                        this._foldinInnerDiv.id = this._contentId;
                    }
                }
            }
            attachToBody() {
                let element = document.getElementsByTagName("body")[0];
                if (element === null) {
                    console.log("Could not find body element");
                    return false;
                }
                this._anchor = element;
                return this.rebuild();
            }
            rebuild() {
                if (this._anchor !== null) {
                    let anchor = this._anchor;
                    let foldinInnerDiv = document.createElement("div");
                    foldinInnerDiv.className = "fp-components-foldin-inner";
                    if (this._contentId !== null) foldinInnerDiv.id = this._contentId;
                    foldinInnerDiv.style.width = this._width;
                    let foldinOuterDiv = document.createElement("div");
                    foldinOuterDiv.className = "fp-components-base fp-components-foldin";
                    let glassDiv = document.createElement("div");
                    glassDiv.className = "fp-components-foldin-glasspane";
                    glassDiv.onclick = () => {
                        this.hide();
                    };
                    foldinOuterDiv.appendChild(foldinInnerDiv);
                    anchor.appendChild(foldinOuterDiv);
                    anchor.appendChild(glassDiv);
                    this._foldinInnerDiv = foldinInnerDiv;
                    this._foldinOuterDiv = foldinOuterDiv;
                    this._glassDiv = glassDiv;
                }
            }
            show() {
                if (this._show === true) {
                    return;
                }
                this._show = true;
                if (this._foldinOuterDiv !== null) {
                    this._glassDiv.style.display = "block";
                    this._foldinOuterDiv.style.width = this._width;
                    this._foldinInnerDiv.style.minWidth = this._width;
                }
            }
            hide() {
                if (this._show === false) {
                    return;
                }
                this._show = false;
                if (this._foldinOuterDiv !== null) {
                    this._glassDiv.style.display = "none";
                    this._foldinOuterDiv.style.width = "0";
                }
            }
        };
        o.Foldin_A.VERSION = "1.6.0";
    }
})(FPComponents);