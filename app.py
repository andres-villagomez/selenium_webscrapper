import json
from time import sleep
from selenium import webdriver
from selenium import __version__
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.remote import remote_connection
from base64 import b64encode
from flask import Flask, Response
import os
import platform
from selenium.webdriver.common.by import By
import google.auth.transport.requests
import google.oauth2.id_token

app = Flask(__name__)

if os.environ.get('SELENIUM_URL') is not None:
    selenium_url = os.environ.get('SELENIUM_URL')
else:
    raise Exception('No remote Selenium webdriver provided in the environment.')

# Overwriting the RemoteConnection class in order to authenticate with the Selenium Webdriver in Cloud Run.
class RemoteConnectionV2(remote_connection.RemoteConnection):
    @classmethod
    def set_remote_connection_authentication_headers(self):
        # Environment variable: identity token -- this can be set locally for debugging purposes.
        if os.environ.get('IDENTITY_TOKEN') is not None:
            print('[Authentication] An identity token was found in the environment. Using it.')
            identity_token = os.environ.get('IDENTITY_TOKEN')
        else:
            print('[Authentication] No identity token was found in the environment. Requesting a new one.')
            auth_req = google.auth.transport.requests.Request()
            identity_token = google.oauth2.id_token.fetch_id_token(auth_req, selenium_url)
        self._auth_header = {'Authorization': 'Bearer %s' % identity_token}
    
    @classmethod
    def get_remote_connection_headers(self, cls, parsed_url, keep_alive=False):
        """
        Get headers for remote request -- an update of Selenium's RemoteConnection to include an Authentication header.
        :Args:
         - parsed_url - The parsed url
         - keep_alive (Boolean) - Is this a keep-alive connection (default: False)
        """

        system = platform.system().lower()
        if system == "darwin": 
            system = "mac"

        default_headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json;charset=UTF-8',
            'User-Agent': 'selenium/{} (python {})'.format(__version__, system)
        }

        headers = {**default_headers, **self._auth_header}
        if 'Authorization' not in headers:
            if parsed_url.username:
                base64string = b64encode('{0.username}:{0.password}'.format(parsed_url).encode())
                headers.update({
                    'Authorization': 'Basic {}'.format(base64string.decode())
                })

        if keep_alive:
            headers.update({
                'Connection': 'keep-alive'
            })

        return headers

@app.route("/start_scraping/<query>")
def scrape(query: str):
    response = 'No results found.'
    selenium_connection = RemoteConnectionV2(selenium_url, keep_alive = True)
    selenium_connection.set_remote_connection_authentication_headers()
    chrome_driver = webdriver.Remote(selenium_connection, DesiredCapabilities.CHROME)
    try:
        chrome_driver.get('https://www.themoviedb.org/')
        browser_input = chrome_driver.find_element_by_xpath('/html/body/div[1]/main/section[1]/div/div/div/div[2]/form/label/input')
        sleep(10)
        browser_input.send_keys(query)
        sleep(10)
        browser_input.submit()
        sleep(10)
        results = chrome_driver.find_elements(By.XPATH, '//*[@data-media-type]')
        if len(results) > 0:
            for result in results:
                if result.get_attribute('href'):
                    result.click()
                    result_title = chrome_driver.find_element_by_xpath('/html/head/meta[12]').get_attribute('content')
                    result_score = chrome_driver.find_element_by_xpath('//*[@data-percent]')
                    result_score_value = result_score.get_attribute('data-percent')
                    response = f'{result_title} has a score of {result_score_value}. More info at {chrome_driver.current_url}.'
                    sleep(10)
                    break
    except Exception as e:
        return Response(json.dumps({'error': str(e)}), status=500, mimetype='application/json')
    finally:
        chrome_driver.quit()

    # return http 200 json response
    return Response(json.dumps({'message': response}), status=200, mimetype='application/json')



if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))