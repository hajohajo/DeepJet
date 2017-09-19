

from training_base import training_base
from Losses import loss_NLL, loss_meansquared
from modelTools import fixLayersContaining,printLayerInfosAndWeights

#also does all the parsing
train=training_base(testrun=False)

train.loadModel("./DeepJet_BaselineV2/KERAS_model_checkpoint_1_IDonly.h5")

reg_train=False
newtraining= not train.modelSet()
#for recovering a training
if newtraining:
    from models import model_deepFlavourReference
    
    train.setModel(model_deepFlavourReference,dropoutRate=0.1)
    
    #train.keras_model=fixLayersContaining(train.keras_model, 'regression', invert=False)
    
    train.compileModel(learningrate=0.001,
                       loss=['categorical_crossentropy',loss_meansquared],
                       metrics=['accuracy'],
                       loss_weights=[1., 0.0000000001])
else:
	reg_train=True

train.train_data.maxFilesOpen=5

if not reg_train:
	print(train.keras_model.summary())
	model,history = train.trainModel(nepochs=1, 
	                                 batchsize=10000, 
	                                 stop_patience=300, 
	                                 lr_factor=0.5, 
	                                 lr_patience=3, 
	                                 lr_epsilon=0.0001, 
	                                 lr_cooldown=6, 
	                                 lr_minimum=0.0001, 
	                                 maxqsize=400)


	print('fixing input norms...')
	train.keras_model=fixLayersContaining(train.keras_model, 'input_batchnorm')
	train.compileModel(learningrate=0.001,
	                       loss=['categorical_crossentropy',loss_meansquared],
	                       metrics=['accuracy'],
	                       loss_weights=[1., 0.000000000001])


	print(train.keras_model.summary())
#printLayerInfosAndWeights(train.keras_model)

	model,history = train.trainModel(nepochs=63, #sweet spot from looking at the testing plots 
	                                 batchsize=10000, 
	                                 stop_patience=300, 
	                                 lr_factor=0.5, 
	                                 lr_patience=3, 
	                                 lr_epsilon=0.0001, 
	                                 lr_cooldown=6, 
	                                 lr_minimum=0.0001, 
	                                 maxqsize=100)

	print('indentification training finished. Starting regression training...')

	train.saveCheckPoint('IDonly')

train.keras_model=fixLayersContaining(train.keras_model, 'regression', invert=True)
train.compileModel(learningrate=0.001,
                       loss=['categorical_crossentropy',loss_meansquared],
                       metrics={'ID_pred':'accuracy','regression_pred':'mse'},
                       loss_weights=[0.01, 1])

train.trainedepoches=0
print(train.keras_model.summary())



model,history = train.trainModel(nepochs=50, 
                                 batchsize=10000, 
                                 stop_patience=300, 
                                 lr_factor=0.5, 
                                 lr_patience=3, 
                                 lr_epsilon=0.0001, 
                                 lr_cooldown=6, 
                                 lr_minimum=0.0001, 
                                 maxqsize=100)
