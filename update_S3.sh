#!/usr/bin/env bash

# Upload support files to location specified

S3_BASE="< Location of S3 bucket used to hold CSS and Favicon files >"

s3cmd -d -P -m 'text/css' put styles.css $S3_BASE

s3cmd -d -P -m 'image/x-icon' put favicon.ico $S3_BASE
