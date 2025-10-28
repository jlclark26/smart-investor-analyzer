"""
Course Number: ENGR 13300
Semester: e.g. Fall 2024

Description:
    This code calculates RSI and metrics.

Assignment Information:
    Assignment:     Python Final Project
    Team ID:        011 - 04 (e.g. LC1 - 01; for section LC1, team 01)
    Author:         Jack Clark, clar1037@purdue.edu
    Date:           12/05/2024

Contributors:
    Name, login@purdue [repeat for each]

    My contributor(s) helped me:
    [ ] understand the assignment expectations without
        telling me how they will approach it.
    [ ] understand different ways to think about a solution
        without helping me plan my solution.
    [ ] think through the meaning of a specific error or
        bug present in my code without looking at my code.
    Note that if you helped somebody else with their code, you
    have to list that person as a contributor here as well.

Academic Integrity Statement:
    I have not used source code obtained from any unauthorized
    source, either modified or unmodified; nor have I provided
    another student access to my code.  The project I am
    submitting is my own original work.
"""

import numpy as np
import pandas as pd

def calculate_rsi(prices, period=14):
    prices = list(prices)
    if len(prices) <= period:
        return [np.nan] * len(prices)

    delta = np.diff(prices)
    gain = np.maximum(delta, 0)
    loss = np.maximum(-delta, 0)

    avg_gain = np.zeros(len(prices))
    avg_loss = np.zeros(len(prices))

    avg_gain[period] = np.mean(gain[:period])
    avg_loss[period] = np.mean(loss[:period])

    for i in range(period + 1, len(prices)):
        avg_gain[i] = (avg_gain[i-1] * (period - 1) + gain[i-1]) / period
        avg_loss[i] = (avg_loss[i-1] * (period - 1) + loss[i-1]) / period

    rs = np.divide(avg_gain, avg_loss, out=np.zeros_like(avg_gain), where=avg_loss != 0)
    rsi = 100 - (100 / (1 + rs))
    return list(rsi)

def calculate_metrics(data):
    if data.empty or len(data['Close']) < 2:
        return 0, 0, 0
    total_return = (data['Close'].iloc[-1] / data['Close'].iloc[0]) - 1
    volatility = data['Close'].pct_change().std() * np.sqrt(252)
    sharpe_ratio = total_return / volatility if volatility != 0 else 0
    return total_return, volatility, sharpe_ratio