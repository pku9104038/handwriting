# -*- coding: utf-8 -*-

"""
项目：写字等级考试数据处理

模块：报名数据合并

输入：
  -
    文件：各区报名数据
    格式：excel
    编码：utf-8/gbk
    字段：学校名称，考场代码，座位号，学生姓名，学生学籍号
输出：
  -
    文件：合并报名数据
    格式：csv
    编码：utf-8
    字段：等级，区，学校名称，考场代码，座位号，学生姓名，学生学籍号

"""
import yaml
import numpy as np
import pandas as pd

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
        文件：报名数据处理配置文件
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
        self.module = "registration"

        # 报名数据处理配置初始化
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
               self.union["copy"]["subdir"] +  self.union["copy"]["file"]

    @property
    def copy_sheet(self):
        return  self.union["copy"]["sheet"]

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
            elif i['type'] == "int":
                value = np.int32
            dtype[key] = value
        return dtype

    @property
    def col_names(self):
        names = list()
        for i in self.union["columns"]:
            names.append(i['name'])
        return names


class Registration(object):
    """
    报名数据处理类
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
            for l in levels:

                # 读取xlsx报名表格
                level = l["level"]
                file = l["file"]
                sheet = l["sheet"]
                row = l["row"]

                xlsx_path = self.cfg.input_dir + file
                df = pd.DataFrame()
                df = pd.read_excel(xlsx_path, sheet_name=sheet, skiprows=row-1)

                # 重命名列名称
                for col in l["columns"]:
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
                df[col_name] = df[col_name].astype(str)
            elif col_type == "int":
                df[col_name] = df[col_name].astype(np.int32)


        # 输出并复制到下一流程（抽样）的数据输入目录
        csv_path = self.cfg.output_file + ".csv"
        print(csv_path)
        df_u.to_csv(csv_path, index=False)

        csv_path = self.cfg.copy_file + ".csv"
        print(csv_path)
        df_u.to_csv(csv_path, index=False)

        xlsx_file = self.cfg.output_file + ".xlsx"
        print(xlsx_file)
        writer = pd.ExcelWriter(xlsx_file)
        df_u.to_excel(writer, self.cfg.output_sheet)
        writer.save()
        writer.close()

        xlsx_file = self.cfg.copy_file + ".xlsx"
        print(xlsx_file)
        writer = pd.ExcelWriter(xlsx_file)
        df_u.to_excel(writer, self.cfg.copy_sheet)
        writer.save()
        writer.close()



def main():
    conf = Config()
    print(conf.year)
    print(conf.dir)
    print(conf.subdir)
    print(conf.config_file)
    print(conf.definition)
    print(conf.process)

    reg = Registration(conf)
    reg.union()

    return 0

if __name__ == '__main__':
    main()
