setlocal
set bw=c:\rdg\Brown\1\brown_nltk_all_fixed
sed %bw% -e "s/''/ '' /g" -e "s/``/ `` /g" -e "s/\([^a-zA-Z'\-]\)\([a-zA-Z'\-]\)/\1 \2/g" -e "s/\([a-zA-Z'\-]\)\([^a-zA-Z'\-]\)/\1 \2/g" -e "s/  */\n/g" | sed -e "/^[a-zA-Z]/!d" | nodups - -fr > Brown_words.txt
