import cPickle as pkl
import csv
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as mtick
import os
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import xgboost as xgb
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM,Dropout
from sklearn.preprocessing import MinMaxScaler
import numpy as np
from math import sqrt
import tensorflow as tf
def output_real_and_predict_data(y_real,y_pred,path,filename):
    """
    rt
    :param y_real: list
    :param y_pred: list
    :param path:
    :param filename:
    :return: None
    """
    with open(path+filename+'_real.csv','w') as fout:
        for val in y_real:
            fout.write(str(val)+',\n')
    with open(path + filename + '_predict.csv', 'w') as fout:
        for val in y_pred:
            fout.write(str(val) + ',\n')

    # draw(path+filename+'_real.csv',path + filename + '_predict.csv',filename,path+filename+'.jpg')
    draw(path + filename + '_real.csv', path + filename + '_predict.csv', filename, path + filename )

    print "finish"+path+filename


def draw(realfilePath, predictfilePath, graphTitle, outputPath):
    tableReal = []
    for line in csv.reader(open(realfilePath)):
        tableReal.append(line[0])

    tablePred = []
    for line in csv.reader(open(predictfilePath)):
        tablePred.append(line[0])

    relativeError = []
    for i in range(len(tableReal)):
        if float(tableReal[i])!=0:
            relativeError.append(100 * abs(float(tablePred[i]) - float(tableReal[i])) / float(tableReal[i]))

    relativeError = sorted(relativeError, key=float)

    sampleRate = []
    length = len(relativeError)
    for i in range(length):
        sampleRate.append(100 * (i + 1) / length)
    area = getArea(relativeError, sampleRate)

    print "++++++++++++++++++++++++++++++++++++++++++++"
    print area,"area!!"
    print "++++++++++++++++++++++++++++++++++++++++++++"
    with open('../data/temp_result/rough_result.txt','a') as fout:
        fout.write("\n++++++++++++++++++++++++++++++++++++++++++++++++++++\n")
        fout.write(outputPath)
        fout.write("\n")
        fout.write("area:"+str(area))

    # _draw(relativeError, sampleRate, graphTitle, outputPath)

def getArea(xData,yData):
	S = 0
	breakFlag = False
	for i,x in enumerate(xData):
		if i == 0:
			continue
		if xData[i] > 100:
			xLen = 100 - xData[i-1]
			yLen1 = yData[i-1]
			yLen2 = yData[i-1]
			breakFlag = True
		else:
			xLen = xData[i] - xData[i-1]
			yLen1 = yData[i-1]
			yLen2 = yData[i]
		S += (yLen1 + yLen2)*xLen/2
		if breakFlag:
			break

	if not breakFlag:
		S += (100 - xData[-1])*yData[-1]
	return S/(100*100)

def _draw(xData, yData, title, outputPath):
    x = np.array(xData)
    y = np.array(yData)
    fig = plt.figure(1, (8, 5))
    ay = fig.add_subplot(1, 1, 1)
    plt.plot(x, y, linestyle='-', color='blue', marker='<')
    plt.grid(True, color='k', linestyle='--', linewidth='1')
    plt.title(title)
    plt.xlabel('relative prediction errors (%)')
    plt.ylabel('samples (%)')

    fmt = '%.2f%%'
    ticks = mtick.FormatStrFormatter(fmt)
    ay.yaxis.set_major_formatter(ticks)
    ay.xaxis.set_major_formatter(ticks)

    axes = plt.gca()
    axes.set_xlim([0, 100])
    axes.set_ylim([0, 100])

    # plt.show()
    plt.savefig(outputPath+ '.pdf')
    plt.savefig(outputPath + '.jpg')

    plt.close()




def get_pd_from_path(path):
    """

    :param path: the path that contains many csv files
    :return: a pd.df that concat all the data
    """
    list=[]
    in_file_list=os.listdir(path)
    for in_file in  in_file_list:
        try:
            list.append(pd.read_csv(path+in_file))
        except:
            pass
    big_pd = pd.concat(list, axis=0, join='outer', join_axes=None, ignore_index=False,
                    keys=None, levels=None, names=None, verify_integrity=False,
                    copy=True)
    return big_pd

