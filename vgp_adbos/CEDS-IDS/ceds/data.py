import sys
import matplotlib
if 'linux' in sys.platform.lower(): matplotlib.use('Agg')
import matplotlib.pyplot as plt

import os
import copy
import torch
from torch.utils.data import Dataset
import numpy as np

class SeismicDataset(Dataset):

    def __init__(self,
                 c,
                 irange=None,
                 verbose=True):
        
        self.c = c
        self.verbose = verbose
        
        if type(irange) == type(None):
            self.n_examples = c.N_EXAMPLES
            self.irange = np.arange(self.n_examples)
        else:
            self.n_examples = len(irange)
            self.irange = np.array(irange)
        if self.verbose:
            print("%i examples"%(self.n_examples))
            print(self.irange)
    
    def __len__(self):
        return self.n_examples
    
    def _preprocess(self, gather, velocity, source_i, i):
        
        gather = (gather - self.c.GATHER_MU) / self.c.GATHER_SIGMA
        velocity = (velocity - self.c.VELOCITY_MU) / self.c.VELOCITY_SIGMA
        source_i = source_i/self.c.VELOCITY_SHAPE[1]# /NX
        
        sample = {'inputs': [torch.from_numpy(velocity), torch.from_numpy(source_i)],
                  'labels': [torch.from_numpy(gather),],
                  'i': i}
        
        return sample
    
    
class SeismicBinaryDBDataset(SeismicDataset):
    """DBSeismic dataset, for use with mydataloader"""

    def __init__(self, 
                 c,
                 irange=None,
                 verbose=True):
        super().__init__(c, irange, verbose)
        if not os.path.isfile(self.c.DATA_PATH): raise OSError("Unable to locate file: %s"%(self.c.DATA_PATH))

        self.velocity_nbytes = (np.prod(self.c.VELOCITY_SHAPE)*32)//8#
        self.gather_nbytes = (np.prod(self.c.GATHER_SHAPE)*32)//8# 
        self.source_i_nbytes = (np.prod(self.c.SOURCE_SHAPE)*32)//8# 
        self.total_nbytes = self.velocity_nbytes + self.gather_nbytes + self.source_i_nbytes
        total_size, file_size = self.c.N_EXAMPLES*self.total_nbytes, os.path.getsize(self.c.DATA_PATH)
        if file_size < total_size: raise Exception("ERROR: file size < expected size: %s (%i < %i)"%(self.c.DATA_PATH, file_size, total_size))
        if file_size > total_size: print("WARNING: file size > expected size: %s (%i != %i)"%(self.c.DATA_PATH, file_size, total_size))

    def open_file_reader(self):
        self.reader = open(self.c.DATA_PATH, 'rb')
        
    def close_file_reader(self):
        "Close database file reader"
        self.reader.close()
        
    def initialise_worker_fn(self, *args):
        "Intialise worker for multiprocessing dataloading"
     
        self.open_file_reader()# 
        self.irange = np.copy(self.irange)#
        self.c = copy.deepcopy(self.c)#

    def __del__(self):
        if hasattr(self, 'reader'): self.close_file_reader()# 
        
    def __getitem__(self, i):
        self.reader.seek(self.irange[i]*self.total_nbytes)
        buf = self.reader.read(self.total_nbytes)#
        array = np.frombuffer(buf, dtype="<f4")# 
        
        # parse
        offset, delta = 0, np.prod(self.c.VELOCITY_SHAPE)
        velocity = array[offset:offset+delta]
        offset += delta; delta = np.prod(self.c.GATHER_SHAPE)
        gather = array[offset:offset+delta]
        offset += delta; delta = np.prod(self.c.SOURCE_SHAPE)
        source_i = array[offset:offset+delta]
        velocity = velocity.reshape(self.c.VELOCITY_SHAPE)
        gather = gather.reshape(self.c.GATHER_SHAPE)
        source_i = source_i.reshape(self.c.SOURCE_SHAPE)
        
        return self._preprocess(gather, velocity, source_i, self.irange[i])


if __name__ == "__main__":
    
    from constants import Constants
    
    #from torch.utils.data import DataLoader
    from mydataloader import DataLoader
    
    c = Constants()
    print(c)
    
    torch.manual_seed(123)
    
    Dataset = SeismicBinaryDBDataset
    
    
    traindataset = Dataset(c,
                             irange=np.arange(0,7*c.N_EXAMPLES//10),
                             verbose=True)
    
    testdataset = Dataset(c,
                             irange=np.arange(7*c.N_EXAMPLES//10,c.N_EXAMPLES),
                             verbose=True)
    
    assert len(set(traindataset.irange).intersection(testdataset.irange)) == 0
    
    trainloader = DataLoader(traindataset
    trainloader_iter = iter(trainloader)
    
    if not traindataset.isDB:#
        print("TRAIN dataset:")
        for i in range(10):
            sample = traindataset[i]# 
            #print(sample)
            print(i, sample['inputs'][0].size(), sample['labels'][0].size(), sample['i'])
        print(sample['inputs'][0].dtype, sample['labels'][0].dtype)
        
    if not testdataset.isDB:
        print("TEST dataset:")
        for i in range(10):
            sample = testdataset[i]# 
            print(i, sample['inputs'][0].size(), sample['labels'][0].size(), sample['i'])
        print(sample['inputs'][0].dtype, sample['labels'][0].dtype)
    
    print("BATCHED dataset:")
    for i_batch in range(10):
        sample_batch = next(trainloader_iter)
        print(i_batch, sample_batch['inputs'][0].size(), sample_batch['labels'][0].size(), sample_batch['i'])
    for ib in range(5):
        
        plt.figure(figsize=(11,5))
        plt.subplot(1,2,1)
        plt.imshow(sample_batch["inputs"][0][ib,0,:,:].numpy().T, vmin=-2, vmax=2)
        plt.colorbar()
        plt.title(sample_batch["i"][ib].numpy())
        plt.subplot(1,2,2)
        plt.imshow(sample_batch["labels"][0][ib,0,:,:].numpy().T,
                   aspect=0.2, cmap="Greys", vmin=-2, vmax=2)
        plt.colorbar()
        plt.title(str(sample_batch["inputs"][1][ib,0,0,0].numpy()))
        plt.subplots_adjust(hspace=0.0, wspace=0.0)
    
    
    
