# -*- coding: utf-8 -*-

"""
项目：写字等级考试数据处理

模块：csv数据文件按{"等级"、"区"}拆分成下发xlsx

输入：
  -
    文件：区成绩数据
    格式：csv
    编码：utf-8
    字段：区，年级，学校名称，学生姓名，学生学籍号，区毛笔成绩，区硬笔成绩，备注：
  -
    文件：考生抽样数据
    格式：csv
    编码：utf-8
    字段：区，年级，学校名称，考场代码，座位号，学生姓名，学生学籍号：
  -
    文件：市成绩数据
    格式：csv
    编码：utf-8
    字段：区，年级，学校名称，学生姓名，学生学籍号，区毛笔成绩，区硬笔成绩，市毛笔成绩，市硬笔成绩，备注
输出：
  -
    文件：等值参数
    格式：csv
    编码：utf-8
    字段：区，等值，区阅毛笔成绩平均，区阅毛笔成绩标准差，区阅硬笔成绩平均，区阅硬笔成绩标准差，
         市阅毛笔成绩平均，市阅毛笔成绩标准差，市阅硬笔成绩平均，市阅硬笔成绩标准差

  -
    文件：成绩等第
    格式：csv
    编码：utf-8
    字段：区，年级，学校名称，学生姓名，学生学籍号，毛笔等第，硬笔等第，备注：

"""

import pandas as pd
import numpy as np


class Split(object):
    """
    csv文件拆分类
    """

    def read(self):
        dtype = dict()

        key = "学籍号"
        value = str
        dtype[key] = value
        df = pd.read_csv("../data.in/2018/等第.csv", dtype=dtype)
        df = df.dropna(subset=["学生姓名"])

        level = df["等级"].unique()
        print(level)
        city = df["区"].unique()
        print(city)

        for l in level:
            df_l = df[df["等级"]==l]
            for c in city:
                xlsx_file = "../data.out/2018/equating/" + c + l + ".xlsx"
                print(xlsx_file)
                df_c = df_l[df_l["区"] == c]
                df_c = df_c[["学校名称","学生姓名","学籍号","硬笔等第","毛笔等第","备注"]]
                df_c['学籍号'] = df_c['学籍号'].astype(str)

                #print(df_c["学籍号"])
                writer = pd.ExcelWriter(xlsx_file)
                df_c.to_excel(writer, l)
                writer.save()

def main():
    split = Split()


    split.read()


    return 0

if __name__ == '__main__':
    main()