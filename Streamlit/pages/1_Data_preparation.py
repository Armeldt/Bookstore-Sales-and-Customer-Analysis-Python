import streamlit as st
import pandas as pd
import numpy as np
import matplotlib as mtp
import matplotlib.pyplot as plt
import seaborn as sns
import datetime

st.header('Data Préparation')

## CRéation du menu latéral

import streamlit as st

st.sidebar.header('Menu')

## IMPORT DATA
customers = pd.read_csv('Source_données/customers.csv')
products = pd.read_csv('Source_données/products.csv')
transactions = pd.read_csv('Source_données/transactions.csv')

customers['birth'] = customers['birth'].astype(int)

st.subheader('Le contexte et les sources de données')

st.markdown("Afin de réaliser l'analyse des ventes de la librairie Lapage nous avons 3 sources de données a notre disposition : ")

st.markdown("- Un export du CRM de l'entreprise avec des données sur la clientèle de la librairie")
st.markdown("- Un export de toutes les transactions effectuées sur le e-commerce")
st.markdown("- Le catalogue de l'ensemble des références disponibles sur le site de la librairie")

st.markdown("Avant de démarrer toutes analyses vérifions que les données sont bien propres et exploitables")

## DF CUSTOMERS
url_client = "/Data_preparation#le-contexte-et-les-sources-de-donn-es"
if st.sidebar.button('1.Dataframe Clients'):
    st.markdown(f"[Cliquez ici pour accéder à l'ancre](#{url_client})")


st.subheader('Dataframe Clients')

with st.expander('Afficher les données brutes'):
    st.dataframe(customers)

st.markdown("Ce dataframe stocke des données d'âge et de sexe par client")
st.markdown("On vérifie l'unicité de la clé primaire (ici la référence client) en affichant d'un côté le nombre de clients uniques") 
customers['client_id'].unique().shape

st.markdown(" et de l'autre le nombre de lignes du dataframe : ")
customers['client_id'].size
st.markdown("en complément de l'unicité, on vient également vérifier la présence de champs vides")
customersNull = customers.isna().sum(axis = 0).rename('valeurs nulles')
st.dataframe(customersNull)

## DF PRODUCTS
url_produits = "Data_preparation#dataframe-produits"
if st.sidebar.button('2.Dataframe Produits'):
    st.markdown(f"[Cliquez ici pour accéder à l'ancre](#{url_produits})")


st.subheader('Dataframe Produits')
with st.expander('Afficher les données brutes'):
    st.dataframe(products)

st.markdown("Ce dataframe stocke le catalogue produit de la librairie avec les notions de prix et de catégorie. On y dénombre :")

unique_products = len(np.unique(products.id_prod).tolist())
str_up = "🏟️ " + str(unique_products) + " Produits uniques"

unique_categ = len(np.unique(products.categ).tolist())
str_uc = "🔖 " + str(unique_categ) + " Catégories uniques"

up, uc  = st.columns(2)
up.write(str_up)
uc.write(str_uc)

st.markdown("De la même manière que précédement on va vérifier l'unicité de la clé primaire en affichant le nombre de produits uniques")
products['id_prod'].unique().shape
st.markdown("Et le nombre de lignes du dataframe")
products['id_prod'].size
st.markdown("En complément on viens également s'assurer que notre dataframe ne présente pas de valeurs nulles")
produtcsNull = products.isna().sum(axis = 0).rename('valeurs nulles')
st.dataframe(produtcsNull)


## DF TRANSACTIONS
url_transaction = "/Data_preparation#dataframe-transactions"
if st.sidebar.button('3.Dataframe Transactions'):
    st.markdown(f"[Cliquez ici pour accéder à l'ancre](#{url_transaction})")



st.subheader('Dataframe Transactions')
st.markdown("Ce dataframe stocke l'ensemble des ventes réalisées sur le site e-commerce de la librairie Lapage avec comme informations la date d'achat, le produit acheté et le client a l'origine de l'achat :")
with st.expander('Afficher les données brutes'):
    st.dataframe(transactions)
st.markdown("le dataframe présente des données de dates dont on aura besoin pour la suite des analyses")
transactions.dtypes
st.markdown("Une analyse de la nature de la donnée nous indique qu'elle est stockée au format 'objet' et non pas 'datetime' ce qui vas nous empêcher de l'exploiter correctement, il faut donc la convertir")

st.markdown("Une erreur suite a l'execution de la commande suivante '#transactions['date'] = pd.to_datetime(transactions['date'])' nous permet de constater que certains entrées du dataframe comportent la mention 'test' ce qui empêche la conversion, on va donc isoler ces lignes pour les traiter")
cleartest = transactions[transactions['date'].str.contains('test')]
st.dataframe(cleartest)

st.markdown("On viens supprimer les lignes en question qui semblent issues de tests réalisés par l'équipe du site")
transactions.drop(transactions[transactions.id_prod == 'T_0'].index, inplace=True)
cleartestv2 = transactions[transactions['date'].str.contains('test')]
st.dataframe(cleartestv2)

st.markdown("Puis on procède a la conversion des dates au format timestamp")
transactions['date'] = pd.to_datetime(transactions['date'])
transactions.dtypes


## Création d'un DF Global

url_global = "/Data_preparation#cr-ation-d-un-dataframe-global-pour-analyse"
if st.sidebar.button('4.Dataframe Global'):
    st.markdown(f"[Cliquez ici pour accéder à l'ancre](#{url_global})")


st.subheader("Création d'un dataframe global pour analyse")
st.markdown("Afin de pouvoir analyser plus en détail nos données on va dans un premier temps venir fusionner les données de notre table transaction avec les données de notre table client")
fusion1 = pd.merge (transactions, customers, on="client_id", how="left")
dfGlobal = pd.merge(fusion1, products, on="id_prod", how="left")


