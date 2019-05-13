"""
@author jimli

Created on Fri May 10 23:06:56 2019

This program will analyze the financial statements and stock
quote of any publically traded company listed in Yahoo Finance
using financial ratio analysis.

The program output a report file in HTML or PDF format of the
results of the analysis.

The comments in this program will be written in Javadoc style. This ensures
compatibility with Doxygen documentation tool.
"""

import requests
import pandas as pd
import numpy as np

# Constants
ROUNDING_PRECISION = 3

# Functions

"""
Retrieves financial statements and stock quote of a company
from Yahoo's website.

@param ticker Ticker symbol for a public corporation.

@return Balance Sheet, Income Statement, Cash Flow Statement, Stock Quote,
and Historical Dates of the First 3 Documents, 
all as Pandas DataFlow Objects (except for Dates, which is a NumPy array.)
"""
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

"""
Calculates the Weighted Average Cost of Capital (WACC) of the firm.
Parameters are retrieved from getFinancialStatementsFromYahoo().

@param balSht Balance Sheet of the firm, as a Pandas DataFlow object.
@param incStmt Income Statement of the firm, as a Pandas DataFlow object.
@param stkQte Stock quote of the firm, as a Pandas DataFlow object.

@return WACC of the firm, as a float.
"""
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

"""
Calculates the cash ratio.

Formula: Cash and Cash Equivalents / Current Liabilities

@param balSht Balance Sheet DataFrame.
@param dates Dates numpy array relevant to the financial statements.

@return Cash Ratio table as a DataFrame object.
"""
def calculateCashRatio (balSht, dates):
    cce = pd.to_numeric(balSht["Cash And Cash Equivalents"])
    currLia = pd.to_numeric(balSht["Total Current Liabilities"])
    
    ratioAsSeries = cce/currLia
    
    return pd.DataFrame(ratioAsSeries.values, index=dates,\
                        columns=["Cash Ratio"])
    
"""
Calculates the quick ratio.

Formula: Quick Assets / Current Liabilities
Quick Assets include cash, cash equivalents, net receivables,
and marketable securities.

@param balSht Balance Sheet DataFrame.
@param dates Dates numpy array relevant to the financial statements.

@return Quick Ratio table as a DataFrame object.
"""
def calculateQuickRatio (balSht, dates):
    cce = pd.to_numeric(balSht["Cash And Cash Equivalents"])
    si = pd.to_numeric(balSht["Short Term Investments"])
    nr = pd.to_numeric(balSht["Net Receivables"])
    qa = cce + si + nr
    currLia = pd.to_numeric(balSht["Total Current Liabilities"])
    
    ratioAsSeries = qa/currLia
    
    return pd.DataFrame(ratioAsSeries.values, index=dates,\
                        columns=["Quick Ratio"])

"""
Calculates the current ratio.

Formula: Current Assets / Current Liabilities

@param balSht Balance Sheet DataFrame.
@param dates Dates numpy array relevant to the financial statements.

@return Current Ratio table as a DataFrame object.
"""
def calculateCurrentRatio (balSht, dates):
    currAssets = pd.to_numeric(balSht["Total Current Assets"])
    currLia = pd.to_numeric(balSht["Total Current Liabilities"])
    
    ratioAsSeries = currAssets/currLia
    
    return pd.DataFrame(ratioAsSeries.values, index=dates,\
                        columns=["Current Ratio"])
"""
Calculates working capital.

Formula: Current Assets - Current Liabilities

@param balSht Balance Sheet DataFrame.
@param dates Dates numpy array relevant to the financial statements.

@return Working Capital table as a DataFrame object.
"""    
def calculateWorkingCapital(balSht, dates):
    currAssets = pd.to_numeric(balSht["Total Current Assets"])
    currLia = pd.to_numeric(balSht["Total Current Liabilities"])
    
    # Since all numbers are in thousands, we multiply
    # current assets and liabilities each by 1000.
    ratioAsSeries = 1000*currAssets - 1000*currLia
    
    return pd.DataFrame(ratioAsSeries.values, index=dates,\
                        columns=["Working Capital (WC)"])
"""
Calculates the cash to working capital ratio.

Formula: Cash and Cash Equivalents / Working Capital

@param balSht Balance Sheet DataFrame.
@param dates Dates numpy array relevant to the financial statements.

@return Cash To WC Ratio table as a DataFrame object.
"""    
def calculateCashToWorkingCapitalRatio(balSht, dates):
    cce = pd.to_numeric(balSht["Cash And Cash Equivalents"])
    wc = calculateWorkingCapital(balSht, dates)
    wc_series = wc["Working Capital (WC)"]
    wc_series.index = cce.index
    
    # CCE in thousands, working capital in exact amount.
    ratioAsSeries = 1000*cce/wc_series
    
    return pd.DataFrame(ratioAsSeries.values, index=dates,\
                        columns=["Cash To WC Ratio"])
