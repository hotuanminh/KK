from flask import Flask, render_template_string
import os

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Flappy UFO Rocket</title>
  <style>
    body { margin:0; display:flex; justify-content:center; align-items:center; height:100vh; background:#70c5ce; }
    canvas { background:#70c5ce; display:block; border:2px solid #000; }
    #playAgain {
      display:none;
      position:absolute;
      top:60%;
      left:50%;
      transform:translate(-50%,-50%);
      padding:10px 20px;
      font-size:20px;
      font-weight:bold;
      background:#ff4444;
      color:white;
      border:none;
      border-radius:8px;
      cursor:pointer;
    }
  </style>
</head>
<body>
  <canvas id="gameCanvas" width="500" height="700"></canvas>
  <button id="playAgain">Play Again</button>
  <script>
    const canvas = document.getElementById("gameCanvas");
    const ctx = canvas.getContext("2d");
    const playBtn = document.getElementById("playAgain");

    let frames, score, gameOver;

    // Bird (Eagle)
    const bird = {
      x: 80, y: 200, w: 40, h: 40,
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
        if(this.y + this.h/2 >= canvas.height || this.y - this.h/2 <= 0){ gameOver = true; }
      }
    };

    // Pipes
    const pipes = {
      position: [],
      w: 60, h: 400, gap: 140,
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
          this.position.push({ x: canvas.width, y: -this.h + Math.random()*200, passed:false });
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
        if(this.position.length && this.position[0].x < -this.w){ this.position.shift(); }
      }
    };

    // UFOs (bay ngang)
    const ufos = {
      items: [],
      draw(){
        this.items.forEach(u => {
          // Thân UFO
          ctx.fillStyle = "#888";
          ctx.beginPath();
          ctx.ellipse(u.x, u.y, 30, 12, 0, 0, 2*Math.PI);
          ctx.fill();
          // Vòm kính
          ctx.fillStyle = "#00f";
          ctx.beginPath();
          ctx.arc(u.x, u.y-8, 10, 0, 2*Math.PI);
          ctx.fill();
          // Đèn vàng
          ctx.fillStyle = "yellow";
          ctx.beginPath();
          ctx.arc(u.x-15, u.y+5, 3, 0, 2*Math.PI);
          ctx.arc(u.x, u.y+5, 3, 0, 2*Math.PI);
          ctx.arc(u.x+15, u.y+5, 3, 0, 2*Math.PI);
          ctx.fill();
        });
      },
      update(){
        if(frames % 150 === 0 && !gameOver){
          this.items.push({ x: canvas.width, y: 100 + Math.random()*(canvas.height-200), dx:3 });
        }
        this.items.forEach(u => {
          u.x -= u.dx;
          if(Math.abs(bird.x - u.x) < 25 && Math.abs(bird.y - u.y) < 20){
            gameOver = true;
          }
        });
        if(this.items.length && this.items[0].x < -50){ this.items.shift(); }
      }
    };

    // Rockets (tên lửa)
    const rockets = {
      items: [],
      draw(){
        this.items.forEach(r => {
          // Thân tên lửa
          ctx.fillStyle = "gray";
          ctx.fillRect(r.x-10, r.y-5, 30, 10);
          // Đầu đỏ
          ctx.fillStyle = "red";
          ctx.beginPath();
          ctx.moveTo(r.x+20, r.y-7);
          ctx.lineTo(r.x+30, r.y);
          ctx.lineTo(r.x+20, r.y+7);
          ctx.closePath();
          ctx.fill();
          // Lửa đuôi
          ctx.fillStyle = "orange";
          ctx.beginPath();
          ctx.moveTo(r.x-10, r.y-5);
          ctx.lineTo(r.x-20, r.y);
          ctx.lineTo(r.x-10, r.y+5);
          ctx.closePath();
          ctx.fill();
        });
      },
      update(){
        if(frames % 200 === 0 && !gameOver){
          this.items.push({ x: canvas.width, y: 100 + Math.random()*(canvas.height-200), dx:5 });
        }
        this.items.forEach(r => {
          r.x -= r.dx;
          if(Math.abs(bird.x - r.x) < 20 && Math.abs(bird.y - r.y) < 20){
            gameOver = true;
          }
        });
        if(this.items.length && this.items[0].x < -50){ this.items.shift(); }
      }
    };

    function drawScore(){
      ctx.fillStyle = "#fff";
      ctx.font = "30px Arial";
      ctx.fillText("Score: " + score, 10, 40);
    }

    function drawGameOver(){
      ctx.fillStyle = "red";
      ctx.font = "50px Arial";
      ctx.fillText("GAME OVER", 100, canvas.height/2 - 40);
      ctx.font = "25px Arial";
      ctx.fillText("Final Score: " + score, 180, canvas.height/2);
      playBtn.style.display = "block";
    }

    function resetGame(){
      frames = 0; score = 0; gameOver = false;
      bird.y = 200; bird.speed = 0;
      pipes.position = [];
      ufos.items = [];
      rockets.items = [];
      playBtn.style.display = "none";
    }

    function draw(){
      ctx.fillStyle = "#70c5ce";
      ctx.fillRect(0,0,canvas.width,canvas.height);
      pipes.draw();
      ufos.draw();
      rockets.draw();
      bird.draw();
      drawScore();
      if(gameOver) drawGameOver();
    }

    function update(){
      if(!gameOver){
        bird.update();
        pipes.update();
        ufos.update();
        rockets.update();
      }
    }

    function loop(){
      update();
      draw();
      frames++;
      requestAnimationFrame(loop);
    }

    // Điều khiển bằng click chuột hoặc phím Space
    canvas.addEventListener("click", () => { if(!gameOver) bird.flap(); });
    document.addEventListener("keydown", e => {
      if(e.code === "Space" && !gameOver){ bird.flap(); }
    });

    playBtn.addEventListener("click", resetGame);

    resetGame();
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
