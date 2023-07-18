from flask import Flask, render_template, request, url_for, flash, redirect
from flask_socketio import SocketIO, emit
from flask_cors import CORS, cross_origin
import pandas as pd
import sqlite3
import statistics
import numpy as np
import random
import multiprocess as mp
import threading
from functools import reduce
import uuid
import time
import warnings 
warnings.filterwarnings('ignore')
from yahoofinancials import YahooFinancials
import datetime
import statistics
import matplotlib.pyplot as plt
import datetime as dt
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
#from tensorflow import keras
import os
import tensorflow as tf 
from tensorflow.keras import optimizers
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import LSTM
from tensorflow.keras.layers import Dropout
from tensorflow.keras.models import load_model
from datetime import date, timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['CORS_HEADERS'] = 'Content-Type'
cors = CORS(app)
numTradeDays = 252
portfolioValue=1000
dbName = os.path.join("/home/sma/deploy/SmartPortfolioAdvisor/System Code/", "frontend/src/database/stocks.db")
#dbName = "stocks.db"
database = None
threads = []
print('number of processors: ', mp.cpu_count())
socketio = SocketIO(app, async_mode=None, cors_allowed_origins='*')
socketio.run(app)


def get_db_connection():
    print('in connection')
    conn = sqlite3.connect('stocks.db')
    conn.row_factory = sqlite3.Row
    return conn

def pullFromDatabase(tickers, startdate, enddate):
    con = sqlite3.connect(dbName)
    cur = con.cursor()
    sqlSelect = "SELECT ticker, date, close, dailyreturn FROM alltickers where ticker in ("
    for ticker in tickers:
        sqlSelect = sqlSelect+"\'" + ticker+"\',"
    sqlSelect = sqlSelect.strip(',')+ ") and date>=\'" + startdate + "\' and date<=\'" + enddate +"\'"
    res = cur.execute(sqlSelect)
    data = res.fetchall()
    cur.close()
    con.close()
    return data

def pullFromTreasury(startdate, enddate):
    con = sqlite3.connect(dbName)
    cur = con.cursor()
    sqlSelect = "SELECT avg(AdjClose) FROM treasury where date>=\'" + startdate + "\' and date<=\'" + enddate +"\'"
    res = cur.execute(sqlSelect)
    data = res.fetchall()
    cur.close()
    con.close()
    return data

def dateToTimestamp(datestr):
    element = datetime.datetime.strptime(datestr,"%Y-%m-%d")
    return datetime.datetime.timestamp(element)
def timestampToDate(timestamp):
    return time.strftime("%Y-%m-%d", time.localtime(int(timestamp)))  

def fetchPortfolio(tickers, startdate, enddate):
    dataSubset = database[database['ticker'].isin(tickers)]
    return dataSubset

#Method uses the daily returns for each ticker
def getAnnualizedWeightedAvgDailyReturn(portfolio, portfolioValues):
    tickers = portfolio.iloc[:, 0];
    tickersAlloc = portfolio.iloc[:,1];
    totalReturn = 0
    for i in range(len(tickers)): #[0.5,0.5]
        ticker = tickers[i]
        proportion = tickersAlloc[i]
        tickerValues = pd.DataFrame(portfolioValues[(portfolioValues.ticker==ticker)])
        meanDailyReturn = statistics.mean(tickerValues['dailyreturn'])
        totalReturn += meanDailyReturn * proportion
    return totalReturn * numTradeDays
        

def getStandardDeviationForTicker(portfolioValues, ticker): 
    tickerValues = portfolioValues[(portfolioValues.ticker==ticker)]
    stddev = statistics.stdev(tickerValues['dailyreturn'])
    return stddev

def getPortfolioStandardDeviation(portfolio, startdate, enddate):
    tickers = portfolio.iloc[:, 0];
    tickersAlloc = portfolio.iloc[:,1];
    portfolioValues = fetchPortfolio(tickers, startdate, enddate)
    
    part_1=0
    for t in range(len(tickers)): #[0.5,0.5]
        proportion = tickersAlloc[t]
        ticker = tickers[t]
        sd = getStandardDeviationForTicker(portfolioValues, ticker)
        pt1_ticker = np.multiply(proportion,sd)**2
        #print ('pt 1 ' , ticker, ' proportion: ', proportion, ' sd: ', sd, ' pt1: ', pt1_ticker)
        part_1 += pt1_ticker
    #print ('pt 1 summation ' , part_1)  
    
    part_2=0 #The covariance matrix
    cov_prep = portfolioValues.pivot(index='date', columns='ticker', values='dailyreturn')
    cov_matrix = pd.DataFrame.cov(cov_prep)
    for i in range(len(tickers)):
        for j in range(len(tickers)):
            if (i==j):
                continue #assume covariance = 0 hence the term 2*w1*w2*cov(ticker1, ticker2) will be 0
            w1=tickersAlloc[i]
            w2=tickersAlloc[j]
            cov=cov_matrix[tickers[i]][tickers[j]]
            part_2 += w1*w2*cov
    portfolioVariance = part_1+part_2
    return (portfolioVariance ** 0.5) * (numTradeDays**0.5)

