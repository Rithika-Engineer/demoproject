const getQuoteBtn = document.getElementById("getQuoteBtn");
const quoteText = document.getElementById("quoteText");
const quoteAuthor = document.getElementById("quoteAuthor");
const historyList = document.getElementById("historyList");

async function loadHistory() {
  try {
    const response = await fetch("http://127.0.0.1:5000/history");
    const history = await response.json();

    historyList.innerHTML = "";

    history.forEach((item) => {
      const div = document.createElement("div");
      div.classList.add("history-item");

      div.innerHTML = `
        <p>"${item.quote_text}"</p>
        <p><strong>- ${item.author}</strong></p>
        <p class="history-meta">Saved at: ${item.created_at} | Source: ${item.source}</p>
      `;

      historyList.appendChild(div);
    });
  } catch (error) {
    console.log("Error loading history:", error);
  }
}

getQuoteBtn.addEventListener("click", async () => {
  try {
    const response = await fetch("http://127.0.0.1:5000/quote");
    const data = await response.json();

    quoteText.innerText = `"${data.quote_text}"`;
    quoteAuthor.innerText = `- ${data.author}`;

    loadHistory();
  } catch (error) {
    console.log("Error getting quote:", error);
    quoteText.innerText = "Could not load quote.";
    quoteAuthor.innerText = "";
  }
});

loadHistory();