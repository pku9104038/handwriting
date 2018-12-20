# -*- coding: utf-8 -*-

"""
项目：写字等级考试数据处理

模块：市阅卷成绩数据合并

输入：
  -
    文件：市、区阅卷成绩数据
    格式：excel
    编码：utf-8/gbk
    字段：学校名称，考场代码，座位号，学生姓名，学生学籍号，区阅硬笔成绩，区阅毛笔成绩，市阅硬笔成绩，市阅毛笔成绩
输出：
  -
    文件：市阅，区阅统计数据
    格式：csv
    编码：utf-8
    字段：等级，书写，区，区阅硬笔成绩平均，区阅毛笔成绩标准差，市阅硬笔成绩平均，市阅毛笔成绩标准差

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
        文件：市阅、区阅成绩数据处理配置文件
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
        self.module = "review"

        # 数据处理配置初始化
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
    def output_file_stat(self):
        return self.output_dir + self.union["output"]["stat"]

    @property
    def output_sheet(self):
        return self.union["output"]["sheet"]

    @property
    def copy_file(self):
        return self.union["copy"]["dir"] + self.yeardir + \
               self.union["copy"]["subdir"] + self.union["copy"]["file"]

    @property
    def copy_file_stat(self):
        return self.union["copy"]["dir"] + self.yeardir + \
               self.union["copy"]["subdir"] + self.union["copy"]["stat"]

    @property
    def copy_sheet(self):
        return self.union["copy"]["sheet"]

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


class Review(object):
    """
    市阅成绩数据处理类
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
            level = i["level"]
            writings = i["writing"]
            print(level)
            df_y = pd.DataFrame()
            df_m = pd.DataFrame()
            for w in writings:

                # 读取xlsx表格
                writing = w["writing"]
                print(writing)
                file = w["file"]
                sheet = w["sheet"]
                row = w["row"]
                dtype = dict()
                if not (w["converters"] is None):
                    for c in w["converters"]:
                        key = c['name']
                        if c['type'] == "string":
                            value = str
                        elif c['type'] == "int":
                            value = np.int32
                        elif c['type'] == "number":
                            value = np.float
                        else:
                            value = str
                        dtype[key] = value


                xlsx_path = self.cfg.input_dir + file
                df = pd.DataFrame()
                df = pd.read_excel(xlsx_path, sheet_name=sheet, skiprows=row-1, converters=dtype)

                # 重命名列名称
                if not (w["columns"] is None):
                    for col in w["columns"]:
                        df[col["out"]] = df[col["in"]]


                # 增加 "等级"， "书写"
                df[self.cfg.col_level] = level
                df[self.cfg.col_writing] = writing

                if writing == "毛笔":
                    df_m = df.copy()
                else:
                    df_y = df.copy()

            # 合并硬笔毛笔成绩
            df = df_y.merge(df_m, how="left",on=[self.cfg.col_code,
                                                 self.cfg.col_city,
                                                 #self.cfg.col_writing,
                                                 self.cfg.col_school,
                                                 self.cfg.col_name,
                                                 self.cfg.col_level])

            print(df.columns)

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


        # 输出并复制到下一流程（等值）的数据输入目录
        csv_path = self.cfg.output_file + ".csv"
        print(csv_path)
        df_u.to_csv(csv_path, index=False)

        copy_path = self.cfg.copy_file + ".csv"
        copyfile(csv_path, copy_path)

        df_agg = df_u.groupby(by=["等级","区"]).agg(['mean','std'])
        print(df_agg)
        csv_path = self.cfg.output_file_stat + ".csv"
        #df_agg.columns = df_agg.columns.get_level_values(0)
        df_agg.columns = ['_'.join(col).strip() for col in df_agg.columns.values]
        df_agg.to_csv(csv_path, index=True)

        copy_path = self.cfg.copy_file_stat + ".csv"
        copyfile(csv_path, copy_path)


def main():
    conf = Config()
    review = Review(conf)

    review.union()



    return 0


if __name__ == '__main__':
    main()
