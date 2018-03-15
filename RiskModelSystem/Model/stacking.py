"""模型训练和预测"""
import numpy as np
import pandas as pd

import xgboost
import lightgbm
import catboost
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.externals import joblib
import os


def calc_class_weight(y, class_weight='balanced'):
    """计算类权重
    Args:
        y: 真实label, 一维int序列, 取值>=0
        class_weight: 'balanced', None或序列
            'balanced', 根据每类样本数自动确定均衡的类权重
            None: 权重全部为1.0
            序列: 手动指定类权重
    Returns:
        每个类别的权重, 一维numpy array, float类型
    """
    y = np.array(y).astype(np.int32)
    bincount = np.bincount(y)
    if class_weight == 'balanced':
        class_weight = len(y) / (len(bincount) * bincount)
    elif isinstance(class_weight, collections.Sequence):
        class_weight = np.array(class_weight)
    else:
        class_weight = np.ones(len(bincount))
    return class_weight.astype(np.float32)

def calc_sample_weight(y, class_weight='balanced'):
    """根据类权重计算样本权重
    Args:
        y: 真实label, 一维int序列, 取值>=0
        class_weight: 'balanced', None或序列
            'balanced', 根据每类样本数自动确定均衡的类权重
            None: 权重全部为1.0
            序列: 手动指定类权重
    Returns:
        每个样本的权重, 一维numpy array, float类型, 和y同size
    """
    y = np.array(y).astype(np.int32)
    sample_weight = np.ones(len(y), dtype=np.float32)
    class_weight = calc_class_weight(y, class_weight)
    one_hot = np.zeros((len(y), len(class_weight)))
    one_hot[np.arange(len(y)), y] = 1
    sample_weight *= np.sum(one_hot * class_weight, axis=1)
    return sample_weight


lightgbm_params = dict(subsample=0.7,
                       reg_lambda=0.1,
                       reg_alpha=0.05,
                       num_leaves=63,
                       n_estimators=280,
                       min_child_weight=4,
                       min_child_samples=80,
                       max_bin=200,
                       learning_rate=0.05,
                       colsample_bytree=0.9,
                       n_jobs=10,
                       verbose=0)

xgboost_params = dict(learning_rate=0.25,
                      max_depth=5,
                      objective='binary:logistic',
                      eval_metric='error',
                      silent=True)

catboost_params = dict(iterations=100,
                       learning_rate=0.2,
                       depth=8,
                       logging_level='Silent')

lr_params = dict()
rf_params = dict(n_estimators=90,
                 max_depth=10,
                 n_jobs=10)


def train(df, name='xgboost', params=None):
    """模型训练
    Args:
        df: DataFrame, 有一列为'label', 之后所有列为指标
        name: 'xgboost', 'lightgbm', 'catboost', 'lr', 'rf'...(TODO: 待添加), 模型类型
        params: 模型参数, 如果为None则使用定义好的默认参数
    Returns:
        训练好的模型对象
    """
    idx = list(df.columns).index('label')
    X, y = df.iloc[:, idx+1:], df.iloc[:, idx]
    if name == 'xgboost':
        dtrain = xgboost.DMatrix(data=X, label=y)
        dtrain.set_weight(calc_sample_weight(y))
        if params is None:
            params = xgboost_params
        return xgboost.train(params=params, dtrain=dtrain, num_boost_round=90)
    elif name == 'lightgbm':
        if params is None:
            params = lightgbm_params
        lb = lightgbm.LGBMClassifier(**params)
        lb.fit(X, y, sample_weight=calc_sample_weight(y))
        return lb
    elif name == 'catboost':
        if params is None:
            params = catboost_params
        cb = catboost.CatBoostClassifier(**params)
        cb.fit(X, y, sample_weight=calc_sample_weight(y))
        return cb
    elif name == 'lr':
        if params is None:
            params = lr_params
        lr = LogisticRegression(class_weight='balanced', **params)
        lr.fit(X, y)
        return lr
    elif name == 'rf':
        if params is None:
            params = rf_params
        rf = RandomForestClassifier(class_weight='balanced', **params)
        rf.fit(X, y)
        return rf
    else:
        raise ValueError('Unsupported model type %s, supported model names are %s' % (name, ['xgboost', 'lightgbm', 'catboost', 'rf', 'lr']))


