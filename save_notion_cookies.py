from playwright.sync_api import sync_playwright
import json

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    page.goto("https://www.notion.so")

    print("⚠️ Please log in to Notion manually. Press ENTER here after you're logged in.")
    input()

    # Save cookies & local storage
    storage = context.storage_state()
    with open("notion_state.json", "w") as f:
        json.dump(storage, f)

    print("✅ Saved login session to notion_state.json")
