<img src="icon.png" width="96" align="right" alt="HongGuo Lite">

# 红果短剧瘦身 · HongGuo Lite

[![validate](https://github.com/k6nfmm7dbr-commits/hongguo-lite/actions/workflows/validate.yml/badge.svg)](https://github.com/k6nfmm7dbr-commits/hongguo-lite/actions/workflows/validate.yml)
![clients](https://img.shields.io/badge/clients-Egern%20%7C%20Surge%20%7C%20Loon%20%7C%20Stash%20%7C%20Shadowrocket-blue)
![license](https://img.shields.io/badge/license-MIT-green)

一个去广告 / 降内存的代理模块：拦截**红果短剧**（`com.phoenix.video`）的
**穿山甲广告 SDK、广告素材签名域和埋点上报**，减少开屏广告等待与剧集插播广告加载。

支持 **Egern**（原生 YAML 模块）、**Surge / Stash / Shadowrocket**（`.sgmodule`）、
**Loon**（`.plugin`）。任意一份都能用 [Script-Hub](https://github.com/Script-Hub-Org/Script-Hub) 互相转换。

---

## ⚠️ 先说结论

代理层（Egern / Surge / Loon 这类）**无法直接降低红果短剧的内存占用**。
短剧 App 的内存大头是**视频解码器 + 预加载缓冲**，这两块模块碰不到：

| 内存大头 | 量级 | 代理层能否触及 |
|---|---|---|
| 视频解码器实例 + 解码帧缓冲 | 大 | ⚠️ 只能减少"要解码的视频条数" |
| 预加载缓冲（红果会预取下一集） | 大 | ❌ 不能 |
| 剧集磁盘缓存 | 中 | ❌ 不能（要在 App 内清） |
| 埋点 / 上报队列 | 小 | ✅ 能 |
| **开屏广告 + 插播广告** | 中 | ✅ **能** |

红果这边和抖音类似：**一条插播广告就是一段完整视频**，和正片一样要占解码器和帧缓冲。
拦掉它省下的是实打实的一段视频内存。但它依然不是银弹。

---

## 一、红果短剧的广告长什么样

红果短剧是字节的产品，广告走**自家的穿山甲 SDK（Pangle）**——和抖音同一套体系。
所以核心域名就那几个，`pangolin` 一个关键词就能覆盖大半个家族。

**但有一个关键区别**：红果是「**免费看剧 + 广告**」的商业模式。
这意味着拦广告时有个**诚实的取舍**：

- 好消息：开屏广告、剧集插播广告都是 SDK 下发的，拦掉域名就没了；
- 需要注意：如果 App 里有「**看广告得金币 / 解锁**」这类入口，广告加载失败可能导致
  那个入口行为异常（点进去没反应、或者不给奖励）。

README 里我把**语义不够确定的域名**（`vas` / `security` / `effect`）默认注释掉了，
就是为了避免误伤金币类功能。真遇到异常，把对应那几行注释掉即可。

> 另外提一句：社区里有给红果做「解锁 VIP / 去水印」的脚本，但**那类脚本实测基本无效**，
> 而且依赖会随版本变的响应结构，失效后反而给每个请求增加开销。
> 本项目**刻意不做**这类改写 —— 只做去广告。

---

## 二、版本选择

| 版本 | 说明 | 需要 MITM / 证书？ |
|---|---|---|
| **基础版**（推荐先用） | 穿山甲 SDK + 广告签名域 + 埋点域名拦截 | ❌ 不需要 |
| **进阶版 Plus** | 基础版 + 广告请求接口拦截（`/api/ad/`） | ✅ 需要 |

**基础版就够了**：穿山甲 SDK 的广告域被整域拦掉后，SDK 连服务器都连不上，
开屏和插播广告基本就没了。进阶版多拦的是**红果自己 API 下发的广告**——
这条在域名层看不出任何异常（`*.snssdk.com` 看起来完全正常），**只有路径里写着 `ad`**。

**两个版本选一个用，不要同时装。**

---

## 三、安装

| 客户端 | 基础版 | 进阶版 |
|---|---|---|
| **Egern** | [hongguo-lite.yaml](https://raw.githubusercontent.com/k6nfmm7dbr-commits/hongguo-lite/main/egern/hongguo-lite.yaml) | [hongguo-lite-plus.yaml](https://raw.githubusercontent.com/k6nfmm7dbr-commits/hongguo-lite/main/egern/hongguo-lite-plus.yaml) |
| **Surge / Stash / Shadowrocket** | [hongguo-lite.sgmodule](https://raw.githubusercontent.com/k6nfmm7dbr-commits/hongguo-lite/main/surge/hongguo-lite.sgmodule) | [hongguo-lite-plus.sgmodule](https://raw.githubusercontent.com/k6nfmm7dbr-commits/hongguo-lite/main/surge/hongguo-lite-plus.sgmodule) |
| **Loon** | [hongguo-lite.plugin](https://raw.githubusercontent.com/k6nfmm7dbr-commits/hongguo-lite/main/loon/hongguo-lite.plugin) | 用 Script-Hub 转换 Surge 进阶版 ↓ |

- **Egern**：工具 → 模块 → 右上角 `+` → 粘贴上面的链接
- **Surge**：首页 → 模块 → 安装新模块 → 粘贴链接
- **Loon**：配置 → 插件 → `+` → 粘贴链接
- **不想托管任何文件**：把 [`egern/snippet-profile.yaml`](egern/snippet-profile.yaml) 里的
  `rules` 直接粘进 Egern 主配置 `Profile.yaml` 即可

### 转成别的客户端

> 在 Surge / Egern 里打开 **`script.hub`**（或访问 <https://scripthub.vercel.app>）
> → 来源类型选「Surge 模块」，粘贴上面的 raw 链接 → 目标类型选你要的客户端。

---

## 四、拦截清单

| 分类 | 条目 | 说明 |
|---|---|---|
| **穿山甲 / Pangle SDK** | `pangolin`（关键词）、`pglstatp-toutiao.com`、`pglstatp-toutiao-b.com` | 一条关键词覆盖 `pangolin-sdk-toutiao{,-b,1}.com`、`pangolin-dsp-toutiao{,-b}.com` 及 `api-access.*` / `log-api.*` 子域 |
| **广告素材签名域** | `-ad-sign.byteimg.com`（关键词） | 覆盖 `p3/p6/p9-ad-sign.byteimg.com` |
| **广告跳转** | `zlink.ugsdk.cn` | 广告落地页跳转 |
| **字节广告 API 子域** | `^ads[0-9]+-normal\.zijieapi\.com$` | `ads3-normal` / `ads5-normal` 等，**只拦带 ads 前缀的**，不碰主域 |
| **埋点 / 上报** | `mon.toutiaocloud.{net,com}`、`i.snssdk.com`、`i-lq.snssdk.com`、`is.snssdk.com`、`is-lq.snssdk.com`、`applog.fqnovel.com`、`-misc.fqnovel.com` | 对内存帮助很小，介意可注释掉 |

共 14 条规则（基础版）。

### 故意没做的事

| 想法 | 为什么不做 |
|---|---|
| 拦剧集视频 CDN（`douyinvod` / `pstatp` / `byteimg` 整域） | 广告和正片共用域名，拦了直接不能看 |
| 拦 API 主域（`snssdk.com` / `zijieapi.com` / `fqnovel.com`） | App 直接打不开，只拦其中明确是广告 / 埋点的子域 |
| 解锁 VIP / 去水印脚本 | 实测基本无效，且失效后给每个请求增加开销 |
| 拦金币 / 签到接口 | 那是 App 的正常功能，不是广告 |
| 默认拦 `vas` / `security` / `effect.snssdk.com` | 语义不够确定，可能误伤金币任务或特效资源，默认注释掉 |

---

## 五、⚠️ 三个必须注意的点

### 1. 规则顺序决定生死

Egern / Surge / Loon 的规则都是**从上到下匹配第一条命中的**。
如果你主配置里有这类宽泛规则且排在前面：

```yaml
- domain_suffix:
    match: "snssdk.com"
    policy: DIRECT          # ← 广告域名也匹配 snssdk.com，会被它抢先放行
```

那么本模块的 `REJECT` **完全不会生效**。请确保本模块规则排在它之前。

**验证**：请求记录 → 打开红果短剧 → 看 `pangolin-sdk-toutiao.com`、
`pglstatp-toutiao.com` 是否显示 `REJECT`。

### 2. 进阶版会解密字节的主 API 域

`*.snssdk.com` 是字节 App 的主 API 域，要拦它下面的 `/api/ad/` 就必须 MITM 它。
万一红果启用了**证书固定（cert pinning）**，会让它连不上，
表现是**红果打不开 / 一直转圈**。

真遇到就**删掉 `[MITM]` 段和 `[Map Local]` 段**，回到基础版 ——
基础版的穿山甲拦截已经能干掉大部分广告。

### 3. 金币类功能异常怎么办

红果是「免费看剧 + 广告」模式。如果拦广告后发现**金币 / 签到 / 看广告得奖励**
这类入口行为异常，把这几行注释掉即可：

- 埋点那一段（`mon.*`、`is.snssdk.com` 等）
- 如果你开了可选段，还有 `vas.snssdk.com`

其余规则不受影响。

---

## 六、App 内设置：真正有效的那一半

模块只能省广告那部分。**红果的内存大头在 App 内部**：

### 1. 清缓存 —— 最立竿见影

> 我 → 设置 → 清理缓存

短剧 App 会把看过的剧集缓存在本地，占用经常是几个 GB。清完之后内存和存储都会明显改善。
（红果的设置入口随版本会变，找不到就在「我的」页面翻一下。）

### 2. 系统层

- **iOS 设置 → 通用 → 后台 App 刷新 → 关闭红果**。
  红果的推送走 APNs，关掉不影响收消息，但能减少后台驻留和预加载。
- **定期彻底退出红果**（上滑卡片杀掉）再打开。
  这一步专门清掉**视频解码器实例和预加载缓冲的残留** —— 模块完全碰不到这块，
  但连刷几小时后它往往是内存涨得最凶的部分。

### 3. 别挂着预加载

红果会在你看到某一集时预取后面的内容。**不看了就退出 App**，别让它挂在后台继续预取。

---

## 七、验证 & 风险

### 验证

1. 请求记录 → 打开红果短剧 → 确认 `pangolin-sdk-toutiao.com`、`pglstatp-toutiao.com`
   显示 `REJECT`；
2. 进阶版：刷剧集 → 请求记录里 `*.snssdk.com/api/ad/` 应显示为 Map Local 命中；
3. 主观：开屏广告是不是没了、剧集插播广告是不是少了。

### 风险

| 风险 | 说明 | 缓解 |
|---|---|---|
| 规则不生效 | 被更靠前的宽泛规则抢先命中 | 用请求记录确认，调整顺序 |
| **MITM 字节主 API 域** | 若存在证书固定，红果可能打不开 | **删掉 `[MITM]` + `[Map Local]` 段回到基础版** |
| 金币 / 奖励功能异常 | 广告或埋点被拦后，相关入口可能不正常 | 注释掉埋点段 |
| 关键词匹配面较广 | `pangolin`、`-ad-sign.byteimg.com` 是关键词匹配 | 出问题就换成精确域名列表 |
| 广告位留白 | 个别位置可能显示空白而非消失 | 可接受 |

**回滚**：关掉模块开关即可，没有改任何持久状态。

---

## 八、域名清单来源

模块里的域名不是拍脑袋写的，逐条对照了社区规则集做了交叉验证：

| 来源 | 提供的条目 |
|---|---|
| [doovvip/sublink-worker2 · HongGuo-Surge-Native](https://github.com/doovvip/sublink-worker2) | `p6/p9-ad-sign.byteimg.com`、`api-access.pangolin-sdk-toutiao*`、`log-api.pangolin-sdk-toutiao*`、`pglstatp-toutiao.com`、`*.snssdk.com/api/ad/` 路径 |
| [LoonKissSurge · 番茄小说去广告](https://github.com/QingRex/LoonKissSurge) | `zlink.ugsdk.cn`、`mon.toutiaocloud.*`、`log3/5-applog.fqnovel.com`、`mon*-misc.fqnovel.com`、`i/is/i-lq/is-lq.snssdk.com`、`ads3/5-normal.zijieapi.com` |
| [zqzess/rule_for_quantumultX · FanQieNovel](https://github.com/zqzess/rule_for_quantumultX) | `p6/p9-ad-sign.byteimg.com`、`pglstatp-toutiao.com` |
| [217heidai/adblockfilters](https://github.com/217heidai/adblockfilters) | `p6-ad-sign.byteimg.com` 交叉核对 |
| [sve1r/Rules-For-Quantumult-X](https://github.com/sve1r/Rules-For-Quantumult-X) | `p*-ad-sign.byteimg.com` 通配写法 |

红果短剧与番茄小说同属字节的免费内容体系（红果就是从番茄的短剧板块独立出来的），
`ad-sign` / `fqnovel` / `snssdk` 这套域两边共用，所以番茄系验证过的条目对红果同样适用。

App 标识核对自 App Store（`红果短剧 - 海量热门短剧随心看`，id `6451407032`，
bundle id `com.phoenix.video`）。

---

## 附：这个模块系列

同系列（结构、规范、CI 完全一致）：

- [wechat-lite](https://github.com/k6nfmm7dbr-commits/wechat-lite) —— 微信去广告 / 降内存
- [douyin-lite](https://github.com/k6nfmm7dbr-commits/douyin-lite) —— 抖音去广告 / 降内存
- [ios-lite](https://github.com/k6nfmm7dbr-commits/ios-lite) —— 全系统通用广告 / 追踪拦截
- **hongguo-lite** —— 红果短剧去广告（本仓库）

> 提醒：`douyin-lite-plus`、`wechat-lite-plus`、`hongguo-lite-plus` 都需要 MITM。
> **不要同时开多个** —— 每条 HTTPS 连接解密都要算 CPU，对性能是实打实的负担。

---

## License

[MIT](LICENSE)
