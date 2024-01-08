from flask import Flask, render_template, request
from datetime import date, timedelta
import pandas as pd
import matplotlib.pyplot as plt
import statistics
import math

# from pandas_datareader import data as pdr

import yfinance as yf
yf.pdr_override()

nifty50_symbols_list = [{'ADANIENT':'Adani Enterprises Ltd.'}, {'ADANIPORTS':'Adani Ports and Special Economic Zone Ltd.'},
           {'APOLLOHOSP':'Apollo Hospitals Enterprise Ltd.'},{'ASIANPAINT':'Asian Paints Ltd.'},{'AXISBANK':'Axis Bank Ltd.'},
           {'BAJAJ-AUTO':'Bajaj Auto Ltd.'},{'BAJFINANCE':'Bajaj Finance Ltd.'},{'BAJAJFINSV':'Bajaj Finserv Ltd.'},{'BPCL':'Bharat Petroleum Corporation Ltd.'},
           {'BHARTIARTL':'Bharti Airtel Ltd.'},{'BRITANNIA':'Britannia Industries Ltd.'},{'CIPLA':'Cipla Ltd.'},{'COALINDIA':'Coal India Ltd.'},
           {'DIVISLAB':'Divi s Laboratories Ltd.'},{'DRREDDY':'Dr. Reddy s Laboratories Ltd.'},{'EICHERMOT':'Eicher Motors Ltd.'},
           {'GRASIM':'Grasim Industries Ltd.'},{'HCLTECH':'HCL Technologies Ltd.'},{'HDFCBANK':'HDFC Bank Ltd.'},
           {'HDFCLIFE':'HDFC Life Insurance Company Ltd.'},{'HEROMOTOCO':'Hero MotoCorp Ltd.'},{'HINDALCO':'Hindalco Industries Ltd.'},
           {'HINDUNILVR':'Hindustan Unilever Ltd.'},{'ICICIBANK':'ICICI Bank Ltd.'},{'ITC':'ITC Ltd'},{'INDUSINDBK':'IndusInd Bank Ltd.'},
           {'INFY':'Infosys Ltd.'},{'JSWSTEEL':'JSW Steel Ltd.'},{'KOTAKBANK':'Kotak Mahindra Bank Ltd'},
           {'LTIM':'LTIMindtree Ltd.'},{'LT':'Larsen & Toubro Ltd.'},{'M&M':'Mahindra & Mahindra Ltd.'},
           {'MARUTI':'Maruti Suzuki India Ltd.'},{'NTPC':'NTPC Ltd.'},{'NESTLEIND':'Nestle India Ltd.'},
           {'ONGC':'Oil & Natural Gas Corporation Ltd.'},{'POWERGRID':'Power Grid Corporation of India Ltd.'},
           {'RELIANCE':'Reliance Industries Ltd.'},{'SBILIFE':'SBI Life Insurance Company Ltd.'},{'SBIN':'State Bank of India'},
           {'SUNPHARMA':'Sun Pharmaceutical Industries Ltd.'},{'TCS':'Tata Consultancy Services Ltd.'},
           {'TATACONSUM':'Tata Consumer Products Ltd.'},{'TATAMOTORS':'Tata Motors Ltd.'},{'TATASTEEL':'Tata Steel Ltd.'},
           {'TECHM':'Tech Mahindra Ltd.'},{'TITAN':'Titan Company Ltd.'},{'UPL':'UPL Ltd.'},{'ULTRACEMCO':'UltraTech Cement Ltd.'},
           {'WIPRO':'Wipro Ltd.'}]

curday = date.today()
first = curday.replace(day=1)

last_month = first - timedelta(days=1)
first_month = last_month.replace(day=1)

active_stocks = []
for x in nifty50_symbols_list:
  key, value = list(x.items())[0]
  stock_name = key
  stock_Ticker = yf.Ticker(stock_name+".NS")

  last_month_info = stock_Ticker.history(start= first_month, end= last_month)
  ret = ((last_month_info['Close'][-1:].values - last_month_info['Open'][:1].values)/last_month_info['Open'][:1].values)*100
  if ret > 0:
    active_stocks.append(x)

active_stocks_list = []
for x in active_stocks:
  key, value = list(x.items())[0]
  dic = {'symbol':key,'name':value}
  active_stocks_list.append(dic)

class stock:
  def __init__(self, stock_name):
        self.stock_name = stock_name
        self.stock_Ticker = yf.Ticker(self.stock_name+".NS")

  def CurPrice(self,curDate):
      curday_info = self.stock_Ticker.history(period="1d")
      return(curday_info['Close'].values)

  def NDayRet(self,N,curDate):
        self.no_days = int(N)
        # self.curday = curDate
        df_Nday_return = pd.DataFrame(columns=['Date', 'Return'], index = range(self.no_days))
        # nxtday = self.curday + timedelta(days=1)
        # fromday = self.curday - timedelta(days= self.no_days + 1)
        self.Nday_info = self.stock_Ticker.history(period=N+"d")
        for i in range(len(self.Nday_info)):
          df_Nday_return['Date'][i] = self.Nday_info.index[i].date()
          df_Nday_return['Return'][i] = ((self.Nday_info['Close'][i]-self.Nday_info['Open'][i])/self.Nday_info['Open'][i])*100
        return(df_Nday_return)

  def Last30daysPrice(self, curDate):
        df_30day_return = pd.DataFrame(columns=['Date', 'Return'], index = range(30))
        self.Nday_info = self.stock_Ticker.history(period="30d")
        for i in range(len(self.Nday_info)):
          df_30day_return['Date'][i] = self.Nday_info.index[i].date()
          df_30day_return['Return'][i] = ((self.Nday_info['Close'][i]-self.Nday_info['Open'][i])/self.Nday_info['Open'][i])*100
        return(df_30day_return)


