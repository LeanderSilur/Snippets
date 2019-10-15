class Joint {
    constructor() {
        this.position = new Vector();
        this.prevPosition = new Vector();
        this.speed = new Vector();
        this.acceleration = new Vector();
        this.reset();
    }
    calc() {
        let prevSpeed = this.speed.clone();
        this.speed._set(this.position.subtract(this.prevPosition));
        this.prevPosition._set(this.position);
        this.acceleration._set(this.speed.subtract(prevSpeed));
    }
    reset() {
        this.prevPosition._set(this.position);
        this.speed._multiply(0);
        this.acceleration._multiply(0);
    }
}

class Segment {
    constructor() {
        this.base = new Joint();
        this.bob = new Joint();

        this.theta = 0.1;
        this.phi = 0.0;
        this.dTheta = 0.0;
        this.dPhi = 0.0;
        this.l = 0.12;
        this.c_a = 0.0;
        this.c_d = 0.0;
        this.mass = 1.0;
        this.force = new Vector(0, 0, -5);
        this.air = new Vector(0, 0, 0);
        

        this.solver = new window.odex_solver(4);
        //this.solver.absoluteTolerance = this.solver.relativeTolerance = 1e-10;
        let pendulum = this;
        // SOLVER
        this.equation = function(x, y) {
            let [θ, dθ, φ, dφ] = y;
            let [l, m] = [pendulum.l, pendulum.mass];
            let [c_a, c_d] = [pendulum.c_a, pendulum.c_d];
            let [gx, gy, gz] = [pendulum.force.x, pendulum.force.y, pendulum.force.z];
            let [wx, wy, wz] = [pendulum.air.x, pendulum.air.y, pendulum.air.z];

            // [keep this for wolframalpha]
            // d/dt ((-l sin(θ) sin(φ) p + l cos(θ) cos(φ) t) - x)^2 + ((l sin(θ) cos(φ) p + l cos(θ) sin(φ) t) - y)^2 + (l sin(θ)t - z)^2
            let vw2 = Math.pow(-l *Math.sin(θ) *Math.sin(φ) *dφ + l *Math.cos(θ) *Math.cos(φ) *dθ - wx, 2)
                    + Math.pow(l *Math.sin(θ) *Math.cos(φ) *dφ + l *Math.cos(θ) *Math.sin(φ) *dθ - wy, 2)
                    + Math.pow(l *Math.sin(θ) *dθ - wz, 2);
            
            let vw121 = Math.pow(vw2, 1/2);
            

            let c_θ = 0;
            let c_φ = 0;
            // Angular Friction [c_a]
            c_θ += c_a * l * l * dθ;
            c_φ += c_a * l * l * dφ * Math.pow(Math.sin(θ), 2);
            // Drag Friction    [c_d]
            c_θ += c_d * m * vw121 * (
                  2 *l *Math.cos(θ) * Math.cos(φ) *(l * dθ * Math.cos(θ) * Math.cos(φ) -l * dφ * Math.sin(θ) * Math.sin(φ) - wx)
                + 2 *l *Math.cos(θ) * Math.sin(φ)* (l* dθ* Math.cos(θ) *Math.sin(φ) +l *dφ *Math.sin(θ) *Math.cos(φ) - wy)
                + 2 *l *Math.sin(θ) *(l *dθ *Math.sin(θ) - wz)
                );
            c_φ += c_d * m * vw121 * (
                2 *l *Math.sin(θ) *(l* dφ* Math.sin(θ)* (Math.pow(Math.sin(φ), 2)
                + Math.pow(Math.cos(φ), 2))
                + wx*Math.sin(φ) - wy*Math.cos(φ))
                );

            let d_θ = dθ;
            let d_dθ =  Math.pow(dφ, 2) / 2 * Math.sin(2*θ)
                        + Math.sin(θ)/l * gz
                        + Math.cos(θ)/l * (gx * Math.cos(φ) + gy * Math.sin(φ))
                        - c_θ / m / l / l;



            let d_φ = dφ;
            let d_dφ =  (-2) * dθ * dφ / Math.tan(θ)
                        + 1/(Math.sin(θ)*l) * (-gx*Math.sin(φ) + gy*Math.cos(φ))
                        - c_φ / m / l / l / Math.pow(Math.sin(θ), 2);

            return [d_θ, d_dθ, d_φ, d_dφ];
        };
    }

    step(time_step) {
        // Calculate force, resulting from movement.
        let result = this.solver.solve(this.equation,
                                0, 
                                [this.theta, this.dTheta, this.phi, this.dPhi], 
                                time_step);
        if (Number.isNaN(result.y[0]))
            return;
        [this.theta, this.dTheta, this.phi, this.dPhi] =  result.y;
    }

    updatePosition() {
        let pos = new Vector(
            this.l * Math.sin(this.theta) * Math.cos(this.phi),
            this.l * Math.sin(this.theta) * Math.sin(this.phi),
            -this.l * Math.cos(this.theta)
            );
        pos._add(this.base.position);
        this.bob.position._set(pos);
    }

    draw(ctx) {
        // Visualization
        let point = new Point(0, 0, 0);
        point.size = 5;
        point.position = this.bob.position;
        point.draw(ctx);

        let line = new Line();
        line.start = this.base.position; line.end = this.bob.position;
        line.draw(ctx);
        
        let line_force = new Line();
        line_force.color = "rgba(119, 200, 255, 0.8)";
        line_force.start = this.base.position;
        line_force.end = this.force.multiply(0.01).add(this.base.position);
        line_force.draw(ctx);
    }
}

class Pendulum {
    constructor(length = 2) {
        this.base = new Vector();
        this.length = length;
        this.segments = new Array(length);

        this.c_a = 0.5;
        this.c_d = 2;
        let c_a_multiplier = 0;
        let c_d_multiplier = 4;
        this.gravity = new Vector(0, 0, -10);
        this.wind = new Vector();
        this.time_step = 1/60;
        
        for (let i = 0; i < this.segments.length; i++) {
            this.segments[i] = new Segment();
            this.segments[i].c_a = this.c_a + i*c_a_multiplier;
            this.segments[i].c_d = this.c_d + i*c_d_multiplier;
            if (i == 0) {
                this.segments[i].base.position = this.base;
            }
            else {
                this.segments[i].base = this.segments[i-1].bob;
            }
            this.segments[i].updatePosition();
            this.segments[i].bob.reset();
        }
    }

    step() {
        this.segments[0].base.calc();
        for (let i = 0; i < this.segments.length; i++) {
            this.segments[i].bob.calc();
        }
        for (let i = 0; i < this.segments.length; i++) {
            const segment = this.segments[i];
            let childForce = new Vector();
            if (i < this.segments.length - 1)
                childForce = this.segments[i+1].bob.acceleration.divide(
                                                    this.time_step*this.time_step
                                                    ).multiply(this.segments[i+1].mass);
            segment.force._set(this.gravity);
            segment.force._add(segment.base.acceleration.divide(-this.time_step*this.time_step).multiply(segment.mass));
            //segment.force._add(childForce);
            segment.air._set(this.wind);
            segment.air._add(segment.base.speed.multiply(-this.time_step));
        }
        for (let i = 0; i < this.segments.length; i++) {
            this.segments[i].step(this.time_step);
        }
       this.updatePosition();
    }

    updatePosition() {
        this.segments.forEach(segment => {
            segment.updatePosition();
        });
    }

    draw(ctx) {
        this.segments.forEach(segment => {
            segment.draw(ctx);
        });
    }
}