"""
Calculates the inventory to working capital ratio.

Formula: Inventory / Working Capital

@param balSht Balance Sheet DataFrame.
@param dates Dates numpy array relevant to the financial statements.

@return Inventory To WC Ratio table as a DataFrame object.
"""     
def calculateInventoryToWorkingCapitalRatio(balSht, dates):
    inventory = pd.to_numeric(balSht["Inventory"])
    wc = calculateWorkingCapital(balSht, dates)
    wc_series = wc["Working Capital (WC)"]
    wc_series.index = inventory.index
    
    # Inventory in thousands, working capital in exact amount.
    ratioAsSeries = 1000*inventory/wc_series
    
    return pd.DataFrame(ratioAsSeries.values, index=dates,\
                        columns=["Inventory To WC Ratio"])
"""
Calculates the sales to working capital ratio.

Formula: Sales / Working Capital

@param balSht Balance Sheet DataFrame.
@param incStmt Income Statement DataFrame.
@param dates Dates numpy array relevant to the financial statements.

@return Sales To WC Ratio table as a DataFrame object.
"""     
def salesToWorkingCapitalRatio(balSht, incStmt, dates):
    sales = pd.to_numeric(incStmt["Total Revenue"])
    wc = calculateWorkingCapital(balSht, dates)
    wc_series = wc["Working Capital (WC)"]
    wc_series.index = sales.index
    
    # Sales in thousands, working capital in exact amount.
    ratioAsSeries = 1000*sales/wc_series
    
    return pd.DataFrame(ratioAsSeries.values, index=dates,\
                        columns=["Sales To WC Ratio"])
"""
Calculates the sales to current assets ratio.

Formula: Sales / Current Assets

@param balSht Balance Sheet DataFrame.
@param incStmt Income Statement DataFrame.
@param dates Dates numpy array relevant to the financial statements.

@return Sales To Current Assets table as a DataFrame object.
"""  
def salesToCurrentAssetsRatio(balSht, incStmt, dates):
    sales = pd.to_numeric(incStmt["Total Revenue"])
    ca = pd.to_numeric(balSht["Total Current Assets"])
    
    ratioAsSeries = sales/ca
    
    return pd.DataFrame(ratioAsSeries.values, index=dates,\
                        columns=["Sales To Current Assets Ratio"])

# Solvency Ratios

"""
Calculates the debt ratio.

Formula: Total Liabilities / Total Assets

@param balSht Balance Sheet DataFrame.
@param dates Dates numpy array relevant to the financial statements.

@return Debt Ratio table as a DataFrame object.
"""
def calculateDebtRatio(balSht, dates):
    tl = pd.to_numeric(balSht["Total Liabilities"])
    ta = pd.to_numeric(balSht["Total Assets"])
    
    ratioAsSeries = tl/ta
    
    return pd.DataFrame(ratioAsSeries.values, index=dates,\
                        columns=["Debt Ratio"])    
"""
Calculates the equity ratio.

Formula: Total Equity / Total Assets

@param balSht Balance Sheet DataFrame.
@param dates Dates numpy array relevant to the financial statements.

@return Equity Ratio table as a DataFrame object.
"""   
def calculateEquityRatio(balSht, dates):
    te = pd.to_numeric(balSht["Total Stockholder Equity"])
    ta = pd.to_numeric(balSht["Total Assets"])
    
    ratioAsSeries = te/ta
    
    return pd.DataFrame(ratioAsSeries.values, index=dates,\
                        columns=["Equity Ratio"])
    
"""
Calculates the debt to equity ratio.

Formula: Total Liabilities / Total Equity

@param balSht Balance Sheet DataFrame.
@param dates Dates numpy array relevant to the financial statements.

@return Debt to Equity Ratio table as a DataFrame object.
"""   
def calculateDebtToEquityRatio(balSht, dates):
    te = pd.to_numeric(balSht["Total Stockholder Equity"])
    tl = pd.to_numeric(balSht["Total Liabilities"])
    ratioAsSeries = tl/te
    
    return pd.DataFrame(ratioAsSeries.values, index=dates,\
                        columns=["Debt to Equity Ratio"])

