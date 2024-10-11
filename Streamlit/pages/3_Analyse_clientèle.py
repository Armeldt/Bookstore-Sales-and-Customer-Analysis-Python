import streamlit as st
import pandas as pd
import numpy as np
import matplotlib as mtp
import matplotlib.pyplot as plt
import seaborn as sns
import datetime
import altair as alt
import datetime
import scipy as sp

st.header('Analyse clientèle')


## IMPORT DATA depuis le script data preparation
dfGlobal = pd.read_csv('Source_données/dfGlobal.csv')
dfGlobal['date'] = pd.to_datetime(dfGlobal['date'])
dfGlobal['categ'] = dfGlobal['categ'].astype(str)
dfGlobalcli = pd.read_csv('Source_données/dfGlobalcli.csv')
dfGlobalProd = pd.read_csv('Source_données/dfGlobalProd.csv')
products = pd.read_csv('Source_données/products.csv')
customers = pd.read_csv('Source_données/customers.csv')


# affichage des données filtrées

st.subheader('1. Courbe de Lorenz')

st.markdown('calcul du coefficient de gini')
def gini(x):
    total = 0
    for i, xi in enumerate(x[:-1], 1):
        total += np.sum(np.abs(xi - x[i:]))
    return total / (len(x)**2 * np.mean(x))

# On va convertir notre colonne de CA par client en array numpy afin de faciliter le calcul du coefficient de gini et la création de la courbe de lorenz
caClientArr = dfGlobalcli['CA'].to_numpy()
# On vient egalement ordonner de manière croissante notre liste de valeurs
caClientArr = np.sort(caClientArr)
st.write(round(gini(caClientArr),2))

st.markdown("Notre coefficient de Gini etant supérieur a 0.35 (seuil qui représente communément la frontière entre une répartition égalitaire et inégalitaire d'une série de valeurs), on peut deja déduire que le chiffre d'affaire de la libraire Lapage est **répartie de manière inégalitaire** entre ses clients. Voyons en détail comment ce dernier est répartie via la courbe de Lorenz")


# Courbe de Lorenz
def lorenz(caClientArr):
    scaled_prefix_sum = caClientArr.cumsum() / caClientArr.sum() * 100
    return np.insert(scaled_prefix_sum, 0, 0)


# Calcul du coefficient de Gini
def gini(caClientArr):
    sorted_ca = np.sort(caClientArr)
    n = len(caClientArr)
    cumulative_sum = sorted_ca.cumsum()
    gini_sum = (cumulative_sum / cumulative_sum[-1]).sum()
    fair_area = n / 2.0
    total_area = gini_sum - fair_area
    return total_area / fair_area


# Calcul de la courbe de Lorenz
y = lorenz(caClientArr)
x = np.linspace(0.0, 1.0, len(y)) * 100

# Création d'un DataFrame avec les données
data = pd.DataFrame({'Part cumulée des clients (en %)': x, "Part cumulée du CA (en %)": y})

# Création du graphique avec Altair
CA_cumule_chart = alt.Chart(data).mark_line().encode(
    x='Part cumulée des clients (en %)',
    y="Part cumulée du CA (en %)"
).properties(
    title='Répartition du chiffre d\'affaire par clients'
)

# Affichage de la droite d'égalité parfaite
perfect_line = alt.Chart(pd.DataFrame({'x': [0, 100], 'y': [0, 100]})).mark_line(color='red').encode(
    x='x',
    y='y',
    tooltip=[]
)

#### WIDGET DE SELECTION DE PART DE CLIENT CUMULE ###


# Champ de sélection du pourcentage de part cumulée des clients
selected_percentage = st.slider("Sélectionnez un pourcentage de part cumulée des clients", 0, 100, 50)

# Calcul de la part de CA cumulée correspondante
selected_ca_percentage = np.interp(selected_percentage, x, y)

# Trouver le point d'intersection avec la courbe de Lorenz
intersection_index = np.argmin(np.abs(y - selected_ca_percentage))
intersection_x = x[intersection_index]

