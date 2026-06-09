# RWA 的「杠杆时代」来了——但合规的窗正在关上

## RWA 时评 | 2026-06-09

### 文章解读

6 月 9 日，两条看似独立的事件正在指向同一个结论：RWA 行业正在从「代币化持有」走向「代币化交易」，而监管窗口正在以超出多数人预期的速度合拢。

Ondo Perps 今天正式上线——全球首个面向非美用户的链上股票永续合约平台，最高 20 倍杠杆，代币化资产直接当保证金。同一天，欧洲 MiCA 的 CASP 授权截止日进入 22 天倒计时，USDT 已被主流交易所从 EEA 零售端下架，Gemini 和 Luno 退出欧盟，210+ 家 CASP 抢滩但只有 14 家交易所拿到完整牌照。

一边是美国 CFTC 为永续合约开闸，一边是欧盟 MiCA 为合规清场。两条监管路径的终点是一样的：**没有牌照的玩家，下半年没得玩。**

---

### Ondo Perps 上线：RWA 从「持有」到「杠杆交易」的质变

Ondo Finance 今天正式推出 Ondo Perps，这不是又一个 DeFi 杠杆协议——它是 RWA 行业从「代币化持有」到「代币化交易」的结构性跃迁。

**核心数据**：

| 指标 | 数据 |
|------|------|
| 上线日期 | 2026 年 6 月 9 日 |
| 支持资产 | 260+ 种代币化美股/ETF |
| 最高杠杆 | 20 倍 |
| 目标用户 | 非美国用户（全球其他地区） |
| Ondo 市场份额 | 代币化股票领域 70%+ |
| Ondo Global Markets TVL | 突破 10 亿美元（5 月 11 日） |
| 累计交易量 | 超过 180 亿美元 |
| 生态总 TVL | 35-38 亿美元（多链） |

**为什么这件事比表面看起来重要得多？**

Ondo Perps 的真正创新不是杠杆本身——dYdX 和 GMX 早就有了。它的创新在于**抵押品机制**：交易者可以用已有的代币化股票持仓直接作为保证金，无需额外存入现金或加密资产。持有代币化特斯拉股票？直接用它来开英伟达的多头。持有 OUSG（代币化美债基金）？用它做抵押品，清算风险比 ETH 低得多。

这意味着 RWA 代币不再是「躺着的资产」——它们变成了**可循环使用的资本**。这在传统金融里叫「抵押再融资」，在链上它是自动化的、即时的、无中介的。

**CFTC 为什么放行？**

2026 年 5 月 29 日，CFTC 批准了 KalshiEX 的 BTCPERP——美国首个受监管的比特币永续合约。随后 Coinbase 也通过离岸关联公司获得了向美国客户推出永续合约的路径。CFTC 的态度转变不是偶然：

- 永续合约是加密市场交易量最大的品类（日均超过 500 亿美元），监管层不可能长期假装它不存在
- CFTC 与 SEC 的管辖权争夺中，「先批先管」是抢占话语权的最优策略
- 对 RWA 衍生品而言，CFTC 的监管先例比 SEC 的证券框架友好得多——商品法比证券法灵活

**Ondo Perps 的风险面**：

- **地区限制是双刃剑**：只面向非美用户，意味着它无法触及全球最大的散户和机构市场。这是一个合规选择，也是增长天花板
- **链下资产验证的复杂性**：RWA 代币作为抵押品时，底层资产的结算仍依赖传统金融基础设施（T+1 或 T+2），这给清算引擎带来了时间差风险
- **领导层过渡**：创始人 Nathan Allman 去世后的团队交接仍在进行中，战略连续性存在不确定性
- **ONDO 代币解锁**：大量代币解锁可能带来价格压力，进而影响生态治理

---

### MiCA 倒计时 22 天：合规的窗正在关上

如果说 Ondo Perps 代表的是 RWA 的「上行空间」，那么 MiCA 7 月 1 日的 CASP 授权截止日代表的则是「下行约束」——而且约束的力度被严重低估了。

**当前格局**：

| 分类 | 数量 | 代表 |
|------|------|------|
| 完整 CASP 授权的交易所 | 14 家 | Coinbase、OKX、Kraken、Crypto.com、Bitstamp |
| 审核进行中 | 2 家 | Binance（希腊）、Bitget（奥地利） |
| 已退出欧盟 | 2 家+ | Gemini（4 月退出）、Luno（6 月清退） |
| 完全未申请 | 3 家+ | MEXC、Bitunix、Nexo |
| ESMA 注册 CASP 总数 | 210+ | 包括各类服务提供商 |

**USDT 被逐出欧盟**：

这是 MiCA 对 RWA 行业影响最直接的事件。Tether 公开表示无意申请 MiCA 授权，结果 USDT 已被 Binance、Coinbase、Kraken、Crypto.com 从 EEA 零售端下架。USDT 日均交易量超过 500 亿美元，是全球流动性最深的稳定币——它的退出意味着：

