#from seq2seq import ngramlm, neurallm
import cPickle, pickle
import numpy as np
import os
from collections import defaultdict
import dynet as dy
from dynet import *
import numpy
import random
from nltk.tokenize import RegexpTokenizer 




class Attention:
  
     def __init__(self, src_vocab_size, tgt_vocab_size, model, lookup, tgt_lookup ):
       self.model = model
       #self.trainer = dy.SimpleSGDTrainer(self.model)
       self.layers = 1
       self.embed_size = 128
       self.hidden_size = 128
       self.state_size = 128
       self.src_vocab_size = src_vocab_size
       self.tgt_vocab_size = tgt_vocab_size
       self.attention_size = 32
       
       self.enc_fwd_lstm = dy.LSTMBuilder(self.layers, self.embed_size, self.state_size, model)
       self.enc_bwd_lstm = dy.LSTMBuilder(self.layers, self.embed_size,self.state_size, model)
       self.dec_lstm = dy.LSTMBuilder(self.layers, self.state_size*2 + self.embed_size,  self.state_size, model)
       
       self.input_lookup = lookup
       self.output_lookup = tgt_lookup
       self.attention_w1 = model.add_parameters( (self.attention_size, self.state_size*2))
       self.attention_w2 = model.add_parameters( (self.attention_size , self.state_size * self.layers* 2))
       self.attention_v = model.add_parameters( (1, self.attention_size))
       self.decoder_w = model.add_parameters( (self.src_vocab_size , self.state_size ))
       self.decoder_b = model.add_parameters( ( self.src_vocab_size ))
       self.output_lookup = lookup
       self.duration_weight = model.add_parameters(( 1, self.state_size ))
       self.duration_bias = model.add_parameters( ( 1 ))
     
     def run_lstm(self, init_state, input_vecs):
            s = init_state
            out_vectors = []
            for vector in input_vecs:
	       x_t = lookup(self.input_lookup, int(vector))
               s = s.add_input(x_t)
               out_vector = s.output()
               out_vectors.append(out_vector)
            return out_vectors 

     def embed_sentence(self, sentence):
          sentence = [EOS] + list(sentence) + [EOS]
          sentence = [char2int[c] for c in sentence]
          global input_lookup
          return [input_lookup[char] for char in sentence]
	
	
     def attend(self, input_mat, state, w1dt):
        #global self.attention_w2
        #global self.attention_v
        w2 = dy.parameter(self.attention_w2)
        v = dy.parameter(self.attention_v)
        w2dt = w2*dy.concatenate(list(state.s()))
        unnormalized = dy.transpose(v * dy.tanh(dy.colwise_add(w1dt, w2dt)))
        att_weights = dy.softmax(unnormalized)
        context = input_mat * att_weights
        return context
     
     def test_duration(self, state, idx):
        dw = dy.parameter(self.duration_weight)
        db = dy.parameter(self.duration_bias)
        probs = dy.softmax(dw * state.output() + db)
        print idx
        return -dy.log(dy.pick(probs, self.output_lookup[int(idx)]))

     def decode(self,  vectors, output, end_token):
        #output = [EOS] + list(output) + [EOS]
        #output = [char2int[c] for c in output]

        w = dy.parameter(self.decoder_w)
        b = dy.parameter(self.decoder_b)
        w1 = dy.parameter(self.attention_w1)
        input_mat = dy.concatenate_cols(vectors)
        w1dt = None

        last_output_embeddings = self.output_lookup[2]
        s = self.dec_lstm.initial_state().add_input(dy.concatenate([dy.vecInput(self.state_size *2), last_output_embeddings]))
        loss = []
        dur_loss = []
        c = 1
        for word in output:
	   c += 1
           print word
           # w1dt can be computed and cached once for the entire decoding phase
           w1dt = w1dt or w1 * input_mat
           vector = dy.concatenate([self.attend(input_mat, s, w1dt), last_output_embeddings])
           s = s.add_input(vector)
           #k = s
           #print "Going"
           #dloss = self.test_duration(k, dur)
           #print "Back"
           #dur_loss.append(dloss)
           out_vector = w * s.output() + b
           print out_vector
           probs = dy.softmax(out_vector)
           last_output_embeddings = self.output_lookup[word]
           print "Got embeddings"
           print " Picking", dy.pick(probs, word).value()
           loss.append(-dy.log(dy.pick(probs, word)))
           print -dy.log(dy.pick(probs, word)).value()
        loss = dy.esum(loss)
        print  "Gave loss"
        return loss
      
     def generate(self, sentence):
        #embedded = embed_sentence(in_seq)
        encoded = self.encode_sentence(sentence)

        w = dy.parameter(self.decoder_w)
        b = dy.parameter(self.decoder_b)
        w1 = dy.parameter(self.attention_w1)
        dw = dy.parameter(self.duration_weight)
        db = dy.parameter(self.duration_bias)
        #duration = dw * state.output() + db
        input_mat = dy.concatenate_cols(encoded)
        w1dt = None

        last_output_embeddings = self.output_lookup[2]
        s = self.dec_lstm.initial_state().add_input(dy.concatenate([dy.vecInput(self.state_size * 2), last_output_embeddings]))

        out = ''
        res = []
        
        count_EOS = 0
        for i in range(len(sentence)*2):
              if count_EOS == 2: break
              # w1dt can be computed and cached once for the entire decoding phase
              w1dt = w1dt or w1 * input_mat
              vector = dy.concatenate([self.attend(input_mat, s, w1dt), last_output_embeddings])
              s = s.add_input(vector)
              #k = s
              #dloss = self.test_duration(k, i, b)
              out_vector = w * s.output() + b
              dur_pred = dw * s.output() + db
              probs = dy.softmax(out_vector).vec_value()
              next_word = probs.index(max(probs))
              last_output_embeddings = self.output_lookup[next_word]
              if next_word == 2:
                  count_EOS += 1
                  continue
	      res.append(next_word)
	      dur_g.append(dy.rectify(dur_pred))

              #out += int2char[next_word]
        return res

     def get_loss(self, sentence,target):
        dy.renew_cg()
        #embedded = self.embed_sentence(sentence)
        encoded = self.encode_sentence(sentence)
        end_token = '</s>'
        print "Returning"
        return self.decode(encoded, target, end_token)
      
	
     def encode_sentence(self, sentence):
        sentence_rev = list(reversed(sentence))
        fwd_vectors = self.run_lstm(self.enc_fwd_lstm.initial_state(), sentence)
        bwd_vectors = self.run_lstm(self.enc_bwd_lstm.initial_state(), sentence_rev)
        bwd_vectors = list(reversed(bwd_vectors))
        vectors = [dy.concatenate(list(p)) for p in zip(fwd_vectors, bwd_vectors)]
        return vectors