#Annual Basis
def getRiskFreeRate(startdate, enddate):
    data = pullFromTreasury(startdate, enddate)
    return data[0][0] * 0.01

def getSharpeRatio(totalReturnPercentage, riskFreeRate, stddev):
    return (totalReturnPercentage-riskFreeRate) / stddev


def computeFitnessValue(portfolio, startdate, enddate):
    tickers = portfolio.iloc[:, 0];
    portfolioValues = fetchPortfolio(tickers, startdate, enddate)
    totalRetDailyAnnualized = getAnnualizedWeightedAvgDailyReturn(portfolio, portfolioValues)
    stddevRetDailyAnnualized = getPortfolioStandardDeviation(portfolio, startdate, enddate)
    sharpeRatio = getSharpeRatio(totalRetDailyAnnualized, getRiskFreeRate(startdate, enddate), stddevRetDailyAnnualized)
    return sharpeRatio, stddevRetDailyAnnualized
    
#isSingleRow = boolean denoting if we are only inserting 1 row of data
def insert(table_name, value_tuple, isSingleRow):
    #print(dbName)
    conn = sqlite3.connect(dbName)
    cur = conn.cursor()
    numargs=0
    if (isSingleRow==True):
        numargs = len(value_tuple)
    else:
        numargs = len(value_tuple[0])
    sql_insert = 'insert into ' +  table_name + ' values('
    if (numargs==0):
        return
    for i in range(numargs):
        sql_insert += '?'
        if (i==numargs-1):
            sql_insert+=')'
        else:
            sql_insert+=','
    # The executemany method will insert multiple rows into SQLite table.
    #print(sql_insert)
    #print(value_tuple)
    if (isSingleRow==True):
        cur.execute(sql_insert, value_tuple)
    else:
        cur.executemany(sql_insert, value_tuple)
    conn.commit()
    cur.close()
    conn.close()   
    
def generateRunId():
    return (str(uuid.uuid4()))[0:6]

# Chromosome Definition
def chromosome(n, totalstocks):
    ''' Generates set of random numbers whose sum is equal to 1
        Input: n = number of stocks we want to invest out of totalstocks. totalstocks = universe of investible stocks
        Output: Array of random numbers'''
    n = np.minimum(n,totalstocks)
    ch = np.random.rand(n)
    ch = ch/sum(ch)
    portfolio = [0] * totalstocks
    i = 0
    while (i < n):
        index = np.random.randint(0, totalstocks)
        if (portfolio[index] == 0):
            portfolio[index] = ch[i]
            i = i + 1
    return portfolio
    
# Generate population
def generatePopulation(pop_size, stocktickers, maxStocks):
    totalstocks = len(stocktickers)
    print("totalStocks : ", totalstocks)
    population = np.array([chromosome(maxStocks, totalstocks) for _ in range(pop_size)])
    return population
    
def toPortfolioDataframe(stocktickers, chromosome):
    return pd.DataFrame({'ticker':stocktickers, 'alloc':chromosome})    
        
def selectElitePopulation(stocktickers, population, selectionRate, startdate, enddate, runId, epoch,reqId='',publishToFrontend=False):
    pool = mp.Pool(mp.cpu_count())
    n_chromosomes = len(population)
    population_fitness = [] 
    population_risk = []
    x1 = len(stocktickers)
    #convert all chromosomes to portfolio dataframes
    populationDFs =[]
    for chromosome in population:
        populationDFs.append(toPortfolioDataframe(stocktickers, chromosome))
        
    pool_outputs = []
    for i in range(n_chromosomes):
        pool_outputs.append(pool.apply_async(computeFitnessValue, args=(populationDFs[i], startdate, enddate))) 
    pool.close()
    pool.join()
    
    chrLen = len(population[0])
    for i in range(len(pool_outputs)):
        sharpe = pool_outputs[i].get()[0]
        risk = pool_outputs[i].get()[1]
        population_fitness.append(sharpe)
        population_risk.append(risk)
    population = np.insert(population, chrLen, population_fitness, axis=1)
    population = sorted(population,key = lambda x: x[chrLen],reverse=True)
    writeGAPopulation(enddate, runId, epoch, population, population_risk)
    if (publishToFrontend==True):
    	sendGAEpochToFrontend(enddate, runId, epoch, stocktickers, population,reqId)
    percentage_elite_idx = int(np.floor(len(population)* selectionRate))
    population = np.delete(population, x1, axis=1)
    return population[:percentage_elite_idx]
    
