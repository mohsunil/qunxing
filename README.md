# 海帕姆：银心初航｜Stellaris Mod 开发工程

版本：0.2.0-alpha（人口机制源代码原型）
整理日期：2026-10-16（Asia/Shanghai）

**已包含首批游戏脚本与本地安装器，适配4.5.2。游戏内运行尚未验证，不是完整可玩版本。**

初始0.1.0交接包保留于仓库 releases/。当前版本已开始实际制作，保留32条用户需求；具体实现进度见 `docs/09-prototype-progress.md`。不要把静态校验或孵化算法检查称为游戏测试通过。

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
- 目标版本：本机已确认 Cygnus 4.5.2 (9776)，已读取其人口组、岗位、特质和事件接口。已发现Utopia等DLC资源，账号授权未单独核对。
- 游戏机制脚本：人口首版已写入 `mod/haipam`，本机已安装；尚未通过引擎加载及游戏内测试。肖像和舰船使用原版占位，没有自制模型。
- 脚本静态校验及406组孵化算法检查通过；实际就业、维护费、领袖与人口删除仍待引擎验收。
- 直接启动在生成脚本日志前退出；通过Steam启动后观察到剩余游戏文件正在下载/安装。崩溃原因尚未确认。
- GitHub 目标：mohsunil/qunxing；用户于2026-10-16明确授权公开上传。上传验证结果查看工作区外部的报告；本包不以上传代替开发完成。
- Codex Cloud 环境或云端开发任务：未创建、未发布、未启动。

## 校验与打包

```sh
python3 scripts/validate_handoff.py
python3 scripts/validate_mod.py
python3 scripts/package_handoff.py --output ../haipam-stellaris-prototype-v0.2.0.zip
```

Windows 可将 python3 改为 python。脚本只依赖 Python 标准库，不下载游戏、模型或凭据。安装器生成的原版规则适配文件与本机安装报告不进入公开仓库或压缩包。

## 安装原型

在工程目录打开PowerShell，按实际安装路径运行：

```powershell
python scripts/install_mod.py --game "D:\steam\steamapps\common\Stellaris" --userdir "$env:USERPROFILE\Documents\Paradox Interactive\Stellaris"
```

安装器仅支持4.5.2，自动生成本地规则适配；不修改游戏安装文件、其他Mod、启动器播放集、设置或存档。重新安装前备份本Mod旧文件。随后在启动器播放集中添加“海帕姆：银心初航（人口原型）”，首轮单独启用它，新建游戏选择“海帕姆帝国（初航原型）”。停用播放集中的本Mod即可回退；测试存档不要用于正式战役。

## 下一步的最小实际交付

按 `docs/10-in-game-acceptance.md` 完成：协同进化双种族、白蚊人领袖、皇家孵化场定时补员、过剩灰蚊人消失、反应釜减耗。通过后接入舰团化、轴炮舰和后续事件；银心定位与完整科技体系仍未实现。