def get_task_data_from_df(df,task):
    """
    :param df: the input data, could be train df or test df
    :param task: the task that we want to conduct
    :return: X, y
    """
    if task ==1:
        X=df.drop(
            ['sampleResLife'],
            axis=1)
        y = df.sampleResLife

    elif task==2:
        X = df.drop(
            ['nbRouteChangesInNextSlot'],
            axis=1)
        y = df.nbRouteChangesInNextSlot
    elif task==3:
        X = df.drop(
            [ 'nextMinRTT', 'nextavgRTT', 'nextMaxRTT', 'nextMdevRTT'],
            axis=1)
        y = df.nextavgRTT
    else:
        exit(-1)

    return X,y


def RF_task(train_path,test_path,task,task_name,n_estimators=10):
    """
    train a rf model
    :param train_path: the path of dir that contains the .csv for each path, trianing data
    :param test_path: the path of dir that contains the .csv for each path, testing data
    :param task: int, 1,2,3
    :param task_name: the name of this experiment, should include the details
    :param n_estimators: number of trees
    :return: none
    """
    trainDF=get_pd_from_path(train_path)
    testDF = get_pd_from_path(test_path)
    train_X , train_y = get_task_data_from_df(trainDF,task)
    test_X, test_y = get_task_data_from_df(testDF, task)
    rf_regressor = RandomForestRegressor(n_estimators=n_estimators, n_jobs=-1)
    rf_regressor.fit(train_X, train_y)
    y_hat = rf_regressor.predict(test_X)
    mse1 = mean_squared_error(y_hat, test_y)

    output_real_and_predict_data(test_y, y_hat, '../data/temp_result/', task_name)


def XGB_task(train_path,test_path,task,task_name,n_estimators=10):
    """
    train a xgb model
    :param train_path: the path of dir that contains the .csv for each path, trianing data
    :param test_path: the path of dir that contains the .csv for each path, testing data
    :param task: int, 1,2,3
    :param task_name: the name of this experiment, should include the details
    :param n_estimators: number of trees
    :return: none
    """
    trainDF=get_pd_from_path(train_path)
    testDF = get_pd_from_path(test_path)
    train_X , train_y = get_task_data_from_df(trainDF,task)
    test_X, test_y = get_task_data_from_df(testDF, task)

    dtrain = xgb.DMatrix(data=train_X, label=train_y)
    dtest= xgb.DMatrix(data=test_X, label=test_y)

    if task==1:
        param = {
                "reg_alpha": 0.0,
                "colsample_bytree": 0.9,
                "scale_pos_weight": 1,
                "learning_rate": 0.05,
                "nthread": 16,
                "min_child_weight": 5,
                "n_estimators": 100,
                "subsample": 0.7,
                "reg_lambda": 0.0032,
                "seed": 27,
                "objective":'reg:linear',
                "max_depth": 7,
                "gamma": 0.0,
                }
    elif task==2:
        param = {
            "reg_alpha": 0.0,
            "colsample_bytree": 0.9,
            "scale_pos_weight": 1,
            "learning_rate": 0.05,
            "nthread": 16,
            "min_child_weight": 5,
            "n_estimators": 100,
            "subsample": 0.7,
            "reg_lambda": 0.0032,
            "seed": 27,
            "objective": 'reg:linear',
            "max_depth": 7,
            "gamma": 0.0,
        }
    elif task==3:
        param = {
            # "reg_alpha": 0.0,
            # "colsample_bytree": 0.9,
            # "scale_pos_weight": 1,
            # "learning_rate": 0.05,
            "nthread": 16,
            # "min_child_weight": 5,
            # "n_estimators": 100,
            # "subsample": 0.7,
            # "reg_lambda": 0.0032,
            # "seed": 27,
            "objective": 'reg:linear',
            # "max_depth": 7,
            # "gamma": 0.0,
        }

    bst1 = xgb.train(param, dtrain, n_estimators)
    y_hat = bst1.predict(dtest)
    output_real_and_predict_data(test_y, y_hat, '../data/temp_result/', task_name)


