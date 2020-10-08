import numpy as np
import hashlib
import time
import requests
import collections
import pandas as pd
from time import sleep 
from datetime import datetime
import os
from random import random

from multiprocessing import Process , freeze_support
from threading import Thread
import pprint
import logging
from stockstats import StockDataFrame

from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, Bot

bot = Bot('1256009620:AAHP1EJkgyoBxkcALsRax5s8MuTJrDJcuIE')

# Users = {}
Users = {499985806 : {'access_id' : 'FBDE522C391A423E80A55123DE06276D' , 'secret' : '5FACF60F45B2480DB3D25CD5215809AD22F2800EE926F56D' , 'be_delete' : [] ,'currencies' : ['BTCUSDT'] ,'temp' : {} , 'part_code' : '' ,'del_message_first':[],'del_message_second':[] ,'status' : 'is off' ,'process_id': None ,'buy_permission' : False,'sell_permission' : False,'sell_rate' : 0.2 , 'buy_rate' : 0.1 ,'trades' : {'temp' : {}}, 'period_time' : '1hour'}}


class CoinExApiError(Exception):
    pass


class CoinEx:

    _headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36'
        }

    def __init__(self, access_id=None, secret=None , Chat_id =None):
        self._access_id = access_id
        self._secret = secret
        self.Chat_id = Chat_id

    def currency_rate(self):
        return self._v1('common/currency/rate')

    def asset_config(self , **params):
        return self._v1('common/asset/config' , **params)

    def market_list(self ):
        return self._v1('market/list')

    def market_ticker(self, market):
        return self._v1('market/ticker', market=market)

    def market_ticker_all(self):
        return self._v1('market/ticker/all')

    def market_depth(self, market, merge='0.00000001', **params):
        return self._v1('market/depth', market=market, merge=merge, **params)

    def market_deals(self, market, **params):
        return self._v1('market/deals', market=market, **params)

    def market_kline(self, market, type='1hour', **params):
        return self._v1('market/kline', market=market, type=type, **params)

    def market_info(self):
        return self._v1('market/info')

    def market_detail(self, market):
        return self._v1('market/detail', market=market)

    def margin_market(self):
        return self._v1('margin/market')

    def margin_transfer(self, from_account, to_account, coin_type, amount):
        return self._v1('margin/transfer', method='post', auth=True, from_account=from_account, to_account=to_account, coin_type=coin_type, amount=amount)

    def margin_account(self, **params):
        return self._v1('margin/account', auth=True, **params)

    def margin_config(self, **params):
        return self._v1('margin/config', auth=True, **params)

    def margin_loan_history(self, **params):
        return self._v1('margin/loan/history', auth=True, **params)

    def margin_loan(self, market, coin_type, amount):
        return self._v1('margin/loan', method='post', auth=True, market=market, coin_type=coin_type, amount=amount)

    def margin_flat(self, market, coin_type, amount, **params):
        return self._v1('margin/flat', method='post', auth=True, market=market, coin_type=coin_type, amount=amount, **params)

    def future_market(self):
        return self._v1('future/market')

    def future_transfer(self, from_account, to_account, coin_type, amount):
        return self._v1('future/transfer', method='post', auth=True, from_account=from_account, to_account=to_account, coin_type=coin_type, amount=amount)

    def future_account(self, **params):
        return self._v1('future/account', auth=True, **params)

    def future_limitprice(self, account_id):
        return self._v1('future/limitprice', account_id=account_id)

    def future_config(self, **params):
        return self._v1('future/config', auth=True, **params)

    def future_loan_history(self, account_id, **params):
        return self._v1('future/loan/history', auth=True, account_id=account_id, **params)

    def future_loan(self, account_id, coin_type, amount):
        return self._v1('future/loan', method='post', auth=True, account_id=account_id, coin_type=coin_type, amount=amount)

    def future_flat(self, account_id, coin_type, amount, **params):
        return self._v1('future/flat', method='post', auth=True, account_id=account_id, coin_type=coin_type, amount=amount, **params)

    def option_market(self):
        return self._v1('option/market')

    def option_detail(self):
        return self._v1('option/detail')

    def option_issue(self, market_type, amount):
        return self._v1('option/issue', method='post', auth=True, market_type=market_type, amount=amount)

    def option_redeem(self, market_type, amount):
        return self._v1('option/redeem', method='post', auth=True, market_type=market_type, amount=amount)

    def balance_info(self):
        return self._v1('balance/info', auth=True)

    def balance_coin_withdraw_list(self, **params):
        return self._v1('balance/coin/withdraw', auth=True, **params)

    def balance_coin_withdraw(self, coin_type, coin_address, actual_amount, transfer_method, **params):
        return self._v1('balance/coin/withdraw', method='post', auth=True, coin_type=coin_type, coin_address=coin_address, actual_amount=actual_amount, transfer_method=transfer_method, **params)

    def balance_coin_withdraw_cancel(self, coin_withdraw_id, **params):
        return self._v1('balance/coin/withdraw', method='delete', auth=True, coin_withdraw_id=coin_withdraw_id, **params)

    def balance_coin_deposit_list(self, **params):
        return self._v1('balance/coin/deposit', auth=True, **params)

    def balance_deposit_address(self, coin_type, **params):
        return self._v1('balance/deposit/address/{}'.format(coin_type), auth=True, **params)

    def balance_deposit_address_new(self, coin_type, **params):
        return self._v1('balance/deposit/address/{}'.format(coin_type), method='post', auth=True, **params)

    def sub_account_transfer(self, coin_type, amount, **params):
        return self._v1('sub_account/transfer', auth=True, coin_type=coin_type, amount=amount, **params)

    def order_limit(self, market, type, amount, price, **params):
        return self._v1('order/limit', method='post', auth=True, market=market, type=type, amount=amount, price=price, **params)

    def order_market(self, market, type, amount, **params):
        return self._v1('order/market', method='post', auth=True, market=market, type=type, amount=amount, **params)

    def order_ioc(self, market, type, amount, price, **params):
        return self._v1('order/ioc', method='post', auth=True, market=market, type=type, amount=amount, price=price, **params)

    def order_pending(self, market, page=1, limit=100):
        return self._v1('order/pending', method='get', auth=True, market=market, page=page, limit=limit)

    def order_finished(self, market, page=1, limit=100):
        return self._v1('order/finished', method='get', auth=True, market=market, page=page, limit=limit)

    def order_status(self, market, id):
        return self._v1('order/status', method='get', auth=True, market=market, id=id)

    def order_deals(self, id, page=1, limit=100):
        return self._v1('order/deals', method='get', auth=True, id=id, page=page, limit=limit)

    def order_user_deals(self, market, page=1, limit=100):
        return self._v1('order/user/deals', method='get', auth=True, market=market, page=page, limit=limit)

    def order_pending_cancel(self, market, id):
        return self._v1('order/pending', method='delete', auth=True, market=market, id=id)

    def order_pending_cancel_all(self, account_id, market):
        return self._v1('order/pending', method='delete', auth=True, account_id=account_id, market=market)

    def order_mining_difficulty(self):
        return self._v1('order/mining/difficulty', method='get', auth=True)

    def _v1(self, path, method='get', auth=False, **params):
        
        headers = dict(self._headers)

        if auth:
            if not self._access_id or not self._secret:
                # raise CoinExApiError('API keys not configured')
                bot.send_message(chat_id= self.Chat_id , text= 'API keys not configured' )
                logging.warning( 'API keys not configured' )

                return {'error' : True}

            params.update(access_id=self._access_id)
            params.update(tonce=int(time.time() * 1000))

        params = collections.OrderedDict(sorted(params.items()))

        if auth:
            headers.update(Authorization=self._sign(params))
        
        resp = None
        while not resp:
            
            try:
                if method == 'post':

                    resp = requests.post('https://api.coinex.com/v1/' + path, json=params, headers=headers)

                else:

                    fn = getattr(requests, method)
                    resp = fn('https://api.coinex.com/v1/' + path, params=params, headers=headers)
            
            except :
                
                _path = 'https://api.coinex.com/v1/' + path 
                bot.send_message(chat_id= self.Chat_id ,text= '⚠️ Error To Send Request to CoinEx!\n\n URL : {0}\n method : {1}\n params : {2}'.format( _path , method , params) )
                logging.warning('!! Error Send Request to CoinEx! [url:%s | method:%s | params:%s]' , _path , method , params) 

        return self._process_response(resp)

    def _process_response(self, resp):
        # resp.raise_for_status()

        data = resp.json()

        if data['code'] != 0:

            data['error'] = True
            logging.warning('!!>> Error process response : %s', data)
            return data
            # raise CoinExApiError(data['message'])

        return data['data']

    def _sign(self, params):

        data = '&'.join([key + '=' + str(params[key]) for key in sorted(params)])
        data = data + '&secret_key=' + self._secret
        data = data.encode()
        return hashlib.md5(data).hexdigest().upper()


