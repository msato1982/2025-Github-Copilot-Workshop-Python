let workMinutes = 25;
let breakMinutes = 5;
let isWorkMode = true;
let timer = null;
let timeLeft = workMinutes * 60;

const timerDisplay = document.getElementById('timer-display');
const startBtn = document.getElementById('start-btn');
const stopBtn = document.getElementById('stop-btn');
const resetBtn = document.getElementById('reset-btn');
const modeLabel = document.getElementById('mode-label');

function updateDisplay() {
	const min = String(Math.floor(timeLeft / 60)).padStart(2, '0');
	const sec = String(timeLeft % 60).padStart(2, '0');
	timerDisplay.textContent = `${min}:${sec}`;
	modeLabel.textContent = isWorkMode ? '作業中' : '休憩中';
}

function tick() {
	if (timeLeft > 0) {
		timeLeft--;
		updateDisplay();
	} else {
		clearInterval(timer);
		timer = null;
		// タイマー終了時の動作（通知など）
		alert(isWorkMode ? '作業時間終了！休憩しましょう。' : '休憩終了！作業に戻りましょう。');
		isWorkMode = !isWorkMode;
		timeLeft = (isWorkMode ? workMinutes : breakMinutes) * 60;
		updateDisplay();
	}
}

startBtn.addEventListener('click', () => {
	if (!timer) {
		timer = setInterval(tick, 1000);
	}
});

stopBtn.addEventListener('click', () => {
	if (timer) {
		clearInterval(timer);
		timer = null;
	}
});

resetBtn.addEventListener('click', () => {
	if (timer) {
		clearInterval(timer);
		timer = null;
	}
	isWorkMode = true;
	timeLeft = workMinutes * 60;
	updateDisplay();
});

// 初期表示
updateDisplay();
