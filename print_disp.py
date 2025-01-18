import matplotlib.pyplot as plt
import os

# 创建图表
plt.figure(figsize=(10, 6))

# 循环读取多个文件，绘制每条线
for i in range(1, 11):  # i 从 1 到 10
    x_values = []
    y_values = []

    # 构造文件路径，确保文件在 floor_disp 目录下
    filename = os.path.join("floor_disp", f"floor{i}_disp.txt")

    try:
        # 打开并读取文件
        with open(filename, 'r', encoding='utf-8') as file:
            for line in file:
                # 跳过空行
                line = line.strip()
                if not line:
                    continue

                # 尝试解析每一行的两个数值
                try:
                    x, y = map(float, line.split())  # 将每行的两个值转换为浮动类型
                    x_values.append(x)
                    y_values.append(y)
                except ValueError:
                    print(f"Skipping invalid line in {filename}: {line}")

        # 如果文件中有有效的数据，绘制该文件的数据
        if x_values and y_values:
            plt.plot(x_values, y_values, label=f"Data from {filename}", linewidth=2)

    except FileNotFoundError:
        print(f"Warning: {filename} not found. Skipping.")

# 添加标题和标签
plt.title("Plots of Data from floor_1_disp.txt to floor_10_disp.txt", fontsize=14)
plt.xlabel("X Axis", fontsize=12)
plt.ylabel("Y Axis", fontsize=12)

# 添加网格线
plt.grid(True)

# 显示图例
plt.legend()

# 显示图表
plt.show()
