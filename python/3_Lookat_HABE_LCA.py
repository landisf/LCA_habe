# Combine HABE data in ../habe20152017_hh_prepared_imputed.csv with LCA data in
# ../data-gwp/nfp73-ccl-preliminary-results-ipcc-gwp-april-2023.csv

import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import warnings
import seaborn as sns
import scipy.stats as st

cm = 1/2.54  # centimeters in inches

# define paths
repo_root = os.path.abspath(os.getcwd())
filedir = os.path.join(repo_root,
                       'python')
habe_2017_dir = os.path.join(repo_root,
                             'data-HABE151617')
agg_dir = os.path.join(repo_root, 'config-aggregation')
fig_dir = os.path.join(repo_root, 'figures')
in_dir = os.path.join(repo_root, 'intermediate_files')
# define filenames (including paths)
habe_lca_file = os.path.join(in_dir,
                             'habe_lca.csv')

agg_file = os.path.join(repo_root, agg_dir, 'aggregations.xlsx')
habe_standard_file = os.path.join(habe_2017_dir,
                                  'HABE151617_Standard.txt')
habe_urbanization_file = os.path.join(habe_2017_dir,
                                      'HABE151617_Wohngemeinden.txt')

habe_lca = pd.read_csv(habe_lca_file,
                       sep=',',
                       header=0,
                       index_col=0)

hh_data = pd.read_csv(habe_standard_file,
                      sep='\t',
                      header=0,
                      index_col=0)
habe_urban = pd.read_csv(habe_urbanization_file,
                         sep='\t',
                         header=0,
                         index_col=0)
hh_data.sort_index()
hh_data
habe_lca


def wtdQuantile(dataframe, var, weight=None, n=10):
    if weight is None:
        # This is what I did before
        return pd.qcut(dataframe[var], n, labels=False)
    else:
        df = dataframe.copy()
        df.sort_values(var, ascending=True, inplace=True)
        cum_sum = df[weight].cumsum()
        cutoff = max(cum_sum)/n
        quantile = np.ceil(cum_sum/cutoff-1e-12)
        return quantile.map(int)


hh_data['PopulationWeight'] = hh_data['AnzahlPersonen98']*hh_data['Gewicht20_151617']
print("Population according to HABE: ", sum(hh_data['PopulationWeight']))
min(hh_data['VerfuegbaresEinkommen08'])
hh_data['AnzahlPersonen98']
hh_data['AnzahlKinder05']
# Old:
hh_data['EquivSize'] = np.sqrt(hh_data['AnzahlPersonen98'])
# New
hh_data['EquivSize'] = (0.5 + 0.5 * (hh_data['AnzahlPersonen98']
                                     - hh_data['AnzahlKinder05'])
                        + 0.3 * hh_data['AnzahlKinder05'])
hh_data['Income'] = hh_data['VerfuegbaresEinkommen08']
hh_data['EquivInc'] = (hh_data['VerfuegbaresEinkommen08']
                       * hh_data['EquivSize'])
hh_data['EquivIncPC'] = (hh_data['VerfuegbaresEinkommen08']
                         / hh_data['EquivSize'])
hh_data['Spending'] = - hh_data['A50m']
hh_data['EquivExp'] = (- hh_data['A50m']
                       * hh_data['EquivSize'])
hh_data['EquivExpPC'] = (- hh_data['A50m']
                         / hh_data['EquivSize'])
hh_data['IncDecile'] = wtdQuantile(hh_data,
                                   'EquivIncPC',
                                   weight='PopulationWeight',
                                   n=10)
# Old, silly, unweighted way of doing things:
# hh_data['IncDecile'] = pd.qcut(hh_data['EquivalentIncome'],
#                                q=10, labels=False)
hh_data['ExpDecile'] = wtdQuantile(hh_data,
                                   'EquivExpPC',
                                   weight='PopulationWeight',
                                   n=10)
hh_data['ExpQuintile'] = wtdQuantile(hh_data,
                                     'EquivExpPC',
                                     weight='PopulationWeight',
                                     n=5)
# 110, 130, 210, 230, 300, 400, or 900  #
lets_see_110 = wtdQuantile(hh_data.loc[hh_data['Haushaltstyp14'] == 110],
                           'EquivExpPC',
                           weight='PopulationWeight',
                           n=5)
lets_see_130 = wtdQuantile(hh_data.loc[hh_data['Haushaltstyp14'] == 130],
                           'EquivExpPC',
                           weight='PopulationWeight',
                           n=5)
lets_see_210 = wtdQuantile(hh_data.loc[hh_data['Haushaltstyp14'] == 210],
                           'EquivExpPC',
                           weight='PopulationWeight',
                           n=5)
lets_see_230 = wtdQuantile(hh_data.loc[hh_data['Haushaltstyp14'] == 230],
                           'EquivExpPC',
                           weight='PopulationWeight',
                           n=5)
# 110, 130, 210, 230, 300, 400, or 900  #
lets_see_300 = wtdQuantile(hh_data.loc[hh_data['Haushaltstyp14'] == 300],
                           'EquivExpPC',
                           weight='PopulationWeight',
                           n=5)
lets_see_400 = wtdQuantile(hh_data.loc[hh_data['Haushaltstyp14'] == 400],
                           'EquivExpPC',
                           weight='PopulationWeight',
                           n=5)
lets_see_900 = wtdQuantile(hh_data.loc[hh_data['Haushaltstyp14'] == 900],
                           'EquivExpPC',
                           weight='PopulationWeight',
                           n=5)

hh_data['hhtype_quintile'] = pd.concat([lets_see_110, lets_see_130,
                                        lets_see_210, lets_see_230,
                                        lets_see_300, lets_see_400,
                                        lets_see_900])
hh_data['IncDecile']               # ranges from 1 to 10
hh_data['ExpDecile']               # ranges from 1 to 10
hh_data['ExpQuintile']               # ranges from 1 to 5
hh_data['ExpDecile'].isna().sum()
hh_data['ExpQuintile'].isna().sum()
hh_data['IncDecile'].isna().sum()
hh_data['EquivExpPC']
hh_data['popweights'] = hh_data['PopulationWeight']
hh_data['statweights'] = hh_data['Gewicht20_151617']
hh_data['npers'] = hh_data['AnzahlPersonen98']

habe_lca = pd.concat([habe_lca,
                      hh_data['IncDecile'],
                      hh_data['ExpDecile'],
                      hh_data['ExpQuintile'],
                      hh_data['popweights'],
                      hh_data['statweights'],
                      hh_data['npers'],
                      hh_data['Spending']
                      ], axis=1)

# ----------------------------------------------------------------------------------------
# Create a bunch of boxplots describing households, spending, GWP across income
# ----------------------------------------------------------------------------------------

# Create totals of GWP

# A column of zeros:
habe_lca['tot_gwp'] = 0
habe_lca['tot_high_gwp'] = 0
for c in habe_lca.columns:
    if (c[0: 3] == 'gwp'):
        if (c == 'gwp622300'):
            # gwp622300 is air transport
            habe_lca['tot_gwp'] = habe_lca['tot_gwp'] + habe_lca[c]
            habe_lca['tot_high_gwp'] = habe_lca['tot_high_gwp'] + 2*habe_lca[c]
        elif (c == 'gwp665000'):
            # gwp665000 is package holidays
            habe_lca['tot_gwp'] = habe_lca['tot_gwp'] + habe_lca[c]
            habe_lca['tot_high_gwp'] = habe_lca['tot_high_gwp'] + 2*habe_lca[c]
        else:
            habe_lca['tot_gwp'] = habe_lca['tot_gwp'] + habe_lca[c]
            habe_lca['tot_high_gwp'] = habe_lca['tot_high_gwp'] + habe_lca[c]

habe_lca['tot_gwp']
habe_lca['tot_high_gwp']

# The lowest weight in HABE is 79.7; rounding seems to introduce an error that is
# of order of magnitude ~1 percent or smaller:
habe_lca['statweights'].min()
hh_data.columns

# hh_data['Grossregion01']
# 1			Genferseeregion
# 2			Espace Mittelland
# 3			Nordwestschweiz
# 4			Zürich
# 5			Ostschweiz
# 6			Zentralschweiz
# 7			Tessin
# hh_data['Kanton08']
# 1			Kanton Zürich
# 2			Kanton Bern
# 3			Kanton Luzern
# 17			Kanton St. Gallen
# 19			Kanton Aargau
# 21			Kanton Tessin
# 22			Kanton Waadt
# 25			Kanton Genf
# 99			Übrige Kantone
# hh_data['Einkommensklasse08_151617'] # For comparison with own quintiles
# 1			1. Fünftel (< 4 530); revidiertes Gewichtungsmodell 20
# 2			2. Fünftel (4 530 – 6 717); revidiertes Gewichtungsmodell 20
# 3			3. Fünftel (6 718 – 9 288); revidiertes Gewichtungsmodell 20
# 4			4. Fünftel (9 289 – 12 855); revidiertes Gewichtungsmodell 20
# 5			5. Fünftel (≥ 12 856); revidiertes Gewichtungsmodell 20
# hh_data['Mieterhaushalt05']
# hh_data['Rentnerhaushalt05']
# hh_data['FrauAlsReferenzperson05']
# habe_urban                      #

forplotting = pd.concat([12*habe_lca['tot_gwp']/1000,
                         12*habe_lca['tot_gwp']/habe_lca['npers']/1000,
                         habe_lca['tot_gwp']/hh_data['Spending'],
                         habe_lca['statweights'].round().astype('int'),
                         habe_lca['popweights'].round().astype('int'),
                         12*hh_data['Spending'],
                         12*hh_data['EquivExpPC'],
                         12*hh_data['EquivIncPC'],
                         12*hh_data['Spending']/hh_data['npers'],
                         habe_lca['ExpDecile'],
                         habe_lca['ExpQuintile'],
                         habe_urban,
                         hh_data['Mieterhaushalt05'],
                         hh_data['Rentnerhaushalt05'],
                         hh_data['FrauAlsReferenzperson05'],
                         hh_data['Grossregion01'],
                         hh_data['Kanton08'],
                         hh_data['Einkommensklasse08_151617'],
                         hh_data['Haushaltstyp14'],
                         hh_data['HaushaltstypEinkommen14_151617'],
                         ],
                        axis=1)

