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

#
# Stores financial data from financial statements in one
# convenient place.
class FinancialData (object):
    # Initializes the financial data class by collecting data
    # from specified financial statements.
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

        # Net Income Value
        temp = incStmt["Net Income"]
        temp.columns = ["NanCol", "Net Income"]
        self.__ni = pd.to_numeric(temp["Net Income"])

        # Cash Flow Statement Values
        self.__ocf = pd.to_numeric(cfStmt\
                       ["Total Cash Flow From Operating Activities"])

    def getCashAndCashEquivalents (self):
        return self.__cce

    def getCurrentLiabilities (self):
        return self.__currLia

    def getCurrentAssets (self):
        return self.__currAssets

    def getShortTermInvestments(self):
        return self.__shortTermInv

    def getNetReceivables(self):
        return self.__NR

    def getInventory(self):
        return self.__inventory

    def getTotalAssets(self):
        return self.__totalAssets

    def getTotalLiabilities(self):
        return self.__totalLia

    def getTotalStockholderEquity(self):
        return self.__totalSE

    def getTotalShareholderEquity(self):
        return self.getTotalStockholderEquity();

    def getSales(self):
        return self.__sales

    def getTotalRevenue(self):
        return self.getSales();

    def getGrossProfit(self):
        return self.__gp

    def getOperatingIncomeOrLoss(self):
        return self.__noil

    def getNetOperatingIncomeOrLoss(self):
        return self.getOperatingIncomeOrLoss()

    def getInterestExpense(self):
        return self.__ie

    def getOperatingCashFlows(self):
        return self.__ocf

    def getEBIT(self):
        return self.__ebit

    def getCostOfRevenue(self):
        return self.__cor

    def getCOR(self):
        return self.getCostOfRevenue()

    def getNetIncome(self):
        return self.__ni


# Functions

# Retrieves financial statements and stock quote of a company
# from Yahoo's website.
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

# Calculates the Weighted Average Cost of Capital (WACC) of the firm.
# Parameters are retrieved from getFinancialStatementsFromYahoo().
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
def calculateCashRatio (dates):
    global financialData
    cce = financialData.getCashAndCashEquivalents()
    currLia = financialData.getCurrentLiabilities()

    ratioAsSeries = cce/currLia

    return pd.DataFrame(ratioAsSeries.values, index=dates,\
                        columns=["Cash Ratio"])

def calculateQuickRatio (dates):
    global financialData
    cce = financialData.getCashAndCashEquivalents()
    si = financialData.getShortTermInvestments()
    nr = financialData.getNetReceivables()
    qa = cce + si + nr
    currLia = financialData.getCurrentLiabilities()

    ratioAsSeries = qa/currLia

    return pd.DataFrame(ratioAsSeries.values, index=dates,\
                        columns=["Quick Ratio"])

def calculateCurrentRatio (dates):
    global financialData
    currAssets = financialData.getCurrentAssets()
    currLia = financialData.getCurrentLiabilities()

    ratioAsSeries = currAssets/currLia

    return pd.DataFrame(ratioAsSeries.values, index=dates,\
                        columns=["Current Ratio"])

def calculateWorkingCapital(dates):
    global financialData
    currAssets = financialData.getCurrentAssets()
    currLia = financialData.getCurrentLiabilities()

    # Since all numbers are in thousands, we multiply
    # current assets and liabilities each by 1000.
    ratioAsSeries = 1000*currAssets - 1000*currLia

    return pd.DataFrame(ratioAsSeries.values, index=dates,\
                        columns=["Working Capital (WC)"])

def calculateCashToWorkingCapitalRatio(dates):
    global financialData
    cce = financialData.getCashAndCashEquivalents()
    wc = calculateWorkingCapital(dates)
    wc_series = wc["Working Capital (WC)"]
    wc_series.index = cce.index

    # CCE in thousands, working capital in exact amount.
    ratioAsSeries = 1000*cce/wc_series

    return pd.DataFrame(ratioAsSeries.values, index=dates,\
                        columns=["Cash To WC Ratio"])

