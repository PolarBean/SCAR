from .main_create import Read_Files, open_cameras, clean_data
from .NNet import build_lstm, inference_generator
import glob, numpy as np, pandas as pd
def open_folder_predict(root_folder, cams, dlc_epoch, lookback = 180, cutoff = 0.5):
    subjects = Read_Files(root_folder, cams, dlc_epoch = dlc_epoch, inference=True)
    model = build_lstm()
    for subject in subjects:
        data = open_file(subject, cams, root_folder, dlc_epoch)
        predictions = predict(data, model, lookback = lookback, batchsize = 2048, cutoff = cutoff)
        predictions.to_csv("{}/{}__{}_cutoff_lstm_preds.csv".format(\
            folder, subjects, cutoff))


def predict(data, model, lookback, batchsize = 2048, cutoff = 0.5):
        data_gen = inference_generator(data, lookback = lookback, batch_size = batchsize)
        predictions = model.predict_generator(data_gen, steps = int((len(data)-lookback)/batchsize), verbose=1)
        prepend = np.zeros(int(lookback/2))
        predictions = (predictions > cutoff).reshape(len(predictions))
        predictions = np.append(prepend, predictions)
        predictions = convert_predictions(predictions)
        return predictions

def open_file(subject, cams, folder, dlc_epoch):
        list_cams = glob.glob(folder+subject+"/*{}.h5".format(dlc_epoch))
        cameras, animals = open_cameras(list_cams, inference=True)
        processed_data = cameras.astype(np.float32)
        animals *= cams
        processed_data = clean_data(processed_data, animals)
        return processed_data

def convert_predictions(predictions):
    behave_dict = {0:"Nothing",  1:"tremors"}
    predictions = [behave_dict[i] for i in predictions]
    predictions = pd.DataFrame({"Frame":np.arange(len(predictions)),"behaviour":predictions})
    hits = predictions["behaviour"].shift()!=predictions["behaviour"]
    predictions['hits'] = predictions["behaviour"][hits]
    return predictions