# forplotting_high = pd.concat([12*habe_lca['tot_high_gwp']/1000,
#                               12*habe_lca['tot_high_gwp']/habe_lca['npers']/1000,
#                               habe_lca['tot_high_gwp']/hh_data['Spending'],
#                               habe_lca['statweights'].round().astype('int'),
#                               habe_lca['popweights'].round().astype('int'),
#                               12*hh_data['Spending'],
#                               12*hh_data['EquivExpPC'],
#                               12*hh_data['EquivIncPC'],
#                               12*hh_data['Spending']/hh_data['npers'],
#                               habe_lca['ExpDecile'],
#                               habe_lca['ExpQuintile'],
#                               habe_urban,
#                               hh_data['Mieterhaushalt05'],
#                               hh_data['Rentnerhaushalt05'],
#                               hh_data['FrauAlsReferenzperson05'],
#                               hh_data['Grossregion01'],
#                               hh_data['Kanton08'],
#                               hh_data['Einkommensklasse08_151617'],
#                               hh_data['Haushaltstyp14'],
#                               hh_data['HaushaltstypEinkommen14_151617'],
#                               ],
#                              axis=1)

forplotting.columns = ['GWP [t CO2-eq]', 'Per capita GWP [t CO2-eq]',
                       'GWP in kg CO2-eq per CHF',
                       'statweights', 'popweights',
                       'Spending', 'Equivalent spending', 'Equivalent income',
                       'Per capita spending in CHF',
                       'Decile group of lifetime income',
                       'Quintile group of lifetime income',
                       'Urbanization', 'Renting', 'Pensioner', 'Female_head',
                       'Region', 'Canton',
                       'Quintile group', 'Household type',
                       'Household type / HABE income quintile group']

forplotting['Decile group of lifetime income']
forplotting['Urbanization']     # Urban, Periurban, Rural
forplotting['Urbanization'] = forplotting['Urbanization'].astype('category')
forplotting['Renting'].min()
forplotting['Renting'].max()
# They say renaming is faster for categories:
# https://stackoverflow.com/questions/67039036/changing-category-names-in-a-pandas-data-frame
# So, first turn 'Renting' into a categorical variable with astype(),
# then rename with cat.rename_categories()
forplotting['Renting'] = forplotting['Renting'].astype('category').cat.rename_categories(
    {0: 'Owner', 1: 'Renter'}
)
forplotting['Pensioner'].min()
forplotting['Pensioner'].max()
forplotting['Pensioner'] = forplotting['Pensioner'].astype('category').\
    cat.rename_categories({0: 'Working', 1: 'Pensioner'})

forplotting['Female_head'].min()
forplotting['Female_head'].max()
forplotting['Female_head'] = forplotting['Female_head'].astype('category').\
    cat.rename_categories({0: 'Male_head', 1: 'Female_head'})

forplotting['Region']           # 1 through 7
forplotting['Region'] = forplotting['Region'].astype('category').\
    cat.rename_categories({1: 'Genferseeregion',
                           2: 'Espace Mittelland',
                           3: 'Nordwestschweiz',
                           4: 'Zürich',
                           5: 'Ostschweiz',
                           6: 'Zentralschweiz',
                           7: 'Tessin'})

forplotting['Canton']           # eight numbers (out of [1,26])
forplotting['Canton'] = forplotting['Canton'].astype('category').\
    cat.rename_categories({1: 'Kt. Zürich',
                           2: 'Kt. Bern',
                           3: 'Kt. Luzern',
                           17: 'Kt. St. Gallen',
                           19: 'Kt. Aargau',
                           21: 'Kt. Tessin',
                           22: 'Kt. Waadt',
                           25: 'Kt. Genf',
                           99: 'Other Kantons'})

forplotting['Quintile group']           # 1 ... 5

forplotting['Household type / HABE income quintile group']
forplotting['Household type / HABE income quintile group'] = \
    forplotting['Household type / HABE income quintile group'].astype('category').\
    cat.rename_categories({111: 'Single Q1',
                           112: 'Single Q2',
                           113: 'Single Q3',
                           114: 'Single Q4',
                           115: 'Single Q5',
                           131: 'Elderly single Q1',
                           132: 'Elderly single Q2',
                           133: 'Elderly single Q3',
                           134: 'Elderly single Q4',
                           135: 'Elderly single Q5',
                           211: 'Couple Q1',
                           212: 'Couple Q2',
                           213: 'Couple Q3',
                           214: 'Couple Q4',
                           215: 'Couple Q5',
                           231: 'Elderly couple Q1',
                           232: 'Elderly couple Q2',
                           233: 'Elderly couple Q3',
                           234: 'Elderly couple Q4',
                           235: 'Elderly couple Q5',
                           401: 'Parent couple Q1',
                           402: 'Parent couple Q2',
                           403: 'Parent couple Q3',
                           404: 'Parent couple Q4',
                           405: 'Parent couple Q5',
                           900: 'Others'})

# Household type is 110, 130, 210, 230, 300, 400, or 900
# 'Quintile of lifetime income' is quintiles in overall population
# I want to have quintiles within hh_types, not overall quintiles! -> hhtype_quintile
forplotting['Household type / Quintile group of lifetime income'] = \
    forplotting['Household type'] + hh_data['hhtype_quintile']

forplotting['Household type / Quintile group of lifetime income']
forplotting['Household type / Quintile group of lifetime income'] = \
    forplotting['Household type / Quintile group of lifetime income'].replace(
        [301, 302, 303, 304, 305, 901, 902, 903, 904, 905], 900).\
    astype('category').\
    cat.rename_categories({111: 'Single Q1',
                           112: 'Single Q2',
                           113: 'Single Q3',
                           114: 'Single Q4',
                           115: 'Single Q5',
                           131: 'Elderly single Q1',
                           132: 'Elderly single Q2',
                           133: 'Elderly single Q3',
                           134: 'Elderly single Q4',
                           135: 'Elderly single Q5',
                           211: 'Couple Q1',
                           212: 'Couple Q2',
                           213: 'Couple Q3',
                           214: 'Couple Q4',
                           215: 'Couple Q5',
                           231: 'Elderly couple Q1',
                           232: 'Elderly couple Q2',
                           233: 'Elderly couple Q3',
                           234: 'Elderly couple Q4',
                           235: 'Elderly couple Q5',
                           401: 'Parent couple Q1',
                           402: 'Parent couple Q2',
                           403: 'Parent couple Q3',
                           404: 'Parent couple Q4',
                           405: 'Parent couple Q5',
                           900: 'Others'
                           })

# Do this one last: we need 'Household type' to be numerical above
forplotting['Household type']           # eight numbers (out of [1,26])
forplotting['Household type'] = forplotting['Household type'].astype('category').\
    cat.rename_categories({110: 'Single',
                           130: 'Elderly single',
                           210: 'Couple',
                           230: 'Elderly couple',
                           300: 'Single parent',
                           400: 'Parent couple',
                           900: 'Others'})

forplotting['Decile group / HH type'] = \
    forplotting['Decile group of lifetime income'].astype('str') + ' - ' +\
    forplotting['Household type'].astype('str')
forplotting['Decile group / HH type']
dectypeorder = []
for decile in range(10):
    for cat in forplotting['Household type'].cat.categories:
        dectypeorder.append(str(decile+1)+' - '+cat)
forplotting['Decile group / Pensioner'] = \
    forplotting['Decile group of lifetime income'].astype('str') + ' - ' + \
    forplotting['Pensioner'].astype('str')
decpensionerorder = []
for decile in range(10):
    for cat in forplotting['Pensioner'].cat.categories:
        decpensionerorder.append(str(decile+1)+' - '+cat)
forplotting['Decile group / Renting'] = \
    forplotting['Decile group of lifetime income'].astype('str') + ' - ' + \
    forplotting['Renting'].astype('str')
decrentingorder = []
for decile in range(10):
    for cat in forplotting['Renting'].cat.categories:
        decrentingorder.append(str(decile+1)+' - '+cat)
forplotting['Decile group / Urbanization'] = \
    forplotting['Decile group of lifetime income'].astype('str') + ' - ' + \
    forplotting['Urbanization'].astype('str')
decurbanizationorder = []
for decile in range(10):
    for cat in forplotting['Urbanization'].cat.categories:
        decurbanizationorder.append(str(decile+1)+' - '+cat)


forplotting

# Split 1st and 10th decile into quintiles
# (deciles are too small for confidentiality agreement! 9000/100=90<150)
forplotting_d1 = forplotting.loc[forplotting['Decile group of lifetime income'] == 1]
forplotting_d1['Quintile within 1st decile'] = wtdQuantile(
    forplotting_d1,
    'Equivalent spending',
    weight='popweights',
    n=5)
# forplotting_d1['1st ten percentiles'] = wtdQuantile(forplotting_d1,
#                                                     'Equivalent spending',
#                                                     weight='popweights',
#                                                     n=10)
forplotting_d1['Low-inc intensity quintile group'] = wtdQuantile(
    forplotting_d1,
    'GWP in kg CO2-eq per CHF',
    weight='popweights',
    n=5)
# forplotting_d1['Low-inc intensity decile group'] = wtdQuantile(forplotting_d1,
#                                                          'GWP in kg CO2-eq per CHF',
#                                                          weight='popweights',
#                                                          n=10)
forplotting_d1['Quintile within 1st decile']
forplotting_d1['Low-inc intensity quintile group']
forplotting_d10 = forplotting.loc[forplotting['Decile group of lifetime income'] == 10]
forplotting_d10['Quintile within 10th decile'] = wtdQuantile(
    forplotting_d10,
    'Equivalent spending',
    weight='popweights',
    n=5)
# forplotting_d10['Last ten percentiles'] = wtdQuantile(forplotting_d10,
#                                                       'Equivalent spending',
#                                                       weight='popweights',
#                                                       n=10)
forplotting_d10['High-inc intensity quintile group'] = wtdQuantile(
    forplotting_d10,
    'GWP in kg CO2-eq per CHF',
    weight='popweights',
    n=5)
