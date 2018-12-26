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
    文件：合并成绩数据
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

                # 保留有效列
                # df = df[self.cfg.col_names]

                # 增加 "等级"， "区"
                df[self.cfg.col_level] = level
                df[self.cfg.col_city] = city


                # 添加到合并数据集
                df_u = df_u.append(df)
                print(df_u.columns)


        # 输出问题校验数据文件
        for col in self.cfg.columns:
            col_name = col["name"]
            df_u[col_name] = df_u[col_name].astype(str)
        print(df_u.columns)
        csv_path = self.cfg.output_file + "问题校验.csv"
        print(csv_path)
        df_u.to_csv(csv_path, index=False)

        # 保留有效列
        df_u = df_u[self.cfg.col_names]

        # 更正数值类型
        for col in self.cfg.columns:
            col_name = col["name"]
            col_type = col["type"]

            if col_type == "string":
                df_u[col_name] = df_u[col_name].astype(str)
                df_u.loc[df_u[col_name] == "nan", col_name] = None
            elif col_type == "number":
                df_u[col_name] = pd.to_numeric(df_u[col_name], errors="coerce")

        print(df_u.dtypes)
        # 输出并复制到下一流程（等值）的数据输入目录
        csv_path = self.cfg.output_file + ".csv"
        print(csv_path)
        df_u.to_csv(csv_path, index=False)

        copy_path = self.cfg.copy_file + ".csv"
        copyfile(csv_path, copy_path)



    def check_city(self):
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

        # 区成绩校验
        df_agg = df.groupby(by=["等级","区"]).agg('mean')
        df_agg["check"] = df_agg["硬笔成绩"] < df_agg["毛笔成绩"]
        df_agg = df_agg[df_agg["check"]==True]
        print(df_agg)
        csv_path = self.cfg.output_file + "_区检查.csv"
        print(csv_path)
        df_agg.to_csv(csv_path, index=True)

    def check_school(self):
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

        # 学校成绩校验
        df_agg = df.groupby(by=["等级","区","学校名称"]).agg('mean')
        df_agg["check"] = df_agg["硬笔成绩"] < df_agg["毛笔成绩"]
        df_agg = df_agg[df_agg["check"]==True]
        print(df_agg)
        csv_path = self.cfg.output_file + "_校检查.csv"
        print(csv_path)
        df_agg.to_csv(csv_path, index=True)

    def check_room(self):
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

        # 考场成绩校验
        df_agg = df.groupby(by=["等级","区","学校名称","考场代码"]).agg('mean')
        df_agg["check"] = df_agg["硬笔成绩"] < df_agg["毛笔成绩"]
        df_agg = df_agg[df_agg["check"]==True]
        print(df_agg)
        csv_path = self.cfg.output_file + "_考场检查.csv"
        print(csv_path)
        df_agg.to_csv(csv_path, index=True)

    def check_student(self):
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

        # 学生成绩校验
        df_agg = df.groupby(by=["等级","区","学校名称","学生学籍号"]).agg('mean')
        df_agg["check1"] = df_agg["硬笔成绩"] < df_agg["毛笔成绩"] - 10
        df_agg["check2"] = df_agg["硬笔成绩"] > 0
        df_agg = df_agg[df_agg["check1"]]
        df_agg = df_agg[df_agg["check2"]]
        #df_agg = df_agg[df_agg["check"]==True]
        print(df_agg)

        path = self.cfg.output_file + "_考生检查.xlsx"
        print(path)
        writer = pd.ExcelWriter(path)
        df_agg.to_excel(writer)
        writer.save()


    def check_error(self):
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

        # 学生成绩校验
        df_err = pd.DataFrame()
        df_e1 = df[df["硬笔成绩"] > 60]
        print(df_e1)
        df_e2 = df[df["硬笔成绩"]<0]
        print(df_e2)
        df_e3 = df[df["毛笔成绩"] > 40]
        print(df_e3)
        df_e4 = df[df["毛笔成绩"] < 0]
        print(df_e4)
        df_err = df_err.append(df_e1)
        df_err = df_err.append(df_e2)
        df_err = df_err.append(df_e3)
        df_err = df_err.append(df_e4)
        print(df_err)

        csv_path = self.cfg.output_file + "_成绩错误.csv"
        print(csv_path)
        df_err.to_csv(csv_path, index=True)


def main():
    conf = Config()
    score = Score(conf)

    score.union()

    """
    score.check_city()

    score.check_school()

    score.check_room()

    score.check_student()

    score.check_error()
    """



    return 0


if __name__ == '__main__':
    main()
