# -*- coding: utf-8 -*-

"""
项目：写字等级考试数据处理

模块：抽样程序

输入：
  -
    文件：报名数据
    格式：csv
    编码：utf-8
    字段：区，年级，学校名称，考场代码，座位号，学生姓名，学生学籍号：
输出：
  -
    文件：考场抽样数据
    格式：csv
    编码：utf-8
    字段：区，学校名称，考场代码：

  -
    文件：考生抽样数据
    格式：csv
    编码：utf-8
    字段：区，年级，学校名称，考场代码，座位号，学生姓名，学生学籍号：

"""

import config as cfg
import pandas as pd
import numpy as np
import math

class Sample(object):
    """
    报名数据抽样类

    """
    def __init__(self):
        """
        初始化Configuration配置实例属性cfg
        """
        self.cfg = cfg.Configuration()

    def union_xlsx(self):
        """
        从原始xlsx上报文件提取数据存入csv
        :return:
        """


    def union_input(self):
        """
        从各区csv文件读取数据，并按照文件命名规则提取"区"，"年级"信息，补全数据字段
        将数据写入sample_input指定的csv文件
        :return:
        """
        unions = self.cfg.sample_union
        dir = self.cfg.sample_input_dir
        df_csv = pd.DataFrame()
        for u in unions:
            df = pd.DataFrame()
            print(u, u[len(u)-5], u[: len(u)-5])
            df = pd.read_csv(dir+u,
                         names=self.cfg.union_columns,
                         skiprows=1,
                         dtype=self.cfg.union_dtype)
            df["区"] = u[:len(u)-5]
            df["年级"] = u[len(u)-5]+"年级"
            df_csv = df_csv.append(df)
        df_csv.to_csv(self.cfg.sample_input, index=False, columns=self.cfg.sample_columns)

    def read_input(self):
        """
        从csv文件读取输入数据到DataFrame实例属性df
        :return:
        """
        self.df = pd.read_csv(self.cfg.sample_input,
                         names=self.cfg.sample_columns,
                         skiprows=1,
                         dtype=self.cfg.sample_dtype)
        self.df["count"] = 1

    def drop(self):
        """
        抛弃df无用的列
        :return:
        """
        self.df = self.df.drop(columns=self.cfg.sample_drop, axis=1)


    def ignore(self):
        """
        忽略无需抽样的区和报名数据有误的学校数据
        :return:
        """
        for i in self.cfg.sample_ignore:
            key = i["key"]
            for value in i["values"]:
                self.df = self.df[self.df[key]!=value]


    def limit(self):
        """
        报名学生数量未达限额的学校不参与抽样
        :return:
        """
        group_key = self.cfg.sample_criterion_limit["group"]
        scope_key = self.cfg.sample_criterion_limit["scope"]
        min = self.cfg.sample_criterion_limit["min"]
        groups = self.df[group_key].unique()
        df_in = self.df.copy()
        for g in groups:
            df_g = df_in[df_in[group_key] == g]
            df_agg = df_g.groupby(by=scope_key).agg('sum')
            df_agg = df_agg[df_agg["count"]<min]
            for i in df_agg.index:
                self.df = self.df[self.df[scope_key]!=i]

    def rate(self):
        """
        根据抽样率计算各区抽样学校数量（仅抽第一考场）
        :return:
        """
        output_dir = self.cfg.sample_output_dir
        group_key = self.cfg.sample_criterion_rate["group"]
        scope_key = self.cfg.sample_criterion_rate["scope"]
        percent = self.cfg.sample_criterion_rate["percent"]
        grain_key = self.cfg.sample_criterion_rate["grain"]
        grain_size = self.cfg.sample_criterion_rate["grainsize"]
        filter_key = self.cfg.sample_criterion_filter["key"]
        filter_value = self.cfg.sample_criterion_filter["value"]
        groups = self.df[group_key].unique()
        df_in = self.df.copy()

        df_student = pd.DataFrame()
        df_school = pd.DataFrame()
        df_city = pd.DataFrame()
        idx = 1
        for g in groups:

            df_g = df_in[df_in[group_key] == g]
            df_agg = df_g.groupby(by=scope_key).agg('sum')
            df_agg["sample"] = df_agg["count"] * percent / 100.0 / grain_size
            df_agg["sample"] = df_agg["sample"].apply(func=int)
            for i in df_agg.index:
                n = df_agg.loc[i, "sample"]
                scope = i
                df_s = pd.DataFrame(df_g[df_g[scope_key]==scope][grain_key].unique(),
                                    columns=[grain_key]).sample(n)
                df_city = pd.DataFrame()
                df_school = pd.DataFrame()
                for s in df_s[grain_key]:
                    df = pd.DataFrame([[g,scope,s,str(filter_value)]],
                                      index=[idx],
                                      columns=[group_key,scope_key,grain_key,filter_key])
                    idx = idx+1
                    df_school = df_school.append(df)

                    df = df_g[df_g[scope_key]==scope]
                    df = df[df[grain_key] == s]
                    df = df[df[filter_key]==filter_value]
                    df = df.drop(["count"], axis=1)
                    df_student = df_student.append(df)

                    df_city = df_city.append(df)

                #print(df_city)
                xlsx_file = output_dir+scope+g+'.xlsx'
                print(xlsx_file)
                writer = pd.ExcelWriter(xlsx_file)

                # writer = pd.ExcelWriter(output_dir+scope+g+'学校.xlsx')
                df_school.to_excel(writer, "学校")
                writer.save()

                #writer = pd.ExcelWriter(output_dir+scope+g+'学生.xlsx')
                df_city.to_excel(writer, "学生")
                #writer.save()




        print(df_student)
        xlsx_file = output_dir+self.cfg.sample_output_file
        print(xlsx_file)

        writer = pd.ExcelWriter(xlsx_file)
        df_student.to_excel(writer, "硬笔")
        df_student.to_excel(writer, "毛笔")
        writer.save()


    def sample(self):
        return 0


def main():
    sample = Sample()
    sample.union_input()
    #sample.read_input()
    #sample.drop()
    #sample.ignore()
    #sample.limit()
    #sample.rate()


    return 0

if __name__ == '__main__':
    main()