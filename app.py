from flask import Flask, render_template, jsonify
from playwright.sync_api import sync_playwright
import os
import re

app = Flask(__name__)

# Directory to save LinkedIn feed HTML
HTML_DIR = "linkedin_feed"
os.makedirs(HTML_DIR, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["POST"])
def linkedin_login():
    with sync_playwright() as p:
        # Launch the browser in visible mode with additional settings to bypass detection
        browser = p.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",  # Bypass automation detection
                "--no-sandbox",  # Avoid sandboxing
                "--disable-setuid-sandbox"  # Disable sandbox restrictions
            ]
        )

        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},  # Standard browser dimensions
            locale="en-US"  # Set locale to US English
        )

        page = context.new_page()

        try:
            # Step 1: Navigate to LinkedIn login page
            page.goto("https://www.linkedin.com/uas/login")
            print("LinkedIn Login Page Opened.")

            # Wait for the user to log in manually
            page.wait_for_selector("#global-nav", timeout=120000)
            print("Logged in successfully to LinkedIn.")

            # Step 2: Navigate to LinkedIn feed page
            page.goto("https://www.linkedin.com/feed/")
            print("Navigated to LinkedIn Feed Page.")

            # Step 3: Save HTML content of feed page
            html_content = page.content()
            html_file_path = os.path.join(HTML_DIR, "linkedin_feed.html")
            with open(html_file_path, "w", encoding="utf-8") as file:
                file.write(html_content)
            print(f"Feed page HTML saved to '{html_file_path}'.")

            # Step 4: Extract LinkedIn profile URL
            patterns = [
                r'"publicIdentifier":"([a-zA-Z0-9\-]+)"',  # Case 1 and Case 3
                r'<a href="/in/([a-zA-Z0-9\-]+)/"',  # Case 2
                r'"actionTarget":"(https://www.linkedin.com/in/[a-zA-Z0-9\-]+)'  # Case 4
            ]
            profile_url = None
            for pattern in patterns:
                match = re.search(pattern, html_content)
                if match:
                    if 'publicIdentifier' in pattern or '/in/' in pattern:
                        identifier = match.group(1)
                        profile_url = f"https://www.linkedin.com/in/{identifier}/"
                    elif 'actionTarget' in pattern:
                        profile_url = match.group(1)
                    break

            browser.close()

            if profile_url:
                return jsonify({"success": True, "profile_url": profile_url})
            else:
                return jsonify({"success": False, "message": "No LinkedIn Profile URL found."})

        except Exception as e:
            browser.close()
            return jsonify({"success": False, "error": str(e)})

if __name__ == "__main__":
    app.run(debug=True)
