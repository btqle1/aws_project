import json
import sys
import boto3

print('Loading function')
prefix = "hachi-"
end_bucket_name = prefix + "4452-f21-bao-results"

two_d_list = []
counter = 0
s3_client = boto3.client('s3')


def lambda_handler(event, context):
    global two_d_list
    global counter
    # print("Received event: " + json.dumps(event, indent=2))

    message = event['Records'][0]['Sns']['Message']

    # Check for special character
    if message[0] == "!":
        # Split into list
        message = message[1:]
        message = message.split(",")

        # Parse the evaluation method
        x = message[2]
        if x == "OPEN":
            x = 4
        if x == "HIGH":
            x = 5
        if x == "LOW":
            x = 6
        if x == "CLOSE":
            x = 7
        print("Calculate average based on: " + message[2] + " w/ period length: " + str(message[1]))

        # Sort first
        sorted_list = sort()

        # Calculate the avg
        lst = calc(int(message[1]), x, sorted_list)

        # Format the list into new string
        data = format_data(lst, message)

        # Create file and upload
        upload(data, message[0])

        # Wipe the 2d array for next lambda function
        two_d_list = []

    # If no special character, we add the message to the two_d array as a list
    else:
        print("From SNS: " + message)
        message = message.split(",")
        two_d_list.append(message)
    return message


def calc(period, func, sorted_list):
    entries = int(period / 5)
    points = len(sorted_list) - entries
    new_list = []

    for i in range(points):
        running_total = 0
        for j in range(entries):
            running_total = running_total + float(sorted_list[i+j][func])
        avg = running_total / entries
        temp = sorted_list[i]
        temp.insert(2, avg)
        new_list.append(temp)

    return new_list


def sort():
    global two_d_list
    two_d_list.sort(key=lambda x: (x[2], x[3]))
    return two_d_list

def format_data(new_list,spec_message):
    # <TICKER>,<PER>,<AVG>, <DATE>,<TIME>,<OPEN>,<HIGH>,<LOW>,<CLOSE>,<VOL>,<OPENINT>
    # <TICKER>,<PER>,<AVG_TYPE>,<QUOTE>,<DATE>,<TIME>,<AVG>,<VOL>
    header = "<TICKER>,<PER>,<AVG_TYPE>,<QUOTE>,<DATE>,<TIME>,<AVG>\n"
    body = ""
    for i in range(len(new_list)):
        ticker = str(new_list[i][0]) + ", "
        per = str(new_list[i][1]) + ", "
        avg_type = "SMA"+str(spec_message[1]) + ", "
        quote = str(spec_message[2]) + ", "
        date = str(new_list[i][4]) + ", "
        time = str(new_list[i][5]) + ", "
        avg = str(new_list[i][2]) + "\n"
        body = body + ticker+per+avg_type+quote+date+time+avg
    final_message = header+body
    return final_message

def upload(message, company):
    global s3_client
    global end_bucket_name
    file = open('/tmp/' + company + '_data.txt', 'w+')
    file.write(message)
    file.close()
    s3_client.upload_file('/tmp/' + company + '_data.txt', end_bucket_name, company + '_data.txt')