# -*- coding: utf-8 -*-
"""Time Series-Submission.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1I0_Sdt4nbEO_oqWSCyimiJA2m4lbxvYK

# **Membuat Model Machine Learning dengan Data Time Series**
- Nama: Muhammad Hafiz
- Email: mhdhfz391@gmail.com
- Id Dicoding: mhdhfzz

## **Menyiapkan semua library yang dibutuhkan**
"""

#dataframe
import pandas as pd
import numpy as np
#split data
from sklearn.model_selection import train_test_split
#preprocessing dan layer
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM,Dense,Bidirectional,Dropout
#visualisasi plot
import matplotlib.pyplot as plt

"""## **Membaca dataset**"""

!wget --no-check-certificate 'https://docs.google.com/uc?export=download&id=149nFyUXIkAaGjGW0SawGunSQyFdgJSIF' -O Metro_Interstate_Traffic_Volume.csv

#import data ke variabel untuk dibaca
df = pd.read_csv('Metro_Interstate_Traffic_Volume.csv')

#cek 5 data teratas
df.head()

df.info()

df = df[["date_time","temp"]]

df["date_time"] = pd.to_datetime(df["date_time"])
df.info()

df['just_date'] = df['date_time'].dt.date

DF=df.drop('date_time',axis=1)
DF.set_index('just_date', inplace= True)
DF.head()

date = df['just_date'].values
temp = df['temp'].values

plt.figure(figsize=(12,5))
plt.plot(DF)
plt.xlabel('Date')
plt.ylabel('temperature')
plt.show()

"""## **Splitting Data**"""

#Split Dataset
x_train, x_test, y_train, y_test = train_test_split(temp, date, test_size = 0.2, random_state = 0 , shuffle=False)

#Total data train (80%) dan validation (20%)
print('Total Data Train : ',len(x_train))
print('Total Data Validation : ',len(x_test))

"""## **Pemodelan Sequential**"""

#Merubah data untuk dapat diterima model
def windowed_dataset(series, window_size, batch_size, shuffle_buffer):
  series = tf.expand_dims(series, axis=-1)
  ds = tf.data.Dataset.from_tensor_slices(series)
  ds = ds.window(window_size + 1, shift=1, drop_remainder = True)
  ds = ds.flat_map(lambda w: w.batch(window_size + 1))
  ds = ds.shuffle(shuffle_buffer)
  ds = ds.map(lambda w: (w[:-1], w[-1:]))
  return ds.batch(batch_size).prefetch(1)

#Pemodelan Sequential

data_x_train = windowed_dataset(x_train, window_size=60, batch_size=100, shuffle_buffer=1000)
data_x_test = windowed_dataset(x_test, window_size=60, batch_size=100, shuffle_buffer=1000)

model = Sequential([
    LSTM(64, return_sequences = True, input_shape=(100, 1)),
    Dropout(0.1),
    LSTM(64, return_sequences = True),
    Dropout(0.1),
    Bidirectional(LSTM(64)),
    Dropout(0.1),
    Dense(8, activation = 'relu'),
    Dense(1)
])

#Menghitung nilai 10% MAE untuk penerapan callback

x = (df['temp'].max() - df['temp'].min()) * 10/100
print(x)

#Penggunaan Callback <10% MAE

class myCallback(tf.keras.callbacks.Callback):
  def on_epoch_end(self, epoch, logs={}):
    if(logs.get('mae')<x and logs.get('val_mae')<x):
      print("\nMAE dari model < 10% skala data")
      self.model.stop_training = True
callbacks = myCallback()

#Penggunaan learning rate SGD untuk optimizer
tf.keras.backend.set_floatx('float64')
optimizer = tf.keras.optimizers.SGD(learning_rate=1.0000e-04, momentum=0.9)

model.compile(loss=tf.keras.losses.Huber(),
              optimizer=optimizer,
              metrics=["mae"])

history = model.fit(data_x_train ,epochs=500, validation_data=data_x_test, callbacks=[callbacks])

"""## **Grafik**"""

plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('Model Loss')
plt.ylabel('Loss')
plt.xlabel('Epochs')
plt.legend(['train', 'test'], loc = 'upper right')
plt.show()

plt.plot(history.history['mae'])
plt.plot(history.history['val_mae'])
plt.title('Model Mae')
plt.ylabel('Mae')
plt.xlabel('Epoch')
plt.legend(['train', 'test'], loc='upper right')
plt.show()