# Ajout de la ligne horizontale sur le graphique
selected_line_horizontal = alt.Chart(pd.DataFrame({'x': [0, intersection_x], 'y': [selected_ca_percentage, selected_ca_percentage]})).mark_line(color='green').encode(
    x='x',
    y='y',
    tooltip=[]
)

# Ajout de la ligne verticale sur le graphique
selected_line_vertical = alt.Chart(pd.DataFrame({'x': [intersection_x, intersection_x], 'y': [0, selected_ca_percentage]})).mark_line(color='green').encode(
    x='x',
    y='y',
    tooltip=[]
)

# Affichage du graphique avec Streamlit
st.altair_chart((CA_cumule_chart + perfect_line + selected_line_horizontal + selected_line_vertical), use_container_width=True) # works

# Affichage de la part de CA cumulée correspondante
st.write("Part de CA cumulée correspondante :", round(selected_ca_percentage, 2), '%')
st.markdown("La visualisation de la courbe de Lorenz nous permet de confirme que la répartition du chiffre d'affaire par clients est **inégalitaire**. A titre d'exemple, on peut constater que les 20% des clients les plus dépensiers génèrent a eux seuls quasiment 50% du CA de la boutique.")
st.markdown("On peut également constater au sommet de la courbe de lorenz, qu'une poignée de client représente a eux seuls environ 8 a 10% du chiffre d'affaire de la boutique :")


df_filtered = dfGlobalcli[['client_id', 'CA']]
st.dataframe(df_filtered.sort_values(by='CA', ascending = False).head(10))

st.markdown("On va stocker dans un dataframe spécifique ces clients dont le CA (supérieur a 100k€) témoigne d'une consommation de livre plus proche de celle d'une entreprise que d'un particulier")

clientsBtoB = ['c_1609','c_4958','c_6714','c_3454']
dfGlobalcliBtoB = dfGlobalcli.loc[dfGlobalcli['client_id'].isin(clientsBtoB),:]
dfGlobalcliBtoC = dfGlobalcli.loc[~dfGlobalcli['client_id'].isin(clientsBtoB),:]
transactionsBtoC = dfGlobal[~dfGlobal['client_id'].isin(clientsBtoB)].reset_index(drop=True)


st.subheader('2. Le lien entre le genre d’un client et les catégories des livres achetés')

row1_1, row1_spacer1, row1_2 = st.columns((5, .1, 3))

with row1_1:
    catxgenre = dfGlobal.groupby(['sex', 'categ']).sum('price')
    catxgenre = catxgenre.reset_index()
    catxgenre = catxgenre.loc[:, ['sex', 'categ', 'price']].rename(columns={'categ':'Catégories','price' : "CA"})
    catxgenre['proportion en %'] = round(((catxgenre['CA'] / catxgenre.groupby('Catégories')['CA'].transform('sum')) * 100),2)
    st.dataframe(catxgenre.sort_values(by='Catégories'))

with row1_2:
    catxgenre_bar = alt.Chart(catxgenre).mark_bar(binSpacing=2).encode(
        x=alt.X('Catégories:N', axis=alt.Axis(labelAngle=0)),
        y='proportion en %',
        color='sex:N'
    )
    st.altair_chart(catxgenre_bar)

st.markdown("La réalisation d'un test de Khi2 sur les deux variables qualitatives que sont le sexe et la catégorie de livre nous confirme ce qu'on peut constater a l'oeil nu sur le graph ci-dessus : le sexe et la catégorie sont effectivement deux variables corrélées")
st.markdown("Cependant le test, qui démontre une corrélation **statistiquement significative** (p_value inférieur a 0,05) nous indique également que le lien entre nos deux variables est **très faible** (confirmé via la méthode du V de Cramer dont la valeur excède a peine 14%)")
st.markdown("D'un point de vue métier, cette corrélation n'est donc pas intéressante à traiter, **les clients d'un genre différent ayant des habitudes de consommation sensiblement similaires en matière de catégories de livres achetés**")

st.subheader('3. Analyses par age')

