#!/usr/bin/env python3.6
import argparse

from supersync.logger import console_logger, logging
from supersync.s3supersync import S3SuperSync

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Sync file changes to s3')
    parser.add_argument('local', type=str, help='Local file to be synced')
    parser.add_argument('dest', type=str, help='Destination of file to be synced')
    parser.add_argument('-d', '--debug', dest='debug', action='store_true', help='Turn on log level debug')
    parser.add_argument('-p', '--profile', dest='profile', default='default', help='AWS Profile to use.')
    parser.add_argument('-c', '--concurrency', dest='concurrency', type=int, default=10, help='Number of processes to use.')
    parser.add_argument('-t', '--table_name', dest='table_name', type=str, default='supersync', help='DynamoDB table name too use.')
    parser.add_argument('-s', '--speed', dest='speed', type=str, choices=['default','fast'], default='default', help='Hash speed option. Warning: fast hash may result in colisions and data coruption. Automatically adds speed type to table name because the attributes differ.')
    args = parser.parse_args()
    if args.debug:
        console_logger.setLevel(logging.DEBUG)
    if args.speed != 'default':
        args.table_name = args.table_name + '_' + args.speed
    supersync = S3SuperSync(args.profile,args.table_name,args.local,args.dest,args.concurrency,args.speed)
    supersync.sync()	
