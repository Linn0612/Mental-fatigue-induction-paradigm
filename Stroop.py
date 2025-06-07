# Stroop任务升级版（10分钟）
from psychopy import visual, core, event, gui
import random
import time
import pandas as pd

# 创建对话框获取被试信息
info = {'被试编号': '', '年龄': '', '性别': ['男', '女']}
dlg = gui.DlgFromDict(info, title='Stroop实验升级版')
if not dlg.OK:
    core.quit()

# 显示器调节1---配置显示器参数
from psychopy import monitors
my_monitor = monitors.Monitor("myScreen")  # 创建显示器配置文件
my_monitor.setWidth(53.1)                  # 屏幕实际宽度（厘米）
my_monitor.setSizePix([1440, 900])         # 分辨率
my_monitor.setDistance(40)                 # 被试眼睛到屏幕的距离（厘米）
my_monitor.save()                          # 保存配置（会生成一个文件，以后不用重复测量）

# 显示器调节2---创建窗口（自动适配当前分辨率）
win = visual.Window(
    size=my_monitor.getSizePix(),          # 自动读取分辨率
    color=(-1, -1, -1),                    # 默认背景黑色
    fullscr=False,
    monitor="myScreen",                    # 使用刚保存的配置
    units="height",                        # 推荐单位：按屏幕高度比例显示
    screen=0                               # 主显示器（多屏时选0/1）
)

# 显示器调节3---字体优化
instruction_text = visual.TextStim(
    win,
    font="Microsoft YaHei UI",             # 微软雅黑（系统自带）
    height=0.08,                           # 文字高度为屏幕高度的8%
    wrapWidth=3,                           # 换行宽度（1.5倍文字高度）
    pos=(0, 0),                            # 位置：水平居中，垂直方向30%高度
    color=(1, 1, 1)                        # 白色文字
)

# 显示指导语
instructions = [
    "欢迎参加Stroop实验升级版！",
    "当屏幕为黑色时，忽略字的含义，根据字的颜色进行判断：\n\nR-红  G-绿  B-蓝  Y-黄  P-紫\n\n按空格键继续",
    "当屏幕为灰色时，忽略字的颜色，根据字的含义进行判断：\n\nR-红  G-绿  B-蓝  Y-黄  P-紫\n\n按空格键开始练习",
    "练习结束\n 按空格键开始正式实验（持续10分钟）",
]

def show_instruction(page):
    instruction_text.text = instructions[page]
    instruction_text.draw()
    win.flip()
    event.waitKeys(keyList=['space'])

# 实验参数设置
colors = {
    '红': (1, -1, -1),  # RGB红色
    '绿': (-1, 1, -1),  # RGB绿色
    '蓝': (-1, -1, 1),  # RGB蓝色
    '黄': (1, 1, -1),   # RGB黄色
    '紫': (1, -1, 1)    # RGB紫色
}
keys_mapping = {'r': '红', 'g': '绿', 'b': '蓝', 'y': '黄', 'p': '紫'}

# 练习阶段
show_instruction(0)
show_instruction(1)
show_instruction(2)

for _ in range(10):
    # 随机选择背景颜色（黑色或灰色）
    background_color = random.choice([(-1, -1, -1), (0.5, 0.5, 0.5)])
    win.color = background_color
    win.flip()  # 更新背景颜色

    # 根据背景颜色选择任务规则
    if background_color == (-1, -1, -1):  # 黑色背景：判断颜色
        word = random.choice(list(colors.keys()))
        color = random.choice([c for c in colors if c != word])  # 颜色与文字不一致
        correct_response = color  # 正确答案是颜色
    else:  # 灰色背景：判断含义
        word = random.choice(list(colors.keys()))
        color = random.choice(list(colors.keys()))  # 颜色可以与文字一致或不一致
        correct_response = word  # 正确答案是文字含义

    # 呈现刺激
    text_stim = visual.TextStim(win, text=word, color=colors[color],
                                height=0.2, font='Microsoft YaHei UI')
    text_stim.draw()
    win.flip()

    # 记录反应
    start_time = time.time()
    keys = event.waitKeys(keyList=['r', 'g', 'b', 'y', 'p', 'escape'])
    rt = (time.time() - start_time) * 1000  # 反应时间（毫秒）

    if 'escape' in keys:
        core.quit()

    # 反馈
    response = keys_mapping[keys[0]] if keys else None
    feedback = "正确！" if response == correct_response else "错误"
    instruction_text.text = f"{feedback}\n\n反应时间：{rt:.0f}ms\n按空格继续"
    instruction_text.draw()
    win.flip()
    event.waitKeys(keyList=['space'])

# 正式实验
show_instruction(3)
results = []
timer = core.Clock()
experiment_duration = 600  # 10分钟 = 600秒

while timer.getTime() < experiment_duration:
    # 随机选择背景颜色（黑色或灰色）
    background_color = random.choice([(-1, -1, -1), (0.5, 0.5, 0.5)])
    win.color = background_color
    win.flip()  # 更新背景颜色

    # 根据背景颜色选择任务规则
    if background_color == (-1, -1, -1):  # 黑色背景：判断颜色
        word = random.choice(list(colors.keys()))
        color = random.choice([c for c in colors if c != word])  # 颜色与文字不一致
        correct_response = color  # 正确答案是颜色
    else:  # 灰色背景：判断含义
        word = random.choice(list(colors.keys()))
        color = random.choice(list(colors.keys()))  # 颜色可以与文字一致或不一致
        correct_response = word  # 正确答案是文字含义

    # 呈现刺激
    text_stim = visual.TextStim(win, text=word, color=colors[color],
                                height=0.2, font='Microsoft YaHei UI')
    text_stim.draw()
    win.flip()

    # 记录反应
    event.clearEvents()
    start_time = time.time()
    keys = event.waitKeys(maxWait=3, keyList=['r', 'g', 'b', 'y', 'p', 'escape'])
    rt = (time.time() - start_time) * 1000  # 毫秒

    if keys and 'escape' in keys:
        core.quit()

    # 保存数据
    response = keys_mapping[keys[0]] if keys else None
    results.append({
        '背景颜色': '黑色' if background_color == (-1, -1, -1) else '灰色',
        '词语': word,
        '颜色': color,
        '反应时': rt,
        '反应键': keys[0] if keys else None,
        '是否正确': response == correct_response
    })

import os

# 创建一个文件夹来保存数据
data_dir = "实验数据"
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

# 生成文件名
file_name = f"{info['被试编号']}_stroop_results.csv"
file_path = os.path.join(data_dir, file_name)

# 将结果保存为CSV文件
df = pd.DataFrame(results)
df.to_csv(file_path, index=False, encoding='utf-8-sig')

# 打印文件保存路径
print(f"数据已保存到: {file_path}")

# 结束界面
instruction_text.text = f"实验结束！\n\n完成试次数：{len(results)}\n正确率：{sum(r['是否正确'] for r in results) / len(results):.1%}\n按任意键退出"
instruction_text.draw()
win.flip()
event.waitKeys()
win.close()
core.quit()
