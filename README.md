# S3SuperSync

## Objective
Deduplication of chunks sent to s3 by copying parts that are already available in other objects. 

*NOTE* This is not an attempt to conserve storage useage on S3, infact the exact opposite, the idea is the more data you have in S3 the less you have to transfer. This requires a versioned bucket.

## How it works
In short S3SuperSync faciliates a multipart upload to S3 sending the least amount of chunks possible. It chunks files and hashes those chunks with two different hashing algorithms. The parts are tracked via a DynamoDB table where the hashes create a composite key. A location column in the DynamoDB table instructs S3SuperSync on where to find chunks that are identical to the chunk to be upload, then uses those chunks to copy from S3 to S3 rather then sending the chunk from your local site. 

### Chunking
S3 multipart uploads consist of chunks no smaller than 5MB with exception for the last chunk. The number of parts in a multipart upload are limited to 10,000. S3SuperSync checks to see if the destination file already exists, if it does it will attempt to use it's part size. This application uses a 8MB default chunk size. If the size of your file divided by 8MB equates to more than 10,000 parts the chunk size is doubled until True.

### Hashing 
Each part is hashed with the sha3-512 and blake2b algorithms. Two algorithms are used to lower the possibility of hash colisions. 

### Metadata
A DynamoDB table name is provided by the user, the table is created if it does not exist. If the table does exist it's checked for the approprate primary key attributes. The table name defaults to 'supersync'. The partition key is named sha3, the sort key is named blake2. A third item attribute is used to store a list of objects that instruct the system on where it can find a particular chunk. After a chunk is hashed the table is checked for a match, if a match is found the multipart upload for that part is a copy from an object in s3, if the hashes are not found the chunk is uploaded for that part in the multipart upload. 
Example item:
``` JSON
{
  "sha3": "HASH",
  "blake2": "RANGE",
  "locations": [
    {
      "bucket": "String",
      "key": "String",
      "part": "Int",
      "version": "String",
      "upload_id": "String",
      "content_range": "String"
    }
  ]
}
```

### Concurrency
S3SuperSync defaults to 10 concurrent processes.

## Usage
```
usage: supersync.py [-h] [-d] [-p PROFILE] [-c CONCURRENCY] [-t TABLE_NAME]
                    local dest

Sync file changes to s3

positional arguments:
  local                 Local file to be synced
  dest                  Destination of file to be synced

optional arguments:
  -h, --help            show this help message and exit
  -d, --debug           Turn on log level debug
  -p PROFILE, --profile PROFILE
                        AWS Profile to use.
  -c CONCURRENCY, --concurrency CONCURRENCY
                        Number of processes to use.
  -t TABLE_NAME, --table_name TABLE_NAME
                        DynamoDB table name too use.
  -s {default,fast}, --speed {default,fast}
                        Hash speed option. Warning: fast hash may result in
                        colisions and data coruption. Automatically adds speed
                        type to table name because the attributes differ.
```

# Fast Hash Warning
I've implemented what looks like a faster hashing algorithm for when the hashing is a bottle neck. This hash is xxhash and is not a cryptographic hash and therefore more prone to colisions. *Also* when using fast hash there is only one hashing algorithm used which further increases the likelyhood of colisions. When using this option it is highly advised to use a separate table_name per item uploaded. 

## ToDo
1. File locking for writes
2. Info output
3. Abort multipart upload on error
4. Clean Ctr-C 
5. Walk directory structures
6. Support for files less than 5/8MB 
7. Encryption Support
8. Create indexer that will scan S3 and index what chunks already exist
9. Stats about how many chunks are deduplicated per item
10. Status
11. Retry decorator


# Stats
## 31GB Upload VMDK
#### First Upload
real	192m55.349s
user	20m49.460s
sys	3m5.912s
#### No Change Upload @ 50 r/w Capacity w/ ~10 w/r used 10 concurrency 
real	17m5.263s
user	17m6.136s
sys	0m58.500s
#### Small Change Upload @ same perf as prior
real	25m23.252s
user	16m7.296s
sys	1m6.892s


