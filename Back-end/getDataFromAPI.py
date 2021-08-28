import requests
import json
import mysql.connector as mysql
import datetime
import time

def createDBConnection():        
    # Create a connection to the database
    db = mysql.connect(
        host = "SQL-SERVER",
        user = "SQLL-USERNAME",
        passwd = "SQL-PASSWORD",
        database = "SQL-DATABASE"
    ),

    return db

def closeDBConnection(cursor, cn):
    cursor.close()
    cn.close()

def get_data_from_api(stock_symbol, api_key):
    url = "https://alpha-vantage.p.rapidapi.com/query"

    querystring = {"function":"GLOBAL_QUOTE","symbol":f'{stock_symbol}'}

    headers = {
        'x-rapidapi-key': f"{api_key}",
        'x-rapidapi-host': "alpha-vantage.p.rapidapi.com"
        }

    response = requests.request("GET", url, headers=headers, params=querystring)
    return response.text

def checkForBuyOrders(symbol, price):
    """
    
    * @param symbol: symbol of the stock to check
    * @param price: current price of the stock to check for orders under that price
    """
    cn = createDBConnection()
    cursor = cn.cursor()
    query = f"SELECT * FROM `tbl_orders` WHERE `Symbol`='{symbol}' AND `Price`>={price} AND `Order_Type`='buy' AND `status`=0"
    cursor.execute(query)
    results = cursor.fetchall()
    for record in results:
        # Get all needed data from the record
        userID = record[2]
        wantedPrice = float(record[4])
        amount = int(record[5])
        newStatus = 1
        transactionPrice = price
        transactionAmount = transactionPrice* amount
        removeAmount = wantedPrice*amount
        query = f"SELECT * FROM `tbl_users` WHERE `userID`='{userID}'"
        cursor.execute(query)
        userData = cursor.fetchall()
        # Get current balances
        currentBalance = float(userData[0][2])
        holdingBalance = float(userData[0][3])
        # Get new balances
        newHolding = holdingBalance - removeAmount
        newCurrent = currentBalance - transactionAmount
        # update current balance and holding balance
        query = f"UPDATE `tbl_users` SET `Current_Balance`={newCurrent}, `Holding_Balance`={newHolding},`Last_Updated_Time`=CURRENT_TIMESTAMP() WHERE userID='{userID}'"
        cursor.execute(query)
        cn.commit()
        # Check if user already owns the same stock 
        query = f"SELECT COUNT(*) FROM `tbl_holding` WHERE `userID`='{userID}' AND `Symbol`='{symbol}'"
        cursor.execute(query)
        a = cursor.fetchall()
        exists = a[0][0]
        if (exists==0):
            # User does not own stock insert a new record
            query = f"""INSERT INTO `tbl_holding` (`userID`, `Symbol`, `Price_Bought_At`, `Amount`, `On_Hold`, `Last_Updated_Date`, `Current_Value`) VALUES('{userID}','{symbol}',{price},{amount},0,CURRENT_TIMESTAMP(),{price*amount})"""
            cursor.execute(query)
            cn.commit()
        else:
            # User owns the stock get the price and amount
            query = f"SELECT * FROM `tbl_holding` WHERE `userID`='{userID}' and `symbol`='{symbol}'"
            cursor.execute(query)
            row = cursor.fetchall()
            averageCost = float(row[0][2])
            currentlyOwnedAmount = float(row[0][3])
            newAverageCost = (averageCost*currentlyOwnedAmount+amount*transactionPrice)/(currentlyOwnedAmount+amount)
            newAmount = currentlyOwnedAmount + amount
            query = f"UPDATE `tbl_holding` SET `Price_Bought_At`={newAverageCost}, `Amount`={newAmount}, `Last_Updated_Date`=CURRENT_TIMESTAMP() WHERE `userID`='{userID}' AND `Symbol`='{symbol}'"
            cursor.execute(query)
            cn.commit()
        # Update the record on `tbl_orders` to have a 1 status and insert the price
        query = f"UPDATE `tbl_orders` SET `Status`=1, `Last_Updated_Time`=CURRENT_TIMESTAMP(), `Transaction_Price`={transactionPrice},`Transaction_Amount`={transactionAmount} WHERE `userID`='{userID}' AND `Symbol`='{symbol}' AND `Price`>={price} AND `Order_Type`='buy' AND `status`=0"
        cursor.execute(query)
        cn.commit()
    closeDBConnection(cursor, cn)

