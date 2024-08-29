#! Final demand per household in right units

# In this note book we will combine the different expenditure data
# to create one file with the final demand per household per
# consumption catergory including the ones with
# precalculated unit conversions (i.e. electricity expenditure to kwh).
# Replicate Andi's hh_prepared_imputed file

import pandas as pd
import numpy as np
import os
import itertools
import matplotlib.pyplot as plt

# define paths
repo_root = os.path.abspath(os.getcwd())
filedir = os.path.join(repo_root,
                       'python')
habe_2017_dir = os.path.join(repo_root,
                             'data-HABE151617')
auxdata_dir = os.path.join(repo_root, 'data-elcom_froemelt')
out_dir = os.path.join(repo_root, 'intermediate_files')

# define filenames (including paths)
habe_ausgaben_file = os.path.join(habe_2017_dir,
                                  'HABE151617_Ausgaben.txt')
habe_gueter_file = os.path.join(habe_2017_dir,
                                'HABE151617_Konsumgueter.txt')
habe_mengen_file = os.path.join(habe_2017_dir,
                                'HABE151617_Mengen.txt')
habe_standard_file = os.path.join(habe_2017_dir,
                                  'HABE151617_Standard.txt')
aux_elcom_file = os.path.join(auxdata_dir,
                              'Electricity_prices_per_canton_2015-2017.xlsx')
aux_froemelt_file = os.path.join(auxdata_dir,
                                 'Froemelt_et_al_2018_tables.xlsx')
imputed_file = os.path.join(out_dir,
                            'habe20152017_hh_prepared_imputed.csv')
properties_file = os.path.join(out_dir,
                               'hh_properties.csv')

# ----------------------------------------------------------------------------------------
# First, write household properties
# ----------------------------------------------------------------------------------------

# We need demographics data so first read in data on the households:
hh_data = pd.read_csv(habe_standard_file, sep='\t', header=0, index_col=0)
hh_data.sort_index()

# ----------------------------------------------------------------------------------------
# What's on offer in hh_data:
#
# HaushaltID	Strate01	SRPH20_151617	Gewicht20_151617
# E10	E11	E12	E15	E20	E21	E22	E23	E25	E70
# A30m	A31m	A32m	A33m	A35m	A40m	A41m	A42m	A43m	A44m	A50m
# A51m	A52m	A53m	A56m	A57m	A58m	A61m	A62m	A63m	A66m	A69m
# Primaereinkommen08	Bruttoeinkommen08	VerfuegbaresEinkommen08
# Sparbetrag08
# AnzahlPersonen98	AnzahlSelbstaendiger05	AnzahlUnselbstaendiger05
# AnzahlRentner05	AnzahlAusbildung05	AnzahlAndere05	AnzahlKinder05
# Anzahl0004Personen08	Anzahl0514Personen08	Anzahl1524Personen08
# Anzahl2534Personen08	Anzahl3544Personen08	Anzahl4554Personen08
# Anzahl5564Personen08	Anzahl6574Personen08	Anzahl7599Personen08
# Einpersonenhaushalt05	Mieterhaushalt05
# Rentnerhaushalt05	Jungerhaushalt05	FrauAlsReferenzperson05
# MindestensEinAuto05	MindestensEinVelo05	MindestensEinComputer05
# MindestensEinNatel05	MindestensEinHaustier05
# Jahr08	Grossregion01	Sprachregion98	Kanton08
# AltersklasseRefP08	Einkommensklasse08_151617	Haushaltstyp14
# HaushaltstypAnzahlKinder14	HaushaltstypAlter14	HaushaltstypGrob14
# HaushaltstypEinkommen14_151617  #
# ----------------------------------------------------------------------------------------
hh_properties = pd.concat([hh_data["Gewicht20_151617"],
                           hh_data["Kanton08"],
                           hh_data["Grossregion01"],
                           hh_data["Mieterhaushalt05"],
                           hh_data["Rentnerhaushalt05"],
                           hh_data["AnzahlPersonen98"],
                           hh_data["Sprachregion98"],
                           hh_data["Bruttoeinkommen08"],
                           hh_data["Haushaltstyp14"]
                           ], axis=1)
hh_properties.columns = ['weight', 'canton', 'region', 'renter', 'retired', 'size',
                         'language', 'income', 'hhtype']
hh_properties.to_csv(properties_file)


# ----------------------------------------------------------------------------------------
# Now, combine 'Ausgaben', 'Konsumgueter' and 'Mengen' files
# ----------------------------------------------------------------------------------------
# That is: Expenditure, durable goods and quantitities

ausgaben = pd.read_csv(habe_ausgaben_file,
                       sep='\t',
                       header=0,
                       index_col=0)
konsum = pd.read_csv(habe_gueter_file,
                     sep='\t',
                     header=0,
                     index_col=0)
mengen = pd.read_csv(habe_mengen_file,
                     sep='\t',
                     header=0,
                     index_col=0)

# Read in the LCA model to get the variable names of the consumption goods
konsum_variable_names = ['cg_nonewcars', 'cg_nousedcars', 'cg_nomotorbikes',
                         'cg_nobicycles', 'cg_nofreezers', 'cg_nodishwashers',
                         'cg_nowashmachines', 'cg_nodriers', 'cg_nocrttvs',
                         'cg_nolcdtvs', 'cg_nosat', 'cg_nocams',
                         'cg_novideorecs', 'cg_novieogames', 'cg_nodesktoppcs',
                         'cg_nolaptops', 'cg_noprinters', 'cg_nomobilephones',
                         'cg_nomp3players', 'cg_nogps']
konsum_variable_names

# change durable goods names to match the codes of the LCA model
konsum.columns = konsum_variable_names

# Append the three dataframes
Total_demand = pd.concat([ausgaben, konsum, mengen], axis=1)
column_names = [col.lower() for col in Total_demand.columns]
Total_demand.columns = column_names
Total_demand.sort_index()
Total_demand.index.name = 'haushaltid'
Total_demand


# ----------------------------------------------------------------------------------------
# Now we will add the following mx categories
#     mx571202: Kehrichtabfuhrgebühren des Hauptwohnsitzes
#     mx571203: Abwassergebühren des Hauptwohnsitzes
#     mx571204: Wasserzins des Hauptwohnsitzes
#     mx571301: Elektrizität des Hauptwohnsitzes
#     mx571302: Gas und andere Brennstoffe des Hauptwohnsitzes
#     mx571303: Zentralheizung oder Fernwärme des Hauptwohnsitzes
# mx571303 is not explicitly modelled but included in mx571302

# For the first three categories (Water supply, waste water treatment and waste
# collection) we will use the data from Andi for now (See table S6,S7 and S8).
# He got the data from: https://www.preisvergleiche.preisueberwacher.admin.ch/
# ----------------------------------------------------------------------------------------

weights = hh_data["Gewicht20_151617"]

# define masks needed for utility conversion
years = [2015, 2016, 2017]
# dictionary of canton numbers:
cantons_dict = {1: 'Canton Zurich',
                2: 'Canton Bern',
                3: 'Canton Lucerne',
                17: 'Canton St. Gallen',
                19: 'Canton Aargau',
                21: 'Canton Ticino',
                22: 'Canton Vaud',
                25: 'Canton Geneva',
                99: 'Swiss Average',
                }
cantons_dict_r = {k: v for v, k in cantons_dict.items()}
household_size = {'HH1': 1,
                  'HH2': 2,
                  'HH3': 3,
                  'HH4': 4
                  }

