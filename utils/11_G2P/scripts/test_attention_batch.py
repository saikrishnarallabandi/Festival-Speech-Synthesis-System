from seq2seq_v1 import Attention_Batch as AED_B
import nltk
from seq2seq_v1 import EncoderDecoder as ed
from seq2seq_v1 import nnlm as LM
from seq2seq_v1 import RNNLanguageModel_batch as RNNLM_B 
import dynet as dy
import time
import math
start = time.time()
import random
from dynet import *
from utils import CorpusReader as CR

src_filename = '../data/cmudict-plain_tokenized_input.txt'
tgt_filename = '../data/cmudict-plain_tokenized_output.txt'
#filename = '../../../../dynet-base/dynet/examples/python/written.txt'
#filename = 'txt.done.data'

src_filename_test = '../data/en-de/test.en-de.low.de'
tgt_filename_test = '../data/en-de/test.en-de.low.en'

cr = CR()
src_wids = cr.read_corpus_word(src_filename, 0)
tgt_wids = cr.read_corpus_char(tgt_filename, 0)
src_i2w = {i:w for w,i in src_wids.iteritems()}
tgt_i2w = {i:w for w,i in tgt_wids.iteritems()}

model = Model()     
trainer = SimpleSGDTrainer(model)
num_layers = 1
input_dim = 128
embedding_dim = 128
src_vocab_size = len(src_wids)
tgt_vocab_size = len(tgt_wids)
minibatch_size = 16

src_lookup = model.add_lookup_parameters((len(src_wids), embedding_dim))
tgt_lookup = model.add_lookup_parameters((len(tgt_wids), embedding_dim))
builder = LSTMBuilder
minibatch_size = 32
aed_b =  AED_B(len(src_wids), len(tgt_wids),  model, input_dim, embedding_dim, src_lookup, tgt_lookup, minibatch_size, builder)

def get_indexed(arr, src_flag):
  ret_arr = []
  for a in arr:
    #print a, wids[a], M[wids[a]].value()
    if src_flag == 1:
      ret_arr.append(src_wids[a])
    else:
      ret_arr.append(tgt_wids[a])
  return ret_arr  

def get_indexed_batch(sentence_array):
  ret_ssent_arr = []
  ret_tsent_arr  = []
  words_mb = 0
  for ssent,tsent in sentence_array:
    #print sent
    ar_s = get_indexed(ssent.split(),1)
    ret_ssent_arr.append(ar_s)
    ar = get_indexed(tsent.split(),0)
    ret_tsent_arr.append(ar)
    words_mb += len(ar_s)
  return ret_ssent_arr, ret_tsent_arr, words_mb  



# Accumulate training data
# I am using this simple version as I dont need to do tokenization for this assignment. Infact, tokenization might be bad in this case.
src_sentences  = []
f = open(src_filename)
for  line in f:
   line = line.strip()
   src_sentences.append( line )

tgt_sentences  = []
f = open(tgt_filename)
for  line in f:
   line = line.strip()
   tgt_sentences.append( line )

# Batch the training data ##############################################
# Sort
sentences = zip(src_sentences, tgt_sentences)
sentences.sort(key=lambda x: -len(x))
train_order = [x*minibatch_size for x in range(int((len(sentences)-1)/minibatch_size + 1))]
test_order = train_order[-1]
train_order = train_order[:-1]


print ("startup time: %r" % (time.time() - start))
# Perform training

i = words = sents = loss = cumloss = dloss = 0
for epoch in range(100):
 random.shuffle(train_order) 
 loss = 0
 c = 1
 print train_order
 for sentence_id in train_order:
  #print "Processing ", sentence
  #sentence = train_order[sentence_id]
  #sentence = sentence.split() 
  #if len(sentence) > 2:  
    #print "This is a valid sentence"
  if 3 > 2:  
    #print "This is a valid sentence"
    c = c+1
    print c, " out of ", len(train_order)
    if c%5 == 1:
    #     #print "I will print trainer status now"
         trainer.status()
         print "Loss: ", loss / words
         print "Perplexity: ", math.exp(loss / words)
         print ("time: %r" % (time.time() - start))
         for jj in range(minibatch_size):
	      sentence_id = jj + test_order[0]
              #isents, idurs, words_minibatch_indexing = get_indexed_batch(sentences[sentence_id:sentence_id+minibatch_size])
              src,tgt = sentences[sentence_id]
              resynth = aed_b.generate(src)
              tgt_resynth = " ".join([tgt_i2w[c] for c in resynth]).strip()
              BLEUscore = nltk.translate.bleu_score.sentence_bleu([src], tgt_resynth)
              print "BLEU: ", BLEUscore
         #isent = get_indexed(src_sentence, 1)
         #itype = get_indexed(tgt_sentence,0)
         #resynth= red.generate(isent)

         #resythn = red.sample(nchars= len(sentence),stop=wids["</s>"])
         #print(" ".join([tgt_i2w[c] for c in resynth]).strip())
         #print '\n'
         #durs = durs[0:5]
         #hypothesis = resynth
         #reference = itype
         #BLEUscore = nltk.translate.bleu_score.sentence_bleu([reference], hypothesis)
         #print "BLEU: ", BLEUscore

         #BLEUscore = nltk.translate.bleu_score.sentence_bleu([reference], hypothesis)
         #print "BLEU: ", BLEUscore

    #     #print dloss / words
    #     loss = 0
    #     words = 0
    #     dloss = 0
    #     for _ in range(1):
   # 	     print ' '.join(k for k in sentence)
    #         samp = red.sample(nchars= len(sentence),stop=wids["</s>"])
    #         res = red.generate(get_indexed(sentence))
    #         print(" ".join([i2w[c] for c in res]).strip())
    
    #words += len(sentence) - 1
    isents, idurs, words_minibatch_indexing = get_indexed_batch(sentences[sentence_id:sentence_id+minibatch_size])
    
    #print isent
    #print "I will try to calculate error now"
    error, words_minibatch_loss = aed_b.get_loss_batch(isents,idurs)
    ####### I need to fix this sometime
    #print words_minibatch_indexing , words_minibatch_loss
    #assert words_minibatch_indexing == words_minibatch_loss
    words += words_minibatch_indexing
    #print "Obtained loss ", error.value()
    loss += error.value()
    #print "Added error"
    #print error.value()
    error.backward()
    trainer.update(1.0)
 print '\n'   
 print("ITER",epoch,loss)
 print '\n'
 trainer.status()
 trainer.update_epoch(1)
    
    