class EncoderDecoder:
   
     def __init__(self, vocab_size):
       self.model = Model()
       self.trainer = SimpleSGDTrainer(self.model)
       self.layers = 2
       self.embed_size = 128
       self.hidden_size = 128
       self.src_vocab_size = vocab_size
       self.tgt_vocab_size = vocab_size
       
       self.enc_builder = LSTMBuilder(self.layers, self.embed_size, self.hidden_size, self.model) 
       self.dec_builder = LSTMBuilder(self.layers, self.embed_size, self.hidden_size, self.model) 
       self.src_lookup = self.model.add_lookup_parameters((self.src_vocab_size, self.embed_size))
       self.tgt_lookup = self.model.add_lookup_parameters((self.tgt_vocab_size, self.embed_size))
       self.W_y = self.model.add_parameters((self.tgt_vocab_size, self.hidden_size))
       self.b_y = self.model.add_parameters((self.tgt_vocab_size))
       
     def encode(self, instance, wids):
        dy.renew_cg()
        W_y = dy.parameter(self.W_y)
        b_y = dy.parameter(self.b_y)
#        print "chceking wids here",wids["about"]
        src_sent = instance.split()
        #print "printing src sentnce length", len(src_sent)
        losses = []
        total_words = 0
      
        # Encoder
        enc_state = self.enc_builder.initial_state()
        #for current_word in src_sent:
	for (cw, nw) in zip(src_sent, src_sent[1:]):  
            state = enc_state.add_input(self.src_lookup[wids[cw]])
	    encoded = (W_y * state.output()) + b_y
	    err = pickneglogsoftmax(encoded, int(wids[nw]))
	    losses.append(err)
	return dy.esum(losses)    


	dec_state = self.dec_builder.initial_state()
	dec_state = self.dec_builder.initial_state(encoded)
	errs = []
	# Calculate losses for decoding
	for (cw, nw) in zip(src_sent, src_sent[1:]):
	  dec_state = dec_state.add_input(self.tgt_lookup[wids[current_word]])
	  decoded = dec_state.output()
	  ystar = (W_y * dec_state.output()) + b_y
          #print "current word is >>>>>>>", cw
          #print "next word shud be", nw
          loss = dy.pickneglogsoftmax(ystar, wids[nw])
          losses.append(loss)
          '''
          total_words += 1
          dist_array = []
          for i in range(0,len(ystar.value())):
               dist = numpy.linalg.norm(self.tgt_lookup[wids[nw]].value() - ystar.value()[i])
               dist_array.append(dist)
          #print " predicted next_word ========>",  src_sent[dist_array.index(min(dist_array))]
          '''
        return dy.esum(losses) #, total_words, src_sent[dist_array.index(min(dist_array))]