def checkForSellOrders(symbol, price):
    """
    
    * @param symbol: symbol of the stock to check
    * @param price: current price of the stock to check for orders under that price
    """
    cn = createDBConnection()
    cursor = cn.cursor()
    query = f"SELECT * FROM `tbl_orders` WHERE `Symbol`='{symbol}' AND `Price`<={price} AND `Order_Type`='sell' AND `status`=0"
    cursor.execute(query)
    results = cursor.fetchall()
    for record in results:
        # Get all needed data from the record
        userID = record[2]
        wantedPrice = record[4]
        amount = record[5]
        newStatus = 1
        transactionPrice = price
        transactionAmount = transactionPrice*amount
        # Change the tbl_holding to remove the amount
        query = f"UPDATE `tbl_holding` SET `Amount`=`Amount`-{amount},`On_Hold`=`On_Hold`-{amount}, `Last_Updated_Date`=CURRENT_TIMESTAMP WHERE `userID`='{userID}' AND `Symbol`='{symbol}'"
        cursor.execute(query)
        cn.commit()
        query =  f"UPDATE `tbl_holding` SET `Current_Value`=`Amount`*`Price_Bought_At` WHERE `userID`='{userID}' AND `Symbol`='{symbol}'"
        cursor.execute(query)
        cn.commit()
        # Update the record on `tbl_orders` to have a 1 status and insert the price
        query = f"UPDATE `tbl_orders` SET `Status`=1, `Last_Updated_Time`=CURRENT_TIMESTAMP, `Transaction_Price`={transactionPrice},`Transaction_Amount`={transactionAmount} WHERE `userID`='{userID}' AND `Symbol`='{symbol}' AND `Price`<={price} AND `Order_Type`='sell' AND `status`=0"
        cursor.execute(query)
        cn.commit()
        query = f"UPDATE `tbl_users` SET `Current_Balance`=`Current_Balance`+{transactionAmount}"
        cursor.execute(query)
        cn.commit()
    closeDBConnection(cursor, cn)

def deleteZeros():
    cn = createDBConnection()
    cursor = cn.cursor()
    query = "DELETE FROM `tbl_holding` WHERE `Amount`=0"
    cursor.execute(query)
    cn.commit()
    closeDBConnection(cursor, cn)

def checkLimit():
    # Get all expired orders
    cn = createDBConnection()
    cursor = cn.cursor()
    query = f"SELECT * FROM `tbl_orders` WHERE `Limit`<CURRENT_TIMESTAMP AND `Status`=0"
    cursor.execute(query)
    results = cursor.fetchall()

    for result in results:
        orderType = result[1]
        userID = result[2]
        symbol = result[3]
        wantedPrice = result[4]
        amount = result[5]
        if (orderType=='buy'):
            removeBalance = wantedPrice*amount
            query = f"UPDATE `tbl_users` SET `Holding_Balance`=`Holding_Balance`-{removeBalance} WHERE `userID`='{userID}'"
            cursor.execute(query)
            cn.commit()
        if (orderType=='sell'):
            query = f"UPDATE `tbl_holding` SET `On_Hold`=`On_Hold`-{amount} WHERE `userID`='{userID}' AND `Symbol`='{symbol}'"
            cursor.execute(query)
            cn.commit()
        query1 = f"UPDATE `tbl_orders` SET `Status`=9, `Last_Updated_Time`= CURRENT_TIMESTAMP WHERE `Limit`<CURRENT_TIMESTAMP AND `Status`=0"
        cursor.execute(query1)
        cn.commit()
    closeDBConnection(cursor, cn)

