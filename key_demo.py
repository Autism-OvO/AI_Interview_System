"""示例配置：可提交到仓库，不包含任何真实密钥。"""

models = {
    'ds': 'deepseek-chat',
    'doubao': 'your-doubao-model-id',
    'thinking': 'your-thinking-model-id',
}

key = {
    'ds': 'your-deepseek-api-key',
    'ark': 'your-volcengine-ark-api-key',
    'gpt': 'your-openai-api-key',
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
}
