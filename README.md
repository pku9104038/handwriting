# 上海市写字等级考试数据处理

## 业务流程

![](./res/business-flow.png)

## 抽样原则
1. 三线学校不参与抽样
2. 个别优秀区不参与抽样
3. 抽样率约为考生数的5%
4. 以考场为单位抽样
5. 原则上只抽所在学校第一考场

## 成绩等值

### 项目反应理论（IRT）

#### 单参数模式（Rasch模式）

只有一个项目参数——难度（b值）

考生答对题目的概率
Pi = exp(theta-bi)/(1+exp(theta-bi))
theta: 考生的能力
bi: 项目i的难度
初始能力值
theta0 = ln(r/(l-r))
L: 总项目数
r: 答对数
初始难度
b0 = ln((N-S)/S)
N: 考生总数
S: 答对的考生数

#### 双参数模式

Pi(theta) = exp(-D ai(theta-bi))/(1+exp(-D ai(theta-bi)))
ai:项目i的区分度

#### 三参数模式

Pi(theta) = ci + (1-ci)exp(-D ai(theta-bi))/(1+exp(-D ai(theta-bi)))
ci: 项目i猜测程度
D: 调节因子， = 1.7

#### Rasch模式难度值和能力值计算

1. 各题初始难度值
di0 = ln((N-Si)/Si)
N: 总人数
Si: 答对第i题的人数
2. 计算中间值
Y1 = sum(Pr) , r from 1 to L-1
Y2 = sum(Pr*Qr) , r from 1 to L-1
Pr = exp(br-di)/(1+exp(br-di))
Qr = 1 - Pr
3. 计算各题第n次迭代的难度值din
din = din + (Y1-Si)/Y2
检验 abs((Y1-Si)/Y2)是否小于E1 （一般设E1=0.01）
如不满足，回到步骤2. 3.
4. 零化
din = din - sum(din)/L , i from 1 to L
5. 计算答对r=1 至 L-1 题的初始能力值br0
br0 = ln(r/(L-r))
L: 总题目数
r: 答对题数
6. 计算中间值
Y1 = sum(Pr) , r from 1 to L
Y2 = sum(Pr*Qr) , r from 1 to L
Pr = exp(br-di)/(1+exp(br-di))
Qr = 1 - Pr
7. 计算各个答对率r第n次迭代第能力值brn
brn = brn+(r-Y1)/Y2
检验 abs((r-Y1)/Y2)是否小于等于E1
如不满足，回到步骤6. 7.
8. 检验 abs(sum(din-di(n-1)))/4是否小于等于E2 (一般设为0.0001)
如不满足，回到步骤2计算di(n+1)  
9. 计算每题难度值的标准误差Se(di)
Se(di) = 1/sqrt(sum(PriQri)) , r from 1 to N
10. 计算答对r=1 至 L-1题的能力值的标准误差Se(br)
Se(br)=1/sqrt(sum(PriQri)) , i from 1 to L

有了各题难度值di，计算出答对C题的能力值theta及将theta转换成概率P

11. 难度值调整公式
di调=(di原-A)/B
A, B 为回归系数
B = (n*sum(XiYi) - sum(Xi) * sum(Yi))/(n*sum(power(X,2))-power(sum(X),2))
A = (sum(Yi)-B*sum(Xi))/n
Xi, Yi为两组连接项目的难度值
n为连接项目题数
12. 从难度值di求thetar
thetar = thetar(n-1)-E
E = 1.7*(r-sum(Qi/(1+Qi)))/(-power(1.7,2) * sum(Qi/(1+Qi))) , i from 1 to L
thetar = ln(r/(L-r))
r为答对题数， L为总题数
Q = exp(1.7*thetar(n-1)-di)
当abs(E)小于等于0.001时结束
13. 从thetar求概率P
P=exp(thetar)/(1+exp(thetar))
