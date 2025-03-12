import time
# import jaraco

# import packaging
import numpy as np
import pandas as pd
from brainflow.board_shim import BoardShim, BrainFlowInputParams, LogLevels, BoardIds
from brainflow.data_filter import DataFilter
from pynput import keyboard


running = True


def on_press(key, board):
    global running
    try:
        if key.char:
            board.insert_marker(1)
            print(f"Marker inserted at time {time.time()}")
    except AttributeError:
        pass


    if key == keyboard.Key.esc:
        print("ESC pressed. Stopping data collection.")
        running = False
        return False


def main():
    BoardShim.enable_dev_board_logger()

    params = BrainFlowInputParams()
    params.serial_port = "COM9"
    board = BoardShim(BoardIds.CYTON_BOARD, params)
    board.prepare_session()
    board.start_stream()
    BoardShim.log_message(LogLevels.LEVEL_INFO.value, 'start sleeping in the main thread')
   
    listener = keyboard.Listener(on_press=lambda key: on_press(key,board))
    listener.start()
   
    while running:
        time.sleep(1)
   
    data = board.get_board_data()
    board.stop_stream()
    board.release_session()


    # demo how to convert it to pandas DF and plot data
    eeg_channels = BoardShim.get_eeg_channels(BoardIds.CYTON_BOARD)
    df = pd.DataFrame(np.transpose(data))
    print(df.head(10))


    # demo for data serialization using brainflow API, we recommend to use it instead pandas.to_csv()
    DataFilter.write_file(data, 'sudoku4.csv', 'w')  # use 'a' for append mode
    restored_data = DataFilter.read_file('sudoku4.csv')
    restored_df = pd.DataFrame(np.transpose(restored_data))
    print('Data From the File')
    print(restored_df.head(10))


if __name__ == "__main__":
    main()