import pandas as pd
import numpy as np
import datetime as dt
from datetime import timedelta
import math

def check_space(space=pd.DataFrame):
    return (space['low'][-3]>=space['low'][-2] and
            space['low'][-2]<space['low'][-1] and
            all(space['close'][-2:]<space['VWAP'][-2:]) and
            space['high'][-1]<space['VWAP'][-1])

def check_buy(df_i5m=pd.DataFrame, idx_buy=list, tp=float, sl=float):
    global rr_upr, rr_lwr
    price_now = df_i5m['open'][idx_buy]
    price_upr = sl+(tp-sl)/(rr_lwr+1)
    price_lwr = sl+(tp-sl)/(rr_upr+1)
    if price_now >= tp:
        return False, None, None, None, None, None, None
    elif price_now > price_upr:
        if df_i5m['low'][idx_buy]<=price_lwr:
            return True, idx_buy, price_lwr, tp, sl, price_upr, price_lwr
        else: return False, None, None, None, None, None, None
    elif price_now >= price_lwr:
        return True, idx_buy, price_now, tp, sl, price_upr, price_lwr
    elif price_now > sl:
        if df_i5m['high'][idx_buy]>=price_upr:
            return True, idx_buy, price_upr, tp, sl, price_upr, price_lwr
        else: return False, None, None, None, None, None, None
    else:
        return False, None, None, None, None, None, None

def check_sell(df_i5m=pd.DataFrame, idx_buy=dt.datetime, tp=float, sl=float):
    global rr_upr, rr_lwr
    for j, idx_sell in enumerate(df_i5m.loc[idx_buy:idx_buy.replace(hour=15,minute=55)].index):
        if df_i5m['low'][idx_sell]<=sl:
            return idx_sell, sl
        elif df_i5m['high'][idx_sell]>=tp:
            return idx_sell, tp
        else:
            tp = df_i5m['VWAP'][idx_sell]
    return idx_sell, df_i5m['close'][idx_sell]

def create_indicator_input(ind=float, plvs=list):
    inp = [False for _ in range(len(plvs)+1)]
    for p, plv in enumerate(plvs):
        if ind>=plv:
            inp_true_loc = p
            break
    else: inp_true_loc = len(plvs)
    inp[inp_true_loc] = True
    return inp

#----Load stocks intraday data into a dataframe-----------------------------
print('Loading stocks data...')
df_intraday = pd.read_csv(r"df_intraday.csv", parse_dates=['datetime'], index_col=0)
df_intraday.loc[:, 'date'] = [dt.datetime.strptime(d, "%Y-%m-%d").date() for d in df_intraday['date']] #--Converting the strings in 'date' columns into datetime object

#----Create a dictionary of stocks so that we can iterate them-----------------
list_dates = list(set(df_intraday['date']))
list_dates.sort()
dict_stocks = {d:[] for d in list_dates}
for d in dict_stocks:
    list_stocks = list(set(df_intraday['tic'][df_intraday['date']==d]))
    list_stocks.sort()
    dict_stocks[d].extend(list_stocks)
    
#----Initialize the constants we use in the simulation-------------------------
len_space = 3 #--The minimium number of candlesticks needed to observe for entering a trade
rr_upr, rr_lwr = 4, 2 #--The upper and lower range the current price has to be in order to enter into a trade
min_prob = 0.55 #--the minimium posterior probability
data_type = ['train','test']

