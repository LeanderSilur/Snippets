class Vector {
    constructor(x=0, y=0, z=0) {
        this.x = x;
        this.y = y;
        this.z = z;
    }

    clone() {
        return new Vector(this.x, this.y, this.z);
    }
    equals(b) {
        return (this.x == b.x && this.y == b.y && this.z == b.z);
    }
    _set(b) {
        this.x = b.x;
        this.y = b.y;
        this.z = b.z;
    }
    add(b) {
        return new Vector(this.x + b.x, this.y + b.y, this.z + b.z);
    }
    _add(b) {
        this.x += b.x;
        this.y += b.y;
        this.z += b.z;
    }
    subtract(b) {
        return new Vector(this.x - b.x, this.y - b.y, this.z - b.z);
    }
    multiply(n) {
        return new Vector(this.x * n, this.y * n, this.z * n);
    }
    _multiply(n) {
        this.x *= n;
        this.y *= n;
        this.z *= n;
        return new Vector(this.x * n, this.y * n, this.z * n);
    }
    divide(n) {
        return new Vector(this.x / n, this.y / n, this.z / n);
    }
    _divide(n) {
        this.x *= n;
        this.y *= n;
        this.z *= n;
    }
    dot(b) {
        return this.x*b.x + this.y*b.y + this.z*b.z;
    }
    magnitude() { // project v onto s
        return Math.pow(Math.pow(this.x, 2) + Math.pow(this.y, 2) + Math.pow(this.z, 2), 0.5);
    }
    normalize() {
        return this.divide(this.magnitude());
    }
    angle(b) {
        let cosTheta = this.dot(b).divide(this.magnitude() * b.magnitude())
        return Math.acos(cosTheta);
    }
    rotateX(d) {
        return new Vector(this.x * Math.cos(d) + this.z * Math.sin(d),
                          this.y,
                          this.x * Math.sin(d) - this.z * Math.cos(d));
    }
    rotateY(d) {
        return new Vector(this.x,
                          this.y * Math.cos(d) - this.z * Math.sin(d),
                          this.y * Math.sin(d) + this.z * Math.cos(d));
    }
    rotateZ(d) {
        return new Vector(this.x * Math.cos(d) - this.y * Math.sin(d),
                          this.x * Math.sin(d) + this.y * Math.cos(d),
                          this.z);
    }
    cameraTo2d() {
        let v = this.clone();
        v = v.rotateZ(-CAMERA.phi);
        v = v.rotateY(-CAMERA.theta);
        v.z -= CAMERA.distance;
        v = v.multiply(CAMERA.focal / -v.z / CAMERA.sensor);
        v.x += 0.5;
        v.y = -v.y;
        v.y += 0.5 - CAMERA.offset;
        return v;
    }
    cameraTransform() {
        let v = this.clone();
        v = v.rotateZ(-CAMERA.phi);
        v = v.rotateY(-CAMERA.theta);
        v.z -= CAMERA.distance;
        v.y -= CAMERA.offset / -v.z;
        return v;
    }
    cameraTransformInv() {
        let v = this.clone();
        v.y += CAMERA.offset / -v.z;
        v.z += CAMERA.distance;
        v = v.rotateY(CAMERA.theta);
        v = v.rotateZ(CAMERA.phi);
        return v;
    }
    print() { // project v onto s
        return "[" +  this.x.toString() + ", " + this.y.toString() + ", " + this.z.toString() + "]";
    }
}


class Point {
    constructor(x=0, y=0, z=0) {
        this.position = new Vector(x, y, z);
        this.color = "#fff";
        this.size = 10;
        this.draggable = false;
    }
    draw(ctx) {
        let pt = this.position.cameraTo2d();
        ctx.beginPath();
        ctx.arc(pt.x * ctx.canvas.width, pt.y * ctx.canvas.height, this.size, 0, 2 * Math.PI);
        ctx.lineWidth = 2;
        ctx.fillStyle = this.color;
        ctx.fill();
    }
}
class Line {
    constructor() {
        this.start = new Vector(0, 0, 0);
        this.end = new Vector(0, 0, 0);
        this.color = "#888";
        this.width = 2;
    }
    clone() {
        let line = new Line();
        line.color = this.color;
        line.width = this.width;
        line.start = this.start.clone();
        line.end = this.end.clone();
        return line;
    }
    _clone() {
        let line = new Line();
        line.color = this.color;
        line.width = this.width;
        line.start = this.start;
        line.end = this.end;
        return line;
    }
    draw(ctx) {
        let pt0 = this.start.cameraTo2d();
        let pt1 = this.end.cameraTo2d();
        ctx.beginPath();
        ctx.moveTo(pt0.x*ctx.canvas.width, pt0.y*ctx.canvas.height);
        ctx.lineTo(pt1.x*ctx.canvas.width, pt1.y*ctx.canvas.height);
        ctx.strokeStyle = this.color;
        ctx.lineWidth = this.width;
        ctx.stroke();
    }
    multiply(v) {
        let line = this.clone();
        line.start._multiply(v);
        line.end._multiply(v);
        return line;
    }
    _multiply(v) {
        let line = this._clone();
        line.start._multiply(v);
        line.end._multiply(v);
        return line;
    }
}
class GridFloor {
    constructor(width = 2, divisions = 5) {
        this.lines = [];
        for (let x = -width/2; x <= width/2; x+=width/divisions) {
            let line = new Line();
            line.start = new Vector(x, -width/2, 0);
            line.end = new Vector(x, width/2, 0);
            this.lines.push(line);
        }
        for (let y = -width/2; y <= width/2; y+=width/divisions) {
            let line = new Line();
            line.start = new Vector(-width/2, y, 0);
            line.end = new Vector(width/2, y, 0);
            this.lines.push(line);
        }
        this.lines.forEach(line => {
            line.color = "rgba(255, 255, 255, 0.3)";
            line.width = 1;
        });
    }
    draw(ctx) {

        this.lines.forEach(line => {
            line.draw(ctx);
        });
    }
}