electricity_categories = {'H1': (0, 1600),
                          'H2': (1600, 2500),
                          # Difference between h3 and h4 is based in house
                          # type for which we do not have info.
                          # Therefore average the price
                          'H34': (2500, 4500),
                          'H5': (4500, 7500),
                          'H6': (13000, 25000),
                          'H7': (7500, 13000),
                          }
electricity_consumption = np.array([1600, 2500, 4500, 7500, 13000, 25000])
electricity_cats = ['H1', 'H2', 'H34', 'H5', 'H7', 'H6']

electricity_categories_r = {v: k for k, v in electricity_categories.items()}


# ---------------------------------------------------------------------------------------
# Move energy and other utility spending of second homes to primary home
# ---------------------------------------------------------------------------------------

# Energy and utility costs matter for the LCA but the LCA does not have separate entries
# for them in the case of second homes (subcategories of a572).
# I move expenditures from Nebenwohsitze to Hauptwohnsitz
# Rent and mortgage payments do not register in the LCA , so I leave them be

# a5722 is expenditure for general utility in second homes
# add a5722 to a571201 (and thus to a5712, a571) and subtract from a5722, a572
Total_demand['a571201'] = Total_demand['a571201'] + Total_demand['a5722']
Total_demand['a5712'] = Total_demand['a5712'] + Total_demand['a5722']
Total_demand['a571'] = Total_demand['a571'] + Total_demand['a5722']
Total_demand['a572'] = Total_demand['a572'] - Total_demand['a5722']
Total_demand['a5722'] = 0
Total_demand['a572200'] = 0

# a5723 is expenditure for energy in second homes
mask_not1but2 = (
    (Total_demand['a5713'] == 0)
    & (Total_demand['a5723'] != 0)
)
maski_not1but2 = mask_not1but2.astype(int)
mask_1and2 = (
    (Total_demand['a5713'] != 0)
    & (Total_demand['a5723'] != 0)
)
maski_1and2 = mask_1and2.astype(int)
sum(mask_not1but2)
sum(mask_1and2)

# if a5713 (energy in primary residence) does not exist,
# add a5723 to a571201 (general utility expenditure) and thus to a5712:
Total_demand['a571201'] = Total_demand['a571201'] + Total_demand['a5723']*maski_not1but2
Total_demand['a5712'] = Total_demand['a5712'] + Total_demand['a5723']*maski_not1but2

# if a5713 (energy in primary residence) exists, add a5723 to a571301, a571302, a571303:
# - scale them by (a5723+a5713)/a5713
ele_old = Total_demand['a571301']
fuel_old = Total_demand['a571302']
heat_old = Total_demand['a571303']
ele_new = (
    ele_old
    + mask_1and2 * (ele_old
                    * Total_demand['a5723'] / Total_demand['a5713']
                    ).fillna(0)
)
fuel_new = (
    fuel_old
    + mask_1and2 * (fuel_old
                    * Total_demand['a5723'] / Total_demand['a5713']
                    ).fillna(0)
)
heat_new = (
    heat_old
    + mask_1and2 * (heat_old
                    * Total_demand['a5723'] / Total_demand['a5713']
                    ).fillna(0)
)

ele_new.isna().sum()
fuel_new.isna().sum()
heat_new.isna().sum()

Total_demand['a571301'] = ele_new
Total_demand['a571302'] = fuel_new
Total_demand['a571303'] = heat_new

# - add to a5713
Total_demand['a5713'] = Total_demand['a5713'] + Total_demand['a5723']*maski_1and2

# independent of maski_1and2, maski_not1but2:
Total_demand['a571'] = Total_demand['a571'] + Total_demand['a5723']
# - subtract from a5723, a572
Total_demand['a572'] = Total_demand['a572'] - Total_demand['a5723']
Total_demand['a5723'] = 0
Total_demand['a572300'] = 0

# Consistency checks:
# checks = pd.DataFrame(index=Total_demand.index, columns=Total_demand.columns)
checks = pd.DataFrame(index=Total_demand.index)
checks['a5713'] = (Total_demand['a5713']
                   - Total_demand['a571301']
                   - Total_demand['a571302']
                   - Total_demand['a571303'])
checks['a5712'] = (Total_demand['a5712']
                   - Total_demand['a571201']
                   - Total_demand['a571202']
                   - Total_demand['a571203']
                   - Total_demand['a571204']
                   - Total_demand['a571205'])
checks['a571'] = (Total_demand['a571']
                  - Total_demand['a5711']
                  - Total_demand['a5712']
                  - Total_demand['a5713'])
checks['a5723'] = (Total_demand['a5723']
                   - Total_demand['a572300'])
checks['a5722'] = (Total_demand['a5722']
                   - Total_demand['a572200'])
checks['a572'] = (Total_demand['a572']
                  - Total_demand['a5721']
                  - Total_demand['a5722']
                  - Total_demand['a5723'])

checks
checks.max()
max_diff = checks.max().max()
if max_diff > 1e-6:
    raise ValueError("Modified HABE super- and sub-categories do not match.")

# ---------------------------------------------------------------------------------------
# BASIC CHECKS ABOUT ENERGY AND WASTE ENTRIES AND COMPARISON WITH LUMP-SUMS
# ---------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------
# Two observations:
# - Lump-sum payments (a571201) may entail energy expenses and might be relevant for
#   gwp-LCA, but they may not be counted against that gwp.
#   Indeed: LCA numbers suggest that flat-rate costs are low-emissions
#   (zero-emissions, actually: 'Utility lump sum of principal residence' are not even
#   listed in gwp-LCA). So the split into gwp-relevant categories is relevant.
# - Potential contents of lump-sum payments are:
#   + waste                        (a571202)
#   + waste water                  (a571203)
#   + water                        (a571204)
#   + other                        (a571205)
#   + electricity                  (a571301)
#   + gas and other fuels          (a571302)
#   + central and district heating (a571303)
# ----------------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------------
# How do we treat waste? Do lump-sum payments always imply waste expenditures?
# ---------------------------------------------------------------------------------------
# More than half of HHs with lump-sums pay no waste fees - I say waste must be
# included in lump-sum at least in these cases.
print(sum((Total_demand['a571201'] != 0)), 'HHs pay lump-sums and of those,',
      sum((Total_demand['a571201'] != 0)
          & ((Total_demand['a571202'] == 0))), 'pay no waste fees.')
print(sum((Total_demand['a571201'] == 0)),
      'HHs pay NO lump-sums and of those,',
      sum((Total_demand['a571201'] == 0)
          & ((Total_demand['a571202'] == 0))), 'pay no waste fees.')
# But do lump-sum payments always imply waste epxenditures?
# Compare average waste fees for lump-sum payers (ls) with waste fees of nls.
mask_ls = (Total_demand['a571201'] != 0)
mask_nls = (Total_demand['a571201'] == 0)
maski_ls = (Total_demand['a571201'] != 0).astype(int)
maski_nls = (Total_demand['a571201'] == 0).astype(int)
demand_waste_nls = Total_demand['a571202'].loc[mask_nls]*weights.loc[mask_nls]
demand_waste_ls = Total_demand['a571202'].loc[mask_ls]*weights.loc[mask_ls]
# For those paying lump-sum
mean_waste_ls = np.mean(demand_waste_ls[demand_waste_ls != 0])
print('The average positive waste epxenditure for lump-sum payers is:',
      mean_waste_ls)
# Now for those not paying lump-sum
mean_waste_nls = np.mean(demand_waste_nls[demand_waste_nls != 0])
print('The average positive waste epxenditure for non-lump-sum payers is:',
      mean_waste_nls)
# -> The above tells me that lump-sum payers with waste expenditure don't need
#    additional expenditures from lump-sums.
# -> Lump-sum payers withOUT waste expenditure shall get the average share of
#    non-lump sum payers.
# -> The only strange thing will be that there will be lots of non-lump-sum
#    payers withOUT waste payments at all.

