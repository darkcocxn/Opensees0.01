import os
import openseespy.opensees as ops

# 清理现有模型
ops.wipe()

# 创建基本模型：1维（ndm=1），每节点1自由度（ndf=1）
ops.model('basic', '-ndm', 1, '-ndf', 1)

# 楼层参数
numFloors = 10  # 楼层数
floorHeight = 3.0  # 每层楼的高度
mass_per_floor = 1.0e5  # 每层楼质量 (kg)
k_floor = 1.0e8  # 楼层间刚度 (N/m)

# 创建节点
for i in range(numFloors + 1):
    ops.node(i + 1, i * floorHeight)

# 固定底部节点 (1)
ops.fix(1, 1)

# 定义材料
matTag = 1
ops.uniaxialMaterial('Elastic', matTag, k_floor)

# 定义楼层质量
for i in range(2, numFloors + 2):
    ops.mass(i, mass_per_floor)

# 创建楼层之间的 twoNodeLink 元素
elementTag = 1
for i in range(1, numFloors + 1):
    ops.element('twoNodeLink', elementTag, i, i + 1, '-mat', matTag, '-dir', 1)
    elementTag += 1

# 在第6层（节点6和节点7）之间额外添加一个 twoNodeLink
ops.element('twoNodeLink', 20, 6, 7, '-mat', matTag, '-dir', 1)

# 从 accel.txt 文件中读取地震波加速度
timeSeriesTag = 1
dt = 0.02  # 时间步
with open('accel.txt', 'r') as f:
    acc_values = [float(line.strip()) for line in f]

ops.timeSeries('Path', timeSeriesTag, '-dt', dt, '-values', *acc_values)

# 地震波施加到基础节点（节点1）
patternTag = 1
ops.pattern('UniformExcitation', patternTag, 1, '-accel', timeSeriesTag)

# 定义瑞利阻尼 (2% 阻尼比)
zeta = 0.02
betaK = 2 * zeta / (1.0 / (2 * 3.14159) + 1.0 / (2 * 3.14159))  # 示例周期约为 1 秒
ops.rayleigh(0.0, betaK, 0.0, 0.0)

# 定义求解器与分析选项
ops.system('BandGeneral')
ops.numberer('Plain')
ops.constraints('Plain')
ops.integrator('Newmark', 0.5, 0.25)
ops.algorithm('Newton')
ops.analysis('Transient')

# 创建输出目录
dispDir = "floor_disp"
driftDir = "inter_drift"
os.makedirs(dispDir, exist_ok=True)
os.makedirs(driftDir, exist_ok=True)

# 创建记录器文件
recorders = {}
for floor in range(1, numFloors + 1):
    filename = os.path.join(dispDir, f"floor{floor}_disp.txt")
    recorders[floor] = open(filename, 'w')
    recorders[floor].write("Time (s)\tDisplacement (m)\n")  # 文件头

# 创建层间位移角记录器文件
drift_recorders = {}
for i in range(1, numFloors):
    j = i + 1
    filename = os.path.join(driftDir, f"floor{i}_{j}rad.txt")
    drift_recorders[(i, j)] = open(filename, 'w')
    drift_recorders[(i, j)].write("Time (s)\tInterstory Drift Ratio (rad)\n")  # 文件头

# 开始时程分析，记录位移和层间位移角
numSteps = len(acc_values)
max_interstory_drift = {key: 0.0 for key in drift_recorders}  # 最大层间位移角

for step in range(numSteps):
    ops.analyze(1, dt)
    currentTime = step * dt

    # 记录每层的位移
    displacements = {}
    for floor in range(1, numFloors + 1):
        nodeTag = floor + 1  # 节点编号
        disp = ops.nodeDisp(nodeTag, 1)  # 获取水平位移
        recorders[floor].write(f"{currentTime:.6f}\t{disp:.6e}\n")
        displacements[floor] = disp

    # 计算并记录层间位移角
    for i in range(1, numFloors):
        j = i + 1
        drift = (displacements[j] - displacements[i]) / floorHeight  # 层间位移角
        drift_recorders[(i, j)].write(f"{currentTime:.6f}\t{drift:.6e}\n")
        max_interstory_drift[(i, j)] = max(max_interstory_drift[(i, j)], abs(drift))

# 关闭所有记录器文件
for f in recorders.values():
    f.close()
for f in drift_recorders.values():
    f.close()

# 输出最大层间位移角
print("最大层间位移角 (单位: rad):")
for (i, j), drift in max_interstory_drift.items():
    print(f"楼层 {i}-{j}: {drift:.6e} rad")

print(f"Analysis complete. Results saved in '{dispDir}' and '{driftDir}' directories.")
