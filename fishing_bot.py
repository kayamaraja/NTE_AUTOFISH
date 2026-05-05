import json
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple
import cv2
import keyboard
import mss
import numpy as np
import pydirectinput

@dataclass
class Config:
    capture_region: dict
    fish_hsv_low: Tuple[int, int, int]
    fish_hsv_high: Tuple[int, int, int]
    line_hsv_low: Tuple[int, int, int]
    line_hsv_high: Tuple[int, int, int]
    left_key: str
    right_key: str
    dead_zone_px: int
    min_blob_area: int
    target_fps: int
    show_mask_windows: bool

def load_config(path: Path) -> Config:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return Config(
        capture_region=raw["capture_region"],
        fish_hsv_low=tuple(raw["fish_hsv_low"]),
        fish_hsv_high=tuple(raw["fish_hsv_high"]),
        line_hsv_low=tuple(raw["line_hsv_low"]),
        line_hsv_high=tuple(raw["line_hsv_high"]),
        left_key=raw.get("left_key", "a"),
        right_key=raw.get("right_key", "d"),
        dead_zone_px=int(raw.get("dead_zone_px", 8)),
        min_blob_area=int(raw.get("min_blob_area", 20)),
        target_fps=int(raw.get("target_fps", 30)),
        show_mask_windows=bool(raw.get("show_mask_windows", True))
    )

def get_center_x(mask: np.ndarray, min_area: int) -> Optional[int]:
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    best_cnt = None
    max_area = 0
    
    # Ищем самый большой контур (саму зеленую полосу, а не блики)
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > min_area and area > max_area:
            max_area = area
            best_cnt = cnt
            
    if best_cnt is not None:
        x, y, w, h = cv2.boundingRect(best_cnt)
        return x + (w // 2) # Возвращаем геометрический центр объекта
    return None

def run_bot():
    path = Path(__file__).parent / "fishing_config.json"
    cfg = load_config(path)
    
    pydirectinput.PAUSE = 0
    running = False
    print("F8 - Старт, F9 - Стоп, ESC - Выход")

    with mss.mss() as sct:
        while True:
            if keyboard.is_pressed("f8"): running = True
            if keyboard.is_pressed("f9"): 
                running = False
                pydirectinput.keyUp(cfg.left_key)
                pydirectinput.keyUp(cfg.right_key)
            if keyboard.is_pressed("esc"): break

            if not running:
                time.sleep(0.1)
                continue

            # Захват и обработка
            img = np.array(sct.grab(cfg.capture_region))
            bgr = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)

            # Маски (Желтый - индикатор, Зеленый - полоса)
            fish_mask = cv2.inRange(hsv, np.array(cfg.fish_hsv_low), np.array(cfg.fish_hsv_high))
            line_mask = cv2.inRange(hsv, np.array(cfg.line_hsv_low), np.array(cfg.line_hsv_high))

            fx = get_center_x(fish_mask, cfg.min_blob_area)
            lx = get_center_x(line_mask, cfg.min_blob_area)

            if fx is not None and lx is not None:
                diff = fx - lx
                # Если желтый (fx) правее центра зеленого (lx), diff положительный -> жмем влево
                if abs(diff) > cfg.dead_zone_px:
                    if diff > 0:
                        pydirectinput.keyUp(cfg.right_key)
                        pydirectinput.keyDown(cfg.left_key)
                    else:
                        pydirectinput.keyUp(cfg.left_key)
                        pydirectinput.keyDown(cfg.right_key)
                else:
                    # Мы в центре! Отпускаем кнопки
                    pydirectinput.keyUp(cfg.left_key)
                    pydirectinput.keyUp(cfg.right_key)

            # Отрисовка отладки
            if cfg.show_mask_windows:
                cv2.imshow("Debug View", bgr)
                cv2.imshow("Fish (Yellow)", fish_mask)
                cv2.imshow("Line (Green)", line_mask)
                if cv2.waitKey(1) & 0xFF == ord('q'): break

            time.sleep(1/cfg.target_fps)

    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_bot()
