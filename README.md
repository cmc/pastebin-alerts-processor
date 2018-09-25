# pastebin-alerts-smtpd

AWS Lambda for processing alerts received via SES.

Pastebin -> SES Handler -> SNS -> Lambda

Stores content in S3 + Metadata in Dynamo.

Also, standalone mail handler for pastebin keyword alerts (https://pastebin.com/alerts), receives notification email, retrieves paste, writes filename w/ keyword & time.
