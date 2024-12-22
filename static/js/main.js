document.addEventListener('DOMContentLoaded', function() {
    const urlInput = document.getElementById('video-url');
    const downloadBtn = document.getElementById('download-btn');
    const status = document.getElementById('status');
    const progress = document.getElementById('progress');
    const info = document.getElementById('info');

    // 处理回车键
    urlInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            downloadBtn.click();
        }
    });

    // 处理下载按钮点击
    downloadBtn.addEventListener('click', async function() {
        const url = urlInput.value.trim();
        if (!url) {
            showError('请输入视频链接');
            return;
        }

        // 禁用输入和按钮
        urlInput.disabled = true;
        downloadBtn.disabled = true;
        progress.style.display = 'block';
        info.style.display = 'none';
        status.textContent = '正在获取视频信息...';

        try {
            const response = await fetch('/download', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url: url })
            });

            const data = await response.json();

            if (response.ok) {
                showSuccess(`
                    下载完成！<br>
                    标题: ${data.title}<br>
                    质量: ${data.quality}<br>
                    大小: ${data.size}
                `);
            } else {
                showError(data.error || '下载失败');
            }
        } catch (error) {
            showError('网络错误，请稍后重试');
        } finally {
            // 重置界面状态
            urlInput.disabled = false;
            downloadBtn.disabled = false;
            progress.style.display = 'none';
            status.textContent = '';
            urlInput.value = '';
        }
    });

    function showError(message) {
        info.className = 'info error';
        info.innerHTML = message;
        info.style.display = 'block';
    }

    function showSuccess(message) {
        info.className = 'info success';
        info.innerHTML = message;
        info.style.display = 'block';
    }
}); 