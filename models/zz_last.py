# -*- coding: utf-8 -*-

# File needs to be last in order to be able to have all Tables defined

# Instantiate Scheduler instance with the list of tasks
response.s3.tasks = tasks
s3task = s3base.S3Task()
current.s3task = s3task

# END =========================================================================