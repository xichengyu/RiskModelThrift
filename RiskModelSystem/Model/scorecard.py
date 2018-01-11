# coding=utf-8

# import sys
from sklearn.metrics import roc_auc_score
import traceback
from sklearn.externals import joblib
import numpy as np
import math
from scipy import stats
from sklearn.utils.multiclass import type_of_target
import logging
from collections import Counter
# from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import DecisionTreeRegressor
from treeinterpreter import treeinterpreter as ti
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='[%Y-%m-%d %H:%M:%S]', filename='conf/discretion.log', filemode='w')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)


class WOE(object):
    def __init__(self):
        self._WOE_MIN = -20
        self._WOE_MAX = 20
        self._WOE_N = 20
        self._DISCRETION = "percentile_discrete"
        self.interval = []

    def woe(self, X, y, event=1):
        """
        Calculate woe of each feature category and information value
        :param X: 2-D numpy array explanatory features which should be discreted already
        :param y: 1-D numpy array target variable which should be binary
        :param event: value of binary stands for the event to predict
        :return: numpy array of woe dictionaries, each dictionary contains woe values for categories of each feature
                 numpy array of information value of each feature
        """
        self.check_target_binary(y)
        X1, self.interval = self.feature_discretion(X, y)

        res_woe = []
        res_iv = []
        for i in range(0, X1.shape[-1]):
            x = X1[:, i]
            woe_dict, iv1 = self.woe_single_x(x, y, event)
            res_woe.append(woe_dict)
            res_iv.append(iv1)
        return X1, np.array(res_woe), np.array(res_iv)

    def woe_single_x(self, x, y, event=1):
        """
        calculate woe and information for a single feature
        :param x: 1-D numpy starnds for single feature
        :param y: 1-D numpy array target variable
        :param event: value of binary stands for the event to predict
        :return: dictionary contains woe values for categories of this feature
                 information value of this feature
        """
        self.check_target_binary(y)

        event_total, non_event_total = self.count_binary(y, event=event)
        x_labels = np.unique(x)
        woe_dict = {}
        iv = 0
        for x1 in x_labels:
            y1 = y[np.where(x == x1)[0]]
            event_count, non_event_count = self.count_binary(y1, event=event)
            rate_event = 1.0 * event_count / event_total
            rate_non_event = 1.0 * non_event_count / non_event_total
            if rate_event == 0:
                woe1 = self._WOE_MIN
            elif rate_non_event == 0:
                woe1 = self._WOE_MAX
            else:
                woe1 = math.log(rate_event / rate_non_event)
            woe_dict[x1] = woe1
            iv += (rate_event - rate_non_event) * woe1
        return woe_dict, iv

    def woe_replace(self, X, woe_arr):
        """
        replace the explanatory feature categories with its woe value
        :param X: 2-D numpy array explanatory features which should be discreted already
        :param woe_arr: numpy array of woe dictionaries, each dictionary contains woe values for categories of each feature
        :return: the new numpy array in which woe values filled
        """
        if X.shape[-1] != woe_arr.shape[-1]:
            raise ValueError('WOE dict array length must be equal with features length')

        res = np.copy(X).astype(float)
        idx = 0
        for woe_dict in woe_arr:
            for k in woe_dict.keys():
                woe = woe_dict[k]
                res[:, idx][np.where(res[:, idx] == k)[0]] = woe * 1.0
            idx += 1
        return res, self.interval

    def combined_iv(self, X, y, masks, event=1):
        """
        calcute the information vlaue of combination features
        :param X: 2-D numpy array explanatory features which should be discreted already
        :param y: 1-D numpy array target variable
        :param masks: 1-D numpy array of masks stands for which features are included in combination,
                      e.g. np.array([0,0,1,1,1,0,0,0,0,0,1]), the length should be same as features length
        :param event: value of binary stands for the event to predict
        :return: woe dictionary and information value of combined features
        """
        if masks.shape[-1] != X.shape[-1]:
            raise ValueError('Masks array length must be equal with features length')

        x = X[:, np.where(masks == 1)[0]]
        tmp = []
        for i in range(x.shape[0]):
            tmp.append(self.combine(x[i, :]))

        dumy = np.array(tmp)
        # dumy_labels = np.unique(dumy)
        woe, iv = self.woe_single_x(dumy, y, event)
        return woe, iv

    def combine(self, list):
        res = ''
        for item in list:
            res += str(item)
        return res

    def count_binary(self, a, event=1):
        # Error may occur when code running on linux environment, consider add ".astype()"
        event_count = (a == event).astype(int).sum()
        non_event_count = a.shape[-1] - event_count
        return event_count, non_event_count

    def check_target_binary(self, y):
        """
        check if the target variable is binary, raise error if not.
        :param y:
        :return:
        """
        y_type = type_of_target(y)
        if y_type not in ['binary']:
            raise ValueError('Label type must be binary')

    def interval_point(self, x, n=20):
        """
        Get the lower and upper point of one interval
        :param x:
        :param n:
        :return:
        """
        interval = []
        set_x = sorted(set(x))
        max_set_x, min_set_x = max(set_x), min(set_x)
        if len(set_x) <= n:
            interval.append((0, min_set_x))
            for i in range(len(set_x)-2):
                interval.append((set_x[i], set_x[i+1]))
            interval.append((set_x[len(set_x)-2], float("inf")))
        else:
            gap = (max_set_x - min_set_x)/(n-1)*1.0
            interval.append((0, min_set_x))
            for i in range(n-2):
                interval.append((min_set_x+i*gap, min_set_x+(i+1)*gap))
            interval.append((min_set_x+(n-2)*gap, float("inf")))
        return interval

    def feature_discretion(self, X, y):
        """
        Discrete the continuous features of input data X, and keep other features unchanged.
        :param X : numpy array
        :return: the numpy array in which all continuous features are discrete
        """
        temp, X_interval = [], []
        if self._DISCRETION == "percentile_discrete":
            for i in range(0, X.shape[-1]):
                x = X[:, i]
                x_type = type_of_target(x)
                logging.info("before: "+" ".join([str(i), str(set(X[:, i])), str(x_type)]))
                if 0:
                    if x_type == 'continuous':
                        x1, interval = self.percentile_discrete(x, self._WOE_N)
                        X_interval.append(interval)
                        temp.append(x1)
                        logging.info("continue_after: " + " ".join([str(i), str(set(x1)), str(x1)]))
                    else:
                        temp.append(x)
                        logging.info("after: " + " ".join([str(i), str(set(x)), str(x)]))
                else:
                    x1, interval = self.percentile_discrete(x, self._WOE_N)
                    X_interval.append(interval)
                    temp.append(x1)
                    logging.info("continue_after: " + " ".join([str(i), str(set(x1)), str(x1)]))
        elif self._DISCRETION == "interval_discrete":
            for i in range(0, X.shape[-1]):
                x = X[:, i]
                logging.info("before: "+" ".join([str(i), str(set(X[:, i]))]))
                x1, interval = self.interval_discrete(x, self._WOE_N)
                X_interval.append(interval)
                temp.append(x1)
                logging.info("interval_after: " + " ".join([str(i), str(set(x1)), str(x1)]))
        elif self._DISCRETION == "rf_discrete":
            for i in range(0, X.shape[-1]):
                x = X[:, i]
                logging.info("before: "+" ".join([str(i), str(set(X[:, i]))]))
                x1, interval = self.rf_discrete(x, y)
                X_interval.append(interval)
                temp.append(x1)
                logging.info("rf_after: " + " ".join([str(i), str(set(x1)), str(x1)]))
        return np.array(temp).T, X_interval

    def percentile_discrete(self, x, n=20):
        """
        Discrete the input 1-D numpy array based on percentile
        :param n: the number of discretion
        :param x: 1-D numpy array
        :return: discreted 1-D numpy array
        """
        res = np.array([0] * x.shape[-1], dtype=int)
        logging.info("before_counter: " + str(Counter(x)))
        x_temp = x[x != -1.0]
        interval_list = []
        for i in range(1+n):
            if i == 0:
                x1 = x[np.where(x == -1.0)]
                mask = np.in1d(x, x1)
                res[mask] = (i + 1)
                logging.info("discrete: " + str((-1.0, -1.0)))
                point1, point2 = -1, -1
            else:
                point1, point2 = stats.scoreatpercentile(x_temp, [(i-1)*100/n, i*100/n])
                x1 = x[np.where((x >= point1) & (x <= point2))]
                mask = np.in1d(x, x1)
                res[mask] = (i + 1)
                logging.info("discrete: " + str(res) + str((point1, point2)))
            interval_list.append((point1, point2))
            logging.info("mask: " + str(mask))
        logging.info("discrete_main: " + str(res))
        logging.info("discrete_counter: " + str(Counter(res)))
        return res, interval_list

    def interval_discrete(self, x, n=20):
        """
        Discrete the input 1-D numpy array based on interval
        :param n: the number of discretion
        :param x: 1-D numpy array
        :return: discreted 1-D numpy array
        """
        res = np.array([0] * x.shape[-1], dtype=int)
        logging.info("before_counter: " + str(Counter(x)))
        x_temp = x[x != -1.0]
        interval_list = [(-1.0, -1.0)] + self.interval_point(x_temp, n)
        for i, point in enumerate(interval_list):
            point1, point2 = point[0], point[1]
            if point1 == point2:
                x1 = x[np.where((x >= point1) & (x <= point2))]
            else:
                x1 = x[np.where((x > point1) & (x <= point2))]
            mask = np.in1d(x, x1)
            res[mask] = (i + 1)
            logging.info("discrete: " + str(res) + str((point1, point2)))
            logging.info("mask: " + str(mask))
        logging.info("discrete_main: " + str(res))
        logging.info("discrete_counter: " + str(Counter(res)))
        logging.info("interval_point: " + str(interval_list))
        return res, interval_list

    def rf_discrete(self, x, y):
        """
        Discrete the input 1-D numpy array based on RandomForest
        :param x: 1-D numpy array
        :param y: 1-D numpy array target variable
        :return: discreted 1-D numpy array
        """
        res = np.array([0] * x.shape[-1], dtype=int)
        interval_list = []
        x = np.column_stack((x, res))
        # model = RandomForestRegressor(n_estimators=60, max_depth=10)
        model = DecisionTreeRegressor(max_depth=10)
        model.fit(x, y)
        prediction, bias, contribution = ti.predict(model, x)
        print(prediction, "\n", bias, "\n", contribution)
        '''
        for i in range(n):
            point1, point2 = stats.scoreatpercentile(x, [i*100/n, (i+1)*100/n])
            x1 = x[np.where((x >= point1) & (x <= point2))]
            mask = np.in1d(x, x1)
            res[mask] = (i + 1)
            logging.info("discrete: " + str(res) + str((point1, point2)))
            logging.info("mask: " + str(mask))
        logging.info("discrete_main: " + str(res))       
        '''
        # raise ValueError
        return res, interval_list

    def test_percentile_discrete(self, test_X, interval=None):
        """
        Discrete the input 2-D test numpy array based on percentile
        :param test_X: 1-D numpy array
        :param interval: X_interval
        :return: discreted 1-D test numpy array
        """
        if not interval:
            interval = self.interval
        temp = []
        for idx in range(test_X.shape[-1]):
            x = test_X[:, idx]
            res = np.array([0] * x.shape[-1], dtype=int)
            logging.info("test_before_counter: " + str(Counter(x)))
            for i, point in enumerate(interval[idx]):
                point1, point2 = point[0], point[1]
                x1 = x[np.where((x >= point1) & (x <= point2))]
                mask = np.in1d(x, x1)
                res[mask] = (i + 1)
                logging.info("test_discrete: " + str(res) + str((point1, point2)))
                logging.info("test_mask: " + str(mask))
                logging.info("test_interval_point: " + str(point))
            logging.info("test_discrete_main: " + str(res))
            logging.info("test_discrete_counter: " + str(Counter(res)))
            temp.append(res)
        return np.array(temp).T

    def test_interval_discrete(self, test_X, interval=None):
        """
        Discrete the input 2-D test numpy array based on interval
        :param test_X: 2-D numpy array
        :param interval: X_interval
        :return: discreted 1-D test numpy array
        """
        if not interval:
            interval = self.interval
        temp = []
        for idx in range(test_X.shape[-1]):
            x = test_X[:, idx]
            res = np.array([0] * x.shape[-1], dtype=int)
            logging.info("test_before_counter: " + str(Counter(x)))
            for i, point in enumerate(interval[idx]):
                point1, point2 = point[0], point[1]
                if point1 == point2:
                    x1 = x[np.where((x >= point1) & (x <= point2))]
                else:
                    x1 = x[np.where((x > point1) & (x <= point2))]
                mask = np.in1d(x, x1)
                res[mask] = (i + 1)
                logging.info("test_discrete: " + str(res) + str((point1, point2)))
                logging.info("test_mask: " + str(mask))
                logging.info("test_interval_point: " + str(point))
            logging.info("test_discrete_main: " + str(res))
            logging.info("test_discrete_counter: " + str(Counter(res)))
            temp.append(res)
        return np.array(temp).T

    @property
    def WOE_MIN(self):
        return self._WOE_MIN

    @WOE_MIN.setter
    def WOE_MIN(self, woe_min):
        self._WOE_MIN = woe_min

    @property
    def WOE_MAX(self):
        return self._WOE_MAX

    @WOE_MAX.setter
    def WOE_MAX(self, woe_max):
        self._WOE_MAX = woe_max

    @property
    def WOE_N(self):
        return self._WOE_N

    @WOE_N.setter
    def WOE_N(self, woe_n):
        self._WOE_N = woe_n

    @property
    def DISCRETION(self):
        return self._DISCRETION

    @DISCRETION.setter
    def DISCRETION(self, discretion):
        self._DISCRETION = discretion


