#!/usr/bin/env python3

import aws_cdk as cdk

from interview_video_processor.interview_video_processor_stack import InterviewVideoProcessorStack


app = cdk.App()
InterviewVideoProcessorStack(app, "InterviewVideoProcessorStack")

app.synth()