dfGlobal.head()
with st.expander('Afficher les données brutes'):
    st.dataframe(dfGlobal)

# On vient ensuite vérifier que ce dataframe ne contient pas de valeurs nulles générées par nos fusions

st.markdown("On vient ensuite vérifier l'intégrité des données et notamment la présence de valeurs nulles dans nos table fusionnée :")


st.dataframe(dfGlobal.isna().sum(axis = 0))
st.markdown("suite à cette vérification on constate que les différentes fusions ont générées des valeurs nulles, on les consolide dans un autre dataframe pour analyse :")
testNA = dfGlobal[dfGlobal['price'].isna()]
st.dataframe(testNA)
st.markdown("L'ensemble des valeurs nulles semblent concerner un seul produit ce qu'on va vérifier : ")
testNA['id_prod'].unique().shape
st.markdown("Effectivement seul le produit '0_2245' est concerné, regardons ce qu'il en est de ce produit dans la table d'origine Produit :")
products.loc[products['price'] == '0_2245',:]
st.markdown("Le produit n'est pas référencé dans la base de données du e-commerce, il faut remonter le problème en interne pour correction. En attendant on va le supprimer de notre table afin qu'il n'influe pas sur nos calculs d'indicateurs")
dfGlobal.dropna(subset=['price'],inplace=True)

# dfGlobal.to_csv('C:/Users/Armel/Desktop/Formation_OC/Projet_6/Source_données/dfGlobal.csv', index=False)

st.subheader("Enrichissement et déclinaisons")

st.markdown("Afin de pouvoir pousser les analyses client réalisées, on peut déja avec les informations de notre table fusionnée, claculer un indicateur supplémentaire : l'age ")

currentDateTime = datetime.datetime.now()
date = currentDateTime.date()

# Calculer l'âge des clients en soustrayant leur année de naissance de l'année actuelle
dfGlobal['age'] = date.year - dfGlobal['birth']

dfGlobal.head()
with st.expander('Afficher les données brutes'):
    st.dataframe(dfGlobal)


st.markdown("Pour le moment nous n'avons qu'une table enrichie qui pour chaque transaction nous fourni les informations du produit (id, prix, categ) et du client qui l'a acheté (id, sexe, age).")

st.markdown("cependant afin de pouvoir analyser plus en détail le comportement des clients de la librairie on va grouper notre table globale par id_client et en déduire : ")
st.markdown("- Le chiffre d'affaire global, le nombre d'achat(s) réalisé(s) et le panier moyen qui en découle")
st.markdown("- La date de son premier et de son dernier achat afin de calculer une notion de fréquence d'achat mensuelle lissée la période")

# grouper les achats par client et conserver la date de leur premier achat, celle de leur dernier achat, la somme des montants dépensés et le nombre de sessions realisées
dfGlobalcli = dfGlobal.groupby(['client_id','age','sex']).agg({'date': ['min', 'max',],'price':'sum','session_id':'count'}).reset_index()
dfGlobalcli.columns = ['_'.join(col) for col in dfGlobalcli.columns]
#on renomme les colonnes pour plus de lisibilité et pour eviter les accents & espaces
dfGlobalcli = dfGlobalcli.rename(columns={'client_id_':'client_id','age_':'age','sex_':'sex','date_min':'premier_achat','date_max':'dernier_achat', 'session_id_count' : 'nb_achats', 'price_sum':'CA'})
#on drop les clients n'ayant pas réalisé d'achats
dfGlobalcli = dfGlobalcli[dfGlobalcli['nb_achats'] >= 1]
# on calcule la durée entre le premier achat et le dernier achat en date afin de calculer une fréquence d'achat mensuelle moyenne (+ gestion des clients ayant acheté sur une seule date)
dfGlobalcli['periode_moyenne_jours'] = (dfGlobalcli['dernier_achat'] - dfGlobalcli['premier_achat']).dt.days
mask = dfGlobalcli['periode_moyenne_jours'] != 0
dfGlobalcli.loc[mask, "freq_achat_mensuelle"] = round((dfGlobalcli['nb_achats'] / dfGlobalcli['periode_moyenne_jours']) * 30,1)
dfGlobalcli.loc[~mask, "freq_achat_mensuelle"] = 0
# on ajoute la notion de panier moyen par client
dfGlobalcli["panier_moyen"] = round((dfGlobalcli['CA'] / dfGlobalcli['nb_achats']),1)
# et on ajoute les tranches d'age
# bin_labels=labels=['18-24','25-34','35-44','45-60','61+']
# dfGlobalcli["tranche_age"] = pd.cut(x=dfGlobalcli['age'], bins=[18,24,34,44,60,100],labels=bin_labels)
st.dataframe(dfGlobalcli)

st.markdown("On va également réaliser le même exercice en groupant cette fois ci sur les produits afin de récupérer les notions de chiffre d'affaire et nombre de ventes par références")

dfGlobalProd = dfGlobal.groupby(['id_prod','categ']).agg({'price':'sum','date':'count'}).reset_index()
dfGlobalProd = dfGlobalProd.rename(columns={'price':'CA','date':'nb_ventes'})
st.dataframe(dfGlobalProd)



st.subheader("Résultats :")


st.markdown("Le travail de préparation de données nous aura permis d'obtenir 6 dataframes : ")
st.markdown("- les 3 tables sources (Client, Produits, Transactions) testées et nettoyées ")
st.markdown("- Une table enrichie (dfGlobal) puis déclinée en deux nouvelles tables groupées par clients (dfGlobalCli)et par produits (dfGlobalProd)")