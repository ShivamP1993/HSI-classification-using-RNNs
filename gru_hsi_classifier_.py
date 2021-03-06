import numpy as np
import tensorflow as tf
keras = tf.keras
from keras import backend as K
from keras.layers import GRU, Input, Reshape, Dense
from keras.layers import Bidirectional
from keras import regularizers
from keras.models import Model
from sklearn.metrics import confusion_matrix

# Function to perform one hot encoding of the class labels 

def my_ohc(lab_arr):
    lab_arr_unique =  np.unique(lab_arr)
    r,c = lab_arr.shape
    r_u  = lab_arr_unique.shape
    
    one_hot_enc = np.zeros((r,r_u[0]), dtype = 'float')
    
    for i in range(r):
        for j in range(r_u[0]):
            if lab_arr[i,0] == lab_arr_unique[j]:
                one_hot_enc[i,j] = 1
    
    return one_hot_enc

# Function that takes the confusion matrix as input and
# calculates the overall accuracy

def accuracy(cm):
  import numpy as np
  num_class = np.shape(cm)[0]
  n = np.sum(cm)

  P = cm/n
  ovr_acc = np.trace(P)

  return ovr_acc

train_patches = np.load('/data/train_vec.npy')
test_patches = np.load('/data/test_vec.npy')
train_labels = np.load('/data/train_labels.npy')
test_labels = np.load('/data/test_labels.npy')

train_vec = np.reshape(train_vec, [-1,17,12])
test_vec = np.reshape(test_vec, [-1,17,12])

K.clear_session()
g = tf.Graph()
k = 0

with g.as_default():

  x = Input(shape=(17,12), name='inputA') 
  
  g1 = GRU(200, activation="tanh", recurrent_activation="relu", use_bias=True, kernel_initializer="glorot_uniform", recurrent_initializer="orthogonal",
    bias_initializer="zeros", kernel_regularizer=regularizers.l2(0.01), recurrent_regularizer=regularizers.l2(0.01), name = 'L1')(x)

  d1 = Dense(16, activation="softmax")(g1)


# Initialising model
  model = Model(x, d1, name = 'clf_gru')

  # Adam with Nesterov Momentum optimizer
  optim = keras.optimizers.Adam(0.00009)
  
  # Compiling the model
  model.compile(loss='categorical_crossentropy', optimizer=optim, metrics=['accuracy'])

  for epoch in range(100):  # Number of epochs = 1000
    
    model.fit(x = train_vec, 
                  y = my_ohc(np.expand_dims(train_labels, axis = 1)),
                  epochs=1, batch_size = 64, verbose = 1)
  model.save('models/model')

# Evaluating the model on test set

K.clear_session()
g = tf.Graph()

with g.as_default():

  # Loading saved model
  model = keras.models.load_model('models/model')

  preds_final = model.predict(test_vec, verbose = 1)
  conf_final = confusion_matrix(test_labels, np.argmax(preds_final,1))
  ovr_acc_final, usr_acc, prod_acc, kappa, s_sqr = accuracies(conf_final)

print('Test accuracy is ', np.round(100*ovr_acc_final,2), '%') # Final test accuracy

