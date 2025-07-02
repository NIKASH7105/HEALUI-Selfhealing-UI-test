import json
import os
from playwright.sync_api import sync_playwright
import faiss
import numpy as np
import requests
from dotenv import load_dotenv

load_dotenv()
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
TOGETHER_EMBEDDING_URL = "https://api.together.xyz/v1/embeddings"

def get_embeddings_together(texts):
    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "BAAI/bge-base-en-v1.5-vllm",
        "input": texts
    }
    response = requests.post(TOGETHER_EMBEDDING_URL, headers=headers, json=payload)
    response.raise_for_status()
    data = response.json()
    return np.array([item["embedding"] for item in data["data"]])

def generate_element_data(page):
    elements = page.query_selector_all("button, input, a")
    data = []
    for el in elements:
        tag = el.evaluate("e => e.tagName.toLowerCase()")
        text = el.inner_text().strip()
        id_attr = el.get_attribute("id")
        name_attr = el.get_attribute("name")
        type_attr = el.get_attribute("type")
        placeholder = el.get_attribute("placeholder")
        parts = [tag]
        if text: parts.append(f"with text '{text}'")
        if id_attr: parts.append(f"id '{id_attr}'")
        if name_attr: parts.append(f"name '{name_attr}'")
        if type_attr: parts.append(f"type '{type_attr}'")
        if placeholder: parts.append(f"placeholder '{placeholder}'")
        description = f"{tag} " + ", ".join(parts[1:])
        if id_attr:
            selector = f"#{id_attr}"
        elif text:
            selector = f"text={text}"
        elif name_attr:
            selector = f"input[name='{name_attr}']"
        else:
            continue
        data.append({"selector": selector, "description": description})
    return data

def build_faiss_index_from_data(data):
    descriptions = [e["description"] for e in data]
    embeddings = get_embeddings_together(descriptions)
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    return index, data

def find_similar_selector(query, index, data, k=1):
    vec = get_embeddings_together([query])
    _, indices = index.search(vec, k)
    return data[indices[0][0]]["selector"]

def prepare_page_data(page):
    data = generate_element_data(page)
    index, data = build_faiss_index_from_data(data)
    return index, data

def run_ui_test(base_path, test_flow):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        index, data = None, None

        print("\n========== UI Test Started ==========")
        updated = False
        for i, step in enumerate(test_flow, 1):
            action = step["action"]
            print(f"\n--- Step {i}: {action.upper()} ---")
            if action == "goto":
                url = step["target"]
                if not (url.startswith("http://") or url.startswith("https://")):
                    url = "file:///" + os.path.join(base_path, url).replace("\\", "/")
                print(f"Navigating to: {url}")
                try:
                    page.goto(url)
                    print("Navigation successful.")
                except Exception as e:
                    print(f"[ERROR] Navigation failed: {e}")
                index, data = prepare_page_data(page)
            elif action == "click":
                query = step["query"]
                fallback = step.get("fallback")
                print(f"Clicking element: {query}")
                try:
                    page.locator(query).first.click()
                    print("Click successful.")
                except Exception:
                    print("[WARNING] Selector failed. Trying fallback...")
                    if fallback and index and data:
                        fb_selector = find_similar_selector(fallback, index, data)
                        print(f"Using fallback selector: {fb_selector}")
                        try:
                            page.locator(fb_selector).first.click()
                            print("Fallback click successful.")
                            # Save corrected selector in test_flow and JSON
                            step["query"] = fb_selector
                            updated = True
                        except Exception as e:
                            print(f"[ERROR] Fallback click failed: {e}")
            elif action == "fill":
                query = step["query"]
                value = step["value"]
                fallback = step.get("fallback")
                print(f"Filling element: {query} with value: {value}")
                try:
                    page.fill(query, value)
                    print("Fill successful.")
                except Exception:
                    print("[WARNING] Selector failed. Trying fallback...")
                    if fallback and index and data:
                        fb_selector = find_similar_selector(fallback, index, data)
                        print(f"Using fallback selector: {fb_selector}")
                        try:
                            page.fill(fb_selector, value)
                            print("Fallback fill successful.")
                            # Save corrected selector in test_flow and JSON
                            step["query"] = fb_selector
                            updated = True
                        except Exception as e:
                            print(f"[ERROR] Fallback fill failed: {e}")
        print("\n========== UI Test Completed ==========")
        # Only save updated test_flow to JSON file if any selectors were corrected
        if updated:
            with open(config_path, "w") as f:
                json.dump({"base_path": base_path, "test_steps": test_flow}, f, indent=2)
        browser.close()

if __name__ == "__main__":
    config_path = r"tests\test_flow.json"  # Path to your JSON config
    with open(config_path, "r") as f:
        config = json.load(f)
    base_path = config["base_path"]
    test_flow = config["test_steps"]
    run_ui_test(base_path, test_flow)