# forplotting_d10['High-inc intensity decile group'] = wtdQuantile(forplotting_d10,
#                                                            'GWP in kg CO2-eq per CHF',
#                                                            weight='popweights',
#                                                            n=10)
# forplotting_d10['Expenditure quinquagintile'] = forplotting_d10[
#     'Expenditure quinquagintile'
# ] + 45
forplotting_d10['Quintile within 10th decile']
forplotting_d10['High-inc intensity quintile group']

# Check that number of observations is reasonable
for quint in range(51):
    length = len(
        forplotting_d1.loc[forplotting_d1['Quintile within 1st decile']
                           == quint])
    if length > 0:
        print("In Decile group 1, number of observations in sub-quintile group "
              + str(quint) +
              " is " + str(length))
    length = len(
        forplotting_d10.loc[forplotting_d10['Quintile within 10th decile']
                            == quint])
    if length > 0:
        print("In Decile group 10, number of observations in sub-quintile group "
              + str(quint) +
              " is " + str(length))

forplotting
ID_sotomo_rich = forplotting.loc[
    forplotting['Equivalent income'] >= 16000*12
    ].index
num_obs_sotomo_rich = len(forplotting.loc[ID_sotomo_rich, :])
print("The number of observations that would be termed very rich in Sotomo study are: ",
      num_obs_sotomo_rich)
num_pers_sotomo_rich = np.sum(forplotting.loc[ID_sotomo_rich, 'popweights'])
population = np.sum(forplotting['popweights'])
print("Percentage of population that would be termed very rich in Sotomo study: ",
      num_pers_sotomo_rich/population*100)
ID_rich_intensive5 = forplotting_d10.loc[
    forplotting_d10['High-inc intensity quintile group'] == 5
].index
ID_rich_rich5 = forplotting_d10.loc[
    forplotting_d10['Quintile within 10th decile'] == 5
].index

ID_poor_intensive5 = forplotting_d1.loc[
    forplotting_d1['Low-inc intensity quintile group'] == 5
].index
ID_poor_rich5 = forplotting_d1.loc[
    forplotting_d1['Quintile within 1st decile'] == 5
].index

# In the 10th decile:
max10_gwp = max(forplotting_d10['Per capita GWP [t CO2-eq]'])
max10_int = max(forplotting_d10['GWP in kg CO2-eq per CHF'])
ID_max10_gwp = forplotting_d10.loc[
    forplotting_d10['Per capita GWP [t CO2-eq]'] == max10_gwp
].index
ID_max10_int = forplotting_d10.loc[
    forplotting_d10['GWP in kg CO2-eq per CHF'] == max10_int
].index
ID_max10_gwp
ID_max10_int
# In the first decile:
max1_gwp = max(forplotting_d1['Per capita GWP [t CO2-eq]'])
max1_int = max(forplotting_d1['GWP in kg CO2-eq per CHF'])
ID_max1_gwp = forplotting_d1.loc[
    forplotting_d1['Per capita GWP [t CO2-eq]'] == max1_gwp
].index
ID_max1_int = forplotting_d1.loc[
    forplotting_d1['GWP in kg CO2-eq per CHF'] == max1_int
].index
ID_max1_gwp
ID_max1_int

# Count number of observations in each decile of lifetime income of forplotting
obscount_last_2percentiles = forplotting_d10[
    'Quintile within 10th decile'
].value_counts()
obscount_first_2percentiles = forplotting_d1[
    'Quintile within 1st decile'
].value_counts()
obscount_deciles = forplotting['Decile group of lifetime income'].value_counts()

forplotting_high = forplotting.copy()
forplotting_high_d1 = forplotting_d1.copy()
forplotting_high_d10 = forplotting_d10.copy()

# In forplotting_high, replace values in columns 'GWP [t CO2-eq]',
# 'Per capita GWP [t CO2-eq]', and 'GWP in kg CO2-eq per CHF' with
# 12*habe_lca['tot_high_gwp']/1000,
# 12*habe_lca['tot_high_gwp']/habe_lca['npers']/1000, and
# habe_lca['tot_high_gwp']/hh_data['Spending']
forplotting_high['GWP [t CO2-eq]'] = 12*habe_lca['tot_high_gwp']/1000
forplotting_high['Per capita GWP [t CO2-eq]'] = (12*habe_lca['tot_high_gwp']
                                                 / habe_lca['npers']
                                                 / 1000)
forplotting_high['GWP in kg CO2-eq per CHF'] = (habe_lca['tot_high_gwp']
                                                / hh_data['Spending'])

# do the same for forplotting_high_d1 but only for indices for which forplotting['Decile group of lifetime income'] == 1
forplotting_high_d1['GWP [t CO2-eq]'] = \
    (12*habe_lca['tot_high_gwp']
     / 1000).loc[forplotting['Decile group of lifetime income'] == 1]
forplotting_high_d1['Per capita GWP [t CO2-eq]'] = \
    (12*habe_lca['tot_high_gwp']
     / habe_lca['npers']
     / 1000).loc[forplotting['Decile group of lifetime income'] == 1]
forplotting_high_d1['GWP in kg CO2-eq per CHF'] = \
    (habe_lca['tot_high_gwp']
     / hh_data['Spending']).loc[forplotting['Decile group of lifetime income'] == 1]

forplotting_d1
forplotting_high_d1

# do the same for forplotting_high_d10 but only for indices for which forplotting['Decile group of lifetime income'] == 10
forplotting_high_d10['GWP [t CO2-eq]'] = \
    (12*habe_lca['tot_high_gwp']
     / 1000).loc[forplotting['Decile group of lifetime income'] == 10]
forplotting_high_d10['Per capita GWP [t CO2-eq]'] = \
    (12*habe_lca['tot_high_gwp']
     / habe_lca['npers']
     / 1000).loc[forplotting['Decile group of lifetime income'] == 10]
forplotting_high_d10['GWP in kg CO2-eq per CHF'] = \
    (habe_lca['tot_high_gwp']
     / hh_data['Spending']).loc[forplotting['Decile group of lifetime income'] == 10]

forplotting_d10
forplotting_high_d10

def reindex_df(df, weight_col):
    """expand the dataframe to prepare for resampling
    result is 1 row per count per sample"""
    df = df.reindex(df.index.repeat(df[weight_col]))
    df.reset_index(drop=True, inplace=True)
    return (df)


forplotting


forboxplotting = reindex_df(forplotting, 'popweights')
forboxplotting_d1 = reindex_df(forplotting_d1, 'popweights')
forboxplotting_d10 = reindex_df(forplotting_d10, 'popweights')
forboxplotting_high = reindex_df(forplotting_high, 'popweights')
forboxplotting_high_d1 = reindex_df(forplotting_high_d1, 'popweights')
forboxplotting_high_d10 = reindex_df(forplotting_high_d10, 'popweights')

forboxplotting_d1

# Since all deciles have similar household size, per capita GWP and GWP look
# distributionally similar
# gwp_plt = sns.boxplot(x='Decile group of lifetime income',
#                       y='GWP [t CO2-eq]',
#                       data=forboxplotting,
#                       showmeans=True,
#                       meanprops={'marker': 'o',
#                                  'markerfacecolor': 'white',
#                                  'markeredgecolor': 'black',
#                                  'markersize': '3'})
# gwp_plt.set(ylim=(0, 8000))
# gwp_plt.get_figure()


def plot_differentiation(xname, filename, ymin=0, ymax=50,
                         yname='Per capita GWP [t CO2-eq]',
                         dset=forboxplotting, size=(12.5*cm, 6*cm), givenorder=None,
                         clr_plt=10, ylabscale=1, rotate=False,
                         saturation=0.75
                         ):
    # context is one of {paper, notebook, talk, poster}
    sns.set_context("poster",
                    rc={"font.size": 5, "axes.titlesize": 5, "axes.labelsize": 5})
    # sns.set(font_scale=0.2)
    sns.set(style='darkgrid')
    if type(clr_plt) is int:
        cp = sns.color_palette('hls', clr_plt)
    elif type(clr_plt) is sns.palettes._ColorPalette:
        cp = clr_plt
    elif type(clr_plt) is list:
        cp = clr_plt
    else:
        return ValueError('clr_plt must be an integer, a list, or a color palette')
    # cp = sns.color_palette('husl', 1)
    fig, ax = plt.subplots(figsize=size, tight_layout=True)
    if rotate:
        ax.tick_params(axis='x', rotation=90)
    boxplt = sns.boxplot(data=dset,
                         notch=True,
                         x=xname,
                         y=yname,
                         palette=cp,
                         saturation=saturation,
                         showmeans=True,
                         ax=ax,
                         # If you want to show 'fliers'
                         # (extreme values beyond caps/whiskers)
                         # of basic HABE data, you need permission of the FSO.
                         # But this should be ok with GWP numbers (processed data), right?
                         showfliers=False,
                         meanprops={'marker': 'o',
                                    'markerfacecolor': 'white',
                                    'markeredgecolor': 'black',
                                    'markersize': '3'},
                         order=givenorder)
    boxplt.set(ylim=(ymin, ymax))
    fs = 9
    ax.set_xlabel(xname, fontsize=fs)
    ax.set_ylabel(yname, fontsize=ylabscale*fs)
    plt.yticks(fontsize=fs)
    plt.xticks(fontsize=fs)
    # plt.show()
    pngname = filename+'.png'
    pdfname = filename+'.pdf'
    epsname = filename+'.eps'
    boxplt.get_figure().savefig(os.path.join(fig_dir, pngname), dpi=600)
    boxplt.get_figure().savefig(os.path.join(fig_dir, epsname))
    boxplt.get_figure().savefig(os.path.join(fig_dir, pdfname))
    print('Writing figure: '+filename)
    plt.close()

plot_differentiation(xname='Decile group of lifetime income', filename='pcexp_boxed',
                     ymax=140000, yname='Per capita spending in CHF',
                     dset=forboxplotting, saturation=0)
# Some thoughts on computing error bars on the mean:
# SciPy gives a SEM function to compute error bars on the mean
# https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.sem.html
# But this is not for weighted data and forboxplotting inflates n (no observations)
# by just inserting multiple instances of existing observations.
# SEM = std/sqrt(n)
# std is consistently estimated by the std of the inflated data set
# but n needs correction.
# -> SEM_W=SEM_forboxplotting * sqrt(len(forboxplotting))/sqrt(len(habe))
# where sqrt(len(...)) is based on subsamples in deciles, percentiles or whatever

