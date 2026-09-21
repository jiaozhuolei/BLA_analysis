import plotly.graph_objects as go
import trimesh
import numpy as np
import random
import pickle,os
import pandas as pd


def generate_plotly_color(value,color1=[0,255,0],color2=[0,0,255],cmin=0,cmax=99):
    if value > cmax:
        value = cmax
    r = color2[0]+((cmax-value)*(color1[0]-color2[0])/(cmax-cmin))
    g = color2[1]+((cmax-value)*(color1[1]-color2[1])/(cmax-cmin))
    b = color2[2]+((cmax-value)*(color1[2]-color2[2])/(cmax-cmin))
    return r"rgb(%.2f,%.2f,%.2f)"%(r,g,b)

def generate_color():
    r = round(random.random()*255)
    g = round(random.random()*255)
    b = round(random.random()*255)
    return r"rgb(%.2f,%.2f,%.2f)"%(r,g,b)


def generate_go_ba_qiu(obj_file,o=0.05,c="grey"):
    v = trimesh.load_mesh(obj_file)
    volume = go.Mesh3d(
    x=v.vertices[:, 0],
    y=v.vertices[:, 1],
    z=v.vertices[:, 2],
    i=v.faces[:, 0],
    j=v.faces[:, 1],
    k=v.faces[:, 2],
    opacity=o,
    color=c)
    return volume

def generate_go_ba(area = "root",o=0.05,c="grey",half = True):
    obj_file = ".\\obj\\%s.obj"%area
    v = trimesh.load_mesh(obj_file)
    volume = go.Mesh3d(
    x=v.vertices[:, 0],
    y=v.vertices[:, 1],
    z=v.vertices[:, 2],
    i=v.faces[:, 0],
    j=v.faces[:, 1],
    k=v.faces[:, 2],
    opacity=o,
    color=c)
    return volume


def generate_go_lines(all_points_of_one_neuron,c="black",lw=1,name="arbor",vector=False,showlegend = False):
    """
    u.all_points_xyzs
    """
    if np.shape(all_points_of_one_neuron)[1]>=6:
        x = np.array(all_points_of_one_neuron)[:,2]
        y = np.array(all_points_of_one_neuron)[:,3]
        z = np.array(all_points_of_one_neuron)[:,4]
    else:
        x = np.array(all_points_of_one_neuron)[:,0]
        y = np.array(all_points_of_one_neuron)[:,1]
        z = np.array(all_points_of_one_neuron)[:,2]
    if vector:
        x=x[[0,-1]]
        y=y[[0,-1]]
        z=z[[0,-1]]

    arbor = go.Scatter3d(
        x=x,
        y=y,
        z=z,
        mode="lines",
        name=name,
        # hoverinfo=name,
        line=dict(
            color=c,
            width=lw
            # opacity=0.5
        ),
        showlegend = showlegend)
    
    return arbor

def generate_go_scatters(points,size=3,name="points",color="black",showlegend = False):
    if np.shape(points)[1]>=6:
        x = np.array(points)[:,2]
        y = np.array(points)[:,3]
        z = np.array(points)[:,4]
    else:
        x = np.array(points)[:,0]
        y = np.array(points)[:,1]
        z = np.array(points)[:,2]
    scatters = go.Scatter3d(
        x=x,
        y=y,
        z=z,
        mode="markers",
        name=name,
        marker=dict(
            size=size,
            color=color,
            opacity=1,
        ),
        showlegend = showlegend)
    return scatters

def generate_go_layout(title="Parametric Plot",eye_from="front",big = 1,**kwargs):
    front_view = dict(x=-1.5*big,y=0,z=0)
    top_view = dict(x=0,y=-1.5*big,z=0)
    left_view = dict(x=0,y=0,z=-1.5*big) 
    # se_view = dict(x=-1.25, y=-2, z=-1.25)
    se_view = dict(x=-1.25*big, y=-1, z=-1.25*big)
    if eye_from == "front":
        eye = front_view
    if eye_from == "left":
        eye = left_view
    if eye_from == "top":
        eye = top_view
    if eye_from == "se":
        eye = se_view   
    layout = go.Layout(
        scene_camera=dict(
            up=dict(x=0, y=-1, z=0),
            center=dict(x=0, y=0, z=0),
            eye=eye),
        title=title,
        scene_xaxis_showticklabels=False,
        scene_yaxis_showticklabels=False,
        scene_zaxis_showticklabels=False,
         scene = dict(
            xaxis = dict(
                 backgroundcolor="white",
                 gridcolor="white",
                 showbackground=True,
                 zerolinecolor="white",),
            yaxis = dict(
                backgroundcolor="white",
                gridcolor="white",
                showbackground=True,
                zerolinecolor="white"),
            zaxis = dict(
                backgroundcolor="white",
                gridcolor="white",
                showbackground=True,
                zerolinecolor="white",),
             xaxis_title='',
             yaxis_title='',
             zaxis_title=''),
         **kwargs
    )
    # the same params could also be put in fig.updata_layout()
    return layout