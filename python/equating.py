# -*- coding: utf-8 -*-

"""
项目：写字等级考试数据处理

模块：成绩等值程序

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

import config as cfg
import pandas as pd
import numpy as np


class Equating(object):
    """
    成绩等值处理类
    """

    def __init__(self):
        """
        初始化Configuration配置实例属性cfg
        """
        self.cfg = cfg.Configuration()

    def ramdon_score(self):
        csv_path = self.cfg.equating_input_dir + \
                   self.cfg.equating_random_registration
        df = pd.read_csv(csv_path)

        df = df.drop({"考场代码", "座位号"}, axis=1)
        nrow = len(df.index)
        df["毛笔成绩"] = np.random.randint(low=20, high=40, size=(nrow, 1))
        df["硬笔成绩"] = np.random.randint(low=30, high=60, size=(nrow, 1))
        print(df)
        csv_path = self.cfg.equating_input_dir + \
                   self.cfg.equating_input_city_score
        df.to_csv(csv_path, index=False)

    def sample_score(self):
        csv_path = self.cfg.equating_input_dir + \
                   self.cfg.equating_input_pre_sample
        df = pd.read_csv(csv_path)
        # print(df)
        csv_path = self.cfg.equating_input_dir + \
                   self.cfg.equating_input_city_score
        df2 = pd.read_csv(csv_path)
        # df2 = df2.drop({"区","年级","学校名称","学生姓名"}, axis=1)
        df = df.merge(right=df2, on=["区", "年级", "学校名称", "学生姓名", "学生学籍号"], how='left')
        df = df.drop({"Unnamed: 0"}, axis=1)
        df = df.rename(columns={"毛笔成绩": "区阅毛笔成绩", "硬笔成绩": "区阅硬笔成绩"})
        csv_path = self.cfg.equating_output_dir + \
                   self.cfg.equating_output_sample_score
        df.to_csv(csv_path, index=False)

        nrow = df.shape[0]
        df["市阅毛笔成绩"] = np.random.randint(low=10, high=40, size=(nrow, 1))
        df["市阅硬笔成绩"] = np.random.randint(low=20, high=60, size=(nrow, 1))

        csv_path = self.cfg.equating_output_dir + \
                   self.cfg.equating_output_reviewed_score
        df.to_csv(csv_path, index=False)

    def statistics(self):
        csv_path = self.cfg.equating_input_dir + \
                   self.cfg.equating_input_reviewed_score
        df = pd.read_csv(csv_path)
        df = df.drop({"考场代码"},axis=1)
        group_key = self.cfg.equating_statistics_group

        df_agg = df.groupby(by=group_key).agg(['mean','std'])
        df_stat = pd.DataFrame()
        df_stat["区"] = pd.Series(df_agg.index)

        for i in df_agg.columns.levels[0]:
            for j in df_agg.columns.levels[1]:
                df_stat[i+j] = pd.DataFrame(list(df_agg[i,j]),columns={i+j})
        print(df_stat)

        csv_path = self.cfg.equating_output_dir + \
                   self.cfg.equating_output_score_statistics
        df_stat.to_csv(csv_path,index=False)


def main():
    equating = Equating()

    # equating.ramdon_score()

    # equating.sample_score()

    equating.statistics()

    return 0


if __name__ == '__main__':
    main()
