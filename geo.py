#!/usr/bin/python3.8
# coding=utf-8
import pandas as pd
import geopandas
import matplotlib.pyplot as plt
import contextily as ctx
import sklearn.cluster
import numpy as np
# muzeze pridat vlastni knihovny



def make_geo(df: pd.DataFrame) -> geopandas.GeoDataFrame:
    """[Converts DataFrame into geoDataFrame, excludes invalid items]

    Args:
        df (pd.DataFrame): [DataFrame containing data about accidents in CR since 2016]

    Returns:
        geopandas.GeoDataFrame: [Data from DataFrame converted into GeoDataFrame]
    """
    #exclude invalid data
    df = df[df['d'].notna()]
    df = df[df['e'].notna()]
    
    #convert DataFrame to GeoDataFrame, set Coordinate Reference System
    gdf = geopandas.GeoDataFrame(
        df, geometry=geopandas.points_from_xy(df.d, df.e), crs="EPSG:5514")
    
    return gdf

def plot_geo(gdf: geopandas.GeoDataFrame, fig_location: str = None,
             show_figure: bool = False):
    """[Plots graphs showing accidents in region Vysocina that happened in and outside cities]

    Args:
        gdf (geopandas.GeoDataFrame): [Data of car accidents in Czech Republic since the year 2016]
        fig_location (str, optional): [Saves graphs as image file]. Defaults to None.
        show_figure (bool, optional): [When True plots graphs on screen]. Defaults to False.
    """ 
    
    #create plot
    fig, axes = plt.subplots(1, 2, figsize=(16, 12))
    ax1,ax2 = axes
    
    #plot data only from desired region and accidents inside cities
    gdf[ (gdf["region"] == "VYS") & (gdf["p5a"] == 1)].plot(ax=ax1,markersize= 0.3)
    ax1.axis('off')
    ax1.set_title("Nehody v kraji Vysočina: v obci")
    
    #add background map
    ctx.add_basemap(ax1, crs=gdf.crs.to_string(), source=ctx.providers.Stamen.TonerLite,
    alpha=0.9)
    
    
    #plot data only from desired region and accidents outside cities
    gdf[ (gdf["region"] == "VYS") & (gdf["p5a"] == 2)].plot(ax=ax2,markersize= 0.3)
    ax2.set_title("Nehody v kraji Vysočina: mimo obec")
    ax2.axis('off')
    
    #add background map
    ctx.add_basemap(ax2, crs=gdf.crs.to_string(), source=ctx.providers.Stamen.TonerLite,
    alpha=0.9)
    
    #When not None saves graph into chosen folder
    if fig_location is not None:
        plt.savefig(fig_location)
    #If show_figure flag is True plots data into window
    if show_figure:
        plt.show()




def plot_cluster(gdf: geopandas.GeoDataFrame, fig_location: str = None,
                 show_figure: bool = False):
    """[Plots graphs showing clustered accidents in Vysocina region]

    Args:
        gdf (geopandas.GeoDataFrame): [Data of car accidents in Czech Republic since the year 2016]
        fig_location (str, optional): [Saves graphs as image file]. Defaults to None.
        show_figure (bool, optional): [When True plots graphs on screen]. Defaults to False.
    """ 
    
    #create plot
    
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    
    #separate data only from desired region
    gdf = gdf[(gdf["region"] == "VYS")]
    #plot accidents and hide axis
    gdf.plot(ax=ax,markersize= 0.3,alpha=0.6)
    ax.axis('off')
    ax.set_title("Nehody v kraji Vysočina:")
    
    #calculate clusters
    X = np.array([[i.x,i.y]for i in gdf.geometry])
    kmeans = sklearn.cluster.KMeans(n_clusters=25, random_state=1).fit(X)
    
    #save count of accidents in every cluster
    count = np.bincount(kmeans.labels_)
    
    #save centroids of clusters
    clusters = kmeans.cluster_centers_
    
    #load centroid x,y positions and count of accidents in every cluster into DataFrame
    #for easier plotting
    df = pd.DataFrame(list(zip(clusters[:,0],clusters[:,1],count)),columns=["x","y","count"])
    
    #plot dataframe, clusters change size and colors by their count of accidents
    plt.scatter(x=df["x"],y=df["y"],c=df["count"],cmap="winter",s=df["count"]*0.3,alpha=0.6)
    plt.colorbar()
    
    #add background map
    ctx.add_basemap(ax, crs=gdf.crs.to_string(), source=ctx.providers.Stamen.TonerLite,
    alpha=0.9)
    
    #When not None saves graph into chosen folder
    if fig_location is not None:
        plt.savefig(fig_location)
    #If show_figure flag is True plots data into window
    if show_figure:
        plt.show()


if __name__ == "__main__":
    # zde muzete delat libovolne modifikace
    gdf = make_geo(pd.read_pickle("accidents.pkl.gz"))
    plot_geo(gdf, "geo1.png", True)
    plot_cluster(gdf, "geo2.png", True)

