# -*- coding: utf-8 -*-
"""
Automatically generated by Colaboratory.
"""
from google.colab import drive
drive.mount('/content/drive')

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re

"""After my first look on the data i standardize all *None* values and the date *1/1/1990* to missing values Pandas can recognize.
For me it seems the date 1/1/1990 where a manual created placeholder for a missing date,that's why i changed it aswell.
"""

missing_values = ["n/a", "na", "--","None","1/1/1900"]
data = pd.read_csv("/content/drive/My Drive/31-M29/credit_data.csv",index_col=0,na_values = missing_values)
print("Number of rows: {0:,}".format(len(data)))
print("Number of columns: {0:,}".format(len(data.columns)))

display(data.head())
print('\n Data Types:')
print(data.dtypes)

"""I change our outcome variable *paid in time* to 1 for Yes and 0 for No and NaN as NaN.Than i assign the outcome variable to y as a Series and spreat it out of our feature DataFrame."""

data['Paid in time'].value_counts(dropna=False)

data['Paid in time'] = data['Paid in time'].apply(lambda x: 1 if x=='YES' else (0 if x=='NO' else 'NaN'))
y = data['Paid in time']
data = data.drop('Paid in time',1)

data.head(50)

y.value_counts(dropna=False)

"""**NOTE:** I keep the missing values of the target variable for now.We could later impute them using a model prediction iteself.Otherwise we could remove them.

**checking for duplicated rows**
"""

data.duplicated().sum()

"""**Transforming datetype**"""

data['Loan Start Date'] = pd.to_datetime(data['Loan Start Date'])
data['Loan Due Date'] = pd.to_datetime(data['Loan Due Date'])
data['Client Birthdate'] = pd.to_datetime(data['Client Birthdate'])

"""**checking for wrong dates(if Loan Due Date is before Loan Start Date) and drop these**"""

wrong_date = data['Loan Start Date'] > data['Loan Due Date']

wrong_date.sum()

data[wrong_date]

data = data.drop(data[wrong_date].index)

"""**Checking for missing values**"""

data.isna().sum()

"""**Diving deeper into the missing values**"""

data['Client Birthdate'].isna().sum() / len(data)

"""We have 198 clients with a initiallie date of 1/1/1990 which i standardized to NaN.For later useig and predictions and the fact that there represent only a few of the observations,i decided to drop these rows."""

data.shape

wrong_birthday = data['Client Birthdate'].isna()
data = data.drop(data[wrong_birthday].index)
data.shape

"""We also have missing values in *Client Monthly Income*.Therefore i inspect the numeric features and get a better inside of the data.

**Inspecting the numeric features of the dataset.**
"""

def color(val):
    color = "green"
    if val > 0:
        color = "lightcoral"
    if val > 10:
        color = "red"
    return 'background-color: %s' % color

A = data.describe().transpose()
B = pd.DataFrame(data.isna().sum()).rename(columns={0:"num missing"}, inplace=False)
B["pct missing in data"] = B["num missing"] / len(data) * 100

C = A.join(B, how="left")

display(C[["count", "min", "25%", "mean", "50%", "75%", "max", "std", "pct missing in data"]].round(3).style.applymap(color, subset=["pct missing in data"]))

"""We have 8.785% missing values in the column *Client Monthly Income*.Also there are negative values.First i check how many negative values we have and display more inforamtions about that feature.


"""

negativeincome = data['Client Monthly Income'] < 0

negativeincome.sum()

data[negativeincome]

"""We have 135 negative values in our column.I can't find any reason why there are negative.For further useig and without having more informations, i drop the clients with negative income."""

data = data.drop(data[negativeincome].index)

data.shape

"""Inspecting the missing values in *Client Monthly Income* and fill the missing values with the mean, based on the Client Status."""

incomemissing = data['Client Monthly Income'].isna()
data[incomemissing].head(50)

data[incomemissing].shape

"""Before i fill the missing values i fill the missing values for Status to: **no status** to get the mean for these clients aswell."""

data['Client Status'].fillna('no status',inplace = True)

data['Client Status'].head(50)

data.groupby('Client Status').describe().round(2)