# Then, how do I plot this? Boxplot is overstrained. I think I plot means with error bars
# using a separate plot command. See, e.g.:
# https://stackoverflow.com/questions/20319216/how-to-draw-an-errorplot-and-a-boxplot-sharing-x-and-y-axes
# plt.boxplot(y)
# plt.errorbar(x, np.mean(y, axis=0), yerr=np.std(y, axis=0))
# Or (depending on x-offset)
# plt.boxplot(y)
# plt.errorbar(x + 1, np.mean(y, axis=0), yerr=np.std(y, axis=0))
# Getting CI right: Example 3 in
# https://www.geeksforgeeks.org/how-to-calculate-confidence-intervals-in-python/
# shows how to get from SEM to 95%-CI for big enough samples (n>=50)
# (other examples use t-stats for smaller samples)
# import scipy.stats as st
# st.norm.interval(alpha=0.95,
#                  loc=np.mean(gfg_data),
#                  scale=st.sem(gfg_data))


def plot_errorbars(dset=forboxplotting,
                   xname='Decile group of lifetime income',
                   yname='Per capita GWP [t CO2-eq]', ymax=50,
                   obscount=obscount_deciles,
                   filename='generic_errorbar_plot', size=(12.5*cm, 6*cm),
                   rotate=False):
    sns.set(font_scale=0.8)
    fig, ax = plt.subplots(figsize=size, tight_layout=True)
    if rotate:
        ax.tick_params(axis='x', rotation=90)

    grouped_ys = dset.groupby(xname)[yname]
    expanded_obscount = dset[xname].value_counts()
    if not expanded_obscount.index.name == obscount.index.name:
        return ValueError("Obscount's index name must match xname")
    # expanded_obscount.index.name
    # obscount.index.name

    means = grouped_ys.mean()
    # Correction for actual sample size being smaller than in expanded data set:
    sems = grouped_ys.sem()*np.sqrt(expanded_obscount-1)/np.sqrt(obscount-1)
    cisnorm = st.norm.interval(confidence=0.95,
                               loc=means,
                               scale=sems)
    # convert cisnorm to dataframe
    cisnorm_ = pd.DataFrame(cisnorm).transpose()
    cisnorm_.columns = ['low', 'high']
    cisnorm_.index = means.index
    errors = cisnorm_['high'] - means

    plot_object = pd.concat([means, errors], axis=1)
    plot_object.columns = ['mean', 'error']
    plot_object

    plt.errorbar(plot_object.index, plot_object['mean'], yerr=plot_object['error'],
                 fmt='o', c='black', ecolor='black',
                 # marker='o', markerfacecolor='white', markeredgecolor='black',
                 markerfacecolor='white', markeredgecolor='black',
                 markersize='3',
                 capsize=2, capthick=1)

    # ax.legend(handles_order, reordered_labels, bbox_to_anchor=(1, 1), fontsize='7')
    ax.set(ylim=(0, ymax), ylabel=yname,
           xlabel=xname,
           xticks=plot_object.index
           )
    fs = 9
    ax.set_xlabel(xname, fontsize=fs)
    ax.set_ylabel(yname, fontsize=fs)
    plt.yticks(fontsize=fs)
    plt.xticks(fontsize=fs)
    # plt.show()
    pngname = filename+'.png'
    pdfname = filename+'.pdf'
    epsname = filename+'.eps'
    fig.get_figure().savefig(os.path.join(fig_dir, pngname), dpi=600)
    fig.get_figure().savefig(os.path.join(fig_dir, epsname))
    fig.get_figure().savefig(os.path.join(fig_dir, pdfname))
    print('Writing figure: '+filename)
    plt.close()


plot_errorbars(dset=forboxplotting,
               xname='Decile group of lifetime income',
               yname='Per capita GWP [t CO2-eq]', ymax=30,
               obscount=obscount_deciles,
               filename='errorbars_gwp', size=(12.5*cm, 6*cm))
plot_errorbars(dset=forboxplotting_d1,
               xname='Quintile within 1st decile',
               yname='Per capita GWP [t CO2-eq]', ymax=30,
               obscount=obscount_first_2percentiles,
               filename='errorbars_gwp_poor', size=(5*cm, 6*cm))
plot_errorbars(dset=forboxplotting_d10,
               xname='Quintile within 10th decile',
               yname='Per capita GWP [t CO2-eq]', ymax=30,
               obscount=obscount_last_2percentiles,
               filename='errorbars_gwp_rich', size=(5*cm, 6*cm))

plot_errorbars(dset=forboxplotting,
               xname='Decile group of lifetime income',
               yname='GWP in kg CO2-eq per CHF', ymax=0.8,
               obscount=obscount_deciles,
               filename='errorbars_gwp_chf', size=(12.5*cm, 6*cm))
plot_errorbars(dset=forboxplotting_d1,
               xname='Quintile within 1st decile',
               yname='GWP in kg CO2-eq per CHF', ymax=0.8,
               obscount=obscount_first_2percentiles,
               filename='errorbars_gwp_chf_poor', size=(5*cm, 6*cm))
plot_errorbars(dset=forboxplotting_d10,
               xname='Quintile within 10th decile',
               yname='GWP in kg CO2-eq per CHF', ymax=0.8,
               obscount=obscount_last_2percentiles,
               filename='errorbars_gwp_chf_rich', size=(5*cm, 6*cm))

# Whole population
plot_differentiation(xname=None, filename='avg_gwp_boxed', ymax=27, size=(6*cm, 6*cm))
plot_differentiation(xname=None, dset=forboxplotting_high, filename='avg_gwp_boxed_high', ymax=27, size=(6*cm, 6*cm))
# Zoom in on population mean
plot_differentiation(xname=None, filename='avg_gwp_zoomed', ymin=10, ymax=11, size=(6*cm, 6*cm))
plot_differentiation(xname=None, dset=forboxplotting_high, filename='avg_gwp_high_zoomed', ymin=10, ymax=11, size=(6*cm, 6*cm))

# Not so interesting
plot_differentiation('Female_head', 'Female_box', size=(6*cm, 6*cm), rotate=True)
plot_differentiation('Pensioner', 'Pensioner_box', size=(6*cm, 6*cm), clr_plt=2,
                     rotate=True)
plot_differentiation('Region', 'Region_box', size=(8*cm, 6*cm), rotate=True)
plot_differentiation('Quintile group', 'Quintile_box', size=(8*cm, 6*cm), rotate=True)


# Create some color palettes to subdivide deciles
def create_repeating_palette(numrep, numbasic=10, nummin=None):
    """Create a color palette where each color in palette "('hls', numbasic)" is repeated
       numrep times.
    Arguments:
    numrep: number of times to repeat each color
    numbasic: number of basic colors to use (argument to color_palette('hls', .))
    nummin: color in palette_hls to start with
    Output:
    palette_out: the resuling color palette
    """
    palette_hls = sns.color_palette('hls', numbasic)
    palette_out = []
    count = 0
    for col in palette_hls:
        count = count + 1
        if nummin is None:
            for _ in range(numrep):
                palette_out.extend([col])
        elif count >= nummin:
            for _ in range(numrep):
                palette_out.extend([col])
    return palette_out


palette_2 = create_repeating_palette(2)
palette_3 = create_repeating_palette(3)
palette_4 = create_repeating_palette(4)
palette_5 = create_repeating_palette(5)
palette_5_min10 = create_repeating_palette(5, numbasic=10, nummin=10)
palette_6 = create_repeating_palette(6)
palette_7 = create_repeating_palette(7)
ten_pairs = sns.color_palette('Paired', 10)


# Rather interesting
plot_differentiation('Urbanization', 'Urbanization_box',
                     size=(6*cm, 6*cm), clr_plt=3,
                     ylabscale=0.95, rotate=True, saturation=0)
plot_differentiation('Renting', 'Renting_box', size=(6*cm, 6*cm), clr_plt=2,
                     ylabscale=0.95, rotate=True, saturation=0)
plot_differentiation('Canton', 'Canton_box', size=(8*cm, 6*cm), rotate=True)
plot_differentiation('Household type', 'hh_type_box',
                     ymax=40, size=(8*cm, 6.5*cm), clr_plt=7,
                     ylabscale=0.95, rotate=True, saturation=0)
plot_differentiation('Household type', 'hh_type_box_gwp_per_chf',
                     ymax=1.5, yname='GWP in kg CO2-eq per CHF',
                     size=(8*cm, 6*cm),
                     clr_plt=7, rotate=True)
plot_differentiation('Household type / HABE income quintile group',
                     'hh_type_HABEincome_box',
                     clr_plt=5, rotate=True)
plot_differentiation('Household type / Quintile group of lifetime income',
                     'hh_type_income_box',
                     size=(12.5*cm, 6.99*cm),
                     clr_plt=5,
                     ylabscale=0.95, rotate=True)

# My conclusion: 'Renting', 'Urbanization', and 'Household type' have somewhat interesting
#                differences.
#                I want to analyze the consumption composition of GWP in those HH types.


# Plot the GWP composition of the different household types
plot_differentiation(xname='Decile group / HH type',
                     filename='gwp_boxed_inctype',
                     givenorder=dectypeorder,
                     size=(20*cm, 10*cm),
                     clr_plt=palette_7, rotate=True)
plot_differentiation(xname='Decile group / Pensioner',
                     filename='gwp_boxed_incpension',
                     givenorder=decpensionerorder,
                     size=(20*cm, 10*cm),
                     clr_plt=palette_2, rotate=True)
plot_differentiation(xname='Decile group / Renting',
                     filename='gwp_boxed_increnting',
                     givenorder=decrentingorder,
                     size=(20*cm, 10*cm),
                     clr_plt=palette_2, rotate=True)
plot_differentiation(xname='Decile group / Urbanization',
                     filename='gwp_boxed_incurbanization',
                     givenorder=decurbanizationorder,
                     size=(20*cm, 10*cm),
                     clr_plt=palette_3, rotate=True)
forboxplotting['Decile group / Urbanization']
plot_differentiation(xname='Decile group of lifetime income', filename='gwp_boxed',
                     ymax=50, yname='Per capita GWP [t CO2-eq]', saturation=0)
