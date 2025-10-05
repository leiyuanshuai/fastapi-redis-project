from src.config.env import env

ai_configs = {
  # /*---------------------------------------local-------------------------------------------*/
  "local": {
    "model": "deepseek-r1-distill-qwen-7b",
    "url": "http://127.0.0.1:1234/v1/chat/completions",
    "key": env.llm_key_local
  },
  "local_glm": {
    "model": "glm-4-9b-0414",
    "url": "http://127.0.0.1:1234/v1/chat/completions",
    "key": env.llm_key_local
  },
  "local_embedding": {
    "model": "text-embedding-text2vec-large-chinese",
    "url": "http://127.0.0.1:1234/v1/embeddings",
    "key": env.llm_key_local
  },
  # /*---------------------------------------deepseek-------------------------------------------*/
  'deepseek-v3': {
    'model': 'deepseek-chat',
    'url': 'https://api.deepseek.com/chat/completions',
    'key': env.llm_key_deepseek,
  },
  'deepseek-r1': {
    'model': 'deepseek-reasoner',
    'url': 'https://api.deepseek.com/chat/completions',
    'key': env.llm_key_deepseek,
  },
  # /*---------------------------------------huoshan-------------------------------------------*/
  'huoshan-deepseek-v3': {
    'model': 'deepseek-v3-250324',
    'url': 'https://ark.cn-beijing.volces.com/api/v3/chat/completions',
    'key': env.llm_key_huoshan,
  },
  'huoshan-deepseek-r1': {
    'model': 'deepseek-r1-distill-qwen-7b-250120',
    'url': 'https://ark.cn-beijing.volces.com/api/v3/chat/completions',
    'key': env.llm_key_huoshan,
  },
  'huoshan-doubao': {
    'model': 'doubao-1-5-lite-32k-250115',
    'url': 'https://ark.cn-beijing.volces.com/api/v3/chat/completions',
    'key': env.llm_key_huoshan,
  },
  'huoshan-think-pro': {
    'model': 'doubao-1-5-thinking-pro-250415',
    'url': 'https://ark.cn-beijing.volces.com/api/v3/chat/completions',
    'key': env.llm_key_huoshan,
  },
  'huoshan-doubao-seed': {
    'model': 'doubao-seed-1-6-250615',
    'url': 'https://ark.cn-beijing.volces.com/api/v3/chat/completions',
    'key': env.llm_key_huoshan,
  },
  'doubao-vision-lite': {
    'model': 'doubao-1.5-vision-lite-250315',
    'url': 'https://ark.cn-beijing.volces.com/api/v3/chat/completions',
    'key': env.llm_key_huoshan,
  },

  'huoshan-embedding-240715': {
    "model": 'doubao-embedding-text-240715',
    "url": 'https://ark.cn-beijing.volces.com/api/v3/embeddings',
    'key': env.llm_key_huoshan,
  },
  # /*---------------------------------------bailian-------------------------------------------*/
  'bailian-qwen-turbo': {
    'model': 'qwen-turbo',
    'url': 'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions',
    'key': env.llm_key_bailian,
  },
  'bailian-embedding': {
    'model': 'text-embedding-v4',
    'url': 'https://dashscope.aliyuncs.com/compatible-mode/v1/embeddings',
    'key': env.llm_key_bailian,
  },
}