def mutation(parent):
    #print("In Mutation")
    child=parent.copy()
    n=np.random.choice(range(len(parent)),2)
    while (n[0]==n[1] or (child[n[0]]==0.0 and child[[n[1]]==0.0])):
        n=np.random.choice(range(len(parent)),2)
    child[n[0]],child[n[1]]=child[n[1]],child[n[0]]
    return child    
        
def crossover(parent1, parent2, maxStocks=10):
    length = len(parent1)
    crossoverPt = np.random.randint(0, length)
    child = [0] * length
    numStocks = 0
    stockLoc = []
    for i in range(length):
        if (i<crossoverPt):
            child[i] =  parent1[i]
        else: 
            child[i] =  parent2[i]
        if (child[i] > 0.0):
            numStocks+=1;
            stockLoc.append(i)
        
    if (numStocks > maxStocks):
        toDrop = numStocks - maxStocks
        for j in range(toDrop):
            dropInd = stockLoc[np.random.randint(0, len(stockLoc))]
            child[dropInd] = 0.0
    sumOfChild = sum(child)           
    if (sumOfChild > 0.0):
        child = [float(i)/sumOfChild for i in child]      
    return child
    
    
def nextGeneration(pop_size, elite, crossoverRate, mutationRate):
    #print("In nextGeneration")
    new_population=[]
    pool_outputs = []
    pool = mp.Pool(mp.cpu_count())
    # replicate the elite population into the new population
    # mutate and/or crossover as necessary
    i=0
    while len(new_population) < pop_size:
        new_population.append(elite[i])
        i += 1
        if (i>len(elite)-1):
            i=0
    for j in range(1,pop_size):
        pool_outputs.append(pool.apply_async(mutateOrCrossover, args=(j, new_population, crossoverRate, mutationRate))) 
    pool.close()
    pool.join()
    new_population=[new_population[0]]
    for i in range(len(pool_outputs)):
        new_population.append(pool_outputs[i].get())
    return new_population


def mutateOrCrossover(j, new_population, crossoverRate, mutationRate):
    #print("In mutateOrCrossover")
    crossoverRandom = random.random()
    pop_size = len(new_population)
    sample = new_population[j]
    if (crossoverRandom <= crossoverRate):
        parent1 = sample
        p2Index = random.randint(0, pop_size-1)
        parent2 = new_population[p2Index]
        sample = crossover(parent1, parent2)
    mutateRandom = random.random()
    if (mutateRandom <= mutationRate):
        sample = mutation(new_population[j])
    return sample
    
def writeGAHyperparameters(runId, pop_size, stocktickers, maxStocks, maxIterations, selectionRate, crossoverRate, mutationRate, 
          startdate, enddate):
    value_tuple = (enddate, runId, pop_size, startdate, enddate, str(stocktickers), maxStocks, maxIterations, selectionRate, mutationRate, crossoverRate)
    #print(value_tuple)
    insert('gahyperparams', value_tuple, True)

def writeGAResults(date, runId, epoch, stockName,chromosome, sharpe, risk):
    returns = sharpe * risk
    value_tuple = (date, runId, epoch,str(stockName), str(chromosome), sharpe, returns, risk)
    insert('garesults', value_tuple, True)

def writeGAPopulation(date, runId, epoch, population, population_risk):
    formatted_list = []
    populationLen = len(population[0])
    for i in range(len(population)):
        formatted_list.append((date, runId, epoch, i, str(population[i][0:populationLen-1]), 
                               population[i][populationLen-1:][0], population_risk[i]))
    value_tuple = [tuple(item) for item in formatted_list]
    insert('gapopulation', value_tuple, False)

def sendGAHyperparametersToFrontend(runId, pop_size, stocktickers, maxStocks, maxIterations, selectionRate, crossoverRate, mutationRate, 
          startdate, enddate, reqId):
    data = {}
    data['type'] = 'gahyperparameters'
    data['msgid'] = reqId
    data['data'] = {}
    data['data']['date'] = enddate
    data['data']['runid'] = runId
    data['data']['startdate'] = startdate
    data['data']['enddate'] = enddate
    data['data']['popSize'] = pop_size
    data['data']['maxEpochs'] = maxIterations
    data['data']['selectionRate'] = selectionRate
    data['data']['mutationRate'] = mutationRate
    data['data']['crossoverRate'] = crossoverRate
    socketio.emit('my_response', data);
    
   
def sendGAEpochToFrontend(enddate, runId, epoch, stocktickers, population, reqId): 
    populationLen = len(population[0])
    data = {}
    data['type'] = 'gaEpoch'
    data['msgid'] = reqId
    data['runid'] = runId
    data['epoch'] = epoch
    data['stocktickers'] = stocktickers
    data['population'] = []
    for i in range(len(population)):
        memberChromosome = {}
        memberChromosome['popid'] = i
        memberChromosome['chromosome'] = []
        for j in range(populationLen-1):
            memberChromosome['chromosome'].append(population[i][j])
        memberChromosome['sharpe'] = population[i][populationLen-1:][0]
        data['population'].append(memberChromosome)
    socketio.emit('my_response', data);
    
