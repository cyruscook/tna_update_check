resource "aws_cloudwatch_metric_alarm" "lambda_invocations" {
  alarm_name = "tna-monitor-no-invocations"

  namespace   = "AWS/Lambda"
  metric_name = "Invocations"
  dimensions = {
    FunctionName = aws_lambda_function.monitor_lambda.function_name
  }

  // Should be at least 1 execution every 36 hours (the schedule is once every 24 hours)
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 3
  period              = 60 * 60 * 12 // 12 hours
  statistic           = "Sum"
  threshold           = 1
  treat_missing_data  = "breaching"

  actions_enabled   = true
  alarm_actions     = [aws_sns_topic.changes.arn]
  ok_actions        = [aws_sns_topic.changes.arn]
  alarm_description = "No invocations of the monitor lambda in 36 hours"
}

resource "aws_cloudwatch_metric_alarm" "lambda_errors" {
  alarm_name = "tna-monitor-errors"

  namespace   = "AWS/Lambda"
  metric_name = "Errors"
  dimensions = {
    FunctionName = aws_lambda_function.monitor_lambda.function_name
  }

  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  period              = 60 * 60 * 1 // 1 hour
  statistic           = "Sum"
  threshold           = 0
  treat_missing_data  = "notBreaching"

  actions_enabled   = true
  alarm_actions     = [aws_sns_topic.changes.arn]
  ok_actions        = [aws_sns_topic.changes.arn]
  alarm_description = "Errors occured in monitor lambda"
}
