import ast
import traceback


def lambda_handler(event, context):
    
    try:
        if type(event["body"]) == dict:
            event_body = event["body"]
        else:
            event_body = ast.literal_eval(event["body"])

        return {
            "statusCode": 200,
            "body": f"Hi {event_body['name']}"
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": f"Error: {traceback.format_exc()}"
        }


if __name__ == "__main__":
    e = {
        "body": {
            "name": "Sreeram"
        }
    }
    response = lambda_handler(event=e, context=None)
    print(response)