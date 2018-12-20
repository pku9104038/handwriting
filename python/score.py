# -*- coding: utf-8 -*-

"""
项目：写字等级考试数据处理

模块：区阅卷成绩数据合并

输入：
  -
    文件：各区阅卷成绩数据
    格式：excel
    编码：utf-8/gbk
    字段：学校名称，考场代码，座位号，学生姓名，学生学籍号，硬笔书写成绩，毛笔书写成绩，是否缺考作弊，备注
输出：
  -
    文件：合并报名数据
    格式：csv
    编码：utf-8
    字段：等级，书写，区，学校名称，考场代码，座位号，学生姓名，学生学籍号，硬笔区阅成绩，毛笔区阅成绩，缺考作弊，备注

"""
import yaml
import numpy as np
import pandas as pd
from shutil import copyfile


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
        文件：上报成绩数据处理配置文件
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
        self.module = "score"

        # 上报成绩数据处理配置初始化
        conf_yaml = self.dir["yaml"] + self.yeardir \
                    + self.config_file[self.module]

        yaml_obj = yaml.load(open(conf_yaml))

        self.definition = yaml_obj.get("definition")
        self.process = yaml_obj.get("process")
        self.union = self.process["union"]

    @property
    def input_dir(self):
        return self.dir["input"] + self.yeardir + self.subdir[self.module]

    @property
    def output_dir(self):
        return self.dir["output"] + self.yeardir + self.subdir[self.module]

    @property
    def output_file(self):
        return self.output_dir + self.union["output"]["file"]

    @property
    def output_sheet(self):
        return self.union["output"]["sheet"]

    @property
    def copy_file(self):
        return self.union["copy"]["dir"] + self.yeardir + \
               self.union["copy"]["subdir"] + self.union["copy"]["file"]

    @property
    def copy_sheet(self):
        return self.union["copy"]["sheet"]

    @property
    def col_level(self):
        return self.definition["columns"]["level"]

    @property
    def col_city(self):
        return self.definition["columns"]["city"]

    @property
    def columns(self):
        return self.union["columns"]

    @property
    def col_dtype(self):
        dtype = dict()
        for i in self.union["columns"]:
            key = i['name']
            if i['type'] == "string":
                value = str
            elif i['type'] == "number_whole":
                value = np.int32
            elif i['type'] == "number":
                value = np.float
            else:
                value = str
            dtype[key] = value
        return dtype

    @property
    def col_names(self):
        names = list()
        for i in self.union["columns"]:
            names.append(i['name'])
        return names


class Score(object):
    """
    上报成绩数据处理类
    """

    def __init__(self, config):
        # 基本项目配置初始化
        self.cfg = config

    def union(self):
        """
        根据配置文件，循环读取报名数据excel文件，合并输出
        :return:
        """

        df_u = pd.DataFrame()
        inputs = self.cfg.union["input"]
        for i in inputs:
            city = i["city"]
            levels = i["level"]
            print(city)
            for l in levels:

                # 读取xlsx表格
                level = l["level"]
                print(level)
                file = l["file"]
                sheet = l["sheet"]
                row = l["row"]
                dtype = dict()
                if not (l["converters"] is None):
                    for c in l["converters"]:
                        key = c['name']
                        if c['type'] == "string":
                            value = str
                        elif c['type'] == "int":
                            value = np.int32
                        dtype[key] = value


                xlsx_path = self.cfg.input_dir + file
                df = pd.DataFrame()
                df = pd.read_excel(xlsx_path, sheet_name=sheet, skiprows=row-1, converters=dtype)

                # 重命名列名称
                if not (l["columns"] is None):
                    for col in l["columns"]:
                        if len(col["in"]) == 2:
                            df[col["out"]] = df[col["in"][0]].astype(str) + \
                                             df[col["in"][1]].astype(str)
                        else:
                            df[col["out"]] = df[col["in"]]


                # 增加 "等级"， "区"
                df[self.cfg.col_level] = level
                df[self.cfg.col_city] = city

                # 保留有效列
                df = df[self.cfg.col_names]

                # 添加到合并数据集
                df_u = df_u.append(df)


        # 更正数值类型
        for col in self.cfg.columns:
            col_name = col["name"]
            col_type = col["type"]

            if col_type == "string":
                df_u[col_name] = df_u[col_name].astype(str)
                df_u.loc[df_u[col_name] == "nan", col_name] = None
            elif col_type == "number":
                df_u[col_name] = pd.to_numeric(df_u[col_name], errors="coerce")

                # df_u[col_name+"str"] = df_u[col_name].astype(str)
                # 过滤数字列中的文本
                """
                if not (col["filter"] is None):
                    for f in col["filter"]:
                        df_u.loc[df_u[col_name] == f, col_name] = np.nan

                try:
                    df_u[col_name] = df_u[col_name].astype(np.float)
                    print(col_name, df_u[col_name].mean())
                except ValueError:
                    print("ValueError, 请检查数字列是否存在未过滤文本")
                """

                # 异常检查代码，发现异常时开启阅运行
                print(col_name)
                # df_u[col_name] = pd.to_numeric(df_u[col_name],errors="coerce")

                #index = df_u.index
                #for i in index:
                #    if type(df_u.loc[i,col_name]) == str:
                #        print(i,df_u.loc[i,])
                #        df_u.loc[i, col_name] = np.nan
                        #df_u.loc[i, col_name] = df_u.loc[i, col_name].astype(np.float)


        # 输出并复制到下一流程（等值）的数据输入目录
        csv_path = self.cfg.output_file + ".csv"
        print(csv_path)
        df_u.to_csv(csv_path, index=False)

        copy_path = self.cfg.copy_file + ".csv"
        copyfile(csv_path, copy_path)

        """
        xlsx_file = self.cfg.output_file + ".xlsx"
        print(xlsx_file)
        writer = pd.ExcelWriter(xlsx_file)
        df_u.to_excel(writer, self.cfg.output_sheet)
        writer.save()
        writer.close()

        copy_path = self.cfg.copy_file + ".xlsx"
        copyfile(xlsx_file, copy_path)
        """

    def check(self):
        """
        检查上报成绩中存在的异常
        :return:
        """
        path = self.cfg.output_file + ".csv"
        df = pd.DataFrame()
        df = pd.read_csv(path,
                         names=self.cfg.col_names,
                         skiprows=1, low_memory=False,
                         dtype=self.cfg.col_dtype)

        #df = pd.read_excel(path, sheet_name=self.cfg.output_sheet,
        #                   skiprows=0)
        print(df)
        print(self.cfg.col_dtype)
        print(df.dtypes)
        #df["硬笔成绩"] = df["硬笔成绩"].astype(np.float)
        print(df["硬笔成绩"].mean())


def main():
    conf = Config()

    score = Score(conf)
    score.union()

    score.check()


    return 0


if __name__ == '__main__':
    main()
