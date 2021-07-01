#!/usr/bin/env python3.8
# coding=utf-8

from matplotlib import pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np
import os
# muzete pridat libovolnou zakladni knihovnu ci knihovnu predstavenou na prednaskach
# dalsi knihovny pak na dotaz

# Ukol 1: nacteni dat
def get_dataframe(filename: str, verbose: bool = False) -> pd.DataFrame:
    """[Gets dataframe from file and converts its types to save memory]

    Args:
        filename (str): [file containing data to be converted]
        verbose (bool, optional): [When True prints size of data before and after conversion]. Defaults to False.

    Returns:
        pd.DataFrame: [Data from filename converted to DataFrame]
    """
    df = pd.read_pickle(filename)
    df["date"] = df["p2a"].apply(lambda x: x)
    df1 = pd.DataFrame()
    for column in df:
        if column == "region" or column == "p13a" or column == "p13b" or column == "p13c" or column == "p1":
            df1[column] = df[column]
        else:
            df1[column] = df[column].astype("category")
    if verbose:
        print("orig_size={:.1f} MB".format(df.memory_usage(deep=True).sum() / 1048576))
        print("new_size={:.1f} MB".format(df1.memory_usage(deep=True).sum() / 1048576))
    return df1

# Ukol 2: následky nehod v jednotlivých regionech
def plot_conseq(df: pd.DataFrame, fig_location: str = None,
                show_figure: bool = False):
    """[Plots graphs showing consenquences of car accidents divied by regions]

    Args:
        df (pd.DataFrame): [Data of car accidents in Czech Republic since the year 2016]
        fig_location (str, optional): [Saves graphs as image file]. Defaults to None.
        show_figure (bool, optional): [When True plots graphs on screen]. Defaults to False.
    """
    #Create dataframe containing only columns needed for this function
    df1 = pd.DataFrame()
    df1 = df.groupby("region")\
        .agg({"p13a":"sum","p13b":"sum","p13c":"sum","p1":"count"})\
        .sort_values(by="p1",ascending=False)
    
    #Set Figure and subplots
    fig,axes = plt.subplots(nrows=4,constrained_layout= True , figsize=(8,11))
    ax1,ax2,ax3,ax4 = axes

    #Set Background colors for subplots
    ax1.set_facecolor((0.9,0.95,1))
    ax2.set_facecolor((0.9,0.95,1))
    ax3.set_facecolor((0.9,0.95,1))
    ax4.set_facecolor((0.9,0.95,1))

    #Plot DataFrames onto subplots 
    df1["p13a"].plot(kind="bar",ax=ax1,title="Úmrtí",ylabel="Počet",facecolor=(0.2,0.2,0.2),xlabel="",xticks=[])
    df1["p13b"].plot(kind="bar",ax=ax2,title="Těžce ranění",ylabel="Počet",facecolor=(1,0.2,0.2),xlabel="",xticks=[])
    df1["p13c"].plot(kind="bar",ax=ax3,title="Lehce ranění",ylabel="Počet",facecolor=(0.2,1,0.2),xlabel="",xticks=[])
    df1["p1"].plot(kind="bar",ax=ax4,title="Celkem nehod",ylabel="Počet",facecolor=(0.2,0.2,1),xlabel="",rot=0)

    #Set grid for Y-axis in subplots
    ax1.grid(which="major",axis="y",color=((0.8,0.8,1)),linewidth=1)
    ax1.set_axisbelow(True)
    ax2.grid(which="major",axis="y",color=((0.8,0.8,1)),linewidth=1)
    ax2.set_axisbelow(True)
    ax3.grid(which="major",axis="y",color=((0.8,0.8,1)),linewidth=1)
    ax3.set_axisbelow(True)
    ax4.grid(which="major",axis="y",color=((0.8,0.8,1)),linewidth=1)
    ax4.set_axisbelow(True) 


    """When not None saves graph into chosen folder"""
    if fig_location is not None:
        plt.savefig(fig_location)
    """If show_figure flag is True plots data into window"""
    if show_figure:
        plt.show()