data.loc[(data['Client Monthly Income'].isna()) & (data['Client Status'] == 'female : divorced/separated/married'), ['Client Monthly Income']] = 3837.05
data.loc[(data['Client Monthly Income'].isna()) & (data['Client Status'] == 'female : single'), ['Client Monthly Income']] = 3895.26
data.loc[(data['Client Monthly Income'].isna()) & (data['Client Status'] == 'male : divorced/separated'), ['Client Monthly Income']] = 4003.46
data.loc[(data['Client Monthly Income'].isna()) & (data['Client Status'] == 'male : married/widowed'), ['Client Monthly Income']] = 3811.12
data.loc[(data['Client Monthly Income'].isna()) & (data['Client Status'] == 'male : single'), ['Client Monthly Income']] = 3748.95
data.loc[(data['Client Monthly Income'].isna()) & (data['Client Status'] == 'no status'), ['Client Monthly Income']] = 3972.85

data.isna().sum()

"""**Loan Purpose** and **Client Status** are 
probably Missing not at Random (MNAR).Clients didn't want to share these informations due private reasons. Like i filled the missing values for *Client Status*, i fill the missing values in *Loan purpose* with "no purpose".We can later calcualte if the purpose is correlated with **Paid in time** .

Histograms to get a overview about the distribution of the data.
"""

# Commented out IPython magic to ensure Python compatibility.
# %matplotlib inline
import matplotlib.pyplot as plt

def plot_histogram(x):
  plt.hist(x, color='gray',alpha=0.5)
  plt.title("Histogram of '{var_name}'".format(var_name=x.name))
  plt.xlabel("Value")
  plt.ylabel("Frequency")
  plt.show()

plot_histogram(data['Client Monthly Income'])

"""Histograms to get a overview about the distribution of the features by DV categories."""

def plot_histogram_dv(x,y):
  plt.figure(figsize=(25, 4))
  plt.hist(list(x[y==0]), alpha=0.5, label='DV=0',color='green')
  plt.hist(list(x[y==1]), alpha=0.5, label='DV=1',color='red')
  plt.title("Histogram of '{var_name}' by DV Category".format(var_name=x.name))
  plt.xlabel("Value")
  plt.ylabel("Frequency")
  plt.legend(loc='upper right')
  plt.rc('xtick', labelsize=13) 
  plt.show()

plot_histogram_dv(data['Loan Purpose'],y)

"""**Isolating the year of the *Loan Start Date* and *Loan Due Date**."""

data['started year'] = pd.DatetimeIndex(data['Loan Start Date']).year
data['due year'] = pd.DatetimeIndex(data['Loan Due Date']).year

"""**Adding the Loan Duration in years and days to the dataframe**"""

data['Loan Duration in years'] = data['due year'] - data['started year']

data['Loan Duration in days'] = data['Loan Due Date'] - data['Loan Start Date']

data.head()

"""**Seperate the gender and client relationship status.Also adding a new feature *age* of the Client.**"""

data.loc[(data['Client Status'].str.match("female",na = False)),'Gender'] = 'female'
data.loc[(data['Client Status'].str.match("male",na = False)),'Gender'] = 'male'

data['Client Status'].replace('\w*\s\:\s','',regex = True,inplace = True)

data['age'] = (pd.datetime.now() - data['Client Birthdate']).astype('timedelta64[Y]')
data['age'] = data['age'].astype('Int64')

data.head()

"""**Extract the first two characters of the IBAN and add it two a new column.With that and a precreated dictonary, i create a feature with the country code and name.**"""

country =  {'FR': 'France','ES':'Spain','CH':'Switzerland','DE':'Germany','BE':'Belgium'}

data['Country code'] = data['Client IBAN'].apply(lambda x: x[:2])

data['Country'] = data['Country code'].map(country)

"""**Function to dummy all the categorical variables used for modeling**"""

todummy_list = ['Loan Purpose','Client Status','Country','Gender']

def dummy_data(data,todummy_list):
  for x in todummy_list:
    dummies = pd.get_dummies(data[x], prefix=x,dummy_na=True,drop_first=True)
    data = data.drop(x, 1)
    data = pd.concat([data, dummies], axis=1)
  return data

data = dummy_data(data,todummy_list)
data.head(5)

"""**Task 3:** Describe the model training and evaluation process in 3-5 sentences. What is the input and the output of the model? Is this a classification or a regression task? How do you evaluate the performance of the model?

We need to split our dataset into  train and  test sets.We built a model on the train set and actually do predictions on the test set.I would recommend K-Fold Cross-Validation ,because we have a small dataset.
Our output,the target variable for prediction is **paid in time**. Our inputs(Predictors)are independant variables (features).
This is a (binary) classification task(supervised learning),we want to determine the probability that an observation belongs to one of two(YES(1)/NO(0)) groups.
"""
