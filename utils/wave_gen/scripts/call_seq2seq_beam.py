from seq2seq_beam import Attention_Batch as AB
src_fname = 'arctic_a0001.phn'
test_src_fname = 'arctic_a0001.phn'
tgt_fname = 'arctic_a0001.mcep'
test_tgt_fname = 'arctic_a0001.mcep'
ab = AB(src_fname, test_src_fname, tgt_fname, test_tgt_fname)
ab.initiate_params()
ab.train_generate_model()
#ab.test_only()
