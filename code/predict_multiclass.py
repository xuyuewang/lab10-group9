# copyright: yueshi@usc.edu, jinhyuns@usc.edu
import pandas as pd
import predict 
import hashlib
import os 
from utils import logger
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import numpy as np

from sklearn.feature_selection import SelectFromModel
from sklearn import datasets
from sklearn.linear_model import LassoCV
from sklearn.linear_model import Lasso
from sklearn.model_selection import KFold
from sklearn.model_selection import GridSearchCV
from sklearn.svm import SVC 
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier 
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import classification_report
from sklearn.metrics import precision_score
from sklearn.metrics import accuracy_score
from sklearn.metrics import f1_score
from sklearn.metrics import recall_score
from sklearn.metrics import confusion_matrix 
from sklearn.metrics import precision_recall_fscore_support

from sklearn.decomposition import PCA

def lassoSelection(X_train, y_train, n):
	'''
	Lasso feature selection.  Select n features. 
	'''
	#lasso feature selection
	#print (X_train)
	clf = LassoCV()
	sfm = SelectFromModel(clf, threshold=0)
	sfm.fit(X_train, y_train)
	X_transform = sfm.transform(X_train)
	n_features = X_transform.shape[1]
	
	#print(n_features)
	while n_features > n:
		sfm.threshold += 0.01
		X_transform = sfm.transform(X_train)
		n_features = X_transform.shape[1]
	features = [index for index,value in enumerate(sfm.get_support()) if value == True  ]
	logger.info("selected features are {}".format(features))
	return features

def specificity_score(y_true, y_predict):
	'''
	true_negative rate
	'''
	true_negative = len([index for index,pair in enumerate(zip(y_true,y_predict)) if pair[0]==pair[1] and pair[0]==0 ])
	real_negative = len([index for index,pair in enumerate(zip(y_true,y_predict)) if pair[0]==0 ])
	return true_negative / real_negative 

def model_fit_predict(X_train,X_test,y_train,y_test):

	np.random.seed(2018)
	from sklearn.linear_model import LogisticRegression
	from sklearn.ensemble import RandomForestClassifier
	from sklearn.ensemble import AdaBoostClassifier
	from sklearn.ensemble import GradientBoostingClassifier
	from sklearn.ensemble import ExtraTreesClassifier
	from sklearn.svm import SVC
	models = {
        'KNeighborsClassifier': KNeighborsClassifier(),
		'SVC': SVC(),
        'GaussianNB' : GaussianNB(),
        'DecisionTreeClassifier': DecisionTreeClassifier(),
        'RandomForestClassifier': RandomForestClassifier(),
	}
	tuned_parameters = {
        'KNeighborsClassifier': {'n_neighbors': [1,10]},
		'SVC': {'kernel': ['linear'], 'C': [1, 10], 'gamma': [0.001, 0.0001]},
        'GaussianNB': {},
        'DecisionTreeClassifier': {'max_depth' : [1,10]},
        'RandomForestClassifier': {'n_jobs':[1,10], 'random_state':[0,9]},
	}
	scores= {}
	for key in models:
		clf = GridSearchCV(models[key], tuned_parameters[key], scoring=None,  refit=True, cv=10)
		clf.fit(X_train,y_train)

		y_test_predict = clf.predict(X_test)
        # average = 'micro','macro', or 'weighted' 
		precision = precision_score(y_test, y_test_predict, average = 'weighted')
		accuracy = accuracy_score(y_test, y_test_predict)
		f1 = f1_score(y_test, y_test_predict, average = 'weighted')
		recall = recall_score(y_test, y_test_predict, average = 'weighted')
		specificity = specificity_score(y_test, y_test_predict) 
		scores[key] = [precision,accuracy,f1,recall,specificity]
	#print(scores)
	return scores

