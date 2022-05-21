import argparse 
import pandas as pd
import numpy as np 
import sys
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d

from scipy.spatial.distance import squareform, pdist

def getgood(df, ax, tol=0.20):   
    '''Returns rows or columns with more than tol 
    fraction of numpy.nan entries

    Args:
        df: a pandas.DataFrame instance 
        ax: of type int
            axis along which np.nan entries 
            are to be calculated 
            ax=0 returns nan counts for each column
            ax=1 returna nan counts for each row
        tol: float, value between 0 and 1
             denotes fraction of nan entries to
             tolerate in each pandas.DataFrame row or column

    Returns:
        good_idx: column indices (or row indices, if ax=1) 
                  with nan counts within tolerance
        bad_idx: column indices(or row indices, if ax=1) 
                 with nan counts outside tolerance
        num_nan: fraction of nan entries in each column 
                 (or row if ax=1)
    '''
    # Find number of rows or cols
    num_elems = df.shape[ax]

    # Get a row vector whose entries denote the percentage of NaN entries in 
    # the corresponding column 
    num_nan = np.sum(np.isnan(df), axis = ax)/num_elems

    # Delete columns with perc % or more NaN's
    good_tf   = num_nan < tol
    good_idx  = [i for i, tf in enumerate(good_tf) if tf]


    bad_tf   = num_nan >= tol
    bad_idx  = [int(i) for i, tf in enumerate(bad_tf) if tf]

    return good_idx, bad_idx, num_nan


def Qmap(badC_idx, goodC_idx):
    n = len(badC_idx)+len(goodC_idx)
    D = {}
    i = 0
    count = 0

    for b in badC_idx:
        while i < b:
            D[i-count] = i
            i += 1
        i += 1
        count += 1

    if b < n:
        while i <= n:
            D[i-count] = i
            i += 1
        count += 1

    return D


def stdz_and_nan2zero(X):
    ''' Standardize the data by subtracting the column 
    mean from each entry and dividing each entry by 
    its column's standard deviation. numpy.nanmeans ignores 
    np.nan entries when calculating the col (or row) means
    '''

    # axis = 0: returns column means
    means = np.nanmean(X, axis = 0, keepdims = True) 

    # keepdims = True : returns a row vector of
    # column means means when axis = 0
    stds = np.nanstd(X, axis = 0, keepdims = True) 
    
    Z = np.nan_to_num((X - means) / stds)
    return Z
    

