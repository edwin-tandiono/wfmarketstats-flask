# wfmarketstats-flask
Back-end for [warframe market stats](https://github.com/edwin-tandiono/warframe-market-stats) written using Python Flask. Pay a visit at [https://edwin-tandiono.github.io/warframe-market-stats](https://edwin-tandiono.github.io/warframe-market-stats) to try the web interface!


## Disclaimer
This project is made for learning purposes. Please don't expect the endpoints to work reliably.

## Description
Warframe Market is a great app that allows users to place their orders for in-game items. Not only that, users also use this app to determine item prices based on its statistics. However, accessing the statistics page through the app requires a few clicks and loads away. This custom API is made to summarize all the information I need to determine item prices in a single request.

## Usage
`GET https://edwintandiono.pythonanywhere.com/items/<item-url-name>` to get item price information which includes:
* Latest daily average price  
* Lowest offer from online seller
* Highest offer from online buyer
* 90 days line chart of related transactions

Rank 0 and max rank stats are available for mods and arcanes.
Note that requests is limited to 1 request per second. This is to comply to warframe market public API recommendation of 3 request per second, as each request to this custom API will gather information from 3 endpoint in the warframe market public API (item information, order information, and statistics).

## Acknowledgements
Big thanks to Digital Extremes for the great game, also to Warframe Market team to provide such a useful public API. The public API is available at [this link](https://docs.google.com/document/d/1121cjBNN4BeZdMBGil6Qbuqse-sWpEXPpitQH5fb_Fo). This project is made for learning purposes, and all information used belong to their respective owners.
