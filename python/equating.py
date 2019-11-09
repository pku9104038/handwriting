# -*- coding: utf-8 -*-

"""
项目：写字等级考试数据处理

模块：成绩等值程序

输入：
  -
    文件：区成绩数据
    格式：csv
    编码：utf-8
    字段：等级，区，学校名称，学生姓名，学生学籍号，毛笔成绩，硬笔成绩，备注：
  -
    文件：市成绩统计数据
    格式：csv
    编码：utf-8
    字段：等级,区,区阅硬笔成绩_mean,区阅硬笔成绩_std,市阅硬笔成绩_mean,
        市阅硬笔成绩_std,区阅毛笔成绩_mean,区阅毛笔成绩_std,市阅毛笔成绩_mean,市阅毛笔成绩_std
  -
    文件：市成绩数据
    格式：csv
    编码：utf-8
    字段：等级,区,学校名称,学生学籍号,学生姓名,区阅硬笔成绩,市阅硬笔成绩,区阅毛笔成绩,市阅毛笔成绩
输出：
  -
    文件：成绩等第
    格式：csv
    编码：utf-8
    字段：区，年级，学校名称，学生姓名，学生学籍号，毛笔等第，硬笔等第，备注：

"""

import config as cfg
import pandas as pd
import numpy as np
import yaml

class Config(object):
    """
    配置类

    输入：
      -
        文件：项目配置文件
        格式：yaml
        编码：utf-8
        配置内容：年度、目录结构、配置文件名
      -
        文件：成绩等值处理配置文件
        格式：yaml
        编码：utf-8
        配置内容：公共定义、数据处理配置参数

    输出：
      配置类实例
    """

    def __init__(self):
        # 基本项目配置初始化
        conf_yaml = "conf.yaml"
        yaml_obj = yaml.load(open(conf_yaml))

        self.year = yaml_obj.get("year")
        self.cfg = yaml_obj.get("config")

        self.dir = self.cfg["dir"]
        self.yeardir = self.year + "/"
        self.subdir = self.cfg["subdir"]
        self.config_file = self.cfg["file"]
        self.module = "equating"

        # 数据处理配置初始化
        conf_yaml = self.dir["yaml"] + self.yeardir \
                    + self.config_file[self.module]

        yaml_obj = yaml.load(open(conf_yaml))

        self.definition = yaml_obj.get("definition")
        self.process = yaml_obj.get("process")
        self.input = self.process["input"]

    @property
    def input_dir(self):
        return self.dir["input"] + self.yeardir + self.subdir[self.module]

    @property
    def input_city(self):
        return self.input_dir + self.input["city"]["file"]

    @property
    def city_columns(self):
        names = list()
        for i in self.input["city"]["columns"]:
            names.append(i['name'])
        return names

    @property
    def city_dtype(self):
        dtype = dict()
        for i in self.input["city"]["columns"]:
            key = i['name']
            if i['type'] == "string":
                value = str
            elif i['type'] == "int":
                value = np.int32
            elif i['type'] == "number":
                value = np.float
            else:
                value = str
            dtype[key] = value
        return dtype

    @property
    def input_review(self):
        return self.input_dir + self.input["review"]["file"]

    @property
    def review_columns(self):
        names = list()
        for i in self.input["review"]["columns"]:
            names.append(i['name'])
        return names

    @property
    def review_dtype(self):
        dtype = dict()
        for i in self.input["review"]["columns"]:
            key = i['name']
            if i['type'] == "string":
                value = str
            elif i['type'] == "int":
                value = np.int32
            elif i['type'] == "number":
                value = np.float
            else:
                value = str
            dtype[key] = value
        return dtype

    @property
    def input_stat(self):
        return self.input_dir + self.input["stat"]["file"]

    @property
    def stat_columns(self):
        names = list()
        for i in self.input["stat"]["columns"]:
            names.append(i['name'])
        return names

    @property
    def stat_dtype(self):
        dtype = dict()
        for i in self.input["stat"]["columns"]:
            key = i['name']
            if i['type'] == "string":
                value = str
            elif i['type'] == "int":
                value = np.int32
            elif i['type'] == "number":
                value = np.float
            else:
                value = str
            dtype[key] = value
        return dtype

    @property
    def output_dir(self):
        return self.dir["output"] + self.yeardir + self.subdir[self.module]



    @property
    def col_level(self):
        return self.definition["columns"]["level"]

    @property
    def col_writing(self):
        return self.definition["columns"]["writing"]

    @property
    def col_city(self):
        return self.definition["columns"]["city"]

    @property
    def col_school(self):
        return self.definition["columns"]["school"]

    @property
    def col_code(self):
        return self.definition["columns"]["code"]

    @property
    def col_name(self):
        return self.definition["columns"]["name"]





