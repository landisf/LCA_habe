#! Final demand per household in right units

# In this note book we will combine the different expenditure data
# to create one file with the final demand per household per
# consumption catergory including the ones with
# precalculated unit conversions (i.e. electricity expenditure to kwh).
# Replicate Andi's hh_prepared_imputed file

import pandas as pd
# import numpy as np
import os
# import itertools

# define paths
repo_root = os.path.abspath(os.getcwd())
filedir = os.path.join(repo_root,
                       'python')
mzmv_dir = os.path.join(repo_root, 'data-MZMV')
habe_dir = os.path.join(repo_root, 'intermediate_files')
out_dir = os.path.join(repo_root, 'intermediate_files')

# define filenames (including paths)
imputed_habe_file = os.path.join(habe_dir,
                                 'habe20152017_hh_prepared_imputed.csv')
properties_file = os.path.join(habe_dir,
                               'hh_properties.csv')
MZMV_file = os.path.join(mzmv_dir, 'read_MZMV.xlsx')
out_file = os.path.join(out_dir, 'habe20152017_imputed_withMZkm.csv')
# Read stuff
habe = pd.read_csv(imputed_habe_file,
                   sep=',',
                   header=0,
                   index_col=0)
properties = pd.read_csv(properties_file,
                         sep=',',
                         header=0,
                         index_col=0)
MZMV_by_region = pd.read_excel(MZMV_file,
                               sheet_name='By region',
                               index_col=0)
MZMV_by_language = pd.read_excel(MZMV_file,
                                 sheet_name='By language',
                                 index_col=0)
MZMV_by_hhtype = pd.read_excel(MZMV_file,
                               sheet_name='By hhtype',
                               index_col=0)
MZMV_by_income = pd.read_excel(MZMV_file,
                               sheet_name='By income',
                               index_col=0)


# a_hot_mess = pd.read_excel(categories_file,
#                            sheet_name='Overview & LCA-Modeling',
#                            header=2,
#                            index_col=1)

habe_local = pd.concat([habe, properties], axis=1)

habe_local['bike_spending'] = habe_local['a6213']*properties['weight']
habe_local['bike_owned'] = habe_local['cg_nobicycles']*properties['weight']
habe_local['pass_spending'] = habe_local['a6225']*properties['weight']
habe_local['bus_spending'] = habe_local['a622201']*properties['weight']
habe_local['train_spending'] = habe_local['a622101']*properties['weight']
habe_local['tram_spending'] = habe_local['a622102']*properties['weight']
properties['population'] = properties['size']*properties['weight']

reg_labels = ['Genferseeregion', 'Espace Mittelland', 'Nordwestschweiz', 'Zuerich',
              'Ostschweiz', 'Zentralschweiz', 'Tessin']
# lang_labels = ['Deutsch', 'Franzoesisch', 'Italienisch', 'Rätoromanisch']
# Rätoromanisch is bundled with Deutsch in HABE
lang_labels = ['Deutsch', 'Franzoesisch', 'Italienisch']
inc_labels = ['0-4000', '4001-8000', '8001-12000', '12001-']
type_labels = ['Einzelperson', 'Paar', 'Paarerziehend', 'Alleinerziehend', 'Andere']
properties['region_'] = pd.cut(properties.region, bins=7, labels=reg_labels)
properties['income_'] = pd.cut(properties.income,
                               bins=[0, 4000, 8000, 12000, 1e12],
                               labels=inc_labels)
properties['language_'] = pd.cut(properties.language, bins=3, labels=lang_labels)
properties['hhtype_'] = pd.cut(properties.hhtype,
                               bins=[0, 150, 250, 350, 450, 1000],
                               labels=type_labels)

travel = pd.concat([habe_local['bike_spending'],
                    habe_local['bike_owned'],
                    habe_local['pass_spending'],
                    habe_local['bus_spending'],
                    habe_local['train_spending'],
                    habe_local['tram_spending'],
                    properties['population'],
                    properties['region_'],
                    properties['language_'],
                    properties['income_'],
                    properties['hhtype_'],
                    ], axis=1)
