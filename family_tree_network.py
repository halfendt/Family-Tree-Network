import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from ged4py import GedcomReader
import igraph as ig
import plotly.offline as py
import plotly.graph_objs as go


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', required=True, help='Filename of GEDCOM file')
    parser.add_argument('-d', '--dim', type=int, default=3, help='Dimension of Network graph, 3 = 3D or 2 = 2D')
    parser.add_argument('-n', '--name', type=bool, default=False, help='True to display node name, False for ID number') 
    return parser

def main():
    # Read in command line arguments
    opt = get_parser().parse_args()
    # Read in GEDCOM file
    reader = GedcomReader(opt.file, encoding="utf-8")

    # Build list of individuals from GEDCOM file 
    indi_list = []
    for i, indi in enumerate(reader.records0("INDI")):
        indi_dict = {}
        indi_dict['id'] = int(indi.xref_id.split('@')[1][1:])-1
        if opt.name:
            indi_dict['name'] = indi.name.format()
        indi_dict['gender'] = indi.sub_tag_value("SEX")
        indi_dict['birth_date'] = indi.sub_tag_value("BIRT/DATE")
        indi_dict['birth_place'] = indi.sub_tag_value("BIRT/PLAC")
        indi_dict['death_date'] = indi.sub_tag_value("DEAT/DATE")
        indi_dict['death_place'] = indi.sub_tag_value("DEAT/PLAC")
        indi_list.append(indi_dict)
    # Store in dataframe and save dataframe
    df_indi = pd.DataFrame(indi_list).set_index('id').sort_index().fillna('Unknown')
    df_indi.to_csv('family_tree_network.csv', index=False)
    
    # Build list of families from GEDCOM file
    family_list = []
    for i, fam in enumerate(reader.records0("FAM")):
        husband, wife = fam.sub_tag("HUSB"), fam.sub_tag("WIFE")
        if husband and wife: 
            family_list.append((int(husband.xref_id.split('@')[1][1:])-1, int(wife.xref_id.split('@')[1][1:])-1))
            family_list.append((int(wife.xref_id.split('@')[1][1:])-1, int(husband.xref_id.split('@')[1][1:])-1))
        children = fam.sub_tags("CHIL")
        for child in children:
            if husband:
                family_list.append((int(husband.xref_id.split('@')[1][1:])-1, int(child.xref_id.split('@')[1][1:])-1))
            if wife:
                family_list.append((int(wife.xref_id.split('@')[1][1:])-1, int(child.xref_id.split('@')[1][1:])-1))
    
    # Add nodes (Individuals) and edges (connections between individuals) to graph network
    g = ig.Graph(directed=False)
    g.add_vertices(df_indi.index.max()+1)
    g.add_edges(family_list)
    # Remove individuals not connected to anyone (if applicable)
    g.delete_vertices(list(set(range(df_indi.index.max()))-set(df_indi.index)))

    # Build network graph with x, y positions for 3D or 2D graph with Fruchterman-Reingold layout
    edge_list = g.get_edgelist()
    if opt.dim == 3:
        layout = g.layout('fr3d')
        Xn3d = [layout[k][0] for k in range(len(indi_list))]
        Yn3d = [layout[k][1] for k in range(len(indi_list))]
        Zn3d = [layout[k][2] for k in range(len(indi_list))]

        Xe3d = []
        Ye3d = []
        Ze3d = []
        for e in edge_list:
            Xe3d.extend([layout[e[0]][0], layout[e[1]][0], None])
            Ye3d.extend([layout[e[0]][1], layout[e[1]][1], None])
            Ze3d.extend([layout[e[0]][2], layout[e[1]][2], None])

        trace1 = go.Scatter3d(x=Xe3d, y=Ye3d, z=Ze3d, mode='lines', line=dict(color='rgb(0,0,0)', width=1), hoverinfo='none')
        if opt.name:
            display_text = df_indi['name']
        else:
            display_text = df_indi.index.astype(str)
        trace2 = go.Scatter3d(x=Xn3d, y=Yn3d, z=Zn3d, mode='markers', name='people',
                              marker=dict(symbol='circle', size=6, colorscale='plasma', 
                                          color=np.sqrt(np.array(Xn3d)**2 + np.array(Yn3d)**2 + np.array(Zn3d)**2),
                                          line=dict(color='rgb(50,50,50)', width=0.5)),
                              text=display_text + ' ' + df_indi['birth_date'].astype(str) + '-' + df_indi['death_date'].astype(str),
                              hoverinfo='text')
    else:
        layout = g.layout('fr')
        Xn = [layout[k][0] for k in range(len(indi_list))]
        Yn = [layout[k][1] for k in range(len(indi_list))]

        Xe = []
        Ye = []
        for e in edge_list:
            Xe.extend([layout[e[0]][0], layout[e[1]][0], None])
            Ye.extend([layout[e[0]][1], layout[e[1]][1], None])

        trace1 = go.Scatter(x=Xe, y=Ye, mode='lines', line=dict(color='rgb(0,0,0)', width=1), hoverinfo='none')
        if opt.name:
            display_text = df_indi['name']
        else:
            display_text = df_indi.index.astype(str)
        trace2 = go.Scatter(x=Xn, y=Yn, mode='markers', name='people',
                            marker=dict(symbol='circle', size=6,
                                        colorscale='plasma', color=np.sqrt(np.array(Xn)**2 + np.array(Yn)**2),
                                        line=dict(color='rgb(50,50,50)', width=0.5)),
                            text=display_text + ' ' + df_indi['birth_date'].astype(str) + '-' + df_indi['death_date'].astype(str),
                            hoverinfo='text')
    axis = dict(showbackground=False, showline=False, zeroline=False, showgrid=False, showticklabels=False, title='')
    pylayout = go.Layout(title="Family Tree Network", width=1550, height=750, showlegend=False,
                         scene=dict(xaxis=dict(axis), yaxis=dict(axis), zaxis=dict(axis)),
                         margin=dict(t=30), hovermode='closest',
                         annotations=[dict(showarrow=False, text='', xref='paper', yref='paper',
                                           x=0, y=0.1, xanchor='left', yanchor='bottom', font=dict(size=14))])

    # Display graph and save to file
    data = [trace1, trace2]
    fig = go.Figure(data=data, layout=pylayout)
    py.plot(fig, filename='family_tree_network.html')


if __name__ == '__main__':
    main()