def sendGAResultToFrontend(enddate, runId, stocktickers, allocPerc, sharpeRatio,reqId): 
    data = {}
    data['type'] = 'gaResults'
    data['msgid'] = reqId
    data['runid'] = runId
    data['stocktickers'] = stocktickers
    data['allocPerc'] = allocPerc
    data['sharpe'] = sharpeRatio
    #print(data)
    socketio.emit('my_response', data);


def initialize(stocktickers, startdate, enddate, depth):
    global database
    if (depth==0):
        print(stocktickers)
        database = pd.DataFrame(pullFromDatabase(stocktickers, startdate, enddate))
        database.columns = ['ticker','date', 'price', 'dailyreturn']


def runGA(pop_size, stocktickers, maxStocks, maxIterations, selectionRate, crossoverRate, mutationRate, startdate, enddate, depth, maxDepth=5, runId='', reqId=''):
    initialize(stocktickers, startdate, enddate,depth)
    if (len(runId) == 0):
        runId = generateRunId()
    population = generatePopulation(pop_size, stocktickers, maxStocks)
    elite = selectElitePopulation(stocktickers, population, selectionRate, startdate, enddate, runId, 0, reqId, False)
    iteration=0 
    sharpeRatio = 0
    starttime = time.time()
    prevElite = elite
    distance=1000000
    convergeCount = 0
    writeGAHyperparameters(runId, pop_size, stocktickers, maxStocks, maxIterations, selectionRate, crossoverRate, mutationRate, 
          startdate, enddate)
    sendGAHyperparametersToFrontend(runId, pop_size, stocktickers, maxStocks, maxIterations, selectionRate, crossoverRate, mutationRate, 
          startdate, enddate, reqId)
    while (iteration < maxIterations):
        print('Iteration:',iteration)
        population = nextGeneration(pop_size,elite,crossoverRate,mutationRate)
        elite = selectElitePopulation(stocktickers, population, selectionRate, startdate, enddate, runId, iteration, reqId, True)
        #calculate Euclid dist between portfolios as a measure of similarity to determine
        #if GA has converged
        distance = np.linalg.norm(elite-prevElite)
        print(' distance ... ', distance, ' elite ', elite, ' prevElite ', prevElite)
        prevElite = elite
        topElite = toPortfolioDataframe(stocktickers, elite[0])
        sharpeRatioResult=computeFitnessValue(topElite, startdate, enddate)
        sharpeRatio = sharpeRatioResult[0]
        expectedRisk = sharpeRatioResult[1] 
        print('Current Sharpe Ratio {} Expected Risk {}\n'.format(sharpeRatio, expectedRisk))
        #print('TopElite: ', topElite)
        if (distance < 0.0001):
            convergeCount+=1
        if (convergeCount==3):
            break
        iteration+=1
        

    if (sharpeRatio < 2): #Unsatisfactory local maximum! Rerun the whole GA with a different initial population
        print("UNSATISFACTORY SHARPE .... RERUN GA")
        depth += 1
        if (depth >= maxDepth):
           endtime = time.time()
           print('Portfolio of stocks creation after all the iterations finished.\n')
           print('total time taken: ', endtime-starttime)
           print("Depth : ", depth)
           stocks = topElite[topElite['alloc'] > 0]
           stockName = stocks['ticker'].tolist()
           allocationPerc = stocks['alloc'].tolist()
           allocPerc = stocks['alloc'].values
           print("stockName", stockName)
           print("allocationPerc", allocPerc)
           writeGAResults(enddate, runId, iteration,stockName, allocPerc, sharpeRatio, expectedRisk)
           sendGAResultToFrontend(enddate, runId, stocktickers, allocationPerc, sharpeRatio,reqId)
           threads.remove((reqId, threading.current_thread()))
           print("threads size ", len(threads))
           return stockName,allocationPerc 
        else:
           print("Running for Depth:", depth)
           runGA(pop_size, stocktickers, maxStocks, maxIterations, selectionRate, crossoverRate, mutationRate,startdate, enddate, depth, maxDepth, reqId=reqId)
    else:
        endtime = time.time()
        print('Portfolio of stocks creation after all the iterations finished.\n')
        print('total time taken: ', endtime-starttime)
        print("Depth : ", depth)
        stocks = topElite[topElite['alloc'] > 0]
        stockName = stocks['ticker'].tolist()
        allocationPerc = stocks['alloc'].tolist()
        allocPerc = stocks['alloc'].values
        print("stockName", stockName)
        print("allocationPerc", allocPerc)
        writeGAResults(enddate, runId, iteration, stockName,allocPerc, sharpeRatio, expectedRisk)
        sendGAResultToFrontend(enddate, runId, stocktickers, allocationPerc, sharpeRatio,reqId)
        threads.remove((reqId, threading.current_thread()))
        print("threads size ", len(threads))
        return stockName,allocationPerc
    

