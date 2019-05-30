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
    for d in data:
        if count == 0 and header is True:
            header = d.keys()
            csvwriter.writerow(header)
            count += 1
        elif count == 0 and header is False:
            count += 1
        else:
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


def get_all_orders(shop, filename, fields):
    """ Page through all orders to write orders to csv """
    order_count_response = get_response(shop_url, "/admin/api/2019-04/orders/count.json")
    total_order_count = json.loads(order_count_response.content.decode('utf-8')).get('count')
    current_order_count = 0
    # limit of orders can be a range from 1-250.
    limit = 201

    order_response = get_response(shop, "/admin/api/2019-04/orders.json?limit=%s&fields=%s" % (limit, fields))
    data_file = open(filename, 'w')

    if order_response.status_code == 200:
        min_date = json_to_csv(order_response.content, 'orders', limit, data_file)
        current_order_count += limit - 1
        print("MIN_DATE: ", min_date)
    else:
        print("FAILED")

    while current_order_count < total_order_count:
        endpoint = "/admin/api/2019-04/orders.json?created_at_max=%s&limit=%s&fields=%s" % (min_date, limit, fields)
        order_response = get_response(shop, endpoint)

        if order_response.status_code == 200:
            min_date = json_to_csv(order_response.content, 'orders', limit, data_file, header=False)
            current_order_count += limit - 1
            print("COUNT: ", current_order_count)
        else:
            print("FAILED: ", order_response.status_code)

    data_file.close()


def get_all_customers(shop, filename, fields):
    customer_count_response = get_response(shop, "/admin/api/2019-04/customers/count.json")
    total_customer_count = json.loads(customer_count_response.content.decode('utf-8')).get('count')
    current_customer_count = 0
    # limit of customers can be a range from 1-250.
    limit = 201

    customer_response = get_response(shop, "/admin/api/2019-04/customers.json?limit=%s&fields=%s" % (limit, fields))
    data_file = open(filename, 'w')

    if customer_response.status_code == 200:
        min_date = json_to_csv(customer_response.content, 'customers', limit, data_file)
        current_customer_count += limit - 1
        print("MIN_DATE: ", min_date)
    else:
        print("FAILED")

    while current_customer_count < total_customer_count:
        endpoint = "/admin/api/2019-04/customers.json?created_at_max=%s&limit=%s&fields=%s" % (min_date, limit, fields)
        customer_response = get_response(shop, endpoint)

        if customer_response.status_code == 200:
            min_date = json_to_csv(customer_response.content, 'customers', limit, data_file, header=False)
            current_customer_count += limit - 1
            print("COUNT: ", current_customer_count)
        else:
            print("FAILED: ", customer_response.status_code)

    data_file.close()


if __name__ == '__main__':

    API_KEY = cfg.API_KEY
    API_SECRET = cfg.API_SECRET
    HOST = cfg.HOST

    # Set Shop
    shop_url = "https://%s:%s@%s" % (API_KEY, API_SECRET, HOST)
    shopify.ShopifyResource.set_site(shop_url)

    order_fields = 'id,email,created_at,total_price,buyer_accepts_marketing,location_id'
    customer_fields = 'id, email, accepts_marketing, created_at, orders_count, total_spent'

    # get_all_orders(shop_url, 'pursuit_orders_small.csv', order_fields)
    get_all_customers(shop_url, 'pursuit_customers_small.csv', customer_fields)
