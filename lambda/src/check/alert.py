import os


SNS_TOPIC = os.getenv("SNS_TOPIC")


if not SNS_TOPIC:
    raise Exception("No SNS Topic")


def publish_change(sns, subject: str, msg: str):
    sns.publish(
        TopicArn=SNS_TOPIC,
        Message=msg,
        Subject=subject,
    )
