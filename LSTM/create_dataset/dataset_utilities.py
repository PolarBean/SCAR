from .math.vectorise_EDM import vectorised_EDM
import glob
import numpy as np

def multi_animal_EDM(x, num_animals: int,  batchsize: int = 32768):
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


def check_validity(subject, cams, inference=False, dlc_epoch = ''):
    """
    DESCRIPTION:
    Ensure an animal folder is correctly formatted.

    PARAMETERS:
    subject (str): a path to the animals folder
    cams (int): the number of cameras to expect in the folder
    inference (bool): whether or not the dataset is in the training set or whether we are performing inference on it

    RETURNS:
    valid_status (bool): True if the folder is correctly formatted, False otherwise.
    """
    check_cams = len(glob.glob(subject+"/*{}.h5".format(dlc_epoch)))
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
    

def balance_classes(data, Nothing_weight):
    """
    DESCRIPTION: 
    Takes a set of classes and makes sure 'Nothing' doesn't outweigh everything else.

    PARAMETERS: 
    data (dataframe): a pandas dataframe of the behaviour at each frame of each video.
    Nothing_weight (int): How much greater should Nothing be than the most frequent non-nothing behaviour. 

    RETURNS:
    balanced_classes (list): a list of indexes for your balanced classes
    """
    sizes = []
    indexes = []
    for behaviour in data['behaviour'].unique():
        if behaviour != 'Nothing':
            sizes.append(np.sum(data["behaviour"] == behaviour))
        indexes.append(np.where(data["behaviour"] == behaviour)[0])
        
    balanced_classes = []
    j = 0
    print("Sizes: {}".format(sizes))
    for index in indexes:
        if data['behaviour'].unique()[j] == 'Nothing':
            balanced_classes.append(np.random.choice(index, size=int(np.max(sizes)*Nothing_weight), replace=False))

        else:
                balanced_classes.append(index)

        j += 1
    balanced_classes.append(indexes[-1])
    balanced_classes = [item for sublist in balanced_classes for item in sublist]
    return balanced_classes

def preprocess_Coords(dataset,multi=False, drop = []):
        if multi:
            dataset, animals = format_multi(dataset)
        else:
            scorer = dataset.columns[0][0]
            dataset = dataset[scorer]
            for i in drop:
                dataset = dataset.drop(i, axis=1)
            ####add likelihood mask
            dataset.columns = dataset.columns.droplevel()
            dataset = dataset.drop('likelihood', axis=1)
            dataset = np.array(dataset).reshape((dataset.shape[0], int(dataset.shape[1] / 2), 2))  
            animals = 1
        return dataset, animals