df_space = pd.DataFrame() #--This dataframe stores all the trading data
df_inp = pd.DataFrame() #--This dataframe stores all the observations and their occured events
#----Iterate every tickers in every market date--------------------------------
print('Simulating trades...')
for dt_to in dict_stocks:
    for tic in dict_stocks[dt_to]:
        dt0 = dt.datetime.combine(dt_to,dt.time(9,31)) #--market open time
        dt1 = dt.datetime.combine(dt_to,dt.time(9,40)) #--trade begin time
        dt2 = dt.datetime.combine(dt_to,dt.time(11,30)) #--trade end time
        dt3 = dt.datetime.combine(dt_to,dt.time(16,0)) #--market close time
        df_i5m = df_intraday.loc[df_intraday['date']==dt_to].loc[df_intraday['tic']==tic] #--Load the intraday 5 minute data of a particlar stock in dataframe
        df_i5m.set_index('datetime', inplace=True)

        #----Iterate though dt1 to dt2 and check if trade criteria is met------
        for i, idx in enumerate(df_i5m.loc[dt1:dt2].index):
            space = df_i5m.loc[:idx][-len_space:] #--We take the minimium number of the most current candlesticks and save it into the 'space' dataframe
            if len(space)==len_space:
                if check_space(space): #--Check if the candlesticks meet the trade criteria
                    idx_buy = df_i5m[idx:].index[1]
                    
                    #----Initialize the variables we use in the trade simulation
                    is_buy, price_buy, tp, sl, price_upr, price_lwr = False, None, None, None, None, None
                    tp = space['VWAP'][-1] #--Take profit price, which is VWAP
                    sl = min(space['low']) #--Stop loss price, which is the lowest price in 'space' dataframe
                    #----Check if the current stock price is within range, and returns is_buy=True if it is good
                    is_buy, idx_buy, price_buy, tp, sl, price_upr, price_lwr = check_buy(df_i5m, idx_buy, tp, sl)
                    if is_buy:
                        idx_sell, price_sell = None, None
                        idx_sell, price_sell = check_sell(df_i5m, idx_buy, tp, sl)#--Returns the sell time and sell price of the trade
                        
                        #----Save the trade data into dataframe 'df_space'-----
                        df0 = pd.DataFrame([[dt_to, tic, space.index, idx_buy, price_buy, idx_sell, price_sell]],
                                            columns=['dt_to','tic','space_index','idx_buy','price_buy','idx_sell','price_sell'])
                        df_space = pd.concat([ df_space,df0 ], axis=0, ignore_index=True)
                        print(f'Date:{dt_to}, Ticker:{tic}, Buy time:{idx_buy.time()}, Sell time:{idx_sell.time()}, Buy price:{price_buy:.2f}, Sell price:{price_sell:.2f}')
                        
                        #----These are the observations we make at the time we enter a trade,
                        #----we will count the occurence of their outcomes and calculate the
                        #----likelihood ratios.
                        #--inp00: combination of last candlestick and volume rise/fall
                        inp00 = [False for _ in range(4)]
                        inp00_true_loc = 2*(1 if space['close'][-1]>space['open'][-1] else 0)+1*(1 if space['volume'][-1]>space['volume'][-2] else 0)
                        inp00[inp00_true_loc] = True
                        #--inp01: last 'close' price rise/fall
                        inp01 = [False,True] if space['close'][-1]>space['close'][-2] else [True,False]
                        #--inp02: last 'high' price rise/fall
                        inp02 = [False,True] if space['high'][-1]>space['high'][-2] else [True,False]
                        #--inp03: is the previous 'low' price the lowest price of the day after market opens
                        inp03 = [False,True] if min(df_i5m['low'].loc[dt0:idx])==min(space['low']) else [True,False]
                        #--inp04, inp05: Which price range are the SMA50 and SMA200 in
                        plvs = [tp, price_upr, price_buy, price_lwr, sl]
                        inp04 = create_indicator_input(ind=df_i5m['SMA50'][idx], plvs=plvs)
                        inp05 = create_indicator_input(ind=df_i5m['SMA200'][idx], plvs=plvs)
                        #----Save the trade data into dataframe 'df_space'-----
                        inps = [inp00,inp01,inp02,inp03,inp04,inp05]
                        cols=[]
                        for j in range(len(inps)):
                            for k in range(len(inps[j])):
                                cols.append('inp'+str(j).zfill(2)+'_'+str(k))
                        df_inp = pd.concat([ df_inp,pd.DataFrame([[is_true for inp in inps for is_true in inp]], columns=cols)], axis=0, ignore_index=True)
                    else: pass
                else: pass
            else: pass
            