travel
travel_by_region = travel[['bike_spending', 'bike_owned',
                           'pass_spending', 'bus_spending',
                           'train_spending', 'tram_spending',
                           'population', 'region_']].groupby('region_')
travel_by_language = travel[['bike_spending', 'bike_owned',
                             'pass_spending', 'bus_spending',
                             'train_spending', 'tram_spending',
                             'population', 'language_']].groupby('language_')
travel_by_hhtype = travel[['bike_spending', 'bike_owned',
                           'pass_spending', 'bus_spending',
                           'train_spending', 'tram_spending',
                           'population', 'hhtype_']].groupby('hhtype_')
travel_by_income = travel[['bike_spending', 'bike_owned',
                           'pass_spending', 'bus_spending',
                           'train_spending', 'tram_spending',
                           'population', 'income_']].groupby('income_')
avgs_by_region = travel_by_region.sum().div(travel_by_region['population'].sum(), axis=0)\
                                       .iloc[:, 0:6]
avgs_by_language = travel_by_language.sum().div(travel_by_language['population'].sum(),
                                                axis=0).iloc[:, 0:6]
avgs_by_hhtype = travel_by_hhtype.sum().div(travel_by_hhtype['population'].sum(), axis=0)\
                                       .iloc[:, 0:6]
avgs_by_income = travel_by_income.sum().div(travel_by_income['population'].sum(), axis=0)\
                                       .iloc[:, 0:6]

# I want to analyze the correlation between spending and km.
# Low correlation means high explanatory power of the analyzed dimension (?)
# Do this for
# - bikes
# - overall public transport
# - bus
# - train
# - tram


def compute_correlations(avgs_habe, km_mzmv):
    summary = pd.DataFrame()
    summary["bike_chf"] = avgs_habe["bike_spending"]
    summary["bike_no"] = avgs_habe["bike_owned"]
    summary["bike_km"] = km_mzmv.transpose()["Bikes"]
    summary["PubTran_chf"] = (avgs_habe["pass_spending"]
                              + avgs_habe["bus_spending"]
                              + avgs_habe["train_spending"]
                              + avgs_habe["tram_spending"])
    summary["PubTran_km"] = (km_mzmv.transpose()["Bus"]
                             + km_mzmv.transpose()["Tram"]
                             + km_mzmv.transpose()["Train"])
    summary["Bus_chf"] = (avgs_habe["bus_spending"])
    summary["Bus_km"] = (km_mzmv.transpose()["Bus"])
    summary["Tram_chf"] = (avgs_habe["tram_spending"])
    summary["Tram_km"] = (km_mzmv.transpose()["Tram"])
    summary["Train_chf"] = (avgs_habe["train_spending"])
    summary["Train_km"] = (km_mzmv.transpose()["Train"])

    print(summary)
    corr_local = summary.corr()
    print(corr_local)
    correlations = [corr_local["bike_chf"]["bike_km"],
                    corr_local["bike_no"]["bike_km"],
                    corr_local["PubTran_chf"]["PubTran_km"],
                    corr_local["Bus_chf"]["Bus_km"],
                    corr_local["Tram_chf"]["Tram_km"],
                    corr_local["Train_chf"]["Train_km"],
                    ]

    return correlations


correlations = pd.DataFrame()
correlations.index = ['bike_chf', 'bike_no', 'PubTran', 'Bus', 'Tram', 'Train']
correlations["region"] = compute_correlations(avgs_by_region, MZMV_by_region)
correlations["language"] = compute_correlations(avgs_by_language, MZMV_by_language)
correlations["hhtype"] = compute_correlations(avgs_by_hhtype, MZMV_by_hhtype)
correlations["income"] = compute_correlations(avgs_by_income, MZMV_by_income)

correlations

# ----------------------------------------------------------------------------------------
# Conclusion:
# Correlation between spending and person kilometers is worst across household types.
# I take that to mean that spending is least good at explaining differences hhtypes.
# For infering person kilometers from HABE and the Microcensus, the best I can do is
# to use person kilometers PER HH-TYPE from the Microcensus and distribute them across
# households within this group according to spending (# of bikes in the case of biking).
#
# This makes sence to the extent that hh-type explains best the differences in access to
# family disounts, etc.
#
# Since the differences across hhtype may also correlate to age, an additional in-depth
# analysis using the Microcensus base data may improve upon this basic screening based
# on aggregate summary statistics on the Microcensus side.
# ----------------------------------------------------------------------------------------

