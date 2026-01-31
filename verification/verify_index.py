from playwright.sync_api import sync_playwright

def verify_index():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        # Open local file
        page.goto("file:///app/index.html")

        # Take screenshot
        page.screenshot(path="verification/index_screenshot.png")
        print("Screenshot saved to verification/index_screenshot.png")

        # Print title and h1 text for log verification
        print(f"Title: {page.title()}")
        print(f"H1: {page.locator('h1').inner_text()}")

        browser.close()

if __name__ == "__main__":
    verify_index()
