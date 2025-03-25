# Restart the service
sudo systemctl restart flask-app.service

# Check the status
sudo systemctl status flask-app.service

```bash
chmod +x backup_to_git.sh
```

# Open crontab editor
```bash
crontab -e
```

```bash
0 0 * * * /home/ubuntu/officetracker/backup_to_git.sh >> /home/ubuntu/officetracker/git_backup.log 2>&1
```

# Check the log
cat /home/ubuntu/officetracker/git_backup.log

