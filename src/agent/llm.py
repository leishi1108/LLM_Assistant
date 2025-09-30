import json
import uuid

import requests
from typing import List, Optional, Any
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage, ToolCall
from langchain_core.outputs import ChatResult, ChatGeneration


class CustomLLM(BaseChatModel):
    api_url: str
    api_key: str
    model_name: str
    tools: Optional[List[Any]] = None
    temperature: float
    max_tokens: int

    def bind_tools(self, tools: List[Any], **kwargs):
        return self.model_copy(update={"tools": tools})

    def _convert_tools_to_openai_format(self):
        if not self.tools:
            return []
        
        openai_tools = []
        for tool in self.tools:
            if hasattr(tool, "args_schema") and isinstance(tool.args_schema, type):
                try:
                    parameters = tool.args_schema.schema()
                except Exception:
                    parameters = {}
            else:
                parameters = getattr(tool, "args_schema", {})
            openai_tools.append({
              "type": "function",
              "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": (
                    parameters
                    if hasattr(tool, "args_schema")
                    else tool["parameters"]
                ),
              },
            })
        return openai_tools

    def _generate(
        self,
        messages: List[BaseMessage],
        stop=None,
        run_manager=None,
        **kwargs
    ) -> ChatResult:
        formatted_messages = []
        for m in messages:
            if m.type == "system":
                formatted_messages.append({"role": "system", "content": m.content})
            elif m.type == "human":
                formatted_messages.append({"role": "user", "content": m.content})
            elif m.type == "ai":
                formatted_messages.append({"role": "assistant", "content": m.content})
            else:
                formatted_messages.append({"role": "user", "content": m.content})

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model_name,
            "messages": formatted_messages,
            "temperature": kwargs.get("temperature", self.temperature),
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
        }

        tools_payload = self._convert_tools_to_openai_format()
        if tools_payload:
            payload["tools"] = tools_payload

        resp = requests.post(self.api_url, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()

        message_data = data["choices"][0]["message"]
        output_text = message_data.get("content", "")

        # 如果是工具调用
        if "tool_calls" in message_data:
            tool_calls_list = []
            for t in message_data.get("tool_calls", []):
                # 把 JSON 字符串解析成 dict
                args_dict = json.loads(t["function"]["arguments"])
                tool_calls_list.append(
                    ToolCall(
                        id=str(uuid.uuid4()),  # 唯一 ID
                        name=t["function"]["name"],
                        args=args_dict
                    )
                )
            generation = ChatGeneration(
                message=AIMessage(content="", tool_calls=tool_calls_list)
            )
        else:
            generation = ChatGeneration(
                message=AIMessage(content=output_text)
            )
        return ChatResult(generations=[generation])

    @property
    def _llm_type(self) -> str:
        return "aliyun-chat-model"
