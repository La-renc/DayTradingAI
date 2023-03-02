# Stock Day-Trading using AI techniques

Final project for the Building AI course

## Summary

In this project, we will build a program to see how good AI can do in stock day-trading. Day-trading means all the buying and selling of the stocks are done during the day and we do not hold the stock overnight. We will simulate buying and selling a group of selected stocks over a period of time, with and without using AI, to find out the differences of applying AI techniques.

## Background

The motivation of this project is to find out:
1. If AI can increase the probability of winning
2. If AI can increase the overall earning
3. Can AI reduce the risk

## How is it used?

First of all, we select a number of stocks in each trading day which are suitable for day-trading. The selection criteria are base on a number of factors such as the stocks' price, shares outstanding, volatility etc. We will not cover the method of selection here as it is not the intention of this project. The selected stocks and their intraday data are provided in the df_intraday.csv file. For demostration we only work on the selected stocks in July 2021.

Every trading day, we will enter into a trade by buying one share of the stock with the following criteria:
1. Market time is between 9:40am to 11:30am
2. When the stock price is below the Volume Weighted Average Price (VWAP)
3. The 'low' price in the candlestick chart was previously making new lows but has just made a higher 'low' price in the most current time slot.
4. The current price is within a certain range between the VWAP and the previous 'low' price

We will use the check_space and check_buy functions to carry out the above:
'''
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
'''



After we entered into a trade we will exit our trade either when it reached the VWAP (we won and made a profit), the previous 'low' price (we lose and made a loss), or when it is the market closing time (we exit at whatever the close price is).

Right after we entered a trade, we will take a few observations:
1. Is the last candlestick and volume rising/falling?
2. Is the last 'close' price rising/falling?
3. Is the last 'high' price rising/falling?
4. is the previous 'low' price the lowest price of the day after market opens?
5. Which price range are the technical indicators (Simple moving averages 50 and 200) in? Price ranges can be: Above VWAP, between VWAP and current price, between current price and previous 'low' price, and below previous 'low' price.

By counting the number occurences for each of the observations in every wins and loses, we can come up with the likelihood ratios and use it to calculate the probability of winning with the combination of the occured observations, using Naive-Bayes algorithm.







## Data sources and AI methods
https://polygon.io/

## Challenges

What does your project _not_ solve? Which limitations and ethical considerations should be taken into account when deploying a solution like this?

## What next?

How could your project grow and become something even more? What kind of skills, what kind of assistance would you  need to move on? 


## Acknowledgments

* list here the sources of inspiration 
* do not use code, images, data etc. from others without permission
* when you have permission to use other people's materials, always mention the original creator and the open source / Creative Commons licence they've used
  <br>For example: [Sleeping Cat on Her Back by Umberto Salvagnin](https://commons.wikimedia.org/wiki/File:Sleeping_cat_on_her_back.jpg#filelinks) / [CC BY 2.0](https://creativecommons.org/licenses/by/2.0)
* etc
