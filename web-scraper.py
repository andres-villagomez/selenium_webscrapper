@app.route("/")
def scrape():
    selenium_connection = RemoteConnectionV2(selenium_url, keep_alive = True)
    selenium_connection.set_remote_connection_authentication_headers()
    chrome_driver = webdriver.Remote(selenium_connection, DesiredCapabilities.CHROME)
    
    <INSERT_CODE_HERE>
    
    return

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int|
