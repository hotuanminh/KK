from flask import Flask, render_template_string
import os

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Flappy Eagle - Railway</title>
  <style>
    body { margin:0; display:flex; justify-content:center; align-items:center; height:100vh; background:#70c5ce; }
    canvas { background:#70c5ce; display:block; border:2px solid #000; }
  </style>
</head>
<body>
  <canvas id="gameCanvas" width="400" height="600"></canvas>
  <script>
    const canvas = document.getElementById("gameCanvas");
    const ctx = canvas.getContext("2d");

    let frames = 0;
    let score = 0;
    let gameOver = false;

    // Bird (Eagle)
    const bird = {
      x: 50, y: 150, w: 40, h: 40,
      gravity: 0.25, jump: 4.6, speed: 0,
      draw(){
        ctx.fillStyle = "brown";
        ctx.beginPath();
        ctx.ellipse(this.x, this.y, this.w/2, this.h/3, 0, 0, 2*Math.PI);
        ctx.fill();
        ctx.fillStyle = "white";
        ctx.beginPath();
        ctx.arc(this.x+10, this.y-10, 10, 0, 2*Math.PI);
        ctx.fill();
        ctx.fillStyle = "yellow";
        ctx.beginPath();
        ctx.moveTo(this.x+18, this.y-10);
        ctx.lineTo(this.x+28, this.y-5);
        ctx.lineTo(this.x+18, this.y);
        ctx.closePath();
        ctx.fill();
      },
      flap(){ this.speed = -this.jump; },
      update(){
        this.speed += this.gravity;
        this.y += this.speed;
        if(this.y + this.h/2 >= canvas.height){ gameOver = true; }
      }
    };

    // Pipes
    const pipes = {
      position: [],
      w: 60, h: 400, gap: 130,
      dx: 2,
      draw(){
        ctx.fillStyle = "#228B22";
        this.position.forEach(p => {
          ctx.fillRect(p.x, p.y, this.w, this.h);
          ctx.fillRect(p.x, p.y + this.h + this.gap, this.w, canvas.height);
        });
      },
      update(){
        if(frames % 100 === 0 && !gameOver){
          this.position.push({ x: canvas.width, y: -this.h + Math.random()*150, passed: false });
        }
        this.position.forEach(p => {
          p.x -= this.dx;
          if(bird.x + bird.w/2 > p.x && bird.x - bird.w/2 < p.x + this.w &&
             (bird.y - bird.h/2 < p.y + this.h || bird.y + bird.h/2 > p.y + this.h + this.gap)){
            gameOver = true;
          }
          if(!p.passed && p.x + this.w < bird.x){
            score++;
            p.passed = true;
          }
        });
        if(this.position.length && this.position[0].x < -this.w){
          this.position.shift();
        }
      }
    };

    document.addEventListener("keydown", e => { if(e.code === "Space" && !gameOver) bird.flap(); });
    document.addEventListener("click", () => { if(!gameOver) bird.flap(); });

    function drawScore(){
      ctx.fillStyle = "#fff";
      ctx.font = "30px Arial";
      ctx.fillText("Score: " + score, 10, 40);
    }

    function drawGameOver(){
      ctx.fillStyle = "red";
      ctx.font = "50px Arial";
      ctx.fillText("GAME OVER", 60, canvas.height/2);
      ctx.font = "25px Arial";
      ctx.fillText("Final Score: " + score, 120, canvas.height/2 + 40);
    }

    function draw(){
      ctx.fillStyle = "#70c5ce";
      ctx.fillRect(0,0,canvas.width,canvas.height);
      pipes.draw();
      bird.draw();
      drawScore();
      if(gameOver) drawGameOver();
    }

    function update(){
      if(!gameOver){
        bird.update();
        pipes.update();
      }
    }

    function loop(){
      update();
      draw();
      frames++;
      requestAnimationFrame(loop);
    }
    loop();
  </script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
