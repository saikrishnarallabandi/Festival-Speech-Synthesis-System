import os, random
import numpy as np
from math import sqrt
from collections import defaultdict
from sklearn.metrics import mean_squared_error as mse
from seq2seq_v1 import Attention as RED 
from seq2seq_v1 import EncoderDecoder as ed
from seq2seq_v1 import nnlm as LM
from seq2seq_v1 import RNNLanguageModel 
import dynet as dy
import random
import nltk


#folder = '../duration_stuff_ksp/ctype'
#files = sorted(os.listdir(folder))
src_wids = defaultdict(lambda:  len(src_wids))
tgt_wids = defaultdict(lambda:  len(tgt_wids))

'''
phones = []
durations =[]
for file in files:
   f = open(folder + '/' + file)
   sentence = ' '
   dur = []
   for line in f:
      line = line.strip().split()
      sentence = sentence + ' ' + line[0]
      src_wids[line[0]]
      tgt_wids[line[1]]
      dur.append(line[1])
   phones.append(sentence)
   durations.append(dur)

print "Created phone arrays"   
'''

src_filename = 'txt.done.data'
tgt_filename = 'txt.done.data'

lm = LM()
train_dict,src_wids = lm.read_corpus(src_filename)
train_dict,tgt_wids = lm.read_corpus(tgt_filename)

src_i2w = {i:w for w,i in src_wids.iteritems()}
tgt_i2w = {i:w for w,i in tgt_wids.iteritems()}

print "Prepared index to words"

f = open('src_wids','w')
for w in src_wids:
   f.write(w + ' ' + str(src_wids[w]) + '\n')
f.close()   

mini_batch_size = 32

f = open('tgt_wids','w')
for w in tgt_wids:
   f.write(w + ' ' + str(tgt_wids[w]) + '\n')
f.close()

import dynet as dy
from seq2seq_v1 import Attention as RED 
model = dy.Model()
src_M = model.add_lookup_parameters((len(src_wids), 128))
tgt_M = model.add_lookup_parameters((len(tgt_wids), 128))
red =  RED(len(src_wids), len(tgt_wids), model, src_M, tgt_M)
trainer = dy.SimpleSGDTrainer(model)


src_sentences  = []
f = open(src_filename)
for  line in f:
   line = line.strip()
   src_sentences.append(line)


tgt_sentences  = []
f = open(tgt_filename)
for  line in f:
   line = line.strip()
   tgt_sentences.append(line)

print "Prepared input and output" 

def get_indexed(arr, src_flag):
  if src_flag == 1:
     wids = src_wids
  else:
     wids = tgt_wids

  ret_arr = []
  for a in arr:
    #print a, wids[a], M[wids[a]].value()
    
    ret_arr.append(wids[a])
  return ret_arr  

sentences = zip(src_sentences,tgt_sentences)


words = sents = loss = cumloss = dloss = 0
for epoch in range(100):
 random.shuffle(sentences) 
 b = 0
 c = 1
 for instance in sentences:
  #print "Processing ", instance
  src_sentence, tgt_sentence = instance[0], instance[1]
  print len(src_sentence), len(tgt_sentence)
  src_sentence = src_sentence.split() 
  tgt_sentence = tgt_sentence.split()

  if len(src_sentence) > 2:  
    #print "This is a valid sentence"
    c = c+1
    b = b + 1
    if c%200 == 1:
         #print "I will print trainer status now"
         trainer.status()
         print loss / words
         #print "Duration Loss: ", dloss , " for " , words
         loss = 0
         words = 0
         dloss = 0
         for _ in range(1):
	     print ' '.join(k for  k in src_sentence)
	     isent = get_indexed(src_sentence, 1)
             itype = get_indexed(tgt_sentence,0)
	     resynth= red.generate(isent)
              
             #resythn = red.sample(nchars= len(sentence),stop=wids["</s>"])
             print(" ".join([tgt_i2w[c] for c in resynth]).strip())
             print '\n'
             #durs = durs[0:5]
             hypothesis = resynth
             reference = itype
             BLEUscore = nltk.translate.bleu_score.sentence_bleu([reference], hypothesis)
             print "BLEU: ", BLEUscore
             #print "Original: ", ' '.join(str(float(k)).zfill(3) for k in durs)
             #print "Synthesized: ", ' '.join(str(float(dur_gen[k].value())).zfill(3) for k in range(0,5))
             #synth_durs = [float(k.value()) for k in dur_gen]
             #durs = np.asarray(durs, dtype=float)
             #synth_durs = np.asarray(durs, dtype=float)
             #print "Mean Squared Error is: ", np.linalg.norm(durs - synth_durs) / np.sqrt(len(durs)) 			   
             ##r =  dur_gen - durs
             ##ms = 0
             #try:
             # r = dur_gen - durs
             # ms = 0
             # for k in r:
	     #   ms += k.value() * k.value()
	     # print "Root Mean Squared error: ", sqrt(ms)
	     #except ValueError:
	     #  pass
             
             
    words += len(src_sentence) - 1
    isent = get_indexed(src_sentence,1)
    idur = get_indexed(tgt_sentence,0)
    #print isent
    #print "I will try to calculate error now"
    #print "Processing ", isent
    #print "Processing ", idur
    error = red.get_loss(isent,idur)
    #print "Obtained loss "
    #print error
    loss += error.value()
    #dloss += derror.value()
    #print "Added error"
    #print error.value()
    error.backward()
    #derror.backward()
    if mini_batch_size == b:
       trainer.update(1.0)
       b = 0
 print '\n'   
 print("ITER",epoch,loss)
 print '\n'
 trainer.status()
 trainer.update_epoch(1)
    
    
