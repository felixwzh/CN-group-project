import pandas as pd
import numpy as np
import sklearn
import xgboost as xgb
from utils import output_real_and_predict_data,draw

# read raw data
train = pd.read_csv('../data/raw_data.csv')

val = train.iloc[0:60000]
train = train.iloc[60000:]

# build train data and labels(y1, y2, y3) for three prediction tasks in the paper
# drop the following 6 features, since they are actually `labels`
X_train = train.drop(['sampleResLife', 'nbRouteChangesInNextSlot','nextMinRTT','nextavgRTT','nextMaxRTT','nextMdevRTT'],axis=1)
y1_train = train.sampleResLife
y2_train = train.nbRouteChangesInNextSlot
y3_train = train.nextavgRTT

X_val = val.drop(['sampleResLife', 'nbRouteChangesInNextSlot','nextMinRTT','nextavgRTT','nextMaxRTT','nextMdevRTT'],axis=1)
y1_val = val.sampleResLife
y2_val = val.nbRouteChangesInNextSlot
y3_val = val.nextavgRTT

# build the DMatrix data structure for three tasks
dtrain=[None]*4
dtest=[None]*4
dtrain[1] = xgb.DMatrix(data=X_train,label=y1_train)
dtest[1] = xgb.DMatrix(data=X_val,label=y1_val)
dtrain[2] = xgb.DMatrix(data=X_train,label=y2_train)
dtest[2] = xgb.DMatrix(data=X_val,label=y2_val)
dtrain[3] = xgb.DMatrix(data=X_train,label=y3_train)
dtest[3] = xgb.DMatrix(data=X_val,label=y3_val)

# set parameters for three tasks
param = [None]*4
param[1] = {
"reg_alpha": 0.0006,
"colsample_bytree": 0.8,
"scale_pos_weight": 1,
"learning_rate": 0.0175,
"nthread": 16,
"min_child_weight": 11,
"n_estimators": 1000,
"subsample": 0.8,
"reg_lambda": 0.0049,
"seed": 27,
"objective":'reg:linear',
"max_depth": 7,
"gamma": 0.0,
}
param[2] = {
"reg_alpha": 0.0005,
"colsample_bytree": 0.7,
"scale_pos_weight": 1,
"learning_rate": 0.005,
"nthread": 8,
"min_child_weight": 13,
"n_estimators": 1000,
"subsample": 0.25,
"reg_lambda": 0.0046,
"seed": 27,
"objective":'reg:linear',
"max_depth": 5,
"gamma": 0.7,
}
param[3] = {
    'max_depth':10,
    'eta':0.3,
    'silent':1,
    'objective':'reg:linear'
        }
watchlist = [None]*4
watchlist[1] = [(dtest[1],'eval'), (dtrain[1],'train')]
watchlist[2] = [(dtest[2],'eval'), (dtrain[2],'train')]
watchlist[3] = [(dtest[3],'eval'), (dtrain[3],'train')]

# num of trees
num_round = 200

# train for task 1
bst1 = xgb.train(param[1], dtrain[1], 100, watchlist[1])

y1_hat= bst1.predict(dtest[1])
output_real_and_predict_data(y1_val,y1_hat,'../data/temp_result/','task1_xgb_tuned')


# # train for task 2
# bst2 = xgb.train(param[2], dtrain[2], 1000, watchlist[2])
# y2_hat= bst2.predict(dtest[2])
# output_real_and_predict_data(y2_val,y2_hat,'../data/temp_result/','task2_xgb_tuned')


# # train for task 3
# bst3 = xgb.train(param[3], dtrain[3], num_round, watchlist[3])
# y3_hat= bst3.predict(dtest[3])
# output_real_and_predict_data(y3_val,y3_hat,'../data/temp_result/','task3_xgb')
