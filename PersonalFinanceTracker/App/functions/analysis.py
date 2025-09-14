from django.http import HttpResponse, HttpResponseBadRequest 
from django.views.decorators.http import require_GET
from django.shortcuts import render
import io
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
import os
import joblib
import datetime
import hashlib
#from App.models import Users
from App.functions.DAO import getDf

required = {'category', 'amount', 'date'}

def returnEmpty(plop = None):
    msg = "This user has no transactions" if plop is None else "This user has not enough transactions"
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.text(0.5, 0.5, msg,
            ha='center', va='center', fontsize=16, color='gray')
    ax.axis('off')
    
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return HttpResponse(buf.getvalue(), content_type='image/png')

def Balance(seed = None):
    df = getDf(seed)
    required = {'category', 'amount'}
    if df is None or df.empty or not required.issubset(df.columns):
        return 0
    dfCategory = df.groupby('category')['amount'].sum()
    return dfCategory.get('I', 0) - dfCategory.get('E',0)

@require_GET
def avgExpenses(request,dwmy, seed):
    dwmy = int(dwmy)
    if dwmy not in [0,1,2,3]: 
        return returnEmpty()

    df = getDf(seed)

    if df is None or df.empty or not required.issubset(df.columns):
        return returnEmpty()
    elif (df['category'] == 'E').sum() <= 1:
        return returnEmpty(plop=1)

    df = df[df['category'] == 'E']
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df.dropna(subset=['date'], inplace=True)

    freq = ['D','W','ME','YE'][dwmy]
    
    ser = (df.set_index('date')['amount'].resample(freq).sum().fillna(0))

    ser_nozeros = ser.replace(0, pd.NA).dropna()

    x = ser_nozeros.index
    y = ser_nozeros.values

    fig, ax = plt.subplots(figsize=(6, 3))
    ax.plot(x, y, linestyle='-', color='salmon')

    #if freq == 'D':
    #    locator = mdates.AutoDateLocator(minticks=5, maxticks=10)
    #    fmt     = mdates.DateFormatter('%Y-%m-%d')
    #elif freq == 'W':
    #    locator = mdates.WeekdayLocator(byweekday=mdates.MO, interval=6)  
    #    fmt     = mdates.DateFormatter('%Y-%m-%d')
    #else:
    locator = mdates.AutoDateLocator(minticks=4, maxticks=8)
    fmt     = mdates.DateFormatter('%Y-%m-%d')

    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(fmt)
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

    ax.set_title('Average Expense')
    ax.set_ylabel('Total')
    plt.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    return HttpResponse(buf.getvalue(), content_type='image/png')

def mostFrequent(income = False, expense = False, seed = None):
    df = getDf(seed)

    if df is None or df.empty or not required.issubset(df.columns):
        return returnEmpty()

    if income and not expense:     df = df[df['category'] == 'I']
    elif expense and not income:   df = df[df['category'] == 'E']

    top5 = df['description'].value_counts().head(5)
    if top5.empty:
        return returnEmpty(1)

    fig, ax = plt.subplots()
    top5.plot(kind='bar', ax=ax, color='#4a90e2')
    ax.set_title('Top 5 most frequent descriptions')
    ax.set_ylabel('Frequency')
    ax.set_xlabel('Description')
    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    return HttpResponse(buf.getvalue(), content_type='image/png')

def monthlySummary(seed = None):
    df = getDf(seed)

    if df is None or df.empty or not required.issubset(df.columns):
        return returnEmpty()

    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.to_period('M')
    df = df.groupby(['month', 'category'])['amount'].sum().unstack().fillna(0)
    if df.empty:
        return returnEmpty()
    
    df = df.rename(columns={'I': 'Income', 'E': 'Expense'})
    color_map = {'Income': '#1D7874', 'Expense': '#EE2E31'}

    fig, ax = plt.subplots()
    df.plot.bar(ax=ax, color=[color_map[col] for col in df.columns])
    #ax.set_title('Monthly summary')
    ax.set_ylabel('Amount')
    ax.set_xlabel('Date')
    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    return HttpResponse(buf.getvalue(), content_type='image/png')

def topSpendingDays(seed = None):
    df = getDf(seed)
    if df is None or df.empty or not required.issubset(df.columns):
        return returnEmpty()
    
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
    df['date'] = pd.to_datetime(df['date'])

    top5 = (
        df[df['category']=='E']
        .groupby(df['date'].dt.date)['amount']
        .sum()
        .nlargest(5)
        .reset_index()
        .rename(columns={'date':'Day','amount':'Amount'})
    )

    if top5.empty:
        return returnEmpty()
    
    return top5.to_html(classes='table table-striped', index=False)


