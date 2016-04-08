# GeNet: Learning Text Annotations from Crowdsourced Song Lyric Descriptions

This project is a combination of novel dataset creation and experimental model training with the goal being to produce a sequence-to-sequence network which can 'translate' between song lyrics and natural language annotations.

The dataset is being gathered from genius.com, a website which allows users to annotate song lyrics with the 'meanings' behind them. Given genius.com started as Rap Genius, the majority of the annotations are for hip-hop lyrics, which explains the example translations below.

The file scrape.py creates directories for all desired artists, and pulls all (lyric, annotation) pairs from each of their songs. Raw lyrics are additionally pulled. The code to clean, combine, and process these files is currently in the two iPython notebooks File_Combination and Create_Vocab.

The model is implemented in Tensorflow, and uses the default implementation of the sequence to sequence model with attention and embeddings as can be found in tensorflow.models.rnn.seq2seq.embedding_attention_seq2seq. The main changes to the example implementation are made in translate.py where the bucket size and data preprocessing differed from the english->french translation model. 

The dataset is still being gathered, and work is currently being done to condition the translations on the given artist. Additionally, the model architecture is expected to change to better model the data which is of a different nature than the traditional translation datasets.

Below are some examples from a preliminary model which achieved a perplexity of ~20:

Good:
“he reminds the listener that he is from compton” -> “im from that cpt”
"he has guns in the trunk of his car” -> “choppas in the trunk”
"slang for money” -> “cheese"
“he makes more money than bill gates” -> “im getting commas"

Missed direct meaning, but somewhat related :
"he describes his time in jail and how it hurt him” -> “i forgot my way”
“he likes his gun” -> “heater i spray"

Wrong:
"he makes more money than anyone” -> “i than richer than more"
"he asks his friend where the stash spot is for the money” -> “where where where the spot spot”
“even if he got caught he wouldnt talk to the police” -> “if i caught the police"

The output is expected to improve with the full larger, groomed, dataset and with a larger network.