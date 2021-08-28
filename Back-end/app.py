# Import things
from flask import Flask, json , jsonify, request
import mysql.connector as mysql
from flask_cors import CORS
import datetime


def createDBConnection():        
    # Create a connection to the database
    db = mysql.connect(
        host = "SQL-SERVER",
        user = "SQLL-USERNAME",
        passwd = "SQL-PASSWORD",
        database = "SQL-DATABASE"
    )

    return db

def closeDBConnection(cursor, cn):
    cursor.close()
    cn.close()
# Create a flask app for the backend
app = Flask(__name__)


CORS(app)

@app.route('/getStocks', methods=['GET', 'POST'])
@app.route('/getStocks')
def getStocks():
    # Create a connection to DB
    cn = createDBConnection()
    cursor = cn.cursor()
    # Get variables from URL
    offset = request.args.get('offset')
    searchValue = request.args.get('searchValue')
    # Create a query with a limit and offset
    query = f"""SELECT * FROM `tbl_symbol_index`"""
    if (searchValue != ""):
        query += f" WHERE `Symbol` LIKE '%{searchValue}%'"
    query += f" LIMIT 20 OFFSET {offset}"
    # Select all stocks 
    cursor.execute(query)
    stocks = cursor.fetchall()
    stockList = []
    symbols = []
    sendBack = []
    companyNames = []
    # Create 2 lists one with every company name and one with every symbol
    for stock in stocks:
        symbol = stock[0]
        companyName = stock[1]
        companyNames.append(companyName)
        symbols.append(symbol)
    for i in range(len(symbols)):
        # Get the latest quote from the API
        query = f"SELECT * FROM `tbl_api_quotes` where Symbol='{symbols[i]}' ORDER BY `Time_Stamp` DESC LIMIT 1 "
        cursor.execute(query)
        results = cursor.fetchall()
        # Save all of the data as local variables
        _open = str(results[0][2])
        high = str(results[0][3])
        low = str(results[0][4])
        price = str(results[0][5])
        previousClose = str(results[0][6])
        # Check if stock should be red or green
        if (float(results[0][7]) > 0):
            change = float(results[0][7])
            color = 1
        else: 
            change = float(results[0][7])*-1
            color = 0
        changePercent = str(results[0][8])
        # Append all of the stocks to a list
        sendBack.append({
            "companyName": companyNames[i],
            "symbol": symbols[i],
            "open": _open,
            "high": high, 
            "low": low,
            "price": price,
            "previousClose": previousClose,
            "change": change,
            "changePercent": changePercent,
            "color": color
        })
    # Return a list of all the stocks
    closeDBConnection(cursor, cn)
    return jsonify({"data": sendBack})

@app.route('/createUser', methods=['GET', 'POST'])
def createUser():
    # Create a connection to DB
    cn = createDBConnection()
    cursor = cn.cursor()
    # Get required params from URL
    userID = request.args.get('userID')
    nickname = request.args.get('nickname')
    startingHold = 0
    startingBalance = 10000
    # Create a query string to send to sql to create the user
    query = f"""INSERT INTO `tbl_users`(`userID`, `Nickname`, `Current_Balance`, `Holding_Balance`, `Total_Balance`, `Creation_Date`) 
    VALUES ('{userID}','{nickname}', {startingBalance}, {startingHold} , {startingBalance}, CURRENT_TIMESTAMP);"""
    cursor.execute(query)
    cn.commit()
    closeDBConnection(cursor, cn)
    return jsonify({"data":"none"})