def categoryPredict(desc,seed=None):
    if not isinstance(desc,str): return ''
    df = getDf(seed)
    if df is None or df.empty or not required.issubset(df.columns):
        return HttpResponse("No data", status=400)
    
    df['description'] = df['description'].astype(str).str.lower().str.strip()
    desc = desc.lower().strip()
    
    if desc.lower().strip() not in set(df['description']):
        raise ValueError("Description not in Data Frame")

    vectorizer = TfidfVectorizer(ngram_range=(1, 2))
    X = vectorizer.fit_transform(df['description'])
    y = df['category']

    model = LogisticRegression(class_weight='balanced')
    model.fit(X, y)

    new_vec = vectorizer.transform([desc])
    prediction = model.predict(new_vec)

    return prediction[0]

class ExpensePredictor:
    def __init__(self, modelFilename='model.pkl', seed=None):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.modelPath = os.path.join(BASE_DIR, modelFilename)
        self.model = None
        self.dailyDf = None
        self.seed = seed

    def getDataHash(self, df): return hashlib.md5(pd.util.hash_pandas_object(df, index=True).values).hexdigest()

    def shouldRetrain(self):
        transactions = getDf(self.seed)
        transactions = transactions[transactions['category'] == 'E']
        df = pd.DataFrame(transactions)

        current_hash = self.getDataHash(df)
        hash_path = self.modelPath.replace('.pkl', '_hash.txt')

        if os.path.exists(self.modelPath) and os.path.exists(hash_path):
            with open(hash_path, 'r') as f:
                saved_hash = f.read().strip()
            if saved_hash == current_hash:
                return False
            else:
                os.remove(self.modelPath) 
                os.remove(hash_path)      

        with open(hash_path, 'w') as f:
            f.write(current_hash)
        return True

    def trainModel(self):
        transactions = getDf(self.seed)
        transactions = transactions[transactions['category'] == 'E']
        df = pd.DataFrame(transactions)

        df['date'] = pd.to_datetime(df['date'], dayfirst=True)
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
        df = df.dropna(subset=['amount'])

        daily = df.groupby(df['date'].dt.date)['amount'].sum().reset_index()
        daily['day'] = pd.to_datetime(daily['date']).dt.day
        daily['month'] = pd.to_datetime(daily['date']).dt.month
        daily['weekday'] = pd.to_datetime(daily['date']).dt.weekday
        daily['isWeekend'] = daily['weekday'].apply(lambda x: 1 if x >= 5 else 0)

        daily = daily.sort_values('date')
        daily['prev7Avg'] = daily['amount'].rolling(window=7, min_periods=1).mean().shift(1).fillna(0)

        X = daily[['day', 'month', 'weekday', 'isWeekend', 'prev7Avg']]
        y = daily['amount']

        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X, y)

        os.makedirs(os.path.dirname(self.modelPath), exist_ok=True)
        joblib.dump(model, self.modelPath)
        self.model = model
        self.dailyDf = daily

    def loadModel(self):
        if os.path.exists(self.modelPath):
            self.model = joblib.load(self.modelPath)
        else:
            raise FileNotFoundError(f"Model not found at {self.modelPath}. Train.")

    def prev7Avg(self, target):
        if self.dailyDf is None:
            raise ValueError("Diary DataFrame not found. Train.")
        df = self.dailyDf[self.dailyDf['date'] < target]
        last7 = df.tail(7)
        return last7['amount'].mean() if not last7.empty else 0

    def predict(self, day, month):
        if self.model is None:
            self.loadModel()
        if self.shouldRetrain():
            self.trainModel()

        target = datetime.date(2025, month, day)
        weekday = target.weekday()
        isWeekend = 1 if weekday >= 5 else 0
        prev7Avg = self.prev7Avg(target)

        newInput = pd.DataFrame({
            'day': [day],
            'month': [month],
            'weekday': [weekday],
            'isWeekend': [isWeekend],
            'prev7Avg': [prev7Avg]
        })

        rawPrediction = self.model.predict(newInput)[0]
        clippedPrediction = max(0, min(rawPrediction, 10000))

        if clippedPrediction != rawPrediction:
            print(f"Advertencia: Original prediction: {rawPrediction:.2f}, Limited Prediction {clippedPrediction:.2f}")

        return round(clippedPrediction, 2)

    def evaluate_model(self):
        if self.model is None or self.dailyDf is None:
            raise ValueError("Data or model missing")

        X = self.dailyDf[['day', 'month', 'weekday', 'isWeekend', 'prev7Avg']]
        y_true = self.dailyDf['amount']
        y_pred = self.model.predict(X)
        mae = mean_absolute_error(y_true, y_pred)
        print(f"MAE: {mae:.2f}")

if __name__ == '__main__':
    seed = 'Gfj0NgmdETHy7EVJfpIH'
    predictor = ExpensePredictor(seed=seed,modelFilename=f'{seed}.pkl')
    predictor.trainModel()
    #print('day = 20', 'month = 12')
    resultado = predictor.predict(day=20, month=12)
    print(resultado)