class autoTrade():

    def __init__(self  ,chat_id):

        logging.warning('in auto trade')
        self.coinEx = CoinEx(Users[chat_id]['access_id'] , Users[chat_id]['secret'] ,chat_id )
        self.Chat_id = chat_id

    def check_order_time(self ,currency):
        

        currency_data =  self.coinEx.market_kline( currency , Users[self.Chat_id]['period_time'] )

        packetData = [ {'time' : float(i[0]) ,'open': float(i[1]) ,'close': float(i[2]) ,'high': float(i[3]) ,'low': float(i[4]) ,'volume': float(i[5]) ,'amount': float(i[6])} for i in currency_data]
        stock = StockDataFrame.retype(pd.DataFrame(packetData))

        macdLine = stock['macd']
        signalLine = stock['macds']
        rsi = stock['rsi']

        # =========================================== signal sell

        flag = {'rsi' : False , 'macd' : False}
        # logging.warning('rsi : %s ' ,dic['rsi'][-3:] )
        # logging.warning('macd : %s ' ,macdLine[-10:] )
        # logging.warning('ma9  : %s ' ,signalLine[-10:] )
        # logging.warning('def macd : %s ' ,macd[-10:] )
        if rsi[-3] > 50 or rsi[-2] > 50 or rsi[-1] > 50:
            logging.warning('rsi_1 to sell')
            flag['rsi'] = True

        defMacdFromSignal = abs(macdLine[-3:] - signalLine[-3:])
        if macdLine[-1] > 0 and (defMacdFromSignal[0] >= defMacdFromSignal[1] and defMacdFromSignal[1] >= defMacdFromSignal[2] ):
            logging.warning('macd to sell')
            flag['macd'] = True
        
        if all(flag.values()) :
            return 'sell'

        # =========================================== signal buy

        flag = {'rsi' : False , 'macd' : False}
        defMacdFromSignal = abs(macdLine[-3:] - signalLine[-3:])

        if rsi[-3] < 35 or rsi[-2] < 35 or rsi[-1] < 35:
            flag['rsi'] = True
            logging.warning('rsi_1 to buy')

        if macdLine[-1] < 0 and (defMacdFromSignal[0] >= defMacdFromSignal[1] and defMacdFromSignal[1] >= defMacdFromSignal[2] ) :
            flag['macd'] = True
            logging.warning('macd to buy')

        if all(flag.values()) :
            return 'buy'

        return None

    def waitForTrade(self):
        
        while True:

            temp = Users[self.Chat_id]['trades']['temp']

            for id ,detail in temp:

                if detail['state'] == True or (datetime.now() - detail['time']).total_seconds() > 300:
                    
                    order_type = Users[self.Chat_id]['trades'][id]['type']
                    currency = Users[self.Chat_id]['trades'][id]['currency']
                    price = Users[self.Chat_id]['trades'][id]['price'] = self.coinEx.market_ticker(currency)['ticker']['last'] 
                    rate =  Users[self.Chat_id][order_type + '_rate']
                    amount = Users[self.Chat_id]['trades'][id]['amount'] = float( self.coinEx.balance_info()['USDT']['available'] ) * rate / float( price )
                    permission = Users[self.Chat_id][ order_type + '_permission']
                    Users[self.Chat_id]['trades'][id]['time'] = datetime.now()
                    
                    if order_type == 'sell': 
                        order_type =  '🔸 Sell ' + currency
                    else:
                        order_type =  '🔹 Buy ' + currency

                    Error = False
                    modeText = '📋 Notice ...'
                    if permission:
                        
                        modeText = '✅ Done ...'
                        res_order = self.coinEx.order_market(currency , order_type , str(amount) )
                        if 'error' in res_order.keys():
                            Error = res_order
                    
                    Users[self.Chat_id]['trades'][id]['error'] = Error

                    del Users[self.Chat_id]['trades']['temp'][id]

                    text = '{0}\n\n{1}\n© Currency : {2}\n🔢 Amount : {3}\n💰 Price : {4}\n🔐 Permission : {5}\n⚠️ Error : {6}'.format(modeText ,order_type ,currency ,amount ,price ,permission , Error)
                    feedBack = bot.send_message(chat_id= self.Chat_id , text= text)
                    Users[self.Chat_id]['del_message_first'].append(feedBack['message_id'])
                    return

                elif detail['state'] == False :

                    Users[self.Chat_id]['trades'][id]['state'] = False
                    try:
                        bot.delete_message( self.Chat_id , Users[self.Chat_id]['trades'][id]['state']['message_id'] )
                    except:
                        logging.warning('message %s form <%s> not found' , Users[self.Chat_id]['trades'][id]['state']['message_id'] , self.Chat_id)

                    del Users[self.Chat_id]['trades']['temp'][id]

            sleep(1)

    def manageTrade(self):


        currencies = Users[self.Chat_id]['currencies']

        Thread(target= self.waitForTrade ).start()

        convertTime = { '1min': 60 ,'3min': 3*60 ,'5min': 5*60 ,'15min': 15*60 ,
                       '30min': 30*60 ,'1hour':60*60 ,'2hour': 2*60*60 ,'4hour': 4*60*60 ,
                       '6hour': 6*60*60 ,'12hour': 12*60*60 ,'1day' : 24*60*60 ,'3day': 3*24*60*60,'1week': 7*24*60*60 }
        
        while True:

            for currency in currencies :

                order_signal = self.check_order_time(currency)
                logging.warning('order singnal : %s' , order_signal)
                
                # s = self.coinEx.order_pending_cancel( currency , res_order['id'])(
                # logging.warning('== cancel-order : %s' , s)
                
                if not ([id for id in Users[self.Chat_id]['trades']['temp'].keys() if Users[self.Chat_id]['trades'][id]['currency'] == currency ] ) :

                    if order_signal == 'sell' :
                        
                        id = str(random() )[2:14:2]
                        while id in Users[self.Chat_id]['trades']:
                            id = str(random() )[2:14:2]

                        rate= Users[self.Chat_id]['sell_rate']
                        price = self.coinEx.market_ticker(currency)['ticker']['last']
                        amount = float( self.coinEx.balance_info()['USDT']['available'] ) * rate / float( price )

                        
                        Users[self.Chat_id]['trades'][id] = {'type': 'sell' ,'currency': currency ,'rate': rate ,'state' : None ,'price' : price , 'time' : datetime.now() ,'error' : False}
                        Users[self.Chat_id]['trades']['temp'][id] = {'time': datetime.now() , 'state': None , 'message_id' : None}
                        
                        text = '🔸 Type : Sell\n© Currency : {0}\n🔢 Amount : {1}\n💰 Price : {2}'.format( currency ,amount ,price)
                        reply = InlineKeyboardMarkup([[ InlineKeyboardButton( '📤 Sell' , callback_data = 'doTrade-{0}'.format(id) ) , InlineKeyboardButton( '♦️ Cancel' , callback_data = 'cancelTrade-{0}'.format(id) )]])
                        bot.send_message(chat_id= self.Chat_id ,text= '⏰ Waiting for Trade...\n\n{0}'.format(text) ,reply_markup=reply  )
                        Users[self.Chat_id]['trades']['temp'][id]['message_id'] = feedBack['message_id']


                    elif order_signal == 'buy':

                        id = str(random() )[2:14:2]
                        while id in Users[self.Chat_id]['trades']:
                            id = str(random() )[2:14:2]

                        rate= Users[self.Chat_id]['buy_rate']
                        price = self.coinEx.market_ticker(currency)['ticker']['last'] 
                        amount = float( self.coinEx.balance_info()['USDT']['available'] ) * rate / float( price )

                        
                        Users[self.Chat_id]['trades'][id] = {'type': 'buy' ,'currency': currency ,'rate': rate ,'state' : None ,'price' : price , 'time' : datetime.now() ,'error' : False}
                        Users[self.Chat_id]['trades']['temp'][id] = {'time': datetime.now() , 'state': None , 'message_id' : None}
                        
                        text = '🔹 Type : Buy\n© Currency : {0}\n🔢 Amount : {1}\n💰 Price : {2}'.format( currency ,amount ,price)
                        reply = InlineKeyboardMarkup([[ InlineKeyboardButton( 'Cancel' , callback_data = 'cancelTrade-{0}'.format(id)  ) , InlineKeyboardButton( 'Buy' , callback_data = 'doTrade-{0}'.format(id)  )]])
                        feedBack = bot.send_message(chat_id= self.Chat_id ,text= '⏰ Waiting for Trade...\n\n{0}'.format(text) ,reply_markup=reply  )
                        Users[self.Chat_id]['trades']['temp'][id]['message_id'] = feedBack['message_id']

            sleep( convertTime[ Users[self.Chat_id]['period_time']] / 60 )


