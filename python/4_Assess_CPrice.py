# Combine HABE data in ../habe20152017_hh_prepared_imputed.csv with LCA data in
# ../data-gwp/nfp73-ccl-preliminary-results-ipcc-gwp-april-2023.csv

import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns

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
print('Population according to HABE: ', sum(hh_data['PopulationWeight']))
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
                      hh_data['npers']], axis=1)

# ----------------------------------------------------------------------------------------
# Create a bunch of boxplots describing households, spending, GWP across income
# ----------------------------------------------------------------------------------------

# Create totals of GWP

# A column of zeros:
habe_lca['tot_gwp'] = 0
for c in habe_lca.columns:
    if (c[0: 3] == 'gwp'):
        habe_lca['tot_gwp'] = habe_lca['tot_gwp'] + habe_lca[c]

# -https://zenodo.org/records/8296864-

# ----------------------------------------------------------------------------------------
# Aggregate the consumption categories to a reasonable number of commodities
# ----------------------------------------------------------------------------------------

# This is simlar to what I did in 3_Lookat_HABE_LCA.py, but there I did it for
# Decile means, while I keep the whole household heterogeneity here.

aggregation = pd.read_excel(agg_file,
                            sheet_name='overview',
                            index_col=0)
aggregation_cprice = pd.read_excel(agg_file,
                                   sheet_name='cprice_versions',
                                   index_col=0)
# aggregation_mobility = pd.read_excel(agg_file,
#                                      sheet_name='mobility',
#                                      index_col=0)
# aggregation_residential = pd.read_excel(agg_file,
#                                         sheet_name='heating',
#                                         index_col=0)
aggregation
aggregation_cprice

hhindex = habe_lca.index


def aggregate_categories(means=habe_lca, aggregation=aggregation,
                         displayname="HH-ID", index=hhindex):
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


aggregate_categories(habe_lca)

gwp_sums = aggregate_categories(habe_lca, aggregation=aggregation_cprice)

gwp_sums.columns

habe_lca['tot_gwp']

hh_description = pd.DataFrame()
hh_description['Decile group of lifetime income'] = hh_data['ExpDecile']
hh_description['popweights'] = hh_data['popweights'].round().astype('int')
hh_description['statweights'] = hh_data['statweights'].round().astype('int')
hh_description['size'] = hh_data['npers'].round().astype('int')
hh_description['Spending'] = hh_data['Spending']*12
hh_description['Urbanization'] = habe_urban
hh_description['Renting'] = hh_data['Mieterhaushalt05']
hh_description['Pensioner'] = hh_data['Rentnerhaushalt05']
hh_description['Female_head'] = hh_data['FrauAlsReferenzperson05']
hh_description['Region'] = hh_data['Grossregion01']
hh_description['Canton'] = hh_data['Kanton08']
hh_description['Quintile group'] = hh_data['Einkommensklasse08_151617']
hh_description['Household type'] = hh_data['Haushaltstyp14']
hh_description['Household type / HABE income quintile group'] = \
    hh_data['HaushaltstypEinkommen14_151617']
hh_description['Urbanization'] = hh_description['Urbanization'].astype('category')
hh_description['Renting'] = hh_description[
    'Renting'
].astype('category').cat.rename_categories({0: 'Owner', 1: 'Renter'})
hh_description['Pensioner'] = hh_description['Pensioner'].astype('category').\
    cat.rename_categories({0: 'Working', 1: 'Pensioner'})

hh_description['Female_head'] = hh_description['Female_head'].astype('category').\
    cat.rename_categories({0: 'Male_head', 1: 'Female_head'})

hh_description['Region'] = hh_description['Region'].astype('category').\
    cat.rename_categories({1: 'Genferseeregion',
                           2: 'Espace Mittelland',
                           3: 'Nordwestschweiz',
                           4: 'Zürich',
                           5: 'Ostschweiz',
                           6: 'Zentralschweiz',
                           7: 'Tessin'})

