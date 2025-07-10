# Construct
## Basic working flow
1. Accept user input, in text format
2. Pass the user input to rule base engine
3. Base on the response, decide whether call the function or leave the request to local LLM
4. After function calling is done, decide what to response base on the response from function calling
    * Execution success: Base on the function which called by router, generate a response to tell user that function execution is done
    * Execution failed: Base on the function which called by router, generate a response to tell user that function execution is failed
    * No function called: In this scenario, do not generate any response, just print message to terminal and tell developer what did router do

## RuleBase engine
Import RuleBase engine like this:
```python
from RuleBaseEngine.RuleBaseEngine import RuleEngine
```
RuleBaseEngine_usage.md describe a sort of usage of the rule base engine
## LLM
Import local LLM like this 
```python
from ChatBots.LocalChatBot import LocalChatBot
```
Use the method: intent_phrase(user_query:str) to extract the real user intention
## Function calling
There is an API register table with JSON format exits in: 
* Windows style path: "\RegistryModule\Registration.json"
* Unix style path: "/RegistryModule/Registration.json"
Function calling should compatible with both style of path.
### The way to call a function
Load Registration.json, and check whether the function name do exist in registry table, if so use method "function_call(user_query:str, function_name:str)" in LocalChatBot.py.
If not, use the "unknown_function_call(user_query:str, function_name:str)" and try to call the function again
**Tips:**
* If rule base engine fail to extract function name, then pass "" as augment
## Others
* The return of rule base engine should be a tuple, which contain function name as the first element, user intent as the second element
* If the return of rule base engine is ("LLM", "leave to chat_bot"), then leave this request to local LLM with method: "chat(user_query:str)"
* If the risk level of current operation is too high, then router should not execute, also, it should explain the reason base on Rules.json
* The return value of router is a Python string, if any error happened, then return value should be "Error: " + error message