from flask import jsonify
import json
import csv
import requests
import shopify

from config import Config as cfg


def json_to_csv(json_data, column_name, limit, data_file, header=True):
    """ convert api response data to csv file """
    data_str = json_data.decode('utf-8')
    data_parsed = json.loads(data_str)
    data = data_parsed[column_name]

    # create csv writer object
    csvwriter = csv.writer(data_file)
    count = 0
    print("limit: ", limit)
    for d in data:
        print("count: ", count)
        if count == 0 & header is True:
            header = d.keys()
            csvwriter.writerow(header)
            count += 1
        csvwriter.writerow(d.values())
        count += 1
        if count == limit:
            min_date = d['created_at']
            return min_date


def order_info(json_data, column_name):
    """ convert api response data to csv file """
    data_str = json_data.decode('utf-8')
    data_parsed = json.loads(data_str)
    data = data_parsed[column_name]

    current = ''
    for d in data:
        print("Data: ", d['created_at'])
        if current is '':
            current = d['created_at']
        else:
            print("Descending?: ", current > d['created_at'])
            current = d['created_at']


def get_response(shop, endpoint, params=''):
    if params == '':
        response = requests.get("%s%s" % (shop, endpoint))
    else:
        response = requests.get("%s%s&%s" % (shop, endpoint, params))

    return response


def get_all_orders(shop, filename):
    """ Page through all orders to write orders to csv """
    total_order_count = get_response(shop_url, "/admin/api/2019-04/orders/count.json")
    current_order_count = 0

    order_response = get_response(shop, "/admin/api/2019-04/orders.json?limit=250")
    data_file = open(filename, 'w')

    if order_response.status_code == 200:
        min_date = json_to_csv(order_response.content, 'orders', 250, data_file)
        print("MIN_DATE: ", min_date)
    else: 
        print("FAILED")

    endpoint = "/admin/api/2019-04/orders.json?created_at_min=%s&limit=250" % (min_date)
    order_response = get_response(shop, endpoint)

    if order_response.status_code == 200:
        min_date = json_to_csv(order_response.content, 'orders', 250, data_file, header=False)
    else: 
        print("FAILED: ", order_respone.status_code)

    data_file.close()

    # get order count
    # set current_order_count = 0
    # open datafile
    # get first 250 orders
    #      - set csv headers
    #      - write rows to csv
    #      - return last order's created at date
    # keep getting 250 orders with new min data param
    #   - update min date param
    #   - write rows to csv
    # close datafile



if __name__ == '__main__':
    #Set Shop
    shop_url = "https://%s:%s@%s" % (API_KEY, API_SECRET, HOST)
    shopify.ShopifyResource.set_site(shop_url)

    get_all_orders(shop_url, 'pursuit_order_500.csv')
