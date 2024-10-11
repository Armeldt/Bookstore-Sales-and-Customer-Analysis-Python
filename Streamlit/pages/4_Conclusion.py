import streamlit as st
import pandas as pd
import numpy as np
import matplotlib as mtp
import matplotlib.pyplot as plt
import seaborn as sns
import datetime
import altair as alt
import datetime

## IMPORT DATA depuis le script data preparation
dfGlobal = pd.read_csv('Source_données/dfGlobal.csv')
dfGlobal['date'] = pd.to_datetime(dfGlobal['date'])
dfGlobal['categ'] = dfGlobal['categ'].astype(str)
dfGlobalcli = pd.read_csv('Source_données/dfGlobalcli.csv')
dfGlobalProd = pd.read_csv('Source_données/dfGlobalProd.csv')
products = pd.read_csv('Source_données/products.csv')
customers = pd.read_csv('Source_données/customers.csv')

clientsBtoB = ['c_1609','c_4958','c_6714','c_3454']
dfGlobalcliBtoB = dfGlobalcli.loc[dfGlobalcli['client_id'].isin(clientsBtoB),:]
dfGlobalcliBtoC = dfGlobalcli.loc[~dfGlobalcli['client_id'].isin(clientsBtoB),:]
transactionsBtoC = dfGlobal[~dfGlobal['client_id'].isin(clientsBtoB)].reset_index(drop=True)

#streamlit 

st.header('Conclusion')


st.subheader('Analyse des indicateurs de performance du e-commerce')

st.markdown("Le site e-commerce de la librairie Lapage a réalisé un chiffre d'affaire de **11,8 millions d'euros* depuis Mars 2021")

st.markdown("L'évolution de ce chiffre d'affaire est plutôt **neutre** sur la période d'analyse, d'ou l'utilité d'initier ce travail exploratoire ayant pour but de déboucher sur des idées d'améliorations à mettre en place afin de **relancer la croissance du site**")

st.markdown("le chiffre d'affaire du site est réparti de manière inégalitaire entre ses clients :") 
            
st.markdown(" * Il est majoritairement généré par une **minorité de clients réalisant des gros montants de dépenses**")
st.markdown(" * Quatre clients se détachent de la masse avec des **montants de dépenses qui s'apparentent plus à la consommation que pourrait avoir une entreprise ou une collectivité** en matière de livres")


st.subheader('Analyse de la clientèle du e-commerce')

st.markdown("Suite aux différentes analyses réalisées sur la clientèle du site, nous avons pu établir que des corélations statistiquements prouvées liaient plusieurs indicateurs de performance clé du site (CA, fréquence d'achat, panier moyen, catégorie d'achat) avec l'âge des clients.") 

st.markdown("De ces analyses émergent 3 profils de clients ayant des habitudes de consommation bien distinctes et dans lesquels on va pouvoir classer les utilisateurs du site pour mieux les adresser :")

tab1, tab2, tab3, tab4 = st.tabs(["Age x Catégorie","Age x Panier moyen","Age x Frequence d'achat","Age x Chiffre d'affaire"])

with tab1:
    Categ_age_scatterplot = alt.Chart(transactionsBtoC).mark_circle(size=60).encode(
    x='categ',
    y='age',
    color='count(age)',
    tooltip=['count(age)','categ', 'age']
    ).properties(
    width=400,
    height=300
    )
    st.altair_chart(Categ_age_scatterplot, use_container_width=True)

with tab2:
    # Création du nuage de points avec Altair
    panierMoyenAge_scatterplot = alt.Chart(dfGlobalcli).mark_circle(size=60).encode(
        x='age',
        y='panier_moyen',
        color='panier_moyen',
        tooltip=['age', 'panier_moyen']
    ).properties(
        width=400,
        height=300
    )
    st.altair_chart(panierMoyenAge_scatterplot, use_container_width=True)

