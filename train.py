# -*- coding: utf-8 -*-
"""hackerearth_train.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1034ab7eibiRkQq-LdFHY9Y-tzq3FZowc
"""

#!git clone https://github.com/Calvinwilson99/HackerEarth-DeepLearning.git

# Import necessary header files 

import cv2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from keras.preprocessing.image import ImageDataGenerator
from keras.models import Sequential
from keras.layers import Dense, Conv2D, MaxPool2D, Flatten, Dropout
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from keras.applications import VGG16
from keras.models import load_model
import random

# Import the training dataset
# y is list of target values

train = pd.read_csv("dataset/train.csv")
y = train.iloc[:,1].values
y = LabelEncoder().fit_transform(y)

# Read each image and add matrix to X (list of training values)

X = []
for i in range(len(train)):
    image = cv2.imread("dataset/Train Images/" + train.Image[i])
    resized = cv2.resize(image, (224,224))
    X.append(resized)

# Split into training and test set

X = np.array(X)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state = 42)
print(X_train.dtype)

# Import VGG16 architecture to help in learning - Expects input shape to be (224,224,3) (remove output layer)
# Add our final layer for output

trained_model = VGG16(weights="imagenet", include_top=False, input_shape=(224, 224, 3), pooling='avg')
trained_model.trainable = False

model = Sequential()

model.add(trained_model)
model.add(Dropout(0.2))
model.add(Dense(4, activation = "softmax"))

# callbacks to save model weights at checkpoints, change learning rate dynamically

callbacks = [
    EarlyStopping(patience = 10, verbose = 1),
    ReduceLROnPlateau(factor = 0.1, patience = 3,
    min_lr = 0.00001, verbose = 1),
    ModelCheckpoint('models/model.h5',verbose = 1, save_best_only = True,
    save_weights_only = True)
]

# Compile the model

model.compile(optimizer = 'Adam', metrics = ['accuracy'], loss = 'sparse_categorical_crossentropy')
# Train the model

model.fit(X_train, y_train, epochs = 50, validation_data = (X_test,y_test), callbacks = callbacks)

# Load test dataset and change into expected format 

test = pd.read_csv("dataset/test.csv")

X_final = []
for i in range(len(test)):
    image = cv2.imread("dataset/Test Images/" + test.Image[i])
    resized = cv2.resize(image, (224,224))
    X_final.append(resized)

X_final = np.array(X_final)

# Load saved weights for prediction

pred_model = Sequential()

pred_model.add(trained_model)
pred_model.add(Dropout(0.2))
pred_model.add(Dense(4, activation = "softmax"))
pred_model.load_weights('models/best_model.h5')

# Predicting output

y_pred = pred_model.predict(X_final)

y_pre = [np.argmax(i) for i in y_pred]
output = ["Attire", "Decorationandsignage", "Food", "misc"]

labels = [output[i] for i in y_pre]

# Visualising the results (run cell again for different outputs)

for i in range(4):
  ind = random.randint(0, len(test))
  image = plt.imread("dataset/Test Images/" + test.Image[ind])
  print(output[y_pre[ind]])
  print(y_pre[ind])
  plt.imshow(image)
  plt.show()

submission = pd.DataFrame({ 'Image': test.Image, 'Class': labels })
print(submission.head())

submission.to_csv('submission.csv', index = False)