st.markdown("Afin de permettre une analyse plus lisible, on va venir créer des tranche d'âges afin de représenter l'ensemble des catégories d'acheteurs de la librairie par des tranches de vies communes d'un point de vue marketing :")
st.markdown("*   Les étudiants (18 - 24 ans)")
st.markdown("*   Les jeunes actifs (25 - 34 ans)")
st.markdown("*   Les actifs + parentalité (35 - 44 ans)")
st.markdown("*   Les actifs  (45 - 60 ans)")
st.markdown("*   Les retraités (61 ans et plus)")

with st.expander('Afficher les données brutes'):
    st.dataframe(dfGlobalcli)


st.markdown("#### 3.1 Lien entre l'âge des clients et les montants d'achats effectués")

st.markdown("Afin de réaliser cette analyse, nous allons exploiter nos tranches d'age et voir si la repartition des clients & la somme du CA diffère entre ces dernières")

row11_1, row11_spacer1, row11_2 = st.columns((2, .1, 2))

with row11_1:
    st.altair_chart(alt.Chart(dfGlobalcliBtoC).mark_boxplot(size=20).encode(
        alt.X("tranche_age", axis=alt.Axis(labelAngle=0)),
        y='CA',
        tooltip=['CA','tranche_age']).properties(
        title="Répartition du CA par tranche d\'âge",
        width=300))


with row11_2:
    montantParTrancheAge = dfGlobalcliBtoC.groupby(["tranche_age"]).agg({'CA':'sum', 'nb_achats':'sum',}).rename(columns={'price' : 'CA'}).reset_index().sort_values('CA', ascending=False)
    st.altair_chart(alt.Chart(montantParTrancheAge).mark_bar().encode(
        x=alt.X("tranche_age", axis=alt.Axis(labelAngle=0)),
        y='CA',
        tooltip=['CA','tranche_age']).properties(
        title="Chiffre d'affaire cumulé par tranche d\'âge",
        width=300))

st.markdown("Que ce soit dans la répartition ou dans le cumul du chiffre d'affaire, il semblerait qu'une corrélation existe entre la tranche d'âge et le Chiffre d'affaire")

st.markdown("Afin de déterminer comment tester cette corrélation, on va observer la distribution de notre variable quantitative : la Chiffre d'affaire")

# Création des données
X = dfGlobalcliBtoC['CA']
x_min = 0
x_max = np.max(X)
mean = np.mean(X)
std = np.std(X)
x = np.linspace(x_min, x_max, 100)
y = sp.stats.norm.pdf(x, mean, std)

# Création du dataframe
data = pd.DataFrame({'x': x, 'y': y})

# Graphique
line = alt.Chart(data).mark_line(color='blue').encode(
    x='x',
    y='y'
).properties(
    title='Comparaison entre la distribution du CA de librairie et une distribution normale',
    width=500,
    height=400
)

distrib = alt.Chart(dfGlobalcliBtoC).transform_density(
    'CA',
    as_=['CA', 'density'],
).mark_area(color='indianred',
            fillOpacity=0.5,
            stroke='indianred',
            strokeWidth=2).encode(
    x="CA:Q",
    y='density:Q',
)

distribCA_chart = distrib + line
distribCA_chart.configure_axis(
    labelFontSize=10,
    titleFontSize=10
).configure_legend(
    title=None
).configure_title(
    fontSize=10
)
container = st.container()
with container:
    st.altair_chart(distribCA_chart, use_container_width=True)

st.markdown("Confirmé a l'aide d'un **test de Shapiro**, la distribution non normale de notre variable de CA entraine l'utilisation d'un test non paramétrique afin de confirmer ou infirmer la corrélation, nous allons utiliser celui de Kruskal-Wallis")

st.markdown("Le statistique du test (dont la valeur est de 404,2) combinée a une valeur p très faible (<0,05) viens confirmer l'interpretation faite des deux premiers graphiques : les groupes créés par nos tranches d'âge différent significativement les uns des autres en terme de valeur dans la variable CA")

st.markdown("La réalisation d'un test de **Welch-ANOVA** (défini suite au test des variances des groupes) en complément vient confirmer qu'un lien significatif existe entre nos deux variables")

st.markdown("Pour la librairie, cela signifie qu'il peut être très intéressant d'exploiter cette corrélation afin d'adapter son ciblage en matière de marketing et / ou d'offre")

