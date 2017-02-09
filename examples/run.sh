#!/bin/bash

#./bin/get_wavs recording/*.wav
#./bin/prune_silence wav/*.wav

./bin/do_build build_prompts etc/txt.done.data
./bin/do_build label etc/txt.done.data
./bin/do_clustergen parallel build_utts etc/txt.done.data
./bin/do_clustergen generate_statenames
./bin/do_clustergen generate_filters

./bin/do_clustergen parallel f0_v_sptk
./bin/do_clustergen parallel mcep_sptk
./bin/do_clustergen parallel combine_coeffs_v

./bin/traintest etc/txt.done.data
./bin/do_clustergen parallel cluster etc/txt.done.data.train
./bin/do_clustergen dur etc/txt.done.data.train

./bin/do_clustergen cg_test resynth cgp etc/txt.done.data.test
./bin/do_clustergen cg_test tts tts etc/txt.done.data.test

nohup ./bin/build_cg_rfs_voice