# Create a 'mask' (vector of logical entries) to indicate those households that
# pay lump-sums and which are assumed to derive waste services from the
# lump-sums:
mask_havels_needwaste = ((Total_demand['a571201'] != 0)
                         & ((Total_demand['a571202'] == 0)))
maski_havels_needwaste = mask_havels_needwaste.astype(int)

# ---------------------------------------------------------------------------------------
# How do we treat energy? Do lump-sum payments always imply energy expenditures?
#
# I want to check how many households don't do energy and check how many households have
# lump-sums that are considerably bigger than their explicit energy expenditure.
#
# ---------------------------------------------------------------------------------------

print('147 HHs without explicit energy: ',
      sum((Total_demand['a571301'] == 0)
          & (Total_demand['a571302'] == 0)
          & (Total_demand['a571303'] == 0)), '.')
print('66 HHs without any energy anywhere: ',
      sum((Total_demand['a571201'] == 0)
          & (Total_demand['a571301'] == 0)
          & (Total_demand['a571302'] == 0)
          & (Total_demand['a571303'] == 0)), '.')
print('1907 HHs without any heat anywhere:',
      sum((Total_demand['a571201'] == 0)
          & (Total_demand['a571302'] == 0)
          & (Total_demand['a571303'] == 0)), '.')
print('70 HHs without any electricity anywhere:',
      sum((Total_demand['a571201'] == 0) & (Total_demand['a571301'] == 0)), '.')
# Conclusions:
# - Almost all households have expenditures for electricity
# - Around 2000 out of 10'000 have no expenditures for heat
#   (no lump-sums!, so nothing there).
# For the time being I try taking these zeros at face value and see if averages look ok.

# Determine those that have both energy and lump-sum
mask_lsene = (((Total_demand['a571201'] != 0)
               & ((Total_demand['a571301'] != 0)
                  | (Total_demand['a571302'] != 0)
                  | (Total_demand['a571303'] != 0))))
# Establish ratios between lump-sums and exlicit energy expenditures
ratio_ls_ene = (Total_demand['a571201'].loc[mask_lsene]
                / (Total_demand['a571301'].loc[mask_lsene]
                   + Total_demand['a571302'].loc[mask_lsene]
                   + Total_demand['a571303'].loc[mask_lsene]))
# I say that those households that have energy expenditures that are small compared to
# lump-sums shall get additional energy from lump-sums
mask_havels_needene = (
    # The HHs have positive lump-sums, and ...
    (Total_demand['a571201'] != 0)
    & (
        # ...don't have energy expenditures...
        (
            (Total_demand['a571301'] == 0)
            & (Total_demand['a571302'] == 0)
            & (Total_demand['a571303'] == 0)
        )
        # ... or have energy expenditures clearly lower than lump-sums
        | (ratio_ls_ene > 2)
    )
)
maski_havels_needene = mask_havels_needene.astype(int)
# ----------------------------------------------------------------------------------------
# Renters v. Owners
# ----------------------------------------------------------------------------------------
mask_rent = (hh_properties['renter'] == 1)
maski_rent = mask_rent.astype(int)
mask_own = (hh_properties['renter'] == 0)
maski_own = mask_own.astype(int)

# ---------------------------------------------------------------------------------------
# Establish utility shares of households without lump-sums (renters v. owners)
# ---------------------------------------------------------------------------------------
# For estimating shares need households without lump-sums:
# Categorize them according to rent/own and establish shares
# demand_rent = Total_demand['a571100']
# demand_ls = Total_demand['a571201']
demand_waste = Total_demand['a571202'].loc[mask_nls]*weights.loc[mask_nls]
demand_wwtr = Total_demand['a571203'].loc[mask_nls]*weights.loc[mask_nls]
demand_wtr = Total_demand['a571204'].loc[mask_nls]*weights.loc[mask_nls]
demand_other = Total_demand['a571205'].loc[mask_nls]*weights.loc[mask_nls]
demand_ele = Total_demand['a571301'].loc[mask_nls]*weights.loc[mask_nls]
demand_gas = Total_demand['a571302'].loc[mask_nls]*weights.loc[mask_nls]
demand_heat = Total_demand['a571303'].loc[mask_nls]*weights.loc[mask_nls]

total_ene_waste = sum(demand_waste + demand_wwtr + demand_wtr + demand_other
                      + demand_ele + demand_gas + demand_heat)
total_ene = sum(demand_wwtr + demand_wtr + demand_other
                + demand_ele + demand_gas + demand_heat)
total_waste = sum(demand_waste + demand_wwtr + demand_wtr + demand_other)
total_simple = sum(demand_wwtr + demand_wtr + demand_other)

rent_ene_waste = sum(demand_waste.loc[mask_rent] + demand_wwtr.loc[mask_rent]
                     + demand_wtr.loc[mask_rent] + demand_other.loc[mask_rent]
                     + demand_ele.loc[mask_rent] + demand_gas.loc[mask_rent]
                     + demand_heat.loc[mask_rent])
rent_ene = sum(demand_wwtr.loc[mask_rent]
               + demand_wtr.loc[mask_rent]
               + demand_other.loc[mask_rent]
               + demand_ele.loc[mask_rent] + demand_gas.loc[mask_rent]
               + demand_heat.loc[mask_rent])
rent_waste = sum(demand_waste.loc[mask_rent] + demand_wwtr.loc[mask_rent]
                 + demand_wtr.loc[mask_rent] + demand_other.loc[mask_rent])
rent_simple = sum(demand_wwtr.loc[mask_rent] + demand_wtr.loc[mask_rent]
                  + demand_other.loc[mask_rent])

own_ene_waste = sum(demand_waste.loc[mask_own] + demand_wwtr.loc[mask_own]
                    + demand_wtr.loc[mask_own] + demand_other.loc[mask_own]
                    + demand_ele.loc[mask_own] + demand_gas.loc[mask_own]
                    + demand_heat.loc[mask_own])
own_ene = sum(demand_wwtr.loc[mask_own] + demand_wtr.loc[mask_own]
              + demand_other.loc[mask_own]
              + demand_ele.loc[mask_own] + demand_gas.loc[mask_own]
              + demand_heat.loc[mask_own])
own_waste = sum(demand_waste.loc[mask_own] + demand_wwtr.loc[mask_own]
                + demand_wtr.loc[mask_own] + demand_other.loc[mask_own])
own_simple = sum(demand_wwtr.loc[mask_own] + demand_wtr.loc[mask_own]
                 + demand_other.loc[mask_own])

shares_nls_total = pd.DataFrame(
    np.array([[sum(demand_waste) / total_ene_waste,
               sum(demand_wwtr) / total_ene_waste,
               sum(demand_wtr) / total_ene_waste,
               sum(demand_other) / total_ene_waste,
               sum(demand_ele) / total_ene_waste,
               sum(demand_gas) / total_ene_waste,
               sum(demand_heat) / total_ene_waste],
              [0,
               sum(demand_wwtr) / total_ene,
               sum(demand_wtr) / total_ene,
               sum(demand_other) / total_ene,
               sum(demand_ele) / total_ene,
               sum(demand_gas) / total_ene,
               sum(demand_heat) / total_ene],
              [sum(demand_waste) / total_waste,
               sum(demand_wwtr) / total_waste,
               sum(demand_wtr) / total_waste,
               sum(demand_other) / total_waste,
               0, 0, 0],
              [0,
               sum(demand_wwtr) / total_simple,
               sum(demand_wtr) / total_simple,
               sum(demand_other) / total_simple,
               0, 0, 0]
              ]
             ),
    columns=['waste', 'wwtr', 'wtr', 'other', 'ele', 'gas', 'heat'],
    index=['ene_waste', 'ene', 'waste', 'simple']
)

