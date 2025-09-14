from App.functions.connection import *
from datetime import datetime
import pandas as pd
class TransactionsDAO:

    def __init__(self,seed=None):
        self.seed = seed 

    def baseSelect(self):
        return (
            "SELECT id, description, category, amount, date "
            "FROM app_transactions WHERE userSeed = %s"
        )

    def build_select(
        self,
        category=None,
        min_amount=None, max_amount=None,
        start_date=None, end_date=None,
        order_by=None  # Tuples: [("amount", "ASC"), ("date", "DESC")]
    ):
        query = self.baseSelect()
        filters = []

        if category in ("Income", "Expense"): filters.append(f"category = '{category}'")

        if min_amount is not None: filters.append(f"amount >= {min_amount}")
        if max_amount is not None: filters.append(f"amount <= {max_amount}")

        if start_date is not None: filters.append(f"date >= '{start_date}'")
        if end_date is not None: filters.append(f"date <= '{end_date}'")

        # WHERE
        if filters: query += " WHERE " + " AND ".join(filters)

        # ORDER BY 
        if order_by:
            order = [f"{field} {direction.upper()}" for field, direction in order_by]
            query += " ORDER BY " + ", ".join(order)

        return query, [self.seed]
    
    def fetchTransactions(self, **kwargs):
        query, params = self.build_select(**kwargs)
        try:
            con = Connection.getConnection()
            cursor = con.cursor(dictionary=True)
            cursor.execute(query, params)
            results = cursor.fetchall()
        except Exception as e:
            print(f'Error: {e}')
            results = []
        finally:
            if con:
                cursor.close()
                Connection.closeConnection(con)
        return results
    

    
#    @classmethod
#    def Update(cls, data = None):
#        con = None
#        try:
#            con = Connection.getConnection()
#            cursor = con.cursor()
#            i = int(input('Insert ID: ')) if data is None else data.id
#            d = input('Insert Description: ') if data is None else data.description
#            c = data.category if data is not None else input("Insert Category ['Income','Expense']: ")
#            a = input("Insert Amount: ") if data is None else data.amount
#            date = input("Insert Date: ") if data is None else data.date
#            values = (d,c,float(a),datetime.strptime(date),i)
#            cursor.execute(cls.UPDATE,values)
#            if data is None: data = Transactions(id=i,description=d,category=c,amount=a,date=date)
#            print(f'Transaction modified!: \n{data}')
#            con.commit()
#        except Exception as e:
#            print(f'Error: {e}') 
#        finally: 
#            if con is not None: 
#                cursor.close()
#                Connection.closeConnection(con) 
#
#    @classmethod
#    def Delete(cls):
#        try:
#            con = Connection.getConnection()
#            cursor = con.cursor()
#            i = int(input('Insert ID: '))
#            values = (i,)
#            cursor.execute(cls.DELETE,values)
#            print('Transaction Deleted!')
#            con.commit()
#
#        except Exception as e:
#            print(f'Error: {e}') 
#        finally: 
#            if con is not None: 
#                cursor.close()
#                Connection.closeConnection(con) 


def getDf(seed): 
        dao = TransactionsDAO(seed)
        raw_data = dao.fetchTransactions()
        df = pd.DataFrame(raw_data)
        df = df.drop(columns=[col for col in df.columns if col.startswith('_')], errors='ignore')
        return df

def insert_transaction(data, seed):
    query = (
    "INSERT INTO app_transactions (description, category, amount, date, created, updated, userSeed) "
    "VALUES (%s, %s, %s, %s, %s, %s, %s)"
    )
    with Connection.getConnection() as conn: 
        with conn.cursor() as cursor:
            values = [data['description'], data['category'], data['amount'], data['date'],data['created'], datetime.today(), seed]
            print('transaccion insertada')
            cursor.execute(query, values)
            conn.commit()

def update_transaction(data,seed):
    query = (
        "UPDATE app_transactions SET description = %s, category = %s, amount = %s, date = %s, updated = %s"
        "WHERE id = %s AND userSeed = %s"
    )
    with Connection.getConnection() as conn:
        with conn.cursor() as cursor:
            values = [data['description'],data['category'],data['amount'], data['date'], datetime.today(), data['Id'], seed]
            cursor.execute(query, values)
            conn.commit()

def delete_transaction(data,seed):
    try:
        query = "DELETE FROM app_transactions WHERE id = %s AND userSeed = %s"
        values = [int(data['Id']), str(seed)]
        conn = Connection.getConnection()
        cursor = conn.cursor()
        cursor.execute(query, values)
        conn.commit()
        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Error al eliminar transacción: {e}")


if __name__ == '__main__':
    print(getDf('Gfj0NgmdETHy7EVJfpIH'))