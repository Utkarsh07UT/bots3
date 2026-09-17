import re
with open("backend/app/streaming/consumer.py", "r") as f:
    content = f.read()

content = content.replace(
    '''raw_flow = json.loads(data[b'flow'].decode('utf-8') if type(data.get(b'flow')) == bytes else data.get('flow', '{}'))
    predictions = json.loads(data[b'predictions'].decode('utf-8') if type(data.get(b'predictions')) == bytes else data.get('predictions', '{}'))''',
    '''raw_flow_str = data.get("flow") or data.get(b"flow") or "{}"
    if isinstance(raw_flow_str, bytes): raw_flow_str = raw_flow_str.decode("utf-8")
    raw_flow = json.loads(raw_flow_str)
    
    pred_str = data.get("predictions") or data.get(b"predictions") or "{}"
    if isinstance(pred_str, bytes): pred_str = pred_str.decode("utf-8")
    predictions = json.loads(pred_str)'''
)

with open("backend/app/streaming/consumer.py", "w") as f:
    f.write(content)
