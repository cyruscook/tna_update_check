data "aws_iam_policy_document" "assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "lambda_role" {
  name_prefix        = "tna-monitor-lambda-role-"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
}

data "aws_iam_policy_document" "lambda_access_s3" {
  statement {
    effect = "Allow"

    actions = [
      "s3:ListBucket",
      "s3:GetObject",
      "s3:PutObject",
    ]

    resources = [
      aws_s3_bucket.storage_bucket.arn,
      "${aws_s3_bucket.storage_bucket.arn}/*"
    ]
  }
}

resource "aws_iam_policy" "lambda_access_s3" {
  name_prefix = "tna-monitor-lambda-access-policy-"
  policy      = data.aws_iam_policy_document.lambda_access_s3.json
}

resource "aws_iam_role_policy_attachment" "lambda_access_s3" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_access_s3.arn
}

variable "function_filename" {
  type    = string
  default = "../lambda/lambda.zip"
}

locals {
  function_path = "${path.module}/${var.function_filename}"
}

resource "aws_lambda_function" "monitor_lambda" {
  filename      = local.function_path
  function_name = "tna-monitor-function"
  role          = aws_iam_role.lambda_role.arn
  handler       = "lambda_function.lambda_handler"
  architectures = ["arm64"]
  runtime       = "python3.13"
  timeout       = 15

  source_code_hash = filebase64sha256(local.function_path)

  environment {
    variables = {
      LOGLEVEL       = "DEBUG"
      STORAGE_BUCKET = aws_s3_bucket.storage_bucket.bucket
    }
  }
}

resource "aws_lambda_function_url" "monitor_lambda" {
  function_name      = aws_lambda_function.monitor_lambda.function_name
  authorization_type = "NONE"
}

output "function_url" {
  value = aws_lambda_function_url.monitor_lambda.function_url
}