class EncoderDecoder_debug:
   
     def __init__(self, vocab_size):
       self.model = dy.Model()
       self.trainer = dy.SimpleSGDTrainer(self.model)
       self.layers = 2
       self.embed_size = 1
       self.hidden_size = 1
       self.src_vocab_size = vocab_size
       self.tgt_vocab_size = vocab_size
       
       self.enc_builder = dy.LSTMBuilder(self.layers, self.embed_size, self.hidden_size, self.model) 
       self.dec_builder = dy.LSTMBuilder(self.layers, self.embed_size, self.hidden_size, self.model) 
       self.src_lookup = self.model.add_lookup_parameters((self.src_vocab_size, self.embed_size))
       self.tgt_lookup = self.model.add_lookup_parameters((self.tgt_vocab_size, self.embed_size))
       self.W_y = self.model.add_parameters((self.tgt_vocab_size, self.hidden_size))
       self.b_y = self.model.add_parameters((self.tgt_vocab_size))
       
     def encode(self, instance, wids):
        dy.renew_cg()
        W_y = dy.parameter(self.W_y)
        b_y = dy.parameter(self.b_y)
#        print "chceking wids here",wids["about"]
        src_sent = instance.split()
        #print "printing src sentnce length", len(src_sent)
        losses = []
        total_words = 0
      
        # Encoder
        enc_state = self.enc_builder.initial_state()
        for current_word in src_sent:
            state = enc_state.add_input(self.src_lookup[wids[current_word]])
	    encoded = (W_y * state.output()) + b_y


	dec_state = self.dec_builder.initial_state()
	dec_state = self.dec_builder.initial_state(encoded)
	errs = []
	# Calculate losses for decoding
	for (cw, nw) in zip(src_sent, src_sent[1:]):
	  dec_state = dec_state.add_input(self.tgt_lookup[wids[current_word]])
	  decoded = dec_state.output()
	  ystar = (W_y * dec_state.output()) + b_y
          print "current word is >>>>>>>", cw
          print "next word shud be", nw
          #loss = dy.pickneglogsoftmax(ystar, wids[nw])
          for wid in wids:
	     loss = dy.pickneglogsoftmax(ystar, wids[wid])
	     print "Loss for ", wid, " w.r.t ", nw, " is ", loss.value()   



from collections import defaultdict
from itertools import count
import sys

class RNNLanguageModel:
  
    def __init__(self, model, LAYERS, INPUT_DIM, HIDDEN_DIM, VOCAB_SIZE, builder=SimpleRNNBuilder):
        self.builder = builder(LAYERS, INPUT_DIM, HIDDEN_DIM, model)

        self.lookup = model.add_lookup_parameters((VOCAB_SIZE, INPUT_DIM))
        self.R = model.add_parameters((VOCAB_SIZE, HIDDEN_DIM))
        self.bias = model.add_parameters((VOCAB_SIZE))

    def save_to_disk(self, filename):
        model.save(filename, [self.builder, self.lookup, self.R, self.bias])

    def load_from_disk(self, filename):
        (self.builder, self.lookup, self.R, self.bias) = model.load(filename)
        
    def build_lm_graph(self, sent):
        renew_cg()
        init_state = self.builder.initial_state()

        R = parameter(self.R)
        bias = parameter(self.bias)
        errs = [] # will hold expressions
        es=[]
        state = init_state
        for (cw,nw) in zip(sent,sent[1:]):
            # assume word is already a word-id
            x_t = lookup(self.lookup, int(cw))
            state = state.add_input(x_t)
            y_t = state.output()
            r_t = bias + (R * y_t)
            err = pickneglogsoftmax(r_t, int(nw))
            errs.append(err)
        nerr = esum(errs)
        return nerr
    
    def predict_next_word(self, sentence):
        renew_cg()
        init_state = self.builder.initial_state()
        R = parameter(self.R)
        bias = parameter(self.bias)
        state = init_state
        for cw in sentence:
            # assume word is already a word-id
            x_t = lookup(self.lookup, int(cw))
            state = state.add_input(x_t)
        y_t = state.output()
        r_t = bias + (R * y_t)
        prob = softmax(r_t)
        return prob
    
    def sample(self, first=1, nchars=0, stop=-1):
        res = [first]
        renew_cg()
        state = self.builder.initial_state()

        R = parameter(self.R)
        bias = parameter(self.bias)
        cw = first
        while True:
            x_t = lookup(self.lookup, cw)
            state = state.add_input(x_t)
            y_t = state.output()
            r_t = bias + (R * y_t)
            ydist = softmax(r_t)
            dist = ydist.vec_value()
            rnd = random.random()
            for i,p in enumerate(dist):
                rnd -= p
                if rnd <= 0: break
            res.append(i)
            cw = i
            if cw == stop: break
            if nchars and len(res) > nchars: break
        return res



