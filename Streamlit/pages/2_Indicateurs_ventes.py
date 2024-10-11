import streamlit as st
st.header('Analyse des indicateurs de ventes')

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib as mtp
import matplotlib.pyplot as plt
import seaborn as sns
import altair as alt
import datetime


st.subheader("1. Indicateurs et graphiques autour du chiffre d'affaire")

## IMPORT DATA depuis le script data preparation
dfGlobal = pd.read_csv('Source_données/dfGlobal.csv')
dfGlobal['date'] = pd.to_datetime(dfGlobal['date'])
dfGlobal['categ'] = dfGlobal['categ'].astype(str)
dfGlobalcli = pd.read_csv('Source_données/dfGlobalcli.csv')
dfGlobalProd = pd.read_csv('Source_données/dfGlobalProd.csv')
products = pd.read_csv('Source_données/products.csv')
customers = pd.read_csv('Source_données/customers.csv')

#calcul du chiffre d'affaire
CA = dfGlobal['price'].sum()
st.write("le E-commerce a réalisé", round(CA,2),"€ de chiffre d'affaire de Mars 2021 à Février 2023")


#Calcul du chiffre d'affaire par mois date hors index
caMensuel = dfGlobal.drop(['categ','birth'], axis=1).groupby(pd.Grouper(key='date', freq='M')).sum('price')
caMensuel = caMensuel.reset_index()
caMensuel['date'] = pd.to_datetime(caMensuel['date'], format='%Y-%m')
caMensuel = caMensuel.rename(columns={"price": "CA"})
st.dataframe(caMensuel)


#histogramme

caMensuel_chart = alt.Chart(caMensuel).mark_area(line={'color':'blue'},color='blue').encode(
    x=alt.X('yearmonth(date):O', axis=alt.Axis(title='Mois')),
    y=alt.Y('CA', axis=alt.Axis(title="Chiffre d'affaires")),
    tooltip=['date', 'CA']
).properties(
    title="Chiffre d'affaires mensuel",
    width=1000
)
st.altair_chart(caMensuel_chart, use_container_width=True)

#moyenne mobile 

st.subheader('La moyenne mobile')

caMensuel['rolling_avg'] = caMensuel['CA'].rolling(window=3).mean() # moyenne mobile sur 3 mois

# Options de l'utilisateur pour la moyenne mobile
rolling_window = st.slider('Fenêtre de moyenne mobile (en mois)', min_value=1, max_value=len(caMensuel), value=3)

st.write('- Utilisez le curseur pour modifier la fenêtre de moyenne mobile.')
# Calcul du chiffre d'affaires mensuel avec la moyenne mobile personnalisée
caMensuel_chart = caMensuel[['date', 'CA']].copy()
caMensuel_chart['Moyenne mobile'] = caMensuel_chart['CA'].rolling(window=rolling_window).mean()

chart = alt.Chart(caMensuel_chart).mark_line(point=True).encode(
    x=alt.X('yearmonth(date):O', axis=alt.Axis(title='Mois')),
    y=alt.Y("CA", axis=alt.Axis(title="Chiffre d'affaires")),
    tooltip=['date', "CA"]
).properties(
    title="Chiffre d'affaires mensuel avec moyenne mobile sur " + str(rolling_window) + " mois"
)

rolling_avg_chart = alt.Chart(caMensuel_chart).mark_line(point=alt.MarkConfig(color='red'), color='red').encode(
    x='date',
    y='Moyenne mobile',
    tooltip=['date', 'Moyenne mobile']
)

chart = (chart + rolling_avg_chart).properties(height=400, width=800)

st.altair_chart(chart, use_container_width=True)

st.subheader('Les tops et les flops')

# Obtenir les valeurs sélectionnables pour le selectbox
categories = dfGlobalProd['categ'].unique()

row5_1, row5_spacer2, row5_2 = st.columns((5, .1, 5))
with row5_1:
    # Sélection dans le selectbox (avec possibilité de sélection multiple)
    selected_categories = st.multiselect("Catégorie", options=categories, default=categories[:3])


    # Filtrer les données en fonction de la sélection
    filtered_df = dfGlobalProd[dfGlobalProd['categ'].isin(selected_categories)]

    # Obtenir les valeurs minimales et maximales du prix unitaire à partir des données filtrées
    min_price = float(dfGlobalProd['prix_unitaire'].min())
    max_price = float(dfGlobalProd['prix_unitaire'].max())
with row5_2:
    # Sélection dans le slider pour la fourchette de prix
    selected_min_price, selected_max_price = st.slider("Fourchette de prix", min_value=min_price, max_value=max_price, value=(min_price, max_price))

    # Filtrer les données en fonction de la fourchette de prix
    filtered_df = filtered_df[(filtered_df['prix_unitaire'] >= selected_min_price) & (filtered_df['prix_unitaire'] <= selected_max_price)]

# Afficher les résultats
row7_1, row7_spacer2, row7_2 = st.columns((5, .1, 5))
with row7_1:
    st.markdown('Les tops ⬆️')
    st.dataframe(filtered_df.sort_values(by='CA', ascending=False))

with row7_2:
    st.markdown('Les flops ⬇️')
    st.dataframe(filtered_df.sort_values(by='CA', ascending=True))