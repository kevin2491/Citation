# -*- coding: utf-8 -*-
"""SciBert_Pytorch_With_data_augmentation final.ipynb

Automatically generated by Colaboratory.


"""

!pip install transformers

#importing libraries 
import os
from argparse import Namespace
from collections import Counter
import json
import pandas as pd
import numpy as np
import torch
from tqdm.notebook import tqdm
import pandas as pd
from gensim.models import KeyedVectors
from nltk.tokenize import RegexpTokenizer
from nltk.stem.porter import PorterStemmer
import random
from transformers import BertTokenizer
from torch.utils.data import TensorDataset
from transformers import AutoTokenizer, AutoModel, BertForSequenceClassification
import re
import string

import nltk
import random
nltk.download('punkt')
from nltk import sent_tokenize
import json

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from tqdm import tqdm_notebook
from google.colab import drive
drive.mount('/content/gdrive',force_remount = True)

#citation

#creating the dataframe
pd.set_option('max_rows', 99999)
pd.set_option('max_colwidth', 400)
pd.describe_option('max_colwidth')

#unzipping the file
!unzip -q "/content/gdrive/MyDrive//Multilabel_BERT_FRL/final_cit_map_function.zip"

#creating the dataframe 
citation = pd.DataFrame(columns=['Text_Tokens','Cit_func','citseg_id'])

import os
paths=[]
d = "/content/per_func_map_organised_small"
for path in os.listdir(d):
    full_path = os.path.join(d, path)
    if os.path.isfile(full_path):
        paths.append(full_path)
#getiing the ctx_text data from the json files 
for i in range(len(paths)):
  path = paths[i]
  print(path)
  f=open(path)
  data=json.load(f)
  for i in data.values():
    citation_contexts=i['citation_contexts']
    for j in range(len(citation_contexts)):
      a=[]
      tokens=citation_contexts[j]['ctx_text']
      #print(tokens)


        
      
      _tokens=[item for item in tokens]
      
#extract the cit_funcs 
      l=len(_tokens)
      tokens = tokens
      for cit_refs in range(len(citation_contexts[j]['cit_refs'])):
         citseg_id=citation_contexts[j]['cit_refs'][cit_refs]['citseg_id']
         if citseg_id not in  a:
            a.append(citseg_id)
            c=citation_contexts[j]['cit_refs'][cit_refs]['citseg_id']
            c = c + l
            f=citation_contexts[j]['cit_refs'][cit_refs]['function_agreed']
            citation = citation.append({'Text_Tokens':tokens, 'Cit_func':f,'citseg_id':c},ignore_index=True)

#dataframe columsn and dtypes
citation.info()

citation['Cit_func'].value_counts() #value of the inqiue values in the cit_func column

#split the subset by rating to create new train, val and test splits
import collections
by_rating = collections.defaultdict(list)
for _,row in citation.iterrows():
  by_rating[row.Cit_func].append(row.to_dict())

#create split data
seed =1021
final_list = []
np.random.seed(seed)
train_proportion = 0.7
val_proportion = 0.2
test_proportion = 0.1

#test_proportion = 0.05

for _, item_list in sorted(by_rating.items()):
  np.random.shuffle(item_list)

  n_total = len(item_list)
  n_train = int(train_proportion * n_total)
  n_val = int(val_proportion * n_total)
  n_test = int(test_proportion * n_total)


  #give data points  split attribute

  for item in item_list[:n_train]:
    item['split'] = 'train'

  #for item in item_list[n_train:n_train+n_val]:
   # item['split'] = 'val'

  for item in item_list[n_train:n_train+n_val]:
    item['split'] = 'val'

  for item in item_list[n_train+n_val:n_train+n_val+n_test]:
    item['split'] = 'test'


  #Add to final list

  final_list.extend(item_list)


final_citation = pd.DataFrame(final_list)

final_citation['split'].value_counts()

final_citation.groupby(['Cit_func','split']).size().unstack(level=1)  
a=final_citation.groupby(['Cit_func','split']).size().unstack(level=1)  
a.plot(kind='bar')
final_citation.groupby(['Cit_func','split']).size()

#final_citation.drop(final_citation.query('Cit_func == "CoCoGM" & split == "train"').sample(n=50).index,inplace=True)

#final_citation.drop(final_citation.query('Cit_func == "Neut" & split == "train"').sample(n=400).index,inplace=True)

#final_citation.drop(final_citation.query('Cit_func == "PMot" & split == "train"').sample(n=50).index,inplace=True)

#final_citation.drop(final_citation.query('Cit_func == "PUse" & split == "train"').sample(n=200).index,inplace=True)

