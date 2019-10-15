class Pendulum {
    constructor() {
        this.base = new Vector();
        this.bob = new Vector();

        this.previousBasePosition = this.base.clone();
        this.previousBaseSpeed = new Vector();
        
        this.theta = 1e-10;
        this.phi = 0.0;
        this.dTheta = 0.0;
        this.dPhi = 0.0;
        this.l = 0.2;
        this.c_a = 0.0;
        this.c_d = 1.0;
        this.mass = 1.0;
        this.gravity = new Vector(0, 0, -10);
        this.force = this.gravity.clone();
        this.wind = new Vector(0, 0, 0);
        this.air = new Vector(0, 0, 0);
        this.time_step = 1/60;

        this.debug = 0.0;

        // Visualization
        this.line = new Line();
        this.point_base = new Point(0, 0, 0);
        this.point_base.size = 3;
        this.point_bob = new Point(0, 0, 0);
        this.point_bob.size = 6;
        
        this.line_force = new Line();
        this.line_force.color = "rgba(119, 102, 255, 0.4)";
        this.line_force.end = this.force;

        this.line_wind = new Line();
        this.line_wind.color = "#7ff";
        this.line_wind.end = this.wind;

        this.line.start = this.point_base.position = this.base;
        this.line.end = this.point_bob.position = this.bob;

        

        this.updatePosition();

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
            
                    pendulum.debug = vw2;
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


        this.lines = [];
        for (let i = 0; i < 400; i++) {
            this.lines.push(new Line());
        }
        this.resetLines();
        this.stepSize = 2;
        this.currentStep = 0;
    }

    resetLines() {
        this.lines.forEach(line => {
            line.start = line.end = this.bob;
        });
    }

    step() {
        // Calculate force, resulting from movement.
        let speed = this.base.subtract(this.previousBasePosition);
        speed = speed.divide(this.time_step);
        this.previousBasePosition._set(this.base);
        let acceleration = speed.subtract(this.previousBaseSpeed);
        acceleration = acceleration.divide(this.time_step);
        this.previousBaseSpeed._set(speed);
        
        this.force._set(this.gravity);
        this.force._add(acceleration.multiply(-1));
        this.air._set(this.wind);
        this.air._add(speed.multiply(-1));
        
        //if (Math.abs(this.theta) + Math.abs(this.dTheta))
        
        let result = this.solver.solve(this.equation,
                                0, 
                                [this.theta, this.dTheta, this.phi, this.dPhi], 
                                this.time_step);
        [this.theta, this.dTheta, this.phi, this.dPhi] =  result.y;
        
        this.updatePosition();
        this.currentStep += 1;
        if (this.currentStep == this.stepSize) {
            this.currentStep = 0;
            let newLine = new Line();
            newLine.width = 1;
            newLine.start = this.bob.clone();
            newLine.end = this.lines[0].start.clone();
            this.lines.pop();
            this.lines.unshift(newLine);
        }
    }

    updatePosition() {
        this.bob.x = this.l * Math.sin(this.theta) * Math.cos(this.phi);
        this.bob.y = this.l * Math.sin(this.theta) * Math.sin(this.phi);
        this.bob.z = -this.l * Math.cos(this.theta);

        this.bob._add(this.base);
    }

    draw(ctx) {
        for (let i = 0; i < this.lines.length; i++) {
            const line = this.lines[i];
            line.color = "rgba(0, 150, 180, " + Math.pow((1 - i/this.lines.length), 2).toString() + ")";
            line.draw(ctx);

        }
        
        this.line.draw(ctx);
        this.line_wind.multiply(0.01).draw(ctx);
        this.line_force._multiply(0.01).draw(ctx);
        
        this.point_base.draw(ctx);
        this.point_bob.draw(ctx);

    }
}