plot_differentiation(xname='Decile group of lifetime income', dset=forboxplotting_high,
                     filename='gwp_boxed_high',
                     ymax=50, yname='Per capita GWP [t CO2-eq]')
# Zoom in on mean of low-income decile group
plot_differentiation(xname='Decile group of lifetime income',
                     filename='gwp_boxed_zoomed1',
                     ymin=5, ymax=5.2, yname='Per capita GWP [t CO2-eq]')
# Zoom in on mean of high-income decile group
plot_differentiation(xname='Decile group of lifetime income',
                     filename='gwp_boxed_zoomed10',
                     ymin=18.6, ymax=18.8, yname='Per capita GWP [t CO2-eq]')
plot_differentiation(xname='Quintile group of lifetime income',
                     filename='gwp_boxed_myquintiles',
                     ymax=50, yname='Per capita GWP [t CO2-eq]', size=(8*cm, 6*cm))
plot_differentiation(xname='Quintile group',
                     filename='gwp_boxed_HABEquintiles',
                     ymax=50, yname='Per capita GWP [t CO2-eq]', size=(8*cm, 6*cm))
plot_differentiation(xname='Quintile within 10th decile',
                     filename='gwp_rich_boxed',
                     ymax=50, yname='Per capita GWP [t CO2-eq]',
                     dset=forboxplotting_d10, size=(5*cm, 6*cm),
                     clr_plt=palette_5_min10, saturation=0)
plot_differentiation(xname='Quintile within 10th decile',
                     filename='gwp_rich_boxed_high',
                     ymax=50, yname='Per capita GWP [t CO2-eq]',
                     dset=forboxplotting_high_d10, size=(5*cm, 6*cm),
                     clr_plt=palette_5_min10)
plot_differentiation(xname='Quintile within 1st decile',
                     filename='gwp_poor_boxed',
                     ymax=50, yname='Per capita GWP [t CO2-eq]',
                     dset=forboxplotting_d1, size=(5*cm, 6*cm),
                     clr_plt=palette_5, saturation=0)
plot_differentiation(xname='Quintile within 1st decile',
                     filename='gwp_poor_boxed_high',
                     ymax=50, yname='Per capita GWP [t CO2-eq]',
                     dset=forboxplotting_high_d1, size=(5*cm, 6*cm),
                     clr_plt=palette_5)
plot_differentiation(xname='Decile group of lifetime income', filename='gwp_chf_boxed',
                     ymax=1.5, yname='GWP in kg CO2-eq per CHF',
                     dset=forboxplotting, saturation=0)
plot_differentiation(xname='Quintile within 10th decile',
                     filename='gwp_chf_rich_boxed',
                     ymax=1.5, yname='GWP in kg CO2-eq per CHF',
                     dset=forboxplotting_d10, size=(5*cm, 6*cm),
                     clr_plt=palette_5_min10, saturation=0)
plot_differentiation(xname='Quintile within 1st decile',
                     filename='gwp_chf_poor_boxed',
                     ymax=1.5, yname='GWP in kg CO2-eq per CHF',
                     dset=forboxplotting_d1, size=(5*cm, 6*cm),
                     clr_plt=palette_5, saturation=0)
plot_differentiation(xname='Decile group of lifetime income',
                     filename='gwp_chf_boxed_high',
                     ymax=1.5, yname='GWP in kg CO2-eq per CHF',
                     dset=forboxplotting_high)
plot_differentiation(xname='Quintile within 10th decile',
                     filename='gwp_chf_rich_boxed_high',
                     ymax=1.5, yname='GWP in kg CO2-eq per CHF',
                     dset=forboxplotting_high_d10, size=(5*cm, 6*cm),
                     clr_plt=palette_5_min10)
plot_differentiation(xname='Quintile within 1st decile',
                     filename='gwp_chf_poor_boxed_high',
                     ymax=1.5, yname='GWP in kg CO2-eq per CHF',
                     dset=forboxplotting_high_d1, size=(5*cm, 6*cm),
                     clr_plt=palette_5)
plot_differentiation(xname='Decile group of lifetime income', filename='exp_boxed',
                     ymax=300000, yname='Spending',
                     dset=forboxplotting)
plot_differentiation(xname='Decile group of lifetime income', filename='eqexp_boxed',
                     ymax=140000, yname='Equivalent spending',
                     dset=forboxplotting)
plot_differentiation(xname='Decile group of lifetime income', filename='eqinc_boxed',
                     ymax=250000, yname='Equivalent income',
                     dset=forboxplotting)
plot_differentiation(xname='Quintile within 10th decile',
                     filename='eqinc_rich_boxed',
                     ymax=250000, yname='Equivalent income',
                     dset=forboxplotting_d10, size=(5*cm, 6*cm),
                     clr_plt=palette_5_min10)
plot_differentiation(xname='Decile group of lifetime income', filename='pcexp_boxed',
                     ymax=140000, yname='Per capita spending in CHF',
                     dset=forboxplotting, saturation=0)

# ----------------------------------------------------------------------------------------
# Create barplots that distinguish different consumption categories
# ----------------------------------------------------------------------------------------

# Add interesting variables for plotting (we take everything for plotting from habe_lca
habe_lca = pd.concat([habe_lca,
                      forplotting['Urbanization'],
                      forplotting['Renting'],
                      forplotting['Household type']
                      ], axis=1)

habe_lca.columns


def cats4plotting(stats_index=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                  xrange=range(10), xlabel='ExpDecile',
                  index_dict={}):
    pcmeans_container = pd.DataFrame()
    intmeans_container = pd.DataFrame()
    hhmeans_container = pd.DataFrame()
    pcmeans_container_ch = pd.DataFrame()
    intmeans_container_ch = pd.DataFrame()
    hhmeans_container_ch = pd.DataFrame()
    stats_index.append('CH')
    stats_container = pd.DataFrame(index=stats_index)
    stats_container['min'] = float('nan')
    stats_container['max'] = float('nan')
    stats_container['std'] = float('nan')
    stats_container['avg'] = float('nan')
    stats_container['avg_size'] = float('nan')
    stats_container['std_biased'] = float('nan')
    stats_container['std_biased_weighted'] = float('nan')
    with warnings.catch_warnings():
        # warnings.filterwarnings can filter by:
        # - message='string' where string is a regex or substring of the messages
        # - lineno
        # - module
        # - category
        warnings.filterwarnings("ignore", message='DataFrame is highly fragmented.')
        # ----------------------------------------------------------------------
        # Statistics and categorization for CH
        # ----------------------------------------------------------------------
        d_weight = habe_lca['statweights']
        d_npers = habe_lca['npers']
        d_gwp = habe_lca['tot_gwp']*12/1000
        stats_container['min']['CH'] = min(d_gwp/d_npers)
        stats_container['max']['CH'] = max(d_gwp/d_npers)
        stats_container['std_biased']['CH'] = np.sqrt(np.cov(d_gwp/d_npers))
        stats_container['std_biased_weighted']['CH'] = np.sqrt(
            np.cov(d_gwp/d_npers,
                   aweights=(d_weight*d_npers))
        )
        stats_container['std']['CH'] = np.std(d_gwp/d_npers)
        stats_container['avg']['CH'] = np.average(d_gwp/d_npers,
                                                     weights=d_weight * d_npers)
        stats_container['avg_size']['CH'] = np.average(d_npers,
                                                          weights=d_weight)
        for c in habe_lca.columns:
            if (c[0: 3] == 'gwp'):
                # Subset of entries in column c that belong to 'decile' d
                cd_val = habe_lca[c]*12/1000
                # The weighted per capita mean of that subset
                wmean_cd = (
                    (cd_val*d_weight).sum()
                    / (d_npers*d_weight).sum()
                )
                wintmean_cd = (
                    (
                        habe_lca[c]*d_weight
                    ).sum()
                    / (
                        habe_lca['Spending']*d_weight
                    ).sum()
                )
                whhmean_cd = (
                    (cd_val*d_weight).sum()
                    / (d_weight).sum()
                )
                # Save in the data frame 'means'
                pcmeans_container_ch.loc['CH', c] = wmean_cd
                intmeans_container_ch.loc['CH', c] = wintmean_cd
                hhmeans_container_ch.loc['CH', c] = whhmean_cd
        # ----------------------------------------------------------------------
        # Statistics and categorization for d in xrange
        # ----------------------------------------------------------------------
        for d in xrange:         # note that range(10) extends from 0 to 9
            if type(d) == int:
                section = d+1
            else:
                section = d
            d_weight = habe_lca.loc[habe_lca[xlabel] == section, 'statweights']
            d_npers = habe_lca.loc[habe_lca[xlabel] == section, 'npers']
            d_gwp = habe_lca.loc[habe_lca[xlabel] == section, 'tot_gwp']*12/1000
            # GWP intensity
            # d_int = (habe_lca.loc[habe_lca[xlabel] == section, 'tot_gwp']
            #          / habeh_lca.loc[hh_data[xlabel] == section, 'Spending'])
            stats_container['min'][section] = min(d_gwp/d_npers)
            stats_container['max'][section] = max(d_gwp/d_npers)
            stats_container['std_biased'][section] = np.sqrt(np.cov(d_gwp/d_npers))
            stats_container['std_biased_weighted'][section] = np.sqrt(
                np.cov(d_gwp/d_npers,
                       aweights=(d_weight*d_npers))
            )
            stats_container['std'][section] = np.std(d_gwp/d_npers)
            stats_container['avg'][section] = np.average(d_gwp/d_npers,
                                                         weights=d_weight * d_npers)
            stats_container['avg_size'][section] = np.average(d_npers,
                                                              weights=d_weight)
            for c in habe_lca.columns:
                if (c[0: 3] == 'gwp'):
                    # Subset of entries in column c that belong to 'decile' d
                    cd_val = habe_lca.loc[habe_lca[xlabel] == section, c]*12/1000
                    # The weighted per capita mean of that subset
                    wmean_cd = (
                        (cd_val*d_weight).sum()
                        / (d_npers*d_weight).sum()
                    )
                    wintmean_cd = (
                        (
                            habe_lca.loc[habe_lca[xlabel] == section, c]*d_weight
                         ).sum()
                        / (
                            habe_lca.loc[habe_lca[xlabel] == section, 'Spending']*d_weight
                           ).sum()
                    )
                    whhmean_cd = (
                        (cd_val*d_weight).sum()
                        / (d_weight).sum()
                    )
                    # Save in the data frame 'means'
                    pcmeans_container.loc[section, c] = wmean_cd
                    intmeans_container.loc[section, c] = wintmean_cd
                    hhmeans_container.loc[section, c] = whhmean_cd
                elif (c == 'IncDecile' or c == 'ExpDecile'):
                    cd_val = habe_lca.loc[habe_lca[xlabel] == section, c]
                    cd_intval = habe_lca.loc[habe_lca[xlabel] == section, c]
                    # The unweighted mean of decile numbers
                    mean_cd = np.mean(cd_val)
                    intmean_cd = np.mean(cd_intval)
                    pcmeans_container.loc[section, c] = mean_cd
                    intmeans_container.loc[section, c] = intmean_cd
                    hhmeans_container.loc[section, c] = mean_cd
        # ----------------------------------------------------------------------
        # Statistics and categorization for key in index_dict
        # ----------------------------------------------------------------------
        for key in index_dict:
            idx = index_dict[key]
            d_weight = habe_lca.loc[idx, 'statweights']
            d_npers = habe_lca.loc[idx, 'npers']
            d_gwp = habe_lca.loc[idx, 'tot_gwp']*12/1000
            stats_container['min'][key] = min(d_gwp/d_npers)
            stats_container['max'][key] = max(d_gwp/d_npers)
            if len(d_gwp) > 1:
                stats_container['std_biased'][key] = np.sqrt(np.cov(d_gwp/d_npers))
                stats_container['std_biased_weighted'][key] = np.sqrt(
                    np.cov(d_gwp/d_npers,
                           aweights=(d_weight*d_npers))
                )
            else:
                stats_container['std_biased'][key] = 0
                stats_container['std_biased_weighted'][key] = 0
            stats_container['std'][key] = np.std(d_gwp/d_npers)
            stats_container['avg'][key] = np.average(d_gwp/d_npers,
                                                     weights=d_weight * d_npers)
            stats_container['avg_size'][key] = np.average(d_npers,
                                                          weights=d_weight)
            for c in habe_lca.columns:
                if (c[0: 3] == 'gwp'):
                    # Subset of entries in column c that belong to decile d
                    cd_val = habe_lca.loc[idx, c]*12/1000
                    # Weighted mean of that subset
                    wmean_cd = ((cd_val*d_weight).sum()
                                / (d_npers*d_weight).sum()
                                )
                    wintmean_cd = (
                        (
                            habe_lca.loc[idx, c]*d_weight
                        ).sum()
                        / (
                            habe_lca.loc[idx, 'Spending']*d_weight
                        ).sum()
                    )
                    whhmean_cd = ((cd_val*d_weight).sum()
                                  / (d_weight).sum()
                                  )
                    # Save in the data frame 'means'
                    pcmeans_container.loc[key, c] = wmean_cd
                    intmeans_container.loc[key, c] = wintmean_cd
                    hhmeans_container.loc[key, c] = whhmean_cd
                elif (c == 'ExpDecile'):
                    cd_val = habe_lca.loc[idx, c]
                    # The unweighted mean of decile numbers
                    mean_cd = np.mean(cd_val)
                    pcmeans_container.loc[key, c] = mean_cd
                    intmeans_container.loc[key, c] = intmean_cd
                    hhmeans_container.loc[key, c] = mean_cd
    return pcmeans_container, stats_container, hhmeans_container, intmeans_container,\
        pcmeans_container_ch, hhmeans_container_ch, intmeans_container_ch


