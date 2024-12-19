import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats

# 加载数据
temperature_data = np.loadtxt('temperature_data.csv', delimiter=',')
voltage_data = np.loadtxt('voltage_data.csv', delimiter=',')
lifespan_data = np.loadtxt('lifespan_data.csv', delimiter=',')

# 计算统计属性
def compute_stats(data):
    mean = np.mean(data)
    std_dev = np.std(data)
    return mean, std_dev

# 计算温度数据的统计属性
temperature_mean, temperature_std = compute_stats(temperature_data)

# 计算电压数据的统计属性
voltage_mean, voltage_std = compute_stats(voltage_data)

# 计算寿命数据的统计属性
lifespan_mean, lifespan_std = compute_stats(lifespan_data)

# 比较正态分布和指数分布的理论与计算值
normal_theoretical_mean = 25
normal_theoretical_std = 3
print(f"Normal Distribution - Theoretical Mean: {normal_theoretical_mean}, Calculated Mean: {temperature_mean}")
print(f"Normal Distribution - Theoretical Std Dev: {normal_theoretical_std}, Calculated Std Dev: {temperature_std}")

exponential_theoretical_mean = 5
exponential_theoretical_std = 5
print(f"Exponential Distribution - Theoretical Mean: {exponential_theoretical_mean}, Calculated Mean: {lifespan_mean}")
print(f"Exponential Distribution - Theoretical Std Dev: {exponential_theoretical_std}, Calculated Std Dev: {lifespan_std}")

# 创建直方图并叠加理论 PDF
def plot_hist_with_pdf(data, title, distribution):
    plt.hist(data, bins=30, density=True, alpha=0.6, label='Data Histogram')
    x = np.linspace(min(data), max(data), 100)
    if distribution == 'normal':
        plt.plot(x, stats.norm.pdf(x, loc=temperature_mean, scale=temperature_std), 'r', label='Fitted Normal PDF')
        plt.plot(x, stats.norm.pdf(x, loc=normal_theoretical_mean, scale=normal_theoretical_std), 'g', label='Theoretical Normal PDF')
    elif distribution == 'exponential':
        plt.plot(x, stats.expon.pdf(x, scale=lifespan_mean), 'r', label='Fitted Exponential PDF')
        plt.plot(x, stats.expon.pdf(x, scale=exponential_theoretical_mean), 'g', label='Theoretical Exponential PDF')
    plt.title(title)
    plt.legend()
    plt.show()

# 绘制温度数据直方图及 PDF
plot_hist_with_pdf(temperature_data, 'Temperature Distribution', 'normal')

# 绘制寿命数据直方图及 PDF
plot_hist_with_pdf(lifespan_data, 'Lifespan Distribution', 'exponential')