# Ukol3: příčina nehody a škoda
def plot_damage(df: pd.DataFrame, fig_location: str = None,
                show_figure: bool = False):
    """[Plots graphs showing financial casualities of car accidents in regions: PHA,JHC,VYS,PAK]

    Args:
        df (pd.DataFrame): [Data of car accidents in Czech Republic since the year 2016]
        fig_location (str, optional): [Saves graphs as image file]. Defaults to None.
        show_figure (bool, optional): [When True plots graphs on screen]. Defaults to False.
    """   
    #create DataFrame containing only needed columns for this function, also separate data only from 4 needed regions
    dftemp = pd.DataFrame()
    dftemp["region"] = df["region"]
    dftemp["money"] = df["p53"]
    dftemp["cause"] = df["p12"]
    dftemp = dftemp[(dftemp["region"] == "PHA") | (dftemp["region"] == "JHC") | (dftemp["region"] == "VYS") | (dftemp["region"] == "PAK")]
    
    #Cut money data into 5 groups
    dftemp["money"]= pd.cut(dftemp["money"],[0,500,2000,5000,10000,float("inf")],labels=["<50","50-200","200-500","500-1000",">1000"],include_lowest=True)
    
    #Convert int values of car accident reasons into string values
    bins = pd.IntervalIndex.from_tuples([(99,100), (200,209), (300,311), (400,414), (500,516), (600,615)])
    tempcause = pd.cut(dftemp["cause"].to_list(),bins)
    tempcause.categories = ["nezaviněná řidičem","nepřiměřená rychlost jízdy","nesprávné předjíždění","nedání přednosti v jízdě",
    "nesprávný způsob jízdy","technická závada vozidla"]
    dftemp["cause"] = tempcause

    #Pivot Dataframe into separate DataFrames for each region
    dfPHA = dftemp[dftemp["region"] == "PHA"].pivot_table(index="money",columns="cause",aggfunc="count")
    dfJHC = dftemp[dftemp["region"] == "JHC"].pivot_table(index="money",columns="cause",aggfunc="count")
    dfVYS = dftemp[dftemp["region"] == "VYS"].pivot_table(index="money",columns="cause",aggfunc="count")
    dfPAK = dftemp[dftemp["region"] == "PAK"].pivot_table(index="money",columns="cause",aggfunc="count")
    
    #Create Figure and subplots
    fig,axes = plt.subplots(nrows=2,ncols=2,constrained_layout= True , figsize=(11,8))
    (ax1,ax2),(ax3,ax4) = axes

    #Set background colors for subplots
    ax1.set_facecolor((0.9,0.95,1))
    ax2.set_facecolor((0.9,0.95,1))
    ax3.set_facecolor((0.9,0.95,1))
    ax4.set_facecolor((0.9,0.95,1))

    #Plot DataFrames
    dfPHA.plot(kind="bar",ax=ax1,logy=True,title="PHA",xlabel="Škoda [tisíc Kč]",rot=0,ylabel="Počet",legend= False)
    dfJHC.plot(kind="bar",ax=ax2,logy=True,title="JHC",xlabel="Škoda [tisíc Kč]",rot=0,ylabel="Počet",legend= False)
    dfVYS.plot(kind="bar",ax=ax3,logy=True,title="VYS",xlabel="Škoda [tisíc Kč]",rot=0,ylabel="Počet",legend= False)
    dfPAK.plot(kind="bar",ax=ax4,logy=True,title="PAK",xlabel="Škoda [tisíc Kč]",rot=0,ylabel="Počet")

    #Set Grid for Y axis in subplots
    ax1.grid(which="major",axis="y",color=("white"),linewidth=1)
    ax1.set_axisbelow(True)
    ax1.minorticks_off()
    ax2.grid(which="major",axis="y",color=("white"),linewidth=1)
    ax2.set_axisbelow(True)
    ax2.minorticks_off()
    ax3.grid(which="major",axis="y",color=("white"),linewidth=1)
    ax3.set_axisbelow(True)
    ax3.minorticks_off()
    ax4.grid(which="major",axis="y",color=("white"),linewidth=1)
    ax4.set_axisbelow(True)
    ax4.minorticks_off()

    #Set legend
    handles, labels = ax1.get_legend_handles_labels()
    ax4.legend(handles, ("nezaviněná řidičem","nepřiměřená rychlost jízdy","nesprávné předjíždění","nedání přednosti v jízdě",
    "nesprávný způsob jízdy","technická závada vozidla"), loc='upper right',title="Příčina nehody", bbox_to_anchor=(1.2, 1.2))


    """When not None saves graph into chosen folder"""
    if fig_location is not None:
        plt.savefig(fig_location)
    """If show_figure flag is True plots data into window"""
    if show_figure:
        plt.show()

