$VOX=$1
wav_folder=$2
txt_file=$3


mkdir cmu_indic_tel_$VOX
cd cmu_indic_tel_$VOX
../../../festvox/src/clustergen/setup_cg_indic cmu indic tel $VOX   # Ideally this should start as $FESTVOXDIR/src/clustergen/...
./bin/get_wavs $wav_folder
cp $txt_file etc
cp ../../../run.sh .

# Optionally remove silences based on voice quality
./bin/prune_silence etc/txt.done.data
./bin/prune_middle_silences etc/txt.done.data

# Build base voice
nohup sh run.sh 

# Build Random Forest variant
nohup sh bin/build_cg_rfs_voice
