# Managing the dashboard

## Hosting on the docker instance

By default, the docker instance installed lighttpd to serve the dashboard on port 8081.

Option 1 - By default, the docker instance will remain persistent, and serve the report.

Option 2 - The instance can run in immutable mode, where it will upload the website to an AWS S3 bucket.

** TODO ** How to switch the docker instance off.

## Hosting locally

TODO

## Hosting on AWS S3

Configure an AWS bucket as a [static website](https://docs.aws.amazon.com/AmazonS3/latest/userguide/WebsiteHosting.html).

A few things to note on the AWS S3 bucket.

* Index document must be `index.html`
* Error document must also be `index.html`

Use the following sample bucket policy (just replace the bucket name with your own bucket name)

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": [
                "s3:GetObject"
            ],
            "Resource": [
                "arn:aws:s3:::Bucket-Name/*"
            ]
        }
    ]
}
```

Set the environment variable `STORE_AWS_S3_WEB` to the bucket name.

For more information, refer to the [AWS](https://docs.aws.amazon.com/AmazonS3/latest/userguide/WebsiteAccessPermissionsReqd.html) documentation.




