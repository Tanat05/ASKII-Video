import cv2
import numpy as np
import time
import argparse
import os
from colorama import init, Fore, Back, Style, deinit

init()

ASCII_CHARS = " .,:;i1tfLCG08#@"

def get_ascii_char(intensity):
    if len(ASCII_CHARS) == 0:
        return ' '
    return ASCII_CHARS[int(intensity / 255 * (len(ASCII_CHARS) - 1))]

def frame_to_ascii(frame, width):
    original_height, original_width, _ = frame.shape
    height = int(width * original_height / original_width * 0.5)
    resized_color_frame = cv2.resize(frame, (width, height), interpolation=cv2.INTER_AREA)
    resized_gray_frame = cv2.cvtColor(resized_color_frame, cv2.COLOR_BGR2GRAY)

    ascii_rows = []
    for y in range(height):
        row_chars = []
        for x in range(width):
            b, g, r = resized_color_frame[y, x]
            intensity = resized_gray_frame[y, x]
            char = get_ascii_char(intensity)
            row_chars.append(f"\033[38;2;{r};{g};{b}m{char}")

        ascii_rows.append("".join(row_chars) + Style.RESET_ALL + "\n")

    ascii_string = "".join(ascii_rows)
    return ascii_string


def main():
    parser = argparse.ArgumentParser(description="동영상을 아스키 아트로 변환하여 콘솔에 출력합니다.")
    parser.add_argument("video_path", help="변환할 동영상 파일 경로.")
    parser.add_argument("--width", type=int, default=100, help="아스키 아트의 가로 문자 수 (기본값: 100).")
    args = parser.parse_args()

    video_path = args.video_path
    ascii_width = args.width

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print(f"{Fore.RED}오류: 동영상 파일을 열 수 없습니다")
        deinit()
        exit()

    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        print(f"{Fore.YELLOW}경고: FPS 정보를 가져올 수 없습니다. 기본값 30으로 설정합니다.{Style.RESET_ALL}")
        fps = 30

    target_frame_duration = 1.0 / fps

    print(f"{Fore.GREEN}'{video_path}' 동영상을 색상 아스키 아트로 변환 중입니다...{Style.RESET_ALL}")
    print(f"{Fore.GREEN}'q' 키를 누르면 종료됩니다.{Style.RESET_ALL}")

    while True:
        frame_start_time = time.perf_counter()

        ret, frame = cap.read()

        if not ret:
            break

        ascii_frame = frame_to_ascii(frame, ascii_width)

        print("\033[H", end="")

        print(ascii_frame)

        frame_end_time = time.perf_counter()

        processing_print_time = frame_end_time - frame_start_time

        wait_duration = max(0, target_frame_duration - processing_print_time)

        wait_ms = max(1, int(wait_duration * 1000))

        key = cv2.waitKey(wait_ms) & 0xFF

        if key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    print(f"{Fore.GREEN}동영상 재생이 종료되었습니다.{Style.RESET_ALL}")

    deinit()

if __name__ == "__main__":
    main()
