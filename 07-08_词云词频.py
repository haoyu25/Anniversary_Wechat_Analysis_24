from wordcloud import WordCloud
import pandas as pd
from PIL import Image
import numpy
import jieba
import re # re用于正则表达式处理
from collections import Counter # Counter用于计数
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import seaborn as sns

font = "/usr/share/fonts/winfont/simsun.ttc"
cmap = ListedColormap(
    [
        "#fac1cf",
        "#a9d7ba",
        "#58b1db",
        "#f296ab",
        "#5dab81",
        "#3d9ec4",
        "#e16a8d",
        "#237b50",
        "#1e8299",
        "#8d3549",
        "#35563b",
        "#2d5d73",
    ]
)

#设置中文字体
plt.rcParams['font.sans-serif']=['SimHei']#默认字体设置改为中文黑体
plt.rcParams['axes.unicode_minus']=False #中文不识别符号

df = pd.read_csv("msg.csv").query("Type == 1")

def get_wordcload(Nickname,Image_path,Save_path,Bar_path):
    global df # 使用全局变量 df，或者在函数内读取数据
    df_filtered = df[df["NickName"].isin(Nickname)]
    texts = [str(text) for text in df_filtered['StrContent'].to_list()]

   # 读取停用词
    with open("data/CNstopwords.txt", 'r', encoding='utf-8') as f:
        lines = f.readlines()
    stopwords = [line.strip().replace("\ufeff", "") for line in lines]
    stopwords.extend(["OK", '哈哈哈哈','哈哈哈'])

    norm_texts = []
    pattern_emoji = re.compile("(\[.+?\])")
    pattern_num = re.compile(r"\d+")

    for text in texts:
        text = pattern_emoji.sub('', text).replace("\n", "")
        text = pattern_num.sub('', text).replace("\n", "")
        words = jieba.lcut(text)  # 使用jieba分词
        res = [word for word in words if word not in stopwords and word.replace(" ", "") != "" and len(word) > 1]
        if res != []:
            norm_texts.extend(res)

    count_dict = dict(Counter(norm_texts))
    mask_image = numpy.array(Image.open(Image_path))
    wc = WordCloud(
                    #    width=2560,
                    #    height=1440, # 自定义mask后，图片尺寸取决于mask
                       font_path=font,
                       background_color="white",
                       colormap='tab20b',
                       mask=mask_image,
                       scale=7, # 增大以提高分辨率，倍数增加
                       collocations=False,
                       )
    wc = wc.fit_words(count_dict)
    plt.imshow(wc)
    plt.axis("off")
    plt.savefig(Save_path)
    plt.show()
    plt.close()

    sort_dict = pd.DataFrame(sorted(count_dict.items(), key=lambda x: x[1], reverse=True)[:30],
                             columns=["Word", "Count"])

    plt.figure(figsize=(10, 6))
    ax = sns.barplot(
        data=sort_dict,
        x="Word",
        y="Count",
        color="#3fb0fa",
        alpha=0.6,
    )

    # Add bar labels
    for p in ax.patches:
        ax.annotate(format(p.get_height(), '.0f'),
                    (p.get_x() + p.get_width() / 2., p.get_height()),
                    ha='center', va='center',
                    xytext=(0, 9),
                    textcoords='offset points',
                    fontsize=8)

    ax.set_xticklabels(ax.get_xticklabels(),
                       rotation=45,
                       horizontalalignment='right',
                       fontsize=11)

    sns.despine()

    plt.savefig(Bar_path)
    plt.show()
    plt.close()



get_wordcload(['小猪快跑','整天快乐'],'data/wordcloud_mask.png','my/07.png','my/08.png')
get_wordcload(['小猪快跑'],'data/mask_pao.png','my/07_pao.png','my/08_pao.png')
get_wordcload(['整天快乐'],'data/mask_run.png','my/07_run.png','my/08_run.png')
