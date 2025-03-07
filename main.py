import re
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api.provider import LLMResponse
from openai.types.chat.chat_completion import ChatCompletion

@register("r1-filter", "Soulter", "可选择是否过滤推理模型的思考内容", "1.0.0", 'https://github.com/Soulter/astrbot_plugin_r1_filter')
class R1Filter(Star):
    def __init__(self, context: Context, config: dict):
        super().__init__(context)
        self.config = config
        self.display_reasoning_text = self.config.get('display_reasoning_text', True)
    
    @filter.on_llm_response()
    async def resp(self, event: AstrMessageEvent, response: LLMResponse):
        if self.display_reasoning_text:
            if response and response.raw_completion and isinstance(response.raw_completion, ChatCompletion):
                if len(response.raw_completion.choices) \
                        and response.raw_completion.choices[0].message:
                    message = response.raw_completion.choices[0].message
                    reasoning_content = "" 

                    if hasattr(message, 'reasoning') and message.reasoning:
                        reasoning_content = message.reasoning
                    elif hasattr(message, 'reasoning_content') and message.reasoning_content:
                        reasoning_content = message.reasoning_content

                    if reasoning_content:
                        response.completion_text = f"🤔思考：{reasoning_content}\n\n{message.content}"
                    else:
                        response.completion_text = message.content
        else: 
            completion_text = response.completion_text
            
            # 清除完整标签对和孤立闭合标签
            completion_text = re.sub(
                r'(<think>.*?</think>|.*?</think>)', 
                '', 
                completion_text, 
                flags=re.DOTALL|re.IGNORECASE
            ).strip()

            # 清理残留标签
            completion_text = re.sub(
                r'</?\s*think\s*/?>',  # 匹配所有变体标签
                '', 
                completion_text, 
                flags=re.IGNORECASE
            ).strip()

        
            completion_text = re.sub(r'\n{2,}', '\n', completion_text)
            
            response.completion_text = completion_text