st.markdown("#### 3.2 Le lien entre l'âge des clients et la fréquence d'achat")

st.markdown("Observons désormais la répartition de la fréquence d'achat des clients en fonction de leur âge")


st.altair_chart(alt.Chart(dfGlobalcliBtoC).mark_circle(size=60).encode(
    x='age',
    y='nb_achats',
    color='freq_achat_mensuelle',
    tooltip=['age', 'nb_achats', 'freq_achat_mensuelle']
    ).properties(
    ),use_container_width=True)


st.markdown("A vue d'oeil il semblerait que les tranches d'âge ayant le plus fort CA cumulé sont également celles qui achètent le plus souvent en boutique (30 - 50 ans)")
st.markdown("Au dela de cette première observation, nous allons vérifier si les deux variables que sont l'âge et la fréquence d'achat sont corrélées") 

row111_1, row111_spacer1, row111_2 = st.columns((2, .1, 2))

###### DISTRIB AGE ######
with row111_1 : 
    # Création des données pour la distribution d'âge
    X_age = dfGlobalcliBtoC['age']
    x_min_age = 0
    x_max_age = np.max(X_age)
    mean_age = np.mean(X_age)
    std_age = np.std(X_age)
    x_age = np.linspace(x_min_age, x_max_age, 100)
    y_age = sp.stats.norm.pdf(x_age, mean_age, std_age)

    # Création du dataframe pour la distribution d'âge
    data_age = pd.DataFrame({'x': x_age, 'y': y_age})

    # Graphique pour la distribution d'âge
    line_age = alt.Chart(data_age).mark_line(color='blue').encode(
        x='x',
        y='y'
    ).properties(
        title='Ditribution de l\'âge'
    )

    distribAge = alt.Chart(dfGlobalcliBtoC).transform_density(
        'age',
        as_=['age', 'density']
    ).mark_area(color='indianred',
                fillOpacity=0.5,
                stroke='indianred',
                strokeWidth=2).encode(
        x="age:Q",
        y='density:Q'
    )

    distribAge_chart = distribAge + line_age
    st.altair_chart(distribAge_chart)

with row111_2:  
    ###### DISTRIB FREQ ACHAT ######

    # Création des données pour la distribution de fréquence d'achat
    X_freq = dfGlobalcliBtoC['freq_achat_mensuelle']
    x_min_freq = 0
    x_max_freq = np.max(X_freq)
    mean_freq = np.mean(X_freq)
    std_freq = np.std(X_freq)
    x_freq = np.linspace(x_min_freq, x_max_freq, 100)
    y_freq = sp.stats.norm.pdf(x_freq, mean_freq, std_freq)

    # Création du dataframe pour la distribution de fréquence d'achat
    data_freq = pd.DataFrame({'x': x_freq, 'y': y_freq})

    # Graphique pour la distribution de fréquence d'achat
    line_freq = alt.Chart(data_freq).mark_line(color='blue').encode(
        x='x',
        y='y'
    ).properties(
        title='Distribution de la Freq_achat_mensuelle',
    )

    distribFreq = alt.Chart(dfGlobalcliBtoC).transform_density(
        'freq_achat_mensuelle',
        as_=['freq_achat_mensuelle', 'density']
    ).mark_area(color='indianred',
                fillOpacity=0.5,
                stroke='indianred',
                strokeWidth=2).encode(
        x="freq_achat_mensuelle:Q",
        y='density:Q'
    )

    distribFreq_chart = distribFreq + line_freq
    st.altair_chart(distribFreq_chart)

st.markdown("Après avoir testé la distribution de nos variables, puis  leur corrélation a l'aide du test de Spearman on constate que l\'âge est un facteur qui impact la fréquence d\'achat du client mais dans des proportions contenues")
# st.markdown("D\'un point de vue business, il pourrait être intéressant de l'exploiter en créant par exemple un outil de relance commerciale a géométrie variable, avec **plus de fréquence d'envoi sur les catégories les moins suceptibles d'acheter fréquemment (moins de 30 ans et plus de 55 ans)** afin d'essayer de mieux fidéliser ces deux tranches d'âge")
# st.markdown("le calcul de la fréquence d'achat par clients représente aussi une opportunité de doter la librairie d'un outil de relance commercial")

