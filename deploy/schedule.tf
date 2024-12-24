resource "aws_scheduler_schedule" "check" {
  name_prefix = "tna-check-"

  flexible_time_window {
    mode                      = "FLEXIBLE"
    maximum_window_in_minutes = 30
  }

  schedule_expression = "cron(0 3 * * ? *)"
  state               = "ENABLED"

  target {
    arn      = aws_lambda_function.monitor_lambda.arn
    role_arn = aws_iam_role.scheduler.arn
    input = jsonencode({
      action = "check"
    })
  }
}

data "aws_iam_policy_document" "sched_assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["scheduler.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "scheduler" {
  name_prefix        = "sched-"
  assume_role_policy = data.aws_iam_policy_document.sched_assume_role.json
}

resource "aws_iam_role_policy_attachment" "scheduler" {
  policy_arn = aws_iam_policy.scheduler.arn
  role       = aws_iam_role.scheduler.name
}

data "aws_iam_policy_document" "schedule_access" {
  statement {
    effect = "Allow"

    actions = [
      "lambda:InvokeFunction"
    ]

    resources = [
      aws_lambda_function.monitor_lambda.arn
    ]
  }
}

resource "aws_iam_policy" "scheduler" {
  name_prefix = "sched-"
  policy      = data.aws_iam_policy_document.schedule_access.json
}