shares_nls_rent = pd.DataFrame(
    np.array([[sum(demand_waste.loc[mask_rent]) / rent_ene_waste,
               sum(demand_wwtr.loc[mask_rent]) / rent_ene_waste,
               sum(demand_wtr.loc[mask_rent]) / rent_ene_waste,
               sum(demand_other.loc[mask_rent]) / rent_ene_waste,
               sum(demand_ele.loc[mask_rent]) / rent_ene_waste,
               sum(demand_gas.loc[mask_rent]) / rent_ene_waste,
               sum(demand_heat.loc[mask_rent]) / rent_ene_waste],
              [0,
               sum(demand_wwtr.loc[mask_rent]) / rent_ene,
               sum(demand_wtr.loc[mask_rent]) / rent_ene,
               sum(demand_other.loc[mask_rent]) / rent_ene,
               sum(demand_ele.loc[mask_rent]) / rent_ene,
               sum(demand_gas.loc[mask_rent]) / rent_ene,
               sum(demand_heat.loc[mask_rent]) / rent_ene],
              [sum(demand_waste.loc[mask_rent]) / rent_waste,
               sum(demand_wwtr.loc[mask_rent]) / rent_waste,
               sum(demand_wtr.loc[mask_rent]) / rent_waste,
               sum(demand_other.loc[mask_rent]) / rent_waste,
               0, 0, 0],
              [0,
               sum(demand_wwtr.loc[mask_rent]) / rent_simple,
               sum(demand_wtr.loc[mask_rent]) / rent_simple,
               sum(demand_other.loc[mask_rent]) / rent_simple,
               0, 0, 0]
              ]
             ),
    columns=['waste', 'wwtr', 'wtr', 'other', 'ele', 'gas', 'heat'],
    index=['ene_waste', 'ene', 'waste', 'simple']
)

shares_nls_own = pd.DataFrame(
    np.array([[sum(demand_waste.loc[mask_own]) / own_ene_waste,
               sum(demand_wwtr.loc[mask_own]) / own_ene_waste,
               sum(demand_wtr.loc[mask_own]) / own_ene_waste,
               sum(demand_other.loc[mask_own]) / own_ene_waste,
               sum(demand_ele.loc[mask_own]) / own_ene_waste,
               sum(demand_gas.loc[mask_own]) / own_ene_waste,
               sum(demand_heat.loc[mask_own]) / own_ene_waste],
              [0,
               sum(demand_wwtr.loc[mask_own]) / own_ene,
               sum(demand_wtr.loc[mask_own]) / own_ene,
               sum(demand_other.loc[mask_own]) / own_ene,
               sum(demand_ele.loc[mask_own]) / own_ene,
               sum(demand_gas.loc[mask_own]) / own_ene,
               sum(demand_heat.loc[mask_own]) / own_ene],
              [sum(demand_waste.loc[mask_own]) / own_waste,
               sum(demand_wwtr.loc[mask_own]) / own_waste,
               sum(demand_wtr.loc[mask_own]) / own_waste,
               sum(demand_other.loc[mask_own]) / own_waste,
               0, 0, 0],
              [0,
               sum(demand_wwtr.loc[mask_own]) / own_simple,
               sum(demand_wtr.loc[mask_own]) / own_simple,
               sum(demand_other.loc[mask_own]) / own_simple,
               0, 0, 0]
              ]
             ),
    columns=['waste', 'wwtr', 'wtr', 'other', 'ele', 'gas', 'heat'],
    index=['ene_waste', 'ene', 'waste', 'simple']
)

shares_nls_total
shares_nls_rent
shares_nls_own


