from sklearn.tree import DecisionTreeRegressor
from sklearn.linear_model import LinearRegression
import pickle
import numpy as np

with open ('saved_model.pkl', 'rb') as file:
    data = pickle.load(file)

test = np.array([["san francisco", 8]])

le_location = data["le_location"]

linear_predict = data["linear"]

test[:,0] = le_location.transform(test[:,0])

test = test.astype(float)

predict = linear_predict.predict(test)

print(predict.flat[0])