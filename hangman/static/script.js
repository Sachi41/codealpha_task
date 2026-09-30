const $ = (id) => document.getElementById(id);
const LETTERS = "abcdefghijklmnopqrstuvwxyz".split("");
let state = null;

async function api(path, body) {
  const res = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body || {}),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || "Something went wrong");
  return data;
}

function render() {
  $("word").innerHTML = state.masked
    .map((c) => `<span>${c === "_" ? "" : c}</span>`).join("");
  $("lives").textContent = `Wrong guesses: ${state.wrong} / ${state.max_wrong}`;
  $("hint").textContent = `Hint: ${state.hint}`;
  for (let i = 1; i <= 6; i++) $("p" + i).classList.toggle("show", i <= state.wrong);

  const over = state.status !== "playing";
  document.querySelectorAll("#keyboard button").forEach((btn) => {
    const l = btn.dataset.letter;
    const used = state.guessed.includes(l);
    btn.disabled = used || over;
    btn.className = used ? (state.masked.includes(l) ? "correct" : "wrong") : "";
  });

  const msg = $("message");
  msg.className = "message " + state.status;
  if (state.status === "won") msg.textContent = "🎉 You won!";
  else if (state.status === "lost") msg.textContent = `Game over! The word was "${state.word}".`;
  else msg.textContent = "";
}

async function guess(letter) {
  if (!state || state.status !== "playing" || state.guessed.includes(letter)) return;
  try {
    state = await api("/api/guess", { id: state.id, letter });
    render();
  } catch (e) { showError(e.message); }
}

async function newGame() {
  try { state = await api("/api/new"); render(); }
  catch (e) { showError(e.message); }
}

function showError(text) {
  $("message").className = "message err";
  $("message").textContent = text;
}

$("keyboard").innerHTML = LETTERS
  .map((l) => `<button data-letter="${l}">${l}</button>`).join("");
$("keyboard").addEventListener("click", (e) => {
  if (e.target.dataset.letter) guess(e.target.dataset.letter);
});
document.addEventListener("keydown", (e) => {
  if (e.ctrlKey || e.metaKey || e.altKey) return;
  const k = e.key.toLowerCase();
  if (LETTERS.includes(k)) guess(k);
});
$("new").addEventListener("click", newGame);
newGame();