#----Calculate the profit/loss of each trade and save in 'df_space'------------
df_space['bal'] = df_space['price_sell']-df_space['price_buy']
df_space['win'] = df_space['bal']>0

#----Finished iterating every tickers on a market date-------------------------

#----Split train data and test data by date------------------------------------
print('Choose training begin dates (between 2021-7-1 and 2021-7-30):')
y, m, d = [int(x) for x in input("Enter training begin date (YYYY-MM-DD):").split("-")]
train_date_from = dt.date(y, m, d)
print(f'Choose testing begin dates (between {train_date_from+timedelta(days=1)} and 2021-7-31):')
y, m, d = [int(x) for x in input("Enter testing begin date (YYYY-MM-DD):").split("-")]
test_date_from = dt.date(y, m, d)
train_date_to = test_date_from-timedelta(days=1)
print(f'Choose testing end dates (between {test_date_from} and 2021-7-31):')
y, m, d = [int(x) for x in input("Enter testing end date (YYYY-MM-DD):").split("-")]
test_date_to = dt.date(y, m, d)

df_space_train = df_space.loc[df_space['dt_to']>=train_date_from].loc[df_space['dt_to']<=train_date_to].copy()
df_inp_train = df_inp.loc[df_space_train.index].copy()
df_space_train.reset_index(drop=True, inplace=True)
df_inp_train.reset_index(drop=True, inplace=True)

df_space_test = df_space.loc[df_space['dt_to']>=test_date_from].loc[df_space['dt_to']<=test_date_to].copy()
df_inp_test = df_inp.loc[df_space_test.index].copy()
df_space_test.reset_index(drop=True, inplace=True)
df_inp_test.reset_index(drop=True, inplace=True)

#----Calculate the likelihood ratios from train data, which will be used for prediction in test data
pr_win = [sum(globals()['df_inp_train'][col][globals()['df_space_train']['win']==True])/len(globals()['df_inp_train'][col][globals()['df_space_train']['win']==True]) for col in cols]
pr_not_win = [sum(globals()['df_inp_train'][col][globals()['df_space_train']['win']==False])/len(globals()['df_inp_train'][col][globals()['df_space_train']['win']==False]) for col in cols]
pr_win = [0.00000001 if p==0 else p for p in pr_win]
pr_not_win = [0.00000001 if p==0 else p for p in pr_not_win]
likelihood_ratios = [i/j for i,j in zip(pr_win,pr_not_win)]
prior_odds = globals()['df_space_train']['win'].tolist().count(True) / globals()['df_space_train']['win'].tolist().count(False)

#----Save likelihood ratios data in 'df_result'--------------------------------
df_result = pd.DataFrame([[prior_odds,likelihood_ratios,pr_win,pr_not_win]],
                          columns=['prior_odds','likelihood_ratios','pr_win','pr_not_win'],
                          index=[train_date_from.strftime("%Y%m%d")+'to'+train_date_to.strftime("%Y%m%d")]
                          )

