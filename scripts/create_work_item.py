from robocorp import workitems
# Define the payload for the new output work item
payload = {
    "search_phrase": "trump",
    "anotherKey": "anotherValue"
}


def save_work_item_payloads(payloads):
    for payload in payloads:
        variables = dict(traffic_data=payload)
        print(payload)
        workitems.outputs.create(variables)


save_work_item_payloads(payload)
