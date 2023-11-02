import requests
import json
import xml.dom.minidom as minidom
import datetime
import http.server
import socketserver
import os
import webbrowser

def start_web_server(port=8000, xml_file="prices.xml"):

    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), Handler) as httpd:
        httpd.directory = os.path.dirname(os.path.abspath(xml_file))
        print(f"Serving {xml_file} at http://localhost:{port}/")
        webbrowser.open_new_tab(f"http://localhost:{port}/{os.path.basename(xml_file)}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("Shutting down the server...")
            httpd.shutdown()

response = requests.get("https://www.elprisenligenu.dk/api/v1/prices/2023/05-30_DK2.json")

if response.status_code == 200:
    data = json.loads(response.text)

    prices = []

    for item in data:
        prices.append(item["DKK_per_kWh"])

    root = minidom.Document()

    prices_element = root.createElement("prices")
    root.appendChild(prices_element)

    for item in data:
        price_element = root.createElement("price")
        price_element.appendChild(root.createTextNode(str(item["DKK_per_kWh"])))
        prices_element.appendChild(price_element)

        timestamp_str = item["time_end"]

        timestamp = datetime.datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S%z")

        timestamp_element = root.createElement("timestamp")
        timestamp_element.appendChild(root.createTextNode(timestamp_str))

        price_element.appendChild(timestamp_element)

    new_line = input("Ny pris (DKK/kWh): ")
    if new_line.strip():
        price_element = root.createElement("price")
        price_element.appendChild(root.createTextNode(str(new_line)))
        prices_element.appendChild(price_element)

        timestamp_str = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S%z")

        timestamp_element = root.createElement("timestamp")
        timestamp_element.appendChild(root.createTextNode(timestamp_str))

        price_element.appendChild(timestamp_element)

    xml_string = root.toprettyxml(indent="  ")

    with open("prices.xml", "w") as f:
        f.write(xml_string)

    start_web_server()

    print("The XML file has been created with timestamps and a new line if input was provided.")
else:
    print("The request failed.")
