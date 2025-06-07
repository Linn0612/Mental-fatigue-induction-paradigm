# N-back（10分钟）
from psychopy import visual, core, event, gui
import random
import time
import pandas as pd
import os

# ======================
# 实验参数配置
# ======================
# 基础设置
N_BACK = 2  # n-back的n值
TRIAL_DURATION = 3  # 每个试次呈现时间（秒）
RESPONSE_KEYS = ['y', 'n']  # 反应键设置
BLOCK_DURATION = 10 * 60  # 正式实验时长（10分钟）

# 刺激参数
STIM_COLOR = (1, 1, 1)  # 白色
BG_COLOR = (-1, -1, -1)  # 黑色背景
STIM_SIZE = 0.3  # 刺激大小（相对屏幕高度）


# ======================
# 实验组件
# ======================
def show_instruction(text, win):
    """显示指导语"""
    instr = visual.TextStim(
        win,
        text=text,
        height=0.07,
        wrapWidth=2,
        font='Microsoft YaHei UI'
    )
    instr.draw()
    win.flip()
    event.waitKeys(keyList=['space'])


def generate_stim_sequence(length=10, match_prob=0.6, allow_consecutive=False, n_back=2):
    """
    生成精确控制匹配概率的n-back序列
    参数：
    - length: 序列长度
    - match_prob: 匹配的概率
    - allow_consecutive: 是否允许连续匹配
    - n_back: n-back 的 n 值
    """
    sequence = []

    # 初始填充前n_back个随机数字
    for _ in range(n_back):
        sequence.append(str(random.randint(0, 9)))

    # 用于记录匹配的位置
    match_indices = []

    # 计算需要匹配的数量
    required_matches = int((length - n_back) * match_prob)

    # 随机选择匹配的位置
    possible_indices = list(range(n_back, length))
    random.shuffle(possible_indices)
    match_indices = possible_indices[:required_matches]

    # 按顺序排列匹配位置，以便均匀分布
    match_indices.sort()

    # 生成序列
    for i in range(n_back, length):
        if i in match_indices:
            # 匹配的情况
            new_digit = sequence[i - n_back]
            # 检查是否允许连续匹配
            if not allow_consecutive and i > n_back and sequence[i - 1] == sequence[i - n_back - 1]:
                # 如果前一个已经是匹配，则强制生成不匹配
                new_digit = _get_non_match_digit(sequence, i, n_back)
        else:
            # 不匹配的情况
            new_digit = _get_non_match_digit(sequence, i, n_back)

        sequence.append(new_digit)

    return sequence


def _get_non_match_digit(sequence, current_idx, n_back):
    """生成保证不与n-back位置相同的数字"""
    forbidden = sequence[current_idx - n_back]
    while True:
        new_digit = str(random.randint(0, 9))
        if new_digit != forbidden:
            return new_digit


def save_data(results, win):
    """保存数据到文件"""
    # 创建数据保存目录
    data_dir = "实验数据"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    # 生成文件名
    participant_id = participant_info['编号']  # 获取被试编号
    timestamp = time.strftime("%Y%m%d%H%M%S")
    file_name = f"{participant_id}_nback_results_{timestamp}.csv"
    file_path = os.path.join(data_dir, file_name)

    # 将结果保存为CSV文件
    df = pd.DataFrame(results)
    df.to_csv(file_path, index=False, encoding='utf-8-sig')

    # 打印文件保存路径
    print(f"数据已保存到: {file_path}")

    # 在实验界面显示保存路径
    instruction_text = visual.TextStim(
        win,
        text=f"数据已保存到: {file_path}\n\n按任意键继续",
        height=0.05,
        color=(1, 1, 1)
    )
    instruction_text.draw()
    win.flip()
    event.waitKeys()

    return file_path