def get_lstm_data_from_df(train_df,test_df,task,time_steps,min_samples_for_path=5):
    """
    convert the df data structure into lstm suitable form, vector as input

    the current process method: use the previous k trace-route as previous k time-steps,
    and also the label of the trace-route which does not belong to the current route.
    The mark to distinguish different route is `sampleRouteAge`, because every route
    begins with a `sampleRouteAge`=0.
    But one thing left is what should be fed into the `label` feature of the trace-route
    belongs to current route? For now, we just feed 0 to indicate that the trace-route
    belongs to current route

    k+1 inputs and 1 output.

    :param train_df: the input data, train df
    :param test_df: the input data, test df
    :param task: the task that we want to conduct
    :param time_steps: the time_steps of a sequence, time_steps-1 for previous, and the final one for final predict
    :param min_samples_for_path: min_samples_for_path, int, default = 5
    :return: train_lstm_X, train_lstm_y, test_lstm_X, test_lstm_y, feature_dimension

    numpy arrays is ok
    train_lstm_X.shape=[samples, time steps, features]
    train_lstm_y.shape=[samples, time steps]
    test_lstm_X.shape=[samples, time steps, features]
    test_lstm_y.shape=[samples, time steps]
    feature_dimension = X.shape[2]

    """
    # fixme: what's y.shape?

    all_df = pd.concat([train_df,test_df], axis=0, join='outer', join_axes=None, ignore_index=False,
                    keys=None, levels=None, names=None, verify_integrity=False,
                    copy=True)
    all_df = all_df.reset_index(drop=True)

    train_X, train_y = [], []
    test_X, test_y = [], []

    train_len = train_df.shape[0]
    test_len = test_df.shape[0]
    min_samples_for_path = 5


    if train_len < time_steps + min_samples_for_path:
        return None, None, None, None, None

    num_train_sequence = train_len - time_steps + 1
    num_test_sequence = test_len

    # store the index for each training sequence
    train_index_list = []
    for i in range(num_train_sequence):
        train_index_list.append(range(i, i + time_steps))

    # store the index for each test sequence
    test_index_list = []
    for i in range(num_test_sequence):
        test_index_list.append(range(i+train_len-time_steps+1,i+train_len+1))
    if task == 1:
        # get the data from one [1,2,3,4,5], while considering the label for route
        for index_list in train_index_list:
            in_current_route_flag=True
            seq_df = train_df.loc[index_list]
            label = seq_df.loc[index_list[-1]]['sampleResLife']
            for j in range(time_steps-1,0,-1):
                index = index_list[j]
                if not in_current_route_flag:
                    break
                if seq_df.loc[index]['sampleRouteAge'] == 0:
                    in_current_route_flag = False
                seq_df.loc[index, 'sampleResLife'] = 0
            train_X.append(seq_df.values[:, :])
            train_y.append(label)
        # get the data from [34,35,36,37,38,39], while considering the train and test label.
        for index_list in test_index_list:
            in_current_route_flag = True
            seq_df = all_df.loc[index_list]
            label = seq_df.loc[index_list[-1]]['sampleResLife']
            for j in range(time_steps - 1, 0, -1):
                index = index_list[j]
                if not in_current_route_flag:
                    break
                if seq_df.loc[index]['sampleRouteAge'] == 0:
                    in_current_route_flag = False

                seq_df.loc[index,'sampleResLife'] = 0
            test_X.append(seq_df.values[:, :])
            test_y.append(label)

    elif task == 3:
        # get the data from one [1,2,3,4,5], while considering the label for route
        for index_list in train_index_list:

            seq_df = train_df.loc[index_list]
            label = seq_df.loc[index_list[-1]]['nextMinRTT']
            seq_df.drop(['nextMinRTT','nextavgRTT','nextMaxRTT','nextMdevRTT'],axis=1,inplace=True)

            train_X.append(seq_df.values[:, :])
            train_y.append(label)

        # get the data from [34,35,36,37,38,39], while considering the train and test label.
        for index_list in test_index_list:
            seq_df = all_df.loc[index_list]
            label = seq_df.loc[index_list[-1]]['nextMinRTT']
            seq_df.drop(['nextMinRTT', 'nextavgRTT', 'nextMaxRTT', 'nextMdevRTT'], axis=1,inplace=True)

            test_X.append(seq_df.values[:, :])
            test_y.append(label)


    return np.array(train_X),np.array(train_y),np.array(test_X),np.array(test_y),seq_df.shape[1]

