from sklearn.linear_model import LinearRegression 
import numpy as np 
 
def predict_expense(df): 
 
    X = np.array(range(len(df))).reshape(-1, 1) 
    y = df['Amount'].values 
 
    model = LinearRegression() 
    model.fit(X, y) 
 
    future = model.predict([[len(df)]]) 
 
    return round(future[0], 2)
