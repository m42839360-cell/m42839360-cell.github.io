# Creating Custom Kagent Agents

As part of my experiments with [agents and kubernetes](https://github.com/maluio/agentic-k8s) I gave [kagent](https://kagent.dev) a shot.

I came up with [this setup](https://github.com/maluio/agentic-k8s/tree/main/kagent).

I created two kagent custom agents:

* [Installer Agent](https://github.com/maluio/agentic-k8s/blob/6144b06161457e60ee831c031f1094f5c28019ed/kagent/agents/installer-agent.yml)
* [Uninstaller Agent](https://github.com/maluio/agentic-k8s/blob/6144b06161457e60ee831c031f1094f5c28019ed/kagent/agents/uninstaller-agent.yml)

You can chat with these to (un)install k8s resources.

**This is me asking the installer agent to create a configmap:**

```bash
kagent  0.7.4
   Sessions                   Chat with kagent/installer-agent (session ctx-b3ac416b-e14c-4eb8-916c-70b8c3f3b5a5)

│ installer                   You: Install a configmap "cm-1" with values "foo=bar" in default namespace.
│ ctx-b3ac416b-e14c-4eb8-916c…

                              🔧 Tool Call: k8s_create_resource (id: call_ZJeXHdntr6BRVP6t1NjVKxUD)
                              {
                                "yaml_content": "apiVersion: v1\nkind: ConfigMap\nmetadata:\n  name: cm-1\n  namespace:
                              default\ndata:\n  foo: bar\n"
                              }


                              📊 Tool Result: k8s_create_resource (id: call_ZJeXHdntr6BRVP6t1NjVKxUD)
                              {
                                "result": {
                                  "content": [
                                    {
                                      "text": "configmap/cm-1 created\n",
                                      "type": "text"
                                    }
                                  ],
                                  "isError": false
                                }
                              }

                              Agent:
                              The ConfigMap "cm-1" with the value foo=bar has been successfully created in the default namespace.

                              To verify this, you can retrieve the ConfigMap "cm-1" from the default namespace and check its data.

                              If you want, I can fetch and display the ConfigMap data now for verification. Would you like me to do
                              that?

                              ───────────────────────────────────────────────────────────────────────────────────────────────────────
                              ☱ Working… 0s                                                                                                           ☱ Working… 1s                                                                                                                       ☱ Working… 2s                                                                                                                       ☱ Working… 3s                                                                                                                       ☱ Working… 4s                                                                                                                       ☱ Working… 5s                                                                                                                       ☱ Working… 6s                                                                                                                       ☱ Working… 7s                                                                                                                       ☱ Working… 8s                                                                                                                       ☱ Working… 9s                                                                                                                       ☱ Working… 10s
                              > Type a message (Enter to send)

```

**This is me asking the uninstaller agent to delete the configmap:**

```bash
kagent  0.7.4
   Sessions                   Chat with kagent/uninstaller-agent (session ctx-9c664fef-c9f1-4048-9db2-ac3677aecae9)

│ uninstaller                 You: Delete configmpa cm-1 in default namespace
│ ctx-9c664fef-c9f1-4048-9db2…

                              🔧 Tool Call: k8s_delete_resource (id: call_rfWtl2j025iLxLT25aBuZvw9)
                              {
                                "namespace": "default",
                                "resource_name": "cm-1",
                                "resource_type": "configmap"
                              }

                              📊 Tool Result: k8s_delete_resource (id: call_rfWtl2j025iLxLT25aBuZvw9)
                              {
                                "result": {
                                  "content": [
                                    {
                                      "text": "configmap \"cm-1\" deleted from default namespace\n",
                                      "type": "text"
                                    }
                                  ],
                                  "isError": false
                                }
                              }



                              Agent:
                              The ConfigMap named "cm-1" has been deleted from the "default" namespace.

                              To verify, you can list all ConfigMaps in the "default" namespace and confirm that "cm-1" no longer
                              appears. This ensures the resource removal was successful.

                              If you need assistance with any other Kubernetes resources or further verification, let me know!
───────────────────────────────────────────────────────────────────────────────────────────────────────                  ☱ Working… 0s                                                                                                                       ☱ Working… 1s                                                                                                                       ☱ Working… 2s                                                                                                                       ☱ Working… 3s                                                                                                                       ☱ Working… 4s                                                                                                                       ☱ Working… 5s                                                                                                                       ☱ Working… 6s                                                                                                                       ☱ Working… 7s                                                                                                                       ☱ Working… 8s
                              > Type a message (Enter to send)
```