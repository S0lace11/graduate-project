import yt_dlp
import os
import time
import sys

def format_size(bytes):
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024:
            return f"{bytes:.1f} {unit}"
        bytes /= 1024
    return f"{bytes:.1f} TB"

def show_progress(d):
    """显示下载进度"""
    if d['status'] == 'downloading':
        # 计算进度
        total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
        downloaded = d.get('downloaded_bytes', 0)
        
        # 计算速度
        speed = d.get('speed', 0)
        if speed:
            speed_str = format_size(speed) + '/s'
        else:
            speed_str = 'N/A'
            
        # 计算进度百分比
        if total_bytes:
            percent = downloaded / total_bytes * 100
            downloaded_str = format_size(downloaded)
            total_str = format_size(total_bytes)
            
            # 计算剩余时间
            eta = d.get('eta', 0)
            if eta:
                eta_str = f"{eta//60}分{eta%60}秒"
            else:
                eta_str = 'N/A'
                
            print(f"\r下载进度: {percent:.1f}% | {downloaded_str}/{total_str} | 速度: {speed_str} | 剩余时间: {eta_str}", end="")
    
    elif d['status'] == 'finished':
        print("\n下载完成！正在处理...")

def find_best_format(formats, target_height=720):
    """找到最接近目标分辨率的格式"""
    # 过滤出所有MP4格式
    mp4_formats = [f for f in formats if f.get('ext') == 'mp4' and f.get('height')]
    
    if not mp4_formats:
        return None
        
    # 按照分辨率高度与720p的差值排序
    sorted_formats = sorted(mp4_formats, 
                          key=lambda x: abs(x.get('height', 0) - target_height))
    
    return sorted_formats[0]

def download_video(url, output_path=None):
    if output_path is None:
        output_path = os.getcwd()
        
    # 配置下载选项
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',  # 默认格式
        'merge_output_format': 'mp4',  # 确保输出mp4格式
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),  # 输出文件模板
        'progress_hooks': [show_progress],  # 进度回调
        'quiet': True,  # 不显示debug信息
        'no_warnings': True,  # 不显示警告
        'ignoreerrors': True,  # 忽略错误继续下载
        'noprogress': True,  # 禁用yt-dlp默认进度条
    }
    
    try:
        print("正在获取视频信息...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # 获取视频信息
            info = ydl.extract_info(url, download=False)
            
            if not info:
                print("无法获取视频信息")
                return False
                
            # 显示视频信息
            print(f"\n视频标题: {info.get('title', 'Unknown')}")
            print(f"时长: {int(info.get('duration', 0)/60)}分{int(info.get('duration', 0)%60)}秒")
            
            # 获取最接近720p的格式
            best_format = find_best_format(info.get('formats', []))
            
            if best_format:
                height = best_format.get('height', 0)
                format_id = best_format.get('format_id', '')
                size = format_size(best_format.get('filesize', 0))
                
                print(f"\n已选择视频质量: {height}p - {size}")
                ydl_opts['format'] = f"{format_id}+bestaudio[ext=m4a]"
            else:
                print("\n无法找到合适的视频格式，将使用默认质量")
            
            print("\n开始下载...")
            ydl.download([url])
            return True
            
    except Exception as e:
        print(f"\n下载出错: {str(e)}")
        if "Video unavailable" in str(e):
            print("视频不可用或已被删除")
        elif "Unable to extract" in str(e):
            print("无法解析视频信息，请检查链接是否正确")
        return False

if __name__ == "__main__":
    print("YouTube视频下载器 (输入 'q' 退出)")
    print("提示：")
    print("1. 此版本使用 yt-dlp，下载更稳定")
    print("2. 自动选择720p或最接近的分辨率")
    print("3. 显示实时下载速度和剩余时间\n")
    
    while True:
        video_url = input("请输入YouTube视频链接: ")
        if video_url.lower() == 'q':
            break
            
        # 尝试修正常见的YouTube短链接
        if 'youtu.be' in video_url:
            video_id = video_url.split('/')[-1].split('?')[0]
            video_url = f'https://www.youtube.com/watch?v={video_id}'
            
        download_video(video_url)