@app.route('/createOrder', methods=['GET', 'POST'])
def createOrder():
    # Create a connection to DB
    cn = createDBConnection()
    cursor = cn.cursor()
    # Get required params from URL
    orderType = request.args.get('orderType')
    userID = request.args.get('userID')
    symbol = request.args.get('symbol')
    price = float(request.args.get('price'))
    amount = float(request.args.get('amount'))
    limit = request.args.get('limit')
    if (orderType == "buy"):
        # Get balances to see if user has enough balance
        query = f"""SELECT * FROM `tbl_users` where userID='{userID}'"""
        cursor.execute(query)
        results = cursor.fetchall()
        currentBalance = float(results[0][2])
        holdingBalance = float(results[0][3])
        sumOfOrder = float(price)*float(amount)
        # Calculate if user will have enough left over balance
        leftover = currentBalance-holdingBalance-sumOfOrder
        if (leftover >= 0):
            # Create a query to create an order
            query = f"SELECT * FROM `tbl_api_quotes` WHERE `Symbol`='{symbol}' ORDER BY `Time_Stamp` DESC LIMIT 1"
            cursor.execute(query)
            results = cursor.fetchall()
            APIPrice = float(results[0][5])
            finalSumOfOrder = amount*APIPrice
            if (APIPrice<=price):
                query = f"UPDATE `tbl_users` SET `Current_Balance`=`Current_Balance`-{finalSumOfOrder}, `Last_Updated_Time`=CURRENT_TIMESTAMP WHERE `userID`='{userID}'"
                cursor.execute(query)
                query = f"""INSERT INTO `tbl_orders`
                (`order_type`, `userID`, `Symbol`, `Price`, `Amount`, `Limit`, `Order_Date_Time`, `Status`,`Transaction_Price`, `Transaction_Amount`)
                VALUES('{orderType}','{userID}','{symbol}',{price},{amount},ADDDATE(CURRENT_TIMESTAMP, interval {limit} day),CURRENT_TIMESTAMP,1,{APIPrice},{finalSumOfOrder})"""
                # Execute the query
                cursor.execute(query)
                cn.commit()
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
                    newAverageCost = (averageCost*currentlyOwnedAmount+amount*APIPrice)/(currentlyOwnedAmount+amount)
                    newAmount = currentlyOwnedAmount + amount
                    query = f"UPDATE `tbl_holding` SET `Price_Bought_At`={newAverageCost}, `Amount`={newAmount}, `Last_Updated_Date`=CURRENT_TIMESTAMP() WHERE `userID`='{userID}' AND `Symbol`='{symbol}'"
                    cursor.execute(query)
                    cn.commit()
                cn.commit()
                query = f"UPDATE `tbl_holding` SET `Current_Value`=`Amount`*{APIPrice} WHERE `Symbol`='{symbol}'" 
                cursor.execute(query)
                cn.commit()
                return jsonify({"data":"orderComplete"})
            else:
                query = f"""INSERT INTO `tbl_orders`
                (`order_type`, `userID`, `Symbol`, `Price`, `Amount`, `Limit`, `Order_Date_Time`, `Status`,`Transaction_Price`, `Transaction_Amount`)
                VALUES('{orderType}','{userID}','{symbol}',{price},{amount},ADDDATE(CURRENT_TIMESTAMP, interval {limit} day),CURRENT_TIMESTAMP,0,0,0)"""
                # Execute the query
                cursor.execute(query)
                cn.commit()
                # Create a new holding variable and change the holding balance to be that
                newHolding = holdingBalance+sumOfOrder
                query = f"""UPDATE `tbl_users` SET `Holding_Balance`={newHolding}, `Last_Updated_Time`=CURRENT_TIMESTAMP WHERE `userID`='{userID}'"""
                cursor.execute(query)
                cn.commit()
                closeDBConnection(cursor, cn)
                return jsonify({"data":"Created"})
        else:
            closeDBConnection(cursor, cn)
            return jsonify({"data":"insufficientFunds"})
    if (orderType == "sell"):
        # Create a sell order in `tbl_orders`
        query = f"SELECT `Amount` from `tbl_holding` WHERE `userID`='{userID}' and `symbol`='{symbol}'"
        cursor.execute(query)
        results = cursor.fetchall()
        avaliable = results[0][0]
        if (int(amount)>int(avaliable)):
            return jsonify({'data':int(avaliable)})
        else:
            query = f"""INSERT INTO `tbl_orders`(`order_type`, `userID`, `Symbol`, `Price`, `Amount`, `Limit`, `Order_Date_Time`, `Status`,`Transaction_Price`, `Transaction_Amount`)
            VALUES('{orderType}','{userID}','{symbol}',{price},{amount},ADDDATE(CURRENT_TIMESTAMP, interval {limit} day),CURRENT_TIMESTAMP,0,0,0)"""
            # Execute the query
            cursor.execute(query)
            cn.commit()
            query = f"UPDATE `tbl_holding` SET `Amount`=`Amount`,`On_Hold`=`On_Hold`+{amount} WHERE `userID`='{userID}' AND `Symbol`='{symbol}'"
            cursor.execute(query)
            cn.commit()
        closeDBConnection(cursor, cn)
        return jsonify({"data":"Created"})

