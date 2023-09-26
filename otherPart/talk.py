import openai

# 替换为您的API密钥
openai.api_key = "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"

openai.proxy = 'https://cdn-p1-lm.baibianxiaoying.top:15160'


# 构建请求所需的参数
# prompt = "你好"
# max_tokens = 100  # 生成的最大令牌数
# temperature = 0.8  # 控制输出随机性的值，范围为0到1

# 发送请求到GPT-3.5模型
# response = openai.Completion.create(
#     engine="gpt-3.5-turbo",
#     prompt=prompt,
#     max_tokens=max_tokens,
#     temperature=temperature,
#     n=1,  # 生成的回答数量
#     stop=None,  # 可以设置一个停止符，例如：["\n"]
# )

def talk(messages):
    print(messages)
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "你是一名高级程序员"}, {"role": "user", "content": messages}]
    )
    response = completion.choices[0].message["content"].encode("utf-8").decode("utf-8")
    return response