def pullFromYahooAPI(tickers, startdate, enddate):
    yf_stocks = YahooFinancials(tickers)
    dailyStockPrice = yf_stocks.get_historical_price_data(startdate, enddate, 'daily')
    ticker_df = pd.DataFrame()
    for i in tickers:
        #print(i)
        ticker = pd.DataFrame(dailyStockPrice[i]['prices']) 
        ticker['ticker'] = i
        dailyreturn = [0]
        for j in range(1,ticker.shape[0]):
            dailyreturn.append((ticker.iloc[j]['close'] - ticker.iloc[j-1]['close'])/ticker.iloc[j-1]['close'])
        ticker['dailyreturn'] = dailyreturn
        ticker = ticker[ticker['dailyreturn'] != 0]
        ticker_df = ticker_df.append(ticker)
        date_list = ticker_df['formatted_date'].values
        ticker_df['date'] = date_list
        col_list = list(ticker_df.columns)
        col_list.remove('formatted_date')
        ticker_df1 = ticker_df[col_list]
        ticker_df1.reset_index(drop=True,inplace=True)
    writeAPIPullData(ticker_df1)


def writeAPIPullData(df):
    col_list = df.columns
    data = []
    for i in range(df.shape[0]):
        data.append(df.iloc[i])
    value_tuple = [tuple(item) for item in data]
    #print(len(value_tuple))
    insertAPIPullData('alltickers',value_tuple,False,col_list)
    
def insertAPIPullData(table_name, value_tuple, isSingleRow,column_list):
    #print(dbName)
    conn = sqlite3.connect(dbName)
    cur = conn.cursor()
    numargs=0
    col_len = len(column_list)
    if (isSingleRow==True):
        numargs = len(value_tuple)
    else:
        numargs = len(value_tuple[0])
    sql_insert = 'insert into ' +  table_name + ' ('
    if (col_len==0):
        return
    for i in range(col_len):
        sql_insert += ''+column_list[i]+''
        if (i==col_len-1):
            sql_insert+=') values('
            if (numargs==0):
                return
            for j in range(numargs):
                sql_insert += '?'
                if (j==numargs-1):
                    sql_insert+=')'
                else:
                    sql_insert+=','
        else:
            sql_insert+=','
    # The executemany method will insert multiple rows into SQLite table.
    #print(sql_insert)
    #print(value_tuple)
    if (isSingleRow==True):
        cur.execute(sql_insert, value_tuple)
    else:
        cur.executemany(sql_insert, value_tuple)
    conn.commit()
    cur.close()
    conn.close()
    print('New Records Inserted')   
    return True




#LSTM
def getHistoricalData(stockticker, start_date, end_date):
    features = ['date', 'open', 'close', 'low', 'high', 'volume', 'adjClose']
    yf = YahooFinancials(stockticker)
    df = pd.DataFrame(yf.get_historical_price_data(start_date, end_date, 'daily')[stockticker]['prices'])
    df.date = df.formatted_date
    df= df.drop('formatted_date', axis=1).set_index("date")
    return df
    
def getVIX(stockticker, start_date, end_date):
    df_VIX = pd.DataFrame(YahooFinancials('^VIX').get_historical_price_data(start_date, end_date, 'daily')['^VIX']['prices'])
    df_VIX = df_VIX[['formatted_date','adjclose']].set_index("formatted_date")
    df_VIX = df_VIX.rename(columns = {'adjclose':'VIX'})
    return df_VIX
    
    
def getUSDX(stockticker, start_date, end_date):   
    df_USDX = pd.DataFrame(YahooFinancials('DX-Y.NYB').get_historical_price_data(start_date, end_date, 'daily')['DX-Y.NYB']['prices'])
    df_USDX = df_USDX[['formatted_date','adjclose']]
    df_USDX = df_USDX.rename(columns = {'adjclose':'USDX'})
    return df_USDX.set_index("formatted_date")
    
    
def getMacroIndicator(df, stockticker, start_date, end_date):  
    # VIX
    VIX = getVIX(stockticker, start_date, end_date)
    df = pd.merge(df, VIX, left_index=True, right_index=True)
    
    # USDX
    USDX = getUSDX(stockticker, start_date, end_date)
    df = pd.merge(df, USDX, left_index=True, right_index=True)
    
    return df
    
    
def getMACD(data, n_fast=12, n_slow=26, n_smooth=9):
    fastEMA = data.adjclose.ewm(span=n_fast, min_periods=n_slow).mean()
    slowEMA = data.adjclose.ewm(span=n_slow, min_periods=n_slow).mean()
    MACD = pd.Series(fastEMA-slowEMA, name = 'MACD')
    return MACD
    
    
