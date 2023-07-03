import os
import cv2
import h5py
from dv import AedatFile
import numpy as np
import argparse


def main(args, file_dir):   
    seq_name = os.path.basename(file_dir)[:-7]
    save_dir = os.path.join(args.root, seq_name)
    os.makedirs(save_dir, exist_ok=True)

    event_h5 = h5py.File(os.path.join(save_dir, 'event.h5'), 'a')
    with AedatFile(file_dir) as f:        
        i = 0
        evt_cnt = 0
        grp = event_h5.create_group('event')
        data_t = grp.create_dataset("t", [0], maxshape=[None], chunks=True, dtype=np.int64)
        data_x = grp.create_dataset("x", [0], maxshape=[None], chunks=True, dtype=np.int16)
        data_y = grp.create_dataset("y", [0], maxshape=[None], chunks=True, dtype=np.int16)
        data_p = grp.create_dataset("p", [0], maxshape=[None], chunks=True, dtype=np.int16)
        for e in f['events'].numpy():
            print(f'event {i}')
            new_cnt = e.shape[0]
            evt_cnt += new_cnt
            data_t.resize([evt_cnt])
            data_x.resize([evt_cnt])
            data_y.resize([evt_cnt])
            data_p.resize([evt_cnt])
            data_t[evt_cnt - new_cnt:evt_cnt] = e['timestamp']
            data_x[evt_cnt - new_cnt:evt_cnt] = e['x']
            data_y[evt_cnt - new_cnt:evt_cnt] = e['y']
            data_p[evt_cnt - new_cnt:evt_cnt] = e['polarity']
            i += 1
        print('extracted event.')

        i = 0
        os.makedirs(os.path.join(save_dir, 'images'), exist_ok=True)
        image_ts = []
        start_image_ts = []
        end_image_ts = []
        image_event_inds = []
        for frame in f['frames']:
            print(f'frame {i}')
            cv2.imwrite(os.path.join(save_dir, 'images', '{:06d}.png'.format(i)), frame.image)
            image_ts.append(frame.timestamp)
            start_image_ts.append(frame.timestamp_start_of_exposure)
            end_image_ts.append(frame.timestamp_end_of_exposure)
            start_event_ind = np.searchsorted(data_t, frame.timestamp_start_of_exposure)
            end_event_ind = np.searchsorted(data_t, frame.timestamp_end_of_exposure)
            image_event_inds.append((start_event_ind, end_event_ind))
            i += 1
        image_ts = np.array(image_ts, dtype=np.int64)
        start_image_ts = np.array(start_image_ts, dtype=np.int64)
        end_image_ts = np.array(end_image_ts, dtype=np.int64)
        image_event_inds = np.array(image_event_inds, dtype=np.int64)
        event_h5.create_dataset("image_ts", data=image_ts, maxshape=[None], chunks=True)
        event_h5.create_dataset("start_image_ts", data=start_image_ts, maxshape=[None], chunks=True)
        event_h5.create_dataset("end_image_ts", data=end_image_ts, maxshape=[None], chunks=True)
        event_h5.create_dataset('image_event_inds', data=image_event_inds, maxshape=[None, 2], chunks=True)
        print('extracted frame.')

    event_h5.close()


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-root', type=str, default='./data/')
    args = parser.parse_args()
    # files = os.listdir(args.root)
    # for file in files:
    #     file_dir = os.path.join(args.root, file)
    #     main(args, file_dir)
    for filename in os.listdir(args.root):
        if filename.startswith("high") and filename.endswith('aedat4'):
            file_dir = os.path.join(args.root, filename)
            main(args, file_dir)
    