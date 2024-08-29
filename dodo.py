# from doit.action import CmdAction
import shutil
import os
from doit.tools import run_once


def task_setupDIRs():
    """Make sure all necessary directories exist."""

    def make_some_dirs():
        for dir in ['figures',
                    'intermediate_files',
                    'data-HABE151617']:
            if not os.access(dir, os.F_OK):
                os.mkdir(dir)

    def ask_for_HABE():
        input("Place data files (HABE data files from the FSO)\n" +
              "HABE151617_Wohngemeinden.txt\n" +
              "HABE151617_Standard.txt\n" +
              "HABE151617_Konsumgueter.txt\n" +
              "HABE151617_Mengen.txt\n" +
              "HABE151617_Mengen.txt\n" +
              "HABE151617_Ausgaben.txt\n" +
              "in ./data-HABE151617,\n" +
              "then press ENTER.")

    return {
        'actions': [make_some_dirs,
                    ask_for_HABE],
        'verbosity': 2,
        'uptodate': [run_once],
    }


def task_imputehabe():
    """Run python scripts for imputing missing values in HABE and writing .csv files"""
    return {
        'file_dep': ['python/1_Calculate_demand_per_household.py',
                     'data-HABE151617/HABE151617_Ausgaben.txt',
                     'data-HABE151617/HABE151617_Konsumgueter.txt',
                     'data-HABE151617/HABE151617_Mengen.txt',
                     'data-HABE151617/HABE151617_Standard.txt',
                     'data-elcom_froemelt/Electricity_prices_per_canton_2015-2017.xlsx',
                     'data-elcom_froemelt/Froemelt_et_al_2018_tables.xlsx'],
        'targets': ['intermediate_files/habe20152017_hh_prepared_imputed.csv',
                    'intermediate_files/hh_properties.csv',],
        'actions': ['python python/1_Calculate_demand_per_household.py'],
    }
# I should think about updating excel links. If only by instructing the user to do so...


def task_integrateMZMV():
    """Run python scripts for integrating data from Microcensus to HABE"""
    return {
        'file_dep': ['python/1bis_Integrate_HABE_MZMV.py',
                     'intermediate_files/habe20152017_hh_prepared_imputed.csv',
                     'intermediate_files/hh_properties.csv',
                     'data-MZMV/read_MZMV.xlsx',
                     'data-MZMV/su-d-11.04.03-MZ-2015-T01.xls'],
        'targets': ['intermediate_files/habe20152017_imputed_withMZkm.csv'],
        'actions': ['python python/1bis_Integrate_HABE_MZMV.py'],
    }


# def task_copy_aggregations():
#     """Copy the repo's version of the aggregations file to a working copy."""

#     def copy_agg(targets):
#         shutil.copy('config-aggregation/aggregations_git.xlsx', targets[0])

#     return {
#         'actions': [copy_agg],
#         'targets': ['config-aggregation/aggregations.xlsx'],
#         'file_dep': ['config-aggregation/aggregations_git.xlsx']
#         }


def task_link_HABEtoLCA():
    """Run python scripts for combining HABE and LCA"""

    def copy_agg(targets):
        shutil.copy('config-aggregation/aggregations_git.xlsx', targets[0])

    def printmessage():
        input("./config-aggregation/aggregations.xlsx has been edited. " +
              "To make sure that the edits from different sources match, " +
              "open the file, open the sheet 'check_gwp_list', " +
              "and make sure that all entries in line 5 indicate " +
              "consistent categories across different sources. " +
              "You may want to edit " +
              "'./config-aggregation/aggregations_git.xlsx' or " +
              "'./python/2_Link_HABE_LCA.py' " +
              "and rerun 'doit' if that is not the case.\n" +
              "Press ENTER when done.")

    return {
        'file_dep': ['intermediate_files/habe20152017_imputed_withMZkm.csv',
                     'intermediate_files/hh_properties.csv',
                     'python/2_Link_HABE_LCA.py',
                     'config-aggregation/aggregations_git.xlsx',
                     ],
        'targets': ['config-aggregation/aggregations.xlsx',
                    'intermediate_files/habe_lca.csv',
                    'intermediate_files/gwp_dict.pkl',],
        'verbosity': 2,
        'actions': [copy_agg,
                    'python python/2_Link_HABE_LCA.py',
                    printmessage],
    }


def task_lookat_HABE_LCA():
    """Run python script for illustrating HABE and LCA"""
    return {
        'file_dep': ['data-HABE151617/HABE151617_Standard.txt',
                     'data-HABE151617/HABE151617_Wohngemeinden.txt',
                     'config-aggregation/aggregations.xlsx',
                     'intermediate_files/habe_lca.csv',
                     'python/3_Lookat_HABE_LCA.py',],
        # For targets, I could make a long list of figures, but I think
        # that it's enought to only list one for keeping the doit algorithm
        # working as expected:
        'targets': ['figures/gwp_cat.pdf'],
        'actions': ['python python/3_Lookat_HABE_LCA.py'],
    }


def task_eval_carbonpricing():
    """Run python script for evaluating carbon pricing"""


    def copy_bsp(targets):
        shutil.copy('Dezil_Beispiele_git.xlsx', 'Dezil_Beispiele.xlsx')


    return {
        'file_dep': ['data-HABE151617/HABE151617_Standard.txt',
                     'data-HABE151617/HABE151617_Wohngemeinden.txt',
                     'intermediate_files/habe_lca.csv',
                     'python/4_Assess_CPrice.py',
                     'Dezil_Beispiele_git.xlsx'
                     ],
        # For targets, I could make a long list of figures, but I think
        # that it's enought to only list one for keeping the doit algorithm
        # working as expected:
        'targets': ['figures/hh_type_carbonbox.pdf'],
        'actions': [copy_bsp,
                    'python python/4_Assess_CPrice.py'],
    }


def task_spellcheck_paper():
    """Spell-check the paper"""
    return {
        'file_dep': ['doc/paper.tex'],
        'targets': ['doc/aspell.out'],
        # Use interactive mode to correct spelling mistakes and additionally
        # use list mode to get a file for use as a 'target' in the task.
        'verbosity': 2,
        'actions': ['aspell -t -l en_GB-ize -c doc/paper.tex',
                    'aspell -t -l en_GB-ize list < doc/paper.tex > doc/aspell.out'],
    }


def task_compile_tikz():
    """Compile the paper's TikZ figures"""
    return {
        'file_dep': ['doc/paper_tikz.tex'],
        'targets': ['doc/paper_tikz.pdf'],
        'actions': ['pdflatex -output-directory=doc doc/paper_tikz.tex'],
    }


def task_compile_paper():
    """Compile the paper"""
    return {
        'file_dep': ['doc/paper.tex'],
        'targets': ['doc/paper.pdf'],
        'actions': ['pdflatex -output-directory=doc doc/paper.tex',
                    'cd doc && biber paper && cd ..',
                    'pdflatex -output-directory=doc doc/paper.tex',
                    'pdflatex -output-directory=doc doc/paper.tex'],
    }