def getRSI(data, time_window=14):
    change = data.adjclose.diff()       # diff in one field(one day)
    change.dropna(inplace=True)

    # change_up is equal to the positive difference, otherwise equal to zero
    change_up = change.copy()
    change_up[change_up<0] = 0
    
    # change_down is equal to negative deifference, otherwise equal to zero
    change_down = change.copy()
    change_down[change_down>0] = 0

    # Calculate the rolling average of average up and average down
    avg_up = change_up.rolling(time_window).mean()
    avg_down = change_down.rolling(time_window).mean().abs()

    RS = avg_up/avg_down
    RSI = 100 - 100/(1+RS)
    return RSI
    
    
def getATR(data, time_window=14):
    high_low = data.high - data.low
    high_close = np.abs(data.high - data.close.shift())
    low_close = np.abs(data.low - data.close.shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)
    ATR = true_range.rolling(time_window).sum()/time_window
    return ATR
    
def getTechnicalIndicator(df, stockticker, start_date, end_date):
    df['MACD'] = getMACD(df, 12, 26, 9)
    df['RSI'] = getRSI(df, 14)
    df['ATR'] = getATR(df, 14)
    return df

def getData(stockticker, start_date, end_date):
    df = getHistoricalData(stockticker, start_date, end_date)
    
    df = getMacroIndicator(df, stockticker, start_date, end_date)
    
    df = getTechnicalIndicator(df, stockticker, start_date, end_date)
    
    df = df[["volume", "VIX", "USDX", "MACD", "RSI", "ATR", "adjclose"]][25:]
    
    return df
    
def split_dataset(data, ratio=0.8):
    training_size = int(len(data)*ratio)
    train_data_x = data[:training_size].iloc[:, 0:7]
    train_data_y = data[:training_size].iloc[:, 6:7]
    test_data_x = data[training_size:].iloc[:, 0:7]
    test_data_y = data[training_size:].iloc[:, 6:7]
    return train_data_x, train_data_y, test_data_x, test_data_y
    
def create_dataset(x, y, time_step=40, future_step=10, distance=10):
    dataX, dataY = [], []  
    for i in range(len(x)-time_step-future_step):
        dataX.append(x[i:(i+time_step)])
        dataY.append(y[(i+time_step):(i+time_step+future_step)])
    dataX = np.array(dataX, dtype=float)
    dataY = np.array(dataY,dtype=float)
    
    # reshape to fit lstm
    dataX = dataX.reshape(dataX.shape[0], dataX.shape[1], len(x.columns))
    dataY = dataY.reshape(dataY.shape[0],future_step)
    
    return dataX, dataY
    
def construct_model(input_shape, future_step, optimizer="adam"):
    LSTM_model = Sequential()

    LSTM_model.add(LSTM(units = 64, input_shape = input_shape))
    LSTM_model.add(Dropout(0.2))

    LSTM_model.add(Dense(units = future_step))

    adam = tf.optimizers.Adam(learning_rate=0.001, beta_1=0.9, beta_2=0.999, epsilon=None, decay=0.0, amsgrad=False)
    LSTM_model.compile(optimizer = adam, loss = 'mean_squared_error')
    return LSTM_model
    
def train_model(stockticker, start_date, end_date, time_step = 40, future_step = 10):
    # get data
    df = getData(stockticker, start_date, end_date)
    
    # normalise data
    scaler= MinMaxScaler(feature_range=(0,1))
    df_scaled = df
    df_scaled[df_scaled.columns] = scaler.fit_transform(df[df.columns])
    df_scaled.head()
    
    #findCorelation(df_scaled)
    #plotData(df_scaled)
    
    # data preprocessing
    # split data set
    ratio=0.8
    train_data_x, train_data_y, val_data_x, val_data_y = split_dataset(df_scaled, 0.8)
    
    # create data set

    distance = 10
    x_train, y_train = create_dataset(train_data_x, train_data_y, time_step, future_step, distance)
    x_val, y_val = create_dataset(val_data_x, val_data_y, time_step, future_step)
    
    # construct model
    feature_num = len(df.columns)
    input_shape = (x_train.shape[1], feature_num)
    LSTM_model = construct_model(input_shape, future_step, optimizer="adam")
    LSTM_model.summary()
    
    # fit model
    history = LSTM_model.fit(x_train, y_train, validation_split=0.2, validation_data=(x_val, y_val), epochs = 60, batch_size=10)
    
    # plot result
    plt.plot(history.history['loss'])
    plt.plot(history.history['val_loss'])
    plt.title('model loss')
    plt.ylabel('loss')
    plt.xlabel('epoch')
    plt.legend(['train', 'val'], loc='upper left')
    plt.savefig('Saved_Model/Stock_{stockticker}.png')
    plt.show()
    
    # save model
    LSTM_model.save(f'Saved_Model/{stockticker}_lstm.h5')

