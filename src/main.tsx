import React from 'react';
import ReactDOM from 'react-dom/client';

function PythonAppNotice() {
  return (
    <div style={{
      minHeight: '100vh',
      backgroundColor: '#09090b',
      color: '#f4f4f5',
      fontFamily: 'system-ui, -apple-system, sans-serif',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '24px',
      textAlign: 'center'
    }}>
      <div style={{
        backgroundColor: '#18181b',
        border: '1px solid #27272a',
        borderRadius: '16px',
        padding: '32px 40px',
        maxWidth: '560px',
        boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.5)'
      }}>
        <div style={{ fontSize: '48px', marginBottom: '16px' }}>🐍 ⚔️</div>
        <h1 style={{ fontSize: '22px', fontWeight: 'bold', marginBottom: '12px', color: '#60a5fa' }}>
          Clash Auto Farm Pro - Python Desktop Application
        </h1>
        <p style={{ fontSize: '14px', color: '#a1a1aa', lineHeight: '1.6', marginBottom: '24px' }}>
          Tất cả giao diện và logic chính của bot đã được tập trung 100% vào mã nguồn Python (PySide6 Desktop GUI).
        </p>
        <div style={{
          backgroundColor: '#09090b',
          border: '1px solid #3f3f46',
          borderRadius: '8px',
          padding: '12px 16px',
          fontFamily: 'monospace',
          fontSize: '13px',
          color: '#34d399',
          marginBottom: '20px',
          textAlign: 'left'
        }}>
          <div>$ python main.py</div>
          <div style={{ color: '#71717a', fontSize: '11px', marginTop: '4px' }}>→ Khởi chạy MainWindow (Strategy Tab, Live Deploy, Wall Upgrade...)</div>
        </div>
        <div style={{ fontSize: '12px', color: '#71717a' }}>
          File đã sửa lỗi: <code style={{ color: '#e4e4e7' }}>gui/strategy_tab.py</code> & <code style={{ color: '#e4e4e7' }}>gui/config_preview_dialog.py</code>
        </div>
      </div>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <PythonAppNotice />
  </React.StrictMode>
);
