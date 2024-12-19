import numpy as np
# 正态分布样本数据:温度测量
np.random.seed(100)
temperature = np.random.normal(loc=25, scale=3, size=1000)  # 平均值=25，StdDev=3
# 保存数据
np.savetxt("temperature_data.csv", temperature, delimiter=",")
print("温度数据保存到'temperature_data.csv'")

# 均匀分布样本数据:电压波动
np.random.seed(101)
voltage = np.random.uniform(low=10, high=20, size=1000)  # 最小值=10，最大值=20
# 保存数据
np.savetxt("voltage_data.csv", voltage, delimiter=",")
print("电压数据保存到'voltage_data.csv'中")

# 指数分布样本数据:组件寿命
np.random.seed(102)
lifespan = np.random.exponential(scale=5, size=1000)  # 平均值=5
# 保存数据
np.savetxt("lifespan_data.csv", lifespan, delimiter=",")
print("寿命数据保存到'lifespan_data.csv'")