#----Using the results to calculate the posterior odds on both train and test data
for d in data_type:
    inpx_cols=[]
    for j in range(len(inps)):
        inpx_cols.append(['inp'+str(j).zfill(2)+'_'+str(k) for k in range(len(inps[j]))])
    #----Find the event that happened in every observations--------------------
    dict_pr={}
    for idx in globals()['df_space_'+d].index:
        true_events_likelihood_ratios=[]
        inpx_true_locs=[]
        inpx_start_loc=0
        for inpx in inpx_cols:
            inpx_true_locs.append(globals()['df_inp_'+d][inpx].loc[idx].argmax()+inpx_start_loc)
            inpx_start_loc += len(inpx)
        #----Get the likelihood ratios for every observations according to the event that happened
        true_events_likelihood_ratios = [likelihood_ratios[inpx_true_loc] for inpx_true_loc in inpx_true_locs]
        #----Calculate posterior odds and probability, and save them in dictionary 'dict_pr'
        posterior_odds = prior_odds*math.prod(true_events_likelihood_ratios)
        prob_win = posterior_odds/(1+posterior_odds)
        dict_pr.update({idx:{'inpx_true_locs':inpx_true_locs, 'likelihood_ratios':true_events_likelihood_ratios, 'posterior_odds':posterior_odds, 'prob_win':prob_win}})
    
    #----Make predictions, calculate accuracy, profits etc, and save them in dataframe df_pr
    df_pr = pd.DataFrame([dict_pr[i]['prob_win'] for i in range(len(dict_pr))], columns=['prob_win'])
    df_pr['pred'] = df_pr['prob_win']>min_prob
    df_pr['true'] = globals()['df_space_'+d]['win']
    df_pr['acc']  = df_pr['true']==df_pr['pred']
    df_pr['bal'] = globals()['df_space_'+d]['bal']

    n_wins = sum(df_pr['true'])
    n_trades = len(df_pr)
    prior_prob = sum(df_pr['true'])/len(df_pr) if len(df_pr)!=0 else np.nan
    
    #----Since we will only enter a trade when the price is bullish, we will also
    #----calculate the accuracy for positive predictions
    mk = df_pr['pred']==True
    acc = sum(df_pr['acc'])/len(df_pr['acc']) if len(df_pr['acc'])!=0 else np.nan
    n_acc_wins = sum(df_pr['acc'][mk])
    n_pred_wins = len(df_pr['acc'][mk])
    acc_pred_true = n_acc_wins/n_pred_wins if n_pred_wins!=0 else np.nan
    profit_ai = df_pr['bal'][mk].sum()
    risk_ai = min(df_pr['bal'][mk].cumsum()) if n_pred_wins!=0 else 0
    profit_not_ai = df_pr['bal'].sum()
    risk_not_ai = min(df_pr['bal'].cumsum()) if n_trades!=0 else 0

    print('')
    if d=='train': print(f'----Training from {train_date_from} to {train_date_to}-----')
    elif d=='test': print(f'-----Testing from {test_date_from} to {test_date_to}-----')
    print(f'Overall accuracy = {acc*100:.2f}%')
    print(f'No. of Predicted wins with AI = {n_pred_wins:>4} , No. of True wins with AI = {n_acc_wins:>4} , Positive prediction accuracy = {acc_pred_true*100:.2f}%')
    print(f'No. of trades without AI      = {n_trades:>4} , No. of wins without AI   = {n_wins:>4} , Prior winning probability    = {prior_prob*100:.2f}%')
    print(f'Profit with AI    = {profit_ai:>6,.2f}, Risk with AI    = {risk_ai:>6,.2f}')
    print(f'Profit without AI = {profit_not_ai:>6,.2f}, Risk without AI = {risk_not_ai:>6,.2f}')
    
    #----Save results to df_result---------------------------------------------
    df1 = pd.DataFrame({d+'_n_wins':[n_wins],
                        d+'_n_trades':[n_trades],
                        d+'_acc':[acc],
                        d+'_acc_pred_true':[acc_pred_true],
                        d+'_n_acc_wins':[n_acc_wins],
                        d+'_n_pred_wins':[n_pred_wins],
                        d+'_profit_ai':[profit_ai],
                        d+'_profit_not_ai':[profit_not_ai],
                        d+'_risk_ai':[risk_ai],
                        d+'_risk_not_ai':[risk_not_ai],
                        }, index=[train_date_from.strftime("%Y%m%d")+'to'+train_date_to.strftime("%Y%m%d")]
                        )
    df_result = pd.concat([ df_result,df1 ], axis=1)

