# 海帕姆原创舰体低模原型

依据用户提供的长枪级实验型战列舰D型／捕网级护卫舰资料建模。原图保存在 reference/，没有改写或覆盖原图。中型是同一工业风格的制作派生，尚无用户指定的正式舰级名称。

这些是可编辑的真实三维几何与自行生成的游戏模型文件；不是原版舰船换色，也不是生成图片冒充三维模型。当前仍是低模原型，尚未在实际游戏里验证尺度、材质、分段装配、引擎或开火；外形细节仍需用户审阅，不能视为最终还原。

## 查看和修改

- haipam_hulls_geometry.png：三艘实际几何的斜俯视预览，使用深度缓冲渲染；不是游戏截图。
- haipam_hulls_orthographic.png：实际几何的顶视、侧视。
- light_complete.obj、medium_complete.obj、heavy_complete.obj：完整可编辑舰体。
- light_core.obj、medium_bow.obj、medium_stern.obj、heavy_bow.obj、heavy_core.obj、heavy_stern.obj：六个可编辑舰段。
- haipam_palette.mtl 与 haipam_hulls_diffuse.png：OBJ材质与UV色板；导入OBJ时保留同目录。
- diffuse / normal / specular 三张PNG与DDS全部由本项目生成。法线图采用群星的通道格式，B为发光，G与A为切线空间法线；不能直接作为其他软件的标准RGB法线使用。

## 接入契约

游戏模型目录为 mod/haipam/gfx/models/ships/haipam/。不含原版专有 mesh、anim 或贴图。构建工具只使用独立的 scripts/pdx_binary.py 编码器。

| 舰型 | 舰体框架实体 | 舰段实体 |
|---|---|---|
| 轻型／捕网轮廓 | haipam_light_entity | haipam_light_core_entity |
| 中型／制作派生 | haipam_medium_entity | haipam_medium_bow_entity、haipam_medium_stern_entity |
| 重型／长枪D轮廓 | haipam_heavy_entity | haipam_heavy_bow_entity、haipam_heavy_core_entity、haipam_heavy_stern_entity |

框架有 part1、part2、part3 静态骨。所有骨的变换为单位矩阵，六段保留完整舰体坐标，因此应挂在对应的 part 骨零位；不要按原版舰段的偏移值移动它们。

现有玩法中使用的 small_gun_01、small_gun_02、small_gun_03、medium_gun_01、medium_gun_02、medium_gun_03、large_gun_01 已按各舰段提供；同时提供各自的 _muzzle 节点。框架包含 engine_01、engine_02、engine_03、target_locator_1、target_locator_2。三联炮台和炮管是舰体中的固定几何，不能活动。若同时绘制原版武器组件，会叠出原版炮塔；正式接入需选择隐藏原版武器外观或进一步制作独立可转炮塔。开火源点仍须实机验证。

OBJ坐标为 X右舷、Y上、+Z舰首；游戏导出采用4倍几何单位并将舰首转换为-Z，翻转面序保留外法线。框架实体的缩放值仅为待测试的原型数值。

运行 python scripts/build_ship_models.py 可重新生成模型、UV、法线、切线、三张DDS、OBJ与预览。手工修改后不要直接重跑生成器，以免覆盖修改。model-validation.json 记录索引范围、单位法线、正交切线、UV范围、必需节点、DDS可读性、二进制回读与文件散列；这些静态检查不代表游戏验收通过。
