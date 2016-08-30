#author: Raihan Masud, raihan.masud@gmail.com
#https://www.linkedin.com/in/raihanmasud

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.style.use('ggplot')
import numpy as np
from sklearn import cross_validation
from sklearn.metrics import mean_absolute_error
from sklearn import ensemble
from sklearn.preprocessing import Imputer
from sklearn.pipeline import Pipeline


def load_data():
  path = "C:/Work/GitHub/disease-spread/RustSurvey+EarthEngine.csv"
  print("loading data...")
  data = pd.read_csv(path, encoding='ISO-8859-1', error_bad_lines=False, dtype='unicode')
  print("finished loading data...\n")
  return data


data = load_data()
print('data statistics \n', data.describe())

print('visualizing label..')
def visualize(column):
    outcomes_count = pd.DataFrame(data[column].value_counts())
    sp_ax = plt.subplot2grid((1, 4), (0, 1), colspan=3)
    app_type_bar = outcomes_count.plot(ax=sp_ax, kind='barh', legend=False)
    app_type_bar.invert_yaxis()
    app_type_bar.set_xlabel("Disabled", fontsize="10")
    plt.show()
visualize('StemRust.Binary')

print('cleaning data.. \n')
#remove 2009 data
data[data['StemRust.Binary'] == 'True'][['ObsYear','StemRust.Binary']].groupby('ObsYear').count()
data[data['StemRust.Binary'] == 'False'][['ObsYear','StemRust.Binary']].groupby('ObsYear').count()
clean_data = data[data['ObsYear'] != '2009']

#remove unnecessay features
clean_data = clean_data.drop(['Location.ID', 'HostGenusID', 'HostGenusNameScientific',
       'HostSpeciesID', 'HostSpeciesNameScientific', 'HostCultivarName',
       'UserInit', 'ObsYear', 'ObsDate', 'SurveySiteID', 'SurveySiteName',
       'SurveyorName', 'InstitutionName', 'LocationName' , 'GrowthStageID',
       'GrowthStageName', 'Comment', 'StemRust.Severity',
       'StemRust.SeverityName', 'StemRust.Incidence',
       'StemRust.IncidenceName', 'StemRust.InfectionType',
       'StemRust.InfectionTypeName', 'LeafRust.Severity',
       'LeafRust.SeverityName', 'LeafRust.Incidence',
       'LeafRust.IncidenceName', 'LeafRust.InfectionType',
       'LeafRust.InfectionTypeName', 'YellowRust.Severity',
       'YellowRust.SeverityName', 'YellowRust.Incidence',
       'YellowRust.IncidenceName', 'YellowRust.InfectionType',
       'YellowRust.InfectionTypeName','YellowRust.Binary','NoRust.Binary'], axis=1)

features = list(clean_data.columns.values)

def f(x):
    if x=='True':
        return 1
    elif x=='False':
        return 0
    else: return x

#conver True/False to 0/1
df_bin=clean_data.applymap(f)


df_bin = df_bin[np.isfinite(df_bin['StemRust.Binary'])]

y = df_bin['StemRust.Binary']
X = df_bin.drop(['StemRust.Binary'], axis=1)



print('imputing data\n..')
#impute data
imp = Imputer(missing_values='NaN', strategy='mean', axis=0)
imp.fit(X)
X = imp.transform(X)


#model1
clf = ensemble.RandomForestClassifier(n_estimators=100, max_depth=None, min_samples_split=1,
                                        random_state=0, max_features="auto")

#model2
# clf = ensemble.GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, max_features=5, max_depth=5,
#                                              min_samples_leaf=3, loss='exponential', random_state=None)

#model3
#clf = ensemble.ExtraTreesClassifier(n_estimators=100, max_depth=None, min_samples_split=10, n_jobs=-1)

#train/test data split
print('spliting training/test data ..\n')
def split_train_data(train_input, labels, t_size):
  # train_test does shuffle and random splits
  X_train, X_test, y_train, y_test = cross_validation.train_test_split(
    train_input, labels, test_size=t_size, random_state=0)
  return X_train, X_test, y_train, y_test
X_train, X_test, y_train, y_test = split_train_data(X, y, 0.2)

print('training model..\n')
mdl = clf.fit(X_train, y_train)

print('feature importance: \n')
feature_imp = mdl.feature_importances_

#feature importance
feature_imp_list = []
features.remove('StemRust.Binary')
for i, feature in enumerate(features):
    feature_imp_list.append((feature,feature_imp[i]))
#sort the list of tuples
feature_imp_list.sort(key=lambda tup:tup[1], reverse=True)
for f_imp in feature_imp_list:
    print('feature {0} importance {1}'.format(f_imp[0], f_imp[1]))


#metrics
print('evaluating metrics ..\n')
score = mdl.score(X_test, y_test)
pred_y = mdl.predict(X_test)
print("model score", score)
print('pricision',precision_score(y_test, pred_y, average='macro', sample_weight=None))
print('recall',recall_score(y_test, pred_y, average='macro', sample_weight=None))
print('F1 measure',f1_score(y_test, pred_y, average='macro', sample_weight=None))
