#!/bin/sh

service lighttpd start

# Upload the website code to S3
if [ !-z "$STORE_AWS_S3_WEB" ]; then
  echo "Uploading the React site to $STORE_AWS_S3_WEB"
  aws s3 sync build s3://$STORE_AWS_S3_WEB --acl bucket-owner-full-control
else
  echo "STORE_AWS_S3_WEB is not set.  Uploading the website will be skipped"
fi

while true; do
  sh ./run.sh
  
  # Calculate the number of seconds until midnight
  current_time=$(date +%s)
  next_midnight=$(date -d "tomorrow 00:00:00" +%s)
  sleep_seconds=$((next_midnight - current_time))

  echo "Sleeping for $sleep_seconds seconds until midnight..."
  sleep $sleep_seconds
done