# ---------------------------------------------------------------------------------------
# Now apply these established shares and split lump-sums accordingly
# ---------------------------------------------------------------------------------------
# Note: In the following, I use multiplication with maski_ as "& maski_" and
#       multiplication with abs(maski_ - 1) as "& not maski_".
# Too many NaNs:
# Total_demand_splitls = \
#       pd.DataFrame(index=Total_demand.index, columns=Total_demand.columns)
Total_demand_splitls = Total_demand.copy()
# waste (a571202)
Total_demand_splitls['a571202']
Total_demand_splitls['a571202'] = (
    Total_demand['a571202']
    # Owners
    + Total_demand['a571201']
    * maski_own * maski_havels_needene * maski_havels_needwaste
    * shares_nls_own['waste']['ene_waste']
    + Total_demand['a571201']
    * maski_own * maski_havels_needene * abs(maski_havels_needwaste - 1)
    * shares_nls_own['waste']['ene']
    + Total_demand['a571201']
    * maski_own * abs(maski_havels_needene - 1) * maski_havels_needwaste
    * shares_nls_own['waste']['waste']
    + Total_demand['a571201']
    * maski_own * abs(maski_havels_needene - 1) * abs(maski_havels_needwaste - 1)
    * shares_nls_own['waste']['simple']
    # Renters
    + Total_demand['a571201']
    * maski_rent * maski_havels_needene * maski_havels_needwaste
    * shares_nls_rent['waste']['ene_waste']
    + Total_demand['a571201']
    * maski_rent * maski_havels_needene * abs(maski_havels_needwaste - 1)
    * shares_nls_rent['waste']['ene']
    + Total_demand['a571201']
    * maski_rent * abs(maski_havels_needene - 1) * maski_havels_needwaste
    * shares_nls_rent['waste']['waste']
    + Total_demand['a571201']
    * maski_rent * abs(maski_havels_needene - 1) * abs(maski_havels_needwaste - 1)
    * shares_nls_rent['waste']['simple']
)
# wwtr = Total_demand['a571203']*maski_nls]
Total_demand_splitls['a571203'] = (
    Total_demand['a571203']
    # Owners
    + Total_demand['a571201']
    * maski_own * maski_havels_needene * maski_havels_needwaste
    * shares_nls_own['wwtr']['ene_waste']
    + Total_demand['a571201']
    * maski_own * maski_havels_needene * abs(maski_havels_needwaste - 1)
    * shares_nls_own['wwtr']['ene']
    + Total_demand['a571201']
    * maski_own * abs(maski_havels_needene - 1) * maski_havels_needwaste
    * shares_nls_own['wwtr']['waste']
    + Total_demand['a571201']
    * maski_own * abs(maski_havels_needene - 1) * abs(maski_havels_needwaste - 1)
    * shares_nls_own['wwtr']['simple']
    # Renters
    + Total_demand['a571201']
    * maski_rent * maski_havels_needene * maski_havels_needwaste
    * shares_nls_rent['wwtr']['ene_waste']
    + Total_demand['a571201']
    * maski_rent * maski_havels_needene * abs(maski_havels_needwaste - 1)
    * shares_nls_rent['wwtr']['ene']
    + Total_demand['a571201']
    * maski_rent * abs(maski_havels_needene - 1) * maski_havels_needwaste
    * shares_nls_rent['wwtr']['waste']
    + Total_demand['a571201']
    * maski_rent * abs(maski_havels_needene - 1) * abs(maski_havels_needwaste - 1)
    * shares_nls_rent['wwtr']['simple']
)
# wtr = Total_demand['a571204']*maski_nls]
Total_demand_splitls['a571204'] = (
    Total_demand['a571204']
    # Owners
    + Total_demand['a571201']
    * maski_own * maski_havels_needene * maski_havels_needwaste
    * shares_nls_own['wtr']['ene_waste']
    + Total_demand['a571201']
    * maski_own * maski_havels_needene * abs(maski_havels_needwaste - 1)
    * shares_nls_own['wtr']['ene']
    + Total_demand['a571201']
    * maski_own * abs(maski_havels_needene - 1) * maski_havels_needwaste
    * shares_nls_own['wtr']['waste']
    + Total_demand['a571201']
    * maski_own * abs(maski_havels_needene - 1) * abs(maski_havels_needwaste - 1)
    * shares_nls_own['wtr']['simple']
    # Renters
    + Total_demand['a571201']
    * maski_rent * maski_havels_needene * maski_havels_needwaste
    * shares_nls_rent['wtr']['ene_waste']
    + Total_demand['a571201']
    * maski_rent * maski_havels_needene * abs(maski_havels_needwaste - 1)
    * shares_nls_rent['wtr']['ene']
    + Total_demand['a571201']
    * maski_rent * abs(maski_havels_needene - 1) * maski_havels_needwaste
    * shares_nls_rent['wtr']['waste']
    + Total_demand['a571201']
    * maski_rent * abs(maski_havels_needene - 1) * abs(maski_havels_needwaste - 1)
    * shares_nls_rent['wtr']['simple']
)
# other = Total_demand['a571205']*maski_nls]
Total_demand_splitls['a571205'] = (
    Total_demand['a571205']
    # Owners
    + Total_demand['a571201']
    * maski_own * maski_havels_needene * maski_havels_needwaste
    * shares_nls_own['other']['ene_waste']
    + Total_demand['a571201']
    * maski_own * maski_havels_needene * abs(maski_havels_needwaste - 1)
    * shares_nls_own['other']['ene']
    + Total_demand['a571201']
    * maski_own * abs(maski_havels_needene - 1) * maski_havels_needwaste
    * shares_nls_own['other']['waste']
    + Total_demand['a571201']
    * maski_own * abs(maski_havels_needene - 1) * abs(maski_havels_needwaste - 1)
    * shares_nls_own['other']['simple']
    # Renters
    + Total_demand['a571201']
    * maski_rent * maski_havels_needene * maski_havels_needwaste
    * shares_nls_rent['other']['ene_waste']
    + Total_demand['a571201']
    * maski_rent * maski_havels_needene * abs(maski_havels_needwaste - 1)
    * shares_nls_rent['other']['ene']
    + Total_demand['a571201']
    * maski_rent * abs(maski_havels_needene - 1) * maski_havels_needwaste
    * shares_nls_rent['other']['waste']
    + Total_demand['a571201']
    * maski_rent * abs(maski_havels_needene - 1) * abs(maski_havels_needwaste - 1)
    * shares_nls_rent['other']['simple']
)
# ele = Total_demand['a571301']*maski_nls]
Total_demand_splitls['a571301'] = (
    Total_demand['a571301']
    # Owners
    + Total_demand['a571201']
    * maski_own * maski_havels_needene * maski_havels_needwaste
    * shares_nls_own['ele']['ene_waste']
    + Total_demand['a571201']
    * maski_own * maski_havels_needene * abs(maski_havels_needwaste - 1)
    * shares_nls_own['ele']['ene']
    + Total_demand['a571201']
    * maski_own * abs(maski_havels_needene - 1) * maski_havels_needwaste
    * shares_nls_own['ele']['waste']
    + Total_demand['a571201']
    * maski_own * abs(maski_havels_needene - 1) * abs(maski_havels_needwaste - 1)
    * shares_nls_own['ele']['simple']
    # Renters
    + Total_demand['a571201']
    * maski_rent * maski_havels_needene * maski_havels_needwaste
    * shares_nls_rent['ele']['ene_waste']
    + Total_demand['a571201']
    * maski_rent * maski_havels_needene * abs(maski_havels_needwaste - 1)
    * shares_nls_rent['ele']['ene']
    + Total_demand['a571201']
    * maski_rent * abs(maski_havels_needene - 1) * maski_havels_needwaste
    * shares_nls_rent['ele']['waste']
    + Total_demand['a571201']
    * maski_rent * abs(maski_havels_needene - 1) * abs(maski_havels_needwaste - 1)
    * shares_nls_rent['ele']['simple']
)
# gas = Total_demand['a571302']*maski_nls]
Total_demand_splitls['a571302'] = (
    Total_demand['a571302']
    # Owners
    + Total_demand['a571201']
    * maski_own * maski_havels_needene * maski_havels_needwaste
    * shares_nls_own['gas']['ene_waste']
    + Total_demand['a571201']
    * maski_own * maski_havels_needene * abs(maski_havels_needwaste - 1)
    * shares_nls_own['gas']['ene']
    + Total_demand['a571201']
    * maski_own * abs(maski_havels_needene - 1) * maski_havels_needwaste
    * shares_nls_own['gas']['waste']
    + Total_demand['a571201']
    * maski_own * abs(maski_havels_needene - 1) * abs(maski_havels_needwaste - 1)
    * shares_nls_own['gas']['simple']
    # Renters
    + Total_demand['a571201']
    * maski_rent * maski_havels_needene * maski_havels_needwaste
    * shares_nls_rent['gas']['ene_waste']
    + Total_demand['a571201']
    * maski_rent * maski_havels_needene * abs(maski_havels_needwaste - 1)
    * shares_nls_rent['gas']['ene']
    + Total_demand['a571201']
    * maski_rent * abs(maski_havels_needene - 1) * maski_havels_needwaste
    * shares_nls_rent['gas']['waste']
    + Total_demand['a571201']
    * maski_rent * abs(maski_havels_needene - 1) * abs(maski_havels_needwaste - 1)
    * shares_nls_rent['gas']['simple']
)
# heat = Total_demand['a571303']*maski_nls]
Total_demand_splitls['a571303'] = (
    Total_demand['a571303']
    # Owners
    + Total_demand['a571201']
    * maski_own * maski_havels_needene * maski_havels_needwaste
    * shares_nls_own['heat']['ene_waste']
    + Total_demand['a571201']
    * maski_own * maski_havels_needene * abs(maski_havels_needwaste - 1)
    * shares_nls_own['heat']['ene']
    + Total_demand['a571201']
    * maski_own * abs(maski_havels_needene - 1) * maski_havels_needwaste
    * shares_nls_own['heat']['waste']
    + Total_demand['a571201']
    * maski_own * abs(maski_havels_needene - 1) * abs(maski_havels_needwaste - 1)
    * shares_nls_own['heat']['simple']
    # Renters
    + Total_demand['a571201']
    * maski_rent * maski_havels_needene * maski_havels_needwaste
    * shares_nls_rent['heat']['ene_waste']
    + Total_demand['a571201']
    * maski_rent * maski_havels_needene * abs(maski_havels_needwaste - 1)
    * shares_nls_rent['heat']['ene']
    + Total_demand['a571201']
    * maski_rent * abs(maski_havels_needene - 1) * maski_havels_needwaste
    * shares_nls_rent['heat']['waste']
    + Total_demand['a571201']
    * maski_rent * abs(maski_havels_needene - 1) * abs(maski_havels_needwaste - 1)
    * shares_nls_rent['heat']['simple']
)

# Finally get rid of lump-sums
Total_demand_splitls['a571201'] = 0

Total_utilities_before = sum(Total_demand['a571201']
                             + Total_demand['a571202']
                             + Total_demand['a571203']
                             + Total_demand['a571204']
                             + Total_demand['a571205']
                             + Total_demand['a571301']
                             + Total_demand['a571302']
                             + Total_demand['a571303'])

