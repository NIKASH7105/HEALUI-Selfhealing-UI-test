🔎 Self-Healing UI Test Automation Tool

This project is a self-healing UI automation tool that uses Playwright, FAISS, and Together AI embeddings to robustly test any HTML-based user interface—even if selectors change.

---

🚀 Purpose

Modern web UIs change frequently, causing traditional automated tests to break when selectors are updated.  
This tool uses AI-powered semantic search to find and interact with the correct elements, making your UI tests resilient and low-maintenance.

---

⚙️ How It Works

1. Test Flow as JSON:  
   Define your test steps (goto, click, fill, etc.) and fallback queries in a JSON file.

2. Element Data Collection:  
   For each page, the tool collects all interactive elements and generates semantic descriptions.

3. AI Embeddings & Similarity Search:  
   Descriptions are embedded using Together AI and indexed with FAISS.  
   If a selector fails, the tool uses a semantic fallback query to find the closest matching element and retries the action.

4. Self-Healing:  
   The test continues even if the UI changes, thanks to AI-powered selector recovery.

---

📝 Example `test_flow.json`

{
  "base_path": "C:/path/to/your/UI",
  "test_steps": [
    {"action": "goto", "target": "index.html"},
    {"action": "click", "query": "a[href='laptops.html']>>img", "fallback": "a with text 'Laptop'"},
    {"action": "fill", "query": "input#name", "value": "Test User", "fallback": "input for name"},
    {"action": "click", "query": "button[type='submit']", "fallback": "button with text 'Pay Now'"}
  ]
}

---

🛠️ Usage

1. Install dependencies:
   pip install playwright faiss-cpu numpy requests
   playwright install

2. Edit `test_flow.json` to match your UI and test flow.

3. Run the tool:
   python test_tool.py

---

🧠 Key Features

- Self-healing selectors: Recovers from selector failures using AI embeddings and similarity search.
- Configurable: Works with any UI—just update the JSON config.
- No code changes needed: Add or update test steps in JSON, not Python.

---

📌 Highlights

- Built with Playwright for browser automation.
- Uses Together AI for semantic understanding of UI elements.
- FAISS enables fast, robust similarity search for fallback selectors.
- Great for robust, low-maintenance UI test automation.

---
