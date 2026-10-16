# 海帕姆：银心初航｜Stellaris Mod 设计与开发交接工程

版本：0.1.0-design-handoff
整理日期：2026-10-16（Asia/Shanghai）

**这是一份完整的设计与开发交接工程，不是可安装或已验证的群星 Mod。**

本工作区在打包前没有游戏脚本、模型或可运行构建；本包将当前对话里的最新用户要求持久化，供后续云端开发使用。不要将文档校验通过称为游戏测试通过。

## 先读什么

1. `docs/01-confirmed-design.md`：最新定案方向。
2. `design/requirements.json`：可机器读取的32条需求与关键规则。
3. `docs/02-population-and-buildings.md`：3—6个月补员与过剩自动消失。
4. `docs/03-fleets-and-megastructure.md`：舰团、轴炮舰与母星舰造工程。
5. `docs/04-events-and-ascension.md`：友好分裂、借粮、饿殍遍地、钢铁蚊人。
6. `docs/05-proposals-and-open-questions.md`：未定数值与不能当成定案的内容。
7. `docs/06-development-handoff.md`：下一步实际开发与验收。
8. `docs/07-sources-and-assets.md`：来源、原图索引及可用工具状态。
9. `docs/08-revision-ledger.md`：已撤销的旧解释。

## 当前状态

- 需求与事件交接：已整理。
- 群星目标版本、DLC、安装位置：未确认。
- 游戏机制脚本、动态肖像、舰船模型、游戏内测试：尚未完成。
- GitHub 目标：mohsunil/qunxing；用户于2026-10-16明确授权公开上传。上传验证结果查看工作区外部的报告；本包不以上传代替开发完成。
- Codex Cloud 环境或云端开发任务：未创建、未发布、未启动。

## 校验与打包

```sh
python3 scripts/validate_handoff.py
python3 scripts/package_handoff.py --output ../haipam-stellaris-handoff.zip
```

Windows 可将 python3 改为 python。脚本只依赖 Python 标准库，不下载游戏、模型或凭据。

## 下一步的最小实际交付

锁定游戏版本后，先在游戏里实现并验收：协同进化双种族开局、皇家孵化场定时补员、过剩灰蚊人消失、反应釜减耗。随后验证一艘轴炮舰显示、移动与开火，再扩展其他系统。

