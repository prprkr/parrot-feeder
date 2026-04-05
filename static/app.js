/**
 * 鹦鹉智能喂食器 + 换水系统 - 前端交互逻辑
 */

// ==================== 工具函数 ====================

function showMessage(elementId, message, type = 'info') {
    const element = document.getElementById(elementId);
    element.textContent = message;
    element.className = `message-box ${type}`;
    
    // 5秒后自动隐藏
    if (type !== 'loading') {
        setTimeout(() => {
            element.style.display = 'none';
        }, 5000);
    }
}

function clearMessage(elementId) {
    const element = document.getElementById(elementId);
    element.style.display = 'none';
    element.className = 'message-box';
}

function formatTime(isoString) {
    if (!isoString || isoString === '--') return '--';
    const date = new Date(isoString);
    return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
}

// ==================== 时间显示 ====================

function updateCurrentTime() {
    const now = new Date();
    const timeStr = now.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        weekday: 'long'
    });
    document.getElementById('current-time').textContent = timeStr;
}

// 每秒更新时间
setInterval(updateCurrentTime, 1000);
updateCurrentTime();

// ==================== 喂食控制 ====================

async function feed(portion) {
    const portionNames = {
        'small': '少量',
        'normal': '正常',
        'large': '多量'
    };
    
    showMessage('feed-message', `正在喂食（${portionNames[portion]}）...`, 'loading');
    
    try {
        const response = await fetch('/api/feed', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ portion })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showMessage('feed-message', `✅ ${data.message}`, 'success');
            updateFeedStatus();  // 更新状态
        } else {
            showMessage('feed-message', `❌ ${data.message}`, 'error');
        }
    } catch (error) {
        console.error('喂食请求失败:', error);
        showMessage('feed-message', '❌ 网络错误，请检查连接', 'error');
    }
}

async function updateFeedStatus() {
    try {
        const response = await fetch('/api/feed/status');
        const data = await response.json();
        
        // 更新显示
        document.getElementById('last-feed-time').textContent = 
            formatTime(data.last_feed_time) || '从未';
        document.getElementById('total-feeds').textContent = data.total_feeds || 0;
        
        // 更新最后更新时间
        document.getElementById('last-update').textContent = 
            new Date().toLocaleTimeString('zh-CN');
            
    } catch (error) {
        console.error('获取喂食状态失败:', error);
    }
}

// ==================== 换水控制 ====================

async function changeWater() {
    showMessage('water-message', '正在换水，请稍候...', 'loading');
    
    try {
        const response = await fetch('/api/water/change', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ volume: 150 })  // 默认150ml
        });
        
        const data = await response.json();
        
        if (data.success) {
            showMessage('water-message', `✅ ${data.message}`, 'success');
            updateWaterStatus();  // 更新状态
        } else {
            showMessage('water-message', `❌ ${data.message}`, 'error');
        }
    } catch (error) {
        console.error('换水请求失败:', error);
        showMessage('water-message', '❌ 网络错误，请检查连接', 'error');
    }
}

async function updateWaterStatus() {
    try {
        const response = await fetch('/api/water/status');
        const data = await response.json();
        
        // 更新显示
        document.getElementById('last-water-change').textContent = 
            formatTime(data.last_change) || '从未';
        document.getElementById('next-water-change').textContent = 
            formatTime(data.next_change) || '--';
        document.getElementById('total-water-changes').textContent = 
            data.total_changes || 0;
        
        // 更新状态指示
        const statusElement = document.getElementById('water-status');
        if (data.needs_change) {
            statusElement.textContent = '需要换水';
            statusElement.className = 'status-danger';
        } else {
            statusElement.textContent = '水质良好';
            statusElement.className = 'status-normal';
        }
        
        // 更新间隔选择器
        if (data.interval_hours) {
            document.getElementById('water-interval').value = data.interval_hours;
        }
        
        // 更新最后更新时间
        document.getElementById('last-update').textContent = 
            new Date().toLocaleTimeString('zh-CN');
            
    } catch (error) {
        console.error('获取换水状态失败:', error);
    }
}

async function updateWaterSchedule() {
    const interval = document.getElementById('water-interval').value;
    
    try {
        const response = await fetch('/api/water/schedule', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ interval_hours: parseInt(interval) })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showMessage('water-message', `✅ ${data.message}`, 'success');
            updateWaterStatus();
        } else {
            showMessage('water-message', `❌ ${data.message}`, 'error');
        }
    } catch (error) {
        console.error('设置换水计划失败:', error);
        showMessage('water-message', '❌ 设置失败', 'error');
    }
}

// ==================== 定时刷新 ====================

// 页面加载时初始化
document.addEventListener('DOMContentLoaded', () => {
    console.log('🦜 鹦鹉智能控制系统已启动');
    
    // 初始加载状态
    updateFeedStatus();
    updateWaterStatus();
    
    // 每30秒自动刷新状态
    setInterval(() => {
        updateFeedStatus();
        updateWaterStatus();
    }, 30000);  // 30秒
    
    // 每60秒更新系统整体状态
    setInterval(updateSystemStatus, 60000);
});

async function updateSystemStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        
        // 可以在这里添加更多系统状态的更新逻辑
        console.log('系统状态已更新:', data.timestamp);
        
    } catch (error) {
        console.error('获取系统状态失败:', error);
    }
}

// ==================== 错误处理 ====================

window.addEventListener('unhandledrejection', (event) => {
    console.error('未处理的Promise拒绝:', event.reason);
});

window.addEventListener('error', (event) => {
    console.error('JavaScript错误:', event.error);
});
