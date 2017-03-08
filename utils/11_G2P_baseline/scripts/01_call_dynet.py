import os, random
import numpy as np
from math import sqrt
from collections import defaultdict
from sklearn.metrics import mean_squared_error as mse
folder = '/home/srallaba/voices/cmu_us_ksp/duration_stuff_ksp/duration'
files = sorted(os.listdir(folder))
wids = defaultdict(lambda:  len(wids))

phones = []
durations =[]
for file in files:
   f = open(folder + '/' + file)
   sentence = ' '
   dur = []
   for line in f:
      line = line.strip().split()
      sentence = sentence + ' ' + line[0]
      wids[line[0]]
      dur.append(line[1])
   phones.append(sentence)
   durations.append(dur)

print "Created phone arrays"   
i2w = {i:w for w,i in wids.iteritems()}

import dynet as dy
from seq2seq_v1 import Attention as RED 
model = dy.Model()
M = model.add_lookup_parameters((len(wids), 50))
red =  RED(len(wids), model, M)
trainer = dy.SimpleSGDTrainer(model)


def get_indexed(arr):
  ret_arr = []
  for a in arr:
    #print a, wids[a], M[wids[a]].value()
    
    ret_arr.append(wids[a])
  return ret_arr  

sentences = zip(phones,durations)


words = sents = loss = cumloss = dloss = 0
for epoch in range(100):
 random.shuffle(sentences) 
 c = 1
 for instance in sentences:
  #print "Processing ", sentence
  sentence, durs = instance[0], instance[1]
  sentence = sentence.split() 
  if len(sentence) > 2:  
    #print "This is a valid sentence"
    c = c+1
    if c%1000 == 1:
         #print "I will print trainer status now"
         trainer.status()
         print loss / words
         print "Duration Loss: ", dloss , " for " , words
         loss = 0
         words = 0
         dloss = 0
         for _ in range(1):
	     print ' '.join(k for  k in sentence)
	     isent = get_indexed(sentence)
	     resynth,dur_gen = red.generate(isent)
              
             #samp = red.sample(nchars= len(sentence),stop=wids["</s>"])
             print(" ".join([i2w[c] for c in resynth]).strip())
             durs = durs[0:5]
             
             print "Original: ", ' '.join(str(float(k)).zfill(3) for k in durs)
             print "Synthesized: ", ' '.join(str(float(dur_gen[k].value())).zfill(3) for k in range(0,5))
             synth_durs = [float(k.value()) for k in dur_gen]
             durs = np.asarray(durs, dtype=float)
             synth_durs = np.asarray(durs, dtype=float)
             #print "Mean Squared Error is: ", np.linalg.norm(durs - synth_durs) / np.sqrt(len(durs)) 			   
             ##r =  dur_gen - durs
             ##ms = 0
             try:
              r = dur_gen - durs
              ms = 0
              for k in r:
	        ms += k.value() * k.value()
	      print "Root Mean Squared error: ", sqrt(ms)
	     except ValueError:
	       pass
             
             
    words += len(sentence) - 1
    isent = get_indexed(sentence)
    #print isent
    #print "I will try to calculate error now"
    error, derror = red.get_loss(isent)#,durs)
    #print "Obtained loss ", error.value()
    loss += error.value()
    dloss += derror.value()
    #print "Added error"
    #print error.value()
    error.backward()
    derror.backward()
    trainer.update(1.0)
 print '\n'   
 print("ITER",epoch,loss)
 print '\n'
 trainer.status()
 trainer.update_epoch(1)
    
    
