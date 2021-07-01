#!/usr/bin/env python3.8
# coding=utf-8

from matplotlib import pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np
import os

def get_dataframe(filename: str) -> pd.DataFrame:
    """[Gets dataframe from file and converts its types to save memory]

    Args:
        filename (str): [file containing data to be converted]
        verbose (bool, optional): [When True prints size of data before and after conversion]. Defaults to False.

    Returns:
        pd.DataFrame: [Data from filename converted to DataFrame]
    """
    df = pd.read_pickle(filename)
    df1 = pd.DataFrame()
    df1["date"] = df["p2a"].apply(lambda x: x)
    for column in df:
        if column == "region" or column == "p13a" or column == "p13b" or column == "p13c" or column == "p1" or column == "p11":
            df1[column] = df[column]
        else:
            df1[column] = df[column].astype("category")
    return df1

def get_percentage(a,b):
    """[Calculates percentage out of 2 values]
    
    Args:
        a : [int value of item]
        b : [int value of max]
        
    Returns:
        float: [value of percentage]"""
    temp = a/b
    return round(temp * 100,2)

def doc(df: pd.DataFrame, fig_location: str = None,
                 show_figure: bool = False):
    """[Plots graphs showing percentages of accidents caused by alcohol and drugs]

    Args:
        df (pd.DataFrame): [Data of car accidents in Czech Republic since the year 2016]
        fig_location (str, optional): [Saves graphs as image file]. Defaults to None.
        show_figure (bool, optional): [When True plots graphs on screen]. Defaults to False.
    """
    #create DataFrame containing only needed columns for this function, also separate data only from 4 needed regions
    dftemp = pd.DataFrame()
    dftemp["nehody"] = df["p11"]
    
    #convert date column values into datetime years
    dftemp["date"] = df["date"].astype('datetime64[Y]')
    
    #separate values by ammount of alcohol and drugs 
    dftriezvo = dftemp[(dftemp["nehody"] == 0) | (dftemp["nehody"] == 2)]
    dfnehody = dftemp[(dftemp["nehody"] != 0) & (dftemp["nehody"] != 2)]
    dfdrogy = dfnehody[(dfnehody["nehody"] == 4) |(dfnehody["nehody"] == 5)]
    dfalk_low = dfnehody[(dfnehody["nehody"] == 1) |(dfnehody["nehody"] == 3)]
    dfalk_mid = dfnehody[(dfnehody["nehody"] == 6) |(dfnehody["nehody"] == 7)]
    dfalk_high = dfnehody[(dfnehody["nehody"] == 8) |(dfnehody["nehody"] == 9)]
    
    #agregate separated values
    dftemp = dftemp.groupby(by=["date"]).count()
    dftriezvo = dftriezvo.groupby(by=["date"]).count()
    dfnehody = dfnehody.groupby(by=["date"]).count()
    dfdrogy = dfdrogy.groupby(by=["date"]).count()
    dfalk_low = dfalk_low.groupby(by=["date"]).count()
    dfalk_mid = dfalk_mid.groupby(by=["date"]).count()
    dfalk_high = dfalk_high.groupby(by=["date"]).count()
    
    #insert values as columns
    dftemp["triezvo"] = dftriezvo["nehody"]
    dftemp["podvplyvom"] = dfnehody["nehody"]
    dftemp["alk<0.5"] = dfalk_low["nehody"]
    dftemp["alk>0.5<1.0"] = dfalk_mid["nehody"]
    dftemp["alk>1.0"] = dfalk_high["nehody"]
    dftemp["drogy"] = dfdrogy["nehody"]
    
    #reset index to date and cut months and days values
    dftemp = dftemp.reset_index()
    dftemp["date"] = ["2016","2017","2018","2019","2020"]
    dftemp = dftemp.set_index("date")
    
    #create lists to store percentage values into
    percentage = []
    alklow_percentage = []
    alkmid_percentage = []
    alkhigh_percentage = []
    drugs_percentage = []
    
    #calculate percentage values for every year
    for index,row in dftemp.iterrows():
        percentage.append(get_percentage(row["podvplyvom"],row["nehody"]))
        alklow_percentage.append(get_percentage(row["alk<0.5"],row["podvplyvom"]))
        alkmid_percentage.append(get_percentage(row["alk>0.5<1.0"],row["podvplyvom"]))
        alkhigh_percentage.append(get_percentage(row["alk>1.0"],row["podvplyvom"]))
        drugs_percentage.append(get_percentage(row["drogy"],row["podvplyvom"]))
   
    #create dataframe for percentage values
    dfpercentage = pd.DataFrame(list(zip(percentage,alklow_percentage,alkmid_percentage,alkhigh_percentage,drugs_percentage)),
                                index=["2016","2017","2018","2019","2020"],
                               columns=["pod vplyvom %","alk<0.5 %","0.5 < alk <1.0 %","alk>1.0 %","drogy %"])
    
    #plot percentage values 
    dfpercentage.plot(kind="bar",rot=0,y=["alk<0.5 %","0.5 < alk <1.0 %","alk>1.0 %","drogy %"])
    
    #print tables of amount of accidents and percentages of accidents
    print("Počet nehod od 2016 po 2020:\n")
    print(dftemp)
    print("\nPercento nehod od 2016 po 2020:\n")
    print(dfpercentage)
    
    #When not None saves graph into chosen folder
    if fig_location is not None:
        plt.savefig(fig_location)
    #If show_figure flag is True plots data into window
    if show_figure:
        plt.show()

if __name__ == "__main__":
    pass
    df = get_dataframe("accidents.pkl.gz")
    doc(df,show_figure=True,fig_location="fig.png")




