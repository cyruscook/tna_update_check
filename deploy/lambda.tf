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

data "aws_iam_policy_document" "lambda_access" {
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
  statement {
    effect = "Allow"

    actions = [
      "sns:Publish*"
    ]

    resources = [aws_sns_topic.changes.arn]
  }
  statement {
    effect = "Allow"

    actions = [
      "lambda:GetFunctionUrlConfig"
    ]

    resources = [aws_lambda_function.monitor_lambda.arn]
  }
}

resource "aws_iam_policy" "lambda_access" {
  name_prefix = "tna-monitor-lambda-access-policy-"
  policy      = data.aws_iam_policy_document.lambda_access.json
}

resource "aws_iam_role_policy_attachment" "lambda_access" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_access.arn
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
  timeout       = 15 * 60 // 15 minutes

  source_code_hash = filebase64sha256(local.function_path)

  environment {
    variables = {
      LOGLEVEL       = "DEBUG"
      STORAGE_BUCKET = aws_s3_bucket.storage_bucket.bucket
      SNS_TOPIC      = aws_sns_topic.changes.arn
    }
  }

  logging_config {
    log_format            = "JSON"
    application_log_level = "DEBUG"
    system_log_level      = "INFO"
  }

  dead_letter_config {
    target_arn = aws_sns_topic.changes.arn
  }
}

// TODO: aws_lambda_permission (blocked by https://github.com/hashicorp/terraform-provider-aws/pull/44858)

resource "aws_lambda_function_url" "monitor_lambda" {
  function_name      = aws_lambda_function.monitor_lambda.function_name
  authorization_type = "NONE"
}

output "function_url" {
  value = aws_lambda_function_url.monitor_lambda.function_url
}