#final_citation.drop(final_citation.query('Cit_func == "Neut" & split == "val"').sample(n=100).index,inplace=True)

final_citation.groupby(['Cit_func','split']).size()

final_citation.groupby(['Cit_func','split']).size().unstack(level=1)  
a=final_citation.groupby(['Cit_func','split']).size().unstack(level=1)  
a.plot(kind='bar')

final_citation.Cit_func.value_counts().plot(kind='barh')

display(final_citation.split.value_counts())

#renaming the labels
final_citation['Cit_func'].replace({'PSim':'Comparison or Contrast','Neut':'Background','CoCoXY':'Background','Weak':'Comparison or Contrast',
                                    'CoCoGM':'Comparison or Contrast','PUse':'Uses','PBas':'Extends','PModi':'Extends','CoCoR0':'Comparison or Contrast',
                                    'PMot':'Motivation','CoCo-':'Comparison or Contrast','PSup':'Comparison or Contrast'
                                    }, inplace=True)

final_citation['Cit_func'].unique()


# final_citation['Cit_func'].replace({"CoCo": "compare_contrast", "CoCo-": "compare_contrast","CoCoGM":"compare_contrast","CoCoR0":"compare_contrast","CoCoXY":"compare_contrast","PBas":"support","PModi":"support","PMot":"support","Psim":"support","PSup":"support","PUse":"support"}, inplace=True)

display(final_citation.split.value_counts())

final_citation.Cit_func.value_counts().plot(kind='barh')

final_citation.groupby(['Cit_func','split']).size().unstack(level=1)  
a=final_citation.groupby(['Cit_func','split']).size().unstack(level=1)  
a.plot(kind='bar')

final_citation.groupby(['Cit_func','split']).size()

#final_citation.head(5)

#citation.groupby(["Cit_func" , "citseg_id"]).size()

#df = citation.groupby("Text_Tokens").citseg_id.apply(list).reset_index()

final_citation['Cit_func'].value_counts()

final_citation.head(5)
#creating a copy of the dataframe 
df = final_citation.copy()

#tokenizing function of the texts , input : text , output : tokenized tokens 
tokenizer = RegexpTokenizer(r'\w+')
p_stemmer = PorterStemmer()

def preprocess_atweet(tweet):
    tokens = [t for t in tokenizer.tokenize(tweet.lower())]
    return tokens

#data augmentation part : 
#1-tokenize function 
#2- creating new sentences by just changing the positions of tokens in sentence, it is the simple way to augment data. shuffeling the tokens 
def tokenize(text):
    '''text: list of text documents'''
    tokenized =  sent_tokenize(text)
    return tokenized
			
def shuffle_tokenized(text):
  shuffled=[]

  random.shuffle(text)
  newl=list(text)
  shuffled.append(newl)
  return text



random.seed(123)
def create_atweet(tweet): 


  augmented = []
  reps=[]
  shuffled = []
  for ng_rev in tweet:

    tok = tokenize(ng_rev)
    shuffled= [tok]
    for i in range(11):
	  #generate 11 new sentences
      shuffle_tokenized(shuffled[-1])
      for k in shuffled:

        s = ' '
        new_rev = s.join(k)
        if new_rev not in augmented:
            augmented.append(new_rev)
            
        else:
            reps.append(new_rev)       

  return ' '.join(augmented)
#this function creates the new sentences from the origianl ones. 
#for each (text,label) you create 11 new sentence; for each sentence there are 11 new sentences by just shuffeling the tokens
# "4" can be changed to increase the new sentences. 
def inflade_tweet_set(df=None):
    tweet_list = []
    for idx in df.index:
        label = df.iloc[idx]['label']
        tweet = preprocess_atweet(df.iloc[idx]['Text_Tokens'])
        row = {'label':label, 'Text_Tokens':' '.join(tweet)}
        tweet_list.append(row)
        for i in range(4):
            new_tweet = create_atweet(tweet)
            new_row = {'label':label, 'Text_Tokens':new_tweet}
            tweet_list.append(new_row)
    return pd.DataFrame(tweet_list)

possible_labels = df.Cit_func.unique()

label_dict = {}
for index, possible_label in enumerate(possible_labels):
    label_dict[possible_label] = index
label_dict

#get the labels encoded

df['label'] = df.Cit_func.replace(label_dict) #change the classes from strings to numbers , encoding them

new_df = inflade_tweet_set(df=df) #the new dataframe

new_df



#ValueError: The least populated class in y has only 1 member, which is too few. The minimum number of groups for any class cannot be less than 2.
#df = df[df.label != 1]

