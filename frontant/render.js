// Lightweight markdown -> HTML renderer.
// Handles: ## headings, **bold**, bullet lists, [text](url) links,
// and bare URLs (auto-linkified), so sources are always clickable.

function renderMarkdown(rawText) {
  if (!rawText) return "";

  let text = escapeHTML(rawText);

  // Markdown links: [label](url)
  text = text.replace(
    /\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g,
    '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>'
  );

  // Bare URLs (not already inside an href="...")
  text = text.replace(
    /(?<!href=")(https?:\/\/[^\s<)]+)/g,
    '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>'
  );

  // Headings
  text = text.replace(/^### (.*)$/gm, "<h4>$1</h4>");
  text = text.replace(/^## (.*)$/gm, "<h3>$1</h3>");
  text = text.replace(/^# (.*)$/gm, "<h2>$1</h2>");

  // Bold
  text = text.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");

  // Bullet lists ("- item" lines grouped into <ul>)
  const lines = text.split("\n");
  let html = "";
  let inList = false;

  for (const line of lines) {
    const trimmed = line.trim();
    if (/^-\s+/.test(trimmed)) {
      if (!inList) {
        html += "<ul>";
        inList = true;
      }
      html += `<li>${trimmed.replace(/^-\s+/, "")}</li>`;
    } else {
      if (inList) {
        html += "</ul>";
        inList = false;
      }
      if (trimmed === "") {
        html += "<br>";
      } else if (!/^<h[2-4]>/.test(trimmed)) {
        html += `<p>${trimmed}</p>`;
      } else {
        html += trimmed;
      }
    }
  }
  if (inList) html += "</ul>";

  return html;
}

function escapeHTML(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

// Pull a "Score: X/10" style value out of critic feedback, if present.
function extractScore(feedbackText) {
  if (!feedbackText) return null;
  const match = feedbackText.match(/Score:\s*(\d+(?:\.\d+)?)\s*\/\s*10/i);
  return match ? parseFloat(match[1]) : null;
}