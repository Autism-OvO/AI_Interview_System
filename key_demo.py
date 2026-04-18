"""示例配置：可提交到仓库，不包含任何真实密钥。"""

import os

models = {
    'ds': 'deepseek-chat',
    'doubao': 'your-doubao-model-id',
    'thinking': 'your-thinking-model-id',
    'gpt4o': 'gpt-4o',
    'gpt4o_mini': 'gpt-4o-mini',
    'o3_mini': 'o3-mini',
    'deepseek_reasoner': 'deepseek-reasoner',
    'qwen_turbo': 'qwen-turbo',
    'qwen_plus': 'qwen-plus',
    'qwen_max': 'qwen-max',
    'glm_4_flash': 'glm-4-flash',
    'glm_4_plus': 'glm-4-plus',
    'kimi_auto': 'moonshot-v1-auto',
    'kimi_8k': 'moonshot-v1-8k',
    'silicon_deepseek_r1': 'deepseek-ai/DeepSeek-R1',
    'silicon_qwen_32b': 'Qwen/Qwen2.5-32B-Instruct',
    'openrouter_gpt4o_mini': 'openai/gpt-4o-mini',
    'openrouter_claude_sonnet': 'anthropic/claude-3.5-sonnet',
}

key = {
    'ds': 'your-deepseek-api-key',
    'ark': 'your-volcengine-ark-api-key',
    'gpt': 'your-openai-api-key',
    'openai': os.getenv('OPENAI_API_KEY', ''),
    'dashscope': os.getenv('DASHSCOPE_API_KEY', ''),
    'zhipu': os.getenv('ZHIPU_API_KEY', ''),
    'moonshot': os.getenv('MOONSHOT_API_KEY', ''),
    'siliconflow': os.getenv('SILICONFLOW_API_KEY', ''),
    'openrouter': os.getenv('OPENROUTER_API_KEY', ''),
}

# 完整的模型配置，每个条目包含显示名称、API Key、Base URL、模型名称
MODEL_CONFIGS = {
    'deepseek': {
        'name': 'DeepSeek Chat',
        'api_key': key['ds'],
        'base_url': 'https://api.deepseek.com',
        'model': models['ds'],
    },
    'doubao': {
        'name': '豆包 (Doubao)',
        'api_key': key['ark'],
        'base_url': 'https://ark.cn-beijing.volces.com/api/v3',
        'model': models['doubao'],
    },
    'thinking': {
        'name': '豆包深度思考',
        'api_key': key['ark'],
        'base_url': 'https://ark.cn-beijing.volces.com/api/v3',
        'model': models['thinking'],
    },
    'gpt': {
        'name': 'GPT (OpenAI)',
        'api_key': key['gpt'],
        'base_url': 'https://api.openai.com/v1',
        'model': 'gpt-4o-mini',
    },
    'gpt4o': {
        'name': 'OpenAI GPT-4o',
        'api_key': key.get('openai', ''),
        'base_url': 'https://api.openai.com/v1',
        'model': models['gpt4o'],
    },
    'gpt4o_mini': {
        'name': 'OpenAI GPT-4o mini',
        'api_key': key.get('openai', ''),
        'base_url': 'https://api.openai.com/v1',
        'model': models['gpt4o_mini'],
    },
    'o3_mini': {
        'name': 'OpenAI o3-mini',
        'api_key': key.get('openai', ''),
        'base_url': 'https://api.openai.com/v1',
        'model': models['o3_mini'],
    },
    'deepseek_reasoner': {
        'name': 'DeepSeek R1 (Reasoner)',
        'api_key': key['ds'],
        'base_url': 'https://api.deepseek.com',
        'model': models['deepseek_reasoner'],
    },
    'qwen_turbo': {
        'name': '通义千问 Qwen Turbo',
        'api_key': key.get('dashscope', ''),
        'base_url': 'https://dashscope.aliyuncs.com/compatible-mode/v1',
        'model': models['qwen_turbo'],
    },
    'qwen_plus': {
        'name': '通义千问 Qwen Plus',
        'api_key': key.get('dashscope', ''),
        'base_url': 'https://dashscope.aliyuncs.com/compatible-mode/v1',
        'model': models['qwen_plus'],
    },
    'qwen_max': {
        'name': '通义千问 Qwen Max',
        'api_key': key.get('dashscope', ''),
        'base_url': 'https://dashscope.aliyuncs.com/compatible-mode/v1',
        'model': models['qwen_max'],
    },
    'glm_4_flash': {
        'name': '智谱 GLM-4-Flash',
        'api_key': key.get('zhipu', ''),
        'base_url': 'https://open.bigmodel.cn/api/paas/v4/',
        'model': models['glm_4_flash'],
    },
    'glm_4_plus': {
        'name': '智谱 GLM-4-Plus',
        'api_key': key.get('zhipu', ''),
        'base_url': 'https://open.bigmodel.cn/api/paas/v4/',
        'model': models['glm_4_plus'],
    },
    'kimi_auto': {
        'name': 'Moonshot Kimi Auto',
        'api_key': key.get('moonshot', ''),
        'base_url': 'https://api.moonshot.cn/v1',
        'model': models['kimi_auto'],
    },
    'kimi_8k': {
        'name': 'Moonshot Kimi 8K',
        'api_key': key.get('moonshot', ''),
        'base_url': 'https://api.moonshot.cn/v1',
        'model': models['kimi_8k'],
    },
    'silicon_deepseek_r1': {
        'name': 'SiliconFlow DeepSeek-R1',
        'api_key': key.get('siliconflow', ''),
        'base_url': 'https://api.siliconflow.cn/v1',
        'model': models['silicon_deepseek_r1'],
    },
    'silicon_qwen_32b': {
        'name': 'SiliconFlow Qwen2.5-32B',
        'api_key': key.get('siliconflow', ''),
        'base_url': 'https://api.siliconflow.cn/v1',
        'model': models['silicon_qwen_32b'],
    },
    'openrouter_gpt4o_mini': {
        'name': 'OpenRouter GPT-4o-mini',
        'api_key': key.get('openrouter', ''),
        'base_url': 'https://openrouter.ai/api/v1',
        'model': models['openrouter_gpt4o_mini'],
    },
    'openrouter_claude_sonnet': {
        'name': 'OpenRouter Claude 3.5 Sonnet',
        'api_key': key.get('openrouter', ''),
        'base_url': 'https://openrouter.ai/api/v1',
        'model': models['openrouter_claude_sonnet'],
    },
}