def run_block(win, is_practice=False, duration=None):
    """运行一个任务组块"""
    total_trials_in_block = 0  # 重命名变量
    correct_trials_in_block = 0
    results = []

    # 生成刺激序列
    sequence = generate_stim_sequence(10 if is_practice else 200)

    # 创建刺激文本
    stim = visual.TextStim(
        win,
        text='',
        height=STIM_SIZE,
        color=STIM_COLOR
    )

    # 实验计时器
    timer = core.Clock()

    start_time = time.time()  # 记录块开始时间

    # 刺激间隔时间（秒）
    stimulus_interval = 0.3  # 可以根据需要调整这个值

    for idx, current_stim in enumerate(sequence):
        # 如果设置了持续时间并且超过了，退出循环
        if duration is not None and time.time() - start_time > duration:
            break

        # 呈现刺激
        stim.text = current_stim
        stim.draw()
        win.flip()

        # 记录反应
        response = None
        rt = None
        timer.reset()
        while timer.getTime() < TRIAL_DURATION:
            keys = event.getKeys(keyList=RESPONSE_KEYS + ['escape'])
            if keys:
                if 'escape' in keys:
                    win.close()
                    core.quit()
                response = keys[0]
                rt = timer.getTime()
                break

        # 计算正确答案
        correct_answer = 'y' if idx >= N_BACK and current_stim == sequence[idx - N_BACK] else 'n'

        # 无论是否有反应都记录数据
        total_trials_in_block += 1  # 总试次数+1

        # 计算正确性（无反应自动视为错误）
        is_correct = (response == correct_answer) if response else False
        if is_correct:
            correct_trials_in_block += 1

        # 记录所有试次数据
        results.append({
            'trial_index': idx,
            'stimulus': current_stim,
            'response': response or "无反应",  # 明确标记无反应
            'rt': rt,
            'correct_answer': correct_answer,
            'is_correct': is_correct
        })

        # 练习阶段提供反馈
        if is_practice:
            feedback = "正确！" if response == correct_answer else "错误！"
            show_instruction(f"{feedback}\n\n按空格继续", win)

        # 添加空屏间隔
        win.flip()  # 清空屏幕
        core.wait(stimulus_interval)  # 等待一段时间

        # 如果设置了持续时间并且超过了，退出循环
        if duration is not None and time.time() - start_time > duration:
            break

    # 返回正确和总试验数以及数据
    return total_trials_in_block, correct_trials_in_block, results



# 主实验流程
# ======================
# 收集被试信息
participant_info = {'编号': '', '年龄': '', '性别': ['男', '女']}
dlg = gui.DlgFromDict(participant_info, title="被试信息")
if not dlg.OK:
    core.quit()

# 创建窗口
win = visual.Window(
    size=[1440, 900],
    fullscr=False,
    color=BG_COLOR,
    units='height'
)

# 显示指导语
instructions = [
    "欢迎参加n-back实验！",
    "任务要求：\n判断当前数字是否与前面第2个数字相同\n\n"
    "相同 → 按Y键\n不同 → 按N键\n\n按空格键查看示例",
    "示例：\n2 → 5 → 2 → ?\n第三个数字与第一个相同，应该按Y\n\n按空格开始练习",
]
for text in instructions:
    show_instruction(text, win)

# 练习阶段
run_block(win, is_practice=True)

# 正式实验指导
all_results = []
total_trials = 0
correct_trials = 0
# 正式实验

experiment_start_time = time.time()  # 记录实验开始时间

while time.time() - experiment_start_time < BLOCK_DURATION:
    remaining_time = BLOCK_DURATION - (time.time() - experiment_start_time)
    block_trials, block_correct, block_results = run_block(win, duration=remaining_time)
    total_trials += block_trials
    correct_trials += block_correct
    all_results.extend(block_results)  # 合并数据

file_path = save_data(all_results, win)

# 打印正确率
if total_trials > 0:
    accuracy = correct_trials / total_trials * 100
    print(f"正式实验阶段正确率: {accuracy:.2f}%")

# 结束界面
win.close()
core.quit()