class ManagerPlan():

    def getCoinExKeys(self , update , submit = False):

        Chat_id = update.message.chat.id
        logging.warning('>> getCoinExKeys  : %s' , Chat_id)

        if submit :

            res_sign = CoinEx( Users[Chat_id]['temp']['access_id'] , Users[Chat_id]['temp']['secret'] ).balance_info()

            if 'error' in res_sign.keys():

                feedBack = update.message.reply_text('Sign up on the site was not successful ⁉️\n\n💬 Message : {0}'.format(res_sign)  , reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('🔁 Edited CoinEx Keys' , callback_data='getCoinExKeys')]]) )
                Users[Chat_id]['del_message_first'].append(feedBack['message_id'])
                return

            else:

                Users[Chat_id]['access_id'] , Users[Chat_id]['secret'] = Users[Chat_id]['temp']['access_id'] , Users[Chat_id]['temp']['secret']
                Users[Chat_id]['temp'] = {}
                feedBack = update.message.reply_text('✅ Updated Access_id and Secret Code' )
                Users[Chat_id]['del_message_second'].append(feedBack['message_id'])

                return

        if Users[Chat_id]['part_code'] == 'getCoinExKeys_AccessID':

            Users[Chat_id]['temp']['access_id'] = update.message.text
            Users[Chat_id]['part_code'] = 'getCoinExKeys_Secret'
            feedBack = update.message.reply_text('Your *Accesss ID* is : `{0}`\n\nNow Send *Secret Key* for me'.format(update.message.text) , parse_mode='Markdown')
            Users[Chat_id]['del_message_first'].append(feedBack['message_id'])

        elif Users[Chat_id]['part_code'] == 'getCoinExKeys_Secret':
            
            Users[Chat_id]['part_code'] = ''
            Users[Chat_id]['temp']['secret'] = update.message.text
            
            # if Users[Chat_id]['secret'] == '':
            _secret = Users[Chat_id]['temp']['secret']
            _access_id = Users[Chat_id]['temp']['access_id']
            # else : 
            #     _secret = Users[Chat_id]['secret']
            #     _access_id = Users[Chat_id]['access_id']  

            text = 'Ok Now \nYour *Access ID* : `{0}`\nYour *Secret Key* : `{1}`\n\nCheck the sended information ,Please'.format( _access_id , _secret )
            feedBack = update.message.reply_text( text , reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton( 'Submit information 👍', callback_data = 'Submit_Information') , InlineKeyboardButton( '🔁 Edit Information', callback_data = 'getCoinExKeys')]]) , parse_mode= 'Markdown' )  
            Users[Chat_id]['del_message_first'].append(feedBack['message_id'])

        else:

            Users[Chat_id]['part_code'] = 'getCoinExKeys_AccessID'
            feedBack = update.message.reply_text('Send *Access ID* for me' , parse_mode='Markdown')
            Users[Chat_id]['del_message_second'].append(feedBack['message_id'])

    def getCurrencyListOfPerson(self, update , submit= False):

        Chat_id = update.message.chat.id
        logging.warning('>> getCurrencyListOfPerson  : %s' , Chat_id)

        if submit:

            Users[Chat_id]['currencies'] = Users[Chat_id]['temp']['currencies']
            Users[Chat_id]['temp']['currencies'] = {}
            self.configSetting(update)
            feedBack = update.message.reply_text('✅ Updated Currency List' )
            Users[Chat_id]['del_message_first'].append(feedBack['message_id'])
            return

        if Users[Chat_id]['part_code'] == 'getCurrencyListOfPerson' :
            
            Users[Chat_id]['part_code'] = ''
            market_list = CoinEx().market_list()
            
            Users[Chat_id]['temp']['currencies'] = list( set(([item.strip().upper() for item in update.message.text.split(',') if item.strip().upper() in market_list] )))
            notFound = list( set(([item.strip().upper() for item in update.message.text.split(',') if item.strip().upper() not in market_list] )))
            notFound = ' • '.join(notFound)
            _currency = ' • '.join(Users[Chat_id]['temp']['currencies'])

            reply = InlineKeyboardMarkup([[InlineKeyboardButton( 'Submit Currency 👍', callback_data = 'Submit_Currency') , InlineKeyboardButton( '🔁 Edited Currency ', callback_data = 'getCurrencyListOfPerson')]])
            feedBack = update.message.reply_text('💡 Found Currency is : `[{0}]`\n\n🏮 Not Found Currency : `[{1}]`'.format( _currency , notFound ) , reply_markup= reply , parse_mode='Markdown' )
            Users[Chat_id]['del_message_first'].append(feedBack['message_id'])

        else:

            Users[Chat_id]['part_code'] = 'getCurrencyListOfPerson'
            feedBack = update.message.reply_text('Send Currency list for me \n*(Ex : BTCUSDT , BTCETH ,... )*' , parse_mode='Markdown')
            Users[Chat_id]['del_message_first'].append(feedBack['message_id'])
            
    def showProfile(self , update):
        
        Chat_id = update.message.chat.id
        logging.warning('>> showProfile  : %s' , Chat_id)

        Users[Chat_id]['part_code'] = '' 
        
        if Users[Chat_id]['status'] == 'is On' :
            _status = 'is On ✔'
            _statusKey = 'Turn Off'
        else : 
            _status = 'is Off ⚠️' 
            _statusKey = 'Turn On'

        reply = InlineKeyboardMarkup([[ InlineKeyboardButton( _statusKey , callback_data = 'ChangeStatus'  )] ,
                                        [InlineKeyboardButton( '🗄 Trade History' , callback_data = 'showHistory')]])

        feedBack = update.message.reply_text('🤖 *Status*:  `{0}`\n\n© *Currency List* : `[{1}]`\n🔁 *Current Trade* : `{2}`'.format(
                                    _status , ' • '.join(Users[Chat_id]['currencies']) , len(Users[Chat_id]['trades']['temp']) ) , reply_markup= reply ,parse_mode='Markdown' )
        
        Users[Chat_id]['del_message_first'].append(feedBack['message_id'])

    def configSetting(self, update):

        Chat_id = update.message.chat.id
        logging.warning('>> configSetting  : %s' , Chat_id)

        Users[Chat_id]['part_code'] = ''

        textBuyPermission , _buyState = "❗️ has'nt Permission to Buy" , 'Not'
        textSellPermission , _sellState = "❗️ has'nt Permission to Sell" , 'Not'

        if Users[Chat_id]['buy_permission'] : 
            textBuyPermission , _buyState = "👍 has Permission to Buy" , 'Ok'

        if Users[Chat_id]['sell_permission']:
            textSellPermission , _buyState = "👍 has Permission to Sell" , 'Ok'
        
        reply = InlineKeyboardMarkup([  [InlineKeyboardButton( 'Edited CoinEx Keys', callback_data = 'getCoinExKeys')]
                                        ,[InlineKeyboardButton( textBuyPermission, callback_data = 'Permission-Buy_' + _buyState)] 
                                        ,[InlineKeyboardButton( textSellPermission, callback_data = 'Permission-Sell_' + _sellState)]
                                        ,[InlineKeyboardButton( 'Edited Buy Rate', callback_data = 'getRate-Buy')
                                        ,InlineKeyboardButton( 'Edited Sell Rate', callback_data = 'getRate-Sell')]
                                        ,[InlineKeyboardButton( 'Edited Currency', callback_data = 'getCurrencyListOfPerson')
                                        ,InlineKeyboardButton( 'Edited Period Time', callback_data = 'getPeriodTime')] 
                                        ,[InlineKeyboardButton( '🗑 Deleted history Trades', callback_data = 'deletedHistoryTrade')]])

        feedBack = update.message.reply_text('⚙ *Configure...* \n\n*Access ID* : `{0}******{1}`\n*Secret key* : `{2}******{3}` \n\n🎖 *Currency List* : `[{4}]`\n⏱ *Period Time* : `{5}`\n🔸 *Sell Rate* : `{6}`\n🔹 *Buy Rate* : `{7}`'.format(
                                    Users[Chat_id]['access_id'][:12] ,Users[Chat_id]['access_id'][-11:] , Users[Chat_id]['secret'][:12],Users[Chat_id]['secret'][-11:] , ' • '.join(Users[Chat_id]['currencies']) , Users[Chat_id]['period_time'] , 
                                    Users[Chat_id]['sell_rate'] , Users[Chat_id]['buy_rate'] ) , reply_markup= reply ,parse_mode= 'Markdown' )
        
        Users[Chat_id]['del_message_first'].append(feedBack['message_id'])
    
    def deletedHistoryTrade(self , update , submit= False):

        Chat_id = update.message.chat.id
        logging.warning('>> deletedHistoryTrade  : %s' , Chat_id)

        if len(Users[Chat_id]['trades']) == 1:

            feedBack = update.message.reply_text('🤷‍♂️ History Trade is Empty !')
            Users[Chat_id]['del_message_second'].append(feedBack['message_id'])
            
            return

        if submit:

            backUp = Users[Chat_id]['trades']['temp']
            Users[Chat_id]['trades'] = {'temp' : backUp}
            feedBack = update.message.reply_text('▫️ Now History Trade is Clean' )
            Users[Chat_id]['del_message_second'].append(feedBack['message_id'])

        else:

            reply = InlineKeyboardMarkup([[InlineKeyboardButton( "Yes i'm Sure 👍" , callback_data = 'DoDeleteHT'  ) , InlineKeyboardButton( '♦️ Cancel' , callback_data = 'cancelDeleteHT'  )]])
            feedBack = update.message.reply_text('Are you Sure About Delete History Trade ?' ,reply_markup= reply)
            Users[Chat_id]['del_message_first'].append(feedBack['message_id'])

    def showHistory(self , update):

        Chat_id = update.message.chat.id
        logging.warning('>> showHistory  : %s' , Chat_id)
        num = 1

        if len(Users[Chat_id]['trades']) == 1:
            feedBack = update.message.reply_text('🤷 No trade done yet!')
            Users[Chat_id]['del_message_second'].append(feedBack['message_id'])
            
            return 

        for id , detail in Users[Chat_id]['trades'].items():
            if id != 'temp' :

                if detail['type'] == 'sell':
                    _type = '🔸 Sell'
                else :
                    _type = '🔹 Buy'

                currency = detail['currency']
                price = detail['price']
                amount = detail['amount']
                time = detail['time'].strftime( '%Y-%m-%d  %H:%M' )

                if detail['state'] == True :
                    status = 'Done'

                elif detail['state'] == False:
                    status = 'Canceled'

                elif detail['state'] == None and (datetime.now() - detail['time']).total_seconds() > 300 :
                    status = 'Done Auto'

                elif detail['state'] == None and (datetime.now() - detail['time']).total_seconds() < 300 :
                    status = 'Current...'

                text = '{0}  {1}\n\n📋 Status : {2}\n© Currency : {3}\n🔢 Amount : {4}\n💰 🧾Price : {5}\n⌚️ Time : {6}'.format(_type ,num ,status ,currency ,amount ,price ,time)

                feedBack = update.message.reply_text(text )
                Users[Chat_id]['del_message_first'].append(feedBack['message_id'])
                num += 1

    def getRate(self, update ):
        
        Chat_id = update.message.chat.id
        logging.warning('>> getRate  : %s' , Chat_id)
        
        if Users[Chat_id]['part_code'] and Users[Chat_id]['part_code'].split('-')[0] == 'getRate' :
            
            _rateType = Users[Chat_id]['part_code'].split('-')[1]

            try :
                if float(update.message.text) > 0 and float(update.message.text) <= 1:
                    Users[Chat_id][_rateType  + '_rate'] = float(update.message.text)
                    Users[Chat_id]['part_code'] = ''
                    self.configSetting(update)
                    feedBack = update.message.reply_text('✅ Change {0} rate to {1} successfully'.format(_rateType.capitalize() , update.message.text) )
                    Users[Chat_id]['del_message_first'].append(feedBack['message_id'])

                else:
                    feedBack = update.message.reply_text('❗️ Please Send For me With Standard Foramt\nEx : 0.1 - 0.9 ')
                    Users[Chat_id]['del_message_second'].append(feedBack['message_id'])

            except:
                feedBack = update.message.reply_text('❗️ Please Send For me With Standard Foramt\nEx : 0.1 - 0.9 ')
                Users[Chat_id]['del_message_second'].append(feedBack['message_id'])
                

        else:
            
            Users[Chat_id]['part_code'] = 'getRate-' + update.data.split('-')[1].lower()

            feedBack = update.message.reply_text('Send {0} Rate for me [ 0.1 - 0.9]'.format(update.data.split('-')[1]) )
            Users[Chat_id]['del_message_first'].append(feedBack['message_id'])

    def changeModePermission(self, update):
        
        Chat_id = update.message.chat.id
        logging.warning('>> changeModePermission  : %s' , Chat_id)

        replyKeyboard = update.message.reply_markup['inline_keyboard']

        keyboardLine = []
        
        for line in replyKeyboard :
            itemInLine = []
            for item in line:
                
                if item['callback_data'] == update.data :

                    if item['callback_data'] == 'Permission-Buy_Not':
                        callBack ,text = 'Permission-Buy_Ok' , "👍 has Permission to Buy"
                        Users[Chat_id]['buy_permission'] = True

                    elif item['callback_data'] == 'Permission-Buy_Ok':
                        callBack ,text = 'Permission-Buy_Not' , "❗️ has'nt Permission to Buy"
                        Users[Chat_id]['buy_permission'] = False

                    elif item['callback_data'] == 'Permission-Sell_Not':
                        callBack ,text = 'Permission-Sell_Ok' , "👍 has Permission to Sell"
                        Users[Chat_id]['sell_permission'] = True

                    elif item['callback_data'] == 'Permission-Sell_Ok':
                        callBack ,text = 'Permission-Sell_Not' , "❗️ has'nt Permission to Sell"
                        Users[Chat_id]['sell_permission'] = False
                    
                    itemInLine.append(InlineKeyboardButton( text , callback_data = callBack))
                    continue

                itemInLine.append(InlineKeyboardButton( item['text'] , callback_data = item['callback_data']))
            
            keyboardLine.append(itemInLine)

        update.edit_message_reply_markup(reply_markup= InlineKeyboardMarkup(keyboardLine))

    def changeStatus(self , update):

        Chat_id = update.message.chat.id
        logging.warning('>> changeStatus  : %s' , Chat_id)

        if Users[Chat_id]['status'] == 'is On':

            Users[Chat_id]['status'] = 'is Off'
            _status , _statusKey  = self._manageProcess(Chat_id ,start= False)

        else:

            if not Users[Chat_id]['access_id'] :
                update.message.reply_text('🤷 Send First *Access ID* and *Secret Key* Code!' , parse_mode='Markdown')
                return
            
            if not Users[Chat_id]['currencies'] :
                update.message.reply_text('🤷 Send First your *Currencies*!' , parse_mode='Markdown')
                return

            else :

                Users[Chat_id]['status'] = 'is On'
                _status , _statusKey = self._manageProcess(Chat_id ,start= True)


        reply = InlineKeyboardMarkup([[ InlineKeyboardButton( _statusKey , callback_data = 'ChangeStatus'  )] ,
                                        [InlineKeyboardButton( '🗄 Trade History' , callback_data = 'showHistory')]])

        update.edit_message_text('🤖 *Status* :  `{0}`\n\n© *Currency List* : `[{1}]`\n🔁 *Current Trade* : `{2}`'.format(
                                    _status ,  ' • '.join(Users[Chat_id]['currencies'])  , len(Users[Chat_id]['trades']['temp']) ) , reply_markup= reply , parse_mode='Markdown')
        
    def changeModeIdTempTrade(self , chat_id , id , delete= False):

        if delete:

            Users[chat_id]['trades']['temp'][id]['state'] = False

        else :

            Users[chat_id]['trades']['temp'][id]['state'] = True

    def getPeriodTime(self, update , submit= False):

        Chat_id = update.message.chat.id
        logging.warning('>> getPeriodTime  : %s' , Chat_id)

        if submit:

            Users[Chat_id]['period_time'] = update.data.split('-')[1]
            self.configSetting(update)
            feedBack = update.message.reply_text('✅ Successfuly Changed Period Time')
            Users[Chat_id]['del_message_first'].append(feedBack['message_id'])

        else:

            ls_inlineKeyboard = []
            ls_temp = []
            ls_times = ['1min' ,'3min' ,'5min' ,'15min' ,'30min' ,'1hour' ,'2hour' ,'4hour' ,'6hour' ,'12hour' ,'1day' ,'3day' ,'1week' ]
            
            for time in ls_times:

                ls_temp.append( InlineKeyboardButton( time , callback_data = 'getPeriodTime-' + time) )

                if len(ls_temp) % 3 == 0 :
                    ls_inlineKeyboard.append(ls_temp)
                    ls_temp = [] 

            if ls_temp:
                ls_inlineKeyboard.append(ls_temp)

            feedBack = update.edit_message_text('⏱ Choice Period Time : ' , reply_markup= InlineKeyboardMarkup(ls_inlineKeyboard) )
            Users[Chat_id]['del_message_first'].append(feedBack['message_id'])

    def _manageProcess(self ,Chat_id ,start= False):
        
        logging.warning('>> _manageProcess <%s> : %s' , start , Chat_id)

        if start:

            Users[Chat_id]['process_id'] = Process(target=autoTrade( Chat_id ).manageTrade )
            Users[Chat_id]['process_id'].start()


            _status = 'is On ✔'
            _statusKey = 'Turn Off'

            return _status , _statusKey 

        else:
            

            Users[Chat_id]['process_id'].kill()
            Users[Chat_id]['process_id'] = None
            
            _status = 'is Off ⚠️'
            _statusKey = 'Turn On'
            
            return _status , _statusKey 


