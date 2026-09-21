import pandas as pd
import os,sys
sys.path.append(r"D:\python\core")
from brain_area import BrainArea
# ba = BrainArea()

class brain_level():
    # ba = BrainArea()

    def __init__(self):
        self.filepath = r"D:\python\pre-cube length"
        self.dfbrain = pd.read_excel(os.path.join(self.filepath,"brain_areas.xlsx"),index_col=0)
        # ba = BrainArea()
    def export_level_file(self,i=8):
        ba = BrainArea()
        dfchange = self.dfbrain.loc[self.dfbrain.level >i]
        areas_dic = []
        for area in dfchange.region:
            level = {}
            level["father"] = ba.search_brain_area(area)[i-1][1]
            level["child"] = area
            areas_dic.append(level)
        dfmap = pd.DataFrame(areas_dic)
        dfmap.to_excel(os.path.join(self.filepath,"level_%d_map.xlsx"%i))
    
    def check_self_define_level(self,dfdata,file):
        dfmap = pd.read_excel(os.path.join(self.filepath,file),index_col=0)
        
        areas = dfdata.columns.tolist()
        target = dfmap.child.tolist()
        self.dfdata = dfdata

        map_list = []
        for area in areas:
            if area in target:
                map_list.append(area)
        
        self.map_dic = {}
        for area in map_list:
            father = dfmap.loc[dfmap.child == area].father.tolist()[0]
            if father not in self.map_dic:
                self.map_dic[father] = [area]
            else:
                self.map_dic[father].append(area)
 
        contain = []
        for level,subarea in self.map_dic.items():
            contain.append(level in self.dfdata.columns.to_list())
 
        if True in contain:
            print("high level areas exist, run up_projection2level_exist")
            tmp = [i for i,x in enumerate(contain) if x==True]
            back_area = []
            back = list(self.map_dic.items())
            for id in tmp:
                back_tmp = back[id][0]
                back_area.append(back_tmp)            
            return contain,back_area,self.map_dic

        else:
            print("high level areas not exist, run up_projection2level")
            return contain,"no","no"



    def check_high_level_area(self,dfdata,level = 8):
        dfmap = pd.read_excel(os.path.join(self.filepath,"level_%d_map.xlsx"%level),index_col=0)
        
        areas = dfdata.columns.tolist()
        target = dfmap.child.tolist()
        self.dfdata = dfdata

        map_list = []
        for area in areas:
            if area in target:
                map_list.append(area)
        
        self.map_dic = {}
        for area in map_list:
            father = dfmap.loc[dfmap.child == area].father.tolist()[0]
            if father not in self.map_dic:
                self.map_dic[father] = [area]
            else:
                self.map_dic[father].append(area)
 
        contain = []
        for level,subarea in self.map_dic.items():
            contain.append(level in self.dfdata.columns.to_list())
 
        if True in contain:
            print("high level areas exist, run up_projection2level_exist")
            tmp = [i for i,x in enumerate(contain) if x==True]
            back_area = []
            back = list(self.map_dic.items())
            for id in tmp:
                back_tmp = back[id][0]
                back_area.append(back_tmp)            
            return contain,back_area

        else:
            print("high level areas not exist, run up_projection2level")
            return contain,"no"

    def up_projection2level(self):
        for level,subarea in self.map_dic.items():
            self.dfdata[level] = self.dfdata[subarea].apply(lambda x: x.sum(), axis=1)
            self.dfdata.drop(subarea,axis=1,inplace=True)
        
        return self.dfdata

    def up_projection2level_exist(self,morelist = ""):
        for level,subarea in self.map_dic.items():
            if level not in morelist:
                self.dfdata[level] = self.dfdata[subarea].apply(lambda x: x.sum(), axis=1)
                self.dfdata.drop(subarea,axis=1,inplace=True)
            else:
                if subarea != [level]:
                    self.dfdata[level] = self.dfdata[subarea+[level]].apply(lambda x: x.sum(), axis=1)
                    self.dfdata.drop(subarea,axis=1,inplace=True)
                elif subarea == [level]:
                    pass
        return self.dfdata