# The default case:
(means_expdec, stats_expdec, hhmeans_expdec, means_expdec_int,
 means_expdec_ch, hhmeans_expdec_ch, means_expdec_int_ch
 ) = cats4plotting()
stats_expdec
means_expdec_ch
means_expdec_int
# Income deciles rather than expenditure deciles:
(means_incdec, stats_incdec,
 hhmeans_incdec, means_incdec_int,dump1,dump2,dump3) = cats4plotting(xlabel='IncDecile')

# Want integers rather than floats to describe deciles
means_incdec['IncDecile'] = means_incdec['IncDecile'].round().astype('int')
means_expdec['ExpDecile'] = means_expdec['ExpDecile'].round().astype('int')
means_expdec_int['ExpDecile'] = means_expdec_int['ExpDecile'].round().astype('int')
hhmeans_incdec['IncDecile'] = hhmeans_incdec['IncDecile'].round().astype('int')
hhmeans_expdec['ExpDecile'] = hhmeans_expdec['ExpDecile'].round().astype('int')

# ----------------------------------------------------------------------------------------
# Compare GWP intensive households with the averages of their respective deciles
# ----------------------------------------------------------------------------------------
idx_dict = {'1high': ID_poor_intensive5, '10high': ID_rich_intensive5,
            '10maxgwp': ID_max10_gwp, '10maxint': ID_max10_int,
            '1maxgwp': ID_max1_gwp, '1maxint': ID_max1_int,
            '1rich': ID_poor_rich5, '10rich': ID_rich_rich5}
(means_expextreme,
 stats_expextreme,
 hhmeans_expextreme,
 means_expextreme_int,
 dump1,dump2,dump3) = cats4plotting(stats_index=[1, 10,
                                                 '1high', '10high',
                                                 '10maxgwp', '10maxint',
                                                 '1maxgwp', '1maxint',
                                                 '1rich', '10rich'],
                                    xrange=[0, 9],
                                    xlabel='ExpDecile',
                                    index_dict=idx_dict)
# Look at that crazy houshold spending so much on gasoline:
habe_lca.loc[ID_max10_gwp, ['gwp_bike', 'gwp621501', 'gwp621502']]
habe_lca.loc[ID_max10_int, ['gwp_bike', 'gwp621501', 'gwp621502']]
habe_lca.loc[ID_max1_gwp, ['gwp_bike', 'gwp621501', 'gwp621502']]
habe_lca.loc[ID_max1_int, ['gwp_bike', 'gwp621501', 'gwp621502']]

# Fix labels and entries
means_expextreme['ExpDecile']
means_extreme = means_expextreme.drop('IncDecile', axis=1)
hhmeans_extreme = hhmeans_expextreme.drop('IncDecile', axis=1)
means_extreme.index = ['1', '10',
                       '1 high GWP', '10 high GWP',
                       '10 max GWP', '10 max Int',
                       '1 max GWP', '1 max Int',
                       '1 rich', '10 rich']
hhmeans_extreme.index = ['1', '10',
                         '1 high GWP', '10 high GWP',
                         '10 max GWP', '10 max Int',
                         '1 max GWP', '1 max Int',
                         '1 rich', '10 rich']
means_extreme['ExpDecile'] = means_extreme['ExpDecile'].round().astype('int')
hhmeans_extreme['ExpDecile'] = hhmeans_extreme['ExpDecile'].round().astype('int')
means_extreme

# ----------------------------------------------------------------------------------------
# Compare extremes with averages in the 10th decile
# ----------------------------------------------------------------------------------------
idx_dict = {'10high': ID_rich_intensive5,
            '10max': ID_max10_gwp,
            '10rich': ID_rich_rich5,
            '10sotomo_rich': ID_sotomo_rich}
(means_sotomorich,
 stats_sotomorich,
 hhmeans_sotomorich,
 means_sotomorich_int,
 dump1,dump2,dump3) = cats4plotting(stats_index=[10,
                                                 '10high',
                                                 '10max',
                                                 '10rich',
                                                 '10sotomo_rich'],
                                    xrange=[9],
                                    xlabel='ExpDecile',
                                    index_dict=idx_dict)
# Fix labels and entries
means_sotomorich = means_sotomorich.drop('IncDecile', axis=1)
hhmeans_sotomorich = hhmeans_sotomorich.drop('IncDecile', axis=1)
means_sotomorich.index = ['10',
                          '10 high GWP', '10 max GWP',
                          '10 rich',
                          '10 sotomo rich']
hhmeans_sotomorich.index = ['10',
                            '10 high GWP', '10 max GWP',
                            '10 rich',
                            '10 sotomo rich']
means_sotomorich['ExpDecile'] = means_sotomorich['ExpDecile'].round().astype('int')
hhmeans_sotomorich['ExpDecile'] = hhmeans_sotomorich['ExpDecile'].round().astype('int')
means_sotomorich

# ----------------------------------------------------------------------------------------
# Compare GWP per categories across urbanization and renting
# ----------------------------------------------------------------------------------------

(means_urban,
 stats_urban,
 hhmeans_urban,
 means_urban_int,
 dump1,dump2,dump3) = cats4plotting(stats_index=['Urban', 'Periurban', 'Rural'],
                                    xrange=['Urban', 'Periurban', 'Rural'],
                                    xlabel='Urbanization')
means_urban
stats_urban

(means_renter,
 stats_renter,
 hhmeans_renter,
 means_renter_int,
 dump1,dump2,dump3) = cats4plotting(stats_index=['Renter', 'Owner'],
                                    xrange=['Renter', 'Owner'],
                                    xlabel='Renting')
means_renter
stats_renter

(means_hhtype,
 stats_hhtype,
 hhmeans_hhtype,
 means_hhtype_int,
 dump1,dump2,dump3) = cats4plotting(stats_index=['Single', 'Elderly single',
                                                 'Couple', 'Elderly couple',
                                                 'Single parent',
                                                 'Parent couple',
                                                 'Others'],
                                    xrange=['Single', 'Elderly single', 'Couple',
                                            'Elderly couple', 'Single parent',
                                            'Parent couple', 'Others'],
                                    xlabel='Household type')
means_hhtype
stats_hhtype

# ----------------------------------------------------------------------------------------
# Aggregate the consumption categories to a reasonable number of commodities
# ----------------------------------------------------------------------------------------

aggregation = pd.read_excel(agg_file,
                            sheet_name='overview',
                            index_col=0)
aggregation_mobility = pd.read_excel(agg_file,
                                     sheet_name='mobility',
                                     index_col=0)
