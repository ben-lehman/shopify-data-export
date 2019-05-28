from flask import (
    Flask, Blueprint, render_template, request, redirect, Response, session, jsonify
)

import requests
import json
import csv

bp = Blueprint('export', __name__)


@bp.route('/')
def index():
    return render_template('export/index.html')


def json_to_csv(json_data, column_name, filename):
    """ convert api response data to csv file """
    data_str = json_data.decode('utf-8')
    data_parsed = json.loads(data_str)
    data = data_parsed[column_name]

    # Create file for writing
    data_file = open(filename, 'w')

    # create csv writer object
    csvwriter = csv.writer(data_file)
    count = 0

    for d in data:
        if count == 0:
            header = d.keys()
            csvwriter.writerow(header)
            count += 1
        csvwriter.writerow(d.values())
    data_file.close()


@bp.route('/orders', methods=['GET'])
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
        json_to_csv(response.content, 'orders', 'order_data.csv')
        print("Orders written!")

        return render_template('export/orders.html')
        # return response.content, response.status_code, response.headers.items()
    else:
        print("Failed")
        return False


@bp.route('/customers', methods=['GET'])
def customers():
    """ Get a stores orders """
    headers = {
        "X-Shopify-Access-Token": session.get("access_token"),
        "Content-Type": "application/json"
    }

    endpoint = "/admin/api/2019-04/customers.json"
    response = requests.get("https://{0}{1}".format(session.get("shop"),
                                                    endpoint), headers=headers)

    if response.status_code == 200:
        print("Writing customers to csv")
        json_to_csv(response.content, 'customers', 'customer_data.csv')
        print("Customers written!")

        return render_template('export/customers.html')
        # return response.content, response.status_code, response.headers.items()
    else:
        print("Failed")
        return False