@app.route('/addToWatchlist', methods=['GET', 'POST'])
def addToWatchlist():
    # Create a connection to DB
    cn = createDBConnection()
    cursor = cn.cursor()
    # Get required params from URL
    userID = request.args.get('userID')
    symbol = request.args.get('symbol')
    # Check if user already has stock in watchlist
    query = f"SELECT EXISTS(SELECT * FROM `tbl_watchlist` WHERE `userID`='{userID}' and `symbol`='{symbol}');"
    cursor.execute(query)
    result = cursor.fetchall()
    result = result[0][0]
    # If user already have the stock in his watchlist
    if (result==1):
        closeDBConnection(cursor, cn)
        return jsonify({"data":"notAdded"})
    else:
        # Create a query to add stock to watchlist
        query = f"""INSERT INTO `tbl_watchlist`
        (`userID`, `Symbol`)
        VALUES('{userID}','{symbol}')"""
        cursor.execute(query)
        cn.commit()
        closeDBConnection(cursor, cn)
        return jsonify({"data":"added"})

@app.route('/removeFromWatchlist', methods=['GET', 'POST'])
def removeFromWatchlist():
    # Create a connection to DB
    cn = createDBConnection()
    cursor = cn.cursor()
    # Get required params from URL
    userID = request.args.get('userID')
    symbol = request.args.get('symbol')
    # Create a query to remove stock from watchlist
    query = f"""DELETE FROM `tbl_watchlist` WHERE `userID`='{userID}' and `symbol`='{symbol}'"""
    cursor.execute(query)
    cn.commit()
    closeDBConnection(cursor, cn)

    return jsonify({"data":"removed"})

@app.route('/getWatchlist', methods=['GET', 'POST'])
def getWatchlist():
    # Create a connection to DB
    cn = createDBConnection()
    cursor = cn.cursor()
    # Get required params from URL
    userID = request.args.get('userID')
    # Create a query to get all watchlisted stocks
    query = f"""SELECT * FROM `tbl_watchlist` where userID='{userID}'"""
    cursor.execute(query)
    # Fetch all the stocks and add them to a list called symbols
    results = cursor.fetchall()
    symbols = []
    for stock in results:
        symbol = stock[1]
        symbols.append(symbol)
    stocks = []
    # Loop through every symbol and get the data and add to a list
    for i in range(len(symbols)):
        # Create the query
        query = f"SELECT * FROM `tbl_api_quotes` where Symbol='{symbols[i]}' ORDER BY `Time_Stamp` DESC LIMIT 1 "
        cursor.execute(query)
        results = cursor.fetchall()
        # Save all data to local variables
        _open = str(results[0][2])
        high = str(results[0][3])
        low = str(results[0][4])
        price = str(results[0][5])
        previousClose = str(results[0][6])
        # Check if stock is + or - today
        if (float(results[0][7]) > 0):
            change = float(results[0][7])
            color = 1
        else: 
            change = float(results[0][7])*-1
            color = 0
        changePercent = str(results[0][8])
        # Add all of the stocks in watchlist into array
        stocks.append({
            "symbol": symbols[i],
            "open": _open,
            "high": high, 
            "low": low,
            "price": price,
            "previousClose": previousClose,
            "change": change,
            "changePercent": changePercent,
            "color": color
        })
    # If user does not have any stocks in watchlist
    closeDBConnection(cursor, cn)
    if (len(stocks) == 0):
        return jsonify({"data": "none"})
    else:
        return jsonify({"data": stocks})

@app.route('/getBalance', methods=['GET', 'POST'])
def getBalance():
    # Create a connection to DB
    cn = createDBConnection()
    cursor = cn.cursor()
    # Get required params from URL
    userID = request.args.get('userID')
    # Create a query to get all the balances where the userID matches the inputted record
    data = {}
    balances = []
    query = f"""SELECT * FROM `tbl_users` where userID='{userID}'"""
    cursor.execute(query)
    results = cursor.fetchall()
    currentBalance = float(results[0][2])
    holdingBalance = float(results[0][3])
    totalBalance = float(results[0][4])
    balances.append({'currentBalance': currentBalance})
    balances.append({'holdingBalance': holdingBalance})
    balances.append({'totalBalance': totalBalance})
    closeDBConnection(cursor, cn)
    return jsonify({"data":balances})

