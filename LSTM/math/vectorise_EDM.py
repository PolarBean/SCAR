import numpy as np
import cupy as cp

def create_mask_EDM(m):
    """
    DESCRIPTION:
    Create a mask which removes redundancies from EDM comparisons
    ie; if the distance from point [1,1] to point [2,2] has been saved
    there is no need to compare point [2,2] to point [1,1], so create 
    a mask which excludes these redundancies. 

    For an array of 5 points this mask would look like
      [[0., 0., 0., 0., 0.],
       [1., 0., 0., 0., 0.],
       [1., 1., 0., 0., 0.],
       [1., 1., 1., 0., 0.],
       [1., 1., 1., 1., 0.]]
    Here each point is compared to every other point only once and never to itself.
    
    PARAMETERS: 
    m (int): the number of points in the array you would like to make a mask for
    
    RETURNS:
    unroll_col (array): the column indices for the non-redundant points you will compare in the EDM

    unroll_row (array): the row indices for the non-redundant points you will compare in the EDM
    """
    
    unroll_col = [([j for j in range(i, m)]) for i in range(1, m)]
    unroll_row = [([i]*j) for i, j in zip(range(m), range(m-1, 0, -1))]
    ##Flatten lists and convert to array
    unroll_col = cp.asarray([j for i in unroll_col for j in i])
    unroll_row = cp.asarray([j for i in unroll_row for j in i])
    return unroll_col, unroll_row

def vectorised_EDM(x, batchsize = 4096):
    """
    DESCRIPTION:
    given a three-dimensional input matrix x which consists of many sets of two-dimensional coordinates 
    for each set create a euclidean distance matrix and return a 2d array where each row is the condensed 
    distance matrix for the corresponding slice in x. this function could be generalised to n dimensions
    if needed. 

    PARAMETERS:
    x (array): an array of shape (m , n, 2) where m is the number of coordinate lists, n is the number of coordinates, and o is (x, y)
    batchsize (int): the number of EDMs to process at once, limited by GPU memory.

    RETURNS:
    EDM_array (array): an array of shape m, ((n*n)-n)/2

    """
    x = cp.asarray(x)
    ##create a sqaureform shape of your coordinate lists
    new_shape = np.array(x.shape)[[0,1,1,2]]
    ##create a mask for this squareform to avoid redundancies
    unroll_col, unroll_row = create_mask_EDM(new_shape[1])
    ##broadcast your array to this new shape
    x =  cp.broadcast_to(x[:,:,None,:], new_shape)
    ##swap the rows and columns of each sqaureform array so that you have an array to compare each point to
    x_transpose = x.transpose(0,2,1,3)
    EDM_array = []
    for batch in tqdm(range(int(len(x)/batchsize))):
        ##for each batch compare the masked coordinates to each other
        distance = x_transpose[batch*batchsize:(batch+1)*batchsize,unroll_col, unroll_row] - x[batch*batchsize:(batch+1)*batchsize,unroll_col, unroll_row]
        distamce = cp.linalg.norm(distance, axis=-1)
        EDM_array.append(cp.asnumpy(distance))
    ##compare any coordinates which didnt fit neatly into a batch
    distance = x_transpose[(batch+1)*batchsize:,unroll_col, unroll_row] - x[(batch+1)*batchsize:,unroll_col, unroll_row]
    distance = cp.linalg.norm(distance, axis=-1)
    EDM_array.append(cp.asnumpy(distance))
    return np.concatenate(EDM_array)
