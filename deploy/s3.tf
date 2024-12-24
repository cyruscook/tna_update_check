resource "aws_s3_bucket" "storage_bucket" {
  bucket_prefix = "tna-monitor-storage-"
}

resource "aws_s3_object" "recs" {
  bucket  = aws_s3_bucket.storage_bucket.bucket
  key     = "monitored_records.json"
  content = "[]"

  lifecycle {
    ignore_changes = [content]
  }
}

resource "aws_s3_object" "redirs" {
  bucket  = aws_s3_bucket.storage_bucket.bucket
  key     = "redirs.json"
  content = "{}"

  lifecycle {
    ignore_changes = [content]
  }
}