with tab3:
    st.altair_chart(alt.Chart(dfGlobalcliBtoC).mark_circle(size=60).encode(
        x='age',
        y='nb_achats',
        color='freq_achat_mensuelle',
        tooltip=['age', 'nb_achats', 'freq_achat_mensuelle']
        ).properties(
        ),use_container_width=True)

with tab4:   
    st.altair_chart(alt.Chart(dfGlobalcliBtoC).mark_circle(size=60).encode(
            x='age',
            y='CA',
            color='CA',
            tooltip=['age', 'CA']
            ).properties(
            ),use_container_width=True)

st.markdown('<span style="color: blue;">**Les étudiants et jeunes actifs**</span> (dont la tranche d\'âge est située entre 18 et 32 ans)', unsafe_allow_html=True)

st.markdown(" * Ce profil comprends les clients ayant le plus fort panier moyen mais également les clients achetant le moins fréquemment")

with st.expander('Histogramme du CA dépensé par mois pour la catégorie 18-32 ans'):
   
    # Sélection des clients entre 18 et 32 ans
    selected_df = dfGlobal.loc[dfGlobal['age'].between(18, 32),:]
    selected_df = selected_df.groupby([pd.Grouper(key='date', freq='M')]).sum('price')
    selected_df = selected_df.reset_index()
    selected_df['date'] = pd.to_datetime(selected_df['date'], format='%Y-%m')
    selected_df = selected_df.rename(columns={"price": "CA"})
    # Affichage dans un graph
    st.altair_chart(alt.Chart(selected_df).mark_bar().encode(
        x='date',
        y='sum(CA)',
        tooltip=["CA","date"]
    ).properties(width=600))



st.markdown("On constate sur ce graphique que les pics de consommation de cette cible sont en Juillet et Aout, en amont de la rentrée scolaire")

st.markdown("Concernant cette cible deux actions me semblent intéressantes : ")

st.markdown("* Adapter l'offre dédiée à cette cible (scolaire) a l'approche de la rentrée de septembre pour faire gonfler le chiffre d'affaire ")
st.markdown("* Essayer de fidéliser cette clientèle à l'occasion de ce maronnier qu'est la rentrée en l'incitant à revenir sur le e-commerce pour ses loisirs via de l'action commerciale (bon de réduction, frais de livraison offert etc...) ")

st.markdown('<span style="color: blue;">**Les actifs**</span> (dont la tranche d\'âge est située entre 33 et 51 ans)', unsafe_allow_html=True)

st.markdown("Ce profil comprends les clients ayant **généré le plus de CA au sein de la boutique en ligne**, ce notamment grâce a une **très forte fréquence d'achat** malgré un **panier moyen plus faible** que les jeunes actifs & étudiants")

st.markdown("Cette cible semble acheter souvent des produits des catégories 1 et 2 mais en petite quantitée à chaque fois, pourquoi ne pas essayer de profiter de cette forte fréquence d'achat pour pousser ces clients à ajouter plus de produits à leur panier et ainsi générer plus de CA à l'aide d'actions commerciales ou d'une stratégie de prix revisitée par exemple")

st.markdown('<span style="color: blue;">**Les seniors**</span> (dont la tranche d\'age et de 50 ans et plus)', unsafe_allow_html=True)

st.markdown("Cette cible regroupe les clients ayant le plus faible CA, avec une fréquence d'achat et un panier moyen dans la moyenne basse")

st.markdown("**Cette cible semble la moins adressée des trois par le e-commerce**, que ce soit dans l'offre (les achats sont répartis entres les catégories 0 et 1, pas de catégorie de prédilection contrairement aux deux autres cibles) ou dans les actions de communication (faible CA, faible fréquence d'achat...)")

st.markdown("Il serait intéressant de comparer ces données avec leur équivalent sur les magasins physiques, cette cible etant probablement plus habituée au commerce qu'au e-commerce et en parallèle développer une offre leur permettant de compléter leur achats en magasin avec des achats sur le e-commerce. ")