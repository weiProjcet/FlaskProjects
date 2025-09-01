document.addEventListener('DOMContentLoaded', function () {
    // Tab切换功能
    document.querySelectorAll('.tab-button').forEach(button => {
        button.addEventListener('click', function () {
            // 移除所有active类
            document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));

            // 添加active类到当前元素
            this.classList.add('active');
            const tabId = this.getAttribute('data-tab');
            document.getElementById(tabId + '-tab').classList.add('active');

            // 如果是预览tab，更新预览内容
            if (tabId === 'preview') {
                updatePreview();
            }
        });
    });

// 实时预览功能
    const contentTextarea = document.getElementById('content');
    contentTextarea.addEventListener('input', updatePreview);

    function updatePreview() {
        const content = contentTextarea.value;
        const previewElement = document.getElementById('preview-content');

        // 简单的Markdown转HTML（实际项目中应使用专门的库）
        let html = content
            .replace(/^# (.*$)/gim, '<h1>$1</h1>')
            .replace(/^## (.*$)/gim, '<h2>$2</h2>')
            .replace(/^### (.*$)/gim, '<h3>$1</h3>')
            .replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/gim, '<em>$1</em>')
            .replace(/!\[(.*?)\]\((.*?)\)/gim, '<img alt="$1" src="$2" style="max-width:100%;">')
            .replace(/\[(.*?)\]\((.*?)\)/gim, '<a href="$2">$1</a>')
            .replace(/^(> (.*$))/gim, '<blockquote style="border-left: 3px solid #ccc; margin: 0; padding-left: 10px; color: #666;">$2</blockquote>')
            .replace(/^(- (.*$))/gim, '<li>$2</li>')
            .replace(/\n/g, '<br>');

        previewElement.innerHTML = html || '预览区域';
    }

// 初始化预览
    document.addEventListener('DOMContentLoaded', function () {
        updatePreview();
    });
});