def get_scale_location(base_score=600.0, gap=20.0, odds=10.0):
    """
    score = ln(odds)*scale + location
    :param base_score:
    :param gap:
    :param odds: the ratio of good/bad
    :return: scale, location
    """
    if isinstance(base_score, float) and isinstance(gap, float):
        scale = gap/(math.log(2*odds)-math.log(odds))
        location = base_score - math.log(odds)*scale
        return scale, location
    else:
        return "Param type error, float is needed!"


def get_raw_data(data_dir, default=-1, y_idx=0):
    """
    load joblib format data from local place
    :param data_dir: data directory
    :param default:
    :param y_idx: the index of y
    :return:
    """
    data = np.array(joblib.load(data_dir))
    for idx in range(data.shape[-1]):        # replace non_type value with -1.0
        data[:, idx][np.where((data[:, idx] == '') | (data[:, idx] == None) | (data[:, idx] == "NULL"))[0]] = default
    data = data.astype(float)
    if y_idx == 0:
        train_X = data[:, 1:]
        train_y = data[:, 0]
    else:
        train_X = data[:, :-1]
        train_y = data[:, -1]
    data = np.column_stack((train_X, train_y))
    return data


def get_train_test_data(data, target_fields=None):
    if not target_fields:
        target_fields = []
    train_data = []
    test_data = []
    try:
        '''create train_data, test_data'''
        randsamp = ds.RandSamp()
        randsamp.MULTIPLE = 1
        randsamp.Y_IDX = -1
        randsamp.TRAIN_PERCENTILE = 0.8
        train_data, test_data = randsamp.random_sampling(data)

    except:
        traceback.print_exc()
        pass
    return train_data, test_data