Total_utilities_after = sum(Total_demand_splitls['a571201']
                            + Total_demand_splitls['a571202']
                            + Total_demand_splitls['a571203']
                            + Total_demand_splitls['a571204']
                            + Total_demand_splitls['a571205']
                            + Total_demand_splitls['a571301']
                            + Total_demand_splitls['a571302']
                            + Total_demand_splitls['a571303'])


print("See? I totally did everything correctly:",
      "\nBefore my changes, the total expenditure on utilities was",
      Total_utilities_before,
      "\nand after my changes, it is", Total_utilities_after, ".",
      "The difference is a mere", (Total_utilities_after-Total_utilities_before))

# ----------------------------------------------------------------------------------------
# First waste bags, waste water treatment, and water supply
# ----------------------------------------------------------------------------------------

# read in waste bag-, waste water treatment-, and water supply- prices from Andi
waste_prices = pd.read_excel(aux_froemelt_file,
                             sheet_name='waste bag prices',
                             index_col=0)
waste_prices.rename(index={'Swiss Average (other cantons)': 'Swiss Average'},
                    inplace=True)
waste_water_prices = pd.read_excel(aux_froemelt_file,
                                   sheet_name='waste water treatment prices',
                                   index_col=0)
waste_water_prices.rename(index={'Swiss Average (other cantons)': 'Swiss Average'},
                          inplace=True)
water_prices = pd.read_excel(aux_froemelt_file,
                             sheet_name='water supply prices',
                             index_col=0)
water_prices.rename(index={'Swiss Average (other cantons)': 'Swiss Average'},
                    inplace=True)

# multiply the hh expenditure with the price based on household demographic
mx571202 = Total_demand_splitls['a571202'].copy()  # waste
mx571202.name = 'mx571202'
mx571203 = Total_demand_splitls['a571203'].copy()  # waste water treatment
mx571203.name = 'mx571203'
mx571204 = Total_demand_splitls['a571204'].copy()  # Water supply
mx571204.name = 'mx571204'

n_hh = 0  # sum entries in all masks to check if all households are covered
for hh, canton in itertools.product(household_size.keys(), cantons_dict_r.keys()):
    if not hh == 'HH4':
        mask = ((hh_data['AnzahlPersonen98'] == household_size[hh])
                & (hh_data['Kanton08'] == cantons_dict_r[canton]))
        n_hh += mask.sum()
    else:
        mask = ((hh_data['AnzahlPersonen98'] >= household_size[hh])
                & (hh_data['Kanton08'] == cantons_dict_r[canton]))
        n_hh += mask.sum()
    waste_price = waste_prices.loc[canton, hh]
    mx571202.loc[mask] /= waste_price
    waste_water_price = waste_water_prices.loc[canton, hh]
    mx571203.loc[mask] /= waste_water_price
    water_price = water_prices.loc[canton, hh]
    mx571204.loc[mask] /= water_price

print(n_hh, 'households covered')


# Now the geneva price for waste is zero, so give people there just
# an the average non zero waste for the rest of CH
geneva = cantons_dict_r['Canton Geneva']
geneva_households = hh_data[hh_data['Kanton08'] == geneva].index
non_geneva_housholds = hh_data[hh_data['Kanton08'] != geneva].index
mx571202.loc[geneva_households] = mx571202.loc[
    non_geneva_housholds
].loc[
    mx571202.loc[non_geneva_housholds] != 0
].mean()

# ---------------------------------------------------------------------------------------
# SHOW SOME STUFF GRAPHICALLY
# ---------------------------------------------------------------------------------------
# Interactiveness seems not to work: turn off and use plt.show
plt.ioff()
plt.plot()
plt.ioff()


Total_demand_splitls.loc[
    Total_demand_splitls['a571202'] != 0,
    'a571202'
].plot(kind='hist',
       bins=np.linspace(1, 201, 21))
plt.axvline(
    Total_demand_splitls.loc[Total_demand_splitls['a571202'] != 0, 'a571202'].median(),
    c='r')
plt.axvline(
    Total_demand_splitls.loc[Total_demand_splitls['a571202'] != 0, 'a571202'].mean(),
    c='orange')
plt.xlabel('Waste collection expenditure')
plt.show()

Total_demand_splitls.loc[Total_demand_splitls['a571202'] != 0, 'a571202'].std()

# ----------------------------------------------------------------------------------------
# Waste water
# ----------------------------------------------------------------------------------------
# set waste for all households without expenditure data to the CH average
mx571202.loc[Total_demand_splitls['a571202'] == 0] = mx571202.loc[mx571202 != 0].mean()
mx571202
# number of households without waste water expenditure
sum(Total_demand_splitls['a571203'] == 0)

plt.ioff()
mx571203.loc[Total_demand_splitls['a571203'] != 0].plot(kind='hist', bins=30)
plt.axvline(mx571203.loc[Total_demand_splitls['a571203'] != 0].median(), c='r')
plt.axvline(mx571203.loc[Total_demand_splitls['a571203'] != 0].mean(), c='orange')
plt.show()

mx571203.loc[Total_demand_splitls['a571203'] != 0].mean()
# same here, set waste water collection to average for household without expenditure info
mx571203.loc[Total_demand_splitls['a571203'] == 0] = \
    mx571203.loc[Total_demand_splitls['a571203'] != 0].mean()
mx571203

# ----------------------------------------------------------------------------------------
# Water use
# ----------------------------------------------------------------------------------------
# number of households without water use expenditure
sum(Total_demand_splitls['a571204'] == 0)

plt.ioff()
mx571204.loc[Total_demand_splitls['a571204'] != 0].plot(kind='hist', bins=30)
plt.axvline(mx571204.loc[Total_demand_splitls['a571204'] != 0].median(), c='r')
plt.axvline(mx571204.loc[Total_demand_splitls['a571204'] != 0].mean(), c='orange')
plt.show()

mx571204.loc[Total_demand_splitls['a571204'] != 0].mean()
# same here, set water use to average for household without expenditure info
mx571204.loc[Total_demand_splitls['a571204'] == 0] = (
    mx571204.loc[Total_demand_splitls['a571204'] != 0].mean()
)
mx571204
# Now add the physical demands to the Total_demand_splitlss
Total_demand_splitls = pd.concat([Total_demand_splitls, mx571202, mx571203,
                                  mx571204],
                                 axis=1)
# check that it worked
Total_demand_splitls[['a571202', 'mx571202', 'a571203', 'mx571203', 'a571204',
                      'mx571204']]

# ----------------------------------------------------------------------------------------
# Electricity
# ----------------------------------------------------------------------------------------

# Read in electricity prices
electricity_prices = {}
for year in years:
    electricity_prices_dummy = pd.read_excel(aux_elcom_file,
                                             sheet_name=str(year),
                                             index_col=0)
    electricity_prices_dummy.rename(
        index={'Swiss Average (of above cantons)': 'Swiss Average'},
        inplace=True)
    electricity_prices_dummy['average'] = electricity_prices_dummy.mean(axis=1)
    electricity_prices_dummy['H34'] = electricity_prices_dummy[['H3', 'H4']].mean(axis=1)
    del electricity_prices_dummy['H3']
    del electricity_prices_dummy['H4']
    electricity_prices[str(year)] = electricity_prices_dummy
del electricity_prices_dummy
electricity_prices['2015']