"""from google.colab import files
new_df.to_excel('df_new.xlsx',index = False)
files.download('df_new.xlsx')"""

#download the new dataframe

df= new_df.copy()

"""# TEST1"""

tokenizer = BertTokenizer.from_pretrained('allenai/scibert_scivocab_uncased', 
                                          do_lower_case=True)

#bert tokenizer to tokenize the sentences

from sklearn.model_selection import train_test_split

X_train, X_val, y_train, y_val = train_test_split(df.index.values, 
                                                  df.label.values, 
                                                  test_size=0.15, 
                                                  random_state=42, 
                                                  stratify=df.label.values)

#to create the validation/training sets

df['split'] = ['not_set']*df.shape[0]

df.loc[X_train, 'split'] = 'train'
df.loc[X_val, 'split'] = 'val'

#batch_encode_plus is a function from the tokenizer , the parameters in the function are related to the encoding part of the transformers 
#add spetial tokens , pading them,the attention masks and return the tensors 
encoded_data_train = tokenizer.batch_encode_plus(
    df[df.split=='train'].Text_Tokens.values, 
    add_special_tokens=True, 
    return_attention_mask=True, 
    pad_to_max_length=True, 
    max_length=256, 
    return_tensors='pt'
)

encoded_data_val = tokenizer.batch_encode_plus(
    df[df.split=='val'].Text_Tokens.values, 
    add_special_tokens=True, 
    return_attention_mask=True, 
    pad_to_max_length=True, 
    max_length=256, 
    return_tensors='pt'
)

#these are the data that will be fed to the model in batches after encoding for the trin/val sets
input_ids_train = encoded_data_train['input_ids']
attention_masks_train = encoded_data_train['attention_mask']
labels_train = torch.tensor(df[df.split=='train'].label.values)

input_ids_val = encoded_data_val['input_ids']
attention_masks_val = encoded_data_val['attention_mask']
labels_val = torch.tensor(df[df.split=='val'].label.values)

dataset_train = TensorDataset(input_ids_train, attention_masks_train, labels_train) #create tensors 
dataset_val = TensorDataset(input_ids_val, attention_masks_val, labels_val)

len(dataset_train), len(dataset_val)

model = BertForSequenceClassification.from_pretrained("allenai/scibert_scivocab_uncased",

                                                      num_labels=len(label_dict),
                                                      output_attentions=False,
                                                      output_hidden_states=False)

#loading the model 
#seting the number of labels

from torch.utils.data import DataLoader, RandomSampler, SequentialSampler

#batch size can be changed 
batch_size = 16

dataloader_train = DataLoader(dataset_train, 
                              sampler=RandomSampler(dataset_train), 
                              batch_size=batch_size)

dataloader_validation = DataLoader(dataset_val, 
                                   sampler=SequentialSampler(dataset_val), 
                                   batch_size=batch_size)

from transformers import AdamW, get_linear_schedule_with_warmup
#this is the optimizer , we have used adam. there are other ones . the lr is the learning rate.
optimizer = AdamW(model.parameters(),
                  lr=1e-5, 
                  eps=1e-8)

epochs = 20
scheduler = get_linear_schedule_with_warmup(optimizer, 
                                            num_warmup_steps=0,
                                            num_training_steps=len(dataloader_train)*epochs)

from sklearn.metrics import f1_score

def f1_score_func(preds, labels):
    preds_flat = np.argmax(preds, axis=1).flatten() 
    labels_flat = labels.flatten()
    return f1_score(labels_flat, preds_flat, average='macro') #weighted can be changed  #comparing the true/predicted labels. 

def accuracy_per_class(preds, labels):
    label_dict_inverse = {v: k for k, v in label_dict.items()}
    
    preds_flat = np.argmax(preds, axis=1).flatten() #predicted labels 
    labels_flat = labels.flatten() #true labels 

    for label in np.unique(labels_flat):
        y_preds = preds_flat[labels_flat==label]
        y_true = labels_flat[labels_flat==label]
        print(f'Class: {label_dict_inverse[label]}')
        print(f'Accuracy: {len(y_preds[y_preds==label])}/{len(y_true)}\n') #comparing the true/predicted labels

import random

seed_val = 17
random.seed(seed_val)
np.random.seed(seed_val)
torch.manual_seed(seed_val)
torch.cuda.manual_seed_all(seed_val)

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model.to(device)
#GPU/CPU
print(device)

