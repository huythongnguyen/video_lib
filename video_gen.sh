#!/bin/bash
# Video Generation Script
# Usage: ./video_gen.sh contents/books/Path/To/job.json

if [ -z "$1" ]; then
    echo "Usage: ./video_gen.sh <job_file>"
    exit 1
fi

JOB_FILE=$1

# Add project root to PYTHONPATH if needed
# export PYTHONPATH=$PYTHONPATH:.

echo "Processing job: $JOB_FILE"
python video_lib_cli.py "$JOB_FILE" --llm gemini --language Vietnamese

# Sample Windows (PowerShell) command:
# python video_lib_cli.py "contents\books\Meaningful-to-Behold\16_Wisdom\17_SHOWINGTHATEXCELLENTRESULTSWILLCOMEFROMABANDONINGG\job.json" --llm gemini --language Vietnamese
