from flask import Flask, render_template, request, jsonify
import yt_dlp
import os
import time
from pathlib import Path

app = Flask(__name__)

# 确保下载目录存在
DOWNLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloads')
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def format_size(bytes):
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024:
            return f"{bytes:.1f} {unit}"
        bytes /= 1024
    return f"{bytes:.1f} TB"

def find_best_format(formats, target_height=720):
    """找到最接近720p的格式"""
    mp4_formats = [f for f in formats if f.get('ext') == 'mp4' and f.get('height')]
    if not mp4_formats:
        return None
    sorted_formats = sorted(mp4_formats, 
                          key=lambda x: abs(x.get('height', 0) - target_height))
    return sorted_formats[0]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_video():
    url = request.json.get('url')
    if not url:
        return jsonify({'error': '请输入视频链接'}), 400

    # 修正YouTube短链接
    if 'youtu.be' in url:
        video_id = url.split('/')[-1].split('?')[0]
        url = f'https://www.youtube.com/watch?v={video_id}'

    try:
        # 配置yt-dlp选项
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'merge_output_format': 'mp4',
            'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
            'ignoreerrors': True,
        }

        # 获取视频信息
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if not info:
                return jsonify({'error': '无法获取视频信息'}), 400

            # 获取最佳格式
            best_format = find_best_format(info.get('formats', []))
            if best_format:
                format_id = best_format.get('format_id', '')
                height = best_format.get('height', 0)
                size = format_size(best_format.get('filesize', 0))
                ydl_opts['format'] = f"{format_id}+bestaudio[ext=m4a]"

            # 开始下载
            ydl.download([url])
            
            return jsonify({
                'success': True,
                'message': '下载完成',
                'title': info.get('title', 'Unknown'),
                'quality': f"{height}p" if best_format else '默认质量',
                'size': size if best_format else 'Unknown'
            })

    except Exception as e:
        error_msg = str(e)
        if "Video unavailable" in error_msg:
            return jsonify({'error': '视频不可用或已被删除'}), 400
        elif "Unable to extract" in error_msg:
            return jsonify({'error': '无法解析视频信息，请检查链接是否正确'}), 400
        return jsonify({'error': f'下载出错: {error_msg}'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
