from flask import Flask, render_template, request, redirect, Response, session, jsonify
from config import Config as cfg
import requests
import json
import csv

app = Flask(__name__, template_folder="templates")
app.debug = True
app.secret_key = cfg.SECRET_KEY


@app.route('/orders', methods=['GET'])
def orders():
    """ Get a stores orders """
    headers = {
        "X-Shopify-Access-Token": session.get("access_token"),
        "Content-Type": "application/json"
    }

    endpoint = "/admin/api/2019-04/orders.json"
    response = requests.get("https://{0}{1}".format(session.get("shop"),
                                                   endpoint), headers=headers)

    if response.status_code == 200:
        print("Writing orders to csv")
        order_str = response.content.decode('utf-8')
        order_parsed = json.loads(order_str)
        ord_data = order_parsed['orders']

        # Create file for writing
        order_data = open('order_data.csv', 'w')
        # create csv writer object
        csvwriter = csv.writer(order_data)
        count = 0

        for order in ord_data:
            if count == 0:
                header = order.keys()
                csvwriter.writerow(header)
                count += 1
            csvwriter.writerow(order.values())
        order_data.close()

        print("Orders written!")

        return response.content, response.status_code, response.headers.items()
    else:
        print("Failed")
        return False


@app.route('/install', methods=['GET'])
def install():
    """
    Connect a shopify store
    """
    if request.args.get('shop'):
        shop = request.args.get('shop')
    else:
        return Response(response="Error:parameter shop not found", status=500)

    auth_url = "https://{0}/admin/oauth/authorize?client_id={1}&scope={2}&redirect_uri={3}".format(
        shop, cfg.SHOPIFY_CONFIG["API_KEY"], cfg.SHOPIFY_CONFIG["SCOPE"],
        cfg.SHOPIFY_CONFIG["REDIRECT_URI"]
    )
    print("Debug - auth URL: ", auth_url)
    return redirect(auth_url)


@app.route('/connect', methods=['GET'])
def connect():
    if request.args.get("shop"):
        params = {
            "client_id": cfg.SHOPIFY_CONFIG["API_KEY"],
            "client_secret": cfg.SHOPIFY_CONFIG["API_SECRET"],
            "code": request.args.get("code")
        }
        resp = requests.post(
            "https://{0}/admin/oauth/access_token".format(
                request.args.get("shop")
            ),
            data=params
        )

        if 200 == resp.status_code:
            resp_json = json.loads(resp.text)

            session['access_token'] = resp_json.get("access_token")
            session['shop'] = request.args.get("shop")

            return render_template('welcome.html', from_shopify=resp_json,
                                   orders=orders())
        else:
            print("Failed to get access token: ", resp.status_code, resp.text)
            return render_template('error.html')


if __name__ == "__main__":
    app.run(host="localhost", port=8080)
