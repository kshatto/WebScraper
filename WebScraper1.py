import contextlib
import requests
import bs4
import os
import sys
import datetime

# import logging

log_filename = 'WebScraper1.log'


def simple_get(url):
    """
    Obtained original version of this code, June 2018, from:
    https://realpython.com/python-web-scraping-practical-introduction/
    Made my own modifications. -kshatto

    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.

    If no HTML is obtained, and the URL does not end with a forward slash,
    then add forward slash and try again.
    """
    try:
        with contextlib.closing(requests.get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except requests.RequestException as e:
        log_error('Error during request to {} : {}'.format(url, str(e)))
        return None


def is_good_response(resp):
    """
    Returns True if the response seems to be HTML.
    False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)


def log_error(e):
    print_to_console_and_or_log(e, True, True)


def get_html_and_print_status(url):
    html = simple_get(url)
    if html:
        print('{} | First try at getting html: Successful.'.format(url))
    else:
        print('{} | First try at getting html: NOT successful.'.format(url))
        if url[-1] == '/':
            print('{} | url already ends with slash so nothing more to try.'.format(url))
        else:
            url = url + '/'
            html = simple_get(url)
            if html:
                print('{} | Second try at getting html (after adding slash): Successful.'.format(url))
            else:
                print('{} | Second try at getting html (after adding slash): NOT successful.'.format(url))
    return html


def get_html(url):
    html = simple_get(url)
    if not html and url[-1] != '/':
        url = url + '/'
        html = simple_get(url)

    return html


def print_to_console_and_or_log(text,
                                console: bool,
                                log: bool):
    if console:
        print('{}'.format(text))

    if log:
        with open(log_filename, 'a') as fout:
            fout.write('{}\n'.format(text))


def main():
    print('Web Scraper')
    print('-----------')
    print()

    # logging.basicConfig(filename='WebScraper1.log',
    #                     level=logging.INFO)

    if os.path.exists(log_filename):
        os.remove(log_filename)

    print_to_console_and_or_log(datetime.datetime.now(),
                                False, True)

    filename = 'URLList.txt'
    if not os.path.exists(filename):
        log_text = 'Cannot find file {}'.format(filename)
        print_to_console_and_or_log(log_text, True, True)
        # logging.info(log_text)
        sys.exit()

    print('This will search the HTML in the URLs listed in {}, for a string you define.'.format(filename))
    string_to_find = input('What string do you want to search for? ')

    with open(filename) as fin:
        url_list = fin.readlines()

        for i, url in enumerate(url_list):
            url = url.strip()
            raw_html = get_html(url)

            # soup = bs4.BeautifulSoup(raw_html, 'html.parser')
            if raw_html:
                soup = bs4.BeautifulSoup(raw_html, 'lxml')

                found_it = (soup.prettify().find(string_to_find) > -1)

                if found_it:
                    print_to_console_and_or_log('{}) {} | Found string \'{}\''.format(i + 1, url, string_to_find),
                                                True, True)
                else:
                    print_to_console_and_or_log(
                        '{}) {} | Did not find string \'{}\''.format(i + 1, url, string_to_find),
                        True, True)

            else:
                print_to_console_and_or_log('{}) {} | Unable to retrieve HTML.'.format(i + 1, url),
                                            True, True)


if __name__ == '__main__':
    main()
