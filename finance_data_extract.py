##
# @file finance_data_extract.py
# @namespace finance_data_extract
# @author jimli
#
# Created on Fri May 10 23:06:56 2019
#
# This program will analyze the financial statements and stock
# quote of any publically traded company listed in Yahoo Finance
# using financial ratio analysis.
#
# The program output a report file in HTML or PDF format of the
# results of the analysis.
#
# The comments in this program will be written in Javadoc style. This ensures
# compatibility with Doxygen documentation tool.


import requests
import pandas as pd
import numpy as np

# Constants
ROUNDING_PRECISION = 3

##
# Stores financial data from financial statements in one
# convenient place.
class FinancialData (object):
    ##
    # Initializes the financial data class by collecting data
    # from specified financial statements.
    #
    # @param self A reference to this object.
    # @param balSht Balance Sheet DataFrame. 
    # @param incStmt Income Statement DataFrame.
    # @param cfStmt Cash Flow Statement DataFrame.
    # @param stkQte Stock Quote DataFrame.
    # @param dates Dates from the above financial statements.
    def __init__ (self, balSht, incStmt, cfStmt, stkQte, dates):
        # Balance Sheet Values
        self.__cce = pd.to_numeric(balSht["Cash And Cash Equivalents"])
        self.__currLia = pd.to_numeric(balSht["Total Current Liabilities"])
        self.__currAssets = pd.to_numeric(balSht["Total Current Assets"])
        self.__shortTermInv = pd.to_numeric(balSht["Short Term Investments"])
        self.__NR = pd.to_numeric(balSht["Net Receivables"])
        self.__inventory = pd.to_numeric(balSht["Inventory"])
        self.__totalAssets = pd.to_numeric(balSht["Total Assets"])
        self.__totalLia = pd.to_numeric(balSht["Total Liabilities"])
        self.__totalSE = pd.to_numeric(balSht["Total Stockholder Equity"])
        
        # Income Statement Values
        self.__sales = pd.to_numeric(incStmt["Total Revenue"])
        self.__gp = pd.to_numeric(incStmt["Gross Profit"])
        self.__noil = pd.to_numeric(incStmt["Operating Income or Loss"])
        self.__ie = pd.to_numeric(incStmt["Interest Expense"])
        self.__ebit = pd.to_numeric(\
                        incStmt["Earnings Before Interest and Taxes"])
        self.__cor = pd.to_numeric(incStmt["Cost of Revenue"])
        
        # Cash Flow Statement Values
        self.__ocf = pd.to_numeric(cfStmt\
                       ["Total Cash Flow From Operating Activities"])
        
    
    ##
    # Retrieves cash and cash equivalents value.
    #
    # @param self A reference to this object.
    # @return Value of Cash and cash equivalents.
    def getCashAndCashEquivalents (self):
        return self.__cce
    
    ##
    # Retrieves the current liabilities value.
    #
    # @param self A reference to this object.
    # @return Value of Current Liabilities.
    def getCurrentLiabilities (self):
        return self.__currLia
    
    ##
    # Retrieves the current liabilities value.
    #
    # @param self A reference to this object.
    # @return Value of Current Assets.
    def getCurrentAssets (self):
        return self.__currAssets
    
    ##
    # Retrieves short term investments value.
    #
    # @param self A reference to this object.
    # @return Value of short term investments.
    def getShortTermInvestments(self):
        return self.__shortTermInv
    
    ##
    # Retrieves net receivables value.
    #
    # @param self A reference to this object.
    # @return Value of net receivables.
    def getNetReceivables(self):
        return self.__NR
    
    ##
    # Retrieves inventory value.
    #
    # @param self A reference to this object.
    # @return Value of inventory.
    def getInventory(self):
        return self.__inventory
    
    ##
    # Retrieves total assets value.
    #
    # @param self A reference to this object.
    # @return Value of total assets.
    def getTotalAssets(self):
        return self.__totalAssets
    
    ##
    # Retrieves total liabilities value.
    #
    # @param self A reference to this object.
    # @return Value of total liabilities.
    def getTotalLiabilities(self):
        return self.__totalLia
    
    ##
    # Retrieves total stockholder's equity value.
    #
    # @param self A reference to this object.
    # @return Value of total stockholder's equity.
    def getTotalStockholderEquity(self):
        return self.__totalSE
    
    ##
    # Alias function for getTotalStockholderEquity().
    #
    # @param self A reference to this object.
    # @return Value of total shareholder's equity.
    def getTotalShareholderEquity(self):
        return self.getTotalStockholderEquity();
    
    ##
    # Retrieves sales amount.
    #
    # @param self A reference to this object.
    # @return Value of sales.
    def getSales(self):
        return self.__sales
    
    ##
    # Alias function for getSales().
    #
    # @param self A reference to this object.
    # @return Value of total shareholder's equity.
    def getTotalRevenue(self):
        return self.getSales();
    
    ##
    # Retrieves gross profit value.
    #
    # @param self A reference to this object.
    # @return Value of gross profit.
    def getGrossProfit(self):
        return self.__gp
    
    ##
    # Retrieves operating income/loss value.
    #
    # @param self A reference to this object.
    # @return Value of operating income/loss.
    def getOperatingIncomeOrLoss(self):
        return self.__noil
    
    ##
    # Alias function for getOperating.IncomeOrLoss()
    #
    # @param self A reference to this object.
    # @return Value of operating income/loss.
    def getNetOperatingIncomeOrLoss(self):
        return self.getOperatingIncomeOrLoss()
    
    ##
    # Retrieves interest expense value.
    #
    # @param self A reference to this object.
    # @return Value of interest expense. (Negative Value)
    def getInterestExpense(self):
        return self.__ie
    
    ##
    # Retrieves operating cash flows.
    #
    # @param self A reference to this object.
    # @return Value of operating cash flows.
    def getOperatingCashFlows(self):
        return self.__ocf
    
    ##
    # Retrieves earnings before interest and tax.
    #
    # @param self A reference to this object.
    # @return Value of earnings before interest and tax.
    def getEBIT(self):
        return self.__ebit
    
    ##
    # Retrieves cost of revenue.
    #
    # @param self A reference to this object.
    # @return Value of cost of revenue.
    def getCostOfRevenue(self):
        return self.__cor
    
    ##
    # Alias function for getCostOfRevenue().
    #
    # @param self A reference to this object.
    # @return Value of cost of revenue.
    def getCOR(self):
        return self.getCostOfRevenue()