aggregation_residential = pd.read_excel(agg_file,
                                        sheet_name='heating',
                                        index_col=0)


def aggregate_categories(means, aggregation, displayname, index):
    means_agg = pd.DataFrame()
    means_agg[displayname] = index
    means_agg.index = means.index
    for a in aggregation.index:
        means_agg[a] = [0]*len(index)
        for c in aggregation.columns:
            if aggregation.loc[a, c] is True:
                # print(a, c)
                means_agg[a] = means_agg[a] + means[c]
    return means_agg

def aggregate_categories_high(means, aggregation, displayname, index):
    means_agg = pd.DataFrame()
    means_agg[displayname] = index
    means_agg.index = means.index
    for a in aggregation.index:
        means_agg[a] = [0]*len(index)
        for c in aggregation.columns:
            if aggregation.loc[a, c] is True:
                if (c == 'gwp622300'):
                    # gwp622300 is air transport
                    means_agg[a] = means_agg[a] + 2*means[c]
                elif (c == 'gwp665000'):
                    # gwp665000 is package holidays
                    means_agg[a] = means_agg[a] + 2*means[c]
                else:
                    means_agg[a] = means_agg[a] + means[c]
    return means_agg

incmeans_agg = aggregate_categories(means_incdec, aggregation,
                                    displayname='Income decile group',
                                    index=means_incdec['IncDecile'])
expmeans_agg_ch = aggregate_categories(means_expdec_ch, aggregation,
                                       displayname='Country',
                                       index=['CH'])
expmeans_agg = aggregate_categories(means_expdec, aggregation,
                                    displayname='Decile group of lifetime income',
                                    index=means_expdec['ExpDecile'])
expmeans_agg_high =\
    aggregate_categories_high(means_expdec, aggregation,
                              displayname='Decile group of lifetime income',
                              index=means_expdec['ExpDecile'])
expmeans_agg_ch
expmeans_agg
extremes_agg = aggregate_categories(means_extreme, aggregation,
                                    displayname='Decile group of lifetime income',
                                    index=means_extreme.index)
sotomo_agg = aggregate_categories(means_sotomorich, aggregation,
                                  displayname='Decile group of lifetime income',
                                  index=means_sotomorich.index)
rentmeans_agg = aggregate_categories(means_renter, aggregation,
                                     displayname='Home ownership',
                                     index=means_renter.index)
urbmeans_agg = aggregate_categories(means_urban, aggregation,
                                    displayname='Urbanization',
                                    index=means_urban.index)
typemeans_agg = aggregate_categories(means_hhtype, aggregation,
                                     displayname='Household type',
                                     index=means_hhtype.index)
typehhmeans_agg = aggregate_categories(hhmeans_hhtype, aggregation,
                                       displayname='Household type',
                                       index=hhmeans_hhtype.index)

incmeans_agg
expmeans_agg
extremes_agg
urbmeans_agg
rentmeans_agg
typemeans_agg
typehhmeans_agg
high_agg = extremes_agg.drop('10 max GWP')
high_agg = high_agg.reindex(['1', '1 rich', '1 high GWP', '10', '10 rich', '10 high GWP'])
high_agg
high_agg.index = ['1', '1: richest',
                  '1: highest GWP',
                  '10', '10: richest',
                  '10: highest GWP']
high_agg['Decile group of lifetime income'] = high_agg.index
sotomo_agg = sotomo_agg.drop('10 max GWP')
sotomo_agg = sotomo_agg.reindex(['10', '10 rich', '10 high GWP', '10 sotomo rich'])
sotomo_agg.index = ['10', '10: richest',
                    '10: highest GWP',
                    '10: richest (Sotomo)']
sotomo_agg['Decile group of lifetime income'] = sotomo_agg.index
# Repeat for mobility aggregation
expmeans_agg_mob = aggregate_categories(means_expdec, aggregation_mobility,
                                        displayname='Decile group of lifetime income',
                                        index=means_expdec['ExpDecile'])
expmeans_agg_mob_high\
    = aggregate_categories_high(means_expdec, aggregation_mobility,
                                displayname='Decile group of lifetime income',
                                index=means_expdec['ExpDecile'])
rentmeans_agg_mob = aggregate_categories(means_renter, aggregation_mobility,
                                         displayname='Home ownership',
                                         index=means_renter.index)
urbmeans_agg_mob = aggregate_categories(means_urban, aggregation_mobility,
                                        displayname='Urbanization',
                                        index=means_urban.index)
typemeans_agg_mob = aggregate_categories(means_hhtype, aggregation_mobility,
                                         displayname='Household type',
                                         index=means_hhtype.index)
typehhmeans_agg_mob = aggregate_categories(hhmeans_hhtype, aggregation_mobility,
                                           displayname='Household type',
                                           index=means_hhtype.index)
# Repeat for residential_energy aggregation
expmeans_agg_res = aggregate_categories(means_expdec, aggregation_residential,
                                        displayname='Decile group of lifetime income',
                                        index=means_expdec['ExpDecile'])
rentmeans_agg_res = aggregate_categories(means_renter, aggregation_residential,
                                         displayname='Home ownership',
                                         index=means_renter.index)
urbmeans_agg_res = aggregate_categories(means_urban, aggregation_residential,
                                        displayname='Urbanization',
                                        index=means_urban.index)
typemeans_agg_res = aggregate_categories(means_hhtype, aggregation_residential,
                                         displayname='Household type',
                                         index=means_hhtype.index)
typehhmeans_agg_res = aggregate_categories(hhmeans_hhtype, aggregation_residential,
                                           displayname='Household type',
                                           index=means_hhtype.index)
# Repeat for those gwp-intensity numbers
expmeans_intagg_res = aggregate_categories(means_expdec_int, aggregation_residential,
                                           displayname='Decile group of lifetime income',
                                           index=means_expdec_int['ExpDecile'])
expmeans_intagg_mob = aggregate_categories(means_expdec_int, aggregation_mobility,
                                           displayname='Decile group of lifetime income',
                                           index=means_expdec_int['ExpDecile'])
expmeans_intagg_mob_high =\
    aggregate_categories_high(means_expdec_int, aggregation_mobility,
                              displayname='Decile group of lifetime income',
                              index=means_expdec_int['ExpDecile'])

type(expmeans_agg_mob)
with pd.ExcelWriter("beobachter.xlsx") as writer:
    expmeans_agg_mob.to_excel(writer,sheet_name='Abb. 8a')
    expmeans_intagg_mob.to_excel(writer,sheet_name='Abb. 8b')
    expmeans_agg_res.to_excel(writer,sheet_name='Abb. 9a')
    expmeans_intagg_res.to_excel(writer,sheet_name='Abb. 9b')




# logic checks (findings from trial and error):
# 'a is True' only accepts 'True'
# 'a == True' accepts 'True' and 1
# 'a' accepts all non-zero numeric values, non-empty strings ,
#     float('nan') (!), non-empty lists, ...

# Normal use of plt library:
#
# Normal use of fig,ax = plt.figure() or, shorter, plt.figure() returns objects
# fig,ax that can be worked on using things like plt.legend(), plt.ylabel() etc.
#
# These always work on last used fig/ax ('current'; created, e.g., by
# plt.bar(means_incdec['IncDecile'], means_incdec['gwp571204'])) or can be explicitly
# called on specific objects by writing ax.legend(), ax.ylabel() etc.
#
# Pandas .plot:
#
# - pd.plot returns ax (but no fig, afaict)
# - Seems to call plt.figure and all arguments normally given to figure should be
#   given to pd.plot.
# - Takes numerous arguments:
#   https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.plot.html
# - Takes ax as an optional argument! Can be integrated in previously created
#   fig,ax arrangement (subplots!)

# Colors (dark to light)
# 0-3: blue
# 4-7: green
# 8-11: yellow
# 12-15: reddish
# 16-19: pinkish

mycolororder = (
    plt.cm.tab20b.colors[0],
    plt.cm.tab20b.colors[1],
    plt.cm.tab20b.colors[4],
    plt.cm.tab20b.colors[8],
    plt.cm.tab20b.colors[9],
    plt.cm.tab20b.colors[10],
    plt.cm.tab20b.colors[11],
    plt.cm.tab20b.colors[12],
    plt.cm.tab20b.colors[13],
    plt.cm.tab20b.colors[16],
    plt.cm.tab20b.colors[5],
    plt.cm.tab20b.colors[6],
    plt.cm.tab20b.colors[7],
    plt.cm.tab20b.colors[17],
    plt.cm.tab20b.colors[18],
    plt.cm.tab20b.colors[2],
    plt.cm.tab20b.colors[3],
    plt.cm.tab20b.colors[14],
    plt.cm.tab20b.colors[19],
    plt.cm.tab20b.colors[15]
)


