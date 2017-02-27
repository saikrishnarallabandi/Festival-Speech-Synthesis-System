import os

titles_array = []
text_array = []

audiobook_file = '../etc/txt.done.data.ML_clean'
voice_dir = '../'
pwd = os.getcwd()
f = open(audiobook_file)
for line in f:
    line = line.split('\n')[0]
    title = line.split()[0]
    line_array = line.split()
    text = ' '.join(line_array[i] for i in range(1,len(line_array)))
    titles_array.append(title)
    text_array.append(text)
f.close()


for i in range(len(titles_array)):
    os.chdir(voice_dir)
    print titles_array[i]
    f = open('lab_ML/' + titles_array[i] +'.lab', 'w')
    text = text_array[i]
    f.write(text)
    f.close()
    utt_name = 'utt_baseline_v2/' + titles_array[i] + '.utt'
    #cmd = 'text2wave -o ' + wave_name + ' ' + filename + ' -eval "(voice_iiith_us_Blizzard2016_25April_clunits)"'
    cmd =  'bin/synthutt ' + 'lab_ML/' + titles_array[i] +'.lab ' + utt_name
    print cmd
    os.system(cmd)
    os.chdir(pwd)
      #os.system(cmd)