class RNNEncoderDecoder:
  
    def __init__(self, model, LAYERS, INPUT_DIM, HIDDEN_DIM, VOCAB_SIZE, lookup, builder=SimpleRNNBuilder):
        self.builder = builder(LAYERS, INPUT_DIM, HIDDEN_DIM, model)

        self.lookup = lookup
        self.R = model.add_parameters((VOCAB_SIZE, HIDDEN_DIM))
        self.bias = model.add_parameters((VOCAB_SIZE))

    def save_to_disk(self, filename):
        model.save(filename, [self.builder, self.lookup, self.R, self.bias])

    def load_from_disk(self, filename):
        (self.builder, self.lookup, self.R, self.bias) = model.load(filename)
        
    def build_lm_graph(self, sent):
        renew_cg()
        init_state = self.builder.initial_state()

        R = parameter(self.R)
        bias = parameter(self.bias)
        errs = [] # will hold expressions
        es=[]
        state = init_state
        for (cw,nw) in zip(sent,sent[1:]):
            # assume word is already a word-id
            x_t = lookup(self.lookup, int(cw))
            state = state.add_input(x_t)
            y_t = state.output()
            r_t = bias + (R * y_t)
            err = pickneglogsoftmax(r_t, int(nw))
            errs.append(err)
        nerr = esum(errs)
        #return nerr
        
        encoded = r_t
        dec_state = self.builder.initial_state()
        dec_state = self.builder.initial_state(encoded)
        decoder_errs = []
        
        # Calculate losses for decoding
	for (cw, nw) in zip(sent, sent[1:]):
	  x_t = lookup(self.lookup, int(cw))
	  dec_state = dec_state.add_input(x_t)
	  y_t = dec_state.output()
	  ystar = (R * y_t) + bias
	  err = pickneglogsoftmax(r_t, int(nw))
	  decoder_errs.append(err)
	derr = esum(decoder_errs)
	return derr
        
        
    
    def predict_next_word(self, sentence):
        renew_cg()
        init_state = self.builder.initial_state()
        R = parameter(self.R)
        bias = parameter(self.bias)
        state = init_state
        for cw in sentence:
            # assume word is already a word-id
            x_t = lookup(self.lookup, int(cw))
            state = state.add_input(x_t)
        y_t = state.output()
        r_t = bias + (R * y_t)
        prob = softmax(r_t)
        return prob
      
    def resynth(self, sent):
        renew_cg()
        init_state = self.builder.initial_state()

        R = parameter(self.R)
        bias = parameter(self.bias)
        errs = [] # will hold expressions
        es=[]
        state = init_state
        for cw in sent:
            # assume word is already a word-id
            x_t = lookup(self.lookup, int(cw))
            state = state.add_input(x_t)
            y_t = state.output()
            r_t = bias + (R * y_t)
            err = pickneglogsoftmax(r_t, int(nw))
            errs.append(err)
        nerr = esum(errs)
        #return nerr
        
        encoded = r_t
        dec_state = self.builder.initial_state()
        dec_state = self.builder.initial_state(encoded)
        decoder_errs = []
        
        # Calculate losses for decoding
	for (cw, nw) in zip(sent, sent[1:]):
	  x_t = lookup(self.lookup, int(cw))
	  dec_state = dec_state.add_input(x_t)
	  y_t = dec_state.output()
	  ystar = (R * y_t) + bias
	  err = pickneglogsoftmax(r_t, int(nw))
	  decoder_errs.append(err)
	derr = esum(decoder_errs)
	return derr      
      
      
    
    def sample(self, first=1, nchars=0, stop=-1):
        res = [first]
        renew_cg()
        state = self.builder.initial_state()

        R = parameter(self.R)
        bias = parameter(self.bias)
        cw = first
        while True:
            x_t = lookup(self.lookup, cw)
            state = state.add_input(x_t)
            y_t = state.output()
            r_t = bias + (R * y_t)
            ydist = softmax(r_t)
            dist = ydist.vec_value()
            rnd = random.random()
            for i,p in enumerate(dist):
                rnd -= p
                if rnd <= 0: break
            res.append(i)
            cw = i
            if cw == stop: break
            if nchars and len(res) > nchars: break
        return res
      
      
