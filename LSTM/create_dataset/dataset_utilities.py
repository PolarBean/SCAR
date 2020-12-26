from LSTM.math.vectorise_EDM import vectorised_EDM
import glob
import numpy as np

def multi_animal_EDM(x, num_animals, batchsize = 32768):
    """
    DESCRIPTION: 
    For a stacked array of deeplabcut coordinates which consists of 
    (frames, animals*bodyparts, (x, y)) create a euclidean distance matrix for 
    each animal in the stack, then stack those matrices and return them.

    PARAMETERS: 
    x (array): stacked array of tracked animals. 
    num_animals (int): the number of animals in the array
    batchsize (int): the number of frames to process in a single batch, limited by GPU memory

    RETURNS:
    animals (array): stacked array of EDMs animal in each frame
    """
    bodyparts = int(x.shape[1] / num_animals)
    animals = [vectorised_EDM(x[:, (animal-1) * bodyparts : animal*bodyparts], batchsize=batchsize) for animal in range(1, num_animals+1)]
    animals = np.concatenate(animals, axis=1)
    return animals

def format_multi(dataset):
    """
    DESCRIPTION:
    Take a multi-animal deeplabcut file and return an array of shape (frames, animals*bodyparts, (x, y)).

    PARAMETERS:
    dataset (dataframe): multi-animal deeplabcut file read with pandas.

    RETURNS:
    stacked_datasets (array): an array of shape (frames, animals*bodyparts, (x, y)) of all deeplabcut tracked points.
    animals (int): the number of animals in the file.

    """
    stacked_datasets = []
    scorer = dataset.columns[0][0]
    animals = dataset[scorer].columns.get_level_values(0).unique()
    for animal in animals:
        single =  dataset[scorer][animal]
        single.columns = single.columns.droplevel()
        
        ##here we drop the likelihood columns as theyre not incorporated into this analysis
        single = single.drop('likelihood', axis=1)
        single = np.array(single).reshape((single.shape[0], int(single.shape[1] / 2), 2))
        stacked_datasets.append(single)
    return np.concatenate(stacked_datasets, axis=1), len(animals)  

def format_coords(dataset,multi=False):
    """
    DESCRIPTION:
    Take a deeplabcut file and return an array of shape (frames, bodyparts, (x, y)).

    PARAMETERS:
    dataset (dataframe): deeplabcut file read with pandas.
    multi (bool): whether or not the file is a multi-animal dataset

    RETURNS:
    dataset (array): an array of shape (frames, bodyparts, (x, y)) of all deeplabcut tracked points.
    animals (int): the number of animals in the file.
    """
    if multi:
        dataset, animals = format_multi(dataset)
    else:
        dataset = dataset.drop('likelihood', axis=1)
        dataset = np.array(dataset).reshape((dataset.shape[0], int(dataset.shape[1] / 2), 2))  
        animals = 1
    return dataset, animals


def check_validity(subject, cams, inference=False):
    """
    DESCRIPTION:
    Ensure 
    """
    check_cams = len(glob.glob(subject+"/*.h5"))
    correct_cam_number = check_cams==cams
    
        
    if check_cams==0:
        print("no DeepLabCut files found for {}".format(subject))
        return False
    

    if not correct_cam_number:
        print('the number of DLC files must equal the number of cameras and it does not for {}'.format(subject))
        return False
    
    if not inference:
        behaviour_files = len(glob.glob(subject + "/*scored_behaviour*.csv"))
        if behaviour_files==0:
            print("no scored behaviour files found for {}".format(subject))
            return False
        if behaviour_files>1:
            print("multiple scored behaviour files found for {}".format(subject))
            return False

    else:
        return True
    
