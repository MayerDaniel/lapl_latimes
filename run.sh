cd "$(dirname "$0")"
rm latimes/news*.html
python3 latimes.py
cd ./latimes
python3 ../ebookmaker.py template.json
cp "./La Times.epub" ../output