# Functions

##
# Retrieves financial statements and stock quote of a company
# from Yahoo's website.
#
# @param ticker Ticker symbol for a public corporation.
#
# @return Balance Sheet, Income Statement, Cash Flow Statement, Stock Quote,
# and Historical Dates of the First 3 Documents, 
# all as Pandas DataFlow Objects (except for Dates, which is a NumPy array.)
def getFinancialStatementsFromYahoo (ticker):
    # URLs of various documents.
    url_cf_stmt = \
        "https://finance.yahoo.com/quote/%s/cash-flow?p=%s" %(ticker,ticker)
    url_income_stmt = \
        "https://finance.yahoo.com/quote/%s/financials?p=%s" %(ticker,ticker)
    url_balance_sheet = \
    "https://finance.yahoo.com/quote/%s/balance-sheet?p=%s" %(ticker,ticker)
    url_stock_quote = "https://finance.yahoo.com/quote/%s/" %(ticker)
    
    # To be on the safe side, we disguise this request as a Web Browser
    # request by adding this header.
    #
    # The request MIGHT successfully work without this header.
    
    myHeader = {
      "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
      "X-Requested-With": "XMLHttpRequest"
    }
    
    # Make a request for EACH document
    requestCfStmt = requests.get(url_cf_stmt, headers=myHeader)
    print("Retrieved Cash Flow Statement.")
    requestBalSht = requests.get(url_balance_sheet, headers=myHeader)
    print("Retrieved Balance Sheet.")
    requestIncStmt = requests.get(url_income_stmt, headers=myHeader)
    print("Retrieved Income Statement.")
    requestStkQte = requests.get(url_stock_quote,headers=myHeader)
    print("Retrieved Stock Quote Statement.")
    
    # Format the tables into Pandas Dataflows
    # Note: It is best to have repetitve code, so that
    # the code can easily be changed if Yahoo Inc changes
    # its website's formatting.
    tablesCfStmt = pd.read_html(requestCfStmt.text)
    tablesBalSht = pd.read_html(requestBalSht.text)
    tablesIncStmt = pd.read_html(requestIncStmt.text)
    tablesStkQte = pd.read_html(requestStkQte.text)
    
    cfStmt = tablesCfStmt[0].transpose()
    cfStmt.columns = cfStmt.iloc[0]
    cfStmt = cfStmt[1:]
    
    balSht = tablesBalSht[0].transpose()
    balSht.columns = balSht.iloc[0]
    balSht = balSht[1:]
    
    incStmt = tablesIncStmt[0].transpose()
    incStmt.columns = incStmt.iloc[0]
    incStmt = incStmt[1:]
    
    stkQte0 = tablesStkQte[0].transpose()
    stkQte0.columns = stkQte0.iloc[0]
    stkQte1 = tablesStkQte[1].transpose()
    stkQte1.columns = stkQte1.iloc[0]
    stkQte = stkQte0.join(stkQte1, how='left')[1:]
    
    dates = incStmt[incStmt.columns[0]].values
    
    # Return stock information.
    return balSht, incStmt, cfStmt, stkQte, dates