def evaluate(dataloader_val):

    model.eval()
    
    loss_val_total = 0
    predictions, true_vals = [], []
    
    for batch in dataloader_val:
        
        batch = tuple(b.to(device) for b in batch)
        #input data to the modelbatch of 3 components , from the encoding phase 
        inputs = {'input_ids':      batch[0],
                  'attention_mask': batch[1],
                  'labels':         batch[2],
                 }
#there are zero_grad also can be used here 
        with torch.no_grad():        
            outputs = model(**inputs)
#calculate the loss             
        loss = outputs[0]
        logits = outputs[1]
        loss_val_total += loss.item()

        logits = logits.detach().cpu().numpy()
        label_ids = inputs['labels'].cpu().numpy()
        predictions.append(logits)
        true_vals.append(label_ids)
#averga loss in validation     
    loss_val_avg = loss_val_total/len(dataloader_val) 
    
    predictions = np.concatenate(predictions, axis=0)
    true_vals = np.concatenate(true_vals, axis=0)
            
    return loss_val_avg, predictions, true_vals

for epoch in tqdm(range(1, epochs+1)):
    
    model.train()
    
    loss_train_total = 0

    progress_bar = tqdm(dataloader_train, desc='Epoch {:1d}'.format(epoch), leave=False, disable=False)
    for batch in progress_bar:

        model.zero_grad()
        
        batch = tuple(b.to(device) for b in batch)
        
        inputs = {'input_ids':      batch[0],
                  'attention_mask': batch[1],
                  'labels':         batch[2],
                 }       

        outputs = model(**inputs)
        
        loss = outputs[0]
        loss_train_total += loss.item()
        loss.backward()

        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)

        optimizer.step()
        scheduler.step()
        
        progress_bar.set_postfix({'training_loss': '{:.3f}'.format(loss.item()/len(batch))})
         
        
    torch.save(model.state_dict(), f'/content/sample_data/finetuned_BERT_epoch_{epoch}.model')
        
    tqdm.write(f'\nEpoch {epoch}')
#average training loss    
    loss_train_avg = loss_train_total/len(dataloader_train)            
    tqdm.write(f'Training loss: {loss_train_avg}')
    
    val_loss, predictions, true_vals = evaluate(dataloader_validation)
    val_f1 = f1_score_func(predictions, true_vals)
    tqdm.write(f'Validation loss: {val_loss}')
    tqdm.write(f'F1 Score (Macro): {val_f1}')

torch.cuda.empty_cache()
model = BertForSequenceClassification.from_pretrained("allenai/scibert_scivocab_uncased",
                                                      num_labels=len(label_dict),
                                                      output_attentions=False,
                                                      output_hidden_states=False)

model.to(device)

model.load_state_dict(torch.load('/content/sample_data/finetuned_BERT_epoch_1.model', map_location=torch.device('cpu')))

_, predictions, true_vals = evaluate(dataloader_validation)

accuracy_per_class(predictions, true_vals)

## Write out results
possible_labels = df.label.unique()

label_dict = {}
for index, possible_label in enumerate(possible_labels):
    label_dict[possible_label] = index
#get the labels 
label_dict_inverse = {v: k for k, v in label_dict.items()}

preds_flat = np.argmax(predictions, axis=1).flatten()
labels_flat = true_vals.flatten()
#again comparing the true/predicted labels 

all = np.transpose(np.vstack((labels_flat, preds_flat)))
print(all.shape)
all = pd.DataFrame(all, columns=["l", "p"])
all["label"] = all["l"].map(label_dict_inverse)
all["pred"] = all["p"].map(label_dict_inverse)
all["accuracy"] = 0
mask = all.l == all.p
all.loc[mask, "accuracy"] = 1
all.to_excel("/content/results.xlsx", index=False)



import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix
sns.set(font="IPAexGothic")
#the confusion matrix
cm = confusion_matrix(all["l"], all["p"])  


df_cm = pd.DataFrame(cm, index = [i for i in label_dict_inverse],
                  columns = [i for i in label_dict_inverse])
plt.figure(figsize = (20,15))
ax = sns.heatmap(df_cm, fmt='g', annot=True,cmap="Blues")
ax.set_title('Seaborn Confusion Matrix with labels\n\n');
ax.set_xlabel('\nPredicted Category')
ax.set_ylabel('Actual Category ');

## Ticket labels - List must be in alphabetical order
ax.xaxis.set_ticklabels(["Background","CoCoRXY","Comparison or Contrast","Extends","Future","Motivation","Uses"])
ax.yaxis.set_ticklabels(["Background","CoCoRXY","Comparison or Contrast","Extends","Future","Motivation","Uses"])

## Display the visualization of the Confusion Matrix.
plt.show()
