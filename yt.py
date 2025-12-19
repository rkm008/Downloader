import os
import subprocess
import time  # For animation delay

# Colors
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
CYAN = "\033[36m"
RED = "\033[31m"
BOLD = "\033[1m"
RESET = "\033[0m"

# Set download directory
DOWNLOAD_DIR = os.path.expanduser("~/storage/shared/Download")

# Function to display animated ASCII banner
def display_banner():
    os.system("clear")
    banner_lines = [
        f"{CYAN}{BOLD}",
           "              _______         ___  ____       ____    ____  ",
           "             |_   __ \\       |_  ||_  _|     |_   \\  /   _| ",
           "               | |__) |        | |_/ /         |   \\/   |   ",
           "               |  __ /         |  __'.         | |\\  /| |   ",
           "              _| |  \\ \\_  _   _| |  \\ \\_  _   _| |_\\/ | |_  ",
           "            |____| |___|(_) |____| |___|(_) |_____|  |____| ",
        RESET
    ]
    for line in banner_lines:
        print(line)
        time.sleep(0.1)

def main():
    while True:
        display_banner()
        video_url = input(f"\n📌 {BOLD}Enter Video URL:{RESET} ")

        print(f"\n{BLUE}{BOLD}🔍 Checking available quality options...{RESET}")
        result = subprocess.run(["yt-dlp", "-F", video_url], capture_output=True, text=True)
        formats = result.stdout
        format_sizes = {}

        for line in formats.splitlines():
            size = "Unknown"
            if "MiB" in line:
                idx = line.index("MiB")
                start = idx
                while start > 0 and line[start-1] != " ":
                    start -= 1
                size = line[start:idx+3]
            elif "GiB" in line:
                idx = line.index("GiB")
                start = idx
                while start > 0 and line[start-1] != " ":
                    start -= 1
                size = line[start:idx+3]

            for res, label in [("360", "360p"), ("480", "480p"), ("720", "720p"),
                               ("1080", "1080p"), ("1440", "2K"), ("2160", "4K"), ("4320", "8K")]:
                if res in line:
                    format_sizes[label] = size

        seen = {}
        if "360" in formats: seen["360p"] = True
        if "480" in formats: seen["480p"] = True
        if "720" in formats: seen["720p"] = True
        if "1080" in formats: seen["1080p"] = True
        if "1440" in formats: seen["2K"] = True
        if "2160" in formats: seen["4K"] = True
        if "4320" in formats: seen["8K"] = True

        ordered = ["360p", "480p", "720p", "1080p", "2K", "4K", "8K"]
        options = []

        print(f"\n{YELLOW}{BOLD}📺 Available Video Qualities:{RESET}")

        # Determine dynamic width based on the longest size string
        max_size_len = max(len(size) for size in format_sizes.values() if size) if format_sizes else 9
        size_col_width = max(max_size_len, 9) + 2  # Padding for spacing
        total_box_width = 28 + size_col_width

        print(f"  ┌{'─' * total_box_width}┐")
        i = 1
        for q in ordered:
            if q in seen:
                emoji = f"{i}\u20e3"
                label = q
                if q == "2K": label = "2K (1440p)"
                elif q == "4K": label = "4K (2160p)"
                elif q == "8K": label = "8K (4320p)"
                size_info = format_sizes.get(q, "UnknownSize")
                content = f"  │  {emoji}  {label:<18}  [{size_info:^{size_col_width}}] │"
                print(content)
                options.append(q)
                i += 1

        # MP3 Line (fixed alignment)
        emoji = f"{i}\u20e3"
        mp3_label = "MP3 (Audio Only)"
        content = f"  │  {emoji}  {mp3_label}"
        print(content + " " * (total_box_width - len(content) + 3) + " │")
        options.append("MP3")
        print(f"  └{'─' * total_box_width}┘")

        print(f"\n{CYAN}{BOLD}🎯 Tip:{RESET} Use format codes listed above if you want custom control.")
        print(f"{YELLOW}ℹ️  You'll still get quality options below for easy use.{RESET}")

        choice = input(f"\n🔹 {BOLD}Select an option (1-{len(options)}):{RESET} ")
        try:
            index = int(choice) - 1
            selected = options[index]
        except (ValueError, IndexError):
            print(f"{RED}❌ Invalid selection!{RESET}")
            return

        if selected == "360p":
            fmt = "bestvideo[height<=360]+bestaudio/best[height<=360]"
        elif selected == "480p":
            fmt = "bestvideo[height<=480]+bestaudio/best[height<=480]"
        elif selected == "720p":
            fmt = "bestvideo[height<=720]+bestaudio/best[height<=720]"
        elif selected == "1080p":
            fmt = "bestvideo[height<=1080]+bestaudio/best[height<=1080]"
        elif selected == "2K":
            fmt = "bestvideo[height<=1440]+bestaudio/best[height<=1440]"
        elif selected == "4K":
            fmt = "bestvideo[height<=2160]+bestaudio/best[height<=2160]"
        elif selected == "8K":
            fmt = "bestvideo[height<=4320]+bestaudio/best[height<=4320]"
        elif selected == "MP3":
            fmt = "bestaudio"
        else:
            print(f"{RED}❌ Invalid selection!{RESET}")
            return

        print(f"\n{CYAN}📥 Downloading in selected quality...{RESET}")
        if selected == "MP3":
            result = subprocess.run([
                "yt-dlp", "-f", fmt, "-x", "--audio-format", "mp3",
                "-o", f"{DOWNLOAD_DIR}/%(title).80s.%(ext)s", video_url
            ])
            if result.returncode != 0:
                print(f"\n{RED}⚠️ Audio format failed! Retrying with best audio...{RESET}")
                subprocess.run([
                    "yt-dlp", "-f", "bestaudio", "-x", "--audio-format", "mp3",
                    "-o", f"{DOWNLOAD_DIR}/%(title).80s.%(ext)s", video_url
                ])
        else:
            result = subprocess.run([
                "yt-dlp", "-f", fmt, "--merge-output-format", "mp4",
                "-o", f"{DOWNLOAD_DIR}/%(title).80s.%(ext)s", video_url
            ])
            if result.returncode != 0:
                print(f"\n{RED}⚠️ Video format failed! Retrying with best...{RESET}")
                subprocess.run([
                    "yt-dlp", "-f", "best", "--merge-output-format", "mp4",
                    "-o", f"{DOWNLOAD_DIR}/%(title).80s.%(ext)s", video_url
                ])

        print(f"\n{GREEN}✅ Download completed!{RESET}")
        print(f"{BOLD}📂 File saved to: {DOWNLOAD_DIR}{RESET}\n")

        cont = input(f"\n🔄 {BOLD}Do you want to download more? (y/n):{RESET} ")
        if cont.lower() != 'y':
            break

if __name__ == "__main__":
    main()