def calculateInventoryToWorkingCapitalRatio(dates):
    global financialData
    inventory = financialData.getInventory()
    wc = calculateWorkingCapital(dates)
    wc_series = wc["Working Capital (WC)"]
    wc_series.index = inventory.index

    # Inventory in thousands, working capital in exact amount.
    ratioAsSeries = 1000*inventory/wc_series

    return pd.DataFrame(ratioAsSeries.values, index=dates,\
                        columns=["Inventory To WC Ratio"])

def salesToWorkingCapitalRatio(dates):
    global financialData
    sales = financialData.getSales()
    wc = calculateWorkingCapital(dates)
    wc_series = wc["Working Capital (WC)"]
    wc_series.index = sales.index

    # Sales in thousands, working capital in exact amount.
    ratioAsSeries = 1000*sales/wc_series

    return pd.DataFrame(ratioAsSeries.values, index=dates,\
                        columns=["Sales To WC Ratio"])

def salesToCurrentAssetsRatio(dates):
    global financialData
    sales = financialData.getSales()
    ca = financialData.getCurrentAssets()

    ratioAsSeries = sales/ca

    return pd.DataFrame(ratioAsSeries.values, index=dates,\
                        columns=["Sales To Current Assets Ratio"])

# Solvency Ratios

def calculateDebtRatio(dates):
    global financialData
    tl = financialData.getTotalLiabilities()
    ta = financialData.getTotalAssets()

    ratioAsSeries = tl/ta

    return pd.DataFrame(ratioAsSeries.values, index=dates,\
                        columns=["Debt Ratio"])

def calculateEquityRatio(dates):
    global financialData
    te = financialData.getTotalStockholderEquity()
    ta = financialData.getTotalAssets()

    ratioAsSeries = te/ta

    return pd.DataFrame(ratioAsSeries.values, index=dates,\
                        columns=["Equity Ratio"])

def calculateDebtToEquityRatio(dates):
    global financialData
    te = financialData.getTotalStockholderEquity()
    tl = financialData.getTotalLiabilities()
    ratioAsSeries = tl/te

    return pd.DataFrame(ratioAsSeries.values, index=dates,\
                        columns=["Debt to Equity Ratio"])

def calculateDebtToIncomeRatio(dates):
    global financialData
    tl = financialData.getTotalLiabilities()
    gp = financialData.getGrossProfit()

    ratioAsSeries = tl/gp

    return pd.DataFrame(ratioAsSeries.values, index=dates,\
                        columns=["Debt to Income Ratio"])

def calculateDebtServiceCoverageRatio(dates):
    global financialData
    noi = financialData.getOperatingIncomeOrLoss()
    ie = financialData.getInterestExpense()

    ratioAsSeries = noi/ie

    return pd.DataFrame(ratioAsSeries.values, index=dates,\
                        columns=["Debt Service Coverage Ratio"])

def calculateCashFlowToDebtRatio(dates):
    global financialData
    ocf = financialData.getOperatingCashFlows()
    tl = financialData.getTotalLiabilities()

    ratioAsSeries = ocf/tl

    return pd.DataFrame(ratioAsSeries.values, index=dates,\
                        columns=["Cash Flow to Debt Ratio"])

def calculateWCToDebtRatio(dates):
    global financialData
    tl = financialData.getTotalLiabilities()
    wc = calculateWorkingCapital(dates)
    wc_series = wc["Working Capital (WC)"]
    wc_series.index = tl.index

    ratioAsSeries = wc_series/tl

    return pd.DataFrame(ratioAsSeries.values, index=dates,\
                        columns=["WC to Debt Ratio"])