# travel['bike_owned']: weighted observations
# travel_by_hhtype['shr_inbike']: weighted observations/sum(weighted observations)
travel['shr_inbike'] = (travel['bike_owned']
                        / travel_by_hhtype['bike_owned'].transform('sum'))
travel['shr_inpass'] = (travel['pass_spending']
                        / travel_by_hhtype['pass_spending'].transform('sum'))
travel['shr_inbus'] = (travel['bus_spending']
                       / travel_by_hhtype['bus_spending'].transform('sum'))
travel['shr_intram'] = (travel['tram_spending']
                        / travel_by_hhtype['tram_spending'].transform('sum'))
travel['shr_intrain'] = (travel['train_spending']
                         / travel_by_hhtype['train_spending'].transform('sum'))
travel_by_hhtype = travel.groupby('hhtype_')
# Check: this should be all ones
travel_by_hhtype['shr_inbike'].transform('sum')
travel_by_hhtype['shr_inpass'].transform('sum')
travel_by_hhtype['shr_inbus'].transform('sum')
travel_by_hhtype['shr_intram'].transform('sum')
travel_by_hhtype['shr_intrain'].transform('sum')

shr_pass = (travel_by_hhtype['pass_spending'].transform('sum')
            / (travel_by_hhtype['pass_spending'].transform('sum')
               + travel_by_hhtype['bus_spending'].transform('sum')
               + travel_by_hhtype['tram_spending'].transform('sum')
               + travel_by_hhtype['train_spending'].transform('sum'))
            )
# Note that the share of travel pass spending in overall public transit spending is high.
print(shr_pass)
# Verify that on the national level, travel pass spending has a ~72 percent (!) share in
# overall spending on public transport.
shr_pass_ch = (travel['pass_spending'].sum()
               / (travel['pass_spending'].sum()
                  + travel['bus_spending'].sum()
                  + travel['train_spending'].sum()
                  + travel['tram_spending'].sum())
               )
print(shr_pass_ch)

# Create person km numbers for all households
# ----------------------------------------------------------------------------------------

pkm_hhtype = pd.DataFrame()
pkm_hhtype.index = travel.index
# Columns of HHs with Microcensus's per capita kilometers for appropriate hhtype
pkm_hhtype['bikes_pc'] = MZMV_by_hhtype.transpose()['Bikes'][travel['hhtype_']]\
                                       .set_axis(travel.index)
pkm_hhtype['bus_pc'] = MZMV_by_hhtype.transpose()['Bus'][travel['hhtype_']]\
                                     .set_axis(travel.index)
pkm_hhtype['tram_pc'] = MZMV_by_hhtype.transpose()['Tram'][travel['hhtype_']]\
                                      .set_axis(travel.index)
pkm_hhtype['train_pc'] = MZMV_by_hhtype.transpose()['Train'][travel['hhtype_']]\
                                       .set_axis(travel.index)
# Aggregate km for hhtypes
pkm_hhtype['bikes'] = (pkm_hhtype['bikes_pc']
                       * travel_by_hhtype['population'].transform('sum'))
pkm_hhtype['bus'] = (pkm_hhtype['bus_pc']
                     * travel_by_hhtype['population'].transform('sum'))
pkm_hhtype['tram'] = (pkm_hhtype['tram_pc']
                      * travel_by_hhtype['population'].transform('sum'))
pkm_hhtype['train'] = (pkm_hhtype['train_pc']
                       * travel_by_hhtype['population'].transform('sum'))

pkm_hhtype
#                            bike             bus             tram          train
# einzelpers (360102)        1.074534e+06     1.475357e+06    7.156466e+05  1.099428e+07
# paar (360101)              2.195374e+06     1.733263e+06    8.121856e+05  1.586971e+07
# alleinerziehend (431730)   2.964641e+06     5.422342e+06    1.697867e+06  2.986990e+07
# paarerziehend (431738)     3.987613e+05     5.493169e+05    1.465660e+05  2.835723e+06
# andere (431723)            4.499541e+05     5.699514e+05    2.775737e+05  4.949555e+06

