# Stock Day-Trading using AI techniques

Final project for the Building AI course

## Summary

In this project, we will build a program to see how good AI can do in stock day-trading. Day-trading means all the buying and selling of the stocks are done during the day and we do not hold the stock overnight. We will simulate buying and selling a group of selected stocks over a period of time, with and without using AI, to find out the differences of applying AI techniques.

## Background

Stock prices fluctuates almost every seconds during the market hours. By longing a bullish stock or shorting a bearish stock and liquitate it before the market close we can make a profit. The motivation of this project is to find out:
1. If AI can increase the probability of making a profit
2. If AI can increase the overall earning
3. Can AI reduce the risk

## How is it used?

First of all, we select a number of stocks in each trading day which are suitable for day-trading. The selection criteria are base on a number of factors such as the stocks' price, shares outstanding, volatility etc. We will not cover the method of selection here as it is not the intention of this project. The selected stocks and their intraday data are provided in the df_intraday.csv file. For demostration we only work on the selected stocks in July 2021.
![df_intraday](https://user-images.githubusercontent.com/125923909/222553707-59eb7d9a-0a3b-4243-bcaf-904587067bd1.jpg)

Every trading day, we will enter into a trade by buying one share of the stock when it meets all of the following criteria:
1. Market time is between 9:40am to 11:30am
2. When the stock price is below the Volume Weighted Average Price (VWAP)
3. The 'low' price in the candlestick chart was previously making new lows but has just made a higher 'low' price in the most current time slot.
4. The current price is within a certain range between the VWAP and the previous 'low' price

After we entered into a trade we will exit our trade when it reached one of the following:
1. the VWAP (we won and made a profit)
2. the previous 'low' price (we lose and made a loss)
3. when it is the market closing time (we exit at whatever the close price is)
![sim_trade](https://user-images.githubusercontent.com/125923909/222557417-8c3586b9-2893-4c9b-8836-66f0058fa5da.jpg)

Right after we entered a trade, we will take a few observations:
1. Is the last candlestick and volume rising/falling?
2. Is the last 'close' price rising/falling?
3. Is the last 'high' price rising/falling?
4. is the previous 'low' price the lowest price of the day after market opens?
5. Which price range are the technical indicators (Simple moving averages 50 and 200) in? Price ranges can be: Above VWAP, between VWAP and current price, between current price and previous 'low' price, and below previous 'low' price.

By counting the number of occurences for each of the observations in every wins and loses situation, we can come up with the likelihood ratios and use it to calculate the probability of winning, using Naive-Bayes algorithm.

Let's try the algorithm by spliting the train and test datas with a rolling window in the follow way as an example:

|Train data                          |Test data                           |
|------------------------------------|------------------------------------|
|2021-07-01 to 2021-7-16             |2021-7-17 to 2021-7-21              |
|2021-07-06 to 2021-7-21             |2021-7-22 to 2021-7-26              |
|2021-07-11 to 2021-7-26             |2021-7-27 to 2021-7-31              |

For every 15 days of training we will test it for the next 5 days, repeat 3 times. This way we can have some sort of cross-validation to check for consistency. In practice, We can split the data in any way we wanted as long as it is within the stock data provided.

The results are as follow:
![test_0701_0721](https://user-images.githubusercontent.com/125923909/222568976-8d5baed8-2c9f-48f8-999c-8a8e8deee6d3.jpg)

![test_0706_0726](https://user-images.githubusercontent.com/125923909/222569000-66eef1c1-0796-485b-a3bd-fb48456aa2ca.jpg)

![test_0711_0731](https://user-images.githubusercontent.com/125923909/222569019-6d0fb891-e806-4b91-a55f-71aa97c45fa7.jpg)

If we focus on the results of the test data, it shows that the Positive prediction accuracy (that is, when the algorithm predicts it is going to win and it actually wins) is only around 33~50%. The number is not very high, but is higher comparing to the prior winning probability (that is, we enter in a trade whenever the criteria are met, without going through AI). Also, if we look at the risks (that is the maximum loss throughout the trading period), they are lower when using AI. However, the profits made at the end are also lowered when using AI.

## Data sources and AI methods

The above method is inspired by the Naive-Bayes Classifier in the Building AI online course:
https://www.elementsofai.com/

Validation method is inspired by the rolling window forecast model:
https://machinelearningmastery.com/simple-time-series-forecasting-models/

Stocks intraday data are downloaded from:
https://polygon.io/

## Challenges

Although the above model shows an overall accuracy of around 65-80% (the accuracy for both positive and negative predictions), but we are more interested in the Positive prediction accuracy (the accuracy for positive predictions only), which is around 33-50%, which has much room to improve.
Also, although the risks are low when using AI, the profits are also lowered. This is due to model accuracy as well as the number of trades is much reduced compared to trading without AI.
The above example only applied stock data for one single month, to check for more consistency we need data over a longer period of time (maybe several years?)

## What next?

We can try to improve our model with the following:
1. Input more stocks data with longer timeframe (maybe a few years?) to check for consistency of the model
2. Search for an optimum size of the training/testing data to improve the accuracy
3. Use more observations (such as yesterday high/low/close prices, company financial data, etc) as inputs, or try different combination of observations
4. We can also short a stock by using a similar Naive-Bayes algorithm


## Acknowledgments

https://www.elementsofai.com/

https://machinelearningmastery.com/simple-time-series-forecasting-models/

https://polygon.io/