def main(X):
    woe_score = joblib.load("./conf/woe_score.nparray")
    X_interval = joblib.load("./conf/X_interval.nparray")
    scale_location = joblib.load("./conf/scale_location.coef")
    scale = scale_location[0]
    location = scale_location[1]
    # X = joblib.load("./conf/X.nparray")
    # y = joblib.load("./conf/y.nparray")

    # 计算woe
    cal_woe = WOE()
    cal_woe.WOE_MAX = 1
    cal_woe.WOE_MIN = -1
    cal_woe.WOE_N = 10
    cal_woe.DISCRETION = "interval_discrete"  # rf_discrete, percentile_discrete, interval_discrete

    # 测试集分箱
    def get_score(test_X):
        test_X_discretion = []
        if cal_woe.DISCRETION == "percentile_discrete":
            test_X_discretion = cal_woe.test_percentile_discrete(test_X, X_interval)
        elif cal_woe.DISCRETION == "interval_discrete":
            test_X_discretion = cal_woe.test_interval_discrete(test_X, X_interval)

        print(test_X_discretion.shape)
        joblib.dump(test_X_discretion, "./conf/test_X_discretion.nparray")

        # 计算测试集woe score
        test_X_woe_replace, test_X_interval = cal_woe.woe_replace(test_X_discretion, woe_score)
        joblib.dump(test_X_woe_replace, "./conf/test_X_woe_score.nparray")

        # 计算各用户score
        score = []
        for idx in range(test_X_woe_replace.shape[0]):
            score.append(location+sum(test_X_woe_replace[idx, :]))
        joblib.dump(score, "./conf/score.nparray")

        return score

    # get_score(test_X)
    X_score = get_score(X)
    print(scale, location)

    '''
    # 参数设定
    n = 400
    positive_y = 1
    credit_score_upper = 1000
    credit_score_lower = 0

    # 加载数据
    # y = joblib.load("./conf/test_y.nparray")
    y = joblib.load("./conf/y.nparray")
    score = joblib.load("./conf/score.nparray")
    woe_score = joblib.load("./conf/woe_score.nparray")
    print("total: ", y.shape, "bad_total: ", sum(y))

    # 统计原始score的极值与KS值
    max_score = max(score)
    min_score = min(score)
    gap = (max_score-min_score)/n
    x_label = [min_score+i*gap for i in range(n+1)]
    x_label[-1] = max_score
    # ks_max = met.ROC("lr", "None", score, y, "conf/ks.log", 0, 0, thresholds=x_label)

    # 计算可能出现的score的极值，根据woe_score
    sum_max_woe_score, sum_min_woe_score = location, location
    for score_dict in woe_score:
        sum_max_woe_score += max(score_dict.values())
        sum_min_woe_score += min(score_dict.values())

    # 计算原始score到credit_score的映射参数
    a = (sum_min_woe_score-sum_max_woe_score)/(credit_score_upper-credit_score_lower)
    b = sum_min_woe_score-a*credit_score_upper

    print("a: ", a, "b: ", b)
    print("sum_max_woe_score: ", sum_max_woe_score, "sum_min_woe_score: ", sum_min_woe_score)
    print("max_score: ", max_score, "min_score: ", min_score, "gap: ", gap)
    print("auc: ", roc_auc_score(y, score))

    # 计算原始score对应的credit_score
    score = (score-b)/a
    max_score = max(score)
    min_score = min(score)
    gap = (max_score-min_score)/n
    print("max_credit_score: ", max_score, "min_credit_score: ", min_score, "gap: ", gap)

    x_label = [min_score+i*gap for i in range(n+1)]
    x_label[-1] = max_score

    cnt_dict = {}
    cnt_dict_1 = {}
    for j, item in enumerate(score):
        for i in range(n):
            if item <= x_label[i+1]:
                cnt_dict[i] = cnt_dict.get(i, 0)+1
                cnt_dict_1[i] = cnt_dict_1.get(i, 0)+(1 if y[j] == positive_y else 0)
                break

    for i in range(n):
        if i in cnt_dict:
            print("interval: ", (x_label[i], x_label[i+1]), "interval_total: ", cnt_dict[i], "interval_bad_total: ",
                  cnt_dict_1[i], "interval_bad_rate: ", cnt_dict_1[i]/cnt_dict[i])
    '''
    # cnt_dict = dict(sorted(cnt_dict.items(), key=lambda d: d[0]))
    # BarChart(list(cnt_dict.keys()), list(cnt_dict.values()), chart_name="ctrip_credit_score")

    return X_score