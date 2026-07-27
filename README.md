# P20 Live Position（实验）

该自定义集成不建立第二条 P20 局域网连接，而是复用 Home Assistant 官方
Roborock 集成在 `ConfigEntry.runtime_data` 中持有的设备会话。

## 当前行为

- 目标型号：`roborock.vacuum.a134`
- 离座读取间隔：3 秒
- 回到底座后停止动态坐标请求，改用已验收的固定底座锚点；离座后自动恢复读取。
- 只读命令：`get_dynamic_map_diff`、`get_dynamic_data`
- 实体：`sensor.p20_pro_live_position`
- 状态：`left_percent,top_percent`
- 属性：LAN 坐标、朝向、户型图百分比坐标、更新时间、实际连接类型
- 六个户型映射系数在配置流程中填写，只保存在 HA 本地。

## 实验边界

- 不修改官方 Roborock 集成。
- 不发送清扫、暂停、回充或其它控制命令。
- 已接入家庭3D微缩家园正式看板。
- 依赖 Home Assistant 2026.7.4 当前的 Roborock 运行时结构和
  `python-roborock==5.31.1`，升级后需要重新验证。
