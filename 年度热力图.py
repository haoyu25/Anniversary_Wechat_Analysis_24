import re
import time
import numpy as np
import pandas as pd
#import jieba #中文分词
#import jieba.posseg as pseg
#from PIL import Image
#from wordcloud import WordCloud
import seaborn as sns
import matplotlib.ticker as mticker
import matplotlib.transforms as mtransforms
#from matplotlib.colors import ListedColormap
from matplotlib import pyplot as plt
from matplotlib import font_manager as fm
#from tqdm import tqdm
#from paddlenlp import Taskflow #情感分析

#设置中文字体
sns.set_theme(style="ticks")
font = "/usr/share/fonts/winfont/simsun.ttc"
fp = fm.FontProperties(fname=font)
plt.rcParams["axes.unicode_minus"] = False
#人名标签
labels = ["小猪快跑", "整天快乐"]
nicknames_pao = ["小猪快跑"]
nicknames_run=['整天快乐']
custom_palette = ["#e74c3c", "#3498db"]

#读取数据
filePath = "msg.csv"
dStart = "2023-07-10 00:00:00"
dEnd = "2024-07-07 23:59:59"

df = pd.read_csv(filePath, encoding="utf-8")
df = df.query(
    "CreateTime >= {:d} and CreateTime <= {:d}".format(
        int(time.mktime(time.strptime(dStart, "%Y-%m-%d %H:%M:%S"))),
        int(time.mktime(time.strptime(dEnd, "%Y-%m-%d %H:%M:%S"))),
    )
)

df["StrTime"] = pd.to_datetime(df["StrTime"])
df["day"] = df["StrTime"].dt.dayofweek
df["hour"] = df["StrTime"].dt.hour
df["Count"] = 1

dfs = [df.query("IsSender == 0"), df.query("IsSender == 1")]

#消息过滤
def textFilter(text: str):
    text = text.lower()
    # 过滤 emoji
    try:
        co = re.compile("[\U00010000-\U0010ffff]")
    except re.error:
        co = re.compile("[\uD800-\uDBFF][\uDC00-\uDFFF]")
    text = co.sub(" ", text)
    # 过滤微信表情
    co =  re.compile(r'[\u4E00-\u9FA5]+')
    return co.sub(" ", text)

texts = [
    [textFilter(i) for i in dfs[0].query("Type == 1")["StrContent"].to_list()],
    [textFilter(i) for i in dfs[1].query("Type == 1")["StrContent"].to_list()],
]

#设置中文字体
plt.rcParams['font.sans-serif']=['SimHei']#默认字体设置改为中文黑体
plt.rcParams['axes.unicode_minus']=False #中文不识别符号

#类型分析
data = {}
for i in range(2):
    data[labels[i]] = [
        len(dfs[i].query("Type == 1")),
        len(dfs[i].query("Type == 3")),
        len(dfs[i].query("Type == 34")),
        len(dfs[i].query("Type == 43")),
        len(dfs[i].query("Type == 47")),
    ]

data = (
    pd.DataFrame(data, index=["Text", "Image", "Voice", "Video", "Sticker"])
    .reset_index()
    .melt("index")
    .rename(columns={"index": "Type", "variable": "Person", "value": "Count"})
)


#按周划分年度活跃分析
wTicks = 500
wStart = "2023-07-11"
wEnd = "2024-07-08"

#按日划分年度活跃分析
grouper = pd.Grouper(key="StrTime", freq="D")
data = df.groupby(grouper)["Count"].sum()
data = data.to_frame()

data["date"] = data.index
data["week"] = data["date"].dt.isocalendar()["week"]
data["day"] = data["date"].dt.dayofweek
data.index = range(len(data))
print(data)
for i in range(7):
    if data.loc[i, "week"] > 1:
        data.loc[i, "week"] = 0
#
data = data.pivot(index="day", columns="week", values="Count")
data.index = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
data.columns = pd.date_range(start=wStart, end=wEnd, freq="W-MON").strftime("%m-%d")
print(data)
ax = sns.heatmap(
    data,
    annot=False,
    linewidths=0.5,
    cbar_kws={"orientation": "vertical", "location": "left", "pad": 0.03},
    cmap="Reds",
    vmin=0,
    vmax=800
)
ax.set_xlabel("Week")
ax.set_ylabel("Weekday")
ax.figure.set_size_inches(20, 4)
ax.figure.set_dpi(150)

plt.savefig("my/03.png")
plt.show()
plt.close()

#paopao
df1 = df[df["NickName"].isin(nicknames_pao)]
dfs1 = [df1.query("IsSender == 0"), df1.query("IsSender == 1")]

texts = [
    [textFilter(i) for i in dfs1[0].query("Type == 1")["StrContent"].to_list()],
    [textFilter(i) for i in dfs1[1].query("Type == 1")["StrContent"].to_list()],
]

grouper = pd.Grouper(key="StrTime", freq="D")
data = df1.groupby(grouper)["Count"].sum()
data = data.to_frame()

data["date"] = data.index
data["week"] = data["date"].dt.isocalendar()["week"]
data["day"] = data["date"].dt.dayofweek
data.index = range(len(data))
print(data)
for i in range(7):
    if data.loc[i, "week"] > 1:
        data.loc[i, "week"] = 0
#
data = data.pivot(index="day", columns="week", values="Count")
data.index = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
data.columns = pd.date_range(start=wStart, end=wEnd, freq="W-MON").strftime("%m-%d")
print(data)
ax = sns.heatmap(
    data,
    annot=False,
    linewidths=0.5,
    cbar_kws={"orientation": "vertical", "location": "left", "pad": 0.03},
    cmap="Reds",
    vmin=0,
    vmax=800
)
ax.set_xlabel("Week")
ax.set_ylabel("Weekday")
ax.figure.set_size_inches(20, 4)
ax.figure.set_dpi(150)

plt.savefig("my/03_pao.png")
plt.show()
plt.close()


#runrun
df1 = df[df["NickName"].isin(nicknames_run)]
dfs1 = [df1.query("IsSender == 0"), df1.query("IsSender == 1")]

texts = [
    [textFilter(i) for i in dfs1[0].query("Type == 1")["StrContent"].to_list()],
    [textFilter(i) for i in dfs1[1].query("Type == 1")["StrContent"].to_list()],
]

grouper = pd.Grouper(key="StrTime", freq="D")
data = df1.groupby(grouper)["Count"].sum()
data = data.to_frame()

data["date"] = data.index
data["week"] = data["date"].dt.isocalendar()["week"]
data["day"] = data["date"].dt.dayofweek
data.index = range(len(data))
print(data)
for i in range(7):
    if data.loc[i, "week"] > 1:
        data.loc[i, "week"] = 0
#
data = data.pivot(index="day", columns="week", values="Count")
data.index = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
data.columns = pd.date_range(start=wStart, end=wEnd, freq="W-MON").strftime("%m-%d")
print(data)
ax = sns.heatmap(
    data,
    annot=False,
    linewidths=0.5,
    cbar_kws={"orientation": "vertical", "location": "left", "pad": 0.03},
    cmap="Reds",
    vmin=0,
    vmax=800
)
ax.set_xlabel("Week")
ax.set_ylabel("Weekday")
ax.figure.set_size_inches(20, 4)
ax.figure.set_dpi(150)

plt.savefig("my/03_run.png")
plt.show()
plt.close()