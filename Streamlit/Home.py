import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="Projet 6",
    page_icon="📚",
)

def main():
    st.header('Projet 6')
    

if __name__ == '__main__':
    main()

image = Image.open('logo.png')
st.image(image)

st.title('Analyse des ventes de la Librairie Lapage')

st.subheader('Sommaire :')

st.subheader('1) Point sur la data préparation')

st.subheader('2) Analyse des indicateurs de vente')

st.subheader('3) Analyse du comportement des clients')

st.subheader('4) Conclusion et recommandations')

