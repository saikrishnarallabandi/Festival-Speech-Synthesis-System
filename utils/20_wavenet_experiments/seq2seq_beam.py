#from seq2seq import ngramlm, neurallm

import cPickle, pickle
import numpy as np
import dynet
import os
from copy import copy
from collections import defaultdict
import dynet as dy
from dynet import *
import numpy
import random
#from nltk.tokenize import RegexpTokenizer 
from collections import Counter, defaultdict
import time
import math

class Encoder_Decoder_regress:
  
     def __init__(self, src_train_file, src_test_file, target_path):
       self.model = dynet.Model()
       self.src_train_file = src_train_file
       self.src_test_file = src_test_file
       
     def read_file(self, fname, dd ):
       # src_train=list(read(src_train_file, src_wid)) Used also for src_test, tgt_train, tgt_test
       print "Reading ", fname
       with open(fname, "r") as fh:
             for line in fh:
                 #line = "<s>" + ' ' + line
                 sent = [dd[x] for x in line.strip().split()]
                 sent = sent[1:]
                 sent.append(dd["</s>"])
                 #sent = [str(dd["<s>"])] +  sent
                 yield sent
                 
     def initiate_params(self):
       self.start = time.time()
       self.src_w2i = defaultdict(lambda: len(self.src_w2i))
       self.tgt_w2i = defaultdict(lambda: len(self.tgt_w2i))
       
       self.src_w2i["<unk>"] = 0
       self.src_w2i["<s>"] = 1
       self.src_w2i["</s>"] = 2
       self.src_w2i["<S>"] = 3
        
       self.src_train=list(self.read_file(self.src_train_file, self.src_w2i))
       self.src_test=list(self.read_file(self.src_test_file, self.src_w2i))        
       path = 'dur'
       files = sorted(os.listdir(path))
       self.tgt_train = [np.loadtxt(path + '/' + k, usecols=(1,)) for k in files]
       self.tgt_test = self.tgt_train
       
       self.src_i2w = {i:w for w,i in self.src_w2i.iteritems()}
       self.save_i2ws(self.src_i2w, 0)
        
       self.layers = 1
       self.embed_size = 32
       self.state_size = 512
       self.src_vocab_size = len(self.src_w2i)
       self.tgt_vocab_size = len(self.tgt_w2i)
       self.attention_size = 16
       self.minibatch_size = 16
       self.input_lookup = self.model.add_lookup_parameters((len(self.src_w2i), self.embed_size))
       self.output_lookup = self.model.add_lookup_parameters((len(self.tgt_w2i), self.embed_size))
       self.enc_fwd_lstm = dynet.LSTMBuilder(self.layers, self.embed_size, self.state_size, self.model)
       self.enc_bwd_lstm = dynet.LSTMBuilder(self.layers, self.embed_size, self.state_size, self.model)
       self.dec_lstm = dynet.LSTMBuilder(self.layers, self.state_size*2 + self.embed_size,  self.state_size, self.model)
       self.attention_w1 = self.model.add_parameters( (self.attention_size, self.state_size*2))
       self.attention_w2 = self.model.add_parameters( (self.attention_size , self.state_size * self.layers* 2))
       self.attention_v = self.model.add_parameters( (1, self.attention_size))
       self.decoder_w = self.model.add_parameters(( 1, self.state_size ))
       self.decoder_b = self.model.add_parameters( ( 1 ))
       self.vocab_R = self.model.add_parameters((self.tgt_vocab_size, self.state_size*2))
       self.encoder_w = self.model.add_parameters( (self.src_vocab_size , self.state_size ))
       self.encoder_b = self.model.add_parameters( ( self.src_vocab_size ))
       self.sgd_trainer = dynet.SimpleSGDTrainer(self.model) 
       self.adam_trainer = dynet.AdamTrainer(self.model)

     def save_model(self, l):
          params = [self.input_lookup, self.output_lookup, self.enc_fwd_lstm, self.enc_bwd_lstm, self.dec_lstm, self.attention_w1, self.attention_w2, self.attention_v, self.decoder_w, self.decoder_b, self.encoder_w, self.encoder_b]
          self.model.save("model_beam_" + str(l).zfill(2), params)
 
     def load_model(self, l):
         [self.input_lookup, self.output_lookup, self.enc_fwd_lstm, self.enc_bwd_lstm, self.dec_lstm, self.attention_w1, self.attention_w2, self.attention_v, self.decoder_w, self.decoder_b, self.encoder_w, self.encoder_b] = self.model.load("model_beam_" + str(l).zfill(2))

     def test_generate_model(self,  count):
       dynet.renew_cg()
       self.sentences_test = zip(self.src_test, self.tgt_test)
       f = open('test_output_' + str(self.param) + '_' + str(count).zfill(5),'w')
       for (src, tgt) in self.sentences_test:
            dynet.renew_cg()
            resynth = self.generate(src)
            tgt_resynth = " ".join([self.tgt_i2w[cc] for cc in resynth]).strip()
            f.write(tgt_resynth + '\n')
       f.close()
   

     def softmax(self, x):
        e_x = np.exp(x - np.max(x))
        out = e_x / e_x.sum()
        return out
 
     def save_i2ws(self, dct, src_flag):
          if src_flag == 0:
               dd = 'src'
          else:
               dd = 'tgt'
          print "Saving ", dd
          f = open('wids_' + dd + '.txt','w')
          for w in dct:
	    f.write(str(w) + ' ' + str(dct[w]) + '\n')
          f.close()     

     def train_model(self):
       self.sentences = zip(self.src_train, self.tgt_train)
       self.sentences.sort(key=lambda x: -len(x))
       
       for epoch in range(20):
	    random.shuffle(self.sentences)
	    self.loss, self.words = self.update_minibatch()
	    print "Epoch done ", epoch, self.loss
	    print "Loss per phone: ", self.loss/self.words
	    print "Time: ", time.time() - self.start
	    print '\n'
            #if epoch > 15:
            #  self.save_model(epoch)

     def test_model(self):
       self.sentences_test = zip(self.src_test, self.tgt_test)
       param = 19
       self.load_model(param)
       for (src, tgt) in self.sentences_test:
            print "Source: ", src 
            resynth = self.generate_attention(src)
            tgt_resynth = " ".join([self.tgt_i2w[cc] for cc in resynth]).strip()
            print tgt_resynth
            print '\n'
 
     def update_minibatch(self):
          #self.trainer =  self.sgd_trainer
          L = 0
          W = 0          
          count = 0
          for sentence in self.sentences:
              count += 1
	      if count > 100 and count % 150 == 1:
	           print "Processing sentence ",count , " of ", len(self.sentences) 
	           print time.time() - self.start
                   self.test_generate_model(count)

	      error, words_num = self.get_loss(sentence)
              L += error.value()
	      W += words_num
	      error.backward()
	      self.trainer.update(1)
	  self.trainer.status()
	  self.trainer.update_epoch(1)
	  return L,W
        
     def save_model(self,par):
        self.model.save('seq2seqtranslator_' + str(par) + '.model')
        print "Saved ", 'seq2seqtranslator_' + str(par) + '.pkl'

     def load_model(self,par):
        model = self.model.load('seq2seqtranslator_' + str(par) + '.model')
        print "Loaded ", 'seq2seqtranslator_' + str(par) + '.pkl'

     def attend(self, input_mat, state, w1dt):
        w2 = dynet.parameter(self.attention_w2)
        v = dynet.parameter(self.attention_v)
        w2dt = w2*dynet.concatenate(list(state.s()))
        unnormalized = dynet.transpose(v * dynet.tanh(dynet.colwise_add(w1dt, w2dt)))
        att_weights = dynet.softmax(unnormalized)
        context = input_mat * att_weights
        return context
      
     def decode(self, vectors_array, output_array, input_array, end_token):
         # Preprocess the batch
         #print output_array
         out_vectors_array = []
         isents = output_array #[1:] # transposes    
         inps = input_array[1:]
         # Declare all your stuff  
         input_mat_array = dynet.concatenate_cols(vectors_array)  
         w = dynet.parameter(self.decoder_w)
         b = dynet.parameter(self.decoder_b)
         w1 = dynet.parameter(self.attention_w1)
         w2 = dynet.parameter(self.attention_w2)
         v = dynet.parameter(self.attention_v)
         w1dt = None
         w1dt = w1dt or w1 * input_mat_array
         last_output_embeddings = lookup(self.output_lookup, 1)
         s = self.dec_lstm.initial_state() #.add_input(dynet.concatenate([dynet.vecInput(self.state_size *2), last_output_embeddings])) # This can be argued to be some form of cheating I think
         first_flag = 0
         errs = []

         # Okay Go on
         words = 0
         for (curr_vec, inp) in zip(isents, inps):
	     #print "Mapping: ",  curr_vec 	, inp
             '''            
             if first_flag == 0:
                 first_flag = 1
                 last_output_embeddings = lookup(self.output_lookup, 1)
                 a = dynet.vecInput(1024)
                 bb = last_output_embeddings
             else:
                 bb = last_output_embeddings
                 #a = self.attend(input_mat_array,s, w1dt)
                 a = dynet.vecInput(1024)
             '''
             if  first_flag == 0:
	         first_flag = 1
                 a = dynet.vecInput(1024)
                 bb = last_output_embeddings             
                 x_t = dynet.concatenate([a,bb])
             s = s.add_input(x_t)
             #print "Added input"
             y = s.output()
             #print y.value()
             output_vector = w * y + b
             #err = dynet.pickneglogsoftmax(dynet.softmax(output_vector), curr_vec)
             #rr = dynet.pickneglogsoftmax(output_vector, curr_vec)
             err = dynet.squared_norm(output_vector - curr_vec)
             last_output_embeddings = output_vector
             words += 1
             errs.append(err)
         print errs
         err_v = dynet.esum(errs)
         print "Returning", err_v
         return err_v, words

  
     def generate(self, sentence):
        #embedded = embed_sentence(in_seq)
        encoded = self.encode_sentence_test(sentence)
        sentence = sentence[1:]
        w = dy.parameter(self.decoder_w)
        b = dy.parameter(self.decoder_b)
        w1 = dy.parameter(self.attention_w1)
        input_mat = dy.concatenate_cols(encoded)
        w1dt = None

        last_output_embeddings = self.output_lookup[1]
        s = self.dec_lstm.initial_state().add_input(dy.concatenate([dy.vecInput(self.state_size * 2), last_output_embeddings]))

        out = ''
        res = []
        count_EOS = 0
        for i in range(len(sentence)):
              inp = sentence[i]
              if count_EOS == 2: break
              # w1dt can be computed and cached once for the entire decoding phase
              w1dt = w1dt or w1 * input_mat
              vector = dy.concatenate([self.attend(input_mat, s, w1dt), last_output_embeddings])
              s = s.add_input(vector)
              #k = s
              #dloss = self.test_duration(k, i, b)
              out_vector = w * s.output() + b
              probs = dy.softmax(out_vector).vec_value()
              next_word = probs.index(max(probs))
              last_output_embeddings = self.output_lookup[next_word]
              if next_word == 2:
                  count_EOS += 1
                  continue
	      res.append(next_word)	

              #out += int2char[next_word]
        return res


     def generate_beam(self, sentence):
        #print "Trying to generate"
        encoded = self.encode_sentence_test(sentence)
        w = dynet.parameter(self.decoder_w)
        b = dynet.parameter(self.decoder_b)
        w1 = dynet.parameter(self.attention_w1)
        input_mat = dynet.concatenate_cols(encoded)
        w1dt = None
        last_output_embeddings = lookup(self.output_lookup, 1)
        s = self.dec_lstm.initial_state() #.add_input(dynet.concatenate([dynet.vecInput(self.state_size * 2), last_output_embeddings]))
        out = ''
        res = []
        count_EOS = 0
        for i in range(len(sentence)):
              if count_EOS == 2: 
		#print "I thnk I got 2 EOS symbols. Sorry. Breaking"
		return res
              w1dt = w1dt or w1 * input_mat
              vector = dynet.concatenate([self.attend(input_mat, s, w1dt), last_output_embeddings])
              s = s.add_input(vector)
              out_vector = w * s.output() + b
              probs = dynet.softmax(out_vector).vec_value()
              next_word = probs.index(max(probs))
              last_output_embeddings = self.output_lookup[next_word]
              if next_word == 2:
                  count_EOS += 1
              #print "Next Word: ", next_word
	      res.append(next_word)	

        return res

     def get_loss(self, sentence_tuple): #a = [([1],[2]), ([3],[4]), ([5],[6])]
        dynet.renew_cg()
        src_sentence, tgt_sentence = sentence_tuple
        encoded_array = self.encode_sentence_test(src_sentence)
        end_token = 2
        print "Calling decoder"
        return self.decode(encoded_array, tgt_sentence, src_sentence, end_token)

     def encode_sentence(self, sentence):
        sentence_rev = list(reversed(sentence))
        fwd_vectors = self.run_lstm(self.enc_fwd_lstm.initial_state(), sentence)
        bwd_vectors = self.run_lstm(self.enc_bwd_lstm.initial_state(), sentence_rev)
        bwd_vectors = list(reversed(bwd_vectors))
        vectors = [dynet.concatenate(list(p)) for p in zip(fwd_vectors, bwd_vectors)]
        return vectors

     def encode_sentence_test(self, sentence):
         embeddings = [dynet.lookup(self.input_lookup, drow) for drow in sentence]
         fwd_init_state = self.enc_fwd_lstm.initial_state()  
         fwd_states = fwd_init_state.transduce(embeddings)
         bwd_init_state = self.enc_bwd_lstm.initial_state()

         bwd_states = reversed(bwd_init_state.transduce(reversed(embeddings)))

         #print "Individual Encodings done"
         # Concat for Decoder and get encoding
         states = [dynet.concatenate([fwd, bwd]) for (fwd, bwd) in zip(fwd_states, bwd_states)]
         return states

     def test_only(self):
         self.load_model(19)
         self.test_generate_model(19)


     def generate_attention(self, sentence):
        #print "Trying to generate using beam search"
        #embedded = embed_sentence(in_seq)
        encoded = self.encode_sentence_test(sentence)
        
        #print "Encoded"
        w = dynet.parameter(self.decoder_w)
        b = dynet.parameter(self.decoder_b)
        w1 = dynet.parameter(self.attention_w1)
        input_mat = dynet.concatenate_cols(encoded)
        w1dt = None
        w1dt = w1dt or w1 * input_mat
        last_output_embeddings = self.output_lookup[2]
        s = self.dec_lstm.initial_state() #.add_input(dynet.concatenate([dynet.vecInput(self.state_size * 2), last_output_embeddings]))
        input_mat_array = dynet.concatenate_cols(encoded)
        out = ''
        res = []
        count_EOS = 0
        first_flag = 0
        #vocab_R = dynet.parameter(self.vocab_R)
        #vocab_lookup = dynet.transpose(vocab_R)


        for i in range(len(sentence)):
	      if count_EOS == 2:
		  return res
              if first_flag == 0:
                 first_flag = 1
                 a = dynet.vecInput(1024)
                 bb = last_output_embeddings
              else:
                 #bb = dynet.select_cols(vocab_lookup, last_output_embeddings)
                 #bb = dynet.reshape(bb, (1024 ,), 1)
                 bb = last_output_embeddings
                 a = self.attend(input_mat_array,s, w1dt)
                 
	      x_t = dynet.concatenate([a,bb]) 
              s = s.add_input(x_t)
              y = s.output()
              output_vector = w * y + b
              probs = dynet.softmax(output_vector).vec_value()
              next_word = probs.index(max(probs))
              last_output_embeddings = lookup(self.output_lookup, next_word)
              if next_word == 2:
                  count_EOS += 1
                  #print "I thnk I got 2 EOS symbols. Sorry"
                  continue
              print "Next Word: ", next_word
	      res.append(next_word)	

              #out += int2char[next_word]
        #print "Returning"
        return res

     def generate_attention_beam(self, sentence):
        print "Trying to generate using beam search !"
        #embedded = embed_sentence(in_seq)
        encoded = self.encode_sentence_test(sentence)
        #sentence = sentence[1:]
        #print "Encoded"
        w = dynet.parameter(self.decoder_w)
        b = dynet.parameter(self.decoder_b)
        w1 = dynet.parameter(self.attention_w1)
        input_mat = dynet.concatenate_cols(encoded)
        w1dt = None
        w1dt = w1dt or w1 * input_mat
        last_output_embeddings = [self.output_lookup[1]]
        s = self.dec_lstm.initial_state() #.add_input(dynet.concatenate([dynet.vecInput(self.state_size * 2), last_output_embeddings]))
        input_mat_array = dynet.concatenate_cols(encoded)
        out = ''
        res = []
        count_EOS = 0
        first_flag = 0
        #vocab_R = dynet.parameter(self.vocab_R)
        #vocab_lookup = dynet.transpose(vocab_R)
        score = 0.0
        tokens = [1]
        embeddings = [last_output_embeddings]
        max_tokens = 100
        completed_beams = []
        beam_count = 2
        active_beams = [(score, tokens, last_output_embeddings, s)]
        while len(completed_beams) < beam_count:
         potential_beams = []
         for score, tokens, embeddings, s in active_beams:
           #print tokens
           #print "Embeddings: ", embeddings
           cw = tokens[-1]
           embedding = embeddings[-1]
           #print "Embedding: ", embedding.value()          
           ##if count_EOS == 2:
           ##    return res
           if first_flag == 0:
                 first_flag = 1
                 a = dynet.vecInput(1024)
                 bb = embedding
                
           else:
                 #print "Calling Attention"
                 bb = embedding
                 a = self.attend(input_mat_array,s, w1dt)
           x_t = dynet.concatenate([a,bb])
           s_new = s 
           s_new = s_new.add_input(x_t)
           y = s_new.output()
           output_vector = w * y + b
           score_dist = -numpy.log(self.softmax(output_vector.vec_value()))
           for nw, move_score in zip(range(self.tgt_vocab_size), score_dist):
                    new_score = score + move_score
                    new_toks = copy(tokens)
                    new_toks.append(nw)
                    new_embeddings = copy(embeddings)
                    embedding = lookup(self.output_lookup, nw)
                    new_embeddings.append(embedding)
                    potential_beams.append((new_score, new_toks, new_embeddings, s_new))
           potential_beams.sort()
           active_beams = potential_beams[:beam_count - len(completed_beams)]
           #print active_beams
           abi = 0
           while abi < len(active_beams):
                if active_beams[abi][1][-1] == 2:
                   count_EOS  += 1
                if count_EOS > 2 or len(active_beams[abi][1]) > max_tokens:
                   completed_beams.append(active_beams.pop(abi))
                   continue
                else: abi += 1
        
        score, toks, _ , _= min(completed_beams)
        #return {"toks":toks, "loss": score, "prediction_count":len(toks)-1}
        print score
        return toks
      
