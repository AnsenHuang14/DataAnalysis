# -*- coding: utf8 -*-
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from numpy import linalg 
from scipy import linalg as lin
import read_pgm
class twodPCA:
	def fit_transform(self,X,n_comp=10):
		image_list = list()
		G = np.array([0.0]*(92*92)).reshape(92,92).astype(float)
		Abar = np.array([0.0]*(112*92)).reshape(112,92).astype(float)
		for i in xrange(len(X)):
			Abar = Abar + X.iloc[i].reshape(112,92).astype(float)
		Abar = Abar/float(len(X))
		# Abar = np.mean(Abar,axis=0)
		for i in xrange(len(X)):
			A = X.iloc[i].reshape(112,92).astype(float)
			image_list.append(A)
			A = A-Abar
			A = np.dot(A.T,A)
			G = G + A

		G = G / float(len(X))
		U,S,V = lin.svd(G)
		self.w = U[:,0:n_comp]
		
		self.project_image=list()
		for i in xrange(len(image_list)):
			self.project_image.append(np.dot(image_list[i],self.w))
		
	def transform(self,X):
		image_list = list()
		for i in xrange(len(X)):
			A = X.iloc[i].reshape(112,92).astype(float)
			image_list.append(A)
		project_image=list()
		for i in xrange(len(image_list)):
			project_image.append(np.dot(image_list[i],self.w))
		return project_image

def calDist(X,Y):
	index = [0]*len(X)
	for i in xrange(len(X)):
		Dlist = list()
		for j in xrange(len(Y)):
			TotalD=0.0
			for k in xrange(X[i].shape[1]):
				D=0.0
				for l in xrange(X[i].shape[0]):
					D += (X[i][l,k]-Y[j][l,k])**2
				D = D**0.5
				TotalD+=D
			Dlist.append(TotalD)
			if TotalD<=min(Dlist):
				index[i] = j
	return index

if __name__ == '__main__':
	image_list = list()
	label_list = list()
	for i in xrange(1,41,1):
		for t in xrange(1,11,1):
			image = read_pgm.read_pgm("D:\\PythonScript\\DimensionReduction\\orl_faces\\s"+str(i)+"\\"+str(t)+".pgm", byteorder='<')
			image_list.append(image.ravel())
			label_list.append(i)
	data = pd.DataFrame(image_list)
	data['H'] = label_list
	train_index = list()
	for i in xrange(0,391,10):
		train_index.append(i)
		# train_index.append(i+1)
		train_index.append(i+2)
	# 	train_index.append(i+3)
		train_index.append(i+4)
	# train_index = range(0,400,2)
	test_index = range(400)
	for i in train_index:
		test_index.remove(i)
	train = data.iloc[train_index]
	train.index = range(len(train))
	test = data.iloc[test_index]
	test.index = range(len(test))
	
	for n in range(1,11):
		dpca = twodPCA()
		dpca.fit_transform(train.drop('H',1),n_comp=n)
		newdata = dpca.transform(test.drop('H',1))
		
		index  = calDist(newdata,dpca.project_image)
		err=0.0
		for i in xrange(len(test)):
			if train['H'][index[i]]!=test['H'][i]:
				err+=1.0
		err/=len(test)
		print n,1-err

