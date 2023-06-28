pip install -r requirements.txt

gcloud app deploy index.yaml

set GOOGLE_APPLICATION_CREDENTIALS=gcd.json

gcloud config set project cloud-abin


py  -m venv env

.\env\Scripts\activate

python main.py