def train_multi(df, name='xgboost', params=None, num=20, bootstrap=True):
    """训练多个模型, 每个模型基于原始数据集上随机采样出的不同数据集训练

    Args:
        df: DataFrame, 有一列为'label', 之后所有列为指标
        name: 模型类型 
        params: 模型参数, 如果为None则使用定义好的默认参数
        num: 需要训练的模型数量
        bootstrap: 是否采用放回抽样
    Returns:
        模型列表
    """
    estimators = []
    idx = list(df.columns).index('label')
    for i in range(num):
        print('Training #%d %s estimator' % (i, name))
        df_sample = df.iloc[np.random.choice(len(df), len(df), replace=bootstrap), :]
        estimators.append(train(df_sample, name, params))
    return estimators


def predict(estimator, df):
    """模型推断
    Args:
        estimator: 模型对象
        df: DataFrame, 有一列为'label', 之后所有列为指标
    Returns:
        一维numpy array, float型, 表示模型预测为正类的概率
    """
    idx = list(df.columns).index('label')
    X = df.iloc[:, idx+1:]
    if isinstance(estimator, xgboost.Booster):
        dtest = xgboost.DMatrix(X)
        return estimator.predict(dtest)
    elif callable(getattr(estimator, 'predict_proba', None)):
        return estimator.predict_proba(X)[:, 1]
    else:
        return estimator.predict(X)


def predict_multi(estimators, df):
    """多个模型推断
    Args:
        estimators: 模型对象列表
        df: DataFrame, 有一列为'label', 之后所有列为指标
    Returns:
        二维numpy array, float型, [n_samples, n_estimators], 
        每一列表示一个模型的预测结果
    """
    Y = np.ones((len(df), len(estimators)))
    for i, estimator in enumerate(estimators):
        Y[:, i] = predict(estimator, df)
    return Y

def predict_mean(estimators, df):
    """多个模型推断做平均
    Args:
        estimator: 模型对象
        df: DataFrame, 有一列为'label', 之后所有列为指标
    Returns:
        一维numpy array, float型, 所有模型预测取平均的结果
    """
    return predict_multi(estimators, df).mean(axis=-1)


def train_basic(df, names, kfold=5):
    assert isinstance(kfold, int) and kfold >1 and kfold < 100
    if isinstance(names, str):
        names = [names]
    assert isinstance(names, list)
    names = list(set(names))

    fold_size = len(df) // kfold
    eses = {}
    Y = np.ones((len(df), len(names)))
    for i in range(kfold):
        if i == 0:
            df_train = df.iloc[:fold_size, :]
        elif i == kfold-1:
            df_train = df.iloc[fold_size * i:, :]
        else:
            df_train = pd.concat([df.iloc[:fold_size*i, :], df.iloc[fold_size*(i+1):, :]])
        df_test = df.iloc[fold_size*i:fold_size*(i+1), :]
        
        for j, name in enumerate(names):
            es = train(df_train, name)
            y_ = predict(es, df_test)
            Y[fold_size*i:fold_size*(i+1), j] = y_
            if name not in eses:
                eses[name] = []
            eses[name].append(es)

    idx = list(df.columns).index('label')
    df_eses = pd.concat([df.iloc[:, :idx+1], pd.DataFrame(Y, columns=names, index=df.index)], axis=1)
    return eses, df_eses

def convert_df(eses, df):
    idx = list(df.columns).index('label')
    #X = df.iloc[:, idx+1:]
    Y = np.ones((len(df), len(eses)))
    for i, name in enumerate(eses):
        Y[:, i] = predict_multi(eses[name], df).mean(axis=1)
    # return pd.DataFrame(Y, index=df.index, columns=eses.keys())
    return pd.concat([df.iloc[:, :idx+1], pd.DataFrame(Y, index=df.index, columns=eses.keys())], axis=1)


class StackedModel(object):
    def __init__(self):
        self.eses = None
        self.lr = None

    def fit(self, df, names, kfold=5):
        self.eses, df_eses = train_basic(df, names, kfold=kfold)
        # df = convert_df(self.eses, df)
        self.lr = train(df_eses, 'lr')

    def predict(self, X):
        df = pd.DataFrame(X)
        fake_label = pd.DataFrame(np.ones((len(X), 1)), index=df.index, columns=['label'])
        df = pd.concat([fake_label, df], axis=1)
        df = convert_df(self.eses, df)
        return predict(self.lr, df)