@app.route('/getPortfolio', methods=['GET', 'POST'])
def getPortfolio():
    # Create a connection to DB
    cn = createDBConnection()
    cursor = cn.cursor()
    # Get required params from URL
    userID = request.args.get('userID')
    query = f"SELECT * FROM `tbl_holding` WHERE `userID`='{userID}'"
    cursor.execute(query)
    # Fetch all the stocks and add them to a list called symbols
    results = cursor.fetchall()
    sendBack = []
    a = len(results)
    if (a>0):
        for result in results:
            # Get company name
            query = f"SELECT * FROM `tbl_symbol_index` where Symbol='{result[1]}'"
            cursor.execute(query)
            results1 = cursor.fetchall()
            companyName = str(results1[0][1])
            # Get current price
            query = f"SELECT * FROM `tbl_api_quotes` where Symbol='{result[1]}' ORDER BY `Time_Stamp` DESC LIMIT 1 "
            cursor.execute(query)
            results2 = cursor.fetchall()
            price = float(results2[0][5])
            # Save all data to local variables and append them to an array
            symbol = str(result[1])
            priceBoughtAt = float(result[2])
            amount = int(result[3])
            onHold = int(result[4])
            marketValue = float(result[6])
            netPL = marketValue-(amount*priceBoughtAt)
            if (netPL<0):
                netPL *= -1
            netPLPercent = marketValue/(amount*priceBoughtAt)*100-100
            if (priceBoughtAt*amount > marketValue):
                color = 0
            else:
                color = 1
            sendBack.append({
                'companyName': companyName,
                'symbol': symbol, 
                'priceBoughtAt': priceBoughtAt,
                'amount': amount, 
                'onHold': onHold,
                'currentPrice': price,
                'marketValue': marketValue, 
                'netPLPercent': round(netPLPercent,2),
                'netPL': round(netPL,2),
                'color': color
            })
        data = {}
        balances = []
        query = f"""SELECT * FROM `tbl_users` where userID='{userID}'"""
        cursor.execute(query)
        results = cursor.fetchall()
        currentBalance = float(results[0][2])-float(results[0][3])
        holdingBalance = float(results[0][3])
        totalBalance = float(results[0][4])
        balances.append({'currentBalance': currentBalance})
        balances.append({'holdingBalance': holdingBalance})
        balances.append({'totalBalance': totalBalance})
        closeDBConnection(cursor, cn)
        if (len(sendBack)==0):
            return jsonify({'data': 'none',
                        'balances': balances})
        else:
            return jsonify({'data': sendBack,
                        'balances': balances})
    else:
        balances = []
        query = f"""SELECT * FROM `tbl_users` where userID='{userID}'"""
        cursor.execute(query)
        results = cursor.fetchall()
        currentBalance = float(results[0][2])-float(results[0][3])
        holdingBalance = float(results[0][3])
        totalBalance = float(results[0][4])
        balances.append({'currentBalance': currentBalance})
        balances.append({'holdingBalance': holdingBalance})
        balances.append({'totalBalance': totalBalance})
        closeDBConnection(cursor, cn)
        return jsonify({'data': 'none',
                        'balances': balances})