class nnlm:

         
     def __init__(self):         
         self.feats_and_values ={}
         self.wids = defaultdict(lambda:  len(self.wids))
         self.unigrams = {}
         self.model = dy.Model()
         self.EMB_SIZE = 1
         self.HID_SIZE  = 1
         self.N = 3
         M = self.model.add_lookup_parameters((len(self.wids), self.EMB_SIZE))
         W_mh = self.model.add_parameters((self.HID_SIZE, self.EMB_SIZE * (self.N-1)))
         b_hh = self.model.add_parameters((self.HID_SIZE))
         W_hs = self.model.add_parameters((len(self.wids), self.HID_SIZE))
         b_s = self.model.add_parameters((len(self.wids)))

     def read_corpus(self, file):
       print file
       tokenizer = RegexpTokenizer(r'\w+')
       f = open(file)
       self.data_array_train = []
       for line in f:
          line = '<s> ' + line.split('\n')[0] + ' </s>'          
          words = line.split()
          for word in words:
	      if word == '<s>' or '</s>':
	           pass
	      else: 
	        word = tokenizer.tokenize(word)[0]
	        
              if word in self.unigrams:
		self.unigrams[word] = self.unigrams[word] + 1
              else:
		self.unigrams[word] = 1 
       f.close()         
       self.assign_ids()
       self.create_data(file)
       self.save_wids()
       return self.trigramfeaturedict, self.wids

     def save_wids(self):
       f = open('wids.txt','w')
       for w in self.wids:
	   f.write(w + ' ' + str(self.wids[w]) + '\n')
       f.close()     

     '''       
from nltk.tokenize import RegexpTokenizer 


     def read_corpus(self, file):
       print file
       f = open(file)
       tokenizer = RegexpTokenizer(r'\w+')
       self.data_array_train = []
       for line in f:
          line = line.split('\n')[0]
          line = ['<s>'] + tokenizer.tokenize(line) + ['</s>']
          words = [w.lower() for w in line]
          for word in words:
              if word in self.unigrams:
		self.unigrams[word] = self.unigrams[word] + 1
              else:
		self.unigrams[word] = 1 
       f.close()         
       self.assign_ids()
       self.create_data(file)
       self.save_wids()
       return self.trigramfeaturedict, self.wids
       
     def save_wids(self):
       f = open('wids.txt','w')
       for w in self.wids:
	   f.write(w + ' ' + str(self.wids[w]) + '\n')
       f.close()	   


   
   
'''   
     def assign_ids(self):
         self.wids["<unk>"] = 0
         self.wids["<s>"] = 1
         self.wids["</s>"] = 2
         for w in self.unigrams:
#	   if self.unigrams[w] > 3:
	     self.wids[w]
