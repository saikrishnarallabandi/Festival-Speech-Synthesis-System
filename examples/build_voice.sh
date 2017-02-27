lang=$1
VOX=$2
wav_folder=$3
txt_file=$4

cd $lang
mkdir cmu_indic_tel_$VOX
cd cmu_indic_tel_$VOX
../../../festvox/src/clustergen/setup_cg_indic cmu indic tel $VOX   # Ideally this should start as $FESTVOXDIR/src/clustergen/...
./bin/get_wavs $wav_folder/*.wav
cp $txt_file etc/txt.done.data
cp ../../run.sh .

# Optionally remove silences based on voice quality
./bin/prune_silence etc/txt.done.data
./bin/prune_middle_silences etc/txt.done.data

# Build base voice
sh run.sh 

# Build Random Forest variant
sh bin/build_cg_rfs_voice