##
# Calculates the Weighted Average Cost of Capital (WACC) of the firm.
# Parameters are retrieved from getFinancialStatementsFromYahoo().
#
# @param balSht Balance Sheet of the firm, as a Pandas DataFlow object.
# @param incStmt Income Statement of the firm, as a Pandas DataFlow object.
# @param stkQte Stock quote of the firm, as a Pandas DataFlow object.
#
# @return WACC of the firm, as a float.
def calculateWACC(balSht, incStmt, stkQte):
    # Calculate the cost of debt for the most recent year.
    interestExpense = np.array(list(map(int,\
                        incStmt["Interest Expense"].values[1:])))
    totalDebt = np.array(list(map(int,\
                        balSht["Total Liabilities"].values[1:])))
    
    costOfDebt4Yrs = np.abs(interestExpense)/totalDebt
    
    costOfDebt = pd.DataFrame({"K_d":costOfDebt4Yrs})[:1]\
        ["K_d"].values[0]
                 
    # Calculate the Cost of Equity for the most recent year,
    # using the current beta value.               
    beta = float(stkQte["Beta (3Y Monthly)"].values)        
    
    # These rates are educated guesses.
    riskFreeRate = 0.02 # 2% Assumed
    marketRate = 0.098 # Average historical rate of return for S&P 500.
    
    costOfEquity = riskFreeRate + beta*(marketRate - riskFreeRate)
    
    totalLiabilities = float(balSht["Total Liabilities"][1])
    totalEquity = float(balSht["Total Stockholder Equity"][1])
    totalLiaEquity = totalLiabilities + totalEquity
    
    # Calculate WACC
    WACC = (totalLiabilities/totalLiaEquity)*costOfDebt +\
        (totalEquity/totalLiaEquity)*costOfEquity

    return WACC

# Liquidity Ratios

##
# Calculates the cash ratio.
#
# Formula: Cash and Cash Equivalents / Current Liabilities
#
# @param balSht Balance Sheet DataFrame.
# @param dates Dates numpy array relevant to the financial statements.
#
# @return Cash Ratio table as a DataFrame object.
#
def calculateCashRatio (balSht, dates):
    global financialData
    cce = financialData.getCashAndCashEquivalents()
    currLia = financialData.getCurrentLiabilities()
    
    ratioAsSeries = cce/currLia
    
    return pd.DataFrame(ratioAsSeries.values, index=dates,\
                        columns=["Cash Ratio"])
    
##
# Calculates the quick ratio.
#
# Formula: Quick Assets / Current Liabilities
# Quick Assets include cash, cash equivalents, net receivables,
# and marketable securities.
#
# @param balSht Balance Sheet DataFrame.
# @param dates Dates numpy array relevant to the financial statements.
#
# @return Quick Ratio table as a DataFrame object.
def calculateQuickRatio (balSht, dates):
    global financialData
    cce = financialData.getCashAndCashEquivalents()
    si = financialData.getShortTermInvestments()
    nr = financialData.getNetReceivables()
    qa = cce + si + nr
    currLia = financialData.getCurrentLiabilities()
    
    ratioAsSeries = qa/currLia
    
    return pd.DataFrame(ratioAsSeries.values, index=dates,\
                        columns=["Quick Ratio"])

##
# Calculates the current ratio.
#
# Formula: Current Assets / Current Liabilities
#
# @param balSht Balance Sheet DataFrame.
# @param dates Dates numpy array relevant to the financial statements.
#
# @return Current Ratio table as a DataFrame object.
def calculateCurrentRatio (balSht, dates):
    global financialData
    currAssets = financialData.getCurrentAssets()
    currLia = financialData.getCurrentLiabilities()
    
    ratioAsSeries = currAssets/currLia
    
    return pd.DataFrame(ratioAsSeries.values, index=dates,\
                        columns=["Current Ratio"])
