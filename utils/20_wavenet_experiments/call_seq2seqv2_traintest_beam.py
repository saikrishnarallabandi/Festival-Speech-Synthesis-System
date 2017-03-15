from seq2seq_beam import Encoder_Decoder_regress as AB
src_fname = 'ksp.phseq.data'
test_src_fname = src_fname
ab = AB(src_fname, test_src_fname, 'dur')
ab.initiate_params()
ab.train_model()
#ab.test_only()
