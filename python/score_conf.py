# -*- coding: utf-8 -*-


"""
项目：写字等级考试数据处理

模块：上报成绩处理配置
"""

import yaml
import numpy as np

class Configuration(object):

    """
    项目配置

    输入：
      -
        文件：项目配置文件
        格式：yaml
        编码：utf-8
        配置内容：年度配置文件
      -
        文件：上报成绩处理配置文件
        格式：yaml
        编码：utf-8
        配置内容：运行环境，数据处理开关，数据输入输出

    输出：
      配置数据实例
    """

    def __init__(self):
        #if not conf_yaml:
        conf_yaml = "../yaml/conf.yaml"
        yaml_obj = yaml.load(open(conf_yaml)).get("conf")
        self.dir = yaml_obj["dir"]
        configuration_yaml = yaml_obj["file"]["configuration"]
        yaml_path = self.dir["yaml"]+configuration_yaml
        self.conf = yaml.load(open(yaml_path)).get("configuration")

    @property
    def input_dir(self):
        return self.dir["input"]

    @property
    def score_input_dir(self):
        return self.dir["input"] + self.sample["score"]["dir"]

    @property
    def score_output_file(self):
        return self.dir["output"] + self.sample["output"]["dir"] + self.sample["score"]["file"]

    @property
    def sample(self):
        return self.conf["sample"]

    @property
    def sample_union(self):
        return self.sample["union"]

    @property
    def score_union(self):
        return self.sample["score_union"]

    @property
    def union_dtype(self):
        dtype = dict()
        for i in self.sample["union_dtype"]:
            key = i['name']
            if i['type'] == "string":
                value = str
            elif i['type'] == "int":
                value = np.int32
            dtype[key] = value
        return dtype

    @property
    def score_dtype(self):
        dtype = dict()
        for i in self.sample["score_dtype"]:
            key = i['name']
            if i['type'] == "string":
                value = str
            elif i['type'] == "int":
                value = np.int32
            dtype[key] = value
        return dtype

    @property
    def union_columns(self):
        return list(self.sample["union_columns"].values())

    @property
    def sample_input_dir(self):
        return self.dir["input"] + self.sample["input"]["dir"]

    @property
    def sample_input(self):
        return self.sample_input_dir + self.sample["input"]["file"]

    @property
    def sample_output_dir(self):
        return self.dir["output"] + self.sample["output"]["dir"]

    @property
    def sample_output_file(self):
        return self.sample["output"]["file"]


    @property
    def sample_columns(self):
        return list(self.sample["columns"].values())

    @property
    def sample_dtype(self):
        dtype = dict()
        for i in self.sample["dtype"]:
            key = i['name']
            if i['type'] == "string":
                value = str
            elif i['type'] == "int":
                value = np.int32
            dtype[key] = value
        return dtype



    @property
    def sample_drop(self):
        return self.sample["drop"]

    @property
    def sample_ignore(self):
        return self.sample["ignore"]

    @property
    def sample_criterion(self):
        return self.sample["criterion"]

    @property
    def sample_criterion_limit(self):
        return self.sample_criterion["limit"]

    @property
    def sample_criterion_rate(self):
        return self.sample_criterion["rate"]

    @property
    def sample_criterion_filter(self):
        return self.sample_criterion["filter"]

    @property
    def equating(self):
        return self.conf["equating"]

    @property
    def equating_random_registration(self):
        return self.equating["random"]["registration"]

    @property
    def equating_input_dir(self):
        return self.input_dir + self.equating["input"]["dir"]

    @property
    def equating_input_city_score(self):
        return self.equating["input"]["city_score"]

    @property
    def equating_input_pre_sample(self):
        return self.equating["input"]["pre_sample"]

    @property
    def equating_output_dir(self):
        return self.dir["output"] + self.equating["output"]["dir"]

    @property
    def equating_output_sample_score(self):
        return self.equating["output"]["sample_score"]

    @property
    def equating_output_reviewed_score(self):
        return self.equating["output"]["reviewed_score"]

    @property
    def equating_output_score_statistics(self):
        return self.equating["output"]["score_statistics"]

    @property
    def equating_input_reviewed_score(self):
        return self.equating["input"]["reviewed_score"]

    @property
    def equating_statistics_group(self):
        return self.equating["statistics"]["group"]







def main():
    conf = Configuration()
    print(conf)
    print(conf.sample_output_school)
    print(type(conf.sample_columns))
    print(conf.sample_columns)

    print(type(conf.sample_dtype))
    print(conf.sample_dtype)


    return 0

if __name__ == '__main__':
    main()