# # grouper les achats par client et compter le nombre d'achats par client
# frequenceAchat = clients.groupby('client_id').agg({'date': ['min', 'max'],'session_id':'count'})
# frequenceAchat.columns = ['_'.join(col) for col in frequenceAchat.columns]
# frequenceAchat = frequenceAchat.rename(columns={'date_min':'Premier achat','date_max':'Dernier achat', 'session_id_count' : 'Nombre de paniers achetés'})
# frequenceAchat = frequenceAchat[frequenceAchat['Nombre de paniers achetés'] > 1]
# # calculer la durée entre le premier achat et le dernier achat en date
# frequenceAchat['période (en jours)'] = (frequenceAchat['Dernier achat'] - frequenceAchat['Premier achat']).dt.days
# # calculer la fréquence d'achat ramenée en mois
# frequenceAchat["fréquence d'achat moyenne mensuelle"] = round((frequenceAchat['Nombre de paniers achetés'] / frequenceAchat['période (en jours)']) * 30,1)
# st.dataframe(frequenceAchat.sort_values(by="fréquence d'achat moyenne mensuelle", ascending=False))


# moduleRelance = frequenceAchat
# moduleRelance['nb de jours moyen entre chaque achats']= round(moduleRelance['période (en jours)'] / moduleRelance['Nombre de paniers achetés'],0)
# moduleRelance['nb de jours moyen entre chaque achats'] = moduleRelance['nb de jours moyen entre chaque achats'].astype('int64')
# moduleRelance['Nb de jours depuis dernier achat'] = (currentDateTime - moduleRelance['Dernier achat']).dt.days



# # def filter_clients(moduleRelance, days_multiplier):
# #     return moduleRelance[moduleRelance['Nb de jours depuis dernier achat'] > moduleRelance['nb de jours moyen entre chaque achats'] * days_multiplier]

# # # Display filtered data and export to CSV
# # def display_filtered_data(moduleRelance, days_multiplier):
# #     filtered_df = filter_clients(moduleRelance, days_multiplier)
# #     filtered_df.drop(['Nombre de paniers achetés', "fréquence d'achat moyenne mensuelle", 'période (en jours)'], axis=1, inplace=True)
# #     st.dataframe(filtered_df)

# #     # Export to CSV
# #     csv_export = filtered_df.to_csv(index=False)
# #     st.download_button("Exporter en CSV", data=csv_export, file_name=f"clients_{days_multiplier}_days.csv")

# # # Interface Streamlit
# # st.markdown("Module de relance de clients")
# # days_multiplier = st.slider("Sélectionnez un multiplicateur pour filtrer les clients :", min_value=1.0, max_value=10.0, step=0.1, value=1.5)

# # st.dataframe(display_filtered_data(moduleRelance, days_multiplier))

# def filter_clients(moduleRelance, inferior_multiplier, superior_multiplier):
#     return moduleRelance[
#         (moduleRelance['Nb de jours depuis dernier achat'] > moduleRelance['nb de jours moyen entre chaque achats'] * inferior_multiplier) &
#         (moduleRelance["fréquence d'achat moyenne mensuelle"] < moduleRelance['Nb de jours depuis dernier achat'] * superior_multiplier)
#     ]

# # Display filtered data and export to CSV
# def display_filtered_data(moduleRelance, inferior_multiplier, superior_multiplier):
#     filtered_df = filter_clients(moduleRelance, inferior_multiplier, superior_multiplier)
#     filtered_df.drop(['Nombre de paniers achetés', "fréquence d'achat moyenne mensuelle", 'période (en jours)'], axis=1, inplace=True)
#     st.dataframe(filtered_df)

#     # Export to CSV
#     csv_export = filtered_df.to_csv(index=False)
#     st.download_button("Exporter en CSV", data=csv_export, file_name=f"clients_{inferior_multiplier}_{superior_multiplier}_days.csv")


