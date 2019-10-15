
function FPS(x = 5, y = 25, font = "8px Arial", range = 20) {
    this.font = font;
    this.x = x;
    this.y = y;
    this.calls = 0;
    this.fps = 0;
    this.range = range;
    this.accumulated_time = 0;

    this.lastTime = Date.now();
}
FPS.prototype.draw = function(ctx) {
    let newTime = Date.now();
    let ts = newTime - this.lastTime;
    this.lastTime = newTime;
    if (this.calls == this.range) {
        this.fps = Math.round(this.range * 1000 / this.accumulated_time) + "fps";
        this.calls = 0;
        this.accumulated_time = 0;
    }
    this.accumulated_time += ts;

    ctx.save();
    ctx.font = this.font;
    ctx.fillStyle  = "#000";
    ctx.fillText(this.fps, this.x, this.y);
    ctx.restore();
    this.calls++;
}