import os
import os.path
import sys
import time
import urllib.parse as up
from shutil import which

import requests


def authentication(client_id, redirect_uri, tdauser=None, tdapass=None):
    from selenium import webdriver
    client_id = client_id + '@AMER.OAUTHAP'
    url = 'https://auth.tdameritrade.com/auth?response_type=code&redirect_uri=' + up.quote(redirect_uri) + '&client_id=' + up.quote(client_id)

    options = webdriver.ChromeOptions()

    if sys.platform == 'darwin':
        # MacOS
        if os.path.exists("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"):
            options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        elif os.path.exists("/Applications/Chrome.app/Contents/MacOS/Google Chrome"):
            options.binary_location = "/Applications/Chrome.app/Contents/MacOS/Google Chrome"
    elif 'linux' in sys.platform:
        # Linux
        options.binary_location = which('google-chrome') or which('chrome') or which('chromium')

    else:
        # Windows
        if os.path.exists('C:/Program Files (x86)/Google/Chrome/Application/chrome.exe'):
            options.binary_location = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe'
        elif os.path.exists('C:/Program Files/Google/Chrome/Application/chrome.exe'):
            options.binary_location = 'C:/Program Files/Google/Chrome/Application/chrome.exe'

    chrome_driver_binary = which('chromedriver') or "/usr/local/bin/chromedriver"
    driver = webdriver.Chrome(chrome_driver_binary, chrome_options=options)

    driver.get(url)

    # Set tdauser and tdapass from environemnt if TDAUSER and TDAPASS environment variables were defined
    tdauser = tdauser or os.environ.get('TDAUSER', 'michaelgazsi98')
    tdapass = tdapass or os.environ.get('TDAPASS', 'Mika!20181111')

    # Fully automated oauth2 authentication (if tdauser and tdapass were intputed into the function, or found as
    # environment variables)
    if tdauser and tdapass:
        ubox = driver.find_element_by_id('username')
        pbox = driver.find_element_by_id('password')
        ubox.send_keys(tdauser)
        pbox.send_keys(tdapass)
        driver.find_element_by_id('accept').click()

        driver.find_element_by_id('accept').click()
        while True:
            try:
                code = up.unquote(driver.current_url.split('code=')[1])
                if code != '':
                    break
                else:
                    time.sleep(2)
            except (TypeError, IndexError):
                pass
    else:
        input('after giving access, hit enter to continue')
        code = up.unquote(driver.current_url.split('code=')[1])

    driver.close()

    resp = requests.post('https://api.tdameritrade.com/v1/oauth2/token',
                         headers={'Content-Type': 'application/x-www-form-urlencoded'},
                         data={'grant_type': 'authorization_code',
                               'refresh_token': 'R5F7H0vfLBGL9ag6wy8XKxAaeJKPDL3dHAhnqOwbemwy0OmTfQ60ov4f2EyKFpa0%2F%2BNvwepRtSNaj2ro0jNW1yDrge5%2FCyc9h%2F0cwet0MSeWurCvBbVi%2BOdes06NlZbQCSNFXJKh9GEJi7h%2FriYlZR%2Fm54usNsRUieJZj2bg7wViRSws%2F1onPV8dOzYDKFgPy3hZYUb9mJ2%2BI9p%2BIgRLRK37Gp8Boas6fE7nZWZ5ViBctiR3WRT8Q8ehhQDq3IWOaAG74%2FEvLJyXW%2BaQeXri%2FbYz7Ls7MPoIhiGaTyaXWh9xtJu6%2F6fkNyen33ygk4ISzq21LfZewqqJXWXwZSe1n%2BKpsEN1TDld1OuNtVrKZObzbGw7Ix%2F%2BcoZrmutURVD0HehCp5QfDS1lv1jJWirTW6tsVtDHcKM1UP0F%2B3zvY3IyvSUSlQvD7TT4smu100MQuG4LYrgoVi%2FJHHvljFLoUhHgBqpr%2FBw6TyYkcGQzNVgKPX%2FbQdqkQxJWyzN%2BJBSqBh5Ak0i2wq8hHhv3%2FL1M5z95k5R4tynKfOf7ZUqq6yjI4sQ7ouhPbpaRTGS37G2EcKeeszdf1KnGcjdebaVO5Cu22y5XQINmEk8YSkOPps2i4b5RX6zNFdBPjsLXJOUEclGmozs9zN51zWxyp2HJB%2BtcslXd%2Fk3dxzU%2FJhgfdjKLg79LQvbTRLRT4ZoqmoM9iKwISWj5Zm2uFvtDkpyZu3bKY0OuYHrOHgdbR6lBg3vEQ55YscgkVvlHFBIBmpR0an3W4RqwFcivX1jtjFHcyCuN5qXCAzL4xHCqDptr8bBPezxddiCm7yjH3MkzisJYEgWMf%2FhTEVS5FC8Bku3JjokEs1oO6%2Fe8y1Z0PV8QdSaaQUtuiZIhNKw%2BJkA%2BQisyN%2F6Xyln8Rhg%3D212FD3x19z9sWBHDJACbC00B75E',
                               'access_type': 'offline',
                               'code': code,
                               'client_id': client_id,
                               'redirect_uri': redirect_uri})
    if resp.status_code != 200:
        raise Exception('Could not authenticate!')
    return resp.json()


def access_token(refresh_token, client_id):
    resp = requests.post('https://api.tdameritrade.com/v1/oauth2/token',
                         headers={'Content-Type': 'application/x-www-form-urlencoded'},
                         data={'grant_type': 'refresh_token',
                               'refresh_token': refresh_token,
                               'client_id': client_id})
    if resp.status_code != 200:
        raise Exception('Could not authenticate!')
    return resp.json()


def main():
    client_id = input('client id:')
    redirect_uri = input('redirect uri:')
    print(authentication(client_id, redirect_uri))
