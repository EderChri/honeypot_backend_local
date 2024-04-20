import os
import sys
import traceback

from services import crawler
from constants import MAIL_SAVE_DIR
from services.email.emailprocessor import EmailProcessor


def main(crawl=False):
    if crawl:
        crawler.fetch_all()

    email_filenames = os.listdir(MAIL_SAVE_DIR)
    for email_filename in email_filenames:
        try:
            print(f"Handling {email_filename}")
            processor = EmailProcessor(email_filename)
            processor.handle_email()
        except Exception as e:
            print(e)
            print(traceback.format_exc())


if __name__ == '__main__':
    if os.path.exists("./lock"):
        sys.exit(-1)

    with open("./lock", "w") as f:
        f.write("Running")

    arg_crawl = not ("--no-crawl" in sys.argv)
    main(crawl=False)

    os.remove("./lock")
