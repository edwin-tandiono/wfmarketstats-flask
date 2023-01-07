# Backend for Warframe Market Stats (https://github.com/echo-delta/warframe-market-stats)
# 
# As requested by the Warframe Market team on their API doc
# (https://docs.google.com/document/d/1121cjBNN4BeZdMBGil6Qbuqse-sWpEXPpitQH5fb_Fo),
# all outgoing requests will be limited to 3 RPS

from flask import Flask, redirect, url_for, request, render_template, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

import requests

app = Flask(__name__)
cors = CORS(app, resources={"*": {"origins": "*"}})

# Limiter will be applied for all sources, so we use the same
# key_func for all limiter
GLOBAL_KEY_FUNC = "wf_marketstats"
def get_global_key_func():
	return GLOBAL_KEY_FUNC

limiter = Limiter(key_func=get_global_key_func, app=app)

# Info page
@app.route('/')
@limiter.exempt
def index():
	return render_template("index.html")

# Get all list of available market items
# 
# Since we are only interested on their URL and names, we remove other
# unecessary properties
@app.route('/items')
@limiter.limit("3/second")
def get_items():
	url = "https://api.warframe.market/v1/items"
	result = requests.get(url).json()["payload"]["items"]

	for item in result:
		del item["id"]
		del item["thumb"]

	return jsonify(result)

# Get informations on certain items
# 
# These information will be included in the response
# - Item details (name, mod rank, trade tax, etc.)
# - Order info (minimum demand & maximum offer)
# - Item stats (average price, price history)
# 
# This endpoint will call 3 other endpoints from the Warframe Market server,
# so we only limit this to 1 RPS
@app.route('/items/<item_url>')
@limiter.limit("1/second")
def get_item_detail(item_url):
	# Get item details
	url = "https://api.warframe.market/v1/items/%s" % item_url
	result = requests.get(url)

	if result.status_code != 200:
		return jsonify(result.json())

	item_detail = result.json()["payload"]["item"]["items_in_set"][0]
	mod_max_rank = -1
	if "mod_max_rank" in item_detail:
		mod_max_rank = item_detail["mod_max_rank"]

  # Get order info 
	url = "https://api.warframe.market/v1/items/%s/orders" % item_url
	all_orders = requests.get(url).json()["payload"]["orders"]

	if mod_max_rank == -1:
		min = -1
		max = -1
		for order in all_orders:
			if order["user"]["status"] == "ingame":
				if (min == -1 or order["platinum"] < min) and order["order_type"] == "sell":
					min = order["platinum"]
				if (max == -1 or order["platinum"] > max) and order["order_type"] == "buy":
					max = order["platinum"]
		orders = {"min_sell":min, "max_buy":max}
	else:
		r0_min = -1
		r0_max = -1
		rmax_min = -1
		rmax_max = -1
		for order in all_orders:
			if order["user"]["status"] == "ingame" and order["mod_rank"] == 0:
				if (r0_min == -1 or order["platinum"] < r0_min) and order["order_type"] == "sell":
					r0_min = order["platinum"]
				if (r0_max == -1 or order["platinum"] > r0_max) and order["order_type"] == "buy":
					r0_max = order["platinum"]
			if order["user"]["status"] == "ingame" and order["mod_rank"] == mod_max_rank:
				if (rmax_min == -1 or order["platinum"] < rmax_min) and order["order_type"] == "sell":
					rmax_min = order["platinum"]
				if (rmax_max == -1 or order["platinum"] > rmax_max) and order["order_type"] == "buy":
					rmax_max = order["platinum"]
		orders = {"rank_0":{"min_sell":r0_min, "max_buy":r0_max},"max_rank":{"min_sell":rmax_min, "max_buy":rmax_max}}

  # Get item stats
	url = "https://api.warframe.market/v1/items/%s/statistics" % item_url
	stats = requests.get(url).json()["payload"]["statistics_closed"]["90days"]
	if mod_max_rank == -1:
		stats = [{"datetime":x["datetime"], "avg_price":x["avg_price"]} for x in stats]
	else:
		stats = {"rank_0":[{"datetime":x["datetime"], "avg_price":x["avg_price"]} for x in stats if x["mod_rank"] == 0], "max_rank":[{"datetime":x["datetime"], "avg_price":x["avg_price"]} for x in stats if x["mod_rank"] == mod_max_rank]}
			
	return jsonify(mod_max_rank=mod_max_rank, orders=orders, stats=stats)
 
if __name__ == '__main__':
   app.run(debug=False)