hh_description['Canton'] = hh_description['Canton'].astype('category').\
    cat.rename_categories({1: 'Kt. Zürich',
                           2: 'Kt. Bern',
                           3: 'Kt. Luzern',
                           17: 'Kt. St. Gallen',
                           19: 'Kt. Aargau',
                           21: 'Kt. Tessin',
                           22: 'Kt. Waadt',
                           25: 'Kt. Genf',
                           99: 'Other Kantons'})

hh_description['Household type / HABE income quintile group'] = \
    hh_description['Household type / HABE income quintile group'].astype('category').\
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
hh_description['Household type / Quintile group of lifetime income'] = \
    hh_description['Household type'] + hh_data['hhtype_quintile']

hh_description['Household type / Quintile group of lifetime income'] = \
    hh_description['Household type / Quintile group of lifetime income'].replace(
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
hh_description['Household type'] = hh_description['Household type'].astype('category').\
    cat.rename_categories({110: 'Single',
                           130: 'Elderly single',
                           210: 'Couple',
                           230: 'Elderly couple',
                           300: 'Single parent',
                           400: 'Parent couple',
                           900: 'Others'})

hh_description['Decile group / HH type'] = \
    hh_description['Decile group of lifetime income'].astype('str') + ' - ' +\
    hh_description['Household type'].astype('str')
# dectypeorder = []
# for decile in range(10):
#     for cat in hh_description['Household type'].cat.categories:
#         dectypeorder.append(str(decile+1)+' - '+cat)
hh_description['Decile group / Pensioner'] = \
    hh_description['Decile group of lifetime income'].astype('str') + ' - ' + \
    hh_description['Pensioner'].astype('str')
# decpensionerorder = []
# for decile in range(10):
#     for cat in hh_description['Pensioner'].cat.categories:
#         decpensionerorder.append(str(decile+1)+' - '+cat)
hh_description['Decile group / Renting'] = \
    hh_description['Decile group of lifetime income'].astype('str') + ' - ' + \
    hh_description['Renting'].astype('str')
# decrentingorder = []
# for decile in range(10):
#     for cat in hh_description['Renting'].cat.categories:
#         decrentingorder.append(str(decile+1)+' - '+cat)
hh_description['Decile group / Urbanization'] = \
    hh_description['Decile group of lifetime income'].astype('str') + ' - ' + \
    hh_description['Urbanization'].astype('str')

# decurbanizationorder = []
# for decile in range(10):
#     for cat in hh_description['Urbanization'].cat.categories:
#         decurbanizationorder.append(str(decile+1)+' - '+cat)

# obscount_deciles = hh_description['Decile group of lifetime income'].value_counts()


def reindex_df(df, weight_col):
    """expand the dataframe to prepare for resampling
    result is 1 row per count per sample"""
    df = df.reindex(df.index.repeat(df[weight_col]))
    df.reset_index(drop=True, inplace=True)
    return (df)


# Dictionary of carbon arrays inspired by
# https://stackoverflow.com/questions/33907776/create-an-array-of-dataframes-in-python
carbon_collection = {}
boxcarbon_collection = {}
for v in gwp_sums.columns:
    carbon = pd.DataFrame()
    carbon['gwp'] = gwp_sums[v]*12/1000  # tonnes per year
    carbon['cost_at_100chf'] = carbon['gwp']*100  # chf per year spent on tax
    c_rev_vol = sum(hh_data['statweights']*carbon['cost_at_100chf'])
    print('GWP_sum: ', v)
    print('Volume of carbon pricing revenue (million CHF): ', c_rev_vol/1e6)
    population = sum(hh_data['popweights'])
    print('Population (million): ', population/1e6)
    pc_refund = c_rev_vol/population
    carbon['refund_at_100chf'] = pc_refund*hh_data['npers']
    carbon['Net effect [CHF]'] = carbon['refund_at_100chf']-carbon['cost_at_100chf']
    carbon['Net effect [% of spending]'] = \
        carbon['Net effect [CHF]']/(hh_data['Spending']*12)*100
    carbon = carbon.join(hh_description)
    # Take per-person perspective in these graphs
    boxcarbon = reindex_df(carbon, 'popweights')
    # Take household perspective in these graphs
    boxcarbon = reindex_df(carbon, 'statweights')
    carbon_collection[v] = carbon
    boxcarbon_collection[v] = boxcarbon

# Sample this:
carbon_collection['Total']
boxcarbon_collection['Total']


# forplotting = pd.concat([12*habe_lca['tot_gwp']/1000,
#                          12*habe_lca['tot_gwp']/habe_lca['npers']/1000,
#                          habe_lca['tot_gwp']/hh_data['Spending'],
#                          habe_lca['statweights'].round().astype('int'),
#                          habe_lca['popweights'].round().astype('int'),
#                          12*hh_data['Spending'],
#                          12*hh_data['EquivExpPC'],
#                          12*hh_data['EquivIncPC'],
#                          12*hh_data['Spending']/hh_data['npers'],
#                          habe_lca['ExpDecile'],
#                          habe_lca['ExpQuintile'],
#                          habe_urban,
#                          hh_data['Mieterhaushalt05'],
#                          hh_data['Rentnerhaushalt05'],
#                          hh_data['FrauAlsReferenzperson05'],
#                          hh_data['Grossregion01'],
#                          hh_data['Kanton08'],
#                          hh_data['Einkommensklasse08_151617'],
#                          hh_data['Haushaltstyp14'],
#                          hh_data['HaushaltstypEinkommen14_151617'],
#                          ],
#                         axis=1)

# forplotting.columns = ['GWP [t CO2e]', 'Per capita GWP [t CO2e]',
#                        'GWP in kg CO2e per CHF',
#                        'statweights', 'popweights',
#                        'Spending', 'Equivalent spending', 'Equivalent income',
#                        'Per capita spending in CHF',
#                        'Decile group of lifetime income',
#                        'Quintile group of lifetime income',
#                        'Urbanization', 'Renting', 'Pensioner', 'Female_head',
#                        'Region', 'Canton',
#                        'Quintile group', 'Household type',
#                        'Household type / HABE income quintile group']


# Since all deciles have similar household size, per capita GWP and GWP look
# distributionally similar
# gwp_plt = sns.boxplot(x='Decile of lifetime income',
#                       y='GWP [t CO2e]',
#                       data=forboxplotting,
#                       showmeans=True,
#                       meanprops={'marker': 'o',
#                                  'markerfacecolor': 'white',
#                                  'markeredgecolor': 'black',
#                                  'markersize': '3'})
# gwp_plt.set(ylim=(0, 8000))
# gwp_plt.get_figure()


# ---------------------------------------------------------------------------------------
# Lineplots for average income and expenditure of households of GHG pricing versions
# ---------------------------------------------------------------------------------------


def plot_meanlines(dset=boxcarbon_collection['Total'],
                   xname='Decile group of lifetime income',
                   # yname='Per capita GWP [t CO2e]',
                   ymax=50,
                   # obscount=obscount_deciles,
                   filename='generic_lineplot',
                   size=(12.5*cm, 6*cm)):
    sns.set(font_scale=0.8)
    fig, ax = plt.subplots(figsize=size, tight_layout=True)
    # ax.tick_params(axis='x', rotation=90)

    grouped_costs = dset.groupby(xname)['cost_at_100chf']
    grouped_refunds = dset.groupby(xname)['refund_at_100chf']
    grouped_size = dset.groupby(xname)['size']
    grouped_spending = dset.groupby(xname)['Spending']

    mean_costs = grouped_costs.mean()
    mean_refunds = grouped_refunds.mean()
    mean_size = grouped_size.mean()
    mean_spending = grouped_spending.mean()

    plot_object = pd.concat([mean_costs, mean_refunds], axis=1)
    plot_object.columns = ['Direct cost', 'Lump-sum recycling']
    plot_object

    sns.lineplot(data=plot_object)
    # plt.errorbar(plot_object.index, plot_object['mean'], yerr=plot_object['error'],
    #              fmt='o', c='black', ecolor='black',
    #              # marker='o', markerfacecolor='white', markeredgecolor='black',
    #              markerfacecolor='white', markeredgecolor='black',
    #              markersize='3',
    #              capsize=2, capthick=1)

    yname = 'CHF per year and household'
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
    return mean_costs, mean_refunds, mean_size, mean_spending


# Generate figures for the different GHG pricing versions
for v in gwp_sums.columns:
    filename = v+'_lineplot'
    linedata = boxcarbon_collection[v]
    ym = 1000
    figsize = (6*cm, 5*cm)
    if v == 'Total':
        ym = 5000
        figsize = (12.5*cm, 6*cm)
    if not v == 'HH-ID':
        plot_meanlines(dset=linedata, ymax=ym, filename=filename, size=figsize)

# Generate the generic_lineplot for getting means for illustrative results table
(direct_cost, ls_recycling, size, spending) = plot_meanlines(ymax=5000)
type(direct_cost), type(ls_recycling)
with pd.ExcelWriter("Dezil_Beispiele.xlsx",
                    mode='a',
                    if_sheet_exists='replace') as writer:
    ls_recycling.to_excel(writer, sheet_name='Recycling (rot)')
    direct_cost.to_excel(writer, sheet_name='Direkte Kosten (blau)')
    size.to_excel(writer, sheet_name='Haushaltsgroesse')
    spending.to_excel(writer, sheet_name='Ausgaben')

# One Figure with lines from all versions of GHG pricing
# ---------------------------------------------------------------------------------------


def plot_manymeanlines(dsetdict=boxcarbon_collection,
                       xname='Decile group of lifetime income',
                       list_of_lines=gwp_sums.columns,
                       ymax=300,
                       filename='generic_lineplot',
                       size=(12.5*cm, 6*cm)):
    sns.set(font_scale=0.8)
    fig, ax = plt.subplots(figsize=size, tight_layout=True)
    # ax.tick_params(axis='x', rotation=90)

    refunds_total = dsetdict['Total'].groupby(xname)['refund_at_100chf']
    mean_refunds_total = refunds_total.mean()
    mean_of_means = mean_refunds_total.mean()
    mean_refunds_total = mean_refunds_total*100/mean_of_means
    plot_object = pd.DataFrame(
        {"Lump-sum\nrecycling": mean_refunds_total}
    )
    for v in list_of_lines:
        dset = dsetdict[v]
        grouped_costs = dset.groupby(xname)['cost_at_100chf']
        grouped_refunds = dset.groupby(xname)['refund_at_100chf']
        mean_costs = grouped_costs.mean()
        mean_refunds = grouped_refunds.mean()
        normalized_costs = mean_costs*mean_refunds_total/mean_refunds
        # plot_object.concat(normalized_costs)
        plot_object[v] = normalized_costs
        # plot_object.columns = plot_object.columns.concat(
        #     v
        # )
        # plot_object = pd.concat([mean_costs, mean_refunds], axis=1)

    plot_object.rename(columns={'Clothing and Footwear': 'Clothing and\nFootwear'},
                       inplace=True)
    sns.lineplot(data=plot_object,
                 dashes=[(2, 0), (4, 2), (2, 1), (2, 2), (1, 1), (1, 1.5), (1, 2)],
                 # palette = ['b', 'tab:orange', 'r', 'r', 'r', 'r', 'r'])
                 palette=['b', 'xkcd:orange', 'xkcd:navy blue', 'xkcd:navy blue',
                          'xkcd:forest green', 'xkcd:forest green', 'xkcd:forest green']
                 )
    sns.move_legend(ax, "upper left", bbox_to_anchor=(1, 1))
    ylabel = 'Amounts per HH [CH avg. = 100]'
    ax.set(ylim=(0, ymax), ylabel=ylabel,
           xlabel=xname,
           xticks=plot_object.index
           )
    fs = 9
    ax.set_xlabel(xname, fontsize=fs)
    ax.set_ylabel(ylabel, fontsize=fs)
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
    return plot_object


a_lineslist = (x for x in gwp_sums.columns if not x == 'HH-ID')
trash = ['Jewelry and bags', 'Sports, recreation, holidays', 'Transport (excl. Air)']
the_lineslist = (x for x in a_lineslist if x not in trash)
ploto = plot_manymeanlines(list_of_lines=the_lineslist)


# ---------------------------------------------------------------------------------------
# Whisker plots of overall outcomes of GHG pricing versions
# ---------------------------------------------------------------------------------------


def plot_differentiation(xname, filename, ymax=50, yname='Net effect [CHF]',
                         dset=boxcarbon_collection['Total'], size=(12.5*cm, 6*cm),
                         givenorder=None,
                         clr_plt=10, rotate=False, saturation=0.75):
    sns.set(font_scale=0.8)
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
                         hue=xname,
                         legend=False,
                         showmeans=True,
                         saturation=saturation,
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
    boxplt.set(ylim=(-ymax, ymax))
    fs = 9
    ax.set_xlabel(xname, fontsize=fs)
    ax.set_ylabel(yname, fontsize=fs)
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


# Whole population (one single whisker-box)
plot_differentiation(xname=None,
                     yname='Net effect [CHF]',
                     filename='impacts_CH',
                     ymax=5000, size=(6*cm, 6*cm))

# ABSOLUTE net effect by INCOME
plot_differentiation(xname='Decile group of lifetime income',
                     yname='Net effect [CHF]',
                     filename='impacts_income',
                     ymax=5000, size=(12.5*cm, 6*cm))

# Systematically go through all versions for RELATIVE net effect by INCOME
# ---------------------------------------------------------------------------------------

for v in gwp_sums.columns:
    filename = 'v_'+v+'_rel_impacts_income'
    boxdata = boxcarbon_collection[v]
    ym = 5
    figsize = (6*cm, 5*cm)
    if v == 'Total':
        ym = 15
        figsize = (12.5*cm, 6*cm)
    if not v == 'HH-ID':
        plot_differentiation(xname='Decile group of lifetime income',
                             yname='Net effect [% of spending]',
                             filename=filename,
                             ymax=ym,
                             dset=boxdata,
                             size=figsize,
                             saturation=0
                             )

# Some additional illustrative analyses
# ---------------------------------------------------------------------------------------
# Not so interesting?
plot_differentiation(xname='Female_head', filename='Female_carbonbox',
                     yname='Net effect [% of spending]', ymax=15,
                     size=(6*cm, 12*cm),
                     rotate=True)
plot_differentiation(xname='Pensioner', filename='Pensioner_carbonbox',
                     yname='Net effect [% of spending]', ymax=15,
                     size=(6*cm, 12*cm), clr_plt=2,
                     rotate=True)
plot_differentiation(xname='Region', filename='Region_carbonbox',
                     yname='Net effect [% of spending]', ymax=15,
                     size=(8*cm, 12*cm),
                     rotate=True)
plot_differentiation(xname='Quintile group', filename='Quintile_carbonbox',
                     yname='Net effect [% of spending]', ymax=15,
                     size=(8*cm, 12*cm))
# Rather interesting
plot_differentiation(xname='Urbanization', filename='Urbanization_carbonbox',
                     yname='Net effect [% of spending]', ymax=15,
                     size=(6*cm, 12*cm), clr_plt=3,
                     rotate=True)
plot_differentiation(xname='Renting', filename='Renting_carbonbox',
                     yname='Net effect [% of spending]', ymax=15,
                     size=(6*cm, 12*cm), clr_plt=2,
                     rotate=True)
plot_differentiation(xname='Canton', filename='Canton_carbonbox',
                     yname='Net effect [% of spending]', ymax=15,
                     size=(8*cm, 12*cm),
                     rotate=True)
plot_differentiation(xname='Household type', filename='hh_type_carbonbox',
                     yname='Net effect [% of spending]', ymax=15,
                     size=(8*cm, 12*cm), clr_plt=7,
                     rotate=True)