def find_elec_price_iteratively(prices, cats, expenditure, years, hh_data, cantons_dict):
    '''Iteratively estimate the physical electricity consumption
    from expenditure and electricity prices per canton and consumption bracket.'''
    elec_demand = expenditure.copy()
    elec_demand.name = 'mx571301'
    cantons = hh_data['Kanton08'].apply(lambda row: cantons_dict[row])
    entries_updated = []
    # treat each year seperately
    for year in years:
        print(f'Estimating electricity consumption for {year}')
        year_mask = hh_data['Jahr08'] == year
        # first estimate: average price (over categories) for a given canton
        estimate = (elec_demand.loc[year_mask]
                    / prices[str(year)].loc[
                        cantons.loc[year_mask],
                        'average'
                    ].mean(axis=0) * 100)  # *100 to convert to CHF
        estimate_update = elec_demand.loc[year_mask].copy()
        estimate_old = estimate.copy()
        n_loops = 0
        # In case there are some entries that keep jumping between
        # two price categories with every update, break the while
        # loop if the new update is the same as the second to last one.
        # If so, get an average for all those 'jumping' entries below.
        while (not np.allclose(estimate_update, estimate)
               and not np.allclose(estimate_old, estimate_update)):
            estimate_old = estimate.copy()
            estimate = estimate_update.copy()
            for key in cats.keys():
                cat_mask = estimate.between(cats[key][0], cats[key][1])
                estimate_update.loc[cat_mask] = (
                    elec_demand.loc[year_mask].loc[cat_mask]
                    / prices[str(year)].loc[
                        cantons.loc[year_mask].loc[cat_mask],
                        key
                    ].values
                    * 100)  # *100 to convert to CHF
            n_loops += 1
            entries_updated.append(sum(estimate_update != estimate))
            print(f'{entries_updated[-1]} entries updated')
        print(f'Needed {n_loops} iterations')
        # For those 'jumping' entries take the average of the two cases
        mask = estimate_update != estimate
        print(f'There were {mask.sum()} entries that jumped,'
              + ' taking average for those... \n')
        estimate_update.loc[mask] = (
            (estimate.loc[mask]-estimate_update.loc[mask])/2
            + estimate_update.loc[mask]
        )
        # now update the electricity demand series
        elec_demand.loc[year_mask] = estimate_update
    print(f'Total entries updated: {sum(entries_updated)}')
    return elec_demand


def find_elec_price_iteratively_2(prices, cats, expenditure,
                                  years, hh_data, cantons_dict):
    '''Iteratively estimate the physical electricity consumption
    from expenditure and electricity prices per canton and consumption bracket.'''
    elec_demand = expenditure.copy()
    elec_demand.name = 'mx571301'
    cantons = hh_data['Kanton08'].apply(lambda row: cantons_dict[row])
    entries_updated = []
    # treat each year seperately
    for year in years:
        print(f'Estimating electricity consumption for {year}')
        year_mask = hh_data['Jahr08'] == year
        # first estimate: average price (over categories) for a given canton
        estimate = (elec_demand.loc[year_mask]
                    / prices[str(year)].loc[
                        cantons.loc[year_mask],
                        'average'
                    ].mean(axis=0) * 100)  # *100 to convert to CHF
        estimate_update = elec_demand.loc[year_mask].copy()
        estimate_old = estimate.copy()
        n_loops = 0
        # In case there are some entries that keep jumping between two price categories
        # with every update break the while loop if the new update is the same as the
        # second to last one.
        # If so, get an average for all those 'jumping' entries below
        while (not np.allclose(estimate_update, estimate)
               and not np.allclose(estimate_old, estimate_update)):
            estimate_old = estimate.copy()
            estimate = estimate_update.copy()
            for hh, demand in zip(estimate.index, estimate):
                idx = np.searchsorted(electricity_consumption, demand)
                cat = electricity_cats[idx]
                # print(cat_mask.sum())
                estimate_update.loc[hh] = (elec_demand.loc[hh]
                                           / prices[str(year)].loc[
                                               cantons.loc[hh],
                                               cat
                                           ] * 100)  # *100 to convert to CHF
            n_loops += 1
            entries_updated.append(sum(estimate_update != estimate))
            print(f'{entries_updated[-1]} entries updated')
        print(f'Needed {n_loops} iterations')
        # For those 'jumping' entries take the average of the two cases
        mask = estimate_update != estimate
        print(f'There were {mask.sum()} entries that jumped,'
              + ' taking average for those... \n')
        estimate_update.loc[mask] = ((estimate.loc[mask]-estimate_update.loc[mask])/2
                                     + estimate_update.loc[mask])
        # now update the electricity demand series
        elec_demand.loc[year_mask] = estimate_update
    print(f'Total entries updated: {sum(entries_updated)}')
    return elec_demand


a = find_elec_price_iteratively_2(electricity_prices, electricity_categories,
                                  Total_demand_splitls['a571301'], years,
                                  hh_data, cantons_dict)

b = find_elec_price_iteratively(electricity_prices, electricity_categories,
                                Total_demand_splitls['a571301'], years,
                                hh_data, cantons_dict)

# mean eletricity consumption (a)
print(a.sum()/len(a))
a.mean()
np.mean(a[a != 0])

# mean eletricity consumption (b)
b.mean()
print(b.sum()/len(b))
np.mean(b[b != 0])

# I mean, a and be are SO the same thing
(a-b).mean()
(a-b).max()
(a-b).min()
(a-b).std()
elec_demand = Total_demand_splitls['a571301'].copy()
elec_demand.name = 'mx571301'

cantons = hh_data['Kanton08'].apply(lambda row: cantons_dict[row])
for year in years:
    print(f'Estimating electricity consumption for {year}')
    year_mask = hh_data['Jahr08'] == year
    # first estimate: average price (over categories) for a given canton
    elec_demand.loc[year_mask] = (elec_demand.loc[year_mask]
                                  / electricity_prices[str(year)].loc[
                                      cantons.loc[year_mask],
                                      'average'
                                  ].values * 100)  # *100 to convert to CHF
elec_demand
elec_demand.mean()

# ----------------------------------------------------------------------------------------
# Arthur and Chris (PSI):
# For some reason the average cantonal price gives a better household average than using
# the iterative price. The average household electricity demand for the years 2015,
# 2016, 2017 is 436 kWh, 438kWh and 430 kWh according to national stats from BFE.
# I don't know why but we will use this for now, as the iterative etimate seem
# unreasonably low!
# Me (ZHAW):
# After implementing Froemelt's advice on splitting lump-sums into energy and other
# demands the cantonal prices actually look better now. I'm using 'a' rather than
# 'elec_demand'.
# ----------------------------------------------------------------------------------------
Total_demand_splitls = pd.concat([Total_demand_splitls, a], axis=1)
Total_demand_splitls

# ----------------------------------------------------------------------------------------
# Heat
#
# There are very few households with heating data for 2015-2017. No idea why.
# Use the Swiss houshold average per year for from BFE
# 11199-Webtabellen_Haushalte_2021 Table 12 for now.
# ----------------------------------------------------------------------------------------

# There are again only few households with expenditure data for heating
# (central and district)
Total_demand_splitls.loc[Total_demand_splitls['a571303'] != 0, 'a571303']
# There are again only few households with expenditure data for heating
# (gas and other fuels)
Total_demand_splitls.loc[Total_demand_splitls['a571302'] != 0, 'a571302']
# Just under two thirds of HHs have (imputed) expenditure data for heating (both kinds)
Total_demand_splitls.loc[
    ((Total_demand_splitls['a571302'] != 0) | (Total_demand_splitls['a571303'] != 0)),
    'a571302'
]

# What Arthur and Chris (PSI) did:
# So for now we will just give all households the average monthly household heating
# demand for switzerland from BFE 11199-Webtabellen_Haushalte_2021 Table 12

# Now me:
# Common extimates of annual heating expenditures are ~1500 Francs (~125 per months)

# With all the zeros, my average is not so hot:
heat_expend = np.average((Total_demand_splitls['a571302']
                          + Total_demand_splitls['a571303']),
                         weights=weights)
heat_expend

