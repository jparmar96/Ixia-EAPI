#!/usr/bin/python
# -*- coding: utf-8 -*-
#For python3: pip install jsonrpclib-pelix
#For python2: pip install jsonrpclib
from jsonrpclib import Server
from pprint import pprint
import jinja2
import os
import netaddr
import json

def report(op):
    op = op
    TEMPLATE = """{{ showversion2 }}
    <html>
        <head>
            <meta charset="utf-8">
                <style>
    pre {
        background-color: #f8f8f8;
        border: 1px solid #ddd;
        font-size: 13px;
        line-height: 19px;
        overflow: auto;
        padding: 6px 10px;
        border-radius: 3px;
    }
    code {
        white-space: pre;
    }
                </style>
        </head>

        <body>
            {% if h1 %}
            <h1>{{ h1 }}</h1>
            {% endif %}

            {% for x in op %}
            <pre>
            <code>
{{ x }}
            </code>
            </pre>
            {% endfor %}
        </body>
    </html>
    """


    j2_env = jinja2.Environment(trim_blocks=True, lstrip_blocks=True, keep_trailing_newline=True)
    template = j2_env.from_string(TEMPLATE)

    with open("showversion.html", 'w') as fh:
        htmlContent = template.render(op = op)
        #print(htmlContent)
        fh.write(htmlContent)


def main():
    switch = Server("http://admin:@nfc302/command-api")
    resp = switch.runCmds(1,["show version"],"text")
    #resp = switch.runCmds(1,["show version"],"text")
    op = []
    op.append("nfc302: " + resp[0]['output'])

    #resp = switch.runCmds(1,["show reload cause"],"text")
    #op.append("nfc302: \n" + resp[0]['output'])

    #pprint(op)
    report(op)





if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)







"""
resp = switch.runCmds(1,["show interfaces status connected"],"json")
pprint(resp)

for interface in resp[0]['interfaceStatuses'].keys():
    #print(interface)
    if interface == "Management1":
        resp = switch.runCmds(1,["show interfaces " + interface + " description"],"json")
        pprint(resp)
        resp = switch.runCmds(1,["configure", "interface "+ interface, "description eapi-configured"],"json")
        pprint(resp)
        resp = switch.runCmds(1,["show interfaces " + interface + " description"],"json")
        pprint(resp)
        resp = switch.runCmds(1,["configure", "interface "+ interface, "no description"],"json")
        pprint(resp)
        resp = switch.runCmds(1,["show interfaces " + interface + " description"],"json")
        pprint(resp)
"""
