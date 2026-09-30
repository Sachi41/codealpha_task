const log = document.getElementById("log");
const input = document.getElementById("input");
const sendBtn = document.getElementById("send");

function addMessage(text, who) {
  const div = document.createElement("div");
  div.className = "msg " + who;
  div.textContent = text;           // textContent keeps user text safe
  log.appendChild(div);
  log.scrollTop = log.scrollHeight;
}

async function send(text) {
  text = text.trim();
  if (!text) return;
  addMessage(text, "user");
  input.value = "";
  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error);
    addMessage(data.reply, "bot");
    if (data.end) {                  // "bye" ends the chat
      input.disabled = sendBtn.disabled = true;
      input.placeholder = "Chat ended - refresh to start again";
    }
  } catch (e) {
    addMessage("Error: could not reach the server.", "bot");
  }
}

sendBtn.addEventListener("click", () => send(input.value));
input.addEventListener("keydown", (e) => { if (e.key === "Enter") send(input.value); });
document.querySelector(".chips").addEventListener("click", (e) => {
  if (e.target.dataset.say && !input.disabled) send(e.target.dataset.say);
});
addMessage("Hi! I'm PyBot. Say hello, ask how I am, or say bye.", "bot");