#           else:
#             self.wids[w] = 0
         #print "prinitn wids frm nnlm--------------", self.wids
	 return   
       
     def create_data(self, file):
         self.accumulate_trigramfeatures(file)
         
     def build_nnlm_graph(self, dictionary):
         dy.renew_cg()
         M = self.model.add_lookup_parameters((len(self.wids), self.EMB_SIZE))
         W_mh = self.model.add_parameters((self.HID_SIZE, self.EMB_SIZE * (self.N-1)))
         b_hh = self.model.add_parameters((self.HID_SIZE))
         W_hs = self.model.add_parameters((len(self.wids), self.HID_SIZE))
         b_s = self.model.add_parameters((len(self.wids)))

         w_xh = dy.parameter(W_mh)
         b_h = dy.parameter(b_hh)
         W_hy = dy.parameter(W_hs)
         b_y = dy.parameter(b_s)
         errs = []
         for context, next_word in dictionary:
	    #print context, next_word
            k =  M[self.wids[context.split()[0]]]
            kk =  M[self.wids[context.split()[1]]]
            #print k , kk
            #print k.value()
            x = k.value() + kk.value()
            #print x
            h_val = dy.tanh(w_xh * dy.inputVector(x) + b_h)
            y_val = W_hy * h_val + b_y
            err = dy.pickneglogsoftmax(y_val,self.wids[next_word])
            errs.append(err)
         gen_err = dy.esum(errs)    
         return gen_err
         

         
     def accumulate_trigramfeatures(self, file):
        self.trigramfeaturedict = {}
        g = open(file)
        for line in g:
	  line = '<s> ' + line.split('\n')[0] + ' </s>'
	  line = line.split()
	  contexts = zip(line[0:len(line)-2], line[1:len(line)-1], line[2:])
	  for prev_2, prev_1, current in contexts:
	    #print prev_2, prev_1, current
	    context = prev_2 + ' ' + prev_1
	    self.trigramfeaturedict[context] = current  
        g.close()
        return
      
          
       
         
         

class loglinearlm:
     
     def __init__(self):
         self.feats_and_values ={}
         self.wids = defaultdict(lambda: len(self.wids))
         
     def read_corpus(self, file):
       print file
       f = open(file)
       self.data_array_train = []
       for line in f:
          line = '<s> ' + line.split('\n')[0] + ' </s>'
          
          self.data_array_train.append(line)
          words = line.split()
          for word in words:
              wid = self.wids[word]
       f.close()
       #self.get_feature_vectors(file)  
       
     
     def accumulate_trigramfeatures(self, file):
        self.trigramfeaturedict = {}
        g = open(file)
        for line in g:
	  line = '<s> ' + line.split('\n')[0] + ' </s>'
	  line = line.split()
	  contexts = zip(line[0:len(line)-2], line[1:len(line)-1], line[2:])
	  for prev_2, prev_1, current in contexts:
	    #print prev_2, prev_1, current
	    context = prev_2 + ' ' + prev_1
	    self.trigramfeaturedict[context] = current
	g.close()    

     def print_words(self):
        for wid in self.wids:
            print wid, self.wids[wid]
     
     def get_vocab_size(self):
          return len(self.wids)
     
     def calculate_feature_F1(self, file):
        # This is a trigram context feature
        local_features = []
        local_words = []
        feature_vector_prime = np.zeros(self.get_vocab_size())
        g = open(file)
        for line in g:
	  line = '<s> ' + line.split('\n')[0] + ' </s>'
	  #print line
	  line = line.split()
	  contexts = zip(line[0:len(line)-2], line[1:len(line)-1], line[2:])
	  for prev_2, prev_1, current in contexts:
	    feature_vector = feature_vector_prime
	    #print prev_2, prev_1, current, self.get_vocab_size()
	    #print prev_2, self.wids[prev_2], feature_vector
	    prev_2_id = self.wids[prev_2]
	    feature_vector[prev_2_id] = 1.0
	    prev_1_id = self.wids[prev_1]
	    feature_vector[prev_1_id] = 1.0
	    local_features.append(feature_vector)
	    local_words.append(current)
            #print feature_vector
        #print features[0]   
        g.close()
	return local_features, local_words  
	           
        
     def sparse_features_to_dense_features(self, features):
        ret = np.zeros(len(features))
        #print ret
        for f in features:
             #print f
             ret[f] += 1
        return ret

     def get_feature_vectors(self, file):
            features = []
            #features.append(self.sparse_features_to_dense_features(self.calculate_feature_F1(file)))
            feats,words = self.calculate_feature_F1(file)
            features.append(feats)
            #features.append(calculate_feature_F2())
            #features.append(calculate_feature_F3())
            #features.append(calculate_feature_F4())
            #return zip(features, words)
            return zip(feats, words)
         
         
  
  