"""
Calculates the debt to income ratio.

Formula: Total Liabilities / Gross Income

@param balSht Balance Sheet DataFrame.
@param incStmt Income Statement DataFrame.
@param dates Dates numpy array relevant to the financial statements.

@return Debt to Equity Ratio table as a DataFrame object.
"""    
def calculateDebtToIncomeRatio(balSht, incStmt, dates):
    tl = pd.to_numeric(balSht["Total Liabilities"])
    gp = pd.to_numeric(incStmt["Gross Profit"])
    
    ratioAsSeries = tl/gp
    
    return pd.DataFrame(ratioAsSeries.values, index=dates,\
                        columns=["Debt to Income Ratio"])
   
"""
Calculates the debt service coverage ratio.

Formula: Gross Operating Income / Debt Payments
Debt Payments = Interest Expense + Loan Payments (not shown in Yahoo
Financial)

@param balSht Balance Sheet DataFrame.
@param incStmt Income Statement DataFrame.
@param dates Dates numpy array relevant to the financial statements.

@return Debt Service Coverage Ratio table as a DataFrame object.
"""
def calculateDebtServiceCoverageRatio(balSht, incStmt, dates):
    noi = pd.to_numeric(incStmt["Operating Income or Loss"])
    ie = np.abs(pd.to_numeric(incStmt["Interest Expense"]))
    
    ratioAsSeries = noi/ie
    
    return pd.DataFrame(ratioAsSeries.values, index=dates,\
                        columns=["Debt Service Coverage Ratio"])
"""
Calculates the cash flow to debt ratio.

Formula: Gross Operating Cash Flow / Total Liabilities

@param balSht Balance Sheet DataFrame.
@param cfStmt Cash Flow Statement DataFrame.
@param dates Dates numpy array relevant to the financial statements.

@return Cash Flow To Debt Ratio table as a DataFrame object.
"""    
def calculateCashFlowToDebtRatio(balSht, cfStmt, dates):
    ocf = pd.to_numeric(cfStmt["Total Cash Flow From Operating Activities"])
    tl = pd.to_numeric(balSht["Total Liabilities"])
    
    ratioAsSeries = ocf/tl
    
    return pd.DataFrame(ratioAsSeries.values, index=dates,\
                        columns=["Cash Flow to Debt Ratio"])

"""
Calculates working capital to debt ratio.

Formula: Working Captial / Total Liabilities

@param balSht Balance Sheet DataFrame.
@param dates Dates numpy array relevant to the financial statements.

@return Working Capital to Debt Ratio table as a DataFrame object.
"""
def calculateWCToDebtRatio(balSht, dates):
    pass
    
# Report-generating Functions

"""
Retrieves a table of liquidity ratios.

@param balSht Balance Sheet DataFrame.
@param incStmt Income Statement DataFrame.
@param dates Dates numpy array relevant to the financial statements.

@return A table of liquidity ratios as a DataFrame array.
Dimensions: Row labels represent ratios, column labels
represent dates.
"""
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

"""
Retrieves a table of solvency ratios.

@param balSht Balance Sheet DataFrame.
@param incStmt Income Statement DataFrame.
@param cfStmt Cash Flow Statement DataFrame.
@param dates Dates numpy array relevant to the financial statements.

@return A table of solvency ratios as a DataFrame array.
Dimensions: Row labels represent ratios, column labels
represent dates.
"""
def getSolvencyRatios(balSht, incStmt, cfStmt, dates):
    listOfRatioTables = \
    [calculateDebtRatio(balSht, dates),
     calculateEquityRatio(balSht, dates),
     calculateDebtToEquityRatio(balSht, dates),
     calculateDebtToIncomeRatio(balSht, incStmt, dates),
     calculateDebtServiceCoverageRatio(balSht, incStmt, dates),
     calculateCashFlowToDebtRatio(balSht, cfStmt, dates)]
    
    table = listOfRatioTables[0]

    for index in range(1,len(listOfRatioTables)):
        table = table.join(listOfRatioTables[index], how="left")
        
    return table.round(ROUNDING_PRECISION).astype(object).transpose()

# Main Program
balSht, incStmt, cfStmt, stkQte, dates = \
    getFinancialStatementsFromYahoo("KO")

table = getSolvencyRatios(balSht, incStmt, cfStmt, dates)
    
print(table)
table.to_html("solvRatios.html")

#src = table.to_html()

#src = \
#"""
#<html>
#<head>
#<title> Liquidity Ratios </title>
#<body>
#
#<h1> <u> Liquidity Ratios </u> </h1>
#""" + src + \
#"""
#</body>
#</html>
#"""
#
#myFile = open("liqRatios.html", "w")
#myFile.write(src)
#myFile.close()