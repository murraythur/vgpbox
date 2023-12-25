import socket

import torch.nn.functional as F
import models
import losses

from datasets import SeismicBinaryDBDataset

import sys
sys.path.insert(0, '../shared_modules/')
from constantsBase import ConstantsBase
class Constants(ConstantsBase):
    
    def __init__(self, **kwargs):        
        self.RUN = "fault_constant8_vvdeep_small_final"

        self.DATA = "fault_2ms_r.bin"
        
        # parameter do gpu
        self.DEVICE = 2# cuda device
        
        # modeloss
        self.MODEL = models.AE_r
        
        self.MODEL_LOAD_PATH = None
        #self.MODEL_LOAD_PATH = "server/models/layers_new_lr1e4_b100_constant8_vvdeep_r_l1/model_03000000.torch"
        
        self.DROPOUT_RATE = 0.0#
        self.ACTIVATION = F.relu
    
        self.LOSS = losses.l1_mean_loss_gain
        self.BATCH_SIZE = 100
        self.LRATE = 1e-4
        self.WEIGHT_DECAY = 0 #
        # seed
        self.SEED = 123
        
        self.N_STEPS = 3000000
  
        self.N_CPU_WORKERS = 1# 
        
        self.DATASET = SeismicBinaryDBDataset
        
        self.N_EXAMPLES = 300000
        self.VELOCITY_SHAPE = (1, 128, 128)# 1, NX, NZ
        self.GATHER_SHAPE = (1, 32, 512)# 1, NREC, NSTEPS
        self.SOURCE_SHAPE = (2, 1, 1)# 2, 1, 1
        
        self.T_GAIN = 2.5
        self.VELOCITY_MU = 2700.0 # m/s
        self.VELOCITY_SIGMA = 560.0 # m/s ,       
        self.GATHER_MU = 0.
        self.GATHER_SIGMA = 1.0
        
        ## 3. SUMMARY OUTPUT FREQUENCIES
        self.SUMMARY_FREQ    = 1000    # h.r
        self.TEST_FREQ       = 2000    
        self.MODEL_SAVE_FREQ = 250000    
        for key in kwargs.keys(): self[key] = kwargs[key]
        
        self.SUMMARY_OUT_DIR = "results/summaries/%s/"%(self.RUN)
        self.MODEL_OUT_DIR = "results/models/%s/"%(self.RUN)
    
        self.HOSTNAME = socket.gethostname().lower()
        if 'greyostrich' in self.HOSTNAME:
            self.DATA_PATH = "/data/greyostrich/not-backed-up/aims/aims17/bmoseley/DPhil/Mini_Projects/DIP/forward_seisnets_paper/generate_data/data/"+self.DATA
        elif 'greypartridge' in self.HOSTNAME:
            self.DATA_PATH = "/data/greypartridge/not-backed-up/aims/aims17/bmoseley/DPhil/Mini_Projects/DIP/forward_seisnets_paper/generate_data/data/"+self.DATA
        else:
            self.DATA_PATH = "../generate_data/data/"+self.DATA