##
# Calculates working capital.
#
# Formula: Current Assets - Current Liabilities
#
# @param balSht Balance Sheet DataFrame.
# @param dates Dates numpy array relevant to the financial statements.
#
# @return Working Capital table as a DataFrame object.   
def calculateWorkingCapital(balSht, dates):
    global financialData
    currAssets = financialData.getCurrentAssets()
    currLia = financialData.getCurrentLiabilities()
    
    # Since all numbers are in thousands, we multiply
    # current assets and liabilities each by 1000.
    ratioAsSeries = 1000*currAssets - 1000*currLia
    
    return pd.DataFrame(ratioAsSeries.values, index=dates,\
                        columns=["Working Capital (WC)"])
##
# Calculates the cash to working capital ratio.
#
# Formula: Cash and Cash Equivalents / Working Capital
#
# @param balSht Balance Sheet DataFrame.
# @param dates Dates numpy array relevant to the financial statements.
#
# @return Cash To WC Ratio table as a DataFrame object.
#    
def calculateCashToWorkingCapitalRatio(balSht, dates):
    global financialData
    cce = financialData.getCashAndCashEquivalents()
    wc = calculateWorkingCapital(balSht, dates)
    wc_series = wc["Working Capital (WC)"]
    wc_series.index = cce.index
    
    # CCE in thousands, working capital in exact amount.
    ratioAsSeries = 1000*cce/wc_series
    
    return pd.DataFrame(ratioAsSeries.values, index=dates,\
                        columns=["Cash To WC Ratio"])
##
# Calculates the inventory to working capital ratio.
#
# Formula: Inventory / Working Capital
#
# @param balSht Balance Sheet DataFrame.
# @param dates Dates numpy array relevant to the financial statements.
#
# @return Inventory To WC Ratio table as a DataFrame object.   
def calculateInventoryToWorkingCapitalRatio(balSht, dates):
    global financialData
    inventory = financialData.getInventory()
    wc = calculateWorkingCapital(balSht, dates)
    wc_series = wc["Working Capital (WC)"]
    wc_series.index = inventory.index
    
    # Inventory in thousands, working capital in exact amount.
    ratioAsSeries = 1000*inventory/wc_series
    
    return pd.DataFrame(ratioAsSeries.values, index=dates,\
                        columns=["Inventory To WC Ratio"])
##
# Calculates the sales to working capital ratio.
#
# Formula: Sales / Working Capital
#
# @param balSht Balance Sheet DataFrame.
# @param incStmt Income Statement DataFrame.
# @param dates Dates numpy array relevant to the financial statements.
#
# @return Sales To WC Ratio table as a DataFrame object.   
def salesToWorkingCapitalRatio(balSht, incStmt, dates):
    global financialData
    sales = financialData.getSales()
    wc = calculateWorkingCapital(balSht, dates)
    wc_series = wc["Working Capital (WC)"]
    wc_series.index = sales.index
    
    # Sales in thousands, working capital in exact amount.
    ratioAsSeries = 1000*sales/wc_series
    
    return pd.DataFrame(ratioAsSeries.values, index=dates,\
                        columns=["Sales To WC Ratio"])
##
# Calculates the sales to current assets ratio.
#
# Formula: Sales / Current Assets
#
# @param balSht Balance Sheet DataFrame.
# @param incStmt Income Statement DataFrame.
# @param dates Dates numpy array relevant to the financial statements.
#
# @return Sales To Current Assets table as a DataFrame object. 
def salesToCurrentAssetsRatio(balSht, incStmt, dates):
    global financialData
    sales = financialData.getSales()
    ca = financialData.getCurrentAssets()
    
    ratioAsSeries = sales/ca
    
    return pd.DataFrame(ratioAsSeries.values, index=dates,\
                        columns=["Sales To Current Assets Ratio"])

# Solvency Ratios

##
# Calculates the debt ratio.
#
# Formula: Total Liabilities / Total Assets
#
# @param balSht Balance Sheet DataFrame.
# @param dates Dates numpy array relevant to the financial statements.
#
# @return Debt Ratio table as a DataFrame object.
def calculateDebtRatio(balSht, dates):
    global financialData
    tl = financialData.getTotalLiabilities()
    ta = financialData.getTotalAssets()
    
    ratioAsSeries = tl/ta
    
    return pd.DataFrame(ratioAsSeries.values, index=dates,\
                        columns=["Debt Ratio"])    