class TelegramBot( ManagerPlan ):

    def __init__(self , hashCode):

        self._hashCode = hashCode

    def main(self):
        
        updater = Updater( self._hashCode, use_context=True)
        updater.dispatcher.add_handler(CommandHandler('start', self.start))
        updater.dispatcher.add_handler(MessageHandler(Filters.text, self.reciveMessageText))
        updater.dispatcher.add_handler(CallbackQueryHandler(self.callBackButton))
        updater.dispatcher.add_error_handler(self.error)

        updater.start_polling()
        updater.idle()

    def start(self , update , context):

        Chat_id = update.message.chat.id
        logging.warning('>> Start  : %s' , Chat_id)

        if Chat_id not in Users.keys():

            update.message.reply_text('WyVern' , reply_markup=ReplyKeyboardMarkup([[ KeyboardButton('Setting') , KeyboardButton('Profile')]], resize_keyboard=True ))

            Users[Chat_id] = { 
                                'access_id' : '' , 
                                'secret' : '' , 
                                'be_delete' : [] ,
                                'currencies' : [] ,
                                'temp' : {} , 
                                'part_code' : '' , 
                                'status' : 'is off' ,
                                'process_id': None ,
                                'buy_permission' : False,
                                'sell_permission' : False,
                                'sell_rate' : 0.8,
                                'buy_rate' : 0.4,
                                'trades' : {'temp' : {}}, # struct : {'temp' : {} , 'id' : {} , ...}
                                'period_time' : '1hour' ,
                                'del_message_first' : [] ,
                                'del_message_second' : []
                                }

            self.getCoinExKeys(update)
            

        else:
            
            update.message.reply_text('*WyVern*' , reply_markup=ReplyKeyboardMarkup([[KeyboardButton('Setting') , KeyboardButton('Profile')]], resize_keyboard=True ) ,parse_mode= 'Markdown' )
            update.message.delete()

    def reciveMessageText(self , update , context):
        
        Chat_id = update.message.chat.id
        logging.warning('>> reciveMessageText <%s> FROM %s' , update.message.text, Chat_id)

        dicFunction = {
                        'Setting' : lambda : self.configSetting(update),
                        'Profile' : lambda : self.showProfile(update)
                         }

        dicPartCode = {
                        'getCoinExKeys' : lambda : self.getCoinExKeys(update),
                        'getCoinExKeys_AccessID' : lambda : self.getCoinExKeys(update),
                        'getCoinExKeys_Secret' : lambda : self.getCoinExKeys(update),

                        'getCurrencyListOfPerson' : lambda : self.getCurrencyListOfPerson(update),
                        'getRate' : lambda : self.getRate(update)
                        }
        
        Users[Chat_id]['del_message_second'].append(update.message.message_id)

        # listSafeFromDelete = ['getRate']
        # if Users[Chat_id]['part_code'].split('-')[0] in listSafeFromDelete:
        #     Users[Chat_id]['del_message_first'].pop( Users[Chat_id]['del_message_first'].index(update.message.message_id))
        #     Users[Chat_id]['del_message_second'].append(update.message.message_id)

        self.deleteMessage(Chat_id)

        if update.message.text in dicFunction.keys():

            dicFunction[ update.message.text ]()

        elif Users[Chat_id]['part_code'].split('-')[0] in dicPartCode.keys():

            dicPartCode[ Users[Chat_id]['part_code'].split('-')[0] ]()

        else :
            update.message.delete()

    def callBackButton(self, update, context):

        query = update.callback_query
        Chat_id = query.message.chat.id
        logging.warning('>> callBackButton <%s> FROM %s' , query.data, Chat_id)

        dicFunction = {
                        'getCurrencyListOfPerson' : lambda : self.getCurrencyListOfPerson(query),
                        'getCoinExKeys' : lambda : self.getCoinExKeys(query),
                        'Submit_Information' : lambda : self.getCoinExKeys(query , submit= True),
                        'Submit_Currency' : lambda : self.getCurrencyListOfPerson(query , submit= True),
                        'ChangeStatus' :  lambda : self.changeStatus(query),
                        'getPeriodTime' : lambda : self.getPeriodTime(query),
                        'deletedHistoryTrade' : lambda : self.deletedHistoryTrade(query ),
                        'cancelDeleteHT' : lambda : query.message.delete(), # Delete own Message
                        'DoDeleteHT' : lambda : self.deletedHistoryTrade(query , submit=True),
                        'showHistory' : lambda : self.showHistory(query)
                        } # NOTE : list All Function relete to CallBackQurey

        dicFucntion_2 = {
                        'getPeriodTime' : lambda : self.getPeriodTime(query , submit=True) ,
                        'cancel' : lambda : self.changeModeIdTempTrade(Chat_id, query.data.split('-')[1] , delete=True ), # query.data = [cancel]-[id] 
                        'doTrade' : lambda : self.changeModeIdTempTrade(Chat_id, query.data.split('-')[1] , delete=False ) ,
                        'getRate' : lambda : self.getRate(query),
                        'Permission' : lambda : self.changeModePermission(query)
                        }
        
        listSafeFromDelete = ['Permission' , 'getPeriodTime' , 'deletedHistoryTrade' ,'showHistory' , 'ChangeStatus']
        if query.data.split('-')[0] in listSafeFromDelete:
            Users[Chat_id]['del_message_first'].pop( Users[Chat_id]['del_message_first'].index(query.message.message_id))
            Users[Chat_id]['del_message_second'].append(query.message.message_id)

        self.deleteMessage(Chat_id)
        logging.warning('=== <%s>' , query.data.split('-') )
        if query.data in dicFunction.keys():

            dicFunction[query.data.split('-')[0]]()

        
        elif query.data.split('-')[0] in dicFucntion_2.keys() :
            dicFucntion_2[ query.data.split('-')[0] ]()

    def deleteMessage(self, chat_id):

        logging.warning('>> deleteMessage FROM %s' , chat_id)

        for message_id in Users[chat_id]['del_message_first']:

            try:
                bot.delete_message(chat_id, message_id)

            except:

                logging.warning('message %s form <%s> not found' , message_id , chat_id)
        
        Users[chat_id]['del_message_first'] , Users[chat_id]['del_message_second'] = Users[chat_id]['del_message_second'] , []

    def error(self, update, context):
        
        logging.warning('!! Error <%s> ' , context.error  )
      

######   code

if __name__ == '__main__':

    freeze_support()
    obj = TelegramBot('1256009620:AAHP1EJkgyoBxkcALsRax5s8MuTJrDJcuIE')
    obj.main()

    # obj = autoTrade('FBDE522C391A423E80A55123DE06276D' , '5FACF60F45B2480DB3D25CD5215809AD22F2800EE926F56D')
    # obj.init_market( '1hour' , 'BTCUSDT' )
    # 1256009620:AAHP1EJkgyoBxkcALsRax5s8MuTJrDJcuIE