def calculateTimesInterestEarned(dates):
    global financialData
    ebit = financialData.getEBIT()
    ie = np.abs(financialData.getInterestExpense())

    ratioAsSeries = ebit/ie

    return pd.DataFrame(ratioAsSeries.values, index=dates,\
                        columns=["Times Interest Earned"])

# Efficiency Ratios

def calculateAssetTurnoverRatio(dates):
    global financialData
    sales = financialData.getSales()
    totalAssets = financialData.getTotalAssets().values
    avgAssets = np.array([None]*len(totalAssets))

    for index in range(len(totalAssets)-1):
        avgAssets[index] = 0.5*(totalAssets[index]+totalAssets[index+1])

    avgAssets = pd.Series(avgAssets, index=range(1,len(avgAssets)+1))

    ratioAsSeries = sales/avgAssets

    return pd.DataFrame(ratioAsSeries.values, index=dates,\
                        columns=["Asset Turnover Ratio"])

def calculateInventoryTurnoverRatio(dates):
    global financialData
    cor = financialData.getCOR()
    totalInventory = financialData.getInventory().values
    avgInventory = np.array([None]*len(totalInventory))

    for index in range(len(totalInventory)-1):
        avgInventory[index] = 0.5*(totalInventory[index]+totalInventory[index+1])

    avgInventory = pd.Series(avgInventory, index=range(1,len(avgInventory)+1))

    ratioAsSeries = cor/avgInventory

    return pd.DataFrame(ratioAsSeries.values, index=dates,\
                        columns=["Inventory Turnover Ratio"])

def calculateAccountsReceivableTurnoverRatio(dates):
    global financialData
    sales = financialData.getSales()
    totalAR = financialData.getNetReceivables().values
    avgAR = np.array([None]*len(totalAR))

    for index in range(len(totalAR)-1):
        avgAR[index] = 0.5*(totalAR[index]+totalAR[index+1])

    avgAR = pd.Series(avgAR, index=range(1,len(avgAR)+1))

    ratioAsSeries = sales/avgAR

    return pd.DataFrame(ratioAsSeries.values, index=dates,\
                        columns=["Accounts Receivable Turnover Ratio"])

# Profitability Ratios

def calculateROARatio(dates):
    global financialData
    ni = financialData.getNetIncome()
    totalAssets = financialData.getTotalAssets().values
    avgAssets = np.array([None]*len(totalAssets))

    for index in range(len(totalAssets)-1):
        avgAssets[index] = 0.5*(totalAssets[index]+totalAssets[index+1])

    avgAssets = pd.Series(avgAssets, index=range(1,len(avgAssets)+1))

    ratioAsSeries = ni/avgAssets

    return pd.DataFrame(ratioAsSeries.values, index=dates,\
                        columns=["Return on Assets"])

def calculateROERatio(dates):
    global financialData
    ni = financialData.getNetIncome()
    totalSE = financialData.getTotalStockholderEquity()

    ratioAsSeries = ni / totalSE

    return pd.DataFrame(ratioAsSeries.values, index=dates,\
                        columns=["Return on Equity"])

def calculateROSRatio(dates):
    global financialData
    ebit = financialData.getEBIT()
    sales = financialData.getSales()

    ratioAsSeries = ebit / sales

    return pd.DataFrame(ratioAsSeries.values, index=dates,\
                        columns=["Return on Sales"])

def calculateNetProfitMarginRatio(dates):
    global financialData
    ni = financialData.getNetIncome()
    sales = financialData.getSales()

    ratioAsSeries = ni/sales

    return pd.DataFrame(ratioAsSeries.values, index=dates,\
                        columns=["Net Profit Margin Ratio"])

def calculateGrossProfitMarginRatio(dates):
    global financialData
    gp = financialData.getGrossProfit()
    sales = financialData.getSales()

    ratioAsSeries = gp/sales

    return pd.DataFrame(ratioAsSeries.values, index=dates,\
                        columns=["Gross Profit Margin Ratio"])