##
# Calculates the equity ratio.
#
# Formula: Total Equity / Total Assets
#
# @param balSht Balance Sheet DataFrame.
# @param dates Dates numpy array relevant to the financial statements.
#
# @return Equity Ratio table as a DataFrame object.  
def calculateEquityRatio(balSht, dates):
    global financialData
    te = financialData.getTotalStockholderEquity()
    ta = financialData.getTotalAssets()
    
    ratioAsSeries = te/ta
    
    return pd.DataFrame(ratioAsSeries.values, index=dates,\
                        columns=["Equity Ratio"])
    
##
# Calculates the debt to equity ratio.
#
# Formula: Total Liabilities / Total Equity
#
# @param balSht Balance Sheet DataFrame.
# @param dates Dates numpy array relevant to the financial statements.
#
# @return Debt to Equity Ratio table as a DataFrame object.  
def calculateDebtToEquityRatio(balSht, dates):
    global financialData
    te = financialData.getTotalStockholderEquity()
    tl = financialData.getTotalLiabilities()
    ratioAsSeries = tl/te
    
    return pd.DataFrame(ratioAsSeries.values, index=dates,\
                        columns=["Debt to Equity Ratio"])

##
# Calculates the debt to income ratio.
#
# Formula: Total Liabilities / Gross Income
#
# @param balSht Balance Sheet DataFrame.
# @param incStmt Income Statement DataFrame.
# @param dates Dates numpy array relevant to the financial statements.
#
# @return Debt to Equity Ratio table as a DataFrame object.   
def calculateDebtToIncomeRatio(balSht, incStmt, dates):
    global financialData
    tl = financialData.getTotalLiabilities()
    gp = financialData.getGrossProfit()
    
    ratioAsSeries = tl/gp
    
    return pd.DataFrame(ratioAsSeries.values, index=dates,\
                        columns=["Debt to Income Ratio"])
   
##
# Calculates the debt service coverage ratio.
#
# Formula: Gross Operating Income / Debt Payments
# Debt Payments = Interest Expense + Loan Payments (not shown in Yahoo
# Financial)
#
# @param balSht Balance Sheet DataFrame.
# @param incStmt Income Statement DataFrame.
# @param dates Dates numpy array relevant to the financial statements.
#
# @return Debt Service Coverage Ratio table as a DataFrame object.
def calculateDebtServiceCoverageRatio(balSht, incStmt, dates):
    global financialData
    noi = financialData.getOperatingIncomeOrLoss()
    ie = financialData.getInterestExpense()
    
    ratioAsSeries = noi/ie
    
    return pd.DataFrame(ratioAsSeries.values, index=dates,\
                        columns=["Debt Service Coverage Ratio"])
##
# Calculates the cash flow to debt ratio.
#
# Formula: Gross Operating Cash Flow / Total Liabilities
#
# @param balSht Balance Sheet DataFrame.
# @param cfStmt Cash Flow Statement DataFrame.
# @param dates Dates numpy array relevant to the financial statements.
#
# @return Cash Flow To Debt Ratio table as a DataFrame object.    
def calculateCashFlowToDebtRatio(balSht, cfStmt, dates):
    global financialData
    ocf = financialData.getOperatingCashFlows()
    tl = financialData.getTotalLiabilities()
    
    ratioAsSeries = ocf/tl
    
    return pd.DataFrame(ratioAsSeries.values, index=dates,\
                        columns=["Cash Flow to Debt Ratio"])

##
# Calculates working capital to debt ratio.
#
# Formula: Working Captial / Total Liabilities
#
# @param balSht Balance Sheet DataFrame.
# @param dates Dates numpy array relevant to the financial statements.
#
# @return Working Capital to Debt Ratio table as a DataFrame object.
def calculateWCToDebtRatio(balSht, dates):
    global financialData
    tl = financialData.getTotalLiabilities()
    wc = calculateWorkingCapital(balSht, dates)
    wc_series = wc["Working Capital (WC)"]
    wc_series.index = tl.index
    
    ratioAsSeries = wc_series/tl
    
    return pd.DataFrame(ratioAsSeries.values, index=dates,\
                        columns=["WC to Debt Ratio"])