class read_nfhs5:
    '''Reads and readies the NFHS-5 table of entries for PCA'''

    def __init__(self, badColsTol = 0.20, badRowsTol = 0.20):
        # 1. self.df: Read df from file
        self.df = pd.read_csv('../DATA/NFHS5.csv')
        
        # 2. self.df_nfhs5: Select only the NFHS-5 columns. Ignore error codes
        nfhs5_colnames = np.array(['Q'+str(i)+'_NFHS5' for i in range(1, 105)])
        self.df_nfhs5 = self.df[nfhs5_colnames]
        
        # 3. self.np_nfhs5: Convert dataframe to numpy array
        self.np_nfhs5 = self.df_nfhs5.to_numpy()

        # 4. Get the good+bad COLUMNS of nfhs5_numpy:
        goodC_idx, badC_idx, numC_nan = getgood(self.np_nfhs5, ax=0, tol=badColsTol)
        
        # 5. Get the good+bad ROWS of nfhs5_numpy:
        goodR_idx, badR_idx, numR_nan = getgood(self.np_nfhs5, ax=1, tol=badRowsTol)
        
        if badColsTol != 0.2:
            print('COLUMNS ELIMINATED FROM ANALYSIS:')
            srn = 'Question No.'
            colname = 'Col. Name'
            percnan = f'% NaN > {badColsTol:.2f}'
            print(f'{srn:>12} | {percnan:>4}') 
            print("="*27)
            for j in badC_idx:
                print(f'{j+1:>12} | {numC_nan[j]*100:.4}')

        #print('\nBAD ROWS:')
        #srn = 'Idx.'
        #dist = 'District'
        #state = 'State'
        #percnan = f'% NaN > {badRowsTol:.2f}'
        #print(f'{srn:>4} | {dist:>30} | {state:>30} | {percnan:>4}')
        #for j in badR_idx:
        #    print(f'{j:>4} | {self.df.iloc[j][2]:>30} | {self.df.iloc[j][1]:>30} | {numR_nan[j]*100:.4}')

        # 6. self.X: Eliminate only bad columns indentified in the previous step
        # Do not eliminate any rows
        #print('\nEliminating only bad columns ...')
        self.X = self.np_nfhs5[:, goodC_idx]
        
        # 7. self.D: Construct a map D that takes the new question number (column number)
        # and returns the old column (question) number
        self.D = Qmap(badC_idx, goodC_idx)
        
        # 8. self.tf_isnan: A matrix of True/False to indicate which 
        # cells contain np.nan
        self.tf_isnan = np.isnan(self.X)
        
        # 9. self.Z: standardize X and replace nan's with zeros
        self.Z = stdz_and_nan2zero(self.X)
        
    
    ## Perform SVD on data
    def get_pca(self, reduced_dim = 2):
        '''Perform SVD on self.Z'''
        U, s, Vt = np.linalg.svd(np.transpose(self.Z), full_matrices=False)
        return self.Z @ U[:,:reduced_dim]   # 'r'-dimensional representation of X

    
    def set_axis_limits(self, a, t = 0.1):
        '''Return axis limits as a function of extreme data points'''
        return [np.min(a) - t*(np.max(a) - np.min(a)), np.max(a) + t*(np.max(a) - np.min(a))]  


    def plot2D(self, statename = None):
        A2 = self.get_pca(2)
        
        if statename is not None: 
            idx_state = [ i for i in range(self.df.shape[0]) if self.df.loc[i][1] == statename]
        else:
            idx_state = []

        plt.figure(figsize=(8, 8))
        plt.scatter(A2[:,0], A2[:,1], marker='o', alpha = 0.4)
        plt.scatter(A2[idx_state,0], A2[idx_state,1], marker='o', color = 'red', alpha = 1)
        plt.xlabel('a1')
        plt.ylabel('a2')
        plt.axis('equal')
        plt.xlim(self.set_axis_limits(A2[:, 0], 0))
        plt.ylim(self.set_axis_limits(A2[:, 1], 0))
        for i, distr_num in enumerate(idx_state):
            plt.annotate(self.df.loc[distr_num][2], (A2[idx_state[i],0]+0.5, A2[idx_state[i],1]-0.1))
        plt.show()
    

    def plot3D(self, statename = None):
        ## Get a 3D representation of data points
        A3 = self.get_pca(3)

        if statename is not None: 
            idx_state = [ i for i in range(self.df.shape[0]) if self.df.loc[i][1] == statename]
        else:
            idx_state = []

        ## Plot the 3-d representation of 'Z_nan2zero'
        plt.figure(figsize=(8, 8))
        ax = plt.axes(projection ="3d")

        sctt = ax.scatter3D(A3[:,0], A3[:,1], A3[:,2], marker='o', alpha = 0.5)
        sctt_state = ax.scatter3D(A3[idx_state,0], A3[idx_state,1], A3[idx_state,2], marker='o', color = 'red', alpha = 0.6)

        for i, distr_num in enumerate(idx_state):
            ax.text(A3[idx_state[i],0]+0.5, A3[idx_state[i],1]+0.5, A3[idx_state[i],2]+0.5, self.df.loc[distr_num][2] , color='red')

        ax.set_xlabel('a1', fontweight ='bold')
        ax.set_ylabel('a2', fontweight ='bold')
        ax.set_zlabel('a3', fontweight ='bold')
        ax.set_xlim(self.set_axis_limits(A3[:, 0], 0))
        ax.set_ylim(self.set_axis_limits(A3[:, 1], 0))
        ax.set_zlim(self.set_axis_limits(A3[:, 2], 0))

        plt.show()
    
    def impute_nan(self, opt_variance = 0.80):
        # Perform SVD on var-covariance matrix of X
        U,S,Vt = np.linalg.svd( (np.transpose(self.Z) @ self.Z)/self.Z.shape[0] ) 

        var_lambdas = np.cumsum(S)/np.cumsum(S)[len(S)-1]   
        # Frac. of variance explained if we retained k 
        # principal comp., for k = 1:d

        k = np.searchsorted(var_lambdas, opt_variance)  
        # Find smallest k for which frac. of 
        # var. explained by PCA >= opt_variance

        Z_tilde = self.Z @ U[:,1:k] @ np.transpose(U[:,1:k]) 
        # Z_tilde is closest to Z (after rotating once and then back)
        # Note that Z_tilde is *NOT* a reduced dimension representation of Z

        self.Z[self.tf_isnan] = Z_tilde[self.tf_isnan]       
        # Overwrite currupted pixels in orginal image with Z_tilde

        # Rescale(multiply) by std and add back mean vector to X
        return (self.Z * np.nanstd(self.X, axis = 0, keepdims = True)) + np.nanmean(self.X, axis = 0, keepdims = True), k
    
    
    def distr2indx(self, cityname):
        return self.df[self.df['District'] == cityname].index[0]


    def indx2distr(self, indx):
        return [self.df.iloc[indx]['District'], self.df.iloc[indx]['State']]


    def get_nnb(self, cityname, num = 5, pca = False, reduced_dim = 2):
        # Returns names and distances of `num` nearest neighbors of `cityname` 
        # where distance is computed from distance matrix `dist_mat`

        # First impute the missing entries:
        X_imputed, k = self.impute_nan(0.99)

        # Perform PCA to get a lower dimensional representation
        if pca:
            A = self.get_pca(reduced_dim)
            # Recall that A is already shifted and scaled to get mean = 0 and std = 1
            Y_imputed = pdist(A, metric='euclidean')
        else:
            # Recall that X_imputed has not been shifted and scaled to get mean = 0 and std = 1
            Z_imputed = (X_imputed - np.nanmean(X_imputed, axis = 0, keepdims = True)) / np.nanstd(X_imputed, axis = 0, keepdims = True)
            Y_imputed = pdist(Z_imputed, metric='euclidean')

        dist_mat = squareform(Y_imputed)
        indx = self.distr2indx(cityname)
        t = dist_mat[indx, :]
        idx = np.argsort(t)

        return [(self.indx2distr(idx[i]), idx[i], t[idx[i]]) for i in range(1,num+2)]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                      description = '''Perform PCA on the NFHS-5 database:'''
             )
    parser.add_argument('action', choices=['knn', 'impute', 'plot'], 
                        help='Code returns k-nearest neighbors, imputes missing values, or plots a 2D/3D representation of all 705 data points')
    parser.add_argument('--colTol', type=float,
                        help='up to what fraction of nan values in each column to disregard')
    parser.add_argument('-r', '--rdim', type=int, default=2,
                        help='the number of principal compoments in PCA')
    parser.add_argument('-d', '--dplot', type=int, choices = [2, 3], default=2,
                        help='plot dimension; can be either 2 or 3')
    parser.add_argument('-l', '--lmbda', type=float, default=0.99,
                        help='fraction of variance explained by the principal components in PCA')
    parser.add_argument('--district',
                        help='[not optional if "action" = "knn"] find nearest n neighbors of this district')
    parser.add_argument('--state',
                        help='highlights all districts in "state" in 2D/3D plot')
    parser.add_argument('-k','--knbrs', type=int, default=5,
                        help='number of nearest neighbors')

    args = parser.parse_args()

    if args.colTol is not None: 
        NFHS5 = read_nfhs5(badColsTol = args.colTol)
    else:
        NFHS5 = read_nfhs5()
         
    if args.action == 'knn':
        if args.district is not None:
            nrst_nbrs = NFHS5.get_nnb(args.district, num = args.knbrs, pca = True, reduced_dim = args.rdim)
        else:
            raise TypeError("Must provide a 'district' to knn routine. See code usage for details.")
            sys.exit(1)
        
        print(f'\n{args.knbrs} NEAREST NEIGHBORS OF {args.district} (IN DIM = {args.rdim}):')
        print(f'Row | {"District":>30} | {"State":>30} | Euc. Distance')
        print("="*85)
        for i in nrst_nbrs:
            print(f'{i[1]:>3} | {i[0][0]:>30} | {i[0][1]:>30} | {i[2]:.2}')
     
    elif args.action == 'impute':
        X_imputed, k = NFHS5.impute_nan(args.lmbda)
        # Print all the imputed values
        print('\nIMPUTING MISSING SURVEY VALUES:')
        print(f'{args.lmbda*100}% of variance in the data is explained by {k} principal components of the data matrix.')
        print(f"{'Row':>5} | {'District':>27} | {'State':>29} | {'Q':>5} | {'Imputed Value to Q':<19}")
        print('='*97)
        for r in range(NFHS5.tf_isnan.shape[0]):
            for c in range(NFHS5.tf_isnan.shape[1]):
                if np.isnan(NFHS5.X[r][c]):
                    print(f'{r:>5} | {NFHS5.df.iloc[r][2]:>27} | {NFHS5.df.iloc[r][1]:>29} | {NFHS5.D[c]+1:>5} | {X_imputed[r][c]:.2f}')

    elif args.action == 'plot':
        if args.dplot == 2:
            # 1. Plot a 2-dimensional representation of X
            NFHS5.plot2D(statename = args.state)

        elif args.dplot == 3:
            # 2. Plot a 3-dimensional representation of X
            NFHS5.plot3D(statename = args.state)

