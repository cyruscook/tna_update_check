# TNA Update Check

A tool to monitor for changes to records at The National Archives. Uses AWS Lambda to host a website to configure which records will be monitored. The Lambda will check each night for any changes to those records. Paticularly useful for being alerted to changed in closure status of records that are currently retained/closed.

Any changes found by the Lambda will be published to an SNS topic. You should configure any subscribers to the topic yourself, for example an email address to receive email notifications.
