from playwright.sync_api import sync_playwright
import re
import os

def linkedin_manual_login():
    with sync_playwright() as p:
        # Launch a browser with visible mode
        browser = p.chromium.launch(
            headless=False,  # Use a visible browser
            args=["--disable-blink-features=AutomationControlled"]  # Bypass detection
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
        )

        # Open a new page
        page = context.new_page()

        # Step 1: Navigate to LinkedIn login page
        page.goto("https://www.linkedin.com/uas/login")
        print("LinkedIn Login Page Opened.")

        # Step 2: Wait for manual login
        print("Please log in manually.")
        page.wait_for_selector("#global-nav", timeout=120000)  # Wait for LinkedIn navbar after manual login
        print("Logged in successfully to LinkedIn.")

        # Step 3: Navigate to the LinkedIn feed page
        page.goto("https://www.linkedin.com/feed/")
        print("Navigated to LinkedIn Feed Page.")

        # Step 4: Save the HTML content of the feed page
        html_file = "linkedin_feed.html"
        try:
            html_content = page.content()  # Get the full page HTML content
            with open(html_file, "w", encoding="utf-8") as file:
                file.write(html_content)
            print(f"Feed page HTML saved to '{html_file}'.")
        except Exception as e:
            print("Failed to save feed page HTML:", e)

        # Step 5: Extract LinkedIn profile URL directly from the page content
        try:
            # Patterns to match different formats of the LinkedIn profile URL
            patterns = [
                r'"publicIdentifier":"([a-zA-Z0-9\-]+)"',  # Case 1 and Case 3
                r'<a href="/in/([a-zA-Z0-9\-]+)/"',  # Case 2
                r'"actionTarget":"(https://www.linkedin.com/in/[a-zA-Z0-9\-]+)'  # Case 4
            ]

            profile_url = None
            for pattern in patterns:
                match = re.search(pattern, html_content)
                if match:
                    # Case 1, 2, 3: Build the full URL from the identifier
                    if 'publicIdentifier' in pattern or '/in/' in pattern:
                        identifier = match.group(1)
                        profile_url = f"https://www.linkedin.com/in/{identifier}/"
                    # Case 4: URL is already complete
                    elif 'actionTarget' in pattern:
                        profile_url = match.group(1)
                    break

            if profile_url:
                print("LinkedIn Profile URL found:", profile_url)
            else:
                print("No LinkedIn Profile URL found in the HTML content.")
        except Exception as e:
            print("Failed to extract profile URL:", e)

        # Step 6: Delete the HTML file after processing
        try:
            if os.path.exists(html_file):
                os.remove(html_file)
                print(f"Deleted the file '{html_file}'.")
            else:
                print(f"File '{html_file}' does not exist.")
        except Exception as e:
            print("Failed to delete the HTML file:", e)

        # Close the browser
        browser.close()

if __name__ == "__main__":
    linkedin_manual_login()
