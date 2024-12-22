resource "aws_s3_bucket" "storage_bucket" {
  bucket_prefix = "tna-monitor-storage-"
}

resource "aws_s3_object" "object" {
  bucket = aws_s3_bucket.storage_bucket.bucket
  key    = "monitored_records.json"
  content = "[]"

  lifecycle {
    ignore_changes = [ content ]
  }
}
