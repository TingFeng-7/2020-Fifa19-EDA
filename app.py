import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from dash.dependencies import Input, Output

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__,external_stylesheets=external_stylesheets)
df=pd.read_csv('NoPos_data2.csv')

del df['Special']
#生成可视化表
def generate_table(dataframe, max_rows=20):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))
        ])
    ])
##1.根据一个标签相关生成二维dataframe
def gen_df(df,label):
    data=df[label].value_counts()
    data_df=data.to_frame()
    data_df.rename(columns={label:'Number'},inplace=True)
    return data_df
##2.画饼状图(嵌套1方法)
def draw_pie_chart(df,label):
    df=gen_df(df,label)
    index=df.index ##提前做好索引
    fig=px.pie(df,names=index,values='Number',color=index)
    return fig
##3.不嵌套
def draw_pie_chart1(df):
    index=df.index ##提前做好索引
    fig=px.pie(df,names=index,values='Number',color=index)
    return fig
##4.画柱形图
def draw_Bar_chart(df):
    index=df.index
    fig=px.bar(df,x=index,y='Number',color=index)
    return fig
##
position_df=gen_df(df,'position_agg')
# body_df=gen_df(df,'BodyType')

###每个大类位置的dataframe
fw=df.loc[df['position_agg']=='forward']
mid=df.loc[df['position_agg']=='midfield']
defense=df.loc[df['position_agg']=='defense']
gk=df.loc[df['position_agg']=='goalkeeper']
## tab  散点图
def gen_score_scatter(df,label,score):
    fig_tab=px.scatter(df.loc[df[label]>=score], x="Age", y="Overall", color='Nationality',
        hover_name='Name',hover_data=['Position'])
    fig_tab.update_layout(hovermode="x")
    return fig_tab

##dataframe划分
top_fw_df=gen_df(fw.loc[fw['Overall']>=85],'Nationality')
top_mid_df=gen_df(mid.loc[mid['Overall']>=85],'Nationality')
top_defense_df=gen_df(defense.loc[defense['Overall']>=85],'Nationality')
top_gk_df=gen_df(gk.loc[gk['Overall']>=85],'Nationality')

##tab内容图像准备

fig_tab1 = gen_score_scatter(fw,'Overall',85)
fig_tab2 = gen_score_scatter(mid,'Overall',85)
fig_tab3 = gen_score_scatter(defense,'Overall',85)
fig_tab4 = gen_score_scatter(gk,'Overall',85)

##柱状图来袭
fig_1=draw_Bar_chart(position_df)
position_fig=draw_pie_chart(df,'Position')
prefoot_fig=draw_pie_chart(df,'PreferredFoot')
body_fig=draw_pie_chart(df,'BodyType')
work_fig=draw_pie_chart(df,'WorkRate')
top_fw_fig=draw_pie_chart1(top_fw_df)
##sort排序
##top 20 club fig 6、7
def gen_with_club(df,group,label):
    gwc_df=df.groupby(group)[label].mean().reset_index().sort_values(label,ascending=True).tail(20)
    return px.bar(gwc_df, x=label, y="Club",orientation='h')

club_value_fig = gen_with_club(df,'Club','Value')
Overall_fig=gen_with_club(df,'Club','Overall')

##最佳十一人名单
Best_11_list=['L. Messi','Cristiano Ronaldo',
                'David Silva','K. De Bruyne','L. Modrić','N. Kanté',
                'Marcelo','Sergio Ramos','D. Godín','Azpilicueta',
               'De Gea']

best_df=df.loc[df['Name'].isin(Best_11_list)].reset_index()
best_df=best_df.drop_duplicates(['Name'])
del best_df['Unnamed: 0']
###最终 3d 散点图 最后的fig
ultimate_fig=px.scatter_3d(best_df,x='Age',y='Potential',z='Overall',color='Name',
            hover_name='Name',hover_data=['Nationality'])

##app 的 正式布局
app.layout = html.Div(children=[
    html.H1(children='Welcome to my report'),
    html.Div(children=''),
    html.H3(children='Fifa 19 Dataset'),
    generate_table(df),
    html.H3(children='1.各个位置的人数分布'),
    html.H4(children='①柱状图'),
    dcc.Graph(figure=fig_1),
    html.H4(children='②饼状图'),

    dcc.Graph(figure=position_fig),
    html.H3(children='2.左右脚球员的比例'),
    dcc.Graph(figure=prefoot_fig),
    html.H3(children='3.顶级前锋都来自哪些国家'),
    dcc.Graph(figure=top_fw_fig),
    html.H3(children='4.足坛球员的体型情况'),
    dcc.Graph(figure=body_fig),
    html.H3(children='5.场上积极程度'),
    dcc.Graph(figure=work_fig),
    html.H3(children='6.Top20 球员平均价值的俱乐部'),
    dcc.Graph(figure=club_value_fig),
    html.H3(children='7.Top20 球员平均评分最高的俱乐部'),
    dcc.Graph(figure=Overall_fig),
    ##tab组件分区
    html.Div([dcc.Tabs(id='tabs',value='tab-1',children=[
        dcc.Tab(label='顶级前锋',value='tab-1'),
        dcc.Tab(label='顶级中场',value='tab-2'),
        dcc.Tab(label='顶级后卫',value='tab-3'),
        dcc.Tab(label='顶级门将',value='tab-4')])]),
    html.Div(id='tabs-content'),
    ##again
    html.H3(children='8.足坛最强十一人'),
    generate_table(best_df,11),
    html.Div(children=''),
    html.H3(children='附上3D散点图'),
    dcc.Graph(figure=ultimate_fig)
])
@app.callback(Output('tabs-content', 'children'),
              [Input('tabs', 'value')])
def render_content(tab):
    if tab == 'tab-1':
        return html.Div([
            html.H3('前锋'),
            dcc.Graph(figure=fig_tab1)
        ])
    elif tab == 'tab-2':
        return html.Div([
            html.H3('中场'),
            dcc.Graph(figure=fig_tab2)
        ]),
    elif tab == 'tab-3':
        return html.Div([
            html.H3('后卫'),
            dcc.Graph(figure=fig_tab3)
        ]),
    elif tab == 'tab-4':
        return html.Div([
            html.H3('门将'),
            dcc.Graph(figure=fig_tab4)
            ])

if __name__ == '__main__':
    app.run_server(debug=True)
