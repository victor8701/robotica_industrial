


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

fpComponentsLoadCSS("fp-components/fp-components-menu-a.css");

var FPComponents = FPComponents || {};

(function(o) {
    if (!o.hasOwnProperty("Menu_A")) {
        o.Menu_A = class {
            constructor() {
                this._model = {};
                this._anchor = null;
            }
            get parent() {
                return this._anchor;
            }
            set model(model) {
                this._model = model;
                this.rebuild();
            }
            get model() {
                return this._model;
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
                if (this._anchor != null) {
                    let containerNode = document.createElement("div");
                    containerNode.className = "fp-components-base fp-components-menu-a-container";
                    let content = this._model.content;
                    if (content !== undefined && Array.isArray(content)) {
                        for (let item of content) {
                            if (item.type === "button") {
                                let divNode = document.createElement("div");
                                divNode.className = "fp-components-menu-a-button";
                                if (item.flash !== undefined && item.flash == true) {
                                    divNode.className += " fp-components-menu-a-button-flash";
                                    if (item.flashColor) {
                                        divNode.style.setProperty("--fp-components-menu-flash-color", item.flashColor);
                                    }
                                }
                                if (item.icon !== undefined) {
                                    let imgNode = document.createElement("div");
                                    imgNode.className = "fp-components-menu-a-button-icon";
                                    imgNode.style.backgroundImage = `url("${item.icon}")`;
                                    divNode.appendChild(imgNode);
                                }
                                let pNode = document.createElement("p");
                                if (item.label !== undefined) pNode.appendChild(document.createTextNode(item.label));
                                divNode.appendChild(pNode);
                                containerNode.appendChild(divNode);
                                if (item.arrow !== undefined && (item.arrow === true || item.arrow === "true")) {
                                    let arrowNode = document.createElement("div");
                                    arrowNode.className = "fp-components-menu-a-button-righticon";
                                    arrowNode.style.backgroundImage = 'url("fp-components/img/rightarrow.png")';
                                    divNode.appendChild(arrowNode);
                                }
                                if (item.enabled === false) {
                                    divNode.style.opacity = "0.25";
                                } else {
                                    if (item.onclick !== undefined) divNode.onclick = item.onclick;
                                    divNode.className += " fp-components-menu-a-button-enabled";
                                }
                            } else if (item.type === "gap") {
                                containerNode.appendChild(document.createElement("br"));
                            } else if (item.type === "label") {
                                let divNode = document.createElement("div");
                                divNode.className = "fp-components-menu-a-label";
                                let pNode = document.createElement("p");
                                if (item.label !== undefined) pNode.appendChild(document.createTextNode(item.label));
                                divNode.appendChild(pNode);
                                containerNode.appendChild(divNode);
                            }
                        }
                    }
                    while (this._anchor.firstChild) {
                        this._anchor.removeChild(this._anchor.firstChild);
                    }
                    this._anchor.appendChild(containerNode);
                }
            }
        };
        o.Menu_A.VERSION = "1.6.0";
    }
})(FPComponents);