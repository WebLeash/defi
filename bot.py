#-------------------------------------------------------------------------
# Trading Bot. Trading strategy is the RSI 
#-------------------------------------------------------------------------
# What is a Relative Strength Index (RSI) in trading?
# The Relative Strength Index (RSI) is a popular momentum oscillator developed in 1978.
# RSI provides an indication if the asset is overbought or undersold. It usually is displayed below the SMA/EMA graphs.
# An asset is usually considered overbought when the RSI is above 70% and undersold when it is below 30%.
# RSI is usually calculated over 14 intervals (mostly days) and you will see it represented as RSI14
#https://levelup.gitconnected.com/trading-using-python-relative-strength-index-rsi-f0c63c1c0db

# Nathan C Stott 7/3/2021 - Initial RSI implementation. 

# Work to do. 
# Bot needs Training. 



from binance.client import Client
from binance.enums import *
import threading

from binance.websockets import BinanceSocketManager
import config
import json
import pprint
import websocket
import talib
import numpy
import logging

from twisted.internet import reactor

# Constants 
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
TRADE_SYMBOL = 'BTC/USDT'
TRADE_QUANTITY = 0.05

log = "bot.log"
logging.basicConfig(filename=log,level=logging.DEBUG,format='%(asctime)s %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
logging.info('**** BOT STARTED *****')

closes = []
in_position = False

client = Client(config.API_KEY, config.API_SECRET)
bm = BinanceSocketManager(client)
#-----------------------------------------
time_res = client.get_server_time()
status = client.get_system_status()
info = client.get_exchange_info()
#--------------------------------------------
def process_message(msg):
    print("message type: {}".format(msg['e']))
   # print(msg)
    candle=msg['k']
    print("First Trade: ",format(candle['f']))
    print("Second Trade: ",format(candle['L']))
    print("---candle",format(candle))

    is_candle_closed = candle['x']
    close = candle['c']
    print("debug is_candle_closed= ",format(candle['x']))

    print("debug close= ",format(candle['c']))

    print("lencloses=",format(len(closes)))

    if is_candle_closed:
        print("candle closed at {}".format(close))
        closes.append(float(close))
        print("closes")
        print(closes)

        if len(closes) > RSI_PERIOD:
            np_closes = numpy.array(closes)
            rsi = talib.RSI(np_closes, RSI_PERIOD)
            print("all rsis calculated so far")
            logging.info('all rsis calculated so far')
            
            print(rsi)
            logging.info(rsi)
            last_rsi = rsi[-1]
            print("the current rsi is {}".format(last_rsi))


            if last_rsi > RSI_OVERBOUGHT:
                if in_position:
                    print("Overbought! Sell! Sell! Sell!")
                    logging.info('Overbought! Sell! Sell! Sell!')
                    price = candle['c']
                    logging.info(price)
                    logging.info('^^^ Sold at this price ^^')
                    # put binance sell logic here
                    #order_succeeded = order(SIDE_SELL, TRADE_QUANTITY, TRADE_SYMBOL)
                    #if order_succeeded:
                    in_position = False

                else:
                    print("It is overbought, but we don't own any. Nothing to do.")
                    logging.info("It is overbought, but we don't own any. Nothing to do.")


            if last_rsi < RSI_OVERSOLD:
                if in_position:
                    print("It is oversold, but you already own it, nothing to do.")
                    print("It is oversold, but you already own it, nothing to do.")
                else:
                    print("Oversold! Buy! Buy! Buy!")
                    logging.info("Oversold! Buy! Buy! Buy!")
                    sold = candle['c']
                    logging.info(sold)
                    logging.info("BUY at this price ^^^")
                    # put binance buy order logic here
                    #order_succeeded = order(SIDE_BUY, TRADE_QUANTITY, TRADE_SYMBOL)
                    #if order_succeeded:
                    in_position = True



#conn_key = bm.start_trade_socket('BTCUSDT', process_message)
conn_key = bm.start_kline_socket('BTCUSDT', process_message) # interval=KLINE_INTERVAL_30MINUTE default =1
bm.start()
#json_message = json.loads(info)
#pprint.pprint(info)

#print(client)
#print(ret1)
#print(time_res)
#print(status)
#print(info)
print(bm)

def stop_socket(self, conn_key):
        """Stop a websocket given the connection key

        :param conn_key: Socket connection key
        :type conn_key: string

        :returns: connection key string if successful, False otherwise
        """
        if conn_key not in self._conns:
            return

        # disable reconnecting if we are closing
        self._conns[conn_key].factory = WebSocketClientFactory(self.STREAM_URL + 'tmp_path')
        self._conns[conn_key].disconnect()
        del(self._conns[conn_key])

        # OBSOLETE - removed when adding isolated margin.  Loop over keys instead
        # # check if we have a user stream socket
        # if len(conn_key) >= 60 and conn_key[:60] == self._listen_keys['user']:
        #     self._stop_account_socket('user')

        # # or a margin stream socket
        # if len(conn_key) >= 60 and conn_key[:60] == self._listen_keys['margin']:
        #     self._stop_account_socket('margin')

        # NEW - Loop over keys in _listen_keys dictionary to find a match on
        # user, cross-margin and isolated margin:
        for key, value in self._listen_keys.items():
            if len(conn_key) >= 60 and conn_key[:60] == value:
                self._stop_account_socket(key)
