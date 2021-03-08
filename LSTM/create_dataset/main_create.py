# def File_Reader(folder, look_back, cams, inference, multi, dlc_epoch = '')
##main script
    ##hardcoded resolution for now
 
    # subjects = Read_Files(folder, cams, inference, dlc_epoch)
    # cameras, labels = combine_animal_cameras_labels(subjects, folder, cams, inference, dlc_epoch)
import os
import numpy as np
import pandas as pd
from .dataset_utilities import check_validity, preprocess_Coords
from.math.vectorise_EDM import vectorised_EDM_BAD_PLEASE_FIX
def combine_animal_cameras_labels(subjects, folder, cams, dlc_epoch):
    has_run = False
    labels, label_lens, indexes = open_labels(subjects, folder)
    for subject, label_len in zip(subjects, label_lens):     
        list_cams = glob.glob(folder+subject+"/*{}.h5".format(dlc_epoch))
        # all_cams.extend(list_cams)
        cameras, animals = open_cameras(list_cams, label_len, inference)
        if has_run:
            all_cams = np.concatenate(cameras, axis=1)
        else:
            all_cams = cameras
            has_run = True
    processed_data = all_cams.astype(np.float32)
    animals *= cams
    processed_data = clean_data(processed_data)
    processed_data, labels = add_lookback(processed_data, labels, indexes)
    return processed_data, labels


def Read_Files(folder, cams, inference, dlc_epoch):
    subjects = [i for i in os.listdir(folder) if os.path.isdir(folder+i)]
    subjects = [i for i in subjects if check_validity(folder+i, cams=cams, inference = inference, dlc_epoch=dlc_epoch)]
    print("found {} valid subjects. \n IDs are: {}".format(len(subjects), subjects))
    return subjects

def add_lookback(processed_data, labels, indexes, look_back):
        processed_data = [processed_data[i-int(look_back/2):i+int(look_back/2)] for i in tqdm(indexes)]
        labels = labels.iloc[indexes]
        return processed_data, labels

def multi_animal_vectorise(raw_input, num_animals):
    bodyparts = int(raw_input.shape[1] / num_animals)
    print(bodyparts)
    animals = [vectorised_EDM_BAD_PLEASE_FIX(raw_input[:, (animal-1) * bodyparts : animal*bodyparts], batchsize=2048) for animal in range(1, num_animals+1)]
    return np.concatenate(animals, axis=1)


def clean_data(processed_data, animals):
    Xmax = 270
    Ymax = 360
    ##here we make sure no values are greater than the maximum possible
    ##I used the max of X and Y as there was a bit of weird behaviour
    processed_data[processed_data>Ymax] = Ymax
    ##DLC should not predict values less than zero
    processed_data[processed_data<0] = 0
    means = np.nanmean(processed_data, axis=1)
    means = np.nan_to_num(means, nan=0)
    mask = np.isnan(processed_data)
    ##convert missing values to the mean of the animal
    processed_data[mask] = (means[:, None] * mask)[mask]
    print("animals: {}".format(animals))
    processed_data = multi_animal_vectorise(processed_data, animals)
    ##I dont think this should be here but the lstm is already trained for now
    processed_data[processed_data>Ymax] = Ymax
    ##limit the memory by taking a still massive sample
    idx = np.random.randint(len(processed_data), size=20000)
    mean =  np.mean(processed_data[idx], dtype = np.float64)
    std  =  np.std(processed_data[idx], dtype = np.float64)
    processed_data  = (processed_data-mean)/std
    return processed_data

def open_labels(subjects, folder):
    label_lens = []
    labels=pd.DataFrame()
    for subject in subjects:     
        behaviour = glob.glob(folder + subject + "/*scored_behaviour*.csv")[0]
        print("behaviour:  {}".format(behaviour))
        behaviour = pd.read_csv(behaviour)
        label_lens.append(len(behaviour))
        labels = labels.append(behaviour)
        ##here the nothing weight is set to 10:1
        indexes =  balance_classes(labels,10)
        ##remove indexes that are less than the lookback value
        indexes = [x for x in indexes if x>look_back]
        labels['behaviour'][labels['behaviour']=='bad_jumps']='Nothing'
        print("label_lens: {}".format(label_lens))
        print("num_valid_datasetss: {}".format(len(label_lens)))    
         
    return labels, label_lens, indexes

def open_cameras(all_cams,  inference, label_len = -1, multi=False):
    count=0
    has_run = False
    for cam in all_cams:
        camera = pd.read_hdf(cam)
        if not inference:
            camera = camera[:label_len]
        camera, animals = preprocess_Coords(camera, multi = multi, drop = ['tail_tip'])
        if has_run:
            all_camera = concatenate_cameras([camera, all_camera])
        else:
            all_camera = camera
            has_run = True
    return all_camera, animals


def concatenate_cameras(cams = []):
    cam_lens = [len(cam) for cam in cams]
    min_camlen = np.min(cam_lens)
    cams = [cam[:min_camlen] for cam in cams]
    cams = np.concatenate(cams, axis=1)
    return cams

