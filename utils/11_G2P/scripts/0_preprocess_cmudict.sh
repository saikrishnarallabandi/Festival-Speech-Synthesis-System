#
tail -132918 ../data/cmudict-plain.txt > ../data/cmudict-plain_tokenized.txt 
cut -d ' ' -f 1 ../data/cmudict-plain_tokenized.txt > ../data/cmudict-plain_tokenized_input.txt
cut -d ' ' -f 2- ../data/cmudict-plain_tokenized.txt > ../data/cmudict-plain_tokenized_output.txt

