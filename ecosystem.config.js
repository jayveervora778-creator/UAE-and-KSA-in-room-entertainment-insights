module.exports = {
  apps: [{
    name: 'survey-dashboard',
    cwd: './backend',
    script: 'app.py',
    interpreter: 'python3',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '500M',
    env: {
      FLASK_ENV: 'production',
      FLASK_DEBUG: '0',
      PORT: '5000'
    },
    env_development: {
      FLASK_ENV: 'development',
      FLASK_DEBUG: '1',
      PORT: '5000'
    },
    error_file: './logs/err.log',
    out_file: './logs/out.log',
    log_file: './logs/combined.log',
    time: true
  }]
};