# # Interface Streamlit
# st.markdown("Module de relance de clients")
# inferior_multiplier = st.slider("Sélectionnez un multiplicateur inférieur pour filtrer les clients :", min_value=1.0, max_value=10.0, step=0.1, value=1.0)
# superior_multiplier = st.slider("Sélectionnez un multiplicateur supérieur pour filtrer les clients :", min_value=1.0, max_value=10.0, step=0.1, value=1.5)

# st.dataframe(display_filtered_data(moduleRelance, inferior_multiplier, superior_multiplier))


st.markdown("#### 3.3 Le lien entre l’âge des clients et la taille du panier moyen")

st.markdown("Après avoir parlé de fréquence d'achat, nous allons désormais nous intéresser a un autre KPI crucial pour un commerce : le panier moyen")


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

st.markdown("Une première analyse visuelle de ce nuage du point qui détaille le panier moyen par âge nous permet de constater que la répartition des valeurs semble fortement différente en comparaison de la répartition des fréquences d'achat :")
st.markdown("Ce sont les moins de 30 ans qui présentent la plus grosse densité de panier moyen important, la variable se maintenant a un niveau bien plus faible pour l'immense majorité des clients de + de 30 ans")
st.markdown("La réalisation d'un test non paramétrique de **Pearson** (les deux variables étant ditribuées anormalement), nous conforte dans notre observation préalable : une corrélation statistique négative significative (coefficient de corrélation de -0,33 et p_value < 0,05) existe entre panier moyen et âge du client")


st.markdown("#### 3.4 Le lien entre l’âge des clients et les catégories des livres achetés")

st.markdown("afin de mieux comprendre les habitudes de consommation des clients, on va analyser la répartition des achats par catégories et par tranche d'âge :")

row2_1, row2_spacer1, row2_2 = st.columns((5, .1, 3))

with row2_1 : 
    catxTrancheAge = transactionsBtoC.groupby(['tranche_age', 'categ']).sum('price')
    catxTrancheAge = catxTrancheAge.reset_index()
    catxTrancheAge = catxTrancheAge.loc[:, ['tranche_age', 'categ', 'price']].rename(columns={'categ':'Catégories','price' : "CA"})
    catxTrancheAge['proportion en %'] = round(((catxTrancheAge['CA'] / catxTrancheAge.groupby('Catégories')['CA'].transform('sum')) * 100),2)
    st.dataframe(catxTrancheAge.sort_values(by='Catégories'))

with row2_2:
    catxTrancheAge_bar = alt.Chart(catxTrancheAge).mark_bar(binSpacing=4).encode(
    x=alt.X('Catégories:N', axis=alt.Axis(labelAngle=0)),
    y='proportion en %',
    color='tranche_age:N',
    tooltip=['proportion en %','Catégories','CA']
    ).properties()
    st.altair_chart(catxTrancheAge_bar, use_container_width=True)


st.markdown("Sur le graphique ci dessus, il semblerait que la tranche d'âge ait une corrélation avec la catégorie de livre achetée :")
st.markdown("* La catégorie 2 est majoritairement plébicité par les deux tranches les plus jeunes (18-24 et 25-34)")
st.markdown("* La catégorie 0 est a l'inverse majoritairement achetée par les tranches d'age supérieures (35-44 et 45-60)")
st.markdown("* La catégorie 1 est quand a elle mieux divisée entre chaque tranche d'age mais egalement la catégorie la plus achetée par les séniors(61+)")


st.markdown("le test de **Khi2** nous permet de constater qu'il **existe une corrélation significative entre la tranche d'age et la catégorie de livres achetée** par les clients de la libraire (hors BtoB). Cette observation est cependant pondérée par le test du V de Cramer qui indique par son coéfficient de 0,37 que l'association entre les deux variables étudiées **reste modérée**.")

st.markdown("En complément de cette première analyse, on va regarder également observer la répartition du volume d'achats par âge et par catégorie. On va visualiser a l'aide d'un nuage de point :")

# Création du nuage de points avec Altair
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

st.markdown("La même corrélation semble se dégager qu'avec les tranches d'âge, relation entre l'âge et la catégorie d'achat démontrée a l'aide d'un test de Kruskal-Wallis dont découle une différence significative entre nos différents groupes")