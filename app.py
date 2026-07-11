import requests
import streamlit as st
import pandas as pd
from PIL import Image
import io
import re
import pickle
from io import BytesIO
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np


st.set_page_config(layout="wide")
@st.cache_data
def load_data():
    with open('data.pkl', 'rb') as f:
        data = pickle.load(f)

    df = pd.read_csv('amazon.csv')
    return df,data
df,data = load_data()

def get_image(link):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    try:
        img = requests.get(link,headers=headers).content
    except ConnectionError:
        return None
    else:
        try:
            img = Image.open(io.BytesIO(img))
        except IOError:
            return None
    return img
def get_link(text):

    link = text.split('/')[-1]
    return "https://m.media-amazon.com/images/I/" + link

all_sentences = []

data['product_detail'] = (df['product_name'] )  + df['category']

data['product_detail'] = data['product_detail'].fillna('')
for sentence_list in data['product_detail']:
    all_sentences.extend(sentence_list)

tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(data['product_detail'])


st.title("Product Reccomendation System")


query = st.text_input('Enter Product name')
btn = st.button('Get recommendation')


data['rating_count'] = data['rating_count'].str.replace(',','').astype(float).fillna(0.0)
data['rating'] = pd.to_numeric(data['rating'], errors='coerce').fillna(0)

def recomend(text):
    text = str(text)
    input_vec = tfidf.transform([text])
    scores = cosine_similarity(input_vec, tfidf_matrix)
    scores = scores[0] *  (1 + data['sentiment']) * (data['rating']/5) * (np.log10(data['rating_count'] + 1))
    idx = np.argsort(scores)[::-1]
    j = 0

    product_idx = []
    product_name = []
    product_score = []
    for i in idx:
        if j==5:
            break

        if df['product_name'].iloc[i].split(',')[0] not in product_name:
            j += 1
            product_idx.append(i)
            product_name.append(df['product_name'].iloc[i].split(',')[0])
            product_score.append(scores[i])

    similarity_score = np.sort(scores)[::-1][:5]
    return product_idx,scores,product_score
def get_product_name(idx):
    l = []
    for i in idx:
        pid = data['product_id'][i]
        d = df[df['product_id'] == str(pid)]
        l.append(d['product_name'].iloc[0])
    return l

def write_product_detail(id):
    st.write(l[id])
    st.write('Actual Price:',actual_price[id])
    st.write('Discounted Price:',discount_price[id])
    st.write('Discount Rate:',discount_rate[id])
    st.write('Average Rating:',rating[id])
    st.write('Rating Count:',rating_count[id])
    st.write('Sentiment:',sentiment[id])
    st.write('similarity score',round(similarity_score[id],3))
if btn:
    if query == '':
        st.error("Please enter a product name")
    else:

        link_products = []
        actual_price = []
        discount_price = []
        discount_rate = []
        rating = []
        rating_count = []
        sentiment = []
        idx,scores,similarity_score = recomend(query)

        l = get_product_name(idx)
        for i in idx:

            link_products.append(df['img_link'].iloc[i])
            actual_price.append( df['actual_price'].iloc[i])
            discount_price.append(df['discounted_price'].iloc[i])
            discount_rate.append(df['discount_percentage'].iloc[i])
            rating.append(df['rating'].iloc[i])
            rating_count.append( df['rating_count'].iloc[i])
            sentiment.append(data['sentiment'].iloc[i])
        col1,col2,col3,col4,col5 = st.columns(5)

        with col1:


            img = get_image(link_products[0])
            if img is not None:
                st.image(img)
            else:
                st.image('poster loading fail.png')

            write_product_detail(0)

        with col2:

            img = get_image(link_products[1])
            if img is not None:
                st.image(img)
            else:
                st.image('poster loading fail.png')
            write_product_detail(1)
        with col3:

            img = get_image(link_products[2])
            if img is not None:
                st.image(img)
            else:
                st.image('poster loading fail.png')
            write_product_detail(2)
        with col4:

            img = get_image(link_products[3])
            if img is not None:
                st.image(img)
            else:
                st.image('poster loading fail.png')
            write_product_detail(3)
        with col5:

            img = get_image(link_products[4])
            if img is not None:
                st.image(img)
            else:
                st.image('poster loading fail.png')
            write_product_detail(4)