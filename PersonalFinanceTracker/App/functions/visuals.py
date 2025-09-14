import seaborn as sns
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import numpy as np
import io
import base64
import pandas as pd
from pandas.tseries.offsets import MonthEnd
from sklearn.linear_model import LinearRegression
from App.functions.DAO import getDf

label_map = {
    'I': 'Income',
    'E': 'Expense',
}

required_cols = {'date', 'amount', 'category'}

def returnEmpty():
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.text(0.5, 0.5, "This user has no transactions",
            ha='center', va='center', fontsize=16, color='gray')
    ax.axis('off')
    
    buffer = io.BytesIO()
    fig.savefig(buffer, format='png', bbox_inches='tight')
    buffer.seek(0)
    graphic = base64.b64encode(buffer.getvalue()).decode('utf-8')
    plt.close(fig)
    return graphic

def balancePlot(seed):
    df = getDf(seed)
    if df is None or df.empty or not required_cols.issubset(df.columns):
        return returnEmpty()

    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['date'])

    df['category'] = df['category'].map(label_map).fillna('otro')
    df['signed_amount'] = np.where(
        df['category'].str.lower() == 'income',
        df['amount'],
        -df['amount']
    )

    df.set_index('date', inplace=True)
    daily = df['signed_amount'].resample('D').sum().cumsum()
    if daily.empty:
        return returnEmpty()

    sns.set_theme(style='whitegrid')
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.fill_between(daily.index, daily.values, step='mid',
                    color='gray', alpha=0.2, label='Daily step')
    ax.plot(daily.index, daily.values, color='green', linewidth=3,
            marker='o', markersize=4, label='Balance')

    ax.set_title('Accumulated Balance')
    ax.set_xlabel('Date')
    ax.set_ylabel('Balance')
    plt.xticks(rotation=45)
    ax.xaxis.set_major_locator(plt.MaxNLocator(8))
    ax.legend()
    plt.tight_layout()

    buffer = io.BytesIO()
    fig.savefig(buffer, format='png')
    buffer.seek(0)
    graphic = base64.b64encode(buffer.getvalue()).decode('utf-8')
    plt.close(fig)
    return graphic

def nextMonths(seed, months=12):
    df = getDf(seed)
    if df is None or df.empty or not required_cols.issubset(df.columns):
        return returnEmpty()
    
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)

    monthly = (
        df.groupby([pd.Grouper(freq='ME'), 'category'])
          ['amount']
          .sum()
          .unstack(fill_value=0)
    )
    monthly = monthly.rename(columns=label_map)

    monthly = monthly.reindex(
        columns=['Income', 'Expense'],
        fill_value=0
    )

    y_income  = monthly['Income'].values
    y_expense = monthly['Expense'].values
    X = np.arange(len(y_income)).reshape(-1, 1)

    if len(y_income) < 2:
        pred_i = np.zeros(months)
        pred_e = np.zeros(months)
    else:
        model_i = LinearRegression().fit(X, y_income)
        model_e = LinearRegression().fit(X, y_expense)
        X_future = np.arange(len(y_income), len(y_income) + months).reshape(-1, 1)
        pred_i = model_i.predict(X_future)
        pred_e = model_e.predict(X_future)

    last_month   = monthly.index.max()
    future_dates = pd.date_range(
        start=last_month + MonthEnd(1),
        periods=months,
        freq='ME'
    )

    proj = pd.DataFrame({
        'Income':  pred_i,
        'Expense': pred_e
    }, index=future_dates)

    plt.figure(figsize=(8, 4))
    plt.plot(proj.index, proj['Income'],  marker='o', color='green', label='Income')
    plt.plot(proj.index, proj['Expense'], marker='o', color='red',   label='Expense')
    plt.title(f'{months}-Month Trend Projection')
    plt.xlabel('Month')
    plt.ylabel('Projected Amount')
    plt.xticks(rotation=45)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend()

    plt.tight_layout()
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    graphic = base64.b64encode(image_png).decode('utf-8')
    buffer.close()
    plt.close()

    return graphic

def monthlyTrends(seed):
    df = getDf(seed)
    if df is None or df.empty or not required_cols.issubset(df.columns):
        return returnEmpty()

    df['month'] = pd.to_datetime(df['date']).dt.to_period('M')
    df['category'] = df['category'].map(label_map)
    
    monthly = (
        df
        .groupby(['month', 'category'])['amount']
        .sum()
        .unstack(fill_value=0) 
    )

    monthly = monthly.reindex(
        columns=['Income', 'Expense'],
        fill_value=0
    )

    fig, ax = plt.subplots(figsize=(7, 4))
    
    x = monthly.index.to_timestamp()

    ax.plot(
        x,
        monthly['Expense'],
        marker='o',
        color='red',
        linewidth=2.5,
        label='Expense'
    )
    ax.plot(
        x,
        monthly['Income'],
        marker='o',
        color='green',
        linewidth=2.5,
        label='Income'
    )

    ax.set_title('Monthly Trends', fontsize=14, pad=12)
    ax.set_xlabel('Month', fontsize=12)
    ax.set_ylabel('Amount', fontsize=12)
    ax.grid(alpha=0.3, linestyle='--')
    
    plt.xticks(rotation=45)
    ax.legend(frameon=False, fontsize=11)
    plt.tight_layout()
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    graphic = base64.b64encode(image_png).decode('utf-8')
    buffer.close()
    plt.close()

    return graphic

def categoryDistribution(seed):
    df = getDf(seed)
    if df is None or df.empty or not required_cols.issubset(df.columns):
        return returnEmpty()
    
    df['category'] = df['category'].map(label_map)
    fig, ax = plt.subplots()
    sns.barplot(data=df, x='category', y='amount', estimator=sum, errorbar=None, ax=ax)

    ax.set_title('Category Distribution')
    ax.set_xlabel('Category')
    ax.set_ylabel('Amount')
    plt.xticks(rotation=45)
    plt.tight_layout()

    buffer = io.BytesIO()
    fig.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    plt.close(fig)

    graphic = base64.b64encode(image_png).decode('utf-8')
    return graphic

if __name__ == '__main__':
    nextMonths(seed = 'AoCqo29z4CkdzL5A2yl5')