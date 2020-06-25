# Plot COVID-19  
__author__ = 'Jose Cubero'
__version__ = '1.0.0'

# python libs
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# local libs
import parse_covid_data as pcov

debug_lib = True
world_population_df = pcov.get_world_pop()
world_confirmed_df = pcov.get_clean_covid_data('confirmed')
world_deaths_df    = pcov.get_clean_covid_data('deaths')
world_recovered_df = pcov.get_clean_covid_data('recovered')

# to be run when used as lib. Load all DFs, parse csvs once.
# def load_data?
    # TODO: check is this is the right approach??
    ##### Fill in Covid-19 raw data frames
    # world_population_df = pcov.get_world_pop()

    # world_confirmed_df = pcov.get_clean_covid_data('confirmed')
    # world_deaths_df    = pcov.get_clean_covid_data('deaths')
    # world_recovered_df = pcov.get_clean_covid_data('recovered')


region_list = ["Northern America",
               "Central America",
               "Caribbean",
               "South America",
               "Northern Europe",
               "Western Europe",
               "Southern Europe",
               "Eastern Europe",
               "Northern Africa",
               "Western Africa",
               "Eastern Africa",
               "Middle Africa",
               "Southern Africa",
               "Western Asia",
               "Central Asia",
               "Eastern Asia",
               "Southern Asia",
               "South-eastern Asia",
               "Australia and New Zealand",
               "Melanesia",
            ]

    # cat_reg_type = pd.CategoricalDtype(categories=region_list, ordered=True)

    # df['UN_Region'] = df['UN_Region'].astype(cat_reg_type)
    # #df['Continent'] = df['Continent'].astype(cat_type)


def get_region_country_dict():

    dictX = {}
    grouped_data = world_population_df.groupby(by= "UN_Region")
    
    # Find countries with more infections, per region
    for region, dfx in grouped_data:

        dictX[region] = dfx.index.tolist()
    
    return dictX

def get_region_list():

    listX = []
    grouped_data = world_population_df.groupby(by= "UN_Region")
    
    # Find countries with more infections, per region
    for region, dfx in grouped_data:
        print(str(region) + ": " + str(len(dfx.index.tolist())) )
        listX.append(region)
    
    return listX

def plot_covid_6vars(country_list=[], region=""):

    if(country_list == []):
        print("plot_covid_6vars: received empty list invalid empty list! exiting..")
        exit(1)
    
    # flags = []
    # for idx in range(len(country_list)):
    #     if country_list[idx] not in world_confirmed_df.index.tolist():
    #         flags.append(idx)

    for idx in country_list:
        if idx not in world_confirmed_df.index.tolist():
            country_list.remove(idx)

    #country_list.pop()
    
    # print(flags)

    if(debug_lib):
        print("Selected countries: ")
        print(country_list)
        print("\n")

    exit(0)

    # Filter World population info
    # population_df = pcov.get_world_pop(country_list)
    population_df = world_population_df.loc[ country_list, :]

    ##### Fill in Covid-19 raw data frames
    # confirmed_df = pcov.get_clean_covid_data('confirmed', country_list)
    confirmed_df = world_confirmed_df.loc[ country_list, :]
    # deaths_df    = pcov.get_clean_covid_data('deaths', country_list)
    deaths_df = world_deaths_df.loc[ country_list, :]
    #recovered_df = pcov.get_clean_covid_data('recovered', country_list)
    recovered_df = world_recovered_df.loc[ country_list, :]

    ##### Create derived Covid-19 data 
    # Normalized confirmed cases (per 1000 inhabitants)
    confirmed_norm_df = (confirmed_df.div(population_df['Population_2019'], axis=0))*1000
    # Active cases, (per 1000 inhabitants)
    active_norm_df = confirmed_df - recovered_df - deaths_df
    active_norm_df = (active_norm_df.div(population_df['Population_2019'], axis=0))*1000
    # Daily Increase of confirmed cases (per 1000 inhabitants, moving average)
    # confirmed_delta_df = confirmed_df.diff(axis=1)
    # confirmed_norm_delta_df = confirmed_norm_df.diff(axis=1)
    confirmed_norm_delta_df = confirmed_norm_df.diff(axis=1).rolling(axis=1, window=8).mean()
    # Deaths per confirmed cases. (Mortality Rate %)
    death_rate_df = (deaths_df / confirmed_df) *100

    #### Plotting the data 
    fig, axs = plt.subplots(2, 3, sharex=True,
                            figsize = (17,10),
                            constrained_layout=True)
                        #  gridspec_kw={'hspace': 0.15, 'wspace': 0.15},

    # Plot the data-frames
    confirmed_df.T.plot(ax=axs[0,0], title='Total Confirmed Cases')
    confirmed_norm_df.T.plot(ax=axs[1,0], title='Confirmed Cases norm (per 1k inhabitants)')
    
    active_norm_df.T.plot(ax=axs[0,1], title='Active Cases norm')
    confirmed_norm_delta_df.T.plot(ax=axs[1,1], title='Daily New Confirmed norm, Smoothed')

    deaths_df.T.plot(ax=axs[0,2], title='Total Deaths')
    death_rate_df.T.plot(ax=axs[1,2], title='Death-rate (%) = Net Deaths / Net Cases')
    
    return fig

# This is executed when run from the command line
if __name__ == "__main__":
    # Create the parser
    my_parser = argparse.ArgumentParser(prog='covid_main',
        #usage='%(prog)s -i input [-o output]',
        description='Read latest data and print top 5')

    my_parser.add_argument('-v',
        '--verbose',
        action='store_true')
    
    group = my_parser.add_mutually_exclusive_group(required=True)

    group.add_argument('-c',
        '--country',
        metavar='Country',
        type=str,
        action='store',
        help='Name of the desired country')
    
    group.add_argument('-cl',
        '--country_list',
        metavar='PathToListFile',
        type=str,
        action='store',
        help='File containing a list of countries, one per line')

    # my_parser.add_argument('oFilePath',
    #     metavar='outputFilePath',
    #     type=str,
    #     #required=True,
    #     #action='store',
    #     #default="output.txt",
    #     help='the path to new output file')    

    # Run Argument parser
    args = my_parser.parse_args()

    if args.verbose:
        print("Done with argument parser")
        print("Arguments:\n")
        print(vars(args))
        debug_lib = True
        print("\n")
    
    country_list = []
    if (args.country != None):
        country_list.append(args.country)
    else:
        with open(args.country_list) as clf:
            country_list = [line.rstrip() for line in clf]

    # Preparation: close matplotlib windows..
    plt.close('all')
    # TODO: check if this would be a better approach
    # load_covid_world_data()

    #Run Main function (generates plots)
    plot_covid_6vars(country_list)

    #Show the plots
    plt.show()

    #Exit, no errors
    exit(0)