@app.route('/getTransactions', methods=['GET', 'POST'])
def getTransactions():
    # Create a connection to DB
    cn = createDBConnection()
    cursor = cn.cursor()
    # Get needed params
    userID = request.args.get('userID')
    active = []
    cancelled = []
    completed = []
    query = f"SELECT * FROM `tbl_orders` WHERE `userID`='{userID}'"
    cursor.execute(query)
    transactions = cursor.fetchall()
    # Loop through all transactions
    for transaction in transactions:
        transactionID = int(transaction[0])
        orderType = str(transaction[1])
        symbol = str(transaction[3])
        wantedPrice = float(transaction[4])
        amount = float(transaction[5])
        limit = str(transaction[6])
        orderDate = str(transaction[7])
        status = int(transaction[8])
        transactionPrice = float(transaction[10])
        transactionAmount = float(transaction[11])
        if (status==0):
            active.append({
                "id": transactionID,
                "orderType": orderType, 
                "symbol": symbol, 
                "wantedPrice": wantedPrice, 
                "amount": amount, 
                "limit": limit,
                "orderDate": orderDate,
                "status": status,
                "transactionPrice": transactionPrice,
                "transactionAmount": transactionAmount
            })
        if (status==1):
            completed.append({
                "id": transactionID,
                "orderType": orderType, 
                "symbol": symbol, 
                "wantedPrice": wantedPrice, 
                "amount": amount, 
                "limit": limit,
                "orderDate": orderDate,
                "status": status,
                "transactionPrice": transactionPrice,
                "transactionAmount": transactionAmount
            })
        if (status==9):
            cancelled.append({
                "id": transactionID,
                "orderType": orderType, 
                "symbol": symbol, 
                "wantedPrice": wantedPrice, 
                "amount": amount, 
                "limit": limit,
                "orderDate": orderDate,
                "status": status,
                "transactionPrice": transactionPrice,
                "transactionAmount": transactionAmount
            })
    if (len(active)==0):
        active = 'none'
    if (len(completed)==0):
        completed = 'none'
    if (len(cancelled)==0):
        cancelled = 'none'
    closeDBConnection(cursor, cn)
    return jsonify({'active': active,
                    'completed': completed,
                    'cancelled': cancelled
                    })

@app.route('/cancelTransaction', methods=['GET', 'POST'])
def cancelTransaction():
    # Create a connection to DB
    cn = createDBConnection()
    cursor = cn.cursor()
    orderType = request.args.get('orderType')
    userID = request.args.get('userID')
    symbol = request.args.get('symbol')
    wantedPrice = float(request.args.get('wantedPrice'))
    amount = float(request.args.get('amount'))
    orderID = request.args.get('ID') 
    if (orderType=='buy'):
        removeBalance = wantedPrice*amount
        query = f"UPDATE `tbl_users` SET `Holding_Balance`=`Holding_Balance`-{removeBalance} WHERE `userID`='{userID}'"
        cursor.execute(query)
        cn.commit()
    if (orderType=='sell'):
        query = f"UPDATE `tbl_holding` SET `On_Hold`=`On_Hold`-{amount} WHERE `userID`='{userID}' AND `Symbol`='{symbol}'"
        cursor.execute(query)
        cn.commit()
    query = f"UPDATE `tbl_orders` SET `Status`=9, `Last_Updated_Time`=CURRENT_TIMESTAMP WHERE `id`={orderID}"
    cursor.execute(query)
    cn.commit()
    closeDBConnection(cursor, cn)
    return jsonify({'data':'none'})

@app.route('/getLeaderboard', methods=['GET', 'POST'])
def getLeaderboard():
    # Create a connection to DB
    cn = createDBConnection()
    cursor = cn.cursor()
    userID = request.args.get('userID')
    query = f"SELECT `Nickname`, `Total_Balance` FROM `tbl_users` ORDER BY `Total_Balance` DESC LIMIT 10"
    cursor.execute(query)
    results = cursor.fetchall()
    topTen = []
    for result in results:
        nickname = result[0]
        money = result[1]
        topTen.append({
            "nickname": str(nickname),
            "money": float(money)
            })
    query = f"""SELECT
    COUNT(*) AS rank
    FROM `tbl_users`
    WHERE `Total_Balance`>=(SELECT `Total_Balance` FROM `tbl_users` WHERE `userID`='{userID}')"""
    cursor.execute(query)
    rank = cursor.fetchall()
    if (rank[0][0] > 10):
        user = []
        query = f"SELECT `Nickname`,`Total_Balance` FROM `tbl_users` WHERE `userID`='{userID}'"
        cursor.execute(query)
        results = cursor.fetchall()
        user.append({
            "nickname": str(results[0][0]),
            "money": float(results[0][1]), 
            "level": rank[0][0]
        })
    else:
        user = "top10"
    closeDBConnection(cursor, cn)
    return jsonify({
                'topTen': topTen,
                'user': user
                })

@app.route('/isOpen', methods=['GET', 'POST'])
def isOpen():
    d = datetime.datetime.now()
    day = datetime.datetime.today().weekday()
    if (d.hour >= 9 and d.hour < 17 and day >= 0 and day <=4):
        return jsonify({'data': 'open'})
    else:
        return jsonify({'data': 'closed'})
if __name__== '__main__':
    app.run(debug=True)
