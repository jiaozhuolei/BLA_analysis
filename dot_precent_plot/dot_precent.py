import pandas as pd
import numpy as np
import os,glob
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.pylab import *
import matplotlib.cm as cm
import matplotlib.patches as patches
import matplotlib as mpl
import copy
mpl.rcParams['pdf.fonttype'] = 42
mpl.rcParams['ps.fonttype'] = 42
plt.rc("font",family="Arial")

class dot_process():


    def __init__(self,df):
        if type(df) == str:
            self.dfdata = pd.read_excel(df,index_col=0)
        elif type(df) == pd.core.frame.DataFrame:
            self.dfdata = df
        else:
            print("no correct input data")
        
    
    def get_pecent_df(self,hue,plot_list):
        dfna = copy.deepcopy(self.dfdata)
        dfna[dfna.eq(0)] = np.nan
        dfcount = dfna.pivot_table(index=hue,values=plot_list,aggfunc="count")
        dfall = self.dfdata.pivot_table(index=hue,values=plot_list,aggfunc="count")
        self.dfpercent = ((dfcount.div(dfall)*100)[plot_list]).stack().unstack(0)
        return self.dfpercent
    
    def get_mean_value(self,hue,plot_list):
        self.dfvalues = self.dfdata.pivot_table(index=hue,values=plot_list,aggfunc="mean")
        self.dfvalues = (self.dfvalues[plot_list]).stack().unstack(0)
        return self.dfvalues
    
    def plot_dot_scatter_hue_x(self,filepath,xlabel,ylabel,xlist=None,min_val = 0,max_val = 3000,color_bar = True,dot_bar = True,cmap = 'YlGnBu',figsize = (4.5,20)):
        
        if xlist != None:
            self.dfpercent = self.dfpercent[xlist]
            self.dfvalues = self.dfvalues[xlist]

        col_s = self.dfpercent.apply(lambda x:x.sum(),axis=1) 
        row_s = self.dfpercent.apply(lambda x:x.sum(),axis=0) 
        total = col_s.sum()
        dfdata_y = pd.DataFrame(columns=self.dfpercent.columns.tolist(),index= self.dfpercent.index.tolist())
        dfdata_x = pd.DataFrame(columns=self.dfpercent.columns.tolist(),index= self.dfpercent.index.tolist())
        for i in range(len(col_s)):
            for j in range(len(row_s)):
                dfdata_y.iloc[i,j] = len(col_s)-i
                dfdata_x.iloc[i,j] = j+1
        fig, ax = plt.subplots(figsize = figsize)
        my_cmap = cm.get_cmap(cmap) # or any other one
        norm = matplotlib.colors.Normalize(min_val, max_val)

        color_list= []
        for i in range(len(col_s)):
            color_tmp = []
            for j in range(len(row_s)):
                tmp = self.dfvalues.iloc[i,j]
                color_i = my_cmap(norm(tmp))
                color_h = matplotlib.colors.to_hex(color_i)
                color_list.append(color_h)

        cmmapable = cm.ScalarMappable(norm, my_cmap)
        cmmapable.set_array(np.linspace(min_val, max_val, 100))

        # if color_bar == True:
        #     ax = gca()
        #     colorbar(cmmapable)

        scatter =ax.scatter(dfdata_x.values, dfdata_y.values, c=color_list, s=self.dfpercent.values*self.dfpercent.values/10, alpha=1)
        handles, labels = scatter.legend_elements(prop="sizes",color="salmon",alpha=1,num=5,func=lambda x: sqrt(x*10))

        if color_bar:
            plt.colorbar(cmmapable, ax=ax)
        
        if dot_bar == True:
            l1 = ax.legend(handles, labels
                        , loc="upper right", title="%"
                    ,title_fontsize=24
                    ,labelspacing =3
                    ,fontsize=24
                    ,bbox_to_anchor=(2, 1)
                    ,frameon=False)
            ax.add_artist(l1)
        ax.set_xticks(dfdata_x.iloc[0,:].tolist())
        ax.set_yticks(dfdata_y.iloc[:,0].tolist())
        ax.set_yticklabels(dfdata_y.index.tolist(),fontsize=24)
        ax.set_xticklabels(dfdata_x.columns.tolist(),fontsize=24)
        ax.set_xlabel(xlabel, fontsize=24)
        ax.set_ylabel(ylabel, fontsize=24)
        ax.grid(False)
        plt.savefig(filepath,dpi = 600)
        # plt.savefig(filepath,format = "jpg",dpi = 600)

    def plot_dot_scatter_hue_y(self,filepath,xlabel,ylabel,ylist=None,min_val = 0,max_val = 3000,color_bar = True,dot_bar = True,cmap = 'YlGnBu',figsize = (4.5,20)):
        
        # try to plot the Scatter/rich
        if ylist != None:
            self.dfpercent = self.dfpercent[ylist].stack().unstack(0)
            self.dfvalues = self.dfvalues[ylist].stack().unstack(0)
        else:
            self.dfpercent = self.dfpercent.stack().unstack(0)
            self.dfvalues = self.dfvalues.stack().unstack(0)
        col_s = self.dfpercent.apply(lambda x:x.sum(),axis=1) 
        row_s = self.dfpercent.apply(lambda x:x.sum(),axis=0) 
        total = col_s.sum()
        dfdata_y = pd.DataFrame(columns=self.dfpercent.columns.tolist(),index= self.dfpercent.index.tolist())
        dfdata_x = pd.DataFrame(columns=self.dfpercent.columns.tolist(),index= self.dfpercent.index.tolist())
        for i in range(len(col_s)):
            for j in range(len(row_s)):
                dfdata_y.iloc[i,j] = len(col_s)-i
                dfdata_x.iloc[i,j] = j+1
        fig, ax = plt.subplots(figsize = figsize)
        my_cmap = cm.get_cmap(cmap) # or any other one
        norm = matplotlib.colors.Normalize(min_val, max_val)

        color_list= []
        for i in range(len(col_s)):
            color_tmp = []
            for j in range(len(row_s)):
                tmp = self.dfvalues.iloc[i,j]
                color_i = my_cmap(norm(tmp))
                color_h = matplotlib.colors.to_hex(color_i)
                color_list.append(color_h)

        cmmapable = cm.ScalarMappable(norm, my_cmap)
        cmmapable.set_array(range(min_val, max_val))

        if color_bar == True:
            ax = gca()
            colorbar(cmmapable)

        scatter =ax.scatter(dfdata_x.values, dfdata_y.values, c=color_list, s=self.dfpercent.values*self.dfpercent.values/10, alpha=1)
        handles, labels = scatter.legend_elements(prop="sizes",color="salmon",alpha=1,num=5,func=lambda x: sqrt(x*10))
        
        if dot_bar == True:
            l1 = ax.legend(handles, labels
                        , loc="upper right", title="%"
                    ,title_fontsize=24
                    ,labelspacing =3
                    ,fontsize=24
                    ,bbox_to_anchor=(2, 1)
                    ,frameon=False)
            ax.add_artist(l1)
        ax.set_xticks(dfdata_x.iloc[0,:].tolist())
        ax.set_yticks(dfdata_y.iloc[:,0].tolist())
        ax.set_yticklabels(dfdata_y.index.tolist(),fontsize=24)
        ax.set_xticklabels(dfdata_x.columns.tolist(),rotation =90,fontsize=24)
        ax.set_xlabel(xlabel, fontsize=24)
        ax.set_ylabel(ylabel, fontsize=24)
        ax.grid(False)
        plt.savefig(filepath,dpi = 600)
        # plt.savefig(filepath,format = "jpg",dpi = 600)

if __name__=="__main__":
    import dot_precent as dp

    dotplot = dp.dot_process(r"W:\20220210_for_figs\0818 projection levels\MY_neuron_level7.xlsx")
    dfper = dotplot.get_pecent_df(hue="cluster",plot_list=["LHA","PAG","MEA","TU","ZI"])
    dfval = dotplot.get_mean_value(hue="cluster",plot_list=["LHA","PAG","MEA","TU","ZI"])
    dotplot.plot_dot_scatter_hue_y(filepath=r"W:\20220210_for_figs\0818 projection levels\aa.pdf",xlabel="areas",ylabel="cluster")


    