class ngramlm:
  
     def __init__(self, order):
             self.order = order
             self.unigrams = {}
             self.bigrams = {}
             self.alpha_unk = 0.02
             self.alpha_1 = 0.245
             self.alpha_2 = 0.735
             self.wids = defaultdict(lambda: len(self.wids))

     def get_vocab_size(self):
          return len(self.wids)
	
     def store_counts(self, file):
              self.get_ngrams(file, self.order)
              if self.print_flag == 1:
		 print "Unique Unigrams like :", list(self.unigrams)[0], " are ", len(self.unigrams)
  		 print "Unique Bigrams like :", list(self.bigrams)[0], " are ", len(self.bigrams)
                 
     def get_features_v1(self):
       # This is a basic version which returns wid of every word as feature and its likelihood as target
       self.training_data = []
       self.num_features = 1
       c = 1
       feature_vector = np.zeros(int(self.get_vocab_size()))   # One hot k
       print feature_vector
       for line in self.data_array_train:
	 line = line.split()	 
	 for word in line:
	   feature_vector = np.zeros(int(self.get_vocab_size()))   # One hot k
	   c = c + 1
	   wid = self.wids[word]
	   feature_vector[wid] = 1
	   if c % 1000 == 1:
	     print word, wid, feature_vector[wid] 
	   self.training_data.append(feature_vector)   
       return   
     
     def feature_function(self, ctxt):
       features = []
       features.append(self.calculate_wid(ctxt))
       return features
     
     #def get_likelihood(self, word):
       
     
     def calculate_wid(self, ctxt):
       return wids[ctxt]  
  
     
     def read_corpus(self, file):
       # for each line in the file, split the words and turn them into IDs like this:
       print file
       f = open(file)
       self.data_array_train = []
       for line in f:
          line = line.split('\n')[0]
          self.data_array_train.append(line)
          words = line.split()
          for word in words:
              wid = self.wids[word]

     def print_words(self):
        for wid in self.wids:
            print wid, self.wids[wid]
    
    
     def print_dicts(self):
             print "Printing unigrams"
             for k in self.unigrams:
	       print k,self.unigrams[k]
	     print "Printing bigrams"
	     for  k in self.bigrams:
	       print k, self.bigrams[k]
	       

     def save_dicts(self):
           with open('unigrams.pkl', 'wb') as f:
                 pickle.dump(self.unigrams, f, pickle.HIGHEST_PROTOCOL)

           with open('bigrams.pkl', 'wb') as f:
                 pickle.dump(self.bigrams, f, pickle.HIGHEST_PROTOCOL)  

     def load_dicts(self):
           with open('unigrams.pkl', 'rb') as f:
                 self.unigrams = pickle.load(f)

           with open('bigrams.pkl', 'rb') as f:
                 self.bigrams = pickle.load(f)
	       
     def get_counts(self, file):
              self.print_flag = 1
              self.store_counts(file)
     
     # Calcuates n grams from a line     
     def ngrams(self,line, n):
              lst = line.split()
              output = {}
              for i in range(len(lst) -n + 1):
	           g = ' '.join(lst[i:i+n])
                   output.setdefault(g, 0)
                   output[g] += 1
              return output 
	    
     def combine_dicts(self, base_dict, small_dict):
         for key in small_dict:
             if base_dict.has_key(key):
	         base_dict[key] = int(base_dict[key]) + int(small_dict[key])
	     else:
	         base_dict[key] = int(small_dict[key])
         return base_dict 
   
     # Calculates n grams from a file     
     def get_ngrams(self, file, count):
              f = open(file)
              for line in f:
		   line = '<s> ' + line.split('\n')[0] + ' </s>'
		   bigrams = self.ngrams(line,2)
		   self.bigrams = self.combine_dicts(self.bigrams,bigrams)
		   unigrams = self.ngrams(line,1)
		   self.unigrams = self.combine_dicts(self.unigrams,unigrams)
                   self.remove_singletons(self.unigrams)
                   
     def remove_singletons(self, base_dict):
               for key in base_dict:
                   #print key, base_dict[key]
                   if base_dict[key] < 2:
	           #print key
	              base_dict[key] = 0
	           return   
	              
     def eqn8(self, strng, print_flag):
               l = len(strng.split())
               if l == 1:
                   estimate = (1 - self.alpha_1) * (float(self.unigrams[strng]) / sum(self.unigrams.values())) + self.alpha_unk * np.exp(1e-7)
                   return estimate
               else:
                   c = strng
                   #strng = strng.split()[:-1]
                   #p = ' '.join(tk for tk in strng)
                   p = c.split()[-1]
                   if print_flag ==1:
		      print "Bigram is ", c
                      print "Unigram is ", p
                   #print (1 - self.alpha_2) * (float(self.bigrams[c]) / self.bigrams.values()))
		   #print 			       
                   estimate = (1 - self.alpha_2) * (float(self.bigrams[c]) / sum(self.bigrams.values())) + (1 - self.alpha_1) * (float(self.unigrams[p]) / sum(self.unigrams.values()))  + self.alpha_unk * np.exp(1e-7)
                   return estimate

     def get_file_perplexity(self, file):
           f = open(file)
           print_flag = 0
           self.num_sentences = 0
           self.num_oovs = 0
           self.num_words = 0
           self.logprob = 0
           arr = []
           for line in f:
	        line = line.split('\n')[0].lower()
	        #line = '<s> ' + line.split('\n')[0] + ' </s>'
	        ppl_sentence = self.get_sentence_perplexity(line,0)
	        if print_flag ==1:
	           print line, ppl_sentence, '\n'
	        arr.append(ppl_sentence)
	   #print np.mean(arr) 
	   log_arr = np.log(arr)
	   print log_arr
	   ml_corpus = -1.0 * np.sum(log_arr) * 1.0/len(arr)
	   print np.exp(ml_corpus)
	   
	   print 'Sentences: ', self.num_sentences
	   print 'Words: ', self.num_words
	   print 'OOVs: ' , self.num_oovs
	   print 'Log probability: ', self.logprob
	   self.perplexity = np.exp( -1.0 * self.logprob / ( self.num_words + self.num_sentences - self.num_oovs) * 2.71)  # SRILM constant
	   print "Perplexity over corpus is: ", self.perplexity     
	        
	        
     def get_sentence_perplexity(self, string, print_flag):
           #print len(string)
           num_tokens = 0
           num_oovs = 0
           if len(string.split()) < 2:
	      print "The Sentence you gave me is very short"
	      return -1.0 * np.log(self.eqn8(string,0) / 2)
	   else:
	      mle_sentence = np.log(1.0)
	      line =  string.split('\n')[0] + ' </s>'
	      length_line = len(string.split())
	      line = line.split()
	      b = 0
	      while b < len(line) - 1:
		if print_flag ==1:
		   print "The value of  b is ", b
		kv = line[b] + ' ' + line[b+1]
		if print_flag ==1:
		 print "I am looking for ", kv
		if line[b+1] == '</s>':
		  kv = line[b]
		if print_flag ==1:
		  print "I am looking for ", kv
        	if kv in self.bigrams and self.bigrams[kv] > 0:  
		  if print_flag ==1:
		    print "Found ",kv , " in bigrams"
		  mle = self.eqn8(kv,0)
		  length_gram = 2
		else:
		  if print_flag ==1:
		   print  "I did not find ", kv, " in bigrams" 
		  
		  kv = line[b]
		  if print_flag ==1:
		      print "Now, I am searching for ", kv
		  if kv in self.unigrams and self.unigrams[kv] > 0:
		    if print_flag ==1:
		      print "Found ",kv , " in unigrams"
		    mle = self.eqn8(kv,0)
		    length_gram = 1
		  else:
		    if print_flag ==1:
		       print  "I did not find ", kv, " in unigrams or it was a singleton. I think its an UNK" 		    
		    kv = line[b]
		    mle = self.alpha_unk * np.exp(1e-7)
		    length_gram = 1
		    num_oovs = num_oovs + 1
		b = b + length_gram
		num_tokens = num_tokens + 1 
		mle_sentence = mle_sentence + np.log(mle)
	        self.num_oovs += num_oovs
	      self.num_sentences += 1
	      self.num_words += length_line
	      self.logprob += mle_sentence
	      print_flag = 0
	      mle_sentence_old = mle_sentence 
	      
	      mle_sentence = mle_sentence * (- 1.0 / (length_line + 1 +1 - num_oovs )  )
	      ppl_sentence = np.exp(mle_sentence * 2.3)
	      if print_flag ==1:
	        print "MLE of sentence is ", mle_sentence_old, " and PPL of sentence is ", ppl_sentence, " number of words: ", length_line, " number of OOVs: "  , num_oovs
	        g = open('t','w')
	        g.write(string + '\n')
	        g.close()
	        cmd = 'ngram -lm ../data/en-de/01_srilm_bigram.model -ppl t'
	        os.system(cmd)
	        print '\n\n'
	      print_flag = 0  
	      
	      return ppl_sentence
		
	      
	      
	      
 
  	              
               