travel_by_hhtype['population'].sum()
# Einzelperson       1.387265e+06
# Paar               2.372595e+06
# Paarerziehend      4.378645e+05
# Alleinerziehend    3.375937e+06
# Andere             4.858424e+05

# CH population according to HABE:
travel_by_hhtype['population'].sum().sum()
# 8.059504427738037e+06

# I checked: travel_by_hhtype['population'].sum() multiplied with entries of
# sheet 'By hhtype' in 'read_MZMV.xlsx' agrees with entries of pkm_hhtype

# caveat: shr_pass is lower bound for pkm shares, since it's a share in spending and
#         passes (travel cards) are only purchased if they give more pkm/chf than
#         direct ticket purchases.
# shr_pass is indexed by observations and contains values specific to hh_type.
# pkm_<mode> is best guess for pkm per household observation:
# - shr_pass (for given hh_type) gives share of transport purchased through travel cards
# - travel['shr_inpass'] is the share of travel card spending from a given HH (obs*weight)
# - division by weight gives pkm per observation

pkm_bike = (travel['shr_inbike']*pkm_hhtype['bikes']
            / properties['weight'])
pkm_bus = ((travel['shr_inpass']*shr_pass + travel['shr_inbus']*(1-shr_pass))
           * pkm_hhtype['bus']
           / properties['weight'])
pkm_tram = ((travel['shr_inpass']*shr_pass + travel['shr_intram']*(1-shr_pass))
            * pkm_hhtype['tram']
            / properties['weight'])
pkm_train = ((travel['shr_inpass']*shr_pass + travel['shr_intrain']*(1-shr_pass))
             * pkm_hhtype['train']
             / properties['weight'])

# Look at my creation (daily kilometers) :)
pkm_bike
pkm_bus
pkm_tram
pkm_train

# Check that all kilometers are accunted for
# ----------------------------------------------------------------------------------------

check_km = pd.DataFrame()
check_km.index = ['hhtypes', 'households']

hhtypes = ['Einzelperson', 'Paar', 'Paarerziehend', 'Alleinerziehend', 'Andere']

check_km['bikes'] = [0, 0]
check_km['bus'] = [0, 0]
check_km['tram'] = [0, 0]
check_km['train'] = [0, 0]

for ht in hhtypes:
    check_km['bikes'] = (check_km['bikes']
                         + [(MZMV_by_hhtype[ht]['Bikes']
                             * travel_by_hhtype['population'].sum()[ht]),
                            0]
                         )
    check_km['bus'] = (check_km['bus']
                       + [(MZMV_by_hhtype[ht]['Bus']
                           * travel_by_hhtype['population'].sum()[ht]),
                          0]
                       )
    check_km['tram'] = (check_km['tram']
                        + [(MZMV_by_hhtype[ht]['Tram']
                            * travel_by_hhtype['population'].sum()[ht]),
                           0]
                        )
    check_km['train'] = (check_km['train']
                         + [(MZMV_by_hhtype[ht]['Train']
                             * travel_by_hhtype['population'].sum()[ht]),
                            0]
                         )

check_km['bikes'] = check_km['bikes'] + [0, (pkm_bike*properties['weight']).sum()]
check_km['bus'] = check_km['bus'] + [0, (pkm_bus*properties['weight']).sum()]
check_km['tram'] = check_km['tram'] + [0, (pkm_tram*properties['weight']).sum()]
check_km['train'] = check_km['train'] + [0, (pkm_train*properties['weight']).sum()]

# This looks good:
check_km

# Convert into monthly person kilometers and save to habe columns
habe["pkm_bike"] = pkm_bike*365/12
habe["pkm_bus"] = pkm_bus*365/12
habe["pkm_tram"] = pkm_tram*365/12
habe["pkm_train"] = pkm_train*365/12

habe.to_csv(out_file)