class Scene {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext("2d");
        this.ctx.font = "12px Arial";

        this.items = [];
        this.draggables = [];
        this.attachCanvas();
    }

    attachCanvas() {
        let scene = this;
        this.mousePosition = null;
        this.draggedObject = null;
        this.highlightElement = null;

        this.canvas.addEventListener('contextmenu', function(e) { e.preventDefault(); e.stopPropagation(); });
        this.canvas.onmousedown = function (e) { e.preventDefault();
            scene.mousePosition = scene.windowToCanvasCoords(e);
            if (scene.highlightElement !== null) {
                scene.draggedObject = scene.highlightElement;
                scene.highlightElement = null;
            }
        };
        this.canvas.onmouseup = canvas.onmouseout = function (e) { e.preventDefault();
            scene.mousePosition = null;
            scene.draggedObject = null;
            scene.highlightElement = null;
        };
        
        this.canvas.onmousemove = function (e) {
            e.preventDefault();
            let nextPosition = scene.windowToCanvasCoords(e);
            let cc = scene.windowToCameraCoords(e);

            if (scene.mousePosition == null) {
                let distance = 1E+1000;
                let object = null;
                scene.draggables.forEach(el => {
                    let ep = el.position.cameraTo2d();
                    let d_dist = Math.sqrt(Math.pow(ep.x-cc.x, 2) + Math.pow(ep.y-cc.y, 2)) * CAMERA.distance / CAMERA.focal;
                    if (d_dist < distance) {
                        distance = d_dist;
                        object = el;
                    }
                });
                if (distance < 0.1)
                    scene.highlightElement = object;
                else
                    scene.highlightElement = null;
                return;
            }
            let distance = nextPosition.subtract(scene.mousePosition);
            scene.mousePosition = nextPosition;

            if (e.buttons == 1) {
                if (scene.draggedObject === null) {
                    CAMERA.theta -= distance.y/100;
                    CAMERA.phi -= distance.x  /100;
                }
                else {
                    let ep = scene.draggedObject.position.clone();
                    let tr = ep.cameraTransform();
                    tr.x += distance.x / scene.canvas.width * (CAMERA.focal / CAMERA.sensor / 2 * -tr.z);
                    tr.y -= distance.y / scene.canvas.height *  (CAMERA.focal / CAMERA.sensor / 2 * -tr.z);
                    let tr2 = tr.cameraTransformInv();
                    ep.x = tr2.x;
                    ep.y = tr2.y;
                    ep.z = tr2.z;
                    scene.draggedObject.position._set(ep);
                }
            }
            else if (e.buttons == 2) {
                CAMERA.distance += distance.y/50;
            }
            else if (e.buttons == 4) {
                CAMERA.offset -= distance.y /300;
            }
        };
    }


    addItem(item) {
        this.items.push(item);
    }
    addDraggable(item) {
        this.draggables.push(item);
    }
    draw() {
        let ctx = this.ctx;
        ctx.beginPath();
        ctx.fillStyle="#bababa";
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        ctx.beginPath();
        ctx.fillStyle="#ffffff";
        ctx.fillText(CAMERA.theta.toFixed(2) + ", " + CAMERA.phi.toFixed(2), 4, 14); 
    
        this.items.forEach(item => {
            item.draw(ctx);
        });
        
        // Highlight
        if (this.highlightElement || this.draggedObject) {
            let el = this.highlightElement,
                col = "#2a6";
            if (el === null) {
                el = this.draggedObject;
                col = "#f55";
            }
            
            let high = el.position.cameraTo2d();
            ctx.beginPath();
            ctx.arc(high.x * ctx.canvas.width, high.y * ctx.canvas.height, 8, 0, 2 * Math.PI);
            ctx.lineWidth = 2;
            ctx.strokeStyle = col;
            ctx.stroke();
        }
    }
    
    windowToCanvasCoords(e) { //var x = e.x || e.clientX,
        let bbox = e.target.getBoundingClientRect();
        let v = new Vector((e.clientX - bbox.left * (this.canvas.width  / bbox.width)),
                          (e.clientY - bbox.top  * (this.canvas.height / bbox.height)), -CAMERA.focal);
        return v;
    }
    windowToCameraCoords(e) { 
        let bbox = e.target.getBoundingClientRect();
        let v = new Vector(
            (e.clientX - bbox.left * (this.canvas.width  / bbox.width)) / this.canvas.width,
            (e.clientY - bbox.top  * (this.canvas.height / bbox.height)) / this.canvas.height,
            -CAMERA.distance
            );
        return v;
    }
}





let CAMERA = function() {}
CAMERA.theta = 1.2;
CAMERA.phi = 0.6;
CAMERA.distance = 1.0;
CAMERA.focal = 1.5;
CAMERA.sensor = 1.0;
CAMERA.offset = 0.2;