class Equating(object):
    """
    成绩等值处理类
    """

    def __init__(self, config):
        # 基本项目配置初始化
        self.cfg = config

    def process(self):
        """
        读取区阅卷成绩，
        left join市阅卷统计
        计算等值分数
        left join市阅卷成绩
        等值成绩 = 市阅成绩（抽样试卷）
        等值成绩 = 区阅成绩（豁免区）
        输出等第
        :return:
        """

        # 区阅卷成绩
        path = self.cfg.input_city + ".csv"
        print(path)
        df_c = pd.DataFrame()
        df_c = pd.read_csv(path,
                         names=self.cfg.city_columns,
                         skiprows=1, low_memory=False,
                         dtype=self.cfg.city_dtype)

        xlsx_path = "../data.out/2018/score/absent1.xlsx"
        df_q = pd.DataFrame()
        df_q = pd.read_excel(xlsx_path, sheet_name="Sheet 1", skiprows=0,
                              converters={"学生学籍号": str})
        df_q["缺考"] = True
        df_q = df_q[["学生学籍号","学生姓名","区","学校","缺考"]]
        df_q = df_q.rename(columns={"学校": "学校名称"})
        print(df_c.columns)
        print(df_q.columns)

        df_c = df_c.merge(df_q, how="left", on=["学生学籍号","学生姓名","区","学校名称"])

        idx = df_c[df_c["缺考"]==True].index
        print("缺考")
        print(idx)
        df_i = df_c[df_c["缺考"]==True]
        df_i = df_i[df_i["硬笔成绩"]<1]
        idx1 = df_i.index
        print("硬笔成绩")
        print(idx1)
        df_c.loc[idx1,"硬笔成绩"] = None

        df_i = df_c[df_c["缺考"]==True]
        df_i = df_i[df_i["毛笔成绩"] < 1]
        idx1 = df_i.index
        print("毛笔成绩")
        print(idx1)
        df_c.loc[idx1, "毛笔成绩"] = None

        # 市阅卷成绩
        path = self.cfg.input_review + ".csv"
        print(path)
        df_r = pd.DataFrame()
        df_r = pd.read_csv(path,
                           names=self.cfg.review_columns,
                           skiprows=1, low_memory=False,
                           dtype=self.cfg.review_dtype)

        xlsx_path = "../data.in/2018/review/E缺考统计表.xlsx"
        df_q1 = pd.DataFrame()
        df_q1 = pd.read_excel(xlsx_path, sheet_name="硬笔一级", skiprows=0,
                           converters={"学籍号": str})
        df_q2 = pd.DataFrame()
        df_q2 = pd.read_excel(xlsx_path, sheet_name="硬笔二级", skiprows=0,
                           converters={"学籍号": str})
        df_q3 = pd.DataFrame()
        df_q3 = pd.read_excel(xlsx_path, sheet_name="毛笔一级", skiprows=0,
                           converters={"学籍号": str})
        df_q4 = pd.DataFrame()
        df_q4 = pd.read_excel(xlsx_path, sheet_name="毛笔二级", skiprows=0,
                           converters={"学籍号": str})

        df_q = pd.DataFrame()
        df_q = df_q1.merge(df_q2,how="left",on="学籍号")
        df_q = df_q.merge(df_q3,how="left",on="学籍号")
        df_q = df_q.merge(df_q4, how="left", on="学籍号")
        df_q = df_q.rename(columns={"学籍号": "学生学籍号"})
        df_q["缺考"] = True
        df_q = df_q[["学生学籍号", "缺考"]]

        df_r = df_r.merge(df_q, how="left", on="学生学籍号")
        df_r = df_r[df_r["缺考"] != True]

        df_r = df_r[df_r["区阅硬笔成绩"] > 0.5]
        df_r = df_r[df_r["市阅硬笔成绩"] > 0.5]
        df_r = df_r[df_r["区阅毛笔成绩"] > 0.5]
        df_r = df_r[df_r["市阅毛笔成绩"] > 0.5]

        #print(df_r)

        # 阅卷成绩统计
        path = self.cfg.input_stat + ".csv"
        print(path)
        df_s = pd.DataFrame()
        df_s = pd.read_csv(path,
                           names=self.cfg.stat_columns,
                           skiprows=1, low_memory=False,
                           dtype=self.cfg.stat_dtype)

        df = df_c.merge(df_s,how='left', on=["等级","区"])
        print(df.columns)

        """
        idx1 = df[df["区"]=="嘉定区"].index

        idx2 = df[df["区"]!="嘉定区"].index

        df.loc[idx1, "硬笔等值"] = df.loc[idx1, "硬笔成绩"]
        df.loc[idx1, "毛笔等值"] = df.loc[idx1, "毛笔成绩"]


        df.loc[idx2, "硬笔等值"] = df.loc[idx2, "市阅硬笔成绩_mean"] + \
                               (df.loc[idx2, "硬笔成绩"]-df.loc[idx2, "区阅硬笔成绩_mean"]) / \
                               df.loc[idx2,"区阅硬笔成绩_std"] * df.loc[idx2,"市阅硬笔成绩_std"]
        df.loc[idx2, "毛笔等值"] = df.loc[idx2, "市阅毛笔成绩_mean"] + \
                               (df.loc[idx2, "毛笔成绩"] - df.loc[idx2, "区阅毛笔成绩_mean"]) / \
                               df.loc[idx2, "区阅毛笔成绩_std"] * df.loc[idx2, "市阅毛笔成绩_std"]
        
        """

        df1 = df[df["区"] == "嘉定区"]
        df1.loc[:, "硬笔等值"] = df1.loc[:, "硬笔成绩"]
        df1.loc[:, "毛笔等值"] = df1.loc[:, "毛笔成绩"]

        df2 = df[df["区"] != "嘉定区"]
        df2.loc[:, "硬笔等值"] = df2.loc[:, "市阅硬笔成绩_mean"] + \
                               (df2.loc[:, "硬笔成绩"] - df2.loc[:, "区阅硬笔成绩_mean"]) / \
                               df2.loc[:, "区阅硬笔成绩_std"] * df2.loc[:, "市阅硬笔成绩_std"]
        df2.loc[:, "毛笔等值"] = df2.loc[:, "市阅毛笔成绩_mean"] + \
                               (df2.loc[:, "毛笔成绩"] - df2.loc[:, "区阅毛笔成绩_mean"]) / \
                               df2.loc[:, "区阅毛笔成绩_std"] * df2.loc[:, "市阅毛笔成绩_std"]
        df = df1.append(df2)

        idx = df[df["硬笔成绩"].isnull()].index
        df.loc[idx, "硬笔等值"] = None

        idx = df[df["硬笔成绩"] > 40].index
        df.loc[idx, "硬笔等值"] = 40

        idx = df[df["硬笔成绩"] < 0.5 ].index
        df.loc[idx, "硬笔等值"] = 0

        idx = df[df["毛笔成绩"].isnull()].index
        df.loc[idx, "毛笔等值"] = None

        idx = df[df["毛笔成绩"] > 60].index
        df.loc[idx, "毛笔等值"] = 60

        idx = df[df["毛笔成绩"] < 0.5].index
        df.loc[idx, "毛笔等值"] = 0

        print(df["硬笔等值"].count(), df["硬笔等值"].mean())
        print(df["毛笔等值"].count(), df["毛笔等值"].mean())

        df_r["市阅"] = True
        df = df.merge(df_r, how="left", on=["等级","区","学校名称","学生学籍号","学生姓名"])
        idx = df[df["市阅"]==True].index
        df.loc[idx, "硬笔等值"] = df.loc[idx, "市阅硬笔成绩"]
        df.loc[idx, "毛笔等值"] = df.loc[idx, "市阅毛笔成绩"]

        # 总成绩等值
        df["等值"] = df["硬笔等值"] + df["毛笔等值"]



        print(df["硬笔等值"].count(), df["硬笔等值"].mean())
        print(df["毛笔等值"].count(), df["毛笔等值"].mean())

        idx = df[df["硬笔等值"].isnull()].index
        df.loc[idx, "硬笔等第"] = ""
        df.loc[idx, "硬笔处理"] = True

        idx = df[df["硬笔等值"] >= 48].index
        df.loc[idx, "硬笔等第"] = "优秀"
        df.loc[idx, "硬笔处理"] = True

        idx = df[df["硬笔等值"] < 36].index
        df.loc[idx, "硬笔等第"] = "不合格"
        df.loc[idx, "硬笔处理"] = True

        df.loc[df[df["硬笔处理"] != True].index, "硬笔等第"] = "合格"

        #print(df["硬笔等第"])

        idx = df[df["毛笔等值"].isnull()].index
        df.loc[idx, "毛笔等第"] = ""
        df.loc[idx, "毛笔处理"] = True

        idx = df[df["毛笔等值"] >= 32].index
        df.loc[idx, "毛笔等第"] = "优秀"
        df.loc[idx, "毛笔处理"] = True

        idx = df[df["毛笔等值"] < 24].index
        df.loc[idx, "毛笔等第"] = "不合格"
        df.loc[idx, "毛笔处理"] = True

        df.loc[df[df["毛笔处理"] != True].index, "毛笔等第"] = "合格"

        #print(df["毛笔等第"])

        idx = df[df["等值"].isnull()].index
        df.loc[idx, "等第"] = "缺考"
        df.loc[idx, "处理"] = True

        idx = df[df["等值"] >= 80].index
        df.loc[idx, "等第"] = "优秀"
        df.loc[idx, "处理"] = True

        idx = df[df["等值"] < 60].index
        df.loc[idx, "等第"] = "不合格"
        df.loc[idx, "处理"] = True

        df.loc[df[df["处理"] != True].index, "等第"] = "合格"

        #df.loc[df[df["处理"] != True].index, "等第"] = "合格"

        csv_path = "../data.out/2018/equating/成绩等第结果.csv"
        print(csv_path)
        df.to_csv(csv_path, index=False)

        df = df[["等级", "区", "学校名称", "学生学籍号", "学生姓名", "硬笔成绩", "硬笔等值", "硬笔等第",
                   "毛笔成绩", "毛笔等值", "毛笔等第", "等值", "等第", "市阅", "备注"]]
        csv_path = "../data.out/2018/equating/成绩等级复核.csv"
        print(csv_path)
        df.to_csv(csv_path, index=False)

        # print(df["毛笔等第"])

        #self.df = df[["等级","区","学校名称","学生学籍号","学生姓名","硬笔等第","毛笔等第","备注"]]

        #print(self.df)


        level = df["等级"].unique()
        print(level)
        city = df["区"].unique()
        print(city)

        for l in level:
            df_l = df[df["等级"] == l]
            for c in city:
                xlsx_file = "../data.out/2018/equating/" + c + l + ".xlsx"
                print(xlsx_file)
                df_c = df_l[df_l["区"] == c]
                df_c = df_c[["学校名称", "学生姓名", "学生学籍号", "等第", "备注"]]
                df_c['学生学籍号'] = df_c['学生学籍号'].astype(str)

                # print(df_c["学籍号"])
                writer = pd.ExcelWriter(xlsx_file)
                df_c.to_excel(writer, l)
                writer.save()


        df_y = df[["等级", "区", "学校名称", "学生学籍号", "学生姓名", "硬笔等第", "硬笔等值", "市阅", "备注"]]
        df_y.columns = ["等级", "区", "学校名称", "学生学籍号", "学生姓名", " 等第", "等值", "市阅", "备注"]
        df_y.loc[:, "书写"] = "硬笔"
        df_m = df[["等级", "区", "学校名称", "学生学籍号", "学生姓名", "毛笔等第", "毛笔等值", "市阅", "备注"]]
        df_m.columns = ["等级", "区", "学校名称", "学生学籍号", "学生姓名", " 等第", "等值", "市阅", "备注"]
        df_m["书写"] = "毛笔"
        df_u = df_y.append(df_m)

        csv_path = "../data.out/2018/equating/成绩等第数据分析.csv"
        print(csv_path)
        df_u.to_csv(csv_path, index=False)


def main():
    conf = Config()
    equating = Equating(conf)

    equating.process()

    return 0


if __name__ == '__main__':
    main()
