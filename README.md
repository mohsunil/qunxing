# 海帕姆：银心初航

**0.5.1-alpha · Stellaris Cygnus 4.5.2 (9776)**

开发中的原型。0.5.0已通过新局开场与灰蚊人闲置清理的存档核对；0.5.1新增救国会与可见母星资源修正，尚待引擎复查及功能验收。

- 协同进化、白蚊人领袖、灰蚊人按非精英岗位孵化及过剩删除。
- 皇家设施、灵蚊人、神殿、专属陆军、邮政旧船、资源母星与四阶段舰造工程。
- 舰团化、三档轴炮舰和生产蓝图。
- 新增边疆拓殖、组织度、友好分裂、借粮／饥荒／钢铁蚊人联军。
- 王家双螺旋开放基因与灵能并行，保留科技、飞升槽和传统成本。
- 危机中可能出现海帕姆救国会，提供粮食保障、生产恢复和整顿诉求。

已接入按长枪级D型、捕网级参考制作的原创低模舰体源文件，待游戏显示验收。肖像仍静态；白蚊人暂不加头须，灰蚊人四翼收拢。已有八张角色肖像、六张原创建筑图、十一张科技图标和五张事件卡。

待完成：银心开局定位、模型实装验收、嘴部动画、战役与大可汗实战。平衡数值均为原型；3—6个月补员、白蚊人领袖及过剩删除是固定要求。

当前进度见 docs/15-salvation-and-resources-v051.md；0.5.0内容见 docs/14-frontier-and-ascension-v050.md。原始需求保存在 design/requirements.json；旧版文档为历史记录。

验证入口：scripts/validate_mod.py、validate_content.py、validate_frontier.py、dual_ascension_adapter.py。安装使用 scripts/install_mod.py，备份参数 --backup-root 指向 D:/Codex-Haipam/backups；交付包写入 D:/Codex-Haipam/releases。

本机派生的原版规则、武器参数和双飞升适配留在安装目录，不进入公开包。旧备份、安装包和测试目录已迁至D盘。源仓库 mohsunil/qunxing；上传以外部核验回执为准，未创建Codex Cloud环境。
