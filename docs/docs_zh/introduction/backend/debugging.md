# 如何调试？

OxyGent推荐您使用可视化界面进行调试，以下是有关调试的指南：

## 启动可视化服务

可以通过`start_web_service`启动可视化服务：

```python
async def main():
    async with MAS(oxy_space=oxy_space) as mas:
        await mas.start_web_service(first_query="How many chars in 'OxyGent'?")
```

如果编译正常，在命令行会显示OxyGent的版本等系统信息；否则会显示错误。

```apache
   ____             ______           __ 
  / __ \_  ____  __/ ____/__  ____  / /_
 / / / / |/_/ / / / / __/ _ \/ __ \/ __/
/ /_/ />  </ /_/ / /_/ /  __/ / / / /_  
\____/_/|_|\__, /\____/\___/_/ /_/\__/  
          /____/                        
2025-07-20 20:36:03,613 - INFO ================================================================
2025-07-20 20:36:03,613 - INFO 🚀 OxyGent MAS Application Startup Information
2025-07-20 20:36:03,613 - INFO ================================================================
2025-07-20 20:36:03,613 - INFO App Name     : app
2025-07-20 20:36:03,613 - INFO Version      : 1.0.0
2025-07-20 20:36:03,613 - INFO Environment  : default
2025-07-20 20:36:03,613 - INFO Port         : 8080
2025-07-20 20:36:03,613 - INFO Python Ver   : 3.10.18
2025-07-20 20:36:03,613 - INFO Cache Dir    : ./cache_dir
2025-07-20 20:36:03,614 - INFO Start Time   : 2025-07-20 20:36:03
2025-07-20 20:36:03,614 - INFO ================================================================
2025-07-20 20:36:03,616 - INFO 🌐 OxyGent MAS Organization Structure Overview
2025-07-20 20:36:03,616 - INFO ================================================================
```

## 和智能体对话
![](http://storage.jd.com/ai-gateway-routing/prod_data/oxygent_docs_images/1.png)

界面主页包含以下部分：
+ **MAS的结构**: 包含所有注册好的智能体和工具
+ **对话框**: 包含用户和智能体/智能体和智能体之间的所有对话
+ **思考细节**: 包含智能体内部LLM的思考过程和输出
+ **文件工具**: 保存和加载MAS的工具

![](http://storage.jd.com/ai-gateway-routing/prod_data/oxygent_docs_images/2.png)

您可以在对话框中直接输入查询内容，或是添加图片或视频作为附件。

如果您希望直接向某个智能体发送消息，您可以使用 `@` 。

## 实时监测

![](http://storage.jd.com/ai-gateway-routing/prod_data/oxygent_docs_images/3.png)

正在工作的智能体将以高亮形式展示在左侧的MAS结构图中，同时智能体的思考过程和输出将实时展示在对话区域。

![](http://storage.jd.com/ai-gateway-routing/prod_data/oxygent_docs_images/4.png)

右上角的debug工具能够回溯MAS运行过程，包括移至开始 `«`, 移至最后 `»`, 单步向前 `<`, 单步向后 `>`和自动重播 `⏵` 。您可以使用这些工具按步骤监测MAS的运行。

## 查看运行细节

![](http://storage.jd.com/ai-gateway-routing/prod_data/oxygent_docs_images/5.png)

点击任意思考过程即可进入智能体详情页，这个页面展示了智能体LLM的参数配置、详细的对话过程和 `json` 格式的元数据，您可以点击页面上方的结构图切换要观察的LLM或工具。

![](http://storage.jd.com/ai-gateway-routing/prod_data/oxygent_docs_images/6.png)

## 调试执行过程

![](http://storage.jd.com/ai-gateway-routing/prod_data/oxygent_docs_images/7.png)

您可以通过点击 `View 1 | View 2` 切换详情页的上方视图，查看MAS的性能和各调用过程的生命周期。

![](http://storage.jd.com/ai-gateway-routing/prod_data/oxygent_docs_images/8.png)

详情页同样提供单步调试工具。您可以点击 `regenerate` 在任意节点重新生成output。

[上一章：生成训练样本](../advanced/training.md)
[回到首页](../readme.md)

---

## 相关示例

- [启动 MAS 服务示例](../../examples/backend/demo_launch_mas.md) — 展示如何启动可视化 Web 服务进行调试
