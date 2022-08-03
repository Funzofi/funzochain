import torch
import torch.nn as nn
import pickle
import rsa
import pandas as pd
import numpy as np
from sklearn.svm import SVC
import os	

class Generator(nn.Module):
	def __init__(self):
		super(Generator, self).__init__()
		self.encoder = nn.Sequential(
			nn.Linear(128, 80),
			nn.ReLU(True),
			nn.Linear(80, 64),
			nn.ReLU(True), 
			nn.Linear(64, 32), 
			nn.ReLU(True),
			nn.Linear(32, 8)
		)
		
		self.decoder = nn.Sequential(
			nn.Linear(8, 32),
			nn.ReLU(True),
			nn.Linear(32, 64),
			nn.ReLU(True),
			nn.Linear(64, 80),
			nn.ReLU(True),
			nn.Linear(80, 128)
		)

		self.new = False

		try:
			self.load_state_dict(torch.load('gan-gen'))
		except:
			self.new = True
	
	def train(self, chain):
		self.learning_rate = 1e-3
		self.criterion = nn.MSELoss()
		self.optimizer = torch.optim.Adam(self.parameters(), lr=self.learning_rate, weight_decay=1e-5)
		
		input_ = []
		output_ = []
		for i in range(len(chain)-1):
			if len(input_) == 512:
				break
			input_.append(list(chain[i].seed))
			print(i)
			output_.append(list(chain[i+1].seed))

		self.inp=torch.tensor(input_,dtype=torch.float32)
		self.out=torch.tensor(output_,dtype=torch.float32)
		self.test_inp=self.inp[384:]
		self.test_out=self.out[384:]
		self.inp=self.inp[:384]
		self.out=self.out[:384]

		for epoch in range(5000):
			output = self(self.inp)
			loss = self.criterion(output , self.out)
			self.optimizer.zero_grad()
			loss.backward()
			self.optimizer.step()

			print('epoch [{}/{}], loss:{:.4f}'.format(epoch + 1, 5000, loss.item()))

			torch.save(self.state_dict(),'gan-gen')

	def forward(self,x):
		x = self.encoder(x)
		x = self.decoder(x)
		return x
  
	def gen(self, seed_root):
		tensor_=torch.tensor(list(seed_root), dtype=torch.float32)
		score = self(tensor_)
		score =  torch.round(score)
		score = score.detach().numpy()
		return score

class Descriminator():
	def __init__(self):
		
		self.new = False

		try:
			self.classifier = pickle.load(open('gan-desc', 'rb'))
		except:
			self.new = True

	def train(self, chain):
		input_ = []
		output_ = []
		for i in range(len(chain)-1):
			if len(input_) == 512:
				break
			input_.append(list(chain[i].seed))
			print(i)
			output_.append(list(chain[i+1].seed))

		self.inp=torch.tensor(input_,dtype=torch.float32)
		self.out=torch.tensor(output_,dtype=torch.float32)
		self.test_inp=self.inp[384:]
		self.test_out=self.out[384:]
		self.inp=self.inp[:384]
		self.out=self.out[:384]

		generator = Generator()

		output_ = generator(self.inp)
		output_ =  torch.round(output_)
		output_=output_.detach().numpy()
		
		temp=output_
		df1=pd.DataFrame(temp)
		df1['label']=0
	
		temp=self.out.detach().numpy()
		df2=pd.DataFrame(temp)
		df2['label']=1
	
		df=df1.append(df2, ignore_index = True)
		df=df.sample(frac=1)
	
		x_train=df.drop(['label'], axis = 1)
		y_train=df['label']
	
		self.classifier = SVC(probability=True).fit(x_train, y_train)
		pred_svm = self.classifier.predict_proba(x_train)
		print("Classification accuracy : ",self.classifier.score(x_train,y_train)) 
		pickle.dump(self.classifier, open('classifier', 'wb'))

	def score(self,data_):
		temp=np.array(data_)
		temp=temp.reshape(1, -1)    
		result = self.classifier.predict_proba(temp)
		return result[0][1]
	
class MockGAN(object):
	def __init__(self, name):
		if not os.path.exists('mockgan'):
			open("mockgan", "w").close()

	def initialize(self):
		pass

	def feedData(self, chain):
		pass

	def train(self):
		pass

	def trainClassifier(self):
		pass

	def clf_score(self,data_):
		return str(list(data_)[0]/1000).encode()

	def generator_forward(self,data_):
		import random, string
		
		pub, priv = rsa.newkeys(1024)
		msg = ''.join(random.choices(string.ascii_uppercase + string.digits, k=117))

		return [x for x in rsa.encrypt(msg.encode(), priv)]