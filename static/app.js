const LETTER_VALUES = {
  a: 1, b: 3, c: 3, d: 2, e: 1, f: 4, g: 2, h: 4, i: 1, j: 8, k: 10,
  l: 1, m: 2, n: 1, o: 1, p: 3, q: 8, r: 1, s: 1, t: 1, u: 1, v: 4,
  w: 10, x: 10, y: 10, z: 10,
};

const boardEl = document.getElementById("board");
const cells = Array.from(boardEl.querySelectorAll(".cell"));
const SIZE = Math.sqrt(cells.length);

let board = Array.from({ length: SIZE }, () => Array(SIZE).fill(null));
let blankMap = Array.from({ length: SIZE }, () => Array(SIZE).fill(false));
let currentMoves = [];
let activeMoveIndex = -1;

const letterInput = document.getElementById("letterInput");
const blankToggle = document.getElementById("blankToggle");
const rackInput = document.getElementById("rackInput");
const rackPreview = document.getElementById("rackPreview");
const solveBtn = document.getElementById("solveBtn");
const clearBtn = document.getElementById("clearBoard");
const errorMsg = document.getElementById("errorMsg");
const resultsCard = document.getElementById("resultsCard");
const movesList = document.getElementById("movesList");
const applyBtn = document.getElementById("applyBtn");

function cellAt(r, c) {
  return cells[r * SIZE + c];
}

function renderCell(r, c) {
  const el = cellAt(r, c);
  const letter = board[r][c];
  el.classList.remove("filled", "blank", "suggested");
  const star = el.querySelector(".star");
  el.textContent = "";
  if (star) el.appendChild(star);

  if (letter) {
    el.classList.add("filled");
    if (blankMap[r][c]) el.classList.add("blank");
    el.textContent = letter.toUpperCase();
    el.dataset.points = blankMap[r][c] ? 0 : LETTER_VALUES[letter] || 0;
  } else {
    delete el.dataset.points;
  }
}

function renderAll() {
  for (let r = 0; r < SIZE; r++) {
    for (let c = 0; c < SIZE; c++) renderCell(r, c);
  }
}

boardEl.addEventListener("click", (e) => {
  const cell = e.target.closest(".cell");
  if (!cell) return;
  const r = Number(cell.dataset.row);
  const c = Number(cell.dataset.col);

  if (board[r][c]) {
    board[r][c] = null;
    blankMap[r][c] = false;
  } else {
    const letter = letterInput.value.trim().toLowerCase();
    if (!letter || !/^[a-z]$/.test(letter)) {
      errorMsg.textContent = "Tape une lettre valide avant de poser un pion.";
      return;
    }
    errorMsg.textContent = "";
    board[r][c] = blankToggle.checked ? letter.toUpperCase() : letter;
    blankMap[r][c] = blankToggle.checked;
  }
  renderCell(r, c);
  clearSuggestion();
});

clearBtn.addEventListener("click", () => {
  board = Array.from({ length: SIZE }, () => Array(SIZE).fill(null));
  blankMap = Array.from({ length: SIZE }, () => Array(SIZE).fill(false));
  renderAll();
  clearSuggestion();
});

function renderRackPreview() {
  const raw = rackInput.value;
  rackPreview.innerHTML = "";
  for (const ch of raw) {
    const isBlank = ch === "?";
    const letter = isBlank ? "?" : ch.toLowerCase();
    if (!isBlank && !/^[a-z]$/.test(letter)) continue;
    const tile = document.createElement("div");
    tile.className = "tile" + (isBlank ? " blank" : "");
    tile.textContent = isBlank ? "★" : letter;
    const pts = document.createElement("span");
    pts.className = "pts";
    pts.textContent = isBlank ? 0 : LETTER_VALUES[letter] || 0;
    tile.appendChild(pts);
    rackPreview.appendChild(tile);
  }
}

rackInput.addEventListener("input", renderRackPreview);

function clearSuggestion() {
  cells.forEach((el) => el.classList.remove("suggested"));
  activeMoveIndex = -1;
}

function showMove(index) {
  clearSuggestion();
  const move = currentMoves[index];
  if (!move) return;
  activeMoveIndex = index;
  for (const p of move.placements) {
    cellAt(p.row, p.col).classList.add("suggested");
  }
  Array.from(movesList.children).forEach((li, i) =>
    li.classList.toggle("active", i === index)
  );
  applyBtn.hidden = false;
}

function renderMovesList() {
  movesList.innerHTML = "";
  currentMoves.forEach((move, i) => {
    const li = document.createElement("li");
    const word = document.createElement("span");
    word.className = "word";
    word.textContent = move.word;
    const score = document.createElement("span");
    score.className = "score";
    score.textContent = `${move.score} pts`;
    li.appendChild(word);
    li.appendChild(score);
    li.addEventListener("click", () => showMove(i));
    movesList.appendChild(li);
  });
}

solveBtn.addEventListener("click", async () => {
  errorMsg.textContent = "";
  solveBtn.disabled = true;
  solveBtn.textContent = "Recherche...";
  try {
    const res = await fetch("/api/best-moves", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ board, rack: rackInput.value }),
    });
    const data = await res.json();
    if (!res.ok) {
      errorMsg.textContent = data.error || "Erreur inconnue.";
      resultsCard.hidden = true;
      return;
    }
    currentMoves = data.moves || [];
    resultsCard.hidden = false;
    if (currentMoves.length === 0) {
      movesList.innerHTML = "<li>Aucun coup possible avec ce jeu.</li>";
      applyBtn.hidden = true;
    } else {
      renderMovesList();
      showMove(0);
    }
  } catch (err) {
    errorMsg.textContent = "Impossible de contacter le serveur.";
  } finally {
    solveBtn.disabled = false;
    solveBtn.textContent = "Trouver le meilleur coup";
  }
});

applyBtn.addEventListener("click", () => {
  const move = currentMoves[activeMoveIndex];
  if (!move) return;
  for (const p of move.placements) {
    board[p.row][p.col] = p.blank ? p.letter.toUpperCase() : p.letter;
    blankMap[p.row][p.col] = p.blank;
  }
  renderAll();
  clearSuggestion();
  rackInput.value = "";
  renderRackPreview();
  resultsCard.hidden = true;
});

renderAll();