##
# Calculates times interest earned.
#
# Formula: EBIT / Interest Expense
#
# @param balSht Balance Sheet DataFrame.
# @param dates Dates numpy array relevant to the financial statements.
#
# @return Working Capital to Debt Ratio table as a DataFrame object.   
def calculateTimesInterestEarned(incStmt, dates):
    global financialData
    ebit = financialData.getEBIT()
    ie = np.abs(financialData.getInterestExpense())
    
    ratioAsSeries = ebit/ie
    
    return pd.DataFrame(ratioAsSeries.values, index=dates,\
                        columns=["Times Interest Earned"])
    
# Efficiency Ratios
    
##
# Calculates the asset turnover ratio.
#
# Formula: Sales / Avg Assets
#
# @param balSht Balance Sheet DataFrame.
# @param incStmt Income Statement DataFrame.
# @param dates Dates numpy array relevant to the financial statements.
#
# @return Asset Turnover Ratio table as a DataFrame object.
def calculateAssetTurnoverRatio(balSht, incStmt, dates):
    global financialData
    sales = financialData.getSales()
    totalAssets = financialData.getTotalAssets().values
    avgAssets = np.array([None]*len(totalAssets))
    
    for index in range(len(totalAssets)-1):
        avgAssets[index+1] = 0.5*(totalAssets[index]+totalAssets[index+1])
    
    avgAssets = pd.Series(avgAssets, index=range(1,len(avgAssets)+1))
    
    ratioAsSeries = sales/avgAssets
    
    return pd.DataFrame(ratioAsSeries.values, index=dates,\
                        columns=["Asset Turnover Ratio"])
    
##
# Calculates the inventory turnover ratio.
#
# Formula: COGS (or COR) / Avg Inventory
#
# @param balSht Balance Sheet DataFrame.
# @param incStmt Income Statement DataFrame.
# @param dates Dates numpy array relevant to the financial statements.
#
# @return Inventory Turnover Ratio table as a DataFrame object.
def calculateInventoryTurnoverRatio(balSht, incStmt, dates):
    global financialData
    cor = financialData.getCOR()
    totalInventory = financialData.getInventory().values
    avgInventory = np.array([None]*len(totalInventory))
    
    for index in range(len(totalInventory)-1):
        avgInventory[index+1] = 0.5*(totalInventory[index]+totalInventory[index+1])
    
    avgInventory = pd.Series(avgInventory, index=range(1,len(avgInventory)+1))
    
    ratioAsSeries = cor/avgInventory
    
    return pd.DataFrame(ratioAsSeries.values, index=dates,\
                        columns=["Inventory Turnover Ratio"])
  
##
# Calculates the accounts receivable turnover ratio.
#
# Formula: Sales / Avg A/R
#
# @param balSht Balance Sheet DataFrame.
# @param incStmt Income Statement DataFrame.
# @param dates Dates numpy array relevant to the financial statements.
#
# @return Accounts Receivable Turnover Ratio table as a DataFrame object.    
def calculateAccountsReceivableTurnoverRatio(dates):
    global financialData
    sales = financialData.getSales()
    totalAR = financialData.getNetReceivables().values
    avgAR = np.array([None]*len(totalAR))
    
    for index in range(len(totalAR)-1):
        avgAR[index+1] = 0.5*(totalAR[index]+totalAR[index+1])
    
    avgAR = pd.Series(avgAR, index=range(1,len(avgAR)+1))

    ratioAsSeries = sales/avgAR
    
    return pd.DataFrame(ratioAsSeries.values, index=dates,\
                        columns=["Accounts Receivable Turnover Ratio"])

# Report-generating Functions

##
# Retrieves a table of liquidity ratios.
#
# @param balSht Balance Sheet DataFrame.
# @param incStmt Income Statement DataFrame.
# @param dates Dates numpy array relevant to the financial statements.
#
# @return A table of liquidity ratios as a DataFrame array.
# Dimensions: Row labels represent ratios, column labels
# represent dates.
def getLiquidityRatios(balSht, incStmt, dates):
    listOfRatioTables = [calculateCashRatio(balSht, dates),
    calculateQuickRatio(balSht, dates),calculateCurrentRatio(balSht, dates),
    calculateWorkingCapital(balSht, dates), 
    calculateCashToWorkingCapitalRatio(balSht, dates),
    calculateInventoryToWorkingCapitalRatio(balSht, dates),
    salesToWorkingCapitalRatio(balSht, incStmt, dates),
    salesToCurrentAssetsRatio(balSht, incStmt, dates)]
    
    table = listOfRatioTables[0]

    for index in range(1,len(listOfRatioTables)):
        table = table.join(listOfRatioTables[index], how="left")
        
    return table.round(ROUNDING_PRECISION).astype(object).transpose()