# Without the zeros, the numbers look more reasonable:
avg_non0_heatexp = np.average(
    (Total_demand_splitls['a571302']
     + Total_demand_splitls['a571303']).loc[(Total_demand_splitls['a571302']
                                             + Total_demand_splitls['a571303']) != 0],
    weights=weights.loc[(Total_demand_splitls['a571302']
                         + Total_demand_splitls['a571303']) != 0]
)
avg_non0_heatexp

print("avg_non0_heatexp is close to what others cite as average heat expenditure:",
      avg_non0_heatexp)

# ----------------------------------------------------------------------------------------
# I want to fill in zeros with something that
# - averages to avg_non0_heatexp
# - is proportional to spending on housing (to get at least SOME heterogeneity)
# ----------------------------------------------------------------------------------------

# Establish where we need to add sth (and how much, on average):
heat_expend_add = avg_non0_heatexp*((Total_demand_splitls['a571302']
                                     + Total_demand_splitls['a571303']) == 0).astype(int)


# Here's a function that plots and linearly interpolates non-zero heating
def scatter_ols(x, y, w=None):
    xn0 = x.loc[(y != 0)]
    yn0 = y.loc[(y != 0)]
    if w is not None:
        wn0 = w.loc[(y != 0)]
    else:
        wn0 = None
    c1, c0 = np.polyfit(xn0, yn0, 1, w=wn0)
    plt.ioff()
    plt.plot(x, y, 'o')
    plt.plot(xn0, c0+c1*xn0, color='red')
    plt.show()
    return c0, c1


# Graph and interpolate fuels only
scatter_ols(Total_demand['a571'], Total_demand['a571302'])
# Graph and interpolate central/district only
scatter_ols(Total_demand['a571'], Total_demand['a571303'])
# Graph and interpolate both
c0, c1 = scatter_ols(Total_demand_splitls['a571'],
                     (Total_demand_splitls['a571302'] + Total_demand_splitls['a571303']),
                     np.sqrt(weights)
                     )

# in the sample (non-zero heating), check if estimates have same mean as measurements
sample_estimates = (c0
                    + c1*(Total_demand_splitls['a571'])
                    ).loc[(Total_demand_splitls['a571302']
                           + Total_demand_splitls['a571303']) != 0]
sample_estimates
np.average(sample_estimates,
           weights=weights.loc[(Total_demand_splitls['a571302']
                                + Total_demand_splitls['a571303']) != 0]
           )
avg_non0_heatexp

# outside the 'sample' (for those with zero heating), establish expenditure estimates
nonsample_estimates = (c0
                       + c1*(Total_demand_splitls['a571'])
                       ).loc[(Total_demand_splitls['a571302']
                              + Total_demand_splitls['a571303']) == 0]

# outside 'sample', establish mean of expenditure estimates
nonsample_average = np.average(nonsample_estimates,
                               weights=weights.loc[(Total_demand_splitls['a571302']
                                                    + Total_demand_splitls['a571303'])
                                                   == 0])

nonsample_average

# now, use nonsample_average and nonsample_estimates to scale heat_expend_add and: add
all_estimates = (c0 + c1*(Total_demand_splitls['a571']))
fuelshare = (sum(Total_demand_splitls['a571302'] * weights)
             / sum((Total_demand_splitls['a571302']
                    + Total_demand_splitls['a571303'])
                   * weights)
             )
# Here I'm being extra careful: heat_expend_add is 0 unless
# (Total_demand_splitls['a571302'] + Total_demand_splitls['a571303']) == 0
# Total_demand_splitls['a571302'].loc[
#     (Total_demand_splitls['a571302']
#      + Total_demand_splitls['a571303'])
Total_demand_splitls['a571302'] = (Total_demand_splitls['a571302']
                                   + heat_expend_add
                                   * all_estimates/nonsample_average
                                   * fuelshare)
Total_demand_splitls['a571303'] = (Total_demand_splitls['a571303']
                                   + heat_expend_add
                                   * all_estimates/nonsample_average
                                   * (1-fuelshare))

# further down, scale heat demand by
# 'expenditure estimate'/'mean of expenditure estimates'

avg_heat = np.average(
    (Total_demand_splitls['a571302'] + Total_demand_splitls['a571303']),
    weights=weights
)
avg_heat
avg_non0_heatexp

# Reset expenditure summaries and check totals
Total_demand_splitls['a5711'] = (Total_demand_splitls['a571100'])
Total_demand_splitls['a5712'] = (Total_demand_splitls['a571201']
                                 + Total_demand_splitls['a571202']
                                 + Total_demand_splitls['a571203']
                                 + Total_demand_splitls['a571204']
                                 + Total_demand_splitls['a571205'])
Total_demand_splitls['a5713'] = (Total_demand_splitls['a571301']
                                 + Total_demand_splitls['a571302']
                                 + Total_demand_splitls['a571303'])
Total_demand_splitls['a571'] = (Total_demand_splitls['a5711']
                                + Total_demand_splitls['a5712']
                                + Total_demand_splitls['a5713'])
Total_demand_splitls['a57'] = (Total_demand_splitls['a571']
                               + Total_demand_splitls['a572']
                               + Total_demand_splitls['a573'])

max(Total_demand_splitls['a57']
    - Total_demand['a57']
    - heat_expend_add * all_estimates/nonsample_average)
max(Total_demand_splitls['a571']
    - Total_demand['a571']
    - heat_expend_add * all_estimates/nonsample_average)

# After checking that for a57 and a571, everything adds up, I make it simple:
Total_demand_splitls['a50'] = (Total_demand['a50']
                               + heat_expend_add * all_estimates/nonsample_average)

avg_non0_heatexp
avg_heatexp = np.average(Total_demand_splitls['a571302']
                         + Total_demand_splitls['a571303'],
                         weights=weights)

avg_heatexp

# Check the obvious: what used to be points along y=0 are now points along a
# sloped line that looks very similar to the new linear interpolation (red line)
scatter_ols(Total_demand_splitls['a571'],
            (Total_demand_splitls['a571302'] + Total_demand_splitls['a571303']),
            np.sqrt(weights)
            )

heat_demand_2015 = 4082
heat_demand_2016 = 4005
heat_demand_2017 = 3945

fuel_demand = Total_demand_splitls['a571302'].copy()
heat_demand = Total_demand_splitls['a571303'].copy()
fuel_demand.name = 'mx571302'
heat_demand.name = 'mx571303'

for year, demand in zip(years, [heat_demand_2015, heat_demand_2016, heat_demand_2017]):
    print(year, demand)
    year_mask = hh_data['Jahr08'] == year
    fuel_demand.loc[year_mask] = demand * Total_demand_splitls['a571302'] / avg_heatexp
    heat_demand.loc[year_mask] = demand * Total_demand_splitls['a571303'] / avg_heatexp
fuel_demand
heat_demand

Total_demand_splitls = pd.concat([Total_demand_splitls, fuel_demand, heat_demand], axis=1)
Total_demand_splitls

Total_demand_splitls.to_csv(imputed_file)

# ----------------------------------------------------------------------------------------
# Note:
#
# Here I'm exploiting more information than Arthur and Chris (PSI) do. I don't just plug
# average heat demand into all households, but I make heat demand proportional to
# expenditure.
# Froemelt et al., however, use even more information: staggered fuel prices. Such
# fuel prices are, in principle, available for 2015 to 2017 in
# ../data-elcom_froemelt/Froemelt_et_al_2018_tables_updates.xlsx
# and a function similar to find_elec_price_iteratively could derive quantities of fuel
# demand from these staggered prices and expenditures. But for the time being,
# I leave that to future work.
# ----------------------------------------------------------------------------------------
