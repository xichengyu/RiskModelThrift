# coding=utf-8

from sklearn.externals import joblib


def main(x):
    model = joblib.load("yuecai_0304.m.xgb")
    result = model.predict(x)
    return result