##
# Retrieves a table of solvency ratios.
#
# @param balSht Balance Sheet DataFrame.
# @param incStmt Income Statement DataFrame.
# @param cfStmt Cash Flow Statement DataFrame.
# @param dates Dates numpy array relevant to the financial statements.
#
# @return A table of solvency ratios as a DataFrame array.
# represent dates.
def getSolvencyRatios(balSht, incStmt, cfStmt, dates):
    listOfRatioTables = \
    [calculateDebtRatio(balSht, dates),
     calculateEquityRatio(balSht, dates),
     calculateDebtToEquityRatio(balSht, dates),
     calculateDebtToIncomeRatio(balSht, incStmt, dates),
     calculateDebtServiceCoverageRatio(balSht, incStmt, dates),
     calculateCashFlowToDebtRatio(balSht, cfStmt, dates),
     calculateWCToDebtRatio(balSht, dates),
     calculateTimesInterestEarned(incStmt, dates)]
    
    table = listOfRatioTables[0]

    for index in range(1,len(listOfRatioTables)):
        table = table.join(listOfRatioTables[index], how="left")
        
    return table.round(ROUNDING_PRECISION).astype(object).transpose()

##
# Retrieves a table of efficiency ratios.
#
# @param balSht Balance Sheet DataFrame.
# @param incStmt Income Statement DataFrame.
# @param cfStmt Cash Flow Statement DataFrame.
# @param dates Dates numpy array relevant to the financial statements.
#
# @return A table of efficiency ratios as a DataFrame array.
# represent dates.
def getEfficiencyRatios(balSht, incStmt, cfStmt, dates):
    listOfRatioTables = \
    [calculateAssetTurnoverRatio(balSht, incStmt, dates),
     calculateInventoryTurnoverRatio(balSht, incStmt, dates),
     calculateAccountsReceivableTurnoverRatio(dates)]
    
    table = listOfRatioTables[0]

    for index in range(1,len(listOfRatioTables)):
        table = table.join(listOfRatioTables[index], how="left")
        
    return table.round(ROUNDING_PRECISION).astype(object).transpose()

##
# Outputs an HTML file with all financial ratios.
#
# @param balSht Balance Sheet DataFrame.
# @param incStmt Income Statement DataFrame.
# @param cfStmt Cash Flow Statement DataFrame.
# @param stkQte Stock Quote DataFrame.
# @param dates Dates numpy array relevant to the financial statements.
def createMasterReport(balSht, incStmt, cfStmt, stkQte, dates):
    liqTable = getLiquidityRatios(balSht, incStmt, dates)
    solvTable = getSolvencyRatios(balSht, incStmt, cfStmt, dates)
    effTable = getEfficiencyRatios(balSht, incStmt, cfStmt, dates)
        
    liqTableHTML = liqTable.to_html() # "liqRatios.html"
    solvTableHTML = solvTable.to_html() # "solvRatios.html"
    effTableHTML = effTable.to_html() # "effRatios.html"
    
    header = \
    """
    <html>
    <head>
    <title> Financial Ratios </title>
    <body>
    """
    
    liqTableHTML = \
    """
    <h1> <u> Liquidity Ratios </u> </h1>
    """ + liqTableHTML
    
    solvTableHTML = \
    """
    <h1> <u> Solvency Ratios </u> </h1>
    """ + solvTableHTML
    
    effTableHTML = \
    """
    <h1> <u> Efficiency Ratios </u> </h1>
    """ + effTableHTML
    
    footer = \
    """
    </body>
    </html>
    """
    
    src = header + liqTableHTML + solvTableHTML + effTableHTML + footer
    
    myFile = open("FinancialRatios.html", "w")
    myFile.write(src)
    myFile.close()
    
# Main Program

if __name__ == "__main__":
    balSht, incStmt, cfStmt, stkQte, dates = \
        getFinancialStatementsFromYahoo("KO")
    financialData = FinancialData(balSht, incStmt, cfStmt, stkQte, dates)
    createMasterReport(balSht, incStmt, cfStmt, stkQte, dates)