def draw(scores):
	'''
	draw scores.
	'''
	import matplotlib.pyplot as plt
	logger.info("scores are {}".format(scores))
	ax = plt.subplot(111)
	precisions = []
	accuracies =[]
	f1_scores = []
	recalls = []
	categories = []
	specificities = []
	N = len(scores)
	ind = np.arange(N)  # set the x locations for the groups
	width = 0.1        # the width of the bars
	for key in scores:
		categories.append(key)
		precisions.append(scores[key][0])
		accuracies.append(scores[key][1])
		f1_scores.append(scores[key][2])
		recalls.append(scores[key][3])
		specificities.append(scores[key][4])

	precision_bar = ax.bar(ind, precisions,width=0.1,color='b',align='center')
	accuracy_bar = ax.bar(ind+1*width, accuracies,width=0.1,color='g',align='center')
	f1_bar = ax.bar(ind+2*width, f1_scores,width=0.1,color='r',align='center')
	recall_bar = ax.bar(ind+3*width, recalls,width=0.1,color='y',align='center')
	specificity_bar = ax.bar(ind+4*width,specificities,width=0.1,color='purple',align='center')

	print(categories)
	ax.set_xticks(np.arange(N))
	ax.set_xticklabels(categories)
	ax.legend((precision_bar[0], accuracy_bar[0],f1_bar[0],recall_bar[0],specificity_bar[0]), ('precision', 'accuracy','f1','sensitivity','specificity'))
	ax.grid()
	plt.show()

data_dir ="./data/" #C:\Users\jinhy\Documents\GitHub\ee542-lab10-group9

data_file = data_dir + "miRNA_matrix_multi_v2.csv"

df = pd.read_csv(data_file)
# print(df)
y_data = df.pop('label_primary').values
df.pop('file_id')

columns =df.columns
#print (columns)
X_data = df.values

logger.info("X_Data size is {}".format(np.shape(X_data)))
logger.info("Y_Data size is {}".format(np.shape(y_data)))

# PCA starts here
pca = PCA(n_components=50)
pca_result = pca.fit_transform(df.values)
X_data = pca_result
print('Cumulative explained variation for 50 principal components: {}'.format(np.sum(pca.explained_variance_ratio_)))
np.shape(X_data)

# split the data to train and test set
X_train, X_test, y_train, y_test = train_test_split(X_data, y_data, test_size=0.8, random_state=2018)
	

#standardize the data.
scaler = StandardScaler()
scaler.fit(X_train)
X_train = scaler.transform(X_train)
X_test = scaler.transform(X_test)

# check the distribution of tumor and normal sampels in traing and test data set.
logger.info("Percentage of tumor cases in training set is {}".format(sum(y_train)/len(y_train)))
logger.info("Percentage of tumor cases in test set is {}".format(sum(y_test)/len(y_test)))

''' Skip the lasso selection
n = 7
feaures_columns = lassoSelection(X_train, y_train, n)
'''

# 1.KNN
'''
knn = KNeighborsClassifier(n_neighbors = 7).fit(X_train, y_train) 
accuracy = knn.score(X_test, y_test) 
logger.info("Accuracy of KNN is {}".format(accuracy))
   
knn_predictions = knn.predict(X_test)  
cm = confusion_matrix(y_test, knn_predictions) 
'''

# 2. SVM

svm_model_linear = SVC(kernel = 'linear', C = 1).fit(X_train, y_train) 
svm_predictions = svm_model_linear.predict(X_test) 
    
accuracy = svm_model_linear.score(X_test, y_test) 
logger.info("Accuracy of SVM is {}".format(accuracy))
print(classification_report(y_test, svm_predictions))


# 3. GNB
'''
gnb = GaussianNB().fit(X_train, y_train) 
gnb_predictions = gnb.predict(X_test) 
  
accuracy = gnb.score(X_test, y_test) 
logger.info("Accuracy of GNB is {}".format(accuracy)) 
cm = confusion_matrix(y_test, gnb_predictions) 

# 4. DTree
dtree_model = DecisionTreeClassifier(max_depth = 2).fit(X_train, y_train) 
dtree_predictions = dtree_model.predict(X_test) 

accuracy = dtree_model.score(X_test, y_test) 
logger.info("Accuracy of Decision Tree is {}".format(accuracy)) 
cm = confusion_matrix(y_test, dtree_predictions) 
'''


#scores = model_fit_predict(X_train[:,feaures_columns],X_test[:,feaures_columns],y_train,y_test)
scores = model_fit_predict(X_train,X_test,y_train,y_test)
draw(scores)