app = Flask(__name__)
@app.route('/')
def home():
    df_today_return = pd.DataFrame(columns = ['Stock','Stock Name','Return(%)'], index = range(len(nifty50_symbols_list)))
    for i in range(len(active_stocks)):
      for key, value in active_stocks[i].items():
        stock_name = key
        stock_Ticker = yf.Ticker(stock_name+".NS")

        curday_info = stock_Ticker.history(period="1d")
        df_today_return['Stock'][i] = key
        df_today_return['Stock Name'][i] = value
        stock_return = ((float(curday_info['Open']) - float(curday_info['Close']))/float(curday_info['Close']))*100
        df_today_return['Return(%)'][i] = stock_return

        top_stock = df_today_return.sort_values(by = ['Return(%)'], ascending = False)[:10].reset_index(drop=True)
    return render_template('home.html',active_stocks_list = active_stocks_list,
                           top_stock = [top_stock.to_html(classes= 'data')])

@app.route('/portfolio/', methods = ['POST', 'GET'])
def data():
    if request.method == 'GET':
        return f"The URL /data is accessed directly. Try going to '/form' to submit form"
    if request.method == 'POST':
        form_data = request.form
        # print(form_data)
        print(form_data['stock'])
        stock_obj = stock(form_data['stock'])
        print(stock_obj.CurPrice(curday))
        start_date = form_data['start_date']
        end_date = curday

        stock_name = form_data['stock']
        stock_Ticker = yf.Ticker(stock_name+".NS")
        Nday_info = stock_Ticker.history(start= start_date, end= end_date)

        nifty50_Ticker = yf.Ticker("^NSEI")
        nifty50_info = nifty50_Ticker.history(start= start_date, end= end_date)

        Nday_info['Close'].plot()
        nifty50_info['Close'].plot()
        plt.legend((form_data['stock'], 'Nifty50'), loc="upper left")
        plt.savefig('static/stock.png')

        # Performance
        df_performance = pd.DataFrame(columns = ["CAGR(%)","Volatility(%)","Sharpe Ratio","Start Date","End Date"], index= [form_data['stock'],'Nifty50'])
        # Performance of Stock
        v_final = Nday_info['Close'][-1:]
        v_begin = Nday_info['Open'][:1]
        t = (((Nday_info.index[-1] - Nday_info.index[1])/365).days)
        daily_return = []
        for i in range(len(Nday_info)):
          dl_return = (Nday_info['Close'][i] - Nday_info['Open'][i])/Nday_info['Open'][i]
          daily_return.append(dl_return)

        sd_daily_return = statistics.stdev(daily_return)
        mean_daily_return = statistics.mean(daily_return)

        CAGR = (((v_final.values/v_begin.values)**(1/t))-1)*100
        Volatility = (math.sqrt(252) * sd_daily_return)*100
        Sharpe_Ratio = math.sqrt(252) * (mean_daily_return/sd_daily_return)

        df_performance[df_performance.index == form_data['stock']] = [float(CAGR), Volatility, Sharpe_Ratio, start_date, end_date ]

        # Performance of Nifty50
        v_final = nifty50_info['Close'][-1:]
        v_begin = nifty50_info['Open'][:1]
        t = (((nifty50_info.index[-1] - nifty50_info.index[1])/365).days)
        daily_return = []
        for i in range(len(nifty50_info)):
          dl_return = (nifty50_info['Close'][i] - nifty50_info['Open'][i])/nifty50_info['Open'][i]
          daily_return.append(dl_return)

        sd_daily_return = statistics.stdev(daily_return)
        mean_daily_return = statistics.mean(daily_return)

        CAGR = (((v_final.values/v_begin.values)**(1/t))-1)*100
        Volatility = (math.sqrt(252) * sd_daily_return)*100
        Sharpe_Ratio = math.sqrt(252) * (mean_daily_return/sd_daily_return)

        df_performance[df_performance.index == 'Nifty50'] = [float(CAGR), Volatility, Sharpe_Ratio, start_date, end_date ]

        Nday_Return = stock_obj.NDayRet(form_data['Ndays'], curday)
        days30_Return = stock_obj.Last30daysPrice(curday)
        stock_info = [{'Cur_date':curday,'Cday_Price': stock_obj.CurPrice(curday)}]
        return render_template('portfolio.html',form_data = form_data, stock_info = stock_info,
                               Nday_Return=[Nday_Return.to_html(classes='data')],
                               days30_Return = [days30_Return.to_html(classes='data')],
                               performance_Summary = [df_performance.to_html(classes= 'data')])
if __name__ == "__main__":
    app.run(debug= True)