def calculateOperatingProfitMarginRatio(dates):
    global financialData
    op = financialData.getOperatingIncomeOrLoss()
    sales = financialData.getSales()

    ratioAsSeries = op/sales

    return pd.DataFrame(ratioAsSeries.values, index=dates,\
                        columns=["Operating Profit Margin Ratio"])

# Report-generating Functions
def getLiquidityRatios(dates):
    listOfRatioTables = [calculateCashRatio(dates),
    calculateQuickRatio(dates),calculateCurrentRatio(dates),
    calculateWorkingCapital(dates),
    calculateCashToWorkingCapitalRatio(dates),
    calculateInventoryToWorkingCapitalRatio(dates),
    salesToWorkingCapitalRatio(dates),
    salesToCurrentAssetsRatio(dates)]

    table = listOfRatioTables[0]

    for index in range(1,len(listOfRatioTables)):
        table = table.join(listOfRatioTables[index], how="left")

    return table.round(ROUNDING_PRECISION).astype(object).transpose()

def getSolvencyRatios(dates):
    listOfRatioTables = \
    [calculateDebtRatio(dates),
     calculateEquityRatio(dates),
     calculateDebtToEquityRatio(dates),
     calculateDebtToIncomeRatio(dates),
     calculateDebtServiceCoverageRatio(dates),
     calculateCashFlowToDebtRatio(dates),
     calculateWCToDebtRatio(dates),
     calculateTimesInterestEarned(dates)]

    table = listOfRatioTables[0]

    for index in range(1,len(listOfRatioTables)):
        table = table.join(listOfRatioTables[index], how="left")

    return table.round(ROUNDING_PRECISION).astype(object).transpose()

def getEfficiencyRatios(dates):
    listOfRatioTables = \
    [calculateAssetTurnoverRatio(dates),
     calculateInventoryTurnoverRatio(dates),
     calculateAccountsReceivableTurnoverRatio(dates)]

    table = listOfRatioTables[0]

    for index in range(1,len(listOfRatioTables)):
        table = table.join(listOfRatioTables[index], how="left")

    return table.round(ROUNDING_PRECISION).astype(object).transpose()

def getProfitabilityRatios(dates):
    listOfRatioTables = \
    [calculateROARatio(dates),\
     calculateROERatio(dates),\
     calculateROSRatio(dates),\
     calculateNetProfitMarginRatio(dates),\
     calculateGrossProfitMarginRatio(dates),\
     calculateOperatingProfitMarginRatio(dates)]

    table = listOfRatioTables[0]

    for index in range(1,len(listOfRatioTables)):
        table = table.join(listOfRatioTables[index], how="left")

    return table.round(ROUNDING_PRECISION).astype(object).transpose()

def createMasterReport(dates):
    liqTable = getLiquidityRatios(dates)
    solvTable = getSolvencyRatios(dates)
    effTable = getEfficiencyRatios(dates)
    profitTable = getProfitabilityRatios(dates)

    liqTableHTML = liqTable.to_html() # "liqRatios.html"
    solvTableHTML = solvTable.to_html() # "solvRatios.html"
    effTableHTML = effTable.to_html() # "effRatios.html"
    profitTableHTML = profitTable.to_html()

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

    profitTableHTML = \
    """
    <h1> <u> Profitability Ratios </u> </h1>
    """ + profitTableHTML

    footer = \
    """
    </body>
    </html>
    """

    src = header + liqTableHTML + solvTableHTML + effTableHTML + \
        profitTableHTML + footer

    myFile = open("FinancialRatios.html", "w")
    myFile.write(src)
    myFile.close()

# Main Program
if __name__ == "__main__":
    balSht, incStmt, cfStmt, stkQte, dates = \
        getFinancialStatementsFromYahoo("KO")
    financialData = FinancialData(balSht, incStmt, cfStmt, stkQte, dates)
    createMasterReport(dates)