def plot_categories(plotdata, filename, xvar='Decile group of lifetime income',
                    # figtitle='GWP per capita by consumption category',
                    figtitle=None,
                    y_label='Per capita GWP [t CO$_{2}$-eq]', y_max=20,
                    ncols=1,
                    hscale=1,
                    colorpalette=mycolororder, rotate=None,
                    placelegend=True,
                    halfhatch=False):
    sns.set(font_scale=0.8)
    sns.set(style='darkgrid')
    if plotdata.columns[0] != xvar:
        return print('Warning: xvar not the first entry of plotdata.columns')
    fig, ax = plt.subplots(tight_layout=True)
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.75, box.height])
    plt.rcParams['axes.prop_cycle'] = plt.cycler('color', colorpalette)
    plotdata.plot(x=xvar, kind='bar', stacked=True,
                  title=figtitle, figsize=(12.5*cm, 9.3*cm*hscale),
                  ylabel=y_label, ax=ax, linewidth=0.1, edgecolor='black',
                  rot=rotate)
    if halfhatch:
        bottom_air = (
            plotdata[plotdata.columns[1]]
            + plotdata['Restaurants']
            + plotdata['Clothing and Footwear']
            + plotdata['Utilities']
            + plotdata['Electricity']
            + plotdata['Gas and other heating fuels']
            + plotdata['Central and district heating']
            + plotdata['Maintenance of building']
            # avoid figuring out how to encode '\n' in the column name
            # by using the column index:
            + plotdata[plotdata.columns[9]]
            + plotdata[plotdata.columns[10]]
            + plotdata['Private transport']
        )
        bottom_package = (
            plotdata[plotdata.columns[1]]
            + plotdata['Restaurants']
            + plotdata['Clothing and Footwear']
            + plotdata['Utilities']
            + plotdata['Electricity']
            + plotdata['Gas and other heating fuels']
            + plotdata['Central and district heating']
            + plotdata['Maintenance of building']
            + plotdata[plotdata.columns[9]]
            + plotdata[plotdata.columns[10]]
            + plotdata['Private transport']
            # Air transport
            + plotdata[plotdata.columns[12]]
            # Other transport
            + plotdata[plotdata.columns[13]]
            # Postal services
            + plotdata[plotdata.columns[14]]
            # Electronic eq.
            + plotdata[plotdata.columns[15]]
            # Sports etc.
            + plotdata[plotdata.columns[16]]
        )
        ax.bar(plotdata[xvar]-1,
               plotdata['Transport services - Air']/2,
               bottom=bottom_air,
               hatch='xxxxxxx',
               edgecolor='black',
               label='_nolegend_',
               width=0.5,
               lw=0.1,
               color=mycolororder[11]
               )
        ax.bar(plotdata[xvar]-1,
               plotdata['Package holidays']/2,
               bottom=bottom_package,
               hatch='xxxxxxx',
               edgecolor='black',
               label='_nolegend_',
               width=0.5,
               lw=0.1,
               color=mycolororder[16]
               )
    # Get columns of plotdata but ignore column 0 ('xvar', hopefully...)
    ord_labels = list(plotdata.columns[1:len(plotdata.columns)])
    # Reverse order of all column labels (column labels = legend labels)
    # (I used the following to change the order of the bars in the legend
    # https://stackoverflow.com/questions/66531778/change-bar-order-and-legend-order-in-\
    # plot-matplotlib-pandas)
    reordered_labels = list(ord_labels[::-1])
    # When reading from Excel, '\n' was interpreted as '\\n' -> change back
    for ll in range(0, len(reordered_labels)):
        reordered_labels[ll] = reordered_labels[ll].replace('\\n', '\n')

    # Also get handles of all legend entries and create dictionary label -> handle
    handles, labels = ax.get_legend_handles_labels()
    # When reading from Excel, '\n' was interpreted as '\\n' -> change back
    for ll in range(0, len(labels)):
        labels[ll] = labels[ll].replace('\\n', '\n')

    dict_legends = dict(zip(labels, handles))
    # Use dictionary to order handles according to reordered_labels
    handles_order = [dict_legends[lo] for lo in reordered_labels]
    # Apply order of labels and handles to legend
    if placelegend:
        ax.legend(handles_order, reordered_labels, bbox_to_anchor=(1, 1),
                  fontsize='7',
                  ncol=ncols)
    else:
        ax.legend(handles_order, reordered_labels,
                  fontsize='7',
                  ncol=ncols)
    # plt.legend(ncol=ncols)
    ax.set_ylim([0, y_max])
    fs = 9
    ax.set_xlabel(xvar, fontsize=fs)
    ax.set_ylabel(y_label, fontsize=fs)
    plt.yticks(fontsize=fs)
    plt.xticks(fontsize=fs)
    plt.title(figtitle, fontsize=1.1*fs)
    # plt.show()
    epsname = filename+'.eps'
    pdfname = filename+'.pdf'
    pngname = filename+'.png'
    fig.savefig(os.path.join(fig_dir, epsname), format='eps', dpi=1200)
    fig.savefig(os.path.join(fig_dir, pdfname), format='pdf', dpi=1200)
    fig.savefig(os.path.join(fig_dir, pngname), format='png', dpi=1200)
    plt.close()


plot_categories(plotdata=incmeans_agg,
                filename='Fig_inc1',
                xvar='Income decile group', rotate=0)
plot_categories(plotdata=expmeans_agg,
                filename='gwp_cat',
                y_max=21,
                xvar='Decile group of lifetime income', rotate=0)
plot_categories(plotdata=expmeans_agg_high,
                filename='gwp_high_cat',
                y_max=21,
                xvar='Decile group of lifetime income', rotate=0, halfhatch=True)
plot_categories(plotdata=expmeans_agg_ch,
                filename='gwp_cat_ch',
                xvar='Country', rotate=0)
plot_categories(plotdata=high_agg,
                filename='gwp_cat_high',
                xvar='Decile group of lifetime income',
                y_max=35)
plot_categories(plotdata=sotomo_agg,
                filename='gwp_cat_high_sotomo',
                xvar='Decile group of lifetime income',
                y_max=35)
plot_categories(plotdata=extremes_agg, filename='gwp_cat_extremes',
                xvar='Decile group of lifetime income',
                y_max=30)
plot_categories(plotdata=urbmeans_agg, filename='gwp_cat_urbanization',
                xvar='Urbanization',
                y_max=20)
plot_categories(plotdata=typemeans_agg, filename='gwp_cat_hhtype',
                xvar='Household type',
                y_max=20)
plot_categories(plotdata=typehhmeans_agg, filename='gwp_cat_hhtype_hhmeans',
                xvar='Household type',
                y_label='GWP per household [t CO$_{2}$-eq]',
                y_max=35)
plot_categories(plotdata=rentmeans_agg, filename='gwp_cat_homeownership',
                xvar='Home ownership',
                y_max=20)

# Short versions for mobility and residential energy
# ----------------------------------------------------------------------------------------
# Colors (dark to light)
# 0-3: blue
# 4-7: green
# 8-11: yellow
# 12-15: reddish
# 16-19: pinkish

mobility_colors = (
    # Gasoline and diesel (red)
    plt.cm.tab20b.colors[13],
    plt.cm.tab20b.colors[14],
    # Bikes (green)
    plt.cm.tab20b.colors[4],
    # Flying (pink)
    plt.cm.tab20b.colors[17],
    # Taxi (red)
    plt.cm.tab20b.colors[15],
    # Schiffahrten (blau)
    plt.cm.tab20b.colors[0],
    # Weitere (blau)
    plt.cm.tab20b.colors[1],
    # Bus, Zug, Tram (grün)
    plt.cm.tab20b.colors[5],
    plt.cm.tab20b.colors[6],
    plt.cm.tab20b.colors[7],
    # package holidays (pink)
    plt.cm.tab20b.colors[18]
)

plot_categories(plotdata=expmeans_agg_mob,
                filename='gwp_cat_mob',
                xvar='Decile group of lifetime income', rotate=0,
                y_max=7.5,
                ncols=2,
                hscale=0.71,
                colorpalette=mobility_colors,
                placelegend=False)
plot_categories(plotdata=expmeans_agg_mob_high,
                filename='gwp_high_cat_mob',
                xvar='Decile group of lifetime income', rotate=0,
                y_max=7.5,
                ncols=2,
                hscale=0.71,
                colorpalette=mobility_colors,
                placelegend=False)
plot_categories(plotdata=expmeans_intagg_mob,
                filename='gwp_intcat_mob',
                xvar='Decile group of lifetime income', rotate=0,
                y_label='GWP intensity [kg CO$_{2}$-eq per CHF]',
                # hscale=0.71,
                hscale=0.645,   # yields 6 cm height: hscale*9.3
                y_max=0.21,
                ncols=3,
                colorpalette=mobility_colors)
plot_categories(plotdata=expmeans_intagg_mob_high,
                filename='gwp_high_intcat_mob',
                xvar='Decile group of lifetime income', rotate=0,
                y_label='GWP intensity [kg CO$_{2}$-eq per CHF]',
                # hscale=0.71,
                hscale=0.645,   # yields 6 cm height: hscale*9.3
                y_max=0.21,
                ncols=3,
                colorpalette=mobility_colors)
plot_categories(plotdata=rentmeans_agg_mob,
                filename='gwp_cat_rent_mob',
                xvar='Home ownership',
                y_max=6,
                colorpalette=mobility_colors)
plot_categories(plotdata=urbmeans_agg_mob,
                filename='gwp_cat_urb_mob',
                xvar='Urbanization',
                y_max=6,
                colorpalette=mobility_colors)
plot_categories(plotdata=typemeans_agg_mob,
                filename='gwp_cat_hhtype_mob',
                xvar='Household type',
                y_max=6,
                colorpalette=mobility_colors)
plot_categories(plotdata=typehhmeans_agg_mob,
                filename='gwp_cat_hhtype_hhmeans_mob',
                xvar='Household type',
                figtitle='GWP per household by consumption category',
                y_max=10,
                colorpalette=mobility_colors)

# Colors (dark to light)
# 0-3: blue
# 4-7: green
# 8-11: yellow
# 12-15: reddish
# 16-19: pinkish

residential_colors = (
    # Gas and other fuels (red)
    plt.cm.tab20b.colors[13],
    # District heating (blue)
    plt.cm.tab20b.colors[1]
)

plot_categories(plotdata=expmeans_agg_res,
                filename='gwp_cat_res',
                xvar='Decile group of lifetime income', rotate=0,
                y_max=4,
                hscale=0.71,
                colorpalette=residential_colors,
                placelegend=False)
plot_categories(plotdata=expmeans_intagg_res,
                filename='gwp_intcat_res',
                xvar='Decile group of lifetime income', rotate=0,
                y_label='GWP intensity [kg CO$_{2}$-eq per CHF]',
                y_max=0.2,
                hscale=0.71,
                colorpalette=residential_colors)
plot_categories(plotdata=rentmeans_agg_res,
                filename='gwp_cat_rent_res',
                xvar='Home ownership',
                y_max=5.0,
                colorpalette=residential_colors)
plot_categories(plotdata=urbmeans_agg_res,
                filename='gwp_cat_urb_res',
                xvar='Urbanization',
                y_max=5.0,
                colorpalette=residential_colors)
plot_categories(plotdata=typemeans_agg_res,
                filename='gwp_cat_hhtype_res',
                xvar='Household type',
                y_max=5.0,
                colorpalette=residential_colors)
plot_categories(plotdata=typehhmeans_agg_res,
                filename='gwp_cat_hhtype_hhmeans_res',
                xvar='Household type',
                figtitle='GWP per household by consumption category',
                y_max=7,
                colorpalette=residential_colors)
