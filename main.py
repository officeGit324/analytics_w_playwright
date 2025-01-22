import textwrap
import time
from pathlib import Path
from playwright.sync_api import sync_playwright
import json
from bs4 import BeautifulSoup

def extract_text_and_emojis(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    # Extract all text and emojis
    combined_text = ''.join(
        element.get_text() if element.name is None else element.get('alt', '')
        for element in soup.descendants
    )
    return combined_text

def setup_playwright_with_chrome_data():
    """
        Configure Playwright to use existing Chrome user data including login info and cache.

        # Returns:
            tuple: (browser instance, context instance, page instance)
    """

    # Default Chrome user data directory path for macOS
    chrome_user_data_dir = str(Path.home() / "Library/Application Support/Google/Chrome")

    # Default profile directory (usually "Default" or "Profile 1", "Profile 2", etc.)
    profile_directory = "Default"

    # Initialize Playwright
    playwright = sync_playwright().start()

    # Configure browser options
    browser = playwright.chromium.launch_persistent_context(
        user_data_dir = chrome_user_data_dir,
        channel = "chrome",  # Use installed Chrome instead of Playwright's bundled browser
        headless = False,  # Set to True if you don't need to see the browser
    )

    # Create a new page
    page = browser.new_page()

    return playwright, browser, page


def main():
    try:
        # Set up browser with Chrome data
        playwright, browser, page = setup_playwright_with_chrome_data()

        # Example: Navigate to a site that requires login
        page.goto('https://www.youtube.com/shorts/XW0SbwWHkgY',timeout=60000)

        # define the comment button
        comment_button = page.locator("#comments-button").first
        comment_button.wait_for(state="visible",timeout=15000)
        comment_button.click()

        '''
        #contents -> #comment -> #body -> #main -> #header ===> for (username and time of comment) 
                -> #header-author -> #author-text ==> (has username)
                
        #contents -> #comment -> #body -> #main -> #expander -> #content-text         
        '''

        # Wait for the first comment to be visible before proceeding
        first_comment = page.locator("ytd-comment-thread-renderer").first
        first_comment.wait_for(state="visible", timeout=15000)


        previous_comment_count = 0

        with open("comments_data002.json", 'w', encoding='utf-8') as json_file:

            json_file.write("[\n")

            while True:
                print("Entering while loop \n")

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

                # allow for comments to load
                time.sleep(3)

                current_comment_count = page.locator("ytd-comment-thread-renderer").count()
                print(f"current comment count: {current_comment_count}")

                if current_comment_count == previous_comment_count:
                    print("Breaking out of while loop")
                    break

                previous_comment_count = current_comment_count

                comments = page.locator("ytd-comment-thread-renderer").all()
                print(f'comments: {comments}')

                for index, comment in enumerate(comments):
                    print(f"{index}. comment found/n")

                    try:
                        comment_html = comment.locator("yt-attributed-string span").first.inner_html()
                        combined_text = extract_text_and_emojis(comment_html)
                        print(f"comment_text: {combined_text}")

                        #
                        #
                        user_name = comment.locator("#header #header-author h3").first.inner_text()
                        print(f"user_name: {user_name}")
                        #
                        comment_date = comment.locator("#header #header-author #published-time-text a").first.inner_text()
                        print(f"comment_date: {comment_date}")

                        #
                        # Finds the likes count on comment
                        likes_locator = comment.locator("ytd-comment-engagement-bar #toolbar #vote-count-middle")
                        if likes_locator.count() > 0:  # Check if the element exists
                            likes_on_comment = likes_locator.first.inner_text()
                            print(f"likes_on_comment: {likes_on_comment}")
                        else:
                            likes_on_comment = None
                            print("likes_on_comment: Not available")


                        # Finds the num of replies on the comment
                        replies_locator = comment.locator(
                            "#replies #expander yt-button-shape .yt-spec-button-shape-next__button-text-content span")
                        if replies_locator.count() > 0:  # Check if the element exists
                            replies_on_comment = replies_locator.first.inner_text()
                            print(f"replies_on_comment: {replies_on_comment} \n\n")
                        else:
                            replies_on_comment = None
                            print("replies_on_comment: Not available\n\n")

                        comment_data = {
                            "index": index + 1,
                            "user_name": user_name,
                            "date": comment_date,
                            "likes_on_comment": likes_on_comment,
                            "replies_on_comment": replies_on_comment,
                            "text": combined_text,
                        }
                        json.dump(comment_data, json_file, ensure_ascii=False, indent=4)
                        json_file.write(",\n")

                    except Exception as e:
                        print(f"Error writing comments on .txt file")

                # for i, comment in enumerate(comments, 1):
                #     print("Entered the for loop")
                #     try:
                #         comment_text = comment.locator("yt-attributed-string span").first.inner_text()
                #         print(f"comment_text: {comment_text}")
                #         #
                #         user_name = comment.locator("#header #header-author h3").first.inner_text()
                #         print(f"user_name: {user_name}")
                #         #
                #         comment_date = comment.locator("#header #header-author #published-time-text a").first.inner_text()
                #         print(f"comment_date: {comment_date}")
                #         #
                #         likes_on_comment = comment.locator("ytd-comment-engagement-bar #toolbar #vote-count-middle").first.inner_text()
                #         print(f"likes_on_comment: {likes_on_comment}")
                #         #
                #         replies_on_comment = comment.locator("#replies #expander yt-button-shape .yt-spec-button-shape-next__button-text-content span").first.inner_text()
                #         print(f"replies_on_comment: {replies_on_comment} \n\n")
                #
                #         wf.write(textwrap.dedent(f"""
                #             {{
                #                 "index":{i},
                #                 "user_name": "{user_name}",
                #                 "date": "{comment_date}",
                #                 "likes_on_comment": "{likes_on_comment}",
                #                 "replies_on_comment" : "{replies_on_comment}",
                #                 'text': "{comment_text}",
                #             }},
                #                 """))
                #
                #     except Exception as e:
                #         print(f"Error extracting comment {i}: {e}")



    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Clean up
        if 'browser' in locals():
            browser.close()
        if 'playwright' in locals():
            playwright.stop()


if __name__ == "__main__":
    main()