def get_lstm_data_from_path(train_path,test_path,task,time_steps,min_samples_for_path=5):
    """
    like get_lstm_data_from_df
    :param train_path:
    :param test_path:
    :param task:
    :param time_steps:
    :param min_samples_for_path:
    :return:
    """
    train_X, train_y, test_X, test_y =[],[],[],[]
    train_file_list = os.listdir(train_path)
    test_file_list = os.listdir(test_path)
    if len(train_file_list)!= len(test_file_list):
        print 'length error!'
        exit(-1)
    print len(train_file_list),'df to process'
    for i in range(len(train_file_list)):
        if i%30==0:
            print i
    # for i in range(10):

        if train_file_list[i] == test_file_list[i]:
            train_X_tmp, train_y_tmp, test_X_tmp, test_y_tmp, feature_num = get_lstm_data_from_df(
                train_df=pd.read_csv(train_path+train_file_list[i]),
                test_df=pd.read_csv(test_path+test_file_list[i]),
                task=task,
                time_steps=time_steps,
                min_samples_for_path=min_samples_for_path
            )
            # print train_X_tmp.shape
            if train_X_tmp!=None and train_y_tmp!=None and test_X_tmp!=None and test_y_tmp!=None:

                train_X.append(train_X_tmp)
                train_y.append(train_y_tmp)
                test_X.append(test_X_tmp)
                test_y.append(test_y_tmp)
            else:

                print 'oops',i


    train_X=np.concatenate(train_X,0)
    print "trainx"
    train_y=np.concatenate(train_y,0)
    print "trainy"

    test_X=np.concatenate(test_X,0)
    print "trx"

    test_y=np.concatenate(test_y,0)
    print "ty"

    return train_X, train_y, test_X, test_y, feature_num

def generate_lstm_data_to_pkl(train_path, test_path, task, time_steps, file_name_in_path,min_samples_for_path=5):
    train_X, train_y, test_X, test_y, feature_num=get_lstm_data_from_path(train_path, test_path, task, time_steps, min_samples_for_path=5)
    with open(file_name_in_path,'w') as fout:
        l = []
        l.append(train_X), l.append(train_y), l.append(test_X), l.append(test_y), l.append(feature_num)
        pkl.dump(l, fout)



def LSTM_task(pkl_data_path,task_name,time_steps=10,epochs=10,batch_size=8192,dropout_rate=0.5,hidden_dimension=128):
    config = tf.ConfigProto()
    config.gpu_options.allow_growth = True
    session = tf.Session(config=config)

    # reshape input to be [samples, time steps, features]
    with open(pkl_data_path, 'rb') as fin:  # interface between whole model and training data
        trainX, trainY, testX, testY, feature_len = pkl.load(fin)
    train_samples = trainX.shape[0]
    test_samples = testX.shape[0]
    trainX = np.reshape(trainX, (-1, feature_len))
    testX = np.reshape(testX, (-1, feature_len))

    # scale the data
    trainAll = np.concatenate([trainX, testX], 0)
    scalerX = MinMaxScaler(feature_range=(0, 1))
    scalerX.fit(trainAll)
    trainX = scalerX.transform(trainX)
    testX = scalerX.transform(testX)
    trainX = np.reshape(trainX, (train_samples, -1, feature_len))
    testX = np.reshape(testX, (test_samples, -1, feature_len))

    trainYAll = np.concatenate([trainY, testY], 0)
    scalerY = MinMaxScaler(feature_range=(0, 1))
    scalerY.fit(trainYAll)
    trainY = scalerY.transform(trainY)
    testY = scalerY.transform(testY)

    # MODLE
    model = Sequential()
    model.add(LSTM(hidden_dimension, input_shape=(time_steps, feature_len)))
    model.add(Dropout(dropout_rate))
    model.add(Dense(1))
    model.compile(loss='mean_squared_error', optimizer='adam')

    # train
    model.fit(trainX, trainY, epochs=epochs, batch_size=batch_size, verbose=2)

    trainPredict = model.predict(trainX)
    testPredict = model.predict(testX)

    trainPredict = scalerY.inverse_transform(trainPredict)
    trainY = scalerY.inverse_transform(trainY)
    testPredict = scalerY.inverse_transform(testPredict)
    testY = scalerY.inverse_transform(testY)

    trainScore = sqrt(mean_squared_error(trainY, trainPredict[:, 0]))
    print('Train Score: %.2f RMSE' % (trainScore))
    testScore = sqrt(mean_squared_error(testY, testPredict[:, 0]))
    print('Test Score: %.2f RMSE' % (testScore))

    output_real_and_predict_data(testY, testPredict[:, 0], '../data/temp_result/', task_name)

