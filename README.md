<div align="center">
  <img src="misskey_plugin_huaer_bot/misc/IMG_1411.PNG" width="180" height="180" alt="MisskeyPluginLogo"></a>
</div>

<div align="center">

# misskey-plugin-huaer-bot

_✨基于硅基/DeepSeek API的智能对话插件✨_

<img src="https://img.shields.io/badge/API-siliconflow-red" alt="license">
</a>
</a>
<a href="https://python.org/">
<img src="https://img.shields.io/badge/python-3.9+-orange.svg" alt="python">
</a>
<a href="https://mit-license.org/">
<img src="https://img.shields.io/badge/license-MIT-yellow.svg" alt="license">
</a>
<a href="https://www.siliconflow.com/">
<a href="https://github.com/misskey-dev/misskey" target="_blank"><img src="https://img.shields.io/badge/misskey-plat-green.svg" alt="Misskey">
<a href="https://github.com/inkink365/misskey-plugin-huaer-bot">
<img src="https://img.shields.io/badge/poetry-managed-cyan" alt="license">
</a>
<a href="https://pypi.org/project/misskey-plugin-huaer-bot/">
    <img src="https://img.shields.io/pypi/v/misskey-plugin-huaer-bot.svg" alt="pypi">
</a>
<a href="https://www.deepseek.com/" target="_blank"><img src="https://github.com/deepseek-ai/DeepSeek-V2/blob/main/figures/badge.svg?raw=true" alt="deepseek">
</a>

</div>

## 💿 安装

__pip__

    pip install misskey-plugin-huaer-bot


__git clone__

    见本项目github界面


## 📜 功能特性
- 具有人格定制功能，可以自由设定人格
- 具有频道管理器，可以小规模的同时管理数个频道
- 基于siliconflow丰富的API，可以轻而易举的导入其它大语言模型
- 基于misskey自带的“回复链”实现记忆功能，即以一段连续的回复构成的对话记录为记忆体，即方便的实现了记忆的增删和存储，又获得了很好的会话场景

## 🧐 快速上手/配置
- （必填）在项目文件所在位置下，找到 **'config.toml'** 文件，可在其中根据注释修改配置，添加自己的API key等；所有要添加的频道请用列表格式将其ID输入到`channel_id`
- 按示例启动，通过在指定频道中@bot来对话，通过不断回复来继续对话！

## 🎉 详细使用
#### 示例：
``` python
import misskey_plugin_huaer_bot

misskey_plugin_huaer_bot.run() #如果使用pip安装
```

``` shell
cd 项目文件夹
python demo.py #如果使用git clone
```

上述代码可以实现80%的功能；
如对发送的文本有特殊需求，参见源代码`poster.py`示例

## 🔭 records
- _25.7.18_ v1.0.1 默认配置debug完毕，正式发布

## 🙏 感谢
- Misskey伟大的开源项目
- D圣的开源和S圣的平台搭建
- 欢迎大家加入`https://hub.imikufans.com`！这是一个正在建设中的优质术力口交流平台！
- 各位用户朋友们

