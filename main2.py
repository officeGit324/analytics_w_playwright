import textwrap
import time
from pathlib import Path
from playwright.sync_api import sync_playwright
import json


def setup_playwright_with_chrome_data():
    """
    Configure Playwright to use existing Chrome user data including login info and cache.
    """
    chrome_user_data_dir = str(Path.home() / "Library/Application Support/Google/Chrome")
    profile_directory = "Default"

    playwright = sync_playwright().start()
    browser = playwright.chromium.launch_persistent_context(
        user_data_dir=chrome_user_data_dir,
        channel="chrome",
        headless=False,
    )

    page = browser.new_page()
    return playwright, browser, page


def main():
    try:
        playwright, browser, page = setup_playwright_with_chrome_data()

        # Navigate to YouTube shorts
        page.goto('https://www.youtube.com/shorts/XW0SbwWHkgY', timeout=60000)

        # Click comments button and wait for it
        comment_button = page.locator("#comments-button").first
        comment_button.wait_for(state="visible", timeout=15000)
        comment_button.click()

        # Wait for comments to load
        first_comment = page.locator("ytd-comment-thread-renderer").first
        first_comment.wait_for(state="visible", timeout=15000)

        # Initialize tracking variables
        last_processed_index = 0
        no_new_comments_count = 0
        max_attempts = 3

        # Open file in append mode and write the opening bracket
        with open("comments_data.json", 'w', encoding='utf-8') as f:
            f.write('[\n')

        while True:
            # Scroll to bottom using JavaScript
            page.evaluate("""
                window.scrollTo({
                    top: document.documentElement.scrollHeight,
                    behavior: 'smooth'
                });

                const commentsSection = document.querySelector('ytd-item-section-renderer #contents');
                if (commentsSection) {
                    commentsSection.scrollTop = commentsSection.scrollHeight;
                }
            """)

            time.sleep(3)

            current_comments = page.locator("ytd-comment-thread-renderer").all()
            current_comment_count = len(current_comments)
            print(f"Current comment count: {current_comment_count}")

            if current_comment_count <= last_processed_index:
                no_new_comments_count += 1
                if no_new_comments_count >= max_attempts:
                    print("No new comments loaded after multiple attempts. Breaking loop.")
                    break
            else:
                no_new_comments_count = 0

            # Process only new comments
            with open("comments_data.json", 'a', encoding='utf-8') as f:
                for i in range(last_processed_index, current_comment_count):
                    try:
                        comment = current_comments[i]

                        # Extract comment data with error handling
                        try:
                            comment_text = comment.locator("yt-formatted-string#content-text").first.inner_text()
                        except:
                            comment_text = "N/A"

                        try:
                            user_name = comment.locator("#header-author #author-text").first.inner_text().strip()
                        except:
                            user_name = "N/A"

                        try:
                            comment_date = comment.locator("#header-author #published-time-text").first.inner_text()
                        except:
                            comment_date = "N/A"

                        try:
                            likes_on_comment = comment.locator("#vote-count-middle").first.inner_text()
                        except:
                            likes_on_comment = "0"

                        try:
                            replies_on_comment = comment.locator("#replies-count").first.inner_text()
                        except:
                            replies_on_comment = "0"

                        # Create comment JSON
                        comment_json = {
                            "index": i + 1,
                            "user_name": user_name,
                            "date": comment_date,
                            "likes_on_comment": likes_on_comment,
                            "replies_on_comment": replies_on_comment,
                            "text": comment_text
                        }

                        # Write comment to file with proper formatting
                        json_str = json.dumps(comment_json, ensure_ascii=False, indent=4)
                        f.write(json_str)

                        # Add comma if not the last item (we don't know if it's last yet)
                        f.write(',\n')

                        print(f"Processed comment {i + 1}")

                    except Exception as e:
                        print(f"Error processing comment {i + 1}: {str(e)}")

            last_processed_index = current_comment_count

            # Force a repaint to ensure new comments are loaded
            page.evaluate("window.scrollTo(0, 0)")
            time.sleep(1)
            page.evaluate("window.scrollTo(0, document.documentElement.scrollHeight)")

        # After all comments are processed, remove the last comma and add closing bracket
        with open("comments_data.json", 'rb+') as f:
            f.seek(-2, 2)  # Go to 2nd last character
            f.truncate()  # Remove the last comma and newline
            f.write(b'\n]')  # Add closing bracket

        print(f"Successfully processed {last_processed_index} comments")

    except Exception as e:
        print(f"An error occurred: {e}")

        # In case of error, try to properly close the JSON file
        try:
            with open("comments_data.json", 'rb+') as f:
                f.seek(-2, 2)
                f.truncate()
                f.write(b'\n]')
        except:
            pass

    finally:
        if 'browser' in locals():
            browser.close()
        if 'playwright' in locals():
            playwright.stop()


if __name__ == "__main__":
    main()