1. **RWA 结算层被迫切换**：大量以 USDT 为结算对的 RWA 交易将迁移至 USDC（唯一获 MiCA 授权的大型美元稳定币）或其他合规替代品
2. **流动性碎片化加剧**：EU 区域用 USDC/EURC，非 EU 区域用 USDT，同一个 RWA 资产在两个流动性池中定价，套利成本上升
3. **机构被迫「选边」**：想要在欧盟合规运营的 RWA 发行方，必须同时维护两套稳定币结算通道

**MiCA 合规稳定币全景**：

| 稳定币 | 发行方 | 监管机构 | 牌照类型 | 供应量 |
|--------|--------|----------|----------|--------|
| USDC | Circle | ACPR（法国） | EMT | ~$400 亿+ |
| EURC | Circle | ACPR（法国） | EMT | ~$2 亿+ |
| EURCV | SG-FORGE | ACPR（法国） | EMT（信贷机构） | 小型浮动 |
| USDG | Paxos | FIN-FSA（芬兰） | EMT | 持续增长 |
| EURI | Banking Circle | CSSF（卢森堡） | EMT | 小型浮动 |
| EURQ/USDQ | Quantoz | DNB（荷兰） | EMT | 早期阶段 |
| EURR | StablR | MFSA（马耳他） | EMT | 小型浮动 |
| EUROe | Membrane Finance | FIN-FSA（芬兰） | EMT | 小型浮动 |

Circle 的 USDC 以压倒性优势成为 MiCA 框架下唯一的大型美元稳定币。这对 RWA 意味着什么？**Circle 的合规优势正在转化为 RWA 结算层的事实标准。** USDC 不仅是稳定币，更是 RWA 代币化产品的出入金管道。谁控制了结算层，谁就控制了生态的话语权。

**7 月 1 日之后会发生什么？**

- 未获 CASP 授权的交易所，对欧盟用户必须停止服务
- 未经授权的 CASP 必须提交用户资产清退计划（ESMA 4 月 17 日声明）
- 向欧盟用户进行主动营销变为非法行为
- 各国监管机构可对不合规平台发布封锁令
- 至少 30 家小型平台已主动退出欧盟（占比约 18%）

---

### 对从业者的一些启示

**1. 结算层必须提前布局 MiCA 合规方案**

7 月 1 日后，USDT 在欧盟零售端将彻底不可用。如果你的 RWA 产品面向欧盟用户，现在就必须完成从 USDT 到 USDC 或其他合规稳定币的结算层迁移。这不是「可以等等看」的事——三周后就是硬截止。

**2. RWA 代币的「资本效率」时代已到**

Ondo Perps 证明了一件事：代币化资产不再只是「躺着的持仓」，它可以成为杠杆交易的抵押品、跨资产调度的保证金、DeFi 协议的底层资产。RWA 项目的竞争维度从「能不能发币」升级到了「能不能让代币在 DeFi 里循环使用」。如果你的代币化产品不支持跨协议抵押，你在资本效率上已经落后了。

**3. CFTC 的「商品路径」比 SEC 的「证券路径」更适合 RWA 衍生品**

CFTC 批准永续合约的速度和态度远比 SEC 友好。对于计划推出 RWA 衍生品产品的团队，优先考虑 CFTC 的商品框架进行合规设计，而非 SEC 的证券注册路径。但注意：这只适用于「非美用户」场景，美国国内的监管路径仍然高度不确定。

**4. 欧元稳定币碎片化是 RWA 在欧洲的隐性成本**

8 种 MiCA 合规的欧元稳定币同时存在，没有一个达到 USDC 的规模效应。如果你计划在欧盟发行欧元计价的 RWA 产品，流动性的碎片化意味着更高的做市成本和更低的二级市场深度。短期内，美元计价 + USDC 结算仍然是 RWA 最优的合规路径。

**5. Binance 的 CASP 审批是下半年最大的变量**

Binance 的 CASP 申请正在希腊 HCMC 审查中，EY 和 KPMG 进行合规审计。如果 Binance 获批，它将带着全球最大的散户流量进入 MiCA 体系，这对 RWA 代币在欧盟的分销渠道是重大利好。如果被拒，则意味着即使是全球最大的交易所也无法在 MiCA 框架下找到捷径——合规门槛将被进一步上调。

---

*本文分析基于 2026 年 6 月 7-9 日的公开报道。*
*新闻来源：*
1. AInvest - Ondo Perps Launches June 9, Expanding On-Chain Leverage for Tokenized Equities (June 3, 2026)
2. CryptoDiffer - Ondo Perps Full Launch, 24/7 Equity Perpetuals On-Chain (June 9, 2026)
3. The Street - Ondo Is Bringing Leveraged Stock Trading On-Chain (June 3, 2026)
4. BitcoinMarket - Best MiCA Exchanges 2026: July 1 Deadline (June 2026)
5. Eco - MiCA-Compliant Stablecoins 2026: Full List With Issuers (May 26, 2026)
6. StudioGlobal - Ondo Finance Launches Ondo Perps: 24/7 Leveraged Trading on Tokenized Assets (June 3, 2026)
7. CoinAlert News - Ondo Perps: CFTC Approval (June 2, 2026)