def updateTotal():
    # Get all users
    cn = createDBConnection()
    cursor = cn.cursor()
    query = "SELECT `userID` FROM `tbl_users`"
    cursor.execute(query)
    users = cursor.fetchall()
    for i in range(len(users)):
        # Check if user has any stocks
        query = f"SELECT EXISTS(SELECT * FROM `tbl_holding` WHERE `userID`='{users[i][0]}')"
        cursor.execute(query)
        test = cursor.fetchall()
        if (test[0][0] == 0):
            # If user does not have any stocks
            query = f"""UPDATE `tbl_users` SET 
            `Total_Balance`=`Current_Balance`,`Last_Updated_Time`=CURRENT_TIMESTAMP 
            WHERE `userID`='{users[i][0]}'"""
            cursor.execute(query)
            cn.commit()
        else:
            query = f"""UPDATE `tbl_users` SET 
            `Total_Balance`=`Current_Balance`+(SELECT SUM(`Current_Value`) FROM `tbl_holding`
            WHERE `userID`='{users[i][0]}'),`Last_Updated_Time`=CURRENT_TIMESTAMP 
            WHERE `userID`='{users[i][0]}'"""
            cursor.execute(query)
            cn.commit()
    closeDBConnection(cursor, cn)

while True:
    # Get current time
    d = datetime.datetime.now()
    day = datetime.datetime.today().weekday()
    if (d.hour >= 12 and d.hour < 19 and day >= 0 and day <=4):
    # Stock market is open run the code
        cn = createDBConnection()
        cursor = cn.cursor()
        cursor.execute("""SELECT * FROM `tbl_symbol_index`""")
        stocks = cursor.fetchall()
        index = 1
        for stock in stocks:
            # Change API key
            if (index==1):
                apiKey = "API_KEY"
                index += 1
            elif (index==2):
                apiKey = "API_KEY"
                index += 1
            elif (index==3):
                apiKey = "API_KEY"
                index += 1
            elif (index==4):
                apiKey = "API_KEY"
                index += 1
            elif (index==5):
                apiKey = "API_KEY"
                index += 1
            elif (index==6):
                apiKey = "API_KEY"
                index += 1
            elif (index==7):
                apiKey = "API_KEY"
                index += 1
            elif (index==8):
                apiKey = "API_KEY"
                index += 1
            elif (index==9):
                apiKey = "API_KEY"
                index += 1
            elif (index==10):
                apiKey = "API_KEY"
                index += 1
            elif (index==11):
                apiKey = "API_KEY"
                index += 1
            elif (index==12):
                apiKey = "API_KEY"
                index += 1
            elif (index==13):
                apiKey = "API_KEY"
                index += 1
            elif (index==14):
                apiKey = "API_KEY"
                index = 1
            # Save the data from the API as a variable
            text = get_data_from_api(stock[0], apiKey)
            # Load text into a json
            convertedDict = json.loads(text)
            # Save all data to local vars convert them to floats and round off to 2 decimal places
            symbol = convertedDict['Global Quote']['01. symbol']
            _open = round(float(convertedDict['Global Quote']['02. open']),2)
            high = round(float(convertedDict['Global Quote']['03. high']),2)
            low = round(float(convertedDict['Global Quote']['04. low']),2)
            price = round(float(convertedDict['Global Quote']['05. price']),2)
            previousClose = round(float(convertedDict['Global Quote']['08. previous close']),2)
            change = round(float(convertedDict['Global Quote']['09. change']),2)
            changePercent = round(float(convertedDict['Global Quote']['10. change percent'][:-1]),2)
            query = f"""INSERT INTO `tbl_api_quotes`(`Time_Stamp`, `Symbol`, `Open`, `High`, `Low`, `Price`, `Previous_Close`, `Change`, `Change_Percent`) 
            VALUES (CURRENT_TIMESTAMP, '{symbol}','{_open}', {high}, {low} , {price}, '{previousClose}', '{change}', '{changePercent}');"""
            cursor.execute(query)
            # Update all market values 
            query = f"UPDATE `tbl_holding` SET `Current_Value`=`Amount`*{price} WHERE `Symbol`='{symbol}'" 
            cursor.execute(query)
            cn.commit()
            checkForSellOrders(symbol, price)
            checkForBuyOrders(symbol, price)
            deleteZeros()
            checkLimit()
            updateTotal()
            time.sleep(6)
        closeDBConnection(cursor, cn)

    else:   
        # Stock market is not open don't run the code
        time.sleep(60)
        pass
        