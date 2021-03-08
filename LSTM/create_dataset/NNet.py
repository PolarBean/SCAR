

from tensorflow.keras import Sequential
from tensorflow.keras.layers import LSTM, Dense, InputLayer
from tensorflow.keras.optimizers import Adam
import numpy as np
def build_lstm():
    model = Sequential()
    ##Add an lstm layer which takes in 90 timesteps and returns an output for each one
    model.add(InputLayer(input_shape=(180, 342)))
    # model.add(GaussianNoise(0.1))

    model.add(LSTM(64, return_sequences=True))
    # model.add(GaussianNoise(0.2))

    model.add(LSTM(64,  return_sequences=True))
    # model.add(GaussianNoise(0.2))

    # model.add(Dropout(0.2))
    ##add a second LSTM layer
    model.add(LSTM(64, return_sequences=False))
    # model.add(Dropout(0.2))
    ##add a softmax layer with size=num_classes
    model.add(Dense(1, activation='sigmoid'))
    ##Compile our model
    model.compile(loss='binary_crossentropy', optimizer=Adam(lr=0.001), metrics=['accuracy'])
    return model



def data_gen_train(X, Y, batch, shuffle=False, lookback = 180, animals=2, shuffle_animals=True, noise=False, std=(0,0.1)):
        animal_1_index = (np.arange(0, 342/2,1).astype(int))
        animal_2_index = (np.arange(342/2,342,1).astype(int))
        X_bat = []
        Y_bat = []
        count=0
        if shuffle:
            c = list(zip(X, Y))
            random.shuffle(c)
            X, Y = zip(*c)
        while True:
            for x, y in zip(X, Y):
                if len(x)!=180:
                    continue
                if shuffle_animals:
                    rand = np.random.rand()
                    if rand>0.5:
                        index = np.concatenate((animal_1_index, animal_2_index))
                    else:
                        index = np.concatenate((animal_2_index, animal_1_index))
                    x = x[:, index]
                    if noise:
                        SD = np.random.uniform(*std)
                        gaus = np.random.normal(0,SD,x.shape)
                        x+=gaus
                X_bat.append(x)
                Y_bat.append(y)
                count+=1
                if count%batch==0:
                    yield(np.stack(X_bat), np.array(Y_bat))
                    X_bat = []
                    Y_bat = []

def inference_generator(pairwise_input,lookback=180,batch_size=90):
  batch_output=[]
  for i in range(len(pairwise_input)-lookback):
      output=np.array(pairwise_input[i:i+int(lookback)])    
      batch_output.append(output)
      if i%batch_size==0:
        batch_output=np.array(batch_output)
        batch_output=batch_output.reshape((batch_output.shape[0],batch_output.shape[1],batch_output.shape[2]))          
        yield((batch_output))
        batch_output=[]
                