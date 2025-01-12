import time
from pathlib import Path
from playwright.sync_api import sync_playwright


def setup_playwright_with_chrome_data():
    """
    Configure Playwright to use existing Chrome user data including login info and cache.

    Returns:
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
        user_data_dir=chrome_user_data_dir,
        channel="chrome",  # Use installed Chrome instead of Playwright's bundled browser
        headless=False,  # Set to True if you don't need to see the browser
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

        # comments_w_other_elem = page.locator("#contents ytd-comment-thread-renderer")
        # comments_w_other_elem.wait_for(state="visible", timeout=15000)
        #
        # page.wait_for_timeout(2000)
        #
        # count = comments_w_other_elem.count()
        # print(f'comment count: {count}')

        # Wait for the first comment to be visible before proceeding
        first_comment = page.locator("ytd-comment-thread-renderer").first
        first_comment.wait_for(state="visible", timeout=15000)

        # Now get all comments after we know they're loaded
        comments = page.locator("ytd-comment-thread-renderer")
        comment_count = comments.count()
        print(f'comment_count: {comment_count}')

        print(f'comments: {comments}')

        iteration = 0
        for comment in comments.all():
            iteration += 1

            comment_text = comment.locator("yt-attributed-string span").first.inner_text()
            print(f'{iteration}. Comment text: {comment_text}')
            # print(f'Iteration{iteration}: {comment}')

        # Extract comments
        # for i in range(comment_count):
        #     comment = comments.nth(i)
        #
        #     # Get the author name (appears as @username)
        #     author = comment.locator("#author-text span").inner_text()
        #
        #     # Get the time
        #     time = comment.locator(".published-time-text span").inner_text()
        #
        #     # Combine them
        #     comment_info = f"{author} {time}"
        #     print(f"Comment {i + 1}: {comment_info}")



        #
        # for i in range(count):
        #     comment = comments_w_other_elem.nth(i)
        #     # Get the header info which contains author and time
        #     header_info = comment.locator("#header-author #author-text").inner_text()
        #     time = comment.locator("#header-author .published-time-text").inner_text()
        #
        #     print(f"Author and time: {header_info} {time}")

        # individual_comments = comments_w_other_elem.locator(">> #comment")
        # comments_count = individual_comments.count()
        # print(comments_count)


        # comments = comments_w_other_elem.locator(":scope > *:has(#comment)")
        # cmt_count = comments.count()
        # print(f"comment count: {cmt_count}")
        #
        # # Now for each container, get its #comment element
        # for i in range(cmt_count):
        #     container = comments.nth(i)
        #     comment = container.locator("#comment").first
        #
        #     # Get username and text from the comment
        #     # username = comment.locator("#header-author #author-text").text_content()
        #     comment_text = comment.locator("#expander #content-text").text_content()
        #     print(f"Comment {i + 1}:")
        #     # print(f"Username: {username}")
        #     print(f"Text: {comment_text}")
        #     print("---")

        # with open("comments_data.txt",'w', encoding="utf-8") as wf:
        #     for i in range(comments_count):
        #         # username = comments.nth(i).locator("#header-author #author-text").inner_text().strip()
        #         comment_text_locator = individual_comments.nth(i).locator("#expander >> #content-text")
        #         comment_text = comment_text_locator.inner_text().strip() if comment_text_locator.count() > 0 else "No Comment Text"
        #
        #         print(f'Comment: {comment_text}')
        #         # wf.write(f"Username: {username}\n")
        #         wf.write(f"Comment: {comment_text}\n\n")
        #         # child_html = child_elements.nth(i).inner_html()
        #         # wf.write(f"Child {i+1}: \n{child_html}\n\n")


        time.sleep(300)

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