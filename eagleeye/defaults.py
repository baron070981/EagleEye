from dataclasses import dataclass


@dataclass
class DefVals:
    DIFF_PERC_SECT:int = 10
    PERC_COUNT_DIFFS:int = 8
    NUM_SECT:int = 30
    NUM_SAVE_IMAGES:int = 5
    INTERVAL_BETWEEN_SAVES:float = 0.3
    SLEEP:float = 3.0
    FRAME_OUT_SIZE:tuple = 800, None
    PROC_FRAME_SIZE:tuple = 420, None
    SIZE_SAVE_IMAGE:tuple = None, 760
    OUT_SAVE_FRAME_SIZE:tuple = 420, None
    GAUSIAN_KERNEL:tuple = 21, 21











