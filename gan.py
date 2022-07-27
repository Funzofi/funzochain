import torch
import torch.nn as nn
import random
import pandas as pd
import string
import rsa
import textwrap
from base64 import b64encode
from sklearn.svm import SVC

class GAN(nn.Module):
  def __init__(self):
    super(GAN, self).__init__()
    inp=0
    out=0
    test_inp=0
    test_out=0
    clf=0
    learning_rate = 0
    model = 0
    criterion = 0
    optimizer = 0
    self.encoder = nn.Sequential(
      nn.Linear(230, 128),
      nn.ReLU(True),
      nn.Linear(128, 64),
      nn.ReLU(True), 
      nn.Linear(64, 32), 
      nn.ReLU(True), 
      nn.Linear(32, 8))
        
    self.decoder = nn.Sequential(
      nn.Linear(8, 32),
      nn.ReLU(True),
      nn.Linear(32, 64),
      nn.ReLU(True),
      nn.Linear(64, 128),
      nn.ReLU(True),
      nn.Linear(128, 230))
    
  def initialize(self):
    self.inp=0
    self.out=0
    self.test_inp=0
    self.test_out=0
    self.clf=0
    self.learning_rate = 1e-3
    self.model = GAN()
    self.criterion = nn.MSELoss()
    self.optimizer = torch.optim.Adam(self.model.parameters(), lr=self.learning_rate, weight_decay=1e-5)

  def feedData(self, chain):
    print(chain)
    input_ = [[0]*230 for element in range(512)]
    output_ = [[0]*230 for element in range(512)]
    for i in range(len(chain)):
      if len(input_) == 512:
        break
      input_[i] = self.encode(chain[i].seed if chain[i].seed else [0]*230)
      output_[i] = self.encode(chain[i+1].seed if chain[i+1].seed else [0]*230)

    self.inp=torch.tensor(input_,dtype=torch.float32)
    self.out=torch.tensor(output_,dtype=torch.float32)
    total_inp=self.inp
    total_out=self.out
    self.inp=total_inp[:384]
    self.out=total_out[:384]
    self.test_inp=total_inp[384:]
    self.test_out=total_inp[384:]

  def encode(self,lst):
    temp=[]
    binaryString=""
    for elem in lst:
      temp.append(format(elem,'08b'))
    for item in temp:
      binaryString+=item
    rev_str= binaryString[::-1]
    chunks=textwrap.wrap(rev_str, 6)
    chunks.reverse()
    for i in range(len(chunks)) :
      chunks[i]=chunks[i][::-1]
    encodedList=[]
    for item in chunks:
      encodedList.append(int(item,2))

    return encodedList

  def forward(self, x):
    x = self.encoder(x)
    x = self.decoder(x)
    return x

  def train(self):
    epochs = 2000
    for epoch in range(epochs):
      output = self.model(self.inp)
      loss = self.criterion(output , self.out)
      self.optimizer.zero_grad()
      loss.backward()
      self.optimizer.step()

  def trainClassifier(self):
    output_ = self.model(self.test_inp)
    output_ =  torch.round(output_)

    output_=output_.detach().numpy()


    for i in output_:
      if i[0]!=1. :
        i[0]=1.

    for i in output_:  
      if i[229]!=61. :
        i[229]=61.

    for i in output_:
      for j in range(len(i)):
        if i[j]<0 or i[j]>61 :
          i[j]=40.

    temp=output_
    df1=pd.DataFrame(temp)
    df1['label']=0

    temp=self.test_out.detach().numpy()
    df2=pd.DataFrame(temp)
    df2['label']=1

    df=df1.append(df2, ignore_index = True)
    df=df.sample(frac=1)

    x_train=df.drop(['label'], axis = 1)
    y_train=df['label']

    self.clf = SVC(probability=True).fit(x_train, y_train)
    pred_svm = self.clf.predict_proba(x_train)

  def clf_score(self,data_):
    pred = self.clf.predict_proba(data_)
    return pred


  def getOutput(self,data_) :
    out_ = self.model(data_)
    out_ =  torch.round(out_)
    out_ = out_.detach().numpy()

    for i in out_:
      if i[0]!=1. :
        i[0]=1.

    for i in out_:  
      if i[229]!=61. :
        i[229]=61.

    for i in out_:
      for j in range(len(i)):
        if i[j]<0 or i[j]>61 :
          i[j]=40.

    return out_