# Ukol 4: povrch vozovky
def plot_surface(df: pd.DataFrame, fig_location: str = None,
                 show_figure: bool = False):
    """[Plots graphs showing weather conditions in car accidents in regions: PHA,JHC,VYS,PAK]

    Args:
        df (pd.DataFrame): [Data of car accidents in Czech Republic since the year 2016]
        fig_location (str, optional): [Saves graphs as image file]. Defaults to None.
        show_figure (bool, optional): [When True plots graphs on screen]. Defaults to False.
    """

    #create DataFrame containing only needed columns for this function, also separate data only from 4 needed regions
    dftemp = pd.DataFrame()
    dftemp["region"] = df["region"]
    dftemp["roadstate"] = df["p16"]
    #convert date column values into datetime months
    dftemp["date"] = df["date"].astype('datetime64[M]')
    dftemp = dftemp[(dftemp["region"] == "PHA") | (dftemp["region"] == "JHC") | (dftemp["region"] == "VYS") | (dftemp["region"] == "PAK")]

    #Pivot DataFrames for each separate region, set NaN values to 0
    dfPHA = dftemp[dftemp["region"] == "PHA"].pivot_table(index="date",columns="roadstate",aggfunc="count").fillna(0)
    dfJHC = dftemp[dftemp["region"] == "JHC"].pivot_table(index="date",columns="roadstate",aggfunc="count").fillna(0)
    dfVYS = dftemp[dftemp["region"] == "VYS"].pivot_table(index="date",columns="roadstate",aggfunc="count").fillna(0)
    dfPAK = dftemp[dftemp["region"] == "PAK"].pivot_table(index="date",columns="roadstate",aggfunc="count").fillna(0)

    #Create Figure and subplots
    fig,axes = plt.subplots(nrows=2,ncols=2,constrained_layout= True , figsize=(13,7))
    (ax1,ax2),(ax3,ax4) = axes
    
    #Set background colors for subplots
    ax1.set_facecolor((0.9,0.95,1))
    ax2.set_facecolor((0.9,0.95,1))
    ax3.set_facecolor((0.9,0.95,1))
    ax4.set_facecolor((0.9,0.95,1))

    #Plot DataFrames of separate regions into subplots
    dfPHA.plot(kind="line",ax=ax1,title="PHA",rot=0,ylabel="Počet nehod",legend= False,xlabel="")
    dfJHC.plot(kind="line",ax=ax2,title="JHC",rot=0,legend= False,xlabel="")
    dfVYS.plot(kind="line",ax=ax3,title="VYS",xlabel="Datum vzniku nehody",rot=0,ylabel="Počet nehod",legend= False)
    dfPAK.plot(kind="line",ax=ax4,title="PAK",xlabel="Datum vzniku nehody",rot=0,legend= False)
    
    #Set Grid for both axis in subplots
    ax1.grid(which="major",axis="both",color=("white"),linewidth=1)
    ax1.set_axisbelow(True)
    ax1.minorticks_off()
    ax2.grid(which="major",axis="both",color=("white"),linewidth=1)
    ax2.set_axisbelow(True)
    ax2.minorticks_off()
    ax3.grid(which="major",axis="both",color=("white"),linewidth=1)
    ax3.set_axisbelow(True)
    ax3.minorticks_off()
    ax4.grid(which="major",axis="both",color=("white"),linewidth=1)
    ax4.set_axisbelow(True)
    ax4.minorticks_off()

    #Set Legend
    handles, labels = ax1.get_legend_handles_labels()
    ax4.legend(handles, ("jiný stav","suchý,neznečistěný","suchý,znečistěný","mokrý","bláto","náledí,ujetý sníh - posypané",
    "náledí,ujetý sníh - neposypané","rozlitý olej, nafta a pod.","souvislý sníh","náhlá změna stavu"), loc='upper right',
    title="Stav vozovky", bbox_to_anchor=(1.6, 1.3))


    """When not None saves graph into chosen folder"""
    if fig_location is not None:
        plt.savefig(fig_location)
    """If show_figure flag is True plots data into window"""
    if show_figure:
        plt.show()


if __name__ == "__main__":
    pass
    # zde je ukazka pouziti, tuto cast muzete modifikovat podle libosti
    # skript nebude pri testovani pousten primo, ale budou volany konkreni ¨
    # funkce.
    df = get_dataframe("accidents.pkl.gz",True)
    plot_conseq(df, fig_location="01_nasledky.png", show_figure=True)
    plot_damage(df, "02_priciny.png")
    plot_surface(df, "03_stav.png")
