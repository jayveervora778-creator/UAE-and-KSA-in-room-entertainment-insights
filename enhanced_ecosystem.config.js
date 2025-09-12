module.exports = {
  apps: [{
    name: 'osn-enhanced-dashboard',
    script: 'python3',
    args: '-m streamlit run enhanced_dashboard_with_wordcloud.py --server.port 8502 --server.address 0.0.0.0 --server.headless true --theme.base light',
    cwd: '/home/user/webapp',
    instances: 1,
    exec_mode: 'fork',
    watch: false,
    max_memory_restart: '1G',
    env: {
      PYTHONPATH: '/home/user/webapp',
      STREAMLIT_SERVER_HEADLESS: 'true',
      STREAMLIT_THEME_BASE: 'light'
    },
    log_file: '/home/user/webapp/logs/enhanced_streamlit.log',
    out_file: '/home/user/webapp/logs/enhanced_streamlit_out.log',
    error_file: '/home/user/webapp/logs/enhanced_streamlit_error.log',
    merge_logs: true,
    time: true
  }]
}