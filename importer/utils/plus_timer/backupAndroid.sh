# Backup plus timer from phone
./platform-tools/adb backup "-f -noapk com.pluscubed.plustimer"

# Copy backup
DATE=$(date +"%Y%m%d%H%M")

cp backup.ab ../Databases/PlusTimer_$DATE.ab
