function blur_hack() {
    var tmp = document.createElement("input");
    document.body.appendChild(tmp);
    tmp.focus();
    document.body.removeChild(tmp);
}
const SLDRS = {};
SLDRS.items = [];
function resetFunction()  {
    SLDRS.items.forEach(el => {
        el.apply();
    });
};
function grabFunction() {
    SLDRS.items.forEach(el => {
        el.grab();
    });
}

SLDRS.reset = resetFunction;
SLDRS.grab = function() {};

let btn = document.createElement("button");
btn.appendChild(document.createTextNode("GO"));
document.getElementById('controls').appendChild(btn);
btn.onclick = SLDRS.reset;

let box = document.createElement("input");
box.type = "checkbox";
box.checked = false;
box.id = "box_update";
let lbl = document.createElement("label");
lbl.htmlFor = box.id;
lbl.appendChild(document.createTextNode("update"));
document.getElementById('controls').appendChild(box);
document.getElementById('controls').appendChild(lbl);
box.onclick = function handleClick() {
    if (this.checked)
        SLDRS.grab = grabFunction;
    else
        SLDRS.grab = function() {};
}
box.onclick();
  


class Slider {
    constructor(object, attr) {
        this.object = object;
        this.attr = attr;
        Object.defineProperty(this, 'value', {
            get: function() {
                return this.object[this.attr];;
            },
            set: function(v) {
                this.object[this.attr] = v;
            }
        });

        this.createElement();
        
        this.input.value = this.value;
        let el = this;

        this.input.addEventListener("keyup", function(evt) {
            if (evt.keyCode == 13) blur_hack();
        });
        this.input.addEventListener("blur", function() {el.chd();});
        SLDRS.items.push(this);
    }
    chd() {
        this.apply();
    }
    apply() {
        let newValue = parseFloat(this.input.value);
        this.value = newValue;
        
    }
    grab() {
        if (document.activeElement !== this.input)
            this.input.value = this.value;
    }
    createElement(width) {
        let div = document.createElement("DIV");
        div.classList.add("data");
        let attr = document.createTextNode(this.attr);
        this.input = document.createElement("INPUT");
        div.appendChild(attr);
        div.appendChild(this.input);
        document.getElementById('controls').appendChild(div);
    }
    
}