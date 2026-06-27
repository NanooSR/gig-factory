let score = 0;
let timeLeft = 10;
let timer = null;
let active = false;
const scoreEl = document.getElementById('score');
const timeEl = document.getElementById('time');
const statusEl = document.getElementById('status');
const target = document.getElementById('target');

function resetGame() {
  score = 0;
  timeLeft = 10;
  active = false;
  clearInterval(timer);
  scoreEl.textContent = score;
  timeEl.textContent = timeLeft;
  statusEl.textContent = 'Press Start to play.';
}

document.getElementById('startBtn').addEventListener('click', () => {
  if (active) return;
  active = true;
  statusEl.textContent = 'Go!';
  timer = setInterval(() => {
    timeLeft -= 1;
    timeEl.textContent = timeLeft;
    if (timeLeft <= 0) {
      clearInterval(timer);
      active = false;
      statusEl.textContent = `Time! Final score: ${score}`;
    }
  }, 1000);
});

target.addEventListener('click', () => {
  if (!active) return;
  score += 1;
  scoreEl.textContent = score;
});

document.getElementById('restartBtn').addEventListener('click', resetGame);
resetGame();
