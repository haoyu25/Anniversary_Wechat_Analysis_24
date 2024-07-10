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
custom_palette = ["#fa6596", "#3fb0fa"]

#读取数据
filePath = "msg.csv"
dStart = "2023-06-28 00:00:00"
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
g = sns.catplot(data, kind="bar", x="Type", y="Count", hue="Person",
                palette=custom_palette,
                alpha=0.6, height=6)

for ax in g.axes.ravel():
    for i in range(2):
        ax.bar_label(ax.containers[i], fontsize=9)
sns.move_legend(g, "upper right")
plt.yscale("log")


g.figure.set_size_inches(6, 5)
g.figure.set_dpi(150)
plt.savefig("my/04.png")
plt.show()

#每周活跃分析
grouper = pd.Grouper(key="day")
data = df.groupby(grouper)["Count"].sum()
data = data.sort_index()
data.index = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


fig, ax = plt.subplots(figsize=(5, 5), dpi=150)
ax.pie(data, labels=data.index, autopct='%1.1f%%',
       startangle=90, counterclock=False,
       colors=['#d8b4e9','#e4cfed','#dfc4eb','#dbbbe9'])

ax.set_xlabel("Weekly Activity Distribution")

plt.savefig("my/05.png")
plt.show()
plt.close()

#24小时活跃度分析
multiple = "dodge"

data = {"Time": [], "Person": []}
for i in range(2):
    hour = dfs[i]["hour"].to_list()
    data["Time"] += hour
    data["Person"] += [labels[i]] * len(hour)

data = pd.DataFrame(data)
bins = np.arange(0, 25, 1)

ax = sns.histplot(
    data=data,
    x="Time",
    hue="Person",
    bins=bins,
    multiple=multiple,
    linewidth=0.5,
    palette=custom_palette,
    alpha=0.6,
)
ax.set_xticks(bins)
ax.set_xticklabels(bins)
ax.set_xlabel("Hour")
ax.set_xlim(0, 24)

ax.figure.set_size_inches(8, 4)
ax.figure.set_dpi(150)
sns.despine()

plt.savefig("my/06.png")
plt.show()
plt.close()