def dailyLSTMTrain():
    # use past 40 days to predict future 10 days value
    time_step = 40 
    future_step = 10
    
    # Select the range of training dataset, default 5 years
    years = 5
    end_date = pd.to_datetime("today")
    start_date = end_date - pd.Timedelta(years*365, unit='D')
    
    # List of stocks
    stocktickers=['AAPL','MSFT','AMZN','TSLA','GOOG','BRK-B','UNH','JNJ','XOM','META','NVDA','JPM','PG','V','HD','CVX','MA','PFE','LLY']
    
    # Train model for each stock
    for stockticker in stocktickers:
        print("********************************"+stockticker+"***************************************")
        train_model(stockticker, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"), time_step, future_step)



   
def get_past_data(stockticker, today_date, time_step):
    end_date  = today_date.strftime("%Y-%m-%d")
    start_date = (today_date-pd.Timedelta(100, unit='D')).strftime("%Y-%m-%d")
    
    df = getHistoricalData(stockticker, start_date, end_date)
    
    df = getMacroIndicator(df, stockticker, start_date, end_date)
    
    df = getTechnicalIndicator(df, stockticker, start_date, end_date)
    
    # drop all NaN data
    df = df[["volume", "VIX", "USDX", "MACD", "RSI", "ATR", "adjclose"]][25:]
    
    # Select last time_step rows
    df = df.tail(time_step)
    return df

def get_predict(stockticker, today_date, future_dates, time_step = 40, future_step = 10):
    # get data
    df = get_past_data(stockticker, today_date, time_step)
    data_y = df.iloc[:, 6:7]
    
    # normalise data
    scaler= MinMaxScaler(feature_range=(0,1))
    df[df.columns] = scaler.fit_transform(df[df.columns])
    df = np.array(df, dtype=float).reshape(1, df.shape[0], len(df.columns))
     
    # load model
    LSTM_model = load_model(f'Saved_Model/{stockticker}_lstm.h5')
    
    # predict
    predicted_stock_price = LSTM_model.predict(df)  
    scaler.fit_transform(data_y)
    predicted = pd.DataFrame(scaler.inverse_transform(predicted_stock_price)[0], columns=["adjclose"])
    predicted.index = future_dates  
    
    # Plot the graph
    #plotData(data_y, predicted, time_step, future_step)
    
    # create data base
    data = pd.concat([data_y.tail(10), predicted], axis=0)
    df = pd.DataFrame(columns=["ticker", "date", "price"])
    df["date"] = data.index
    df["price"] = data.adjclose.values
    df = df.assign(ticker=stockticker)
    return df
   
def getLSTM():
    # use past 40 days to predict future 10 days value
    time_step = 40 
    future_step = 10
    
    # find today's date
    today_date = pd.to_datetime("today")
    
    # find future prediction dates
    future_dates = []
    dates_num = 0
    i = 0
    while dates_num < future_step:
        date = today_date + pd.Timedelta(i, unit='D')
        i += 1
        if date.dayofweek <= 4:
            future_dates.append(date.strftime("%Y-%m-%d"))
            dates_num += 1
 
    # List of stocks
    stocktickers=['AAPL','MSFT','AMZN','TSLA','GOOG','BRK-B','UNH','JNJ','XOM','META','NVDA','JPM','PG','V','HD','CVX','MA','PFE','LLY']
    # connect to database
    db = os.path.join("/home/sma/deploy/SmartPortfolioAdvisor/System Code/", "frontend/src/database/lstm_prediction.db")
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    table_name = "predictions"
    cursor.execute(f'CREATE TABLE IF NOT EXISTS {table_name} (ticker TEXT, date TEXT, price REAL)')
    conn.commit()
    
    # Train model for each stock
    df = pd.DataFrame(columns=["ticker", "date", "price"])
    for stockticker in stocktickers:
        print("********************************"+stockticker+"***************************************")
        predicted = get_predict(stockticker, today_date, future_dates, time_step, future_step)
        df = pd.concat([df, predicted], axis=0)
    
    # Save data to database
    df.to_sql(table_name, conn, if_exists='replace', index = False)

    
          
        
@app.route('/customga', methods = ["POST"])
def customga():
    req = request.get_json(silent=False, force=True)
    reqId = req['reqId']
    customStocktickers = req['stocktickers']
    customPopSize = int(req['popSize'])
    customNumEpoch = int(req['numEpoch'])
    customSelectionRate = float(req['selectionRate'])
    customCrossoverRate = float(req['crossoverRate'])
    customMutationRate = float(req['mutationRate'])
    curtime = time.time()
    enddate = timestampToDate(curtime)
    startdate = timestampToDate(curtime-(24*60*60*365))
    depth = 0
    print('stocktickers ' , req['stocktickers'])
    print('popSize ' , req['popSize'])
    print('numEpoch ' , req['numEpoch'])
    print('selectionRate ' , req['selectionRate'])
    print('crossoverRate ' , req['crossoverRate'])
    print('mutationRate ' , req['mutationRate'])
    print('enddate ' , enddate)
    print('startdate ' , startdate)
    generatedRunId = generateRunId()
    threads.append((reqId, socketio.start_background_task(
    	target=runGA, 
    	pop_size=customPopSize, 
    	stocktickers=customStocktickers, 
    	maxStocks=len(customStocktickers), 
        maxIterations=customNumEpoch, 
        selectionRate=customSelectionRate, 
        crossoverRate=customCrossoverRate, 
        mutationRate=customMutationRate, 
        startdate=startdate, 
        enddate=enddate, 
        depth=depth,
        maxDepth=1,
        runId=generatedRunId,
        reqId=reqId
    )))
    print('=================number of threads ', len(threads))
    return 'Server received request for runid: ' + generatedRunId
    
    
@app.cli.command('dailyGA')
def dailyGA():
    """ RUNS THE DAILY GENETIC ALGORITHM FOR ALL THE STOCK TICKERS"""
    stocktickers=['AAPL','MSFT','AMZN','TSLA','GOOG','BRK-B','UNH','JNJ','XOM','META',
              'NVDA','JPM','PG','V','HD','CVX','MA','PFE','LLY','PEP']
    yesterday = date.today() - timedelta(days = 1)
    dayBeforeYesterday = date.today() - timedelta(days = 2)
    gaStartDate = date.today() - timedelta(days = 365)
    pullFromYahooAPI(stocktickers, str(dayBeforeYesterday), str(date.today()))
    #runGA(10, stocktickers, 10, 40, 0.3, 0.6, 0.6, '2021-09-27', str(date.today()),0,5,'','')
    
    dailyLSTMTrain()
    getLSTM()
    
    reqId = ''
    customStocktickers = stocktickers
    customPopSize = 10
    customNumEpoch = 40
    customSelectionRate = 0.3
    customCrossoverRate = 0.6
    customMutationRate = 0.6
    #curtime = time.time()
    enddate = str(date.today())
    startdate = str(gaStartDate)
    depth = 0
    generatedRunId = generateRunId()
    threads.append((reqId, socketio.start_background_task(
    	target=runGA, 
    	pop_size=customPopSize, 
    	stocktickers=customStocktickers, 
    	maxStocks=len(customStocktickers), 
        maxIterations=customNumEpoch, 
        selectionRate=customSelectionRate, 
        crossoverRate=customCrossoverRate, 
        mutationRate=customMutationRate, 
        startdate=startdate, 
        enddate=enddate, 
        depth=depth,
        maxDepth=5,
        runId=generatedRunId,
        reqId=reqId
    )))
    print('=================number of threads ', len(threads))
    return 'Server received request for runid: ' + generatedRunId
    print("DAILY GA RUN COMPLETE")
    
@app.cli.command('dbRecordsDelete')        
def dbRecordsDelete():
    """ DELETE DATABASE RECORDS FOR ALL THE STOCK TICKERS FOR THE TIME MENTIONED"""
    con = sqlite3.connect('stocks.db')
    cur = con.cursor()
    sqlSelect = "delete FROM alltickers where date>= '2022-10-26'and date <= '2022-10-26' "
    print(sqlSelect)
    res = cur.execute(sqlSelect)
    con.commit()
    cur.close()
    con.close()
 
@app.cli.command()
def scheduled():
    """Run scheduled job."""
    print('Importing feeds...')
    today_date = pd.to_datetime("today")
    print("TODAY DATE: ", date.today())
    yesterday = date.today() - timedelta(1)
    print("YESTERDAY DATE: ", yesterday)
    yesterday2 = date.today() - timedelta(2)
    print("YESTERDAY DATE 2: ", yesterday2)
    gaStartDate = date.today() - timedelta(days = 365)
    print("GA Start Date : ",gaStartDate)
    print('Users:')
    print('Done!')  
    
    
@app.cli.command('eg')
def eg():
    stocktickers=['AAPL','MSFT','AMZN','TSLA','GOOG','BRK-B','UNH','JNJ','XOM','META',
              'NVDA','JPM','PG','V','HD','CVX','MA','PFE','LLY','PEP']
    yesterday = date.today() - timedelta(days=1)
    dayBeforeYesterday = date.today() - timedelta(days=2)
    print("TODAY'S DATE :", date.today())
    print("DAY BEFORE YESTERDAY DATE :", dayBeforeYesterday)
    pullFromYahooAPI(stocktickers, '2022-10-23', '2022-10-25')
    print("DAILY DATA LOAD COMPLETE")
