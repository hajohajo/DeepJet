

from training_base import training_base
from Losses import loss_NLL, loss_meansquared,loss_logcosh_noUnc
from modelTools import fixLayersContaining,printLayerInfosAndWeights

#also does all the parsing
train=training_base(testrun=False)

#train.loadModel("./DeepJet_BaselineV2/KERAS_model_checkpoint_1_IDonly.h5")

from models import model_deepFlavourReference, dense_model_reg
    
train.setModel(dense_model_reg,dropoutRate=0.03)
    
train.compileModel(learningrate=0.001,
                       loss=['categorical_crossentropy',loss_logcosh_noUnc],
                       metrics={'ID_pred':'accuracy','regression_pred':'mse'},
                       loss_weights=[0., 1.])


model,history = train.trainModel(nepochs=100, 
                                 batchsize=10000, 
                                 stop_patience=300, 
                                 lr_factor=0.005, 
                                 lr_patience=3, 
                                 lr_epsilon=0.00001, 
                                 lr_cooldown=6, 
                                 lr_minimum=0.00001, 
                                 maxqsize=100)
