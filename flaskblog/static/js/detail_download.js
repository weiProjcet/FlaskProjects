function downloadPdf(blogId) {
    const btn = document.getElementById('pdfBtn');

    // 按钮变灰两秒
    btn.disabled = true;

    // 2秒后恢复按钮文字（但保持禁用状态直到下载完成）
    setTimeout(() => {
        btn.disabled = false;
    }, 2000);

    // 启动PDF生成任务
    fetch(`/download/${blogId}/pdf/start`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('input[name="csrf_token"]').value
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // 启动轮询检查
                checkPdfStatus(blogId, data.task_id);
            }
        })
        .catch(error => {
            // 错误处理但不显示给用户
            console.error('下载请求失败:', error);
        });
}

function checkPdfStatus(blogId, taskId) {
    // 每2秒检查一次任务状态
    const checkInterval = setInterval(() => {
        fetch(`/download/${blogId}/pdf/check/${taskId}`)
            .then(response => response.json())
            .then(data => {
                if (data.status === 'ready') {
                    // 任务完成，停止轮询并开始下载
                    clearInterval(checkInterval);
                    window.location.href = `/download/${blogId}/pdf/download/${taskId}`;
                }
                // 如果还在处理中，继续轮询
            })
            .catch(error => {
                // 错误处理但不显示给用户
                console.error('检查状态失败:', error);
                clearInterval(checkInterval);
            });
    }, 2000);
}