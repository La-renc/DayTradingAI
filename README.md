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

First of all, we select a number of stocks in each trading day which are suitable for day-trading. The selection criteria are base on a number of factors such as the stocks' price, shares outstanding, volatility etc. We will not cover the method of selection here as it is not the intention of this project. The selected stocks are provided in this repository.

Every trading day, we will enter into a trade by buying one share of the stock with the following criteria:
1. Market time is between 9:40am to 12:30pm
2. When the stock price is below the Volume Weighted Average Price (VWAP)
3. The 'low' price in the candlestick chart was previously making new lows but has just made a higher 'low' price in the most current time slot.
4. The current price is within a certain range between the VWAP and the previous 'low' price

After we entered into a trade we will exit our trade either when it reached the VWAP (we won and made a profit), the previous 'low' price (we lose and made a loss), or when it is the market closing time (we exit at whatever the close price is).
Right after we entered a trade, we will take a few observations:
1. Is the last candlestick and volume rising/falling?
2. Is the last 'close' price rising/falling?
3. Is the last 'high' price rising/falling?
4. is the previous 'low' price the lowest price of the day after market opens?
5. Which price range are the technical indicators (Moving averages, pre-market high/low price) in? Price ranges can be: Above VWAP, between VWAP and current price, between current price and previous 'low' price, and below previous 'low' price.

By counting the number occurences for each of the observations in every wins and loses, we can come up with the likelihood ratios and use it to calculate the probability of winning with the combination of the occured observations, using Naive-Bayes algorithm.







## Data sources and AI methods
Where does your data come from? Do you collect it yourself or do you use data collected by someone else?
If you need to use links, here's an example:
[Twitter API](https://developer.twitter.com/en/docs)

| Syntax      | Description |
| ----------- | ----------- |
| Header      | Title       |
| Paragraph   | Text        |

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
