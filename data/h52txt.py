import os.path
import h5py

target_file_startsWith = 'high_outdoor_1'
txt_to_csv = True


def h5_to_txt(h5_file_path, txt_file_path):
    with h5py.File(h5_file_path, 'r') as f:
        # 获取事件数据
        events = f['event']
        t = events['t'][:]
        x = events['x'][:]
        y = events['y'][:]
        p = events['p'][:]

    # 将事件数据保存到 TXT 文件
    with open(txt_file_path, 'w') as f:
        for i in range(len(t)):
            f.write(f'{t[i]} {x[i]} {y[i]} {p[i]}\n')

    if txt_to_csv:
        import pandas as pd
        csv_file_path = txt_file_path.replace(".txt", ".csv")
        df = pd.read_csv(txt_file_path, delimiter=' ')
        '''# 将DataFrame保存为CSV文件
        df.to_csv(csv_file_path, index=False)

        # 读取CSV文件并将第一列数据全部减去第一个数
        df = pd.read_csv(csv_file_path)'''
        df.iloc[:, 0] = df.iloc[:, 0] - df.iloc[0, 0]
        df.iloc[0, 0] = 0
        csv_file_path_ = csv_file_path.replace(".csv", "_.csv")
        df.to_csv(csv_file_path_, index=False)


def h5_to_txt_all(h5_dir):
    # 批量 h5 to txt
    for filename in os.listdir(h5_dir):
        if filename.startswith(target_file_startsWith) and os.path.isdir(os.path.join('./', filename)):
            h5_file_path = os.path.join(h5_dir, filename, 'event.h5')
            txt_file_path = os.path.join(h5_dir, filename, 'event.txt')
            h5_to_txt(h5_file_path, txt_file_path)
            print(filename, 'Done')


def add_size(w, h):
    # 文件首增加一行表示图像尺寸
    for filename in os.listdir('./'):
        if filename.startswith(target_file_startsWith) and os.path.isdir(os.path.join('./', filename)):
            txt_file_path = os.path.join('./', filename, 'event.txt')
            with open(txt_file_path, 'r') as f:
                content = f.read()

            new_content = f'{w} {h}\n' + content

            with open(txt_file_path, 'w') as f:
                f.write(new_content)


if __name__ == '__main__':

    '''source = './dvSave-2023_06_27_11_40_36/event.h5'
    target = './dvSave-2023_06_27_11_40_36/event.txt'
    h5_to_txt(source, target)'''

    h5